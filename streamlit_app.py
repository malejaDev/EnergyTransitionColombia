from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st


# Etiquetas con escapes Unicode para evitar problemas de encoding del archivo en Windows.
# Mantienen tildes en runtime y permiten que el dominio del color haga match exacto.
ENERGY_HIDRAULICA = "Hidr\u00e1ulica"
ENERGY_SOLAR = "Solar"
ENERGY_EOLICA = "E\u00f3lica"
ENERGY_GEOTERMICA = "Geot\u00e9rmica"

ENERGY_COLOR_DOMAIN = [ENERGY_HIDRAULICA, ENERGY_SOLAR, ENERGY_EOLICA, ENERGY_GEOTERMICA]
ENERGY_COLOR_RANGE = ["#0284c7", "#f59e0b", "#10b981", "#ef4444"]  # azul, amarillo, verde/teal, rojo


def _energy_color_scale() -> alt.Scale:
    return alt.Scale(domain=ENERGY_COLOR_DOMAIN, range=ENERGY_COLOR_RANGE)


def _fmt_qty_es(value: float, decimals: int = 1) -> str:
    """Cantidad con separador de miles estilo es-CO."""
    s = f"{value:,.{decimals}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def _labels_for_max_ties(df: pd.DataFrame, cat_col: str, val_col: str) -> tuple[float, list[str]]:
    mx = float(df[val_col].max())
    cats = df.loc[df[val_col] == mx, cat_col].astype(str).unique().tolist()
    return mx, sorted(cats)


def _labels_for_min_ties(df: pd.DataFrame, cat_col: str, val_col: str) -> tuple[float, list[str]]:
    mn = float(df[val_col].min())
    cats = df.loc[df[val_col] == mn, cat_col].astype(str).unique().tolist()
    return mn, sorted(cats)


def _fmt_cat_list(cats: list[str]) -> str:
    if len(cats) == 1:
        return f"**{cats[0]}**"
    if len(cats) == 2:
        return f"**{cats[0]}** y **{cats[1]}**"
    return "**" + "**, **".join(cats[:-1]) + f"** y **{cats[-1]}**"


def _interp_numeric_profile(s: pd.Series, decimals: int = 2) -> str:
    """Perfil n, min, max, media, mediana e IQR (si n≥4)."""
    s = pd.to_numeric(s, errors="coerce").dropna()
    n = len(s)
    if n == 0:
        return "_Sin valores numéricos._"
    parts = [
        f"**n={n}**",
        f"mín **{_fmt_qty_es(float(s.min()), decimals)}**",
        f"máx **{_fmt_qty_es(float(s.max()), decimals)}**",
        f"media **{_fmt_qty_es(float(s.mean()), decimals)}**",
        f"mediana **{_fmt_qty_es(float(s.median()), decimals)}**",
    ]
    if n >= 4:
        q1, q3 = float(s.quantile(0.25)), float(s.quantile(0.75))
        parts.append(f"IQR **{_fmt_qty_es(q3 - q1, decimals)}** (p25–p75)")
    return " · ".join(parts)


def _tukey_upper_fence(s: pd.Series, k: float = 1.5) -> float | None:
    s = pd.to_numeric(s, errors="coerce").dropna()
    if len(s) < 4:
        return None
    q1, q3 = float(s.quantile(0.25)), float(s.quantile(0.75))
    iqr = q3 - q1
    if iqr <= 0:
        return None
    return q3 + k * iqr


def _interp_dominant_share(
    df: pd.DataFrame,
    cat_col: str,
    val_col: str,
    intro_sentence: str,
    unit: str,
    total_unit: str | None = None,
    weight_col: str | None = None,
) -> str:
    """Mayor categoría y participación; con `weight_col` se suma ese campo por categoría antes del cálculo."""
    tu = total_unit or unit
    if df is None or df.empty:
        return "_No hay datos en el conjunto mostrado para generar el resumen._"
    if weight_col is not None:
        if weight_col not in df.columns or cat_col not in df.columns:
            return "_Faltan columnas para participación ponderada._"
        dd = df[[cat_col, weight_col]].dropna(subset=[weight_col]).copy()
        if dd.empty:
            return "_No hay pesos numéricos válidos._"
        dd = dd.groupby(cat_col, as_index=False)[weight_col].sum()
        eff_col = weight_col
    else:
        dd = df[[cat_col, val_col]].dropna(subset=[val_col]).copy()
        eff_col = val_col
    if dd.empty:
        return "_No hay valores numéricos válidos en la gráfica._"
    tot = float(dd[eff_col].sum())
    if tot <= 0:
        return "_La suma del indicador es cero o no positiva; no se calcula participación relativa._"
    mx, tie_cats = _labels_for_max_ties(dd, cat_col, eff_col)
    tied = dd[dd[cat_col].isin(tie_cats)]
    combined = float(tied[eff_col].sum())
    pct_combined = 100.0 * combined / tot
    wnote = f" La participación usa **suma de `{weight_col}`** por categoría." if weight_col else ""
    if len(tie_cats) == 1:
        val = float(tied[eff_col].iloc[0])
        pct = 100.0 * val / tot
        return (
            f"{intro_sentence} {_fmt_cat_list(tie_cats)}, con **~{_fmt_qty_es(val)} {unit}**, "
            f"lo que representa aproximadamente el **{_fmt_qty_es(pct)}%** del total "
            f"(**~{_fmt_qty_es(tot)} {tu}** en **{len(dd)}** categorías en pantalla).{wnote}"
        )
    return (
        f"{intro_sentence} **empate** al máximo entre {_fmt_cat_list(tie_cats)} (~{_fmt_qty_es(mx)} {unit} c/u); "
        f"en conjunto **~{_fmt_qty_es(combined)} {unit}** (**~{_fmt_qty_es(pct_combined)}%** del total "
        f"**~{_fmt_qty_es(tot)} {tu}**, **{len(dd)}** categorías).{wnote}"
    )


def _interp_min_max_mean_rows(df: pd.DataFrame, cat_col: str, val_col: str, metric_label: str, unit: str) -> str:
    """Rango, promedio, mediana e IQR; admite empates en máximo y mínimo."""
    if df is None or df.empty:
        return "_No hay datos para resumir._"
    d = df[[cat_col, val_col]].dropna(subset=[val_col]).copy()
    if d.empty:
        return "_Sin valores numéricos._"
    if len(d) == 1:
        r = d.iloc[0]
        return (
            f"Solo figura **{r[cat_col]}** con **~{_fmt_qty_es(float(r[val_col]))} {unit}**; "
            "agregue más categorías en los datos para comparar rangos."
        )
    mx, max_cats = _labels_for_max_ties(d, cat_col, val_col)
    mn, min_cats = _labels_for_min_ties(d, cat_col, val_col)
    mu = float(d[val_col].mean())
    med = float(d[val_col].median())
    lines: list[str] = []
    if len(max_cats) == 1:
        lines.append(f"- **Mayor {metric_label}:** **{max_cats[0]}** (~{_fmt_qty_es(mx)} {unit}).")
    else:
        lines.append(f"- **Mayor {metric_label}** (empate): {_fmt_cat_list(max_cats)} (~{_fmt_qty_es(mx)} {unit} c/u).")
    if len(min_cats) == 1:
        lines.append(f"- **Menor {metric_label}:** **{min_cats[0]}** (~{_fmt_qty_es(mn)} {unit}).")
    else:
        lines.append(f"- **Menor {metric_label}** (empate): {_fmt_cat_list(min_cats)} (~{_fmt_qty_es(mn)} {unit} c/u).")
    lines.append(f"- **Promedio simple** entre las {len(d)} categorías mostradas: ~{_fmt_qty_es(mu)} {unit}.")
    lines.append(f"- **Mediana:** ~{_fmt_qty_es(med)} {unit}.")
    if len(d) >= 4:
        q1 = float(d[val_col].quantile(0.25))
        q3 = float(d[val_col].quantile(0.75))
        iqr = q3 - q1
        full = mx - mn
        spread = "dispersión moderada" if full > 0 and iqr < 0.5 * full else "dispersión amplia respecto al rango"
        lines.append(
            f"- **IQR (p25–p75):** ~{_fmt_qty_es(q1)}–{_fmt_qty_es(q3)} {unit} "
            f"(Δ ~{_fmt_qty_es(iqr)} {unit}; {spread} en esta muestra)."
        )
    return "\n".join(lines)


def _interp_costos_proyecto_bars(df: pd.DataFrame, val_col: str, label_metric: str, unit: str, anio: object) -> str:
    """Ranking, mediana, IQR y valores altos tipo Tukey sobre `nombre`."""
    if df is None or df.empty:
        return "_Sin proyectos bajo los filtros actuales; amplíe la selección o ajuste año/tipo._"
    need = {"nombre", val_col}
    if not need.issubset(df.columns):
        return "_Faltan columnas esperadas en el conjunto filtrado._"
    d = df[list(need)].dropna(subset=[val_col]).copy()
    if d.empty:
        return "_No hay valores numéricos para el indicador en la gráfica._"
    mx, max_cats = _labels_for_max_ties(d, "nombre", val_col)
    mn, min_cats = _labels_for_min_ties(d, "nombre", val_col)
    mu = float(d[val_col].mean())
    med = float(d[val_col].median())
    yr = f" (año **{anio}**)" if anio is not None and str(anio) != "" else ""
    lines: list[str] = [f"Con **{len(d)}** proyecto(s) en pantalla{yr}:\n"]
    em_m = " — empate" if len(max_cats) > 1 else ""
    em_n = " — empate" if len(min_cats) > 1 else ""
    lines.append(f"- **Mayor {label_metric}:** {_fmt_cat_list(max_cats)} (~{_fmt_qty_es(mx)} {unit}){em_m}.")
    lines.append(f"- **Menor {label_metric}:** {_fmt_cat_list(min_cats)} (~{_fmt_qty_es(mn)} {unit}){em_n}.")
    lines.append(f"- **Promedio:** ~{_fmt_qty_es(mu)} {unit} · **Mediana:** ~{_fmt_qty_es(med)} {unit}.")
    if len(d) >= 4:
        q1 = float(d[val_col].quantile(0.25))
        q3 = float(d[val_col].quantile(0.75))
        iqr = q3 - q1
        lines.append(f"- **IQR:** ~{_fmt_qty_es(q1)}–{_fmt_qty_es(q3)} {unit} (Δ ~{_fmt_qty_es(iqr)} {unit}).")
        hi = _tukey_upper_fence(d[val_col])
        if hi is not None:
            out_mask = d[val_col] > hi
            if out_mask.any():
                out_names = sorted(d.loc[out_mask, "nombre"].astype(str).unique().tolist())
                lines.append(
                    f"- **Valores altos (Tukey):** por encima de ~{_fmt_qty_es(hi)} {unit}: "
                    f"{_fmt_cat_list(out_names)} — revisar si son atípicos operativos o errores."
                )
    return "\n".join(lines)


def _interp_capex_opex_cross(df: pd.DataFrame) -> str:
    if df is None or df.empty:
        return "_No hay proyectos con costos para comparar CAPEX y OPEX._"
    need = {"nombre", "capex_musd", "opex_musd"}
    if not need.issubset(df.columns):
        return "_Datos incompletos para CAPEX/OPEX._"
    d = df[list(need)].dropna(subset=["capex_musd", "opex_musd"]).copy()
    if d.empty:
        return "_Sin pares CAPEX/OPEX válidos._"
    mxc, cats_c = _labels_for_max_ties(d, "nombre", "capex_musd")
    mxo, cats_o = _labels_for_max_ties(d, "nombre", "opex_musd")
    if len(cats_c) == 1:
        rc = d[d["nombre"] == cats_c[0]].iloc[0]
        line_c = (
            f"- **Mayor CAPEX:** **{rc['nombre']}** (~{_fmt_qty_es(float(rc['capex_musd']))} M USD de inversión; "
            f"OPEX ~{_fmt_qty_es(float(rc['opex_musd']))} M USD)."
        )
    else:
        line_c = f"- **Mayor CAPEX** (empate): {_fmt_cat_list(cats_c)} (~{_fmt_qty_es(mxc)} M USD c/u)."
    if len(cats_o) == 1:
        ro = d[d["nombre"] == cats_o[0]].iloc[0]
        line_o = (
            f"- **Mayor OPEX:** **{ro['nombre']}** (~{_fmt_qty_es(float(ro['opex_musd']))} M USD operativo; "
            f"CAPEX ~{_fmt_qty_es(float(ro['capex_musd']))} M USD)."
        )
    else:
        line_o = f"- **Mayor OPEX** (empate): {_fmt_cat_list(cats_o)} (~{_fmt_qty_es(mxo)} M USD c/u)."
    return f"{line_c}\n{line_o}"


def _interp_disponibilidad(df: pd.DataFrame) -> str:
    if df is None or df.empty or "disponibilidad_pct" not in df.columns:
        return "_No hay serie de disponibilidad para analizar._"
    s = df["disponibilidad_pct"].dropna()
    if s.empty:
        return "_Disponibilidad sin valores numéricos._"
    mn, mx, mu = float(s.min()), float(s.max()), float(s.mean())
    med = float(s.median())
    std = float(s.std(ddof=0)) if len(s) > 1 else 0.0
    prof = _interp_numeric_profile(s, 2)
    if mx - mn < 0.05:
        return (
            f"En la muestra, la **disponibilidad** es casi **uniforme** "
            f"(aprox. **{_fmt_qty_es(mu, 2)}%** de media y **{_fmt_qty_es(med, 2)}%** de mediana; "
            f"rango **{_fmt_qty_es(mx - mn, 2)}** puntos). Perfil: {prof}."
        )
    i_max = s.idxmax()
    i_min = s.idxmin()
    nom = df["nombre"] if "nombre" in df.columns else pd.Series(index=s.index, dtype=object)
    hi = nom.loc[i_max] if i_max in nom.index else "—"
    lo = nom.loc[i_min] if i_min in nom.index else "—"
    extra = ""
    if len(s) >= 4:
        q1, q3 = float(s.quantile(0.25)), float(s.quantile(0.75))
        extra = f"\n- **IQR:** ~{_fmt_qty_es(q1, 2)}–{_fmt_qty_es(q3, 2)}% (Δ ~{_fmt_qty_es(q3 - q1, 3)} puntos)."
    return (
        f"- **Máximo:** **{hi}** (~{_fmt_qty_es(mx, 2)}%).\n"
        f"- **Mínimo:** **{lo}** (~{_fmt_qty_es(mn, 2)}%).\n"
        f"- **Media** (~{_fmt_qty_es(mu, 2)}%), **mediana** (~{_fmt_qty_es(med, 2)}%) y **desv. típ.** "
        f"~{_fmt_qty_es(std, 3)} puntos ({len(s)} proyectos).{extra}"
    )


def _interp_regulacion_chart(df: pd.DataFrame) -> str:
    if df is None or df.empty:
        return "_Sin filas de regulación._"
    if not {"ley", "pct_ahorro"}.issubset(df.columns):
        return "_Columnas normativas ausentes._"
    d = df[["ley", "pct_ahorro"]].dropna(subset=["pct_ahorro"]).copy()
    if d.empty:
        return "_Porcentajes de ahorro no numéricos._"
    tot = float(d["pct_ahorro"].sum())
    idx = d["pct_ahorro"].idxmax()
    r = d.loc[idx]
    if tot > 0:
        pct = 100.0 * float(r["pct_ahorro"]) / tot
        share_txt = (
            f"En el gráfico de dona, ese porcentaje tiene un **peso visual ~{_fmt_qty_es(pct)}%** respecto a la "
            f"**suma** de los `%` de ahorro mostrados (**{_fmt_qty_es(tot, 1)}** pp en total entre leyes). "
            f"**No** interpretar como peso en pesos ni impacto tributario real."
        )
    else:
        share_txt = "La suma de porcentajes es cero; revise los datos."
    return (
        f"La ley con mayor **% de ahorro** declarado en el dataset normativo es **{r['ley']}** "
        f"(**{_fmt_qty_es(float(r['pct_ahorro']), 1)}** puntos porcentuales). {share_txt}"
    )


def _interp_lcoe_yoy_global(costos: pd.DataFrame) -> str:
    """Compara el LCOE medio global entre los dos años más recientes disponibles."""
    y = costos.dropna(subset=["anio", "lcoe_usd_mwh"])
    if y["anio"].nunique() < 2:
        return ""
    years = sorted(y["anio"].unique().tolist())
    last_y, prev_y = int(years[-1]), int(years[-2])
    m_last = float(y.loc[y["anio"] == last_y, "lcoe_usd_mwh"].mean())
    m_prev = float(y.loc[y["anio"] == prev_y, "lcoe_usd_mwh"].mean())
    if m_prev == 0:
        return ""
    ch = 100.0 * (m_last - m_prev) / m_prev
    return (
        f"**Contexto temporal (mock):** LCOE medio global **~{_fmt_qty_es(m_last)}** vs **~{_fmt_qty_es(m_prev)}** USD/MWh "
        f"(**{last_y}** vs **{prev_y}**; variación relativa **{_fmt_qty_es(ch)}%**)."
    )


def _interp_lcoe_dashboard(lcoe_por_tipo: pd.DataFrame, yoy_note: str = "") -> str:
    """LCOE por tecnología: estadísticas de la media simple del gráfico + LCOE ponderado por MW."""
    if lcoe_por_tipo is None or lcoe_por_tipo.empty:
        return "_Sin LCOE por tecnología._"
    if not {"fuente", "lcoe_promedio", "lcoe_pond_mw"}.issubset(lcoe_por_tipo.columns):
        return "_Faltan columnas para el resumen de LCOE._"
    base = _interp_min_max_mean_rows(
        lcoe_por_tipo,
        "fuente",
        "lcoe_promedio",
        "LCOE (media simple entre proyectos)",
        "USD/MWh",
    )
    lines = [
        base,
        "\n**LCOE ponderado por MW** dentro de cada tecnología (Σ LCOE×MW / Σ MW en el mock):",
    ]
    for _, r in lcoe_por_tipo.sort_values("fuente").iterrows():
        simp = float(r["lcoe_promedio"])
        pond = float(r["lcoe_pond_mw"])
        if pd.isna(pond):
            continue
        dlt = pond - simp
        lines.append(
            f"- **{r['fuente']}:** ponderado ~{_fmt_qty_es(pond)} vs simple ~{_fmt_qty_es(simp)} USD/MWh (Δ ~{_fmt_qty_es(dlt)})."
        )
    if yoy_note:
        lines.append("\n" + yoy_note)
    return "\n".join(lines)


def _interp_consulta_resultado(result_df: pd.DataFrame, query_type: str) -> str:
    if result_df is None or result_df.empty:
        return "_Ejecute una consulta o revise filtros: no hay resultado en memoria._"
    if not {"label", "value"}.issubset(result_df.columns):
        return "_El resultado no tiene el formato `label` / `value` esperado por el mock._"
    d = result_df.dropna(subset=["value"]).copy()
    if d.empty:
        return "_Valores numéricos vacíos en el resultado._"
    labels = set(d["label"].astype(str).str.strip())
    if labels <= {"Dato 1", "Dato 2"}:
        return (
            "_Este tipo de consulta aún devuelve un **resultado ilustrativo** en el motor mock. "
            "Conéctelo a **MatrizEnergeticaCol** para magnitudes reales._"
        )

    qt = (query_type or "").strip()
    if qt == "eficiencia":
        prof = _interp_numeric_profile(d["value"], 2)
        mx, max_labs = _labels_for_max_ties(d, "label", "value")
        mn, min_labs = _labels_for_min_ties(d, "label", "value")
        return (
            f"**Disponibilidad (%)** por proyecto en el resultado: {prof}.\n\n"
            f"- **Mayor disponibilidad:** {_fmt_cat_list(max_labs)} (~{_fmt_qty_es(mx, 2)}%).\n"
            f"- **Menor disponibilidad:** {_fmt_cat_list(min_labs)} (~{_fmt_qty_es(mn, 2)}%)."
        )

    if qt == "inversion":
        tot = float(d["value"].sum())
        if tot <= 0 or tot != tot:
            return "_Suma de inversión no positiva o no numérica._"
        mx, labs = _labels_for_max_ties(d, "label", "value")
        val = mx
        pc = 100.0 * val / tot if tot else 0.0
        if len(labs) == 1:
            return (
                f"**{labs[0]}** concentra la mayor **inversión CAPEX agregada** (~{_fmt_qty_es(val)} M USD), "
                f"aprox. **{_fmt_qty_es(pc)}%** del total mostrado (~{_fmt_qty_es(tot)} M USD en **{len(d)}** categorías)."
            )
        return (
            f"**Empate** al máximo entre {_fmt_cat_list(labs)} (~{_fmt_qty_es(val)} M USD c/u); "
            f"suman ~{_fmt_qty_es(float(d.loc[d['label'].isin(labs), 'value'].sum()))} M USD del total ~{_fmt_qty_es(tot)} M USD."
        )

    if qt == "cobertura":
        tot = float(d["value"].sum())
        if tot <= 0:
            return "_Total de usuarios no positivo._"
        mx, labs = _labels_for_max_ties(d, "label", "value")
        val = mx
        pc = 100.0 * val / tot
        if len(labs) == 1:
            return (
                f"El departamento **{labs[0]}** concentra más **usuarios** agregados (~{_fmt_qty_es(val)}), "
                f"aprox. **{_fmt_qty_es(pc)}%** del subtotal (~{_fmt_qty_es(tot)} usuarios, **{len(d)}** filas)."
            )
        comb = float(d.loc[d["label"].isin(labs), "value"].sum())
        return (
            f"**Empate** al máximo en usuarios entre {_fmt_cat_list(labs)} (~{_fmt_qty_es(val)} c/u); "
            f"en conjunto **~{_fmt_qty_es(comb)}** usuarios (**~{_fmt_qty_es(100.0 * comb / tot)}%** del total "
            f"~{_fmt_qty_es(tot)} usuarios, **{len(d)}** filas)."
        )
    tot = float(d["value"].sum())
    idx = d["value"].idxmax()
    r = d.loc[idx]
    lbl, val = str(r["label"]), float(r["value"])
    if qt == "capacidad" and tot > 0:
        pc = 100.0 * val / tot
        return (
            f"**{lbl}** aporta la mayor **capacidad agregada** (~{_fmt_qty_es(val)} MW), "
            f"alrededor del **{_fmt_qty_es(pc)}%** del subtotal mostrado (~{_fmt_qty_es(tot)} MW, **{len(d)}** categorías)."
        )
    if qt == "lcoe" and len(d) > 1:
        i_min = d["value"].idxmin()
        r0 = d.loc[i_min]
        return (
            f"LCOE **medio** por tecnología en el mock: va de ~{_fmt_qty_es(float(r0['value']))} USD/MWh (**{r0['label']}**, más bajo) "
            f"a ~{_fmt_qty_es(float(r['value']))} USD/MWh (**{lbl}**, más alto) sobre **{len(d)}** fuentes."
        )
    if tot > 0 and tot == tot:
        pc = 100.0 * val / tot
        return (
            f"**{lbl}** concentra el **valor máximo** (~{_fmt_qty_es(val)}), "
            f"~**{_fmt_qty_es(pc)}%** de la suma del resultado (~{_fmt_qty_es(tot)}) en **{len(d)}** filas."
        )
    return f"Valor **máximo** en **{lbl}**: ~{_fmt_qty_es(val)} (unidad según tipo de consulta)."


def _chart_interp(resumen_datos: str, notas_metodologicas: str = "", export_key: str | None = None) -> None:
    """Resumen a partir del dataframe de la gráfica; `export_key` único habilita descarga .md."""
    with st.expander("📌 Interpretación", expanded=False):
        st.markdown("##### Resumen automático")
        st.markdown(resumen_datos)
        if notas_metodologicas.strip():
            st.markdown("##### Lectura metodológica")
            st.markdown(notas_metodologicas)
        if export_key:
            md = "## Resumen automático\n\n" + resumen_datos + "\n"
            if notas_metodologicas.strip():
                md += "\n## Lectura metodológica\n\n" + notas_metodologicas + "\n"
            st.download_button(
                label="Descargar interpretación (.md)",
                data=md.encode("utf-8"),
                file_name=f"interpretacion_{export_key}.md",
                mime="text/markdown",
                key=f"dl_interp_{export_key}",
            )


def _inject_global_css() -> None:
    st.markdown(
        """
        <style>
          :root{
            --color-bg-primary: #f4f7f6;
            --color-bg-secondary: #f4f7f6;
            --color-text-primary: #111111;
            --color-text-secondary: #4b5563;
            --color-accent-main: #006b3f;
            --color-accent-hover: #004d2d;
            --color-box-bg: #f4f7f6;
            --shadow-light: #ffffff;
            --shadow-dark: #d1d9e6;
          }

          .stApp { background: var(--color-bg-primary); color: var(--color-text-primary); }
          [data-testid="stHeader"] { background: transparent; }
          [data-testid="stToolbar"] { right: 0.75rem; }

          .neo-flat{
            background-color: var(--color-box-bg);
            border-radius: 1rem;
            box-shadow: 6px 6px 12px var(--shadow-dark), -6px -6px 12px var(--shadow-light);
          }
          .neo-card{
            background-color: var(--color-box-bg);
            border-radius: 1.25rem;
            box-shadow: 8px 8px 16px var(--shadow-dark), -8px -8px 16px var(--shadow-light);
            border: 1px solid rgba(255, 255, 255, 0.5);
          }

          /* Altair: tipografía y color de títulos */
          .vega-embed summary { display: none; }
          .vega-embed .chart-wrapper { border-radius: 16px; }

          /* Botones estilo "neo-btn" para navegación */
          div[data-testid="stButton"] > button {
            background-color: var(--color-box-bg) !important;
            color: var(--color-text-secondary) !important;
            border-radius: 0.75rem !important;
            border: none !important;
            box-shadow: 5px 5px 10px var(--shadow-dark), -5px -5px 10px var(--shadow-light) !important;
            transition: all 0.2s ease-in-out;
            padding: 0.55rem 0.9rem !important;
            font-weight: 650 !important;
          }
          div[data-testid="stButton"] > button:hover {
            color: var(--color-accent-main) !important;
            box-shadow: 2px 2px 5px var(--shadow-dark), -2px -2px 5px var(--shadow-light) !important;
          }

          /* Botón "activo": lo renderizamos como primary, y lo reestilizamos */
          div[data-testid="stButton"] > button[kind="primary"]{
            background-color: var(--color-box-bg) !important;
            color: var(--color-accent-main) !important;
            box-shadow: inset 4px 4px 8px var(--shadow-dark), inset -4px -4px 8px var(--shadow-light) !important;
            outline: 2px solid rgba(0, 107, 63, 0.22) !important;
            outline-offset: -2px !important;
          }

          /* Ajuste de contenedor principal para parecer "container mx-auto px-6" */
          section.main > div.block-container{
            padding-top: 1.25rem;
            padding-bottom: 2.5rem;
            max-width: 1200px;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _load_data() -> dict[str, pd.DataFrame]:
    regulacion = pd.DataFrame(
        [
            {"id_regulacion": 1, "ley": "Ley 1715", "incentivo": "Deducción Renta 50%", "pct_ahorro": 50.0},
            {"id_regulacion": 2, "ley": "Ley 2099", "incentivo": "Exclusión IVA Bienes/Servicios", "pct_ahorro": 19.0},
        ]
    )

    tipo_energia = pd.DataFrame(
        [
            {"id_tipo_energia": 1, "fuente": ENERGY_HIDRAULICA, "es_convencional": 1, "descripcion": "Embalses y Filo de agua"},
            {"id_tipo_energia": 2, "fuente": "Solar", "es_convencional": 0, "descripcion": "Fotovoltaica Utility Scale"},
            {"id_tipo_energia": 3, "fuente": ENERGY_EOLICA, "es_convencional": 0, "descripcion": "Aerogeneradores Onshore"},
            {"id_tipo_energia": 4, "fuente": ENERGY_GEOTERMICA, "es_convencional": 0, "descripcion": "Vapor de alta entalpía"},
        ]
    )

    proyectos = pd.DataFrame(
        [
            {"id_proyecto": 101, "nombre": "Hidroituango", "depto": "Antioquia", "id_tipo": 1, "capacidad_mw": 2400},
            {"id_proyecto": 102, "nombre": "Guavio", "depto": "Cundinamarca", "id_tipo": 1, "capacidad_mw": 1213},
            {"id_proyecto": 201, "nombre": "La Loma", "depto": "Cesar", "id_tipo": 2, "capacidad_mw": 187},
            {"id_proyecto": 202, "nombre": "Celsia Solar", "depto": "Tolima", "id_tipo": 2, "capacidad_mw": 80},
            {"id_proyecto": 301, "nombre": "Guajira I", "depto": "La Guajira", "id_tipo": 3, "capacidad_mw": 20},
            {"id_proyecto": 302, "nombre": "Alpha Wind", "depto": "La Guajira", "id_tipo": 3, "capacidad_mw": 504},
            {"id_proyecto": 401, "nombre": "Nereidas", "depto": "Caldas", "id_tipo": 4, "capacidad_mw": 50},
        ]
    )

    costos = pd.DataFrame(
        [
            # 2024 (año de referencia principal)
            {"id_proyecto": 101, "anio": 2024, "lcoe_usd_mwh": 47.54, "capex_musd": 2640.0, "opex_musd": 72.0},
            {"id_proyecto": 102, "anio": 2024, "lcoe_usd_mwh": 44.71, "capex_musd": 1334.3, "opex_musd": 36.39},
            {"id_proyecto": 201, "anio": 2024, "lcoe_usd_mwh": 68.64, "capex_musd": 205.7, "opex_musd": 5.61},
            {"id_proyecto": 202, "anio": 2024, "lcoe_usd_mwh": 71.79, "capex_musd": 88.0, "opex_musd": 2.4},
            {"id_proyecto": 301, "anio": 2024, "lcoe_usd_mwh": 41.42, "capex_musd": 22.0, "opex_musd": 0.6},
            {"id_proyecto": 302, "anio": 2024, "lcoe_usd_mwh": 82.13, "capex_musd": 554.4, "opex_musd": 15.12},
            {"id_proyecto": 401, "anio": 2024, "lcoe_usd_mwh": 42.34, "capex_musd": 55.0, "opex_musd": 1.5},
            # 2023 (serie mock mínima para comparación YoY en interpretaciones)
            {"id_proyecto": 101, "anio": 2023, "lcoe_usd_mwh": 48.36, "capex_musd": 2640.0, "opex_musd": 72.0},
            {"id_proyecto": 102, "anio": 2023, "lcoe_usd_mwh": 45.58, "capex_musd": 1334.3, "opex_musd": 36.39},
            {"id_proyecto": 201, "anio": 2023, "lcoe_usd_mwh": 69.96, "capex_musd": 205.7, "opex_musd": 5.61},
            {"id_proyecto": 202, "anio": 2023, "lcoe_usd_mwh": 72.58, "capex_musd": 88.0, "opex_musd": 2.4},
            {"id_proyecto": 301, "anio": 2023, "lcoe_usd_mwh": 42.22, "capex_musd": 22.0, "opex_musd": 0.6},
            {"id_proyecto": 302, "anio": 2023, "lcoe_usd_mwh": 83.46, "capex_musd": 554.4, "opex_musd": 15.12},
            {"id_proyecto": 401, "anio": 2023, "lcoe_usd_mwh": 43.08, "capex_musd": 55.0, "opex_musd": 1.5},
        ]
    )

    cobertura = pd.DataFrame(
        [
            {"id_proyecto": 101, "id_reg": 2, "usuarios": 1080000, "disponibilidad_pct": 98.5},
            {"id_proyecto": 102, "id_reg": 2, "usuarios": 545850, "disponibilidad_pct": 98.5},
            {"id_proyecto": 201, "id_reg": 1, "usuarios": 84150, "disponibilidad_pct": 98.5},
            {"id_proyecto": 202, "id_reg": 1, "usuarios": 36000, "disponibilidad_pct": 98.5},
            {"id_proyecto": 301, "id_reg": 1, "usuarios": 9000, "disponibilidad_pct": 98.5},
            {"id_proyecto": 302, "id_reg": 1, "usuarios": 226800, "disponibilidad_pct": 98.5},
            {"id_proyecto": 401, "id_reg": 1, "usuarios": 22500, "disponibilidad_pct": 98.5},
        ]
    )

    return {
        "regulacion": regulacion,
        "tipo_energia": tipo_energia,
        "proyectos": proyectos,
        "costos": costos,
        "cobertura": cobertura,
    }


@st.cache_data(show_spinner=False)
def _get_data() -> dict[str, pd.DataFrame]:
    return _load_data()


def _format_currency_es_co(amount: float, digits: int = 2) -> str:
    return f"${amount:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _page_header(title: str, subtitle: str = "Transición Energética 2019-2025") -> None:
    st.markdown(
        f"""
        <div class="neo-flat" style="padding: 1rem 1.25rem; margin-bottom: 0.9rem;">
          <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center;">
            <div style="display:flex; align-items:center; justify-content:center; gap: 0.75rem; flex-wrap: wrap;">
              <div style="
                width: 48px; height: 48px; border-radius: 0.9rem;
                display:flex; align-items:center; justify-content:center;
                background: var(--color-accent-main); color: white; font-weight: 900; font-size: 22px;
                box-shadow: 5px 5px 10px var(--shadow-dark), -5px -5px 10px var(--shadow-light);
              ">⚡</div>
              <div style="font-weight: 900; font-size: 1.35rem; color: var(--color-text-primary);">
                {title}
              </div>
            </div>
            <div style="font-size: 0.95rem; color: var(--color-text-secondary); margin-top: 0.25rem;">
              {subtitle}
            </div>
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _top_nav(current_view: str) -> str:
    nav_items: list[tuple[str, str, str]] = [
        ("inicio", "Inicio", "⚡"),
        ("dashboard", "Dashboard", "📊"),
        ("proyectos", "Proyectos", "🏗️"),
        ("costos", "Costos", "💰"),
        ("cobertura", "Cobertura", "📶"),
        ("regulacion", "Regulación", "📄"),
        ("consultas", "Consultas", "🔎"),
    ]

    def _set_view(vid: str) -> None:
        st.session_state["view"] = vid

    cols = st.columns(len(nav_items), gap="small")
    for i, (vid, label, icon) in enumerate(nav_items):
        with cols[i]:
            is_active = current_view == vid
            st.button(
                f"{icon} {label}",
                key=f"nav_{vid}",
                type="primary" if is_active else "secondary",
                use_container_width=True,
                on_click=_set_view,
                args=(vid,),
            )

    return st.session_state.get("view", current_view)


def _view_inicio() -> None:
    st.markdown("### Bienvenido")
    st.markdown(
        """
        <div class="neo-card" style="padding: 18px;">
          <div style="font-weight: 900; font-size: 18px; margin-bottom: 6px; color: var(--color-text-primary);">
            EnergyTrans Colombia
          </div>
          <div style="color: var(--color-text-secondary); font-size: 14px; line-height: 1.5;">
            Este proyecto consolida indicadores clave para explorar la <b>Transición Energética en Colombia (2019–2025)</b>:
            proyectos, costos (LCOE/CAPEX/OPEX), cobertura y marco regulatorio. La app está diseñada para navegación rápida,
            comparaciones visuales y consultas exploratorias.
          </div>
          <div style="margin-top: 10px; color: var(--color-text-secondary); font-size: 13px; line-height: 1.5;">
            Realizado para el <b>curso de Análisis de Datos Integrador</b> de <b>Talento Tech</b>.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            """
            <div class="neo-card" style="padding: 18px;">
              <div style="font-weight: 900; color: var(--color-text-primary);">🎯 Objetivo</div>
              <div style="margin-top: 8px; color: var(--color-text-secondary); font-size: 13px; line-height: 1.5;">
                Entender el avance de tecnologías renovables y su impacto en capacidad instalada, inversión y cobertura.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div class="neo-card" style="padding: 18px;">
              <div style="font-weight: 900; color: var(--color-text-primary);">🧩 Qué encontrarás</div>
              <div style="margin-top: 8px; color: var(--color-text-secondary); font-size: 13px; line-height: 1.55;">
                - Dashboard ejecutivo<br/>
                - Filtros por tipo/departamento/proyecto<br/>
                - Costos con análisis dinámico<br/>
                - Cobertura y disponibilidad<br/>
                - Marco regulatorio e incentivos
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """
            <div class="neo-card" style="padding: 18px;">
              <div style="font-weight: 900; color: var(--color-text-primary);">🗂️ Datos</div>
              <div style="margin-top: 8px; color: var(--color-text-secondary); font-size: 13px; line-height: 1.55;">
                Fuentes esperadas: MinEnergía / UPME.<br/>
                En esta demo, los datos son <b>mock</b> para mostrar la experiencia y el modelo dimensional.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### Integrantes")
    st.markdown(
        """
        <div class="neo-card" style="padding: 18px;">
          <div style="font-weight: 900; color: var(--color-text-primary); margin-bottom: 10px;">👥 Equipo</div>
          <div style="color: var(--color-text-secondary); font-size: 13px; line-height: 1.7;">
            - Claudia Arroyave<br/>
            - Michely Muñoz<br/>
            - Jesus Garcia<br/>
            - Maria Alejandra Colorado Ríos
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Guía rápida")
    g1, g2 = st.columns(2)
    with g1:
        st.markdown(
            """
            <div class="neo-card" style="padding: 18px;">
              <div style="font-weight: 900; color: var(--color-text-primary);">✅ Cómo usar</div>
              <div style="margin-top: 8px; color: var(--color-text-secondary); font-size: 13px; line-height: 1.6;">
                1) Entra a <b>Dashboard</b> para una vista ejecutiva.<br/>
                2) Usa <b>Proyectos</b> para explorar por tipo/departamento/capacidad.<br/>
                3) En <b>Costos</b>, filtra por tipo/año/proyectos para comparar LCOE y CAPEX.<br/>
                4) En <b>Cobertura</b> revisa usuarios y disponibilidad por proyecto.<br/>
                5) En <b>Consultas</b> haz exploración tipo SQL (demo).
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with g2:
        st.markdown(
            """
            <div class="neo-card" style="padding: 18px;">
              <div style="font-weight: 900; color: var(--color-text-primary);">⚠️ Notas de calidad</div>
              <div style="margin-top: 8px; color: var(--color-text-secondary); font-size: 13px; line-height: 1.6;">
                - Los valores actuales son demostrativos (mock).<br/>
                - El estándar de colores por tipo de energía se mantiene en toda la app.<br/>
                - Si conectas datos reales, la vista de Costos habilitará más años automáticamente.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _view_dashboard(d: dict[str, pd.DataFrame]) -> None:
    proyectos = d["proyectos"]
    costos = d["costos"]
    tipo = d["tipo_energia"]
    cobertura = d["cobertura"]

    capacidad_total = float(proyectos["capacidad_mw"].sum())
    anio_kpi = int(costos["anio"].max())
    costos_kpi = costos.loc[costos["anio"] == anio_kpi]
    inversion_total = float(costos_kpi["capex_musd"].sum())
    usuarios_total = int(cobertura["usuarios"].sum())
    lcoe_promedio = float(costos_kpi["lcoe_usd_mwh"].mean())

    st.markdown("### Resumen")

    def stat_card(icon: str, value: str, label: str, change: str, positive: bool = True) -> None:
        change_color = "var(--color-accent-main)" if positive else "#ea580c"
        st.markdown(
            f"""
            <div class="neo-card" style="padding: 18px; text-align:center;">
              <div style="
                width: 64px; height: 64px; border-radius: 999px;
                margin: 0 auto 12px auto;
                display:flex; align-items:center; justify-content:center;
                box-shadow: inset 6px 6px 12px var(--shadow-dark), inset -6px -6px 12px var(--shadow-light);
                color: var(--color-accent-main);
                font-size: 28px;
              ">{icon}</div>
              <div style="font-size: 28px; font-weight: 900; color: var(--color-text-primary); line-height: 1.1;">
                {value}
              </div>
              <div style="margin-top: 2px; font-size: 13px; font-weight: 650; color: var(--color-text-secondary);">
                {label}
              </div>
              <div style="
                margin-top: 10px; display:inline-block;
                padding: 4px 10px; border-radius: 999px;
                box-shadow: inset 6px 6px 12px var(--shadow-dark), inset -6px -6px 12px var(--shadow-light);
                font-size: 12px; font-weight: 650; color: {change_color};
              ">{change}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    r1, r2, r3 = st.columns(3)
    with r1:
        stat_card("🏗️", f"{int(len(proyectos))}", "Proyectos Activos", "↑ 25% vs 2019", positive=True)
    with r2:
        stat_card("⚡", f"{capacidad_total/1000:.1f} GW", "Capacidad Total", "↑ 15% renovable", positive=True)
    with r3:
        stat_card("💰", f"${inversion_total/1000:.1f}B", "Inversión Total", "↑ 40% privado", positive=True)

    r4, r5, r6 = st.columns(3)
    with r4:
        stat_card("👥", f"{usuarios_total/1_000_000:.1f}M", "Usuarios Beneficiados", "98.5% disponibilidad", positive=True)
    with r5:
        stat_card("📉", f"${lcoe_promedio:.2f}", "LCOE Promedio", "↓ 12% vs 2019", positive=False)
    with r6:
        stat_card("🌿", "73%", "Energía Renovable", "Meta 2025: 80%", positive=True)

    st.markdown("### Mix energético Colombia")
    capacidad_por_tipo = (
        proyectos.merge(tipo, left_on="id_tipo", right_on="id_tipo_energia", how="left")
        .groupby("fuente", as_index=False)["capacidad_mw"]
        .sum()
        .rename(columns={"capacidad_mw": "capacidad_mw_total"})
    )
    capacidad_por_tipo["fuente"] = capacidad_por_tipo["fuente"].astype(str).str.strip()

    base_lcoe = (
        costos.loc[costos["anio"] == anio_kpi]
        .merge(proyectos, on="id_proyecto", how="left")
        .merge(tipo, left_on="id_tipo", right_on="id_tipo_energia", how="left")
    )
    rows_lcoe: list[dict[str, object]] = []
    for fuente, g in base_lcoe.groupby("fuente"):
        mw = float(g["capacidad_mw"].sum())
        lcoe_mean = float(g["lcoe_usd_mwh"].mean())
        pond = float((g["lcoe_usd_mwh"] * g["capacidad_mw"]).sum() / mw) if mw > 0 else float("nan")
        rows_lcoe.append({"fuente": fuente, "lcoe_promedio": lcoe_mean, "lcoe_pond_mw": pond})
    lcoe_por_tipo = pd.DataFrame(rows_lcoe)
    lcoe_por_tipo["fuente"] = lcoe_por_tipo["fuente"].astype(str).str.strip()

    capex_opex = costos_kpi.merge(proyectos[["id_proyecto", "nombre"]], on="id_proyecto", how="left")[
        ["nombre", "capex_musd", "opex_musd"]
    ]

    cobertura_proyecto = cobertura.merge(proyectos[["id_proyecto", "nombre"]], on="id_proyecto", how="left")[
        ["nombre", "usuarios"]
    ]

    col_left, col_right = st.columns(2)
    with col_left:
        chart = (
            alt.Chart(capacidad_por_tipo)
            .mark_arc(innerRadius=60)
            .encode(
                theta=alt.Theta("capacidad_mw_total:Q", title="Capacidad (MW)"),
                color=alt.Color("fuente:N", title="Tipo", scale=_energy_color_scale(), sort=ENERGY_COLOR_DOMAIN),
                tooltip=["fuente:N", alt.Tooltip("capacidad_mw_total:Q", title="Capacidad (MW)")],
            )
            .properties(height=320, title="📊 Capacidad por tipo de energía")
        )
        st.altair_chart(chart, use_container_width=True)
        _chart_interp(
            _interp_dominant_share(
                capacidad_por_tipo,
                "fuente",
                "capacidad_mw_total",
                "La fuente con mayor **capacidad instalada** en los proyectos mostrados es",
                "MW",
                "MW",
            ),
            "**Qué muestra:** participación por **tecnología** en **MW** agregados al cierre de la vista.\n\n"
            "**Cómo leerlo:** el ángulo de cada sector es proporcional al subtotal de MW; refleja el **mix** de esta muestra, no el sistema país completo.\n\n"
            "**Matices:** unidades grandes (p. ej. hidro) pueden dominar el pastel aunque existan más plantas de otras tecnologías.",
            export_key="dash_mix_capacidad",
        )

    with col_right:
        chart = (
            alt.Chart(lcoe_por_tipo)
            .mark_bar()
            .encode(
                x=alt.X("fuente:N", title=None),
                y=alt.Y("lcoe_promedio:Q", title="USD/MWh"),
                color=alt.Color("fuente:N", legend=alt.Legend(title="Tipo"), scale=_energy_color_scale(), sort=ENERGY_COLOR_DOMAIN),
                tooltip=["fuente:N", alt.Tooltip("lcoe_promedio:Q", title="LCOE", format=".2f")],
            )
            .properties(height=320, title="💰 LCOE por tecnología")
        )
        st.altair_chart(chart, use_container_width=True)
        _chart_interp(
            _interp_lcoe_dashboard(lcoe_por_tipo, _interp_lcoe_yoy_global(costos)),
            "**Qué muestra:** **LCOE** medio **simple** por **tipo** (barra) para el año más reciente del mock; el resumen contrasta con el LCOE **ponderado por MW** dentro de cada tecnología.\n\n"
            "**Cómo leerlo:** barras más altas = mayor costo nivelado en la media simple de proyectos; la ponderación re-pesa por **capacidad instalada**.\n\n"
            "**Matices:** ninguno de los dos sustituye el LCOE del sistema país; son indicadores de la **muestra** cargada.",
            export_key="dash_lcoe_tech",
        )

    col_left, col_right = st.columns(2)
    with col_left:
        base = alt.Chart(capex_opex).encode(x=alt.X("nombre:N", title=None))
        chart = (
            alt.layer(
                base.mark_bar(color="#0284c7").encode(y=alt.Y("capex_musd:Q", title="M USD"), tooltip=["nombre:N", "capex_musd:Q"]),
                base.mark_bar(color="#f59e0b").encode(y=alt.Y("opex_musd:Q"), tooltip=["nombre:N", "opex_musd:Q"]),
            )
            .resolve_scale(y="shared")
            .properties(height=320, title="📈 Inversión CAPEX vs OPEX")
        )
        st.altair_chart(chart, use_container_width=True)
        _chart_interp(
            _interp_capex_opex_cross(capex_opex),
            "**Qué muestra:** **CAPEX** (azul) y **OPEX** (ámbar) en **M USD** por proyecto presente en costos.\n\n"
            "**Cómo leerlo:** contraste entre **desembolso de inversión** y **gasto operativo**; no hay proporcionalidad esperada por definición.\n\n"
            "**Matices:** escala compartida puede **comprimir** barras de proyectos pequeños frente a mayores.",
            export_key="dash_capex_opex",
        )

    with col_right:
        chart = (
            alt.Chart(cobertura_proyecto)
            .mark_arc()
            .encode(
                theta=alt.Theta("usuarios:Q", title="Usuarios"),
                color=alt.Color("nombre:N", title="Proyecto"),
                tooltip=["nombre:N", alt.Tooltip("usuarios:Q", title="Usuarios")],
            )
            .properties(height=320, title="👥 Cobertura por proyecto")
        )
        st.altair_chart(chart, use_container_width=True)
        _chart_interp(
            _interp_dominant_share(
                cobertura_proyecto,
                "nombre",
                "usuarios",
                "El proyecto con mayor peso en **usuarios** (variable de cobertura del mock) es",
                "usuarios",
                "usuarios",
            ),
            "**Qué muestra:** reparto de **usuarios** por **proyecto** según la tabla de cobertura cargada.\n\n"
            "**Cómo leerlo:** sectores amplios concentran la mayor parte del subtotal de usuarios **en esta muestra**.\n\n"
            "**Matices:** no equivale a población nacional ni a demanda eléctrica; depende de la definición operativa en datos.",
            export_key="dash_cobertura_donut",
        )

    st.markdown("### Tipos de energía renovable")

    capacidad_by_tipo = proyectos.groupby("id_tipo", as_index=False)["capacidad_mw"].sum().rename(columns={"capacidad_mw": "capacidad_total_mw"})
    tipo_cards = tipo.merge(capacidad_by_tipo, left_on="id_tipo_energia", right_on="id_tipo", how="left").fillna({"capacidad_total_mw": 0})

    icon_by_fuente = {
        "Hidráulica": "💧",
        "Solar": "☀️",
        "Eólica": "🌬️",
        "Geotérmica": "🔥",
    }

    def energy_type_card(icon: str, title: str, desc: str, value: str) -> None:
        st.markdown(
            f"""
            <div class="neo-card" style="padding: 18px; text-align:center; position: relative; overflow:hidden;">
              <div style="position:absolute; top:0; left:0; width:100%; height:4px; background: var(--color-accent-main);"></div>
              <div style="font-size: 40px; margin: 8px 0 10px 0; color: var(--color-accent-main);">{icon}</div>
              <div style="font-weight: 850; font-size: 18px; color: var(--color-text-primary);">{title}</div>
              <div style="margin-top: 6px; font-size: 13px; color: var(--color-text-secondary); min-height: 34px;">{desc}</div>
              <div style="margin-top: 10px; font-weight: 900; color: var(--color-accent-main);">{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    cols = st.columns(4)
    for idx, fuente in enumerate(["Hidráulica", "Solar", "Eólica", "Geotérmica"]):
        row = tipo_cards[tipo_cards["fuente"] == fuente]
        if row.empty:
            continue
        r = row.iloc[0]
        mw = float(r["capacidad_total_mw"])
        with cols[idx]:
            energy_type_card(
                icon_by_fuente.get(fuente, "⚡"),
                fuente,
                str(r["descripcion"]),
                f"{mw:,.0f} MW".replace(",", "."),
            )


def _view_proyectos(d: dict[str, pd.DataFrame]) -> None:
    proyectos = d["proyectos"].copy()
    tipo = d["tipo_energia"]
    costos = d["costos"]

    st.markdown("### Filtros")
    col1, col2, col3 = st.columns(3)
    with col1:
        tipo_options = {"Todos": None, **{row["fuente"]: int(row["id_tipo_energia"]) for _, row in tipo.iterrows()}}
        tipo_label = st.selectbox("Filtrar por tipo", list(tipo_options.keys()), index=0)
        filter_tipo = tipo_options[tipo_label]
    with col2:
        deptos = ["Todos"] + sorted(proyectos["depto"].unique().tolist())
        filter_depto = st.selectbox("Filtrar por departamento", deptos, index=0)
    with col3:
        filter_min_cap = st.number_input("Capacidad mínima (MW)", min_value=0, value=0, step=10)

    if filter_tipo is not None:
        proyectos = proyectos[proyectos["id_tipo"] == filter_tipo]
    if filter_depto != "Todos":
        proyectos = proyectos[proyectos["depto"] == filter_depto]
    if filter_min_cap > 0:
        proyectos = proyectos[proyectos["capacidad_mw"] >= float(filter_min_cap)]

    proyectos = proyectos.merge(tipo[["id_tipo_energia", "fuente"]], left_on="id_tipo", right_on="id_tipo_energia", how="left")
    proyectos = proyectos.merge(costos[["id_proyecto", "lcoe_usd_mwh"]], on="id_proyecto", how="left")

    st.markdown("### Resultados")

    def _badge_color(fuente: str) -> tuple[str, str]:
        mapping = {
            "Hidráulica": ("#dcfce7", "#166534"),
            "Solar": ("#d1fae5", "#065f46"),
            "Eólica": ("#ccfbf1", "#0f766e"),
            "Geotérmica": ("#cffafe", "#155e75"),
        }
        return mapping.get(fuente, ("#f3f4f6", "#111827"))

    def _project_card(nombre: str, depto: str, fuente: str, capacidad_mw: float, lcoe: float | None) -> None:
        bg, fg = _badge_color(fuente)
        lcoe_txt = "N/A" if lcoe is None or pd.isna(lcoe) else f"${float(lcoe):.2f}"
        st.markdown(
            f"""
            <div class="neo-card" style="padding: 18px;">
              <div style="font-weight: 850; font-size: 18px; color: var(--color-text-primary); margin-bottom: 10px;">
                {nombre}
              </div>
              <div style="color: var(--color-text-secondary); font-size: 13px; margin-bottom: 6px;">📍 {depto}</div>
              <div style="color: var(--color-text-secondary); font-size: 13px; margin-bottom: 6px;">⚡ {fuente}</div>
              <div style="color: var(--color-text-secondary); font-size: 13px; margin-bottom: 12px;">💰 LCOE: {lcoe_txt}</div>
              <div style="display:flex; gap: 8px; flex-wrap: wrap; margin-top: 6px;">
                <span style="
                  padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: 750;
                  background: {bg}; color: {fg}; border: 1px solid rgba(15,23,42,0.08);
                ">{fuente}</span>
                <span style="
                  padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: 750;
                  background: #f3f4f6; color: #111827; border: 1px solid rgba(15,23,42,0.08);
                ">{int(capacidad_mw)} MW</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if len(proyectos) > 0:
        per_row = 3
        rows = (len(proyectos) + per_row - 1) // per_row
        for r in range(rows):
            cols = st.columns(per_row, gap="medium")
            for c in range(per_row):
                idx = r * per_row + c
                if idx >= len(proyectos):
                    break
                row = proyectos.iloc[idx]
                with cols[c]:
                    _project_card(
                        nombre=str(row["nombre"]),
                        depto=str(row["depto"]),
                        fuente=str(row["fuente"]) if not pd.isna(row["fuente"]) else "Desconocido",
                        capacidad_mw=float(row["capacidad_mw"]),
                        lcoe=None if pd.isna(row["lcoe_usd_mwh"]) else float(row["lcoe_usd_mwh"]),
                    )
        st.markdown("")

    st.dataframe(
        proyectos[["id_proyecto", "nombre", "depto", "fuente", "capacidad_mw", "lcoe_usd_mwh"]]
        .rename(
            columns={
                "id_proyecto": "ID",
                "nombre": "Proyecto",
                "depto": "Departamento",
                "fuente": "Tipo",
                "capacidad_mw": "Capacidad (MW)",
                "lcoe_usd_mwh": "LCOE (USD/MWh)",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )


def _view_costos(d: dict[str, pd.DataFrame]) -> None:
    proyectos = d["proyectos"]
    tipo = d["tipo_energia"]
    costos = (
        d["costos"]
        .merge(proyectos[["id_proyecto", "nombre", "id_tipo"]], on="id_proyecto", how="left")
        .merge(tipo[["id_tipo_energia", "fuente"]], left_on="id_tipo", right_on="id_tipo_energia", how="left")
    )
    costos["fuente"] = costos["fuente"].astype(str).str.strip()

    st.markdown("### Filtros")
    f1, f2, f3, f4 = st.columns([1.2, 2.2, 1.0, 1.4])
    with f1:
        anios = sorted(costos["anio"].dropna().unique().tolist())
        anio_sel = st.selectbox("Año", anios, index=len(anios) - 1 if anios else 0)
    with f2:
        tipo_options = ["Todos"] + sorted(tipo["fuente"].dropna().unique().tolist())
        tipo_sel = st.selectbox("Tipo de energía", tipo_options, index=0)
    with f3:
        metric_sel = st.selectbox("Métrica", ["LCOE", "CAPEX"], index=0)
    with f4:
        order_sel = st.selectbox("Orden", ["Desc", "Asc"], index=0)

    costos_f = costos.copy()
    if anios:
        costos_f = costos_f[costos_f["anio"] == anio_sel]
    if tipo_sel != "Todos":
        costos_f = costos_f[costos_f["fuente"] == tipo_sel]

    proyectos_disponibles = costos_f["nombre"].dropna().unique().tolist()
    proyectos_disponibles = sorted(proyectos_disponibles)
    proyectos_sel = st.multiselect(
        "Proyectos",
        options=proyectos_disponibles,
        default=proyectos_disponibles,
        help="Selecciona uno o varios proyectos. Las gráficas y la tabla se recalculan en tiempo real.",
    )
    if proyectos_sel:
        costos_f = costos_f[costos_f["nombre"].isin(proyectos_sel)]
    else:
        costos_f = costos_f.iloc[0:0]

    # Orden para mejorar lectura (igual para chart y tabla)
    sort_col = "lcoe_usd_mwh" if metric_sel == "LCOE" else "capex_musd"
    costos_f = costos_f.sort_values(sort_col, ascending=(order_sel == "Asc"))

    st.markdown("### Gráficas")
    col1, col2 = st.columns(2)
    with col1:
        chart = (
            alt.Chart(costos_f)
            .mark_bar()
            .encode(
                x=alt.X("nombre:N", title=None, sort=costos_f["nombre"].tolist()),
                y=alt.Y("lcoe_usd_mwh:Q", title="USD/MWh"),
                color=alt.Color("fuente:N", title="Tipo", scale=_energy_color_scale(), sort=ENERGY_COLOR_DOMAIN),
                tooltip=["nombre:N", "fuente:N", alt.Tooltip("lcoe_usd_mwh:Q", title="LCOE")],
            )
            .properties(height=320, title=f"📊 LCOE comparativo {anio_sel}")
        )
        st.altair_chart(chart, use_container_width=True)
        _chart_interp(
            _interp_costos_proyecto_bars(costos_f, "lcoe_usd_mwh", "LCOE", "USD/MWh", anio_sel),
            "**Qué muestra:** **LCOE** por **proyecto** bajo filtros (año, tecnología, multiselect).\n\n"
            "**Cómo leerlo:** compare **costo nivelado** entre plantas; el color es la **tecnología**.\n\n"
            "**Matices:** filtrando un solo tipo, el contraste es **intra-tecnología**.",
            export_key=f"costos_lcoe_{anio_sel}",
        )
    with col2:
        chart = (
            alt.Chart(costos_f)
            .mark_bar()
            .encode(
                x=alt.X("nombre:N", title=None, sort=costos_f["nombre"].tolist()),
                y=alt.Y("capex_musd:Q", title="M USD"),
                color=alt.Color("fuente:N", title="Tipo", scale=_energy_color_scale(), sort=ENERGY_COLOR_DOMAIN),
                tooltip=["nombre:N", "fuente:N", alt.Tooltip("capex_musd:Q", title="CAPEX (M USD)")],
            )
            .properties(height=320, title="💵 CAPEX por proyecto")
        )
        st.altair_chart(chart, use_container_width=True)
        _chart_interp(
            _interp_costos_proyecto_bars(costos_f, "capex_musd", "CAPEX", "M USD", anio_sel),
            "**Qué muestra:** **CAPEX** en **M USD** por proyecto con los mismos filtros que LCOE.\n\n"
            "**Cómo leerlo:** identifica **escala de inversión** relativa; no implica orden igual al LCOE.\n\n"
            "**Matices:** CAPEX alto con LCOE moderado puede reflejar **vida útil** u **hipótesis de generación** distintas.",
            export_key=f"costos_capex_{anio_sel}",
        )

    st.markdown("### Tabla")
    costos_tbl = costos_f.copy()
    costos_tbl["costo_total_musd"] = costos_tbl["capex_musd"] + costos_tbl["opex_musd"]
    st.dataframe(
        costos_tbl[["nombre", "fuente", "anio", "lcoe_usd_mwh", "capex_musd", "opex_musd", "costo_total_musd"]].rename(
            columns={
                "nombre": "Proyecto",
                "fuente": "Tipo",
                "anio": "Año",
                "lcoe_usd_mwh": "LCOE (USD/MWh)",
                "capex_musd": "CAPEX (M USD)",
                "opex_musd": "OPEX (M USD)",
                "costo_total_musd": "Costo total (M USD)",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )


def _view_cobertura(d: dict[str, pd.DataFrame]) -> None:
    proyectos = d["proyectos"]
    tipo = d["tipo_energia"]
    regulacion = d["regulacion"]
    cobertura = (
        d["cobertura"]
        .merge(proyectos[["id_proyecto", "nombre", "id_tipo"]], on="id_proyecto", how="left")
        .merge(tipo[["id_tipo_energia", "fuente"]], left_on="id_tipo", right_on="id_tipo_energia", how="left")
    )
    cobertura["fuente"] = cobertura["fuente"].astype(str).str.strip()

    st.markdown("### Gráficas")
    col1, col2 = st.columns(2)
    with col1:
        chart = (
            alt.Chart(cobertura)
            .mark_bar()
            .encode(
                x=alt.X("nombre:N", title=None),
                y=alt.Y("usuarios:Q", title="Usuarios"),
                color=alt.Color("fuente:N", title="Tipo", scale=_energy_color_scale(), sort=ENERGY_COLOR_DOMAIN),
                tooltip=["nombre:N", "fuente:N", alt.Tooltip("usuarios:Q", title="Usuarios")],
            )
            .properties(height=320, title="👥 Usuarios por proyecto")
        )
        st.altair_chart(chart, use_container_width=True)
        _chart_interp(
            _interp_dominant_share(
                cobertura[["nombre", "usuarios"]],
                "nombre",
                "usuarios",
                "El proyecto con más **usuarios** en esta vista es",
                "usuarios",
                "usuarios",
            ),
            "**Qué muestra:** **usuarios** por **proyecto** y color por **tipo** de planta.\n\n"
            "**Cómo leerlo:** barras más altas concentran más peso en la variable de cobertura **de la muestra**.\n\n"
            "**Matices:** validar definición operativa antes de extrapolar a nivel sectorial.",
            export_key="cobertura_usuarios",
        )
    with col2:
        base = alt.Chart(cobertura).encode(
            x=alt.X("nombre:N", title=None),
            y=alt.Y("disponibilidad_pct:Q", title="Disponibilidad (%)", scale=alt.Scale(domain=[95, 100])),
        )
        chart = alt.layer(
            base.mark_line(color="#006b3f", opacity=0.65),
            base.mark_point(filled=True, size=80).encode(
                color=alt.Color("fuente:N", title="Tipo", scale=_energy_color_scale(), sort=ENERGY_COLOR_DOMAIN),
                tooltip=["nombre:N", "fuente:N", alt.Tooltip("disponibilidad_pct:Q", title="Disponibilidad (%)")],
            ),
        ).properties(height=320, title="✅ Disponibilidad (%)")
        st.altair_chart(chart, use_container_width=True)
        _chart_interp(
            _interp_disponibilidad(cobertura),
            "**Qué muestra:** **disponibilidad (%)** por proyecto; línea de unión y color por **tecnología**.\n\n"
            "**Cómo leerlo:** eje acotado (95–100) para resaltar diferencias pequeñas.\n\n"
            "**Matices:** si la muestra es casi constante, el gráfico se verá plano; con series largas conviene revisar outliers.",
            export_key="cobertura_disponibilidad",
        )

    st.markdown("### Tabla")
    tabla = (
        d["cobertura"]
        .merge(proyectos[["id_proyecto", "nombre"]], on="id_proyecto", how="left")
        .merge(regulacion[["id_regulacion", "ley"]], left_on="id_reg", right_on="id_regulacion", how="left")
    )
    st.dataframe(
        tabla[["nombre", "ley", "usuarios", "disponibilidad_pct"]].rename(
            columns={"nombre": "Proyecto", "ley": "Regulación", "usuarios": "Usuarios", "disponibilidad_pct": "Disponibilidad (%)"}
        ),
        use_container_width=True,
        hide_index=True,
    )


def _view_regulacion(d: dict[str, pd.DataFrame]) -> None:
    regulacion = d["regulacion"].copy()
    st.markdown("### Marco regulatorio")

    for _, r in regulacion.iterrows():
        st.markdown(
            f"""
            <div class="neo-card" style="margin: 10px 0; padding: 16px 18px;">
              <div style="display:flex; justify-content:space-between; gap:12px; align-items:center;">
                <div>
                  <div style="font-weight:800; font-size: 18px;">{r['ley']}</div>
                  <div style="color: var(--color-text-secondary);">{r['incentivo']}</div>
                </div>
                <div style="
                  display:inline-block; padding: 4px 10px; border-radius: 999px;
                  background: rgba(0,107,63,0.10); color: var(--color-accent-main);
                  font-weight: 650; font-size: 12px;">{r['pct_ahorro']}% Ahorro</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### Impacto de incentivos")
    chart = (
        alt.Chart(regulacion)
        .mark_arc(innerRadius=60)
        .encode(
            theta=alt.Theta("pct_ahorro:Q", title="% Ahorro"),
            color=alt.Color("ley:N", title="Ley"),
            tooltip=["ley:N", alt.Tooltip("pct_ahorro:Q", title="% Ahorro")],
        )
        .properties(height=340)
    )
    st.altair_chart(chart, use_container_width=True)
    _chart_interp(
        _interp_regulacion_chart(regulacion),
        "**Qué muestra:** peso relativo del **% de ahorro** asociado a cada **ley** en el dataset normativo cargado.\n\n"
        "**Cómo leerlo:** el sector refleja la magnitud del porcentaje **respecto a la suma** dibujada —no es impacto fiscal en pesos.\n\n"
        "**Matices:** el efecto real depende de **base gravable**, elegibilidad y ordenamiento jurídico.",
        export_key="regulacion_incentivos",
    )


def _generate_query_string(query_type: str, query_energia: str | None, query_anio: int | None) -> str:
    query = "SELECT "
    if query_type == "capacidad":
        query += "SUM(capacidad_mw) as capacidad_total FROM Dim_Proyecto"
    elif query_type == "lcoe":
        query += "AVG(lcoe_usd_mwh) as lcoe_promedio FROM Fact_Costos"
    elif query_type == "inversion":
        query += "SUM(capex_musd) as inversion_total FROM Fact_Costos"
    elif query_type == "cobertura":
        query += "depto, SUM(usuarios) as usuarios FROM Dim_Proyecto JOIN Fact_Cobertura"
    elif query_type == "eficiencia":
        query += "AVG(disponibilidad_pct) as disponibilidad FROM Fact_Cobertura"
    if query_energia:
        query += f" WHERE id_tipo = {query_energia}"
        if query_anio is not None:
            query += f" AND anio = {query_anio}"
    else:
        if query_anio is not None:
            query += f" WHERE anio = {query_anio}"
    return query + ";"


def _execute_query_mock(
    d: dict[str, pd.DataFrame],
    query_type: str,
    query_energia: str | None,
    query_anio: int | None = None,
) -> pd.DataFrame:
    proyectos = d["proyectos"]
    tipo = d["tipo_energia"]
    costos = d["costos"]
    cobertura = d["cobertura"]

    def _ids_en_anio() -> set[int] | None:
        if query_anio is None:
            return None
        return set(costos.loc[costos["anio"] == query_anio, "id_proyecto"].astype(int))

    if query_type == "capacidad":
        df = proyectos.merge(tipo, left_on="id_tipo", right_on="id_tipo_energia", how="left")
        if query_energia:
            df = df[df["id_tipo"].astype(str) == query_energia]
        ids = _ids_en_anio()
        if ids is not None:
            df = df[df["id_proyecto"].isin(ids)]
        out = df.groupby("fuente", as_index=False)["capacidad_mw"].sum().rename(
            columns={"fuente": "label", "capacidad_mw": "value"}
        )
        return out

    if query_type == "lcoe":
        df = costos.merge(proyectos, on="id_proyecto", how="left").merge(
            tipo, left_on="id_tipo", right_on="id_tipo_energia", how="left"
        )
        if query_anio is not None:
            df = df[df["anio"] == query_anio]
        if query_energia:
            df = df[df["id_tipo"].astype(str) == query_energia]
        out = df.groupby("fuente", as_index=False)["lcoe_usd_mwh"].mean().rename(
            columns={"fuente": "label", "lcoe_usd_mwh": "value"}
        )
        return out

    if query_type == "inversion":
        df = costos.merge(proyectos, on="id_proyecto", how="left").merge(
            tipo, left_on="id_tipo", right_on="id_tipo_energia", how="left"
        )
        if query_anio is not None:
            df = df[df["anio"] == query_anio]
        if query_energia:
            df = df[df["id_tipo"].astype(str) == query_energia]
        out = df.groupby("fuente", as_index=False)["capex_musd"].sum().rename(
            columns={"fuente": "label", "capex_musd": "value"}
        )
        return out

    if query_type == "cobertura":
        cov = cobertura.merge(proyectos, on="id_proyecto", how="left")
        ids = _ids_en_anio()
        if ids is not None:
            cov = cov[cov["id_proyecto"].isin(ids)]
        if query_energia:
            cov = cov[cov["id_tipo"].astype(str) == query_energia]
        out = cov.groupby("depto", as_index=False)["usuarios"].sum().rename(
            columns={"depto": "label", "usuarios": "value"}
        )
        return out

    if query_type == "eficiencia":
        cov = cobertura.merge(proyectos, on="id_proyecto", how="left")
        ids = _ids_en_anio()
        if ids is not None:
            cov = cov[cov["id_proyecto"].isin(ids)]
        if query_energia:
            cov = cov[cov["id_tipo"].astype(str) == query_energia]
        out = cov[["nombre", "disponibilidad_pct"]].rename(
            columns={"nombre": "label", "disponibilidad_pct": "value"}
        )
        return out

    return pd.DataFrame([{"label": "Dato 1", "value": 100.0}, {"label": "Dato 2", "value": 200.0}])


def _view_consultas(d: dict[str, pd.DataFrame]) -> None:
    st.markdown("### Constructor de consultas")

    query_type = st.selectbox(
        "Tipo de consulta",
        options=[
            ("capacidad", "Capacidad por tipo"),
            ("lcoe", "LCOE promedio"),
            ("inversion", "Inversión total"),
            ("cobertura", "Cobertura por departamento"),
            ("eficiencia", "Eficiencia operativa"),
        ],
        format_func=lambda x: x[1],
    )[0]

    tipo = d["tipo_energia"]
    energia_options = {"Todos": None, **{row["fuente"]: str(int(row["id_tipo_energia"])) for _, row in tipo.iterrows()}}
    energia_label = st.selectbox("Filtrar por tipo de energía", list(energia_options.keys()), index=0)
    query_energia = energia_options[energia_label]

    anios_q = sorted(d["costos"]["anio"].dropna().unique().tolist(), reverse=True)
    query_anio = int(st.selectbox("Año", anios_q, index=0)) if anios_q else 2024

    if st.button("🔍 Ejecutar consulta", type="primary", use_container_width=False):
        st.session_state["consulta_result"] = _execute_query_mock(
            d, query_type=query_type, query_energia=query_energia, query_anio=query_anio
        )
        st.session_state["consulta_sql"] = _generate_query_string(query_type, query_energia, query_anio)
        st.session_state["consulta_query_type"] = query_type
        st.session_state["consulta_query_anio"] = query_anio

    result_df: pd.DataFrame | None = st.session_state.get("consulta_result")
    sql: str | None = st.session_state.get("consulta_sql")

    st.markdown("### Resultado")
    if result_df is None or sql is None:
        st.info("Los resultados de la consulta aparecerán aquí…")
        return

    st.code(sql, language="sql")
    st.dataframe(result_df, use_container_width=True, hide_index=True)

    chart = (
        alt.Chart(result_df)
        .mark_bar()
        .encode(
            x=alt.X("label:N", title=None),
            y=alt.Y("value:Q", title="Valor"),
            color=alt.Color("label:N", legend=None, scale=alt.Scale(scheme="tableau10")),
            tooltip=["label:N", alt.Tooltip("value:Q", title="Valor")],
        )
        .properties(height=320, title="Visualización de resultados")
    )
    st.altair_chart(chart, use_container_width=True)
    # Solo el tipo guardado al ejecutar; evita mezclar el select actual con un resultado antiguo.
    q_executed = str(st.session_state.get("consulta_query_type") or "")
    _chart_interp(
        _interp_consulta_resultado(result_df, q_executed),
        "**Qué muestra:** barras desde **`label`** y **`value`** del motor en memoria (filtro por año alineado al ejecutar).\n\n"
        "**Cómo leerlo:** palette **Tableau 10** para distinguir categorías arbitrarias (p. ej. departamentos).\n\n"
        "**Matices:** conecte a **`MatrizEnergeticaCol`** para resultados operativos y SQL productivo.",
        export_key="consultas_resultado",
    )


def main() -> None:
    st.set_page_config(page_title="EnergyTrans Colombia", page_icon="⚡", layout="wide")
    _inject_global_css()
    d = _get_data()

    if "view" not in st.session_state:
        st.session_state["view"] = "inicio"

    _page_header("EnergyTrans Colombia")
    view = _top_nav(st.session_state["view"])

    if view == "inicio":
        _view_inicio()
    elif view == "dashboard":
        _view_dashboard(d)
    elif view == "proyectos":
        _view_proyectos(d)
    elif view == "costos":
        _view_costos(d)
    elif view == "cobertura":
        _view_cobertura(d)
    elif view == "regulacion":
        _view_regulacion(d)
    elif view == "consultas":
        _view_consultas(d)
    else:
        st.error("Vista no reconocida.")

    st.divider()
    st.caption("© 2024 EnergyTrans Colombia | Transición Energética 2019-2025")


if __name__ == "__main__":
    main()
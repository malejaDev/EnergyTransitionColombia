from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st


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
            {"id_tipo_energia": 1, "fuente": "Hidráulica", "es_convencional": 1, "descripcion": "Embalses y Filo de agua"},
            {"id_tipo_energia": 2, "fuente": "Solar", "es_convencional": 0, "descripcion": "Fotovoltaica Utility Scale"},
            {"id_tipo_energia": 3, "fuente": "Eólica", "es_convencional": 0, "descripcion": "Aerogeneradores Onshore"},
            {"id_tipo_energia": 4, "fuente": "Geotérmica", "es_convencional": 0, "descripcion": "Vapor de alta entalpía"},
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
            {"id_proyecto": 101, "anio": 2024, "lcoe_usd_mwh": 47.54, "capex_musd": 2640.0, "opex_musd": 72.0},
            {"id_proyecto": 102, "anio": 2024, "lcoe_usd_mwh": 44.71, "capex_musd": 1334.3, "opex_musd": 36.39},
            {"id_proyecto": 201, "anio": 2024, "lcoe_usd_mwh": 68.64, "capex_musd": 205.7, "opex_musd": 5.61},
            {"id_proyecto": 202, "anio": 2024, "lcoe_usd_mwh": 71.79, "capex_musd": 88.0, "opex_musd": 2.4},
            {"id_proyecto": 301, "anio": 2024, "lcoe_usd_mwh": 41.42, "capex_musd": 22.0, "opex_musd": 0.6},
            {"id_proyecto": 302, "anio": 2024, "lcoe_usd_mwh": 82.13, "capex_musd": 554.4, "opex_musd": 15.12},
            {"id_proyecto": 401, "anio": 2024, "lcoe_usd_mwh": 42.34, "capex_musd": 55.0, "opex_musd": 1.5},
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


def _view_dashboard(d: dict[str, pd.DataFrame]) -> None:
    proyectos = d["proyectos"]
    costos = d["costos"]
    tipo = d["tipo_energia"]
    cobertura = d["cobertura"]

    capacidad_total = float(proyectos["capacidad_mw"].sum())
    inversion_total = float(costos["capex_musd"].sum())
    usuarios_total = int(cobertura["usuarios"].sum())
    lcoe_promedio = float(costos["lcoe_usd_mwh"].mean())

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

    lcoe_por_tipo = (
        costos.merge(proyectos, on="id_proyecto", how="left")
        .merge(tipo, left_on="id_tipo", right_on="id_tipo_energia", how="left")
        .groupby("fuente", as_index=False)["lcoe_usd_mwh"]
        .mean()
        .rename(columns={"lcoe_usd_mwh": "lcoe_promedio"})
    )

    capex_opex = costos.merge(proyectos[["id_proyecto", "nombre"]], on="id_proyecto", how="left")[
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
                color=alt.Color("fuente:N", title="Tipo"),
                tooltip=["fuente:N", alt.Tooltip("capacidad_mw_total:Q", title="Capacidad (MW)")],
            )
            .properties(height=320, title="📊 Capacidad por tipo de energía")
        )
        st.altair_chart(chart, use_container_width=True)

    with col_right:
        chart = (
            alt.Chart(lcoe_por_tipo)
            .mark_bar()
            .encode(
                x=alt.X("fuente:N", title=None),
                y=alt.Y("lcoe_promedio:Q", title="USD/MWh"),
                color=alt.Color("fuente:N", legend=None),
                tooltip=["fuente:N", alt.Tooltip("lcoe_promedio:Q", title="LCOE", format=".2f")],
            )
            .properties(height=320, title="💰 LCOE por tecnología")
        )
        st.altair_chart(chart, use_container_width=True)

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
    costos = d["costos"].merge(proyectos[["id_proyecto", "nombre"]], on="id_proyecto", how="left")

    st.markdown("### Gráficas")
    col1, col2 = st.columns(2)
    with col1:
        chart = (
            alt.Chart(costos)
            .mark_bar(color="#006b3f")
            .encode(
                x=alt.X("nombre:N", title=None),
                y=alt.Y("lcoe_usd_mwh:Q", title="USD/MWh"),
                tooltip=["nombre:N", alt.Tooltip("lcoe_usd_mwh:Q", title="LCOE")],
            )
            .properties(height=320, title="📊 LCOE comparativo 2024")
        )
        st.altair_chart(chart, use_container_width=True)
    with col2:
        chart = (
            alt.Chart(costos)
            .mark_bar(color="#006b3f")
            .encode(
                x=alt.X("nombre:N", title=None),
                y=alt.Y("capex_musd:Q", title="M USD"),
                tooltip=["nombre:N", alt.Tooltip("capex_musd:Q", title="CAPEX (M USD)")],
            )
            .properties(height=320, title="💵 CAPEX por proyecto")
        )
        st.altair_chart(chart, use_container_width=True)

    st.markdown("### Tabla")
    costos_tbl = costos.copy()
    costos_tbl["costo_total_musd"] = costos_tbl["capex_musd"] + costos_tbl["opex_musd"]
    st.dataframe(
        costos_tbl[["nombre", "anio", "lcoe_usd_mwh", "capex_musd", "opex_musd", "costo_total_musd"]].rename(
            columns={
                "nombre": "Proyecto",
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
    regulacion = d["regulacion"]
    cobertura = d["cobertura"].merge(proyectos[["id_proyecto", "nombre"]], on="id_proyecto", how="left")

    st.markdown("### Gráficas")
    col1, col2 = st.columns(2)
    with col1:
        chart = (
            alt.Chart(cobertura)
            .mark_bar(color="#0284c7")
            .encode(
                x=alt.X("nombre:N", title=None),
                y=alt.Y("usuarios:Q", title="Usuarios"),
                tooltip=["nombre:N", alt.Tooltip("usuarios:Q", title="Usuarios")],
            )
            .properties(height=320, title="Usuarios por proyecto")
        )
        st.altair_chart(chart, use_container_width=True)
    with col2:
        chart = (
            alt.Chart(cobertura)
            .mark_line(point=alt.OverlayMarkDef(color="#166534"))
            .encode(
                x=alt.X("nombre:N", title=None),
                y=alt.Y("disponibilidad_pct:Q", title="Disponibilidad (%)", scale=alt.Scale(domain=[95, 100])),
                tooltip=["nombre:N", alt.Tooltip("disponibilidad_pct:Q", title="Disponibilidad (%)")],
            )
            .properties(height=320, title="Disponibilidad (%)")
        )
        st.altair_chart(chart, use_container_width=True)

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


def _execute_query_mock(d: dict[str, pd.DataFrame], query_type: str, query_energia: str | None) -> pd.DataFrame:
    proyectos = d["proyectos"]
    tipo = d["tipo_energia"]
    costos = d["costos"]

    if query_type == "capacidad":
        df = proyectos.merge(tipo, left_on="id_tipo", right_on="id_tipo_energia", how="left")
        if query_energia:
            df = df[df["id_tipo"].astype(str) == query_energia]
        out = df.groupby("fuente", as_index=False)["capacidad_mw"].sum().rename(columns={"fuente": "label", "capacidad_mw": "value"})
        return out

    if query_type == "lcoe":
        df = costos.merge(proyectos, on="id_proyecto", how="left").merge(tipo, left_on="id_tipo", right_on="id_tipo_energia", how="left")
        if query_energia:
            df = df[df["id_tipo"].astype(str) == query_energia]
        out = df.groupby("fuente", as_index=False)["lcoe_usd_mwh"].mean().rename(columns={"fuente": "label", "lcoe_usd_mwh": "value"})
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

    query_anio = st.selectbox("Año", [2024, 2023, 2022, 2021, 2020, 2019], index=0)

    if st.button("🔍 Ejecutar consulta", type="primary", use_container_width=False):
        st.session_state["consulta_result"] = _execute_query_mock(d, query_type=query_type, query_energia=query_energia)
        st.session_state["consulta_sql"] = _generate_query_string(query_type, query_energia, query_anio)

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
        .mark_bar(color="#0284c7")
        .encode(
            x=alt.X("label:N", title=None),
            y=alt.Y("value:Q", title="Valor"),
            tooltip=["label:N", alt.Tooltip("value:Q", title="Valor")],
        )
        .properties(height=320, title="Visualización de resultados")
    )
    st.altair_chart(chart, use_container_width=True)


def main() -> None:
    st.set_page_config(page_title="EnergyTrans Colombia", page_icon="⚡", layout="wide")
    _inject_global_css()
    d = _get_data()

    if "view" not in st.session_state:
        st.session_state["view"] = "dashboard"

    _page_header("EnergyTrans Colombia")
    view = _top_nav(st.session_state["view"])

    if view == "dashboard":
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

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


def _chart_interp(text: str) -> None:
    """Interpretación breve para el usuario (lectura tipo científico de datos)."""
    with st.expander("📌 Interpretación", expanded=False):
        st.markdown(text)


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

          /* Landing page (portada) */
          .lp-wrap { font-family: "Segoe UI", system-ui, sans-serif; }
          .lp-hero{
            position: relative;
            overflow: hidden;
            border-radius: 1.35rem;
            padding: 2.25rem 1.75rem 2rem;
            margin-bottom: 1.5rem;
            background: linear-gradient(135deg, #e8f5ef 0%, #f4f7f6 45%, #dff4e8 100%);
            border: 1px solid rgba(0, 107, 63, 0.12);
            box-shadow: 10px 10px 24px var(--shadow-dark), -8px -8px 20px var(--shadow-light);
          }
          .lp-hero::before{
            content:"";
            position:absolute; inset:0;
            background: radial-gradient(ellipse 80% 60% at 100% 0%, rgba(0, 107, 63, 0.14), transparent 55%),
                        radial-gradient(ellipse 60% 50% at 0% 100%, rgba(2, 132, 199, 0.1), transparent 50%);
            pointer-events:none;
          }
          .lp-hero-inner{ position: relative; z-index: 1; max-width: 720px; }
          .lp-badge{
            display: inline-block;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            color: var(--color-accent-main);
            background: rgba(255,255,255,0.75);
            padding: 0.35rem 0.75rem;
            border-radius: 999px;
            margin-bottom: 0.85rem;
            box-shadow: inset 1px 1px 3px rgba(0,0,0,0.06);
          }
          .lp-h1{
            font-size: clamp(1.55rem, 3.2vw, 2.15rem);
            font-weight: 900;
            line-height: 1.15;
            color: var(--color-text-primary);
            margin: 0 0 0.65rem 0;
            letter-spacing: -0.02em;
          }
          .lp-h1 span{ color: var(--color-accent-main); }
          .lp-lead{
            font-size: 1.05rem;
            line-height: 1.55;
            color: var(--color-text-secondary);
            margin: 0 0 1.1rem 0;
          }
          .lp-stats{
            display: flex; flex-wrap: wrap; gap: 0.65rem 1rem;
            margin-top: 1.1rem;
          }
          .lp-stat{
            background: rgba(255,255,255,0.82);
            border-radius: 0.85rem;
            padding: 0.55rem 0.95rem;
            box-shadow: 3px 3px 8px var(--shadow-dark), -2px -2px 6px var(--shadow-light);
            min-width: 5.5rem;
          }
          .lp-stat-val{ font-size: 1.15rem; font-weight: 900; color: var(--color-accent-main); }
          .lp-stat-lab{ font-size: 0.72rem; color: var(--color-text-secondary); font-weight: 650; margin-top: 0.15rem; }
          .lp-section-title{
            font-size: 1.05rem;
            font-weight: 850;
            color: var(--color-text-primary);
            margin: 1.75rem 0 0.85rem;
            letter-spacing: -0.01em;
          }
          .lp-grid2{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 0.85rem; }
          .lp-card{
            background: var(--color-box-bg);
            border-radius: 1.1rem;
            padding: 1.1rem 1.15rem;
            border: 1px solid rgba(255,255,255,0.55);
            box-shadow: 6px 6px 14px var(--shadow-dark), -5px -5px 12px var(--shadow-light);
            transition: transform 0.18s ease, box-shadow 0.18s ease;
          }
          .lp-card:hover{ transform: translateY(-2px); box-shadow: 8px 8px 18px var(--shadow-dark), -6px -6px 14px var(--shadow-light); }
          .lp-card-ico{ font-size: 1.5rem; margin-bottom: 0.35rem; }
          .lp-card h3{ margin: 0 0 0.4rem; font-size: 0.98rem; font-weight: 800; color: var(--color-text-primary); }
          .lp-card p{ margin: 0; font-size: 0.88rem; line-height: 1.5; color: var(--color-text-secondary); }
          .lp-pipeline{
            display: flex; flex-wrap: wrap; align-items: stretch; gap: 0.6rem;
            margin-top: 0.5rem;
          }
          .lp-step{
            flex: 1 1 140px;
            background: var(--color-box-bg);
            border-radius: 0.95rem;
            padding: 0.85rem 1rem;
            border: 1px solid rgba(0, 107, 63, 0.1);
            box-shadow: 4px 4px 10px var(--shadow-dark), -3px -3px 8px var(--shadow-light);
            position: relative;
          }
          .lp-step-num{
            position:absolute; top: -0.45rem; left: 10px;
            background: var(--color-accent-main); color: white;
            font-size: 0.65rem; font-weight: 800; padding: 0.15rem 0.45rem; border-radius: 6px;
          }
          .lp-step strong{ display:block; font-size: 0.82rem; margin-bottom: 0.25rem; color: var(--color-text-primary); }
          .lp-step span{ font-size: 0.78rem; color: var(--color-text-secondary); line-height: 1.45; }
          .lp-team{
            font-size: 0.88rem;
            color: var(--color-text-secondary);
            line-height: 1.65;
            padding: 0.95rem 1.1rem;
            background: rgba(255,255,255,0.55);
            border-radius: 1rem;
            border: 1px dashed rgba(0, 107, 63, 0.22);
          }
          .lp-quote{
            margin: 1rem 0 0;
            padding: 0.9rem 1.1rem;
            border-left: 4px solid var(--color-accent-main);
            background: rgba(0, 107, 63, 0.06);
            border-radius: 0 0.75rem 0.75rem 0;
            font-size: 0.92rem;
            color: var(--color-text-secondary);
            line-height: 1.5;
            font-style: italic;
          }
          .lp-kicker{
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: var(--color-accent-main);
            margin: 1.5rem 0 0.35rem;
          }
          .lp-sub{
            font-size: 0.92rem;
            color: var(--color-text-secondary);
            line-height: 1.45;
            margin: 0 0 1rem 0;
            max-width: 52rem;
          }
          .lp-uxstrip{
            display: flex; flex-wrap: wrap; gap: 0.5rem;
            margin: 0.75rem 0 1.25rem;
          }
          .lp-chip{
            font-size: 0.72rem;
            font-weight: 750;
            padding: 0.35rem 0.65rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.85);
            border: 1px solid rgba(0, 107, 63, 0.18);
            color: var(--color-text-primary);
            box-shadow: 2px 2px 6px var(--shadow-dark), -2px -2px 5px var(--shadow-light);
          }
          .lp-bento{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(270px, 1fr));
            gap: 0.95rem;
            margin-top: 0.35rem;
          }
          .lp-mod{
            position: relative;
            background: linear-gradient(165deg, #f8faf9 0%, var(--color-box-bg) 100%);
            border-radius: 1.05rem;
            padding: 1rem 1.05rem 0.85rem;
            border: 1px solid rgba(0, 107, 63, 0.11);
            box-shadow: 6px 6px 14px var(--shadow-dark), -5px -5px 12px var(--shadow-light);
            transition: transform 0.16s ease, box-shadow 0.16s ease;
          }
          .lp-mod:hover{
            transform: translateY(-3px);
            box-shadow: 9px 9px 20px var(--shadow-dark), -6px -6px 14px var(--shadow-light);
          }
          .lp-mod-top{
            display:flex; justify-content: space-between; align-items: flex-start; gap: 8px;
            margin-bottom: 0.45rem;
          }
          .lp-mod-ico{ font-size: 1.35rem; line-height: 1; }
          .lp-mod-badge{
            font-size: 0.62rem; font-weight: 850;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            padding: 0.22rem 0.5rem;
            border-radius: 6px;
            white-space: nowrap;
          }
          .lp-mod-badge.filters{ background: rgba(2, 132, 199, 0.14); color: #0369a1; }
          .lp-mod-badge.nofilter{ background: rgba(245, 158, 11, 0.18); color: #b45309; }
          .lp-mod-badge.builder{ background: rgba(16, 185, 129, 0.16); color: #047857; }
          .lp-mod h4{
            margin: 0 0 0.45rem 0;
            font-size: 1rem;
            font-weight: 900;
            color: var(--color-text-primary);
            letter-spacing: -0.02em;
          }
          .lp-mod ul{
            margin: 0; padding-left: 1.05rem;
            font-size: 0.8rem;
            line-height: 1.48;
            color: var(--color-text-secondary);
          }
          .lp-mod .lp-interp{
            margin-top: 0.55rem;
            font-size: 0.72rem;
            font-weight: 750;
            color: var(--color-accent-main);
            display: flex; align-items: center; gap: 0.35rem;
          }
          .lp-mini-vis{
            display: flex; align-items: flex-end; justify-content: center;
            gap: 5px;
            height: 52px;
            margin-top: 0.65rem;
            padding: 0 0.25rem;
          }
          .lp-mini-vis span{
            flex: 1;
            max-width: 22px;
            border-radius: 5px 5px 2px 2px;
            opacity: 0.92;
          }
          .lp-mini-donut{
            width: 52px; height: 52px; border-radius: 50%;
            margin: 0.6rem auto 0;
            background: conic-gradient(#0284c7 0deg 120deg, #f59e0b 120deg 200deg, #10b981 200deg 280deg, #ef4444 280deg 360deg);
            box-shadow: inset 0 0 0 14px var(--color-box-bg);
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


def _page_header(title: str, subtitle: str = "Demostración con datos alineados al SQL (costos 2024)") -> None:
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
        ("inicio", "Inicio", "🏠"),
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


def _go_view(vid: str) -> None:
    """Navegación programática (p. ej. CTAs del landing)."""
    st.session_state["view"] = vid


def _view_inicio(d: dict[str, pd.DataFrame]) -> None:
    """Portada tipo landing: propuesta de valor, CTAs, pilas analíticas y confianza."""
    proyectos = d["proyectos"]
    tipo = d["tipo_energia"]
    regulacion = d["regulacion"]
    n_proyectos = int(len(proyectos))
    mw_total = float(proyectos["capacidad_mw"].sum())
    gw_str = f"{mw_total / 1000:.2f}".replace(".", ",")
    n_tipos = int(len(tipo))
    n_normas = int(len(regulacion))

    st.markdown(
        f"""
        <div class="lp-wrap">
          <div class="lp-hero">
            <div class="lp-hero-inner">
              <div class="lp-badge">Proyecto académico · Talento Tech · Análisis de datos</div>
              <h1 class="lp-h1">Transición energética en Colombia:<br/><span>una lectura integrada</span> de capacidad, costos y cobertura</h1>
              <p class="lp-lead">
                En cada pestaña encontrarás <strong>gráficos interactivos (Altair)</strong>, <strong>filtros</strong> cuando aplica,
                <strong>tablas</strong> y, bajo cada visual, un desplegable <strong>«📌 Interpretación»</strong> con lectura de datos
                (qué muestra, cómo leerlo y matices). Esta portada resume <strong>exactamente</strong> lo que verás al navegar.
              </p>
              <div class="lp-stats">
                <div class="lp-stat"><div class="lp-stat-val">{n_proyectos}</div><div class="lp-stat-lab">Proyectos (muestra)</div></div>
                <div class="lp-stat"><div class="lp-stat-val">{gw_str} GW</div><div class="lp-stat-lab">Capacidad agregada</div></div>
                <div class="lp-stat"><div class="lp-stat-val">{n_tipos}</div><div class="lp-stat-lab">Tipos de energía</div></div>
                <div class="lp-stat"><div class="lp-stat-val">{n_normas}</div><div class="lp-stat-lab">Marcos normativos</div></div>
              </div>
            </div>
          </div>
          <div class="lp-quote">
            &ldquo;¿Cómo se compone la capacidad y la economía por tecnología, y qué patrón emerge al cruzar costos con cobertura y regulación?&rdquo;
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("##### Ir directo a cada experiencia")
    r1c1, r1c2, r1c3, r1c4 = st.columns(4, gap="small")
    with r1c1:
        st.button(
            "📊 Dashboard",
            key="lp_cta_dashboard",
            use_container_width=True,
            type="primary",
            on_click=_go_view,
            args=("dashboard",),
            help="Resumen + 4 gráficos Altair + tarjetas por tecnología",
        )
    with r1c2:
        st.button(
            "🏗️ Proyectos",
            key="lp_cta_proyectos",
            use_container_width=True,
            on_click=_go_view,
            args=("proyectos",),
            help="3 filtros + tarjetas + tabla",
        )
    with r1c3:
        st.button(
            "💰 Costos",
            key="lp_cta_costos",
            use_container_width=True,
            on_click=_go_view,
            args=("costos",),
            help="5 filtros + 2 gráficos + tabla",
        )
    with r1c4:
        st.button(
            "📶 Cobertura",
            key="lp_cta_cobertura",
            use_container_width=True,
            on_click=_go_view,
            args=("cobertura",),
            help="2 gráficos + tabla regulación",
        )
    r2c1, r2c2 = st.columns(2, gap="small")
    with r2c1:
        st.button(
            "📄 Regulación",
            key="lp_cta_regulacion",
            use_container_width=True,
            on_click=_go_view,
            args=("regulacion",),
            help="Tarjetas normativa + donut",
        )
    with r2c2:
        st.button(
            "🔎 Consultas",
            key="lp_cta_consultas",
            use_container_width=True,
            on_click=_go_view,
            args=("consultas",),
            help="Constructor + SQL + barras + interpretación",
        )

    st.markdown(
        """
        <div class="lp-kicker">Mapa de la aplicación</div>
        <p class="lp-sub">
          Lo siguiente corresponde <strong>uno a uno</strong> con el código de <code>streamlit_app.py</code>:
          mismos tipos de gráfico, mismos controles y el mismo patrón de <strong>Interpretación</strong> bajo cada Altair.
        </p>
        <div class="lp-uxstrip">
          <span class="lp-chip">Altair + tooltips</span>
          <span class="lp-chip">Color por tecnología (4 fuentes)</span>
          <span class="lp-chip">📌 Interpretación en expander</span>
          <span class="lp-chip">Neumórfico + contraste legible</span>
        </div>
        <div class="lp-bento">
          <div class="lp-mod">
            <div class="lp-mod-top">
              <span class="lp-mod-ico">📊</span>
              <span class="lp-mod-badge nofilter">Sin filtros</span>
            </div>
            <h4>Dashboard</h4>
            <ul>
              <li><strong>Resumen:</strong> 6 tarjetas KPI (proyectos, capacidad, CAPEX, usuarios, LCOE, FNCER).</li>
              <li><strong>Gráficos:</strong> donut <em>Capacidad por tipo</em>; barras <em>LCOE por tecnología</em>; barras superpuestas <em>CAPEX vs OPEX</em>; donut <em>Cobertura por proyecto</em>.</li>
              <li><strong>Fila inferior:</strong> 4 tarjetas neumórficas por tecnología (icono, descripción, MW).</li>
            </ul>
            <div class="lp-interp">📌 Un expander «Interpretación» debajo de cada gráfico</div>
            <div class="lp-mini-donut" title="Mix capacidad"></div>
          </div>
          <div class="lp-mod">
            <div class="lp-mod-top">
              <span class="lp-mod-ico">🏗️</span>
              <span class="lp-mod-badge filters">3 filtros</span>
            </div>
            <h4>Proyectos</h4>
            <ul>
              <li><strong>Filtros:</strong> <code>selectbox</code> tipo (o Todos); <code>selectbox</code> departamento; <code>number_input</code> capacidad mínima (MW).</li>
              <li><strong>Salida:</strong> rejilla de <strong>tarjetas</strong> (nombre, depto, tipo, LCOE, badges) + <strong>tabla</strong> interactiva (ID, proyecto, depto, tipo, MW, LCOE).</li>
            </ul>
            <div class="lp-interp">Enfoque exploratorio; no hay gráfico de barras en esta vista</div>
            <div class="lp-mini-vis" aria-hidden="true">
              <span style="height:35%;background:#0284c7"></span><span style="height:55%;background:#f59e0b"></span>
              <span style="height:42%;background:#10b981"></span><span style="height:28%;background:#ef4444"></span>
            </div>
          </div>
          <div class="lp-mod">
            <div class="lp-mod-top">
              <span class="lp-mod-ico">💰</span>
              <span class="lp-mod-badge filters">5 filtros + multiselect</span>
            </div>
            <h4>Costos</h4>
            <ul>
              <li><strong>Filtros:</strong> año; tipo de energía; métrica foco (LCOE / CAPEX); orden Asc/Desc; <strong>multiselect</strong> de proyectos (recalcula gráficos y tabla).</li>
              <li><strong>Gráficos:</strong> barras <em>LCOE comparativo</em> por proyecto; barras <em>CAPEX por proyecto</em> (color por tecnología).</li>
              <li><strong>Tabla:</strong> proyecto, tipo, año, LCOE, CAPEX, OPEX, costo total.</li>
            </ul>
            <div class="lp-interp">📌 Interpretación específica para LCOE y para CAPEX</div>
            <div class="lp-mini-vis" aria-hidden="true">
              <span style="height:62%;background:#0284c7"></span><span style="height:45%;background:#f59e0b"></span>
              <span style="height:70%;background:#10b981"></span><span style="height:38%;background:#ef4444"></span>
              <span style="height:52%;background:#0284c7"></span>
            </div>
          </div>
          <div class="lp-mod">
            <div class="lp-mod-top">
              <span class="lp-mod-ico">📶</span>
              <span class="lp-mod-badge nofilter">Gráfico + tabla</span>
            </div>
            <h4>Cobertura</h4>
            <ul>
              <li><strong>Gráficos:</strong> barras <em>Usuarios por proyecto</em>; combinado línea + puntos <em>Disponibilidad %</em> (eje 95–100%, color por tipo).</li>
              <li><strong>Tabla:</strong> proyecto, <strong>ley</strong> de regulación asociada, usuarios, disponibilidad.</li>
            </ul>
            <div class="lp-interp">📌 Dos interpretaciones (usuarios + disponibilidad)</div>
            <div class="lp-mini-vis" aria-hidden="true">
              <span style="height:48%;background:#006b3f"></span><span style="height:52%;background:#0284c7"></span>
              <span style="height:50%;background:#f59e0b"></span>
            </div>
          </div>
          <div class="lp-mod">
            <div class="lp-mod-top">
              <span class="lp-mod-ico">📄</span>
              <span class="lp-mod-badge nofilter">Tarjetas + donut</span>
            </div>
            <h4>Regulación</h4>
            <ul>
              <li><strong>Contenido:</strong> tarjetas por ley (incentivo + badge % ahorro).</li>
              <li><strong>Gráfico:</strong> donut <em>Impacto de incentivos</em> (theta = % ahorro por ley).</li>
            </ul>
            <div class="lp-interp">📌 Interpretación sobre lectura normativa vs impacto fiscal real</div>
            <div class="lp-mini-donut" style="margin-top:0.5rem;max-width:52px;height:52px;background:conic-gradient(#006b3f 0deg 200deg,#0369a1 200deg 360deg);box-shadow:inset 0 0 0 12px var(--color-box-bg)"></div>
          </div>
          <div class="lp-mod">
            <div class="lp-mod-top">
              <span class="lp-mod-ico">🔎</span>
              <span class="lp-mod-badge builder">Constructor demo</span>
            </div>
            <h4>Consultas</h4>
            <ul>
              <li><strong>Controles:</strong> tipo de consulta (capacidad, LCOE, inversión, cobertura, eficiencia); filtro tipo de energía; año para el SQL mostrado.</li>
              <li><strong>Salida:</strong> bloque <code>st.code</code> con la sentencia; <strong>dataframe</strong>; gráfico de <strong>barras</strong> del resultado + 📌 Interpretación.</li>
            </ul>
            <div class="lp-interp">La ejecución es mock; el SQL es plantilla hacia MySQL</div>
            <div class="lp-mini-vis" aria-hidden="true">
              <span style="height:40%;background:#006b3f"></span><span style="height:65%;background:#006b3f"></span>
              <span style="height:50%;background:#006b3f"></span>
            </div>
          </div>
        </div>
        <div class="lp-section-title" style="margin-top:1.35rem;">Por qué funciona como producto de datos</div>
        <div class="lp-grid2">
          <div class="lp-card">
            <div class="lp-card-ico">📐</div>
            <h3>Mismo modelo que el SQL</h3>
            <p>Proyectos, tipos, costos, cobertura y regulación se alinean con <code>MatrizEnergeticaCol</code> para narrativa trazable.</p>
          </div>
          <div class="lp-card">
            <div class="lp-card-ico">🧪</div>
            <h3>Filtros = hipótesis</h3>
            <p>Cada <code>selectbox</code> o multiselect te permite probar escenarios sin salir del navegador.</p>
          </div>
          <div class="lp-card">
            <div class="lp-card-ico">📌</div>
            <h3>Interpretación integrada</h3>
            <p>No solo “ver el gráfico”: el expander ancla criterios de lectura y límites del mock.</p>
          </div>
          <div class="lp-card">
            <div class="lp-card-ico">🔗</div>
            <h3>Tres capas</h3>
            <p>Cuaderno (método), MySQL (persistencia), Streamlit (exploración) — un solo hilo conceptual.</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="lp-section-title">Flujo de trabajo del proyecto</div>
        <div class="lp-pipeline">
          <div class="lp-step"><span class="lp-step-num">1</span><strong>Cuaderno Jupyter</strong><span>EDA, calidad, features e historia analítica (serie sintética 2020–2026).</span></div>
          <div class="lp-step"><span class="lp-step-num">2</span><strong>MySQL / Workbench</strong><span>Esquema MatrizEnergeticaCol, hechos y consultas reproducibles.</span></div>
          <div class="lp-step"><span class="lp-step-num">3</span><strong>Streamlit</strong><span>Exploración operativa; hoy mock alineado al SQL (costos 2024).</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="lp-section-title">Equipo</div>
        <div class="lp-team">
          <strong style="color:var(--color-text-primary);">EnergyTransitionColombia</strong> ·
          Claudia Arroyave · Michely Muñoz · Jesus Garcia · Maria Alejandra Colorado Ríos<br/>
          <span style="font-size:0.82rem;">Curso <strong>Análisis de Datos Integrador</strong> · Referentes metodológicos tipo XM / UPME / SGC en el cuaderno (datos sintéticos).</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("📋 Guía rápida (rutas + interpretaciones)", expanded=False):
        st.markdown(
            """
            1. **Dashboard** — 6 KPI + 4 gráficos Altair (2 donuts, barras LCOE, barras CAPEX/OPEX) + tarjetas por tecnología. Abre **📌 Interpretación** bajo cada gráfico.  
            2. **Proyectos** — Filtros tipo / departamento / MW mínimos → tarjetas + `st.dataframe`.  
            3. **Costos** — Año, tipo, métrica LCOE|CAPEX, orden, multiselect de proyectos → 2 gráficos de barras + tabla; dos interpretaciones.  
            4. **Cobertura** — Barras usuarios + línea/puntos disponibilidad + tabla con ley reguladora.  
            5. **Regulación** — Tarjetas por ley + donut de incentivos + interpretación.  
            6. **Consultas** — Tipo de consulta, energía, año → SQL en pantalla, tabla y barras (mock).
            """
        )

    with st.expander("⚠️ Datos, alcance temporal y uso del tablero", expanded=False):
        st.markdown(
            """
            - Esta **demo web** usa datos **mock en memoria** alineados al modelo del repositorio (costos con corte **2024**).  
            - En el script SQL, **Fact_Generacion** incluye una serie diaria **2020-01-01 a 2020-05-21**; esa serie **aún no** se grafica en Streamlit.  
            - El archivo **Transicion_Energetica.ipynb** usa un horizonte **2020–2026 sintético** para el análisis; no es el mismo universo de fechas que los INSERT actuales del SQL.  
            - Las cifras **no** son estadística oficial: para inferencia sobre el sistema real, sustituye por fuentes primarias y valida en producción.
            """
        )


def _view_dashboard(d: dict[str, pd.DataFrame]) -> None:
    proyectos = d["proyectos"]
    costos = d["costos"]
    tipo = d["tipo_energia"]
    cobertura = d["cobertura"]

    capacidad_total = float(proyectos["capacidad_mw"].sum())
    ren_cap = float(proyectos.loc[proyectos["id_tipo"].isin([2, 3, 4]), "capacidad_mw"].sum())
    fncer_pct = round(100.0 * ren_cap / capacidad_total, 1) if capacidad_total else 0.0
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
        stat_card("🏗️", f"{int(len(proyectos))}", "Proyectos en la muestra", "Dataset demo", positive=True)
    with r2:
        stat_card("⚡", f"{capacidad_total/1000:.1f} GW", "Capacidad total (muestra)", "Suma MW en proyectos demo", positive=True)
    with r3:
        stat_card("💰", f"${inversion_total/1000:.1f}B", "CAPEX agregado", "Suma Fact_Costos / mock (2024)", positive=True)

    r4, r5, r6 = st.columns(3)
    with r4:
        stat_card("👥", f"{usuarios_total/1_000_000:.1f}M", "Usuarios Beneficiados", "98.5% disponibilidad", positive=True)
    with r5:
        stat_card("📉", f"${lcoe_promedio:.2f}", "LCOE promedio (2024)", "Mismo año que Fact_Costos", positive=True)
    with r6:
        stat_card("🌿", f"{fncer_pct}%", "Capacidad FNCER", "Solar+eólica+geoterma / total MW", positive=True)

    st.markdown("### Mix energético Colombia")
    capacidad_por_tipo = (
        proyectos.merge(tipo, left_on="id_tipo", right_on="id_tipo_energia", how="left")
        .groupby("fuente", as_index=False)["capacidad_mw"]
        .sum()
        .rename(columns={"capacidad_mw": "capacidad_mw_total"})
    )
    capacidad_por_tipo["fuente"] = capacidad_por_tipo["fuente"].astype(str).str.strip()

    lcoe_por_tipo = (
        costos.merge(proyectos, on="id_proyecto", how="left")
        .merge(tipo, left_on="id_tipo", right_on="id_tipo_energia", how="left")
        .groupby("fuente", as_index=False)["lcoe_usd_mwh"]
        .mean()
        .rename(columns={"lcoe_usd_mwh": "lcoe_promedio"})
    )
    lcoe_por_tipo["fuente"] = lcoe_por_tipo["fuente"].astype(str).str.strip()

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
                color=alt.Color("fuente:N", title="Tipo", scale=_energy_color_scale(), sort=ENERGY_COLOR_DOMAIN),
                tooltip=["fuente:N", alt.Tooltip("capacidad_mw_total:Q", title="Capacidad (MW)")],
            )
            .properties(height=320, title="📊 Capacidad por tipo de energía")
        )
        st.altair_chart(chart, use_container_width=True)
        _chart_interp(
            "**Qué muestra:** participación de cada **tecnología** en la **capacidad instalada** (MW agregados).\n\n"
            "**Cómo leerlo:** el ángulo de cada sector es proporcional a la capacidad; compara **mix** relativo, no volumen absoluto del sistema país.\n\n"
            "**Matices:** proyectos grandes (p. ej. hidro) pueden dominar el pastel aunque otras tecnologías crezcan en número de plantas."
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
            "**Qué muestra:** **LCOE promedio** (USD/MWh) por **tipo de energía** en el conjunto de proyectos con costo registrado.\n\n"
            "**Cómo leerlo:** barras más altas implican **mayor costo nivelado** unitario en esta muestra; el color sigue la convención por tecnología.\n\n"
            "**Matices:** es un **promedio simple** por fuente; no pondera por generación ni por tamaño hasta que se use un factor de ponderación explícito."
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
            "**Qué muestra:** para cada **proyecto**, **CAPEX** (azul) y **OPEX** (ámbar) en millones de USD.\n\n"
            "**Cómo leerlo:** compara **intensidad de inversión** vs. **costo operativo anualizado**; proyectos con CAPEX alto no siempre tienen OPEX proporcionalmente alto.\n\n"
            "**Matices:** la superposición en una misma escala facilita la comparación visual, pero valores muy distintos entre proyectos pueden comprimir la lectura de los más pequeños."
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
            "**Qué muestra:** distribución de **usuarios** asociados a cada **proyecto** en el dataset (no es la población de Colombia).\n\n"
            "**Cómo leerlo:** sectores grandes concentran mayor peso en **cobertura declarada**; identifica qué proyecto arrastra el reparto.\n\n"
            "**Matices:** no confundir con **demanda energética** ni con cobertura de redes sin definición explícita de la variable."
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
            "**Qué muestra:** **LCOE** por **proyecto** bajo los filtros activos (año, tecnología, multiselección de proyectos).\n\n"
            "**Cómo leerlo:** ordena jerárquicamente el **costo unitario** entre plantas comparables; el color refleja la **tecnología**.\n\n"
            "**Matices:** al filtrar a un solo tipo, todas las barras comparten categoría —el valor está en comparar proyectos dentro de esa tecnología."
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
            "**Qué muestra:** **CAPEX** (inversión) en M USD por proyecto con los mismos filtros que el gráfico de LCOE.\n\n"
            "**Cómo leerlo:** identifica **escala de desembolso** relativa; suele correlacionar con tamaño (MW) pero no de forma 1:1 por tecnología y sitio.\n\n"
            "**Matices:** CAPEX elevado sin LCOE proporcionalmente alto puede indicar **vida útil** o **supuestos de generación** distintos en el cálculo de LCOE."
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
            "**Qué muestra:** magnitud de **usuarios** por proyecto; el color indica **tipo de energía**.\n\n"
            "**Cómo leerlo:** barras altas concentran mayor **alcance en usuarios** dentro de esta muestra.\n\n"
            "**Matices:** la métrica depende de la definición operativa en datos; para inferencias sectoriales hace falta validar contra fuentes oficiales."
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
            "**Qué muestra:** **disponibilidad operativa (%)** por proyecto; la línea verde une puntos y el color del punto es la **tecnología**.\n\n"
            "**Cómo leerlo:** el eje Y está acotado (95–100) para amplificar diferencias pequeñas; compara **homogeneidad** entre plantas.\n\n"
            "**Matices:** rangos muy estrechos en la muestra pueden verse **planos**; con datos reales conviene revisar outliers y periodos."
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
        "**Qué muestra:** magnitud del **% de ahorro** asociado a cada **ley** en el dataset de regulación.\n\n"
        "**Cómo leerlo:** el área representa el peso relativo del porcentaje entre las leyes mostradas; no es impacto fiscal agregado en pesos.\n\n"
        "**Matices:** los porcentajes son **atributos normativos simplificados**; el efecto económico real depende de base gravable y elegibilidad."
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

    anios_demo = sorted({int(x) for x in d["costos"]["anio"].dropna().unique().tolist()}, reverse=True)
    query_anio = st.selectbox("Año (Fact_Costos / mock)", anios_demo or [2024], index=0)

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
        .mark_bar()
        .encode(
            x=alt.X("label:N", title=None),
            y=alt.Y("value:Q", title="Valor"),
            color=alt.Color("label:N", legend=None, scale=_energy_color_scale()),
            tooltip=["label:N", alt.Tooltip("value:Q", title="Valor")],
        )
        .properties(height=320, title="Visualización de resultados")
    )
    st.altair_chart(chart, use_container_width=True)
    _chart_interp(
        "**Qué muestra:** barras del **resultado** de la consulta demo (`label` vs `value`) tras aplicar filtros.\n\n"
        "**Cómo leerlo:** cuando `label` es un **tipo de energía**, el color sigue el estándar del tablero; si la consulta devuelve etiquetas genéricas, el gráfico es solo ilustrativo.\n\n"
        "**Matices:** la lógica es **mock**; para producción debe reemplazarse por ejecución sobre `MatrizEnergeticaCol` o vistas SQL validadas."
    )


def main() -> None:
    st.set_page_config(page_title="EnergyTrans Colombia", page_icon="⚡", layout="wide")
    _inject_global_css()
    d = _get_data()

    if "view" not in st.session_state:
        st.session_state["view"] = "inicio"

    _cur = st.session_state["view"]
    if _cur != "inicio":
        _page_header("EnergyTrans Colombia")
    view = _top_nav(_cur)

    if view == "inicio":
        _view_inicio(d)
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

    if view != "inicio":
        st.divider()
    st.caption("© 2024 EnergyTrans Colombia | Muestra alineada al SQL: costos 2024; generación en BD 2020 (parcial), no mostrada aún")


if __name__ == "__main__":
    main()

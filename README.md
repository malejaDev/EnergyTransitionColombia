# ⚡ EnergyTransitionColombia (Streamlit)

Dashboard interactivo para explorar indicadores de **Transición Energética en Colombia (2019–2025)**: proyectos, costos (LCOE/CAPEX/OPEX), cobertura/disponibilidad y marco regulatorio.

## 🌐 App online (Streamlit)

- **URL**: `https://energytransitioncolombia.streamlit.app/`
- **Archivo principal**: `EnergyTransitionColombia/streamlit_app.py`

## 🎯 Objetivo

- Consolidar y visualizar métricas clave de la transición energética.
- Facilitar comparación entre **tecnologías** (Hidráulica, Solar, Eólica, Geotérmica) con un estándar de color consistente.
- Permitir exploración con filtros y vistas temáticas (costos, cobertura, regulación, etc.).

## 🧑‍🤝‍🧑 Integrantes

- Claudia Arroyave
- Michely Muñoz
- Jesus Garcia
- Maria Alejandra Colorado Ríos

## 🎓 Contexto académico

Proyecto realizado para el **curso de Análisis de Datos Integrador** de **Talento Tech**.

## 🧱 Esquema del proyecto

### 🗂️ Estructura (carpeta Streamlit)

```text
EnergyTransitionColombia/
  streamlit_app.py          # App Streamlit (UI + cálculos + charts)
  requirements.txt          # Dependencias Python
  .streamlit/config.toml    # Tema (colores/estilo)
  README.md                 # Este documento
```

### 🧠 Modelo lógico (demo con datos mock)

- **Dimensiones**
  - `tipo_energia`: tecnología (fuente, descripción)
  - `proyectos`: proyecto (nombre, departamento, tipo, capacidad)
  - `regulacion`: ley/incentivo
- **Hechos**
  - `costos`: LCOE, CAPEX, OPEX por proyecto/año
  - `cobertura`: usuarios y disponibilidad por proyecto

## 🧭 Navegación (módulos)

- **⚡ Inicio**: landing del proyecto + guía rápida.
- **📊 Dashboard**: resumen ejecutivo + mix energético + tarjetas de tipos de energía.
- **🏗️ Proyectos**: filtros + tarjetas neomórficas + tabla.
- **💰 Costos**: filtros dinámicos que alimentan gráficas y tabla.
- **📶 Cobertura**: usuarios y disponibilidad (colores estandarizados por tipo).
- **📄 Regulación**: incentivos y visualización de impacto.
- **🔎 Consultas**: exploración tipo SQL (demo).

## 🛠️ Instalación y ejecución local (Windows)

1) Crear entorno e instalar dependencias:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r EnergyTransitionColombia/requirements.txt
```

2) Ejecutar Streamlit:

```bash
streamlit run EnergyTransitionColombia/streamlit_app.py
```

## 🚀 Despliegue (Streamlit Community Cloud)

1) Sube el repo a GitHub.
2) Entra a [Streamlit](https://streamlit.io/) → **Community Cloud**.
3) Configura:
   - **Main file path**: `EnergyTransitionColombia/streamlit_app.py`
   - **Dependencias**: `EnergyTransitionColombia/requirements.txt` (Streamlit las detecta automáticamente)

## 🧩 Notas

- Los datos actuales en la app son **mock** para demostrar la experiencia end-to-end.
- Al conectar datos reales, se habilitan más años automáticamente en los filtros (p. ej., en **Costos**).
# ⚡ EnergyTransitionColombia (Streamlit)

Dashboard interactivo para explorar indicadores de **Transición Energética en Colombia (2019–2025)**: proyectos, costos (LCOE/CAPEX/OPEX), cobertura/disponibilidad y marco regulatorio.

## 🌐 App online (Streamlit)

- **URL**: `https://energytransitioncolombia.streamlit.app/`
- **Archivo principal**: `EnergyTransitionColombia/streamlit_app.py`

## 🎯 Objetivo

- Consolidar y visualizar métricas clave de la transición energética.
- Facilitar comparación entre **tecnologías** (Hidráulica, Solar, Eólica, Geotérmica) con un estándar de color consistente.
- Permitir exploración con filtros y vistas temáticas (costos, cobertura, regulación, etc.).

## 🧩 Alcance del análisis (qué responde este proyecto)

- **Evolución y composición** de la capacidad instalada por tecnología.
- **Comparación económica** entre proyectos (LCOE, CAPEX, OPEX) y su lectura por tecnología.
- **Cobertura** (usuarios beneficiados) y **disponibilidad** operacional por proyecto.
- **Marco regulatorio** e incentivos (impacto porcentual).

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
  database/                 # Scripts SQL (schema/datos + consultas)
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

## 📌 KPIs y definiciones (glosario)

- **Capacidad instalada (MW)**: suma de `capacidad_mw` por proyecto o por tecnología.
- **LCOE (USD/MWh)**: costo nivelado de energía (métrica comparativa de costo por MWh).
- **CAPEX (M USD)**: inversión de capital (costo de construcción/instalación).
- **OPEX (M USD)**: costos operativos (operación y mantenimiento).
- **Usuarios**: número de usuarios beneficiados/atendidos por proyecto.
- **Disponibilidad (%)**: porcentaje de disponibilidad operativa del proyecto.
- **% Ahorro (incentivo)**: impacto/beneficio porcentual asociado a una regulación/ley.

## 🎨 Estándar visual (UX)

- **Colores por tecnología** (consistentes en todas las gráficas):
  - Hidráulica: `#0284c7` (azul)
  - Solar: `#f59e0b` (amarillo)
  - Eólica: `#10b981` (verde/teal)
  - Geotérmica: `#ef4444` (rojo)

## 🗄️ Base de datos (SQL)

En `EnergyTransitionColombia/database/` encontrarás scripts para crear un esquema y ejecutar consultas de análisis sobre una **matriz energética** (2020–2025).

### 📁 Archivos

- `database/Matriz_Energetica_Colombia_Schema_y_Datos_2020_2025.sql`
  - Crea la base de datos `MatrizEnergeticaCol`
  - Crea tablas tipo **dimensión/hechos** (ej. `Dim_TipoEnergia`, `Dim_Proyecto`, `Fact_Generacion`, etc.)
  - Inserta datos de ejemplo (incluye series por fecha)
- `database/Consultas_Analisis_Matriz_Energetica_Colombia.sql`
  - Conjunto de consultas (Q01, Q02, …) para explorar proyectos, generación, cobertura y costos

### 🧪 Cómo ejecutar (MySQL)

> Motor/herramienta: **MySQL Workbench**.  
> Nota: Algunas consultas usan `DATE_FORMAT`, típico de **MySQL**.

1) Ejecuta el script de esquema + datos:

```sql
SOURCE EnergyTransitionColombia/database/Matriz_Energetica_Colombia_Schema_y_Datos_2020_2025.sql;
```

2) Luego ejecuta las consultas de análisis:

```sql
SOURCE EnergyTransitionColombia/database/Consultas_Analisis_Matriz_Energetica_Colombia.sql;
```

### 🔎 Relación con la app Streamlit

- La app Streamlit actualmente funciona con **datos mock en Python**.
- Estos scripts SQL quedan como base para conectar una BD real en una siguiente iteración (por ejemplo, reemplazando los mocks por lecturas desde MySQL/SQLAlchemy).

## 🧬 Pipeline de datos (recomendado)

> Estado actual: la app usa **mock**. Este pipeline describe cómo llevarlo a un escenario real.

1. **Ingesta**: cargar datos (CSV/API/BD) a tablas de staging.
2. **Modelado**: poblar dimensiones (`Dim_*`) y hechos (`Fact_*`) con llaves consistentes.
3. **Calidad**:
   - Tipos/formatos (fechas, numéricos)
   - Unicidad de IDs (proyecto, tipo, regulación)
   - Reglas básicas (disponibilidad 0–100, capacidades > 0, etc.)
4. **Capa semántica/KPIs**: vistas o queries que calculen KPIs (por tecnología, por proyecto, por periodo).
5. **Consumo (Streamlit)**: lectura desde MySQL (p. ej., SQLAlchemy) y render de vistas.

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

## ✅ Reproducibilidad

- **Python**: instala dependencias desde `EnergyTransitionColombia/requirements.txt`.
- **SQL**: ejecuta los scripts en MySQL Workbench (sección “Base de datos”).
- **Entorno**: evita subir secretos; Streamlit ignora `secrets.toml` por seguridad.

## 🚀 Despliegue (Streamlit Community Cloud)

1) Sube el repo a GitHub.
2) Entra a [Streamlit](https://streamlit.io/) → **Community Cloud**.
3) Configura:
   - **Main file path**: `EnergyTransitionColombia/streamlit_app.py`
   - **Dependencias**: `EnergyTransitionColombia/requirements.txt` (Streamlit las detecta automáticamente)

## 🧩 Notas

- Los datos actuales en la app son **mock** para demostrar la experiencia end-to-end.
- Al conectar datos reales, se habilitan más años automáticamente en los filtros (p. ej., en **Costos**).

## 🛣️ Roadmap (siguientes mejoras)

- Conectar la app a MySQL (lectura de `Dim_*` y `Fact_*`) y reemplazar mocks.
- Agregar más años en costos/series y tendencias temporales.
- Añadir validaciones automáticas de calidad (tests de datos) y reportes.

## 📄 Licencia

Uso académico/educativo (Talento Tech). Si deseas una licencia formal (MIT/Apache-2.0), se puede agregar.
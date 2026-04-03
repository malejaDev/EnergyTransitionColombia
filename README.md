# ⚡ EnergyTransitionColombia

Proyecto desarrollado en el marco del **curso de Análisis de Datos Integrador** de **Talento Tech**.

## 🧑‍🤝‍🧑 Equipo y contexto

- Claudia Arroyave  
- Michely Muñoz  
- Jesus Garcia  
- Maria Alejandra Colorado Ríos  

## 🎯 Problema que aborda el proyecto

### Identificación de la problemática

**Problema específico elegido:** caracterizar cómo evoluciona la **diversificación de la matriz energética colombiana** en el plano analítico—comparando **hídrica, solar, eólica y geotérmica**—cruzando **generación**, **demanda/cobertura**, **costos e inversión** y **emisiones**, con una lectura útil para discusión técnica y apoyo a decisiones. El cuaderno `notebook/Transicion_Energetica.ipynb`, el SQL y el Streamlit concentran ese análisis sobre una serie **sintética 2020–2026**.

### Qué analiza el notebook (resumen)

En `Transicion_Energetica.ipynb` se realizan las siguientes etapas:

1. **Construye el dataset** de trabajo con variables por tecnología y tiempo (generación, demanda, cobertura, costos, inversión, emisiones).  
2. **Controla calidad** (estructura, tipos, faltantes, rangos y coherencia entre magnitudes).  
3. **Agrega** a una base **año × tipo de energía** para analizar tendencias con menos ruido.  
4. Aplica **ingeniería de variables**: participación en generación, crecimiento interanual, variación de generación, costo por unidad generada, intensidad de emisiones, ecoeficiencia, emisiones evitadas vs. referencia, **índice de diversificación** de la matriz, entre otros.  
5. Presenta **síntesis ejecutiva**, **visualización analítica**, **hallazgos** y **conclusiones**, más una sección de **extensiones** metodológicas.

Los datos del notebook son **sintéticos** (inspirados en órdenes de magnitud y tendencias tipo XM / UPME / SGC); los hallazgos **cualitativos del método** son transferibles.

### Pregunta que amarra capas (notebook, SQL, Streamlit)

> ¿Cómo se compone la **capacidad y la economía** de los proyectos por **tipo de energía**, y qué patrón emerge al cruzar **costos** con **cobertura/disponibilidad** y **regulación**?



### Ventana temporal por capa

| Capa | Qué cubre hoy en el repo |
|------|---------------------------|
| **Notebook** (`Transicion_Energetica.ipynb`) | Horizonte **2020–2025** con datos **sintéticos** (metodología y escenarios). |
| **MySQL** (`Matriz_Energetica_Colombia_Schema_y_Datos_2020_2025.sql`) | `Fact_Generacion`: fechas **2020-01-01** a **2020-05-21** (diaria). `Fact_Costos`: año **2024**  |
| **Streamlit** | Mock alineado al SQL para costos y dimensiones: **2024** en costos |

El proyecto organiza el trabajo en **tres capas**: (1) **Notebook** — EDA e indicadores derivados en `notebook/Transicion_Energetica.ipynb`; (2) **MySQL** — esquema dimensional, datos y consultas reproducibles en `database/` (incluye generación diaria e impacto ambiental en tablas de hechos); (3) **Streamlit** — dashboard para filtrar y visualizar proyectos, costos (LCOE, CAPEX, OPEX), cobertura, disponibilidad y regulación.

Hoy el **despliegue web** usa **datos mock en memoria** (`streamlit_app.py`) alineados al modelo; la **fuente analítica “fuerte”** sigue siendo el **SQL + el cuaderno** (calidad, trazabilidad y narrativa). Más abajo están el detalle de cada capa.

| | |
|---|--|
| **App en producción** | [energytransitioncolombia.streamlit.app](https://energytransitioncolombia.streamlit.app/) |
| **Entrada del dashboard** | `EnergyTransitionColombia/streamlit_app.py` |

---



---

## 🗂️ Contenido del repositorio

```text
EnergyTransitionColombia/
  database/
    Matriz_Energetica_Colombia_Schema_y_Datos_2020_2025.sql   # BD, tablas, cargas
    Consultas_Analisis_Matriz_Energetica_Colombia.sql       # Consultas Q01, Q02, …
  notebook/
    Transicion_Energetica.ipynb  # EDA, calidad, features, visualización (Jupyter/Colab)
  streamlit_app.py      # UI, agregaciones, gráficas (pandas + Altair)
  requirements.txt
  .streamlit/config.toml
  README.md
```

---

## 📓 Cuaderno de análisis (`Transicion_Energetica.ipynb`)

El **hilo analítico principal** está descrito arriba, en **Problema que aborda el proyecto → Qué analiza el notebook**. El archivo (≈**28 celdas**) desarrolla además, en secciones propias del cuaderno: **visualización analítica** (§7), **hallazgos principales** (§8), **conclusiones** (§9) y **extensiones metodológicas** (§10).

**Datos:** el cuaderno declara un **conjunto sintético** alineado a **tendencias** de referentes sectoriales (p. ej. XM, UPME, SGC). Úsalo para **método e integración de variables**; sustituye por datos oficiales para inferencia sobre el sistema real.

**Copia publicada (Google Drive / entorno Colab):** puedes abrir o descargar el cuaderno desde [este enlace](https://drive.google.com/file/d/1kWZn9wSRqu6PjTfnsmNb98mSBqC7-J6w/view?usp=drive_link) (`Transicion_Energetica.ipynb`). Para máxima reproducibilidad, prioriza la versión versionada en `notebook/` del repositorio y alinea entorno (versiones de librerías) con la que usó el equipo.

**Ejecución local del `.ipynb`:** con un entorno Python (idealmente el mismo virtualenv del proyecto), instala dependencias del cuaderno si el propio notebook las declara o añade a `requirements.txt` según imports; luego `jupyter lab` o VS Code/Cursor con extensión Jupyter.

---

## 🗄️ Base de datos (MySQL Workbench)

La base **`MatrizEnergeticaCol`** se crea y carga con `database/Matriz_Energetica_Colombia_Schema_y_Datos_2020_2025.sql` (nombre histórico; el contenido actual de `Fact_Generacion` y `Fact_Costos` sigue la tabla **Ventana temporal por capa**). Tablas relevantes:

| Rol | Tablas |
|-----|--------|
| Dimensiones | `Dim_TipoEnergia`, `Dim_Regulacion`, `Dim_Proyecto` |
| Hechos | `Fact_Generacion`, `Fact_Costos`, `Fact_Cobertura`, `Fact_ImpactoAmbiental` |

`database/Consultas_Analisis_Matriz_Energetica_Colombia.sql` contiene análisis reproducibles (listados, filtros, agregaciones, subconsultas; algunas sentencias usan funciones propias de **MySQL**, p. ej. `DATE_FORMAT`).

**Ejecución típica en Workbench** (ajusta rutas si abres el repo desde otra carpeta):

```sql
SOURCE EnergyTransitionColombia/database/Matriz_Energetica_Colombia_Schema_y_Datos_2020_2025.sql;
SOURCE EnergyTransitionColombia/database/Consultas_Analisis_Matriz_Energetica_Colombia.sql;
```

Si un comentario al inicio del archivo de consultas cita otro nombre de script, prioriza el archivo **presente** en `database/` citado arriba.

---

## 💻 Capa de aplicación (Streamlit)

Los datos mostrados en la UI se obtienen de `_load_data()` y se exponen como `pandas.DataFrame` en un diccionario; `_get_data()` aplica `@st.cache_data` para evitar recálculos innecesarios. Las vistas principales, alineadas con el tipo de trabajo analítico, son:

| Vista | Función | Rol |
|-------|---------|-----|
| Inicio | `_view_inicio` | Contexto, equipo, guía de uso |
| Dashboard | `_view_dashboard` | Resumen, mix por tecnología, LCOE por tecnología |
| Proyectos | `_view_proyectos` | Filtros, tarjetas, tabla |
| Costos | `_view_costos` | Filtros dinámicos → gráficas y tabla |
| Cobertura | `_view_cobertura` | Usuarios, disponibilidad, color por tipo |
| Regulación | `_view_regulacion` | Incentivos y gráfica de impacto |
| Consultas | `_view_consultas` | Constructor demo tipo SQL sobre el mock (`_execute_query_mock`) |

Convención de color por **tipo de energía** (misma semántica en gráficos que la usan): implementada con `ENERGY_*`, `_energy_color_scale()` y dominio alineado a las etiquetas de `Dim_TipoEnergia` / mock.


---

## 📌 Glosario de métricas (definición operativa en el tablero)

- **Capacidad instalada (MW):** suma de `capacidad_mw` por agregación elegida.  
- **LCOE (USD/MWh):** costo nivelado unitario para comparación entre proyectos o tecnologías.  
- **CAPEX / OPEX (M USD):** inversión y operación; el costo total agregado es CAPEX + OPEX cuando aplica.  
- **Usuarios:** magnitud de cobertura asociada al proyecto en el dataset.  
- **Disponibilidad (%):** indicador operativo en rango acotado en visualización.  
- **% ahorro (regulación):** magnitud asociada al incentivo normativo en dimensión regulación.

---

## 🎨 Estándar visual (UX / analítica)

Para lectura consistente entre gráficos:

- Hidráulica `#0284c7` · Solar `#f59e0b` · Eólica `#10b981` · Geotérmica `#ef4444`

El tema general de la app se configura en `.streamlit/config.toml`.

---

## 🔁 Cómo trabaja un ciclo de ciencia de datos sobre este repo (visión integrada)

No como lista de plantilla sino como línea de trabajo coherente con lo que ya está versionado:

1. **Negocio y alcance:** fijar qué decisiones apoya cada entregable (cuaderno = narrativa e indicadores; SQL = persistencia reproducible; Streamlit = exploración rápida para stakeholders).  
2. **Datos:** inventariar tablas en el `.sql` de esquema; validar PK/FK; complementar con el flujo del **notebook** y con `Consultas_Analisis_*.sql` para consultas estándar.  
3. **Preparación y calidad:** controles como en el notebook (estructura, faltantes, rangos) y reglas en capa SQL; agregaciones coherentes entre pandas y consultas.  
4. **Análisis y posible modelado:** series en `Fact_Generacion`, economía en `Fact_Costos`, indicadores derivados como en el cuaderno; modelos, si aplica, **fuera** de Streamlit.  
5. **Evaluación:** partición temporal donde haya serie; sin modelos predictivos, auditabilidad de métricas y trazabilidad notebook → SQL → dashboard.  
6. **Producto y despliegue:** notebook (local o [Drive](https://drive.google.com/file/d/1kWZn9wSRqu6PjTfnsmNb98mSBqC7-J6w/view?usp=drive_link)), Streamlit en Community Cloud, MySQL en Workbench.  
7. **Mantenimiento:** versionado de `requirements.txt`, del `.ipynb` y del esquema SQL; alinear definiciones de KPI entre capas.

---

## 🛠️ Entorno local (Windows)

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r EnergyTransitionColombia/requirements.txt
streamlit run EnergyTransitionColombia/streamlit_app.py
```

## 🚀 Despliegue (Streamlit Community Cloud)

Repositorio en GitHub; en [Streamlit](https://streamlit.io/) → Community Cloud:

- **Main file path:** `EnergyTransitionColombia/streamlit_app.py`  
- **Dependencias:** `EnergyTransitionColombia/requirements.txt`  

## ✅ Reproducibilidad

Versionado de paquetes, del cuaderno en `notebook/` y de los scripts SQL; con modelos estocásticos, fijar semillas y registrar resultados. No commitear secretos; usar `secrets.toml` solo en despliegue local/cloud.

---

## 🛣️ Evolución natural del proyecto

- Conectar la app a MySQL y eliminar o reducir mocks manteniendo contratos de datos.  
- Incorporar vistas de **generación** e **impacto ambiental** ya presentes en el esquema.  
- Tests de calidad de datos y pipelines de actualización.  
- **Sincronizar** indicadores del `Transicion_Energetica.ipynb` con columnas/vistas consumidas por Streamlit para una sola fuente de verdad.

---

## 📄 Licencia

Uso académico/educativo en el contexto de **Talento Tech**. Para uso abierto con licencia estándar (MIT, Apache-2.0, etc.) puede formalizarse aparte.

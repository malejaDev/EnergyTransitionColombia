# ⚡ EnergyTransitionColombia

**EnergyTransitionColombia** articula tres capas: **análisis exploratorio y de ingeniería de variables en notebook** (`notebook/Transicion_Energetica.ipynb`), **persistencia y consultas analíticas en MySQL** (`database/`), y un **dashboard en Streamlit** para exploración operativa: proyectos por tecnología y región, costos (LCOE, CAPEX, OPEX), cobertura y disponibilidad, marco regulatorio, y en base de datos además **generación diaria** e **impacto ambiental**. La app publicada alimenta la interfaz con **datos mock en Python** coherentes con el modelo dimensional; la base SQL y el cuaderno son el lugar donde concentrar **trazabilidad, calidad de datos y narrativa analítica** antes o en paralelo al producto interactivo.

**App en producción:** [https://energytransitioncolombia.streamlit.app/](https://energytransitioncolombia.streamlit.app/)  
**Entrada principal del código:** `EnergyTransitionColombia/streamlit_app.py`

---

## 🎯 Qué problema aborda el proyecto

La transición energética exige comparar **tecnologías**, **escala**, **economía del proyecto** y **resultados operativos/cobertura** sin mezclar semánticas ni visualizaciones inconsistentes. Este repositorio documenta y materializa un flujo de trabajo de **ciencia de datos aplicada**: definir métricas, alinear datos en un esquema relacional, explorar y comunicar resultados en un producto consumible.

Pregunta rectora que guía el diseño del tablero y de las consultas SQL:

> ¿Cómo se compone la capacidad y la economía de los proyectos por **tipo de energía**, y qué se observa al cruzar **costos** con **cobertura/disponibilidad** y **regulación**?

**Hipótesis exploratorias** (contrastables cuando los datos provengan de la base y no solo del mock): no siempre mayor capacidad implica menor LCOE; las tecnologías forman clusters distintos en el espacio CAPEX–LCOE; la lectura de cobertura debe contextualizarse con regulación y portafolio. **Límites**: correlación no implica causalidad; con datos académicos/demo las conclusiones son sobre metodología y producto, no necesariamente sobre el sistema eléctrico nacional completo.

---

## 🧑‍🤝‍🧑 Equipo y contexto

- Claudia Arroyave  
- Michely Muñoz  
- Jesus Garcia  
- Maria Alejandra Colorado Ríos  

Proyecto desarrollado en el marco del **curso de Análisis de Datos Integrador** de **Talento Tech**.

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

## 📓 Cuaderno de análisis (laboratorio de ciencia de datos)

En `notebook/Transicion_Energetica.ipynb` está el **hilo analítico principal** del equipo (actualmente **28 celdas**): construcción del dataset de trabajo, control de consistencia, agregación por año y tecnología, **ingeniería de variables** y síntesis previa a visualizaciones.

**Tema y alcance (según el propio cuaderno):** análisis estratégico de la diversificación de la **matriz energética en Colombia (2020–2026)**, con foco en **FNCER (fuentes no convencionales renovables) frente a generación hídrica**, comparando trayectorias de solar, eólica, geotérmica e hídrica en generación, costos, emisiones, participación y diversificación. La fuente declarada en el notebook es un **modelo de datos sintético inspirado en tendencias** de referentes sectoriales (p. ej. XM, UPME, SGC); las conclusiones deben interpretarse en ese marco hasta conectar con datos operativos reales.

**Flujo metodológico resumido en el notebook:**

1. Librerías y configuración visual.  
2. Construcción del dataset (periodo y variables para generación, demanda, cobertura, costos, inversión, emisiones por tecnología).  
3. Revisión inicial: estructura, tipos, faltantes, rangos y coherencia entre magnitudes.  
4. Base analítica agregada por **año × tipo de energía**.  
5. Indicadores derivados (entre otros): participación relativa en generación, crecimiento interanual, variación absoluta de generación, costo por unidad generada, intensidad de emisiones, índice de ecoeficiencia, emisiones evitadas vs. referencia, índice de diversificación de la matriz.  
6. Síntesis ejecutiva preliminar y bloques de visualización analítica.

**Copia publicada (Google Drive / entorno Colab):** puedes abrir o descargar el cuaderno desde [este enlace](https://drive.google.com/file/d/1kWZn9wSRqu6PjTfnsmNb98mSBqC7-J6w/view?usp=drive_link) (`Transicion_Energetica.ipynb`). Para máxima reproducibilidad, prioriza la versión versionada en `notebook/` del repositorio y alinea entorno (versiones de librerías) con la que usó el equipo.

**Ejecución local del `.ipynb`:** con un entorno Python (idealmente el mismo virtualenv del proyecto), instala dependencias del cuaderno si el propio notebook las declara o añade a `requirements.txt` según imports; luego `jupyter lab` o VS Code/Cursor con extensión Jupyter.

---

## 🗄️ Base de datos (MySQL Workbench)

La base **`MatrizEnergeticaCol`** se crea y carga con `database/Matriz_Energetica_Colombia_Schema_y_Datos_2020_2025.sql`. Tablas relevantes:

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

**Estado actual respecto a MySQL:** la app **no lee todavía** `MatrizEnergeticaCol` en runtime; `Fact_Generacion` e `Fact_ImpactoAmbiental` **no** están enlazadas en la interfaz. El siguiente paso de ingeniería de datos es sustituir o enriquecer `_load_data()` con consultas parametrizadas (por ejemplo SQLAlchemy + `st.secrets`) manteniendo los mismos contratos de columnas que esperan `_view_*`.

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

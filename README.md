# ⚡ EnergyTransitionColombia

**EnergyTransitionColombia** es un producto de datos que combina un **modelo dimensional en MySQL** (matriz energética Colombia, 2020–2025) con un **dashboard en Streamlit** orientado a explorar la transición energética: proyectos por tecnología y región, costos (LCOE, CAPEX, OPEX), cobertura y disponibilidad, marco regulatorio, y en base de datos además **generación diaria** e **impacto ambiental**. La aplicación publicada hoy alimenta la interfaz con **datos mock en Python** que replican la lógica del modelo; la capa SQL es el **contrato de datos** y el lugar donde conviene concentrar análisis reproduccibles, calidad y extensiones de modelado.

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
  streamlit_app.py      # UI, agregaciones, gráficas (pandas + Altair)
  requirements.txt
  .streamlit/config.toml
  README.md
```

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

1. **Negocio y alcance:** fijar qué decisiones apoya el tablero (exploración vs. scoring predictivo); hoy el foco es **EDA y comunicación** con base lista para modelado.  
2. **Datos:** inventariar tablas y relaciones en el `.sql` de esquema; validar PK/FK y cobertura temporal; ejecutar y documentar hallazgos vía `Consultas_Analisis_*.sql`.  
3. **Preparación y calidad:** limpieza, tipos, duplicados, reglas (p. ej. disponibilidad en rango, capacidades positivas); agregaciones en SQL o en pandas según capa.  
4. **Análisis y posible modelado:** usar `Fact_Generacion` para series, `Fact_Costos` + dimensiones para regresión o clustering; entrenar **fuera** de Streamlit y, si aplica, exponer solo resultados validados en la app.  
5. **Evaluación:** con modelos, partición temporal para series; métricas adecuadas (MAE/RMSE, etc.) y revisión de residuales; sin modelos, validación por **coherencia de negocio** y reproducibilidad de queries.  
6. **Producto y despliegue:** Streamlit + `requirements.txt` + ruta en Community Cloud; en evolución, `secrets` para credenciales MySQL.  
7. **Mantenimiento:** versiones fijadas en dependencias, contratos de esquema entre SQL y columnas consumidas por la app, monitoreo de deriva cuando exista ETL.

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

Versionado de paquetes, mismo orden de ejecución de scripts SQL, y si se incorporan modelos estocásticos fijar semillas y registrar resultados (notebook o carpeta `experiments/` en evolución). No commitear secretos; usar `secrets.toml` solo en despliegue local/cloud.

---

## 🛣️ Evolución natural del proyecto

- Conectar la app a MySQL y eliminar o reducir mocks manteniendo contratos de datos.  
- Incorporar vistas de **generación** e **impacto ambiental** ya presentes en el esquema.  
- Tests de calidad de datos y pipelines de actualización.  
- Notebooks o scripts de experimentación con línea base y métricas auditables.

---

## 📄 Licencia

Uso académico/educativo en el contexto de **Talento Tech**. Para uso abierto con licencia estándar (MIT, Apache-2.0, etc.) puede formalizarse aparte.

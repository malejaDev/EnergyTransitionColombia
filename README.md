# ⚡ EnergyTransitionColombia (Streamlit)

Producto de datos (**dashboard Streamlit**) construido sobre un **marco dimensional** y orientado a **preguntas cuantitativas** sobre la **Transición Energética en Colombia (2019–2025)**: proyectos, costos (LCOE/CAPEX/OPEX), cobertura/disponibilidad, generación temporal y marco regulatorio.

Este documento describe el proyecto con enfoque de **ciencia de datos**: formulación del problema, datos, supuestos, limitaciones, reproducibilidad y líneas de trabajo **más allá del EDA** (modelado y evaluación).

## 🌐 App online (Streamlit)

- **URL**: `https://energytransitioncolombia.streamlit.app/`
- **Archivo principal**: `EnergyTransitionColombia/streamlit_app.py`

## 🎯 Objetivo (ciencia de datos + producto)

- **Formular y explorar** relaciones observables entre tecnología, capacidad, costos y cobertura (EDA sistemático).
- **Reducir incertidumbre operativa** del usuario final mediante filtros, agregaciones y visualizaciones coherentes.
- **Estandarizar** la semántica de variables y la representación visual (evitar interpretaciones erróneas por colores inconsistentes).
- **Dejar trazabilidad** entre capa de datos (SQL), transformaciones y capa de presentación (Streamlit).

## 🔬 Enfoque de científico de datos

### Pregunta guía

> ¿Cómo se compone la matriz energética en el escenario considerado y **qué patrones** emergen al cruzar **tecnología**, **escala (MW)**, **costos** y **cobertura/disponibilidad**?

### Hipótesis exploratorias (no confirmatorias hasta tener datos oficiales)

Con datos **representativos y limpios**, sería razonable contrastar en el tablero (y luego con modelos):

- Proyectos de **mayor capacidad** no necesariamente implican **menor LCOE** (economías de escala vs. heterogeneidad regional y tecnológica).
- **Tecnologías** con curvas de costo distintas deberían agruparse de forma estable en comparativas (CAPEX vs. LCOE).
- Indicadores de **cobertura/disponibilidad** deben interpretarse **condicionados al contexto regulatorio** y al portafolio de proyectos.

Estas hipótesis aquí son **exploratorias**: la versión actual de la app usa **mock** en Python; al conectar la base `MatrizEnergeticaCol` y validar calidad de datos, pasan a ser **contrastables** con inferencia y/o modelos.

### Supuestos y límites de inferencia

- **Correlación ≠ causalidad**: el dashboard facilita asociaciones; afirmaciones causales requieren diseño (variables de confusión, series temporales, instrumentos, etc.).
- **Representatividad**: con mock/académico, las conclusiones son **sobre el pipeline y la metodología**, no sobre el sistema eléctrico real.
- **Sesgos típicos**: selección de proyectos, años parciales, definiciones de LCOE/CAPEX no homogéneas entre fuentes, y agregaciones que ocultan heterogeneidad intra-región.

### Oportunidades de modelado (siguiente capa)

| Tarea | Idea | Datos útiles | Métrica típica |
|------|------|--------------|----------------|
| Regresión | Explicar/predicción de **LCOE** con capacidad, tecnología, región | `Fact_Costos` + `Dim_Proyecto` + features categóricas | MAE/RMSE, \(R^2\), residuales |
| Clasificación | Clasificar proyectos por “banda” de costo o eficiencia | Costos + capacidad + tipo | F1, AUC (si binario) |
| Series temporales | Pronóstico de **generación** o factor de planta | `Fact_Generacion` (`fecha`) | MAE/RMSE, valores fuera de muestra |
| Agrupamiento | Segmentar proyectos por perfil económico-operativo | Costos + cobertura + disponibilidad | Silhouette, estabilidad de clusters |

## 🧩 Alcance del dominio (qué cubre el producto de datos)

- **Evolución y composición** de la capacidad instalada por tecnología.
- **Comparación económica** entre proyectos (LCOE, CAPEX, OPEX) y su lectura por tecnología.
- **Cobertura** (usuarios beneficiados) y **disponibilidad** operacional por proyecto.
- **Marco regulatorio** e incentivos (impacto porcentual).
- **Generación diaria y agregaciones temporales** (capa SQL en `database/`; la app puede consumirlas en iteraciones futuras).

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
6. **Experimentación (DS)**: versionar conjuntos de entrenamiento/prueba, definir *baseline* (al menos un modelo simple vs. complejo) y documentar decisiones.
7. **Evaluación y despliegue**: métricas en validación, pruebas de regresión del tablero (datos nuevos no deben romper joins/KPIs).

### Validación (cuando exista modelado)

- **Partición temporal** obligatoria si se usan series (`Fact_Generacion`): entrenar con ventanas pasadas y evaluar en fechas futuras.
- **Estratificación** por tecnología o región si hay desbalance.
- **Análisis de residuales** en regresión; curvas de calibración si hay probabilidades.

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
- **Versionado**: fija versiones en `requirements.txt` cuando el proyecto pase de demo a trabajo reproducible en equipo.
- **Semillas**: si se añaden modelos estocásticos, fija `random_state` y documenta en notebook o `docs/`.

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
- Incorporar **notebooks** o scripts (`experiments/`) con modelos baseline y métricas exportables.
- Definir contrato de datos (**data contracts**) entre SQL y la app (schemas esperados por vista).

## 📄 Licencia

Uso académico/educativo (Talento Tech). Si deseas una licencia formal (MIT/Apache-2.0), se puede agregar.
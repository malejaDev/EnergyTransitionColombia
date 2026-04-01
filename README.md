# EnergyTransitionColombia (Streamlit)

Esta carpeta contiene la versión compatible con **Streamlit** de la app originalmente ubicada en `energytrans-colombia/` (React + Vite).

## Contexto académico

Este proyecto fue realizado para el **curso de Análisis de Datos Integrador** de **Talento Tech**.

## Integrantes

- Claudia Arroyave
- Michely Muñoz
- Jesus Garcia
- Maria Alejandra Colorado Ríos

## Ejecutar local (opcional)

1. Crear entorno e instalar dependencias:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

2. Ejecutar:

```bash
streamlit run streamlit_app.py
```

## Desplegar online (Streamlit Community Cloud)

1. Sube este repo a GitHub.
2. Entra a [Streamlit](https://streamlit.io/) y ve a **Community Cloud**.
3. Selecciona el repo y configura:
   - **Main file path**: `EnergyTransitionColombia/streamlit_app.py`
   - **Python dependencies**: `EnergyTransitionColombia/requirements.txt` (Streamlit lo detecta automáticamente al estar en el repo)

Listo: el despliegue debería quedar automatizado en cada push.
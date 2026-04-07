"""
Genera csv/matriz_mock.xlsx (fuente única de tablas mock para Streamlit).
Ejecutar desde EnergyTransitionColombia: python scripts/build_matriz_mock_excel.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "csv" / "matriz_mock.xlsx"


def main() -> None:
    regulacion = pd.DataFrame(
        [
            {"id_regulacion": 1, "ley": "Ley 1715", "incentivo": "Deducción Renta 50%", "pct_ahorro": 50.0},
            {"id_regulacion": 2, "ley": "Ley 2099", "incentivo": "Exclusión IVA Bienes/Servicios", "pct_ahorro": 19.0},
            {
                "id_regulacion": 3,
                "ley": "Marco ZNI / aislados",
                "incentivo": "Reconocimiento tarifario regional",
                "pct_ahorro": 12.0,
            },
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
            {"id_proyecto": 1, "nombre": "Hidroituango", "depto": "Antioquia", "id_tipo": 1, "capacidad_mw": 2400},
            {"id_proyecto": 2, "nombre": "Guavio", "depto": "Cundinamarca", "id_tipo": 1, "capacidad_mw": 1213},
            {"id_proyecto": 3, "nombre": "San Carlos", "depto": "Antioquia", "id_tipo": 1, "capacidad_mw": 1240},
            {"id_proyecto": 4, "nombre": "Sogamoso", "depto": "Santander", "id_tipo": 1, "capacidad_mw": 820},
            {"id_proyecto": 5, "nombre": "Chivor", "depto": "Boyacá", "id_tipo": 1, "capacidad_mw": 1000},
            {"id_proyecto": 6, "nombre": "Porce III", "depto": "Antioquia", "id_tipo": 1, "capacidad_mw": 660},
            {"id_proyecto": 7, "nombre": "Urrá I", "depto": "Córdoba", "id_tipo": 1, "capacidad_mw": 340},
            {"id_proyecto": 8, "nombre": "Betania", "depto": "Huila", "id_tipo": 1, "capacidad_mw": 540},
            {"id_proyecto": 9, "nombre": "El Quimbo", "depto": "Huila", "id_tipo": 1, "capacidad_mw": 400},
            {"id_proyecto": 20, "nombre": "La Loma Solar", "depto": "Cesar", "id_tipo": 2, "capacidad_mw": 187},
            {"id_proyecto": 21, "nombre": "Celsia Solar Tolima", "depto": "Tolima", "id_tipo": 2, "capacidad_mw": 80},
            {"id_proyecto": 22, "nombre": "Bosconia Solar", "depto": "Cesar", "id_tipo": 2, "capacidad_mw": 150},
            {"id_proyecto": 23, "nombre": "Meta Solar Park", "depto": "Meta", "id_tipo": 2, "capacidad_mw": 120},
            {"id_proyecto": 24, "nombre": "Valle Solar", "depto": "Valle del Cauca", "id_tipo": 2, "capacidad_mw": 90},
            {"id_proyecto": 25, "nombre": "Atlántico Solar", "depto": "Atlántico", "id_tipo": 2, "capacidad_mw": 70},
            {"id_proyecto": 26, "nombre": "Bolívar Solar", "depto": "Bolívar", "id_tipo": 2, "capacidad_mw": 65},
            {"id_proyecto": 27, "nombre": "Santander Solar", "depto": "Santander", "id_tipo": 2, "capacidad_mw": 85},
            {"id_proyecto": 28, "nombre": "Cauca Solar", "depto": "Cauca", "id_tipo": 2, "capacidad_mw": 60},
            {"id_proyecto": 29, "nombre": "Nariño Solar", "depto": "Nariño", "id_tipo": 2, "capacidad_mw": 50},
            {"id_proyecto": 40, "nombre": "Guajira I", "depto": "La Guajira", "id_tipo": 3, "capacidad_mw": 20},
            {"id_proyecto": 41, "nombre": "Alpha Wind", "depto": "La Guajira", "id_tipo": 3, "capacidad_mw": 504},
            {"id_proyecto": 42, "nombre": "Beta Wind", "depto": "La Guajira", "id_tipo": 3, "capacidad_mw": 300},
            {"id_proyecto": 43, "nombre": "Caribe Wind", "depto": "Atlántico", "id_tipo": 3, "capacidad_mw": 150},
            {"id_proyecto": 44, "nombre": "Magdalena Wind", "depto": "Magdalena", "id_tipo": 3, "capacidad_mw": 120},
            {"id_proyecto": 45, "nombre": "Sucre Wind", "depto": "Sucre", "id_tipo": 3, "capacidad_mw": 100},
            {"id_proyecto": 60, "nombre": "Nereidas", "depto": "Caldas", "id_tipo": 4, "capacidad_mw": 50},
            {"id_proyecto": 61, "nombre": "Nevado Geo", "depto": "Tolima", "id_tipo": 4, "capacidad_mw": 45},
            {"id_proyecto": 62, "nombre": "Ruiz Geo", "depto": "Caldas", "id_tipo": 4, "capacidad_mw": 40},
            {"id_proyecto": 63, "nombre": "Azufral Geo", "depto": "Nariño", "id_tipo": 4, "capacidad_mw": 35},
            {"id_proyecto": 80, "nombre": "Amazonas Solar", "depto": "Amazonas", "id_tipo": 2, "capacidad_mw": 20},
            {"id_proyecto": 81, "nombre": "Vaupés Solar", "depto": "Vaupés", "id_tipo": 2, "capacidad_mw": 10},
            {"id_proyecto": 82, "nombre": "Guainía Solar", "depto": "Guainía", "id_tipo": 2, "capacidad_mw": 12},
            {"id_proyecto": 83, "nombre": "Putumayo Solar", "depto": "Putumayo", "id_tipo": 2, "capacidad_mw": 25},
            {"id_proyecto": 84, "nombre": "Arauca Solar", "depto": "Arauca", "id_tipo": 2, "capacidad_mw": 30},
            {"id_proyecto": 85, "nombre": "Casanare Solar", "depto": "Casanare", "id_tipo": 2, "capacidad_mw": 70},
        ]
    )

    costos = pd.DataFrame(
        [
            {"id_proyecto": 1, "anio": 2020, "lcoe_usd_mwh": 55, "capex_musd": 2600, "opex_musd": 78},
            {"id_proyecto": 1, "anio": 2021, "lcoe_usd_mwh": 54, "capex_musd": 2620, "opex_musd": 79},
            {"id_proyecto": 1, "anio": 2022, "lcoe_usd_mwh": 52, "capex_musd": 2640, "opex_musd": 80},
            {"id_proyecto": 1, "anio": 2023, "lcoe_usd_mwh": 50, "capex_musd": 2660, "opex_musd": 82},
            {"id_proyecto": 1, "anio": 2024, "lcoe_usd_mwh": 49, "capex_musd": 2680, "opex_musd": 83},
            {"id_proyecto": 1, "anio": 2025, "lcoe_usd_mwh": 48, "capex_musd": 2700, "opex_musd": 84},
            {"id_proyecto": 1, "anio": 2026, "lcoe_usd_mwh": 47, "capex_musd": 2720, "opex_musd": 86},
            {"id_proyecto": 2, "anio": 2020, "lcoe_usd_mwh": 57, "capex_musd": 1300, "opex_musd": 40},
            {"id_proyecto": 2, "anio": 2021, "lcoe_usd_mwh": 56, "capex_musd": 1310, "opex_musd": 41},
            {"id_proyecto": 2, "anio": 2022, "lcoe_usd_mwh": 54, "capex_musd": 1320, "opex_musd": 42},
            {"id_proyecto": 2, "anio": 2023, "lcoe_usd_mwh": 52, "capex_musd": 1335, "opex_musd": 43},
            {"id_proyecto": 2, "anio": 2024, "lcoe_usd_mwh": 51, "capex_musd": 1350, "opex_musd": 44},
            {"id_proyecto": 2, "anio": 2025, "lcoe_usd_mwh": 50, "capex_musd": 1365, "opex_musd": 45},
            {"id_proyecto": 2, "anio": 2026, "lcoe_usd_mwh": 49, "capex_musd": 1380, "opex_musd": 46},
            {"id_proyecto": 4, "anio": 2020, "lcoe_usd_mwh": 60, "capex_musd": 900, "opex_musd": 28},
            {"id_proyecto": 4, "anio": 2021, "lcoe_usd_mwh": 59, "capex_musd": 910, "opex_musd": 29},
            {"id_proyecto": 4, "anio": 2022, "lcoe_usd_mwh": 57, "capex_musd": 920, "opex_musd": 30},
            {"id_proyecto": 4, "anio": 2023, "lcoe_usd_mwh": 55, "capex_musd": 930, "opex_musd": 31},
            {"id_proyecto": 4, "anio": 2024, "lcoe_usd_mwh": 54, "capex_musd": 945, "opex_musd": 32},
            {"id_proyecto": 4, "anio": 2025, "lcoe_usd_mwh": 53, "capex_musd": 960, "opex_musd": 33},
            {"id_proyecto": 4, "anio": 2026, "lcoe_usd_mwh": 52, "capex_musd": 980, "opex_musd": 34},
            {"id_proyecto": 20, "anio": 2020, "lcoe_usd_mwh": 90, "capex_musd": 210, "opex_musd": 4.5},
            {"id_proyecto": 20, "anio": 2021, "lcoe_usd_mwh": 85, "capex_musd": 205, "opex_musd": 4.3},
            {"id_proyecto": 20, "anio": 2022, "lcoe_usd_mwh": 80, "capex_musd": 200, "opex_musd": 4.1},
            {"id_proyecto": 20, "anio": 2023, "lcoe_usd_mwh": 75, "capex_musd": 195, "opex_musd": 4.0},
            {"id_proyecto": 20, "anio": 2024, "lcoe_usd_mwh": 70, "capex_musd": 190, "opex_musd": 3.9},
            {"id_proyecto": 20, "anio": 2025, "lcoe_usd_mwh": 65, "capex_musd": 188, "opex_musd": 3.8},
            {"id_proyecto": 20, "anio": 2026, "lcoe_usd_mwh": 60, "capex_musd": 185, "opex_musd": 3.7},
            {"id_proyecto": 23, "anio": 2020, "lcoe_usd_mwh": 92, "capex_musd": 140, "opex_musd": 3.2},
            {"id_proyecto": 23, "anio": 2021, "lcoe_usd_mwh": 87, "capex_musd": 135, "opex_musd": 3.1},
            {"id_proyecto": 23, "anio": 2022, "lcoe_usd_mwh": 82, "capex_musd": 130, "opex_musd": 3.0},
            {"id_proyecto": 23, "anio": 2023, "lcoe_usd_mwh": 77, "capex_musd": 125, "opex_musd": 2.9},
            {"id_proyecto": 23, "anio": 2024, "lcoe_usd_mwh": 72, "capex_musd": 122, "opex_musd": 2.8},
            {"id_proyecto": 23, "anio": 2025, "lcoe_usd_mwh": 67, "capex_musd": 120, "opex_musd": 2.7},
            {"id_proyecto": 23, "anio": 2026, "lcoe_usd_mwh": 62, "capex_musd": 118, "opex_musd": 2.6},
            {"id_proyecto": 41, "anio": 2020, "lcoe_usd_mwh": 85, "capex_musd": 600, "opex_musd": 15},
            {"id_proyecto": 41, "anio": 2021, "lcoe_usd_mwh": 82, "capex_musd": 590, "opex_musd": 14.8},
            {"id_proyecto": 41, "anio": 2022, "lcoe_usd_mwh": 80, "capex_musd": 580, "opex_musd": 14.5},
            {"id_proyecto": 41, "anio": 2023, "lcoe_usd_mwh": 78, "capex_musd": 570, "opex_musd": 14.2},
            {"id_proyecto": 41, "anio": 2024, "lcoe_usd_mwh": 75, "capex_musd": 560, "opex_musd": 14},
            {"id_proyecto": 41, "anio": 2025, "lcoe_usd_mwh": 72, "capex_musd": 550, "opex_musd": 13.8},
            {"id_proyecto": 41, "anio": 2026, "lcoe_usd_mwh": 70, "capex_musd": 540, "opex_musd": 13.5},
            {"id_proyecto": 43, "anio": 2020, "lcoe_usd_mwh": 88, "capex_musd": 190, "opex_musd": 5},
            {"id_proyecto": 43, "anio": 2021, "lcoe_usd_mwh": 85, "capex_musd": 185, "opex_musd": 4.9},
            {"id_proyecto": 43, "anio": 2022, "lcoe_usd_mwh": 82, "capex_musd": 180, "opex_musd": 4.8},
            {"id_proyecto": 43, "anio": 2023, "lcoe_usd_mwh": 79, "capex_musd": 175, "opex_musd": 4.7},
            {"id_proyecto": 43, "anio": 2024, "lcoe_usd_mwh": 76, "capex_musd": 170, "opex_musd": 4.6},
            {"id_proyecto": 43, "anio": 2025, "lcoe_usd_mwh": 73, "capex_musd": 168, "opex_musd": 4.5},
            {"id_proyecto": 43, "anio": 2026, "lcoe_usd_mwh": 70, "capex_musd": 165, "opex_musd": 4.4},
            {"id_proyecto": 60, "anio": 2020, "lcoe_usd_mwh": 60, "capex_musd": 80, "opex_musd": 3},
            {"id_proyecto": 60, "anio": 2021, "lcoe_usd_mwh": 59, "capex_musd": 82, "opex_musd": 3.1},
            {"id_proyecto": 60, "anio": 2022, "lcoe_usd_mwh": 58, "capex_musd": 84, "opex_musd": 3.2},
            {"id_proyecto": 60, "anio": 2023, "lcoe_usd_mwh": 57, "capex_musd": 86, "opex_musd": 3.3},
            {"id_proyecto": 60, "anio": 2024, "lcoe_usd_mwh": 56, "capex_musd": 88, "opex_musd": 3.4},
            {"id_proyecto": 60, "anio": 2025, "lcoe_usd_mwh": 55, "capex_musd": 90, "opex_musd": 3.5},
            {"id_proyecto": 60, "anio": 2026, "lcoe_usd_mwh": 54, "capex_musd": 92, "opex_musd": 3.6},
        ]
    )

    cobertura = pd.DataFrame(
        [
            {"id_proyecto": 1, "id_reg": 2, "usuarios": 1200000, "disponibilidad_pct": 98.7},
            {"id_proyecto": 2, "id_reg": 2, "usuarios": 620000, "disponibilidad_pct": 98.5},
            {"id_proyecto": 3, "id_reg": 2, "usuarios": 640000, "disponibilidad_pct": 98.6},
            {"id_proyecto": 4, "id_reg": 2, "usuarios": 420000, "disponibilidad_pct": 98.4},
            {"id_proyecto": 5, "id_reg": 2, "usuarios": 520000, "disponibilidad_pct": 98.6},
            {"id_proyecto": 6, "id_reg": 2, "usuarios": 350000, "disponibilidad_pct": 98.5},
            {"id_proyecto": 7, "id_reg": 2, "usuarios": 180000, "disponibilidad_pct": 98.2},
            {"id_proyecto": 8, "id_reg": 2, "usuarios": 280000, "disponibilidad_pct": 98.3},
            {"id_proyecto": 9, "id_reg": 2, "usuarios": 210000, "disponibilidad_pct": 98.2},
            {"id_proyecto": 20, "id_reg": 1, "usuarios": 95000, "disponibilidad_pct": 99.1},
            {"id_proyecto": 21, "id_reg": 1, "usuarios": 40000, "disponibilidad_pct": 99.0},
            {"id_proyecto": 22, "id_reg": 1, "usuarios": 80000, "disponibilidad_pct": 99.1},
            {"id_proyecto": 23, "id_reg": 1, "usuarios": 60000, "disponibilidad_pct": 99.0},
            {"id_proyecto": 24, "id_reg": 1, "usuarios": 45000, "disponibilidad_pct": 99.1},
            {"id_proyecto": 25, "id_reg": 1, "usuarios": 35000, "disponibilidad_pct": 99.0},
            {"id_proyecto": 26, "id_reg": 1, "usuarios": 32000, "disponibilidad_pct": 99.0},
            {"id_proyecto": 27, "id_reg": 1, "usuarios": 42000, "disponibilidad_pct": 99.1},
            {"id_proyecto": 28, "id_reg": 1, "usuarios": 30000, "disponibilidad_pct": 99.0},
            {"id_proyecto": 29, "id_reg": 1, "usuarios": 25000, "disponibilidad_pct": 99.0},
            {"id_proyecto": 40, "id_reg": 1, "usuarios": 12000, "disponibilidad_pct": 98.9},
            {"id_proyecto": 41, "id_reg": 1, "usuarios": 260000, "disponibilidad_pct": 98.8},
            {"id_proyecto": 42, "id_reg": 1, "usuarios": 160000, "disponibilidad_pct": 98.7},
            {"id_proyecto": 43, "id_reg": 1, "usuarios": 85000, "disponibilidad_pct": 98.9},
            {"id_proyecto": 44, "id_reg": 1, "usuarios": 65000, "disponibilidad_pct": 98.8},
            {"id_proyecto": 45, "id_reg": 1, "usuarios": 55000, "disponibilidad_pct": 98.7},
            {"id_proyecto": 60, "id_reg": 1, "usuarios": 30000, "disponibilidad_pct": 99.3},
            {"id_proyecto": 61, "id_reg": 1, "usuarios": 28000, "disponibilidad_pct": 99.4},
            {"id_proyecto": 62, "id_reg": 1, "usuarios": 25000, "disponibilidad_pct": 99.3},
            {"id_proyecto": 63, "id_reg": 1, "usuarios": 22000, "disponibilidad_pct": 99.4},
            {"id_proyecto": 80, "id_reg": 3, "usuarios": 10000, "disponibilidad_pct": 98.5},
            {"id_proyecto": 81, "id_reg": 3, "usuarios": 5000, "disponibilidad_pct": 98.2},
            {"id_proyecto": 82, "id_reg": 3, "usuarios": 6000, "disponibilidad_pct": 98.3},
            {"id_proyecto": 83, "id_reg": 3, "usuarios": 12000, "disponibilidad_pct": 98.4},
            {"id_proyecto": 84, "id_reg": 3, "usuarios": 15000, "disponibilidad_pct": 98.5},
            {"id_proyecto": 85, "id_reg": 3, "usuarios": 35000, "disponibilidad_pct": 98.6},
        ]
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(OUT, engine="openpyxl") as writer:
        regulacion.to_excel(writer, sheet_name="regulacion", index=False)
        tipo_energia.to_excel(writer, sheet_name="tipo_energia", index=False)
        proyectos.to_excel(writer, sheet_name="proyectos", index=False)
        costos.to_excel(writer, sheet_name="costos", index=False)
        cobertura.to_excel(writer, sheet_name="cobertura", index=False)

    print(f"Escrito: {OUT}")


if __name__ == "__main__":
    main()

"""Pruebas de helpers de interpretación (sin ejecución de Streamlit)."""

import pandas as pd

from streamlit_app import (
    _execute_query_mock,
    _fmt_qty_es,
    _interp_consulta_resultado,
    _interp_dominant_share,
    _interp_lcoe_dashboard,
    _interp_lcoe_yoy_global,
    _interp_min_max_mean_rows,
    _interp_numeric_profile,
    _load_data,
    _tukey_upper_fence,
)


def test_fmt_qty_es_miles_decimals() -> None:
    assert _fmt_qty_es(1234.56, 1) == "1.234,6"


def test_interp_numeric_profile_empty() -> None:
    assert "Sin valores" in _interp_numeric_profile(pd.Series([], dtype=float))


def test_interp_dominant_share_empty() -> None:
    assert "No hay datos" in _interp_dominant_share(
        pd.DataFrame(),
        "a",
        "b",
        "X",
        "u",
    )


def test_interp_dominant_share_tie() -> None:
    df = pd.DataFrame({"fuente": ["A", "B"], "mw": [10.0, 10.0]})
    s = _interp_dominant_share(df, "fuente", "mw", "Mayor:", "MW", "MW")
    assert "empate" in s.lower()
    assert "20" in s.replace(",", "").replace(".", "")


def test_interp_min_max_mean_with_iqr() -> None:
    df = pd.DataFrame({"c": ["a", "b", "c", "d"], "v": [1.0, 2.0, 3.0, 100.0]})
    s = _interp_min_max_mean_rows(df, "c", "v", "v", "u")
    assert "IQR" in s
    assert "Mayor" in s


def test_tukey_fence_none_small_n() -> None:
    assert _tukey_upper_fence(pd.Series([1.0, 2.0, 3.0])) is None


def test_lcoe_yoy_with_mock_data() -> None:
    d = _load_data()
    note = _interp_lcoe_yoy_global(d["costos"])
    years = sorted(d["costos"]["anio"].dropna().unique().tolist())
    assert len(years) >= 2
    assert str(years[-1]) in note and str(years[-2]) in note


def test_lcoe_dashboard_weighted() -> None:
    df = pd.DataFrame(
        {
            "fuente": ["Solar", "Eólica"],
            "lcoe_promedio": [70.0, 50.0],
            "lcoe_pond_mw": [69.0, 51.0],
        }
    )
    txt = _interp_lcoe_dashboard(df, "")
    assert "ponderado" in txt.lower()
    assert "Solar" in txt


def test_execute_query_mock_inversion_2024() -> None:
    d = _load_data()
    out = _execute_query_mock(d, "inversion", None, 2024)
    assert not out.empty
    assert set(out.columns) == {"label", "value"}
    assert (out["value"] >= 0).all()


def test_execute_query_mock_cobertura() -> None:
    d = _load_data()
    out = _execute_query_mock(d, "cobertura", None, 2024)
    assert "label" in out.columns


def test_interp_consulta_eficiencia() -> None:
    df = pd.DataFrame({"label": ["P1", "P2"], "value": [98.5, 97.0]})
    s = _interp_consulta_resultado(df, "eficiencia")
    assert "Disponibilidad" in s
    assert "P1" in s or "98" in s

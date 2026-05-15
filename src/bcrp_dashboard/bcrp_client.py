from __future__ import annotations

import re
from datetime import date
from typing import Any

import pandas as pd
import requests


def _build_url(base_url: str, series_code: str, output_format: str) -> str:
    return f"{base_url.rstrip('/')}/{series_code}/{output_format}"


_SPANISH_MONTH_MAP = {
    "ene": 1,
    "feb": 2,
    "mar": 3,
    "abr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "ago": 8,
    "set": 9,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dic": 12,
}


def _parse_month_abbrev_es(token: str) -> int | None:
    key = token.strip().lower().replace(".", "")[:3]
    return _SPANISH_MONTH_MAP.get(key)


def _parse_period_spanish_month(text: str) -> pd.Timestamp | None:
    match = re.match(r"^([A-Za-z]{3})\.(\d{4})$", text)
    if not match:
        return None

    month = _parse_month_abbrev_es(match.group(1))
    year = int(match.group(2))

    if month is None:
        return None

    return pd.Timestamp(year=year, month=month, day=1)


def _parse_period_spanish_day(text: str) -> pd.Timestamp | None:
    match = re.match(r"^(\d{1,2})\.([A-Za-z]{3})\.(\d{2,4})$", text)
    if not match:
        return None

    day = int(match.group(1))
    month = _parse_month_abbrev_es(match.group(2))
    year_token = match.group(3)

    if month is None:
        return None

    year = int(year_token)
    if len(year_token) == 2:
        year += 2000 if year < 70 else 1900

    return pd.Timestamp(year=year, month=month, day=day)


def _parse_period(value: Any) -> pd.Timestamp:
    text = str(value)

    parsed_spanish_month = _parse_period_spanish_month(text)
    if parsed_spanish_month is not None:
        return parsed_spanish_month

    parsed_spanish_day = _parse_period_spanish_day(text)
    if parsed_spanish_day is not None:
        return parsed_spanish_day

    if len(text) == 7 and text[4] == "-":
        return pd.to_datetime(text, format="%Y-%m", errors="coerce")

    if len(text) == 10 and text[4] == "-" and text[7] == "-":
        return pd.to_datetime(text, format="%Y-%m-%d", errors="coerce")

    return pd.to_datetime(text, errors="coerce")


def fetch_bcrp_series(
    series_code: str,
    base_url: str,
    output_format: str = "json",
    timeout: int = 30,
) -> dict[str, Any]:
    """Descarga una serie del BCRP en formato JSON."""
    url = _build_url(base_url=base_url, series_code=series_code, output_format=output_format)
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.json()


def parse_bcrp_json(payload: dict[str, Any], series_code: str) -> pd.DataFrame:
    """Convierte la respuesta JSON del BCRP en un DataFrame normalizado.

    El API puede devolver la data en estructuras ligeramente distintas. Esta función
    intenta resolver las variantes más comunes.
    """

    records: list[dict[str, Any]] = []

    periods = payload.get("periods", [])
    for row in periods:
        period_name = row.get("name")
        values = row.get("values", [])

        if values:
            value = values[0]
        else:
            value = None

        records.append(
            {
                "series_code": series_code,
                "period": period_name,
                "value_raw": value,
            }
        )

    if not records:
        raise ValueError(
            f"No se encontraron periodos para la serie {series_code}. Verifica código/API."
        )

    df = pd.DataFrame(records)

    # Convierte periodos mensuales (YYYY-MM) y diarios (YYYY-MM-DD) en datetime.
    df["date"] = df["period"].map(_parse_period)

    # Estandariza decimal y convierte a número.
    df["value"] = (
        df["value_raw"]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .str.replace(" ", "", regex=False)
    )
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    return df[["series_code", "date", "value", "period", "value_raw"]].sort_values("date")


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega features temporales y variaciones simples."""
    out = df.copy()
    out["year"] = out["date"].dt.year
    out["month"] = out["date"].dt.month
    out["mom_pct"] = out["value"].pct_change() * 100
    out["yoy_pct"] = out["value"].pct_change(12) * 100
    return out


def extract_series_metadata(payload: dict[str, Any]) -> dict[str, str]:
    """Extrae metadatos útiles del payload para trazabilidad en el modelo."""
    config = payload.get("config", {})
    title = str(config.get("title", "")).strip()
    series_list = config.get("series", [])

    if series_list and isinstance(series_list, list):
        series_name = str(series_list[0].get("name", "")).strip()
    else:
        series_name = title

    return {
        "title": title,
        "series_name": series_name,
    }


def filter_date_range(df: pd.DataFrame, start: date | None, end: date | None) -> pd.DataFrame:
    out = df.copy()
    if start is not None:
        out = out[out["date"] >= pd.Timestamp(start)]
    if end is not None:
        out = out[out["date"] <= pd.Timestamp(end)]
    return out

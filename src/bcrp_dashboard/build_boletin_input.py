from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_FILE = PROJECT_ROOT / "data/processed/bcrp_consolidado.parquet"
OUTPUT_FILE = PROJECT_ROOT / "data/processed/boletin_input.json"


def _trend_from_changes(mom: float | None, yoy: float | None) -> str:
    if pd.notna(yoy):
        if yoy > 0:
            return "al_alza"
        if yoy < 0:
            return "a_la_baja"
    if pd.notna(mom):
        if mom > 0:
            return "al_alza"
        if mom < 0:
            return "a_la_baja"
    return "estable"


def build_boletin_input(input_file: Path = INPUT_FILE, output_file: Path = OUTPUT_FILE) -> None:
    if not input_file.exists():
        raise FileNotFoundError(f"No se encontro {input_file}. Ejecuta primero el pipeline.")

    df = pd.read_parquet(input_file)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    summary_rows: list[dict[str, object]] = []

    for code, group in df.groupby("series_code", sort=True):
        group = group.sort_values("date")
        latest = group.iloc[-1]

        summary_rows.append(
            {
                "series_code": code,
                "series_name": latest.get("series_name", ""),
                "theme": latest.get("theme", ""),
                "unit": latest.get("unit", ""),
                "last_date": latest["date"].strftime("%Y-%m-%d") if pd.notna(latest["date"]) else None,
                "last_value": None if pd.isna(latest.get("value")) else float(latest["value"]),
                "mom_pct": None if pd.isna(latest.get("mom_pct")) else float(latest["mom_pct"]),
                "yoy_pct": None if pd.isna(latest.get("yoy_pct")) else float(latest["yoy_pct"]),
                "trend": _trend_from_changes(latest.get("mom_pct"), latest.get("yoy_pct")),
            }
        )

    payload = {
        "source": "BCRP",
        "generated_at": pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ"),
        "series_summary": summary_rows,
    }

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"Archivo generado: {output_file} ({len(summary_rows)} series)")


if __name__ == "__main__":
    build_boletin_input()

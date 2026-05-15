from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pandas as pd

from bcrp_client import (
    add_time_features,
    extract_series_metadata,
    fetch_bcrp_series,
    filter_date_range,
    parse_bcrp_json,
)
from config import PROJECT_ROOT, get_settings


def load_series_catalog(path: Path) -> pd.DataFrame:
    catalog = pd.read_csv(path)

    for col in ["theme", "priority", "series_name", "frequency", "unit"]:
        if col not in catalog.columns:
            catalog[col] = ""

    return catalog


def run_pipeline(start: date | None = None, end: date | None = None) -> None:
    settings = get_settings()
    catalog = load_series_catalog(PROJECT_ROOT / "config/series_bcrp.csv")

    settings.raw_dir.mkdir(parents=True, exist_ok=True)
    settings.processed_dir.mkdir(parents=True, exist_ok=True)

    all_clean: list[pd.DataFrame] = []
    status_rows: list[dict[str, str | int]] = []

    for row in catalog.itertuples(index=False):
        try:
            payload = fetch_bcrp_series(
                series_code=row.series_code,
                base_url=settings.base_url,
                output_format=settings.output_format,
            )

            raw_file = settings.raw_dir / f"{row.series_code}.json"
            with raw_file.open("w", encoding="utf-8") as fh:
                json.dump(payload, fh, ensure_ascii=False, indent=2)

            metadata = extract_series_metadata(payload)

            clean_df = parse_bcrp_json(payload=payload, series_code=row.series_code)
            clean_df = filter_date_range(clean_df, start=start, end=end)

            clean_df = clean_df.dropna(subset=["date", "value"]).copy()
            clean_df = add_time_features(clean_df)

            catalog_name = str(row.series_name).strip()
            clean_df["series_name"] = catalog_name if catalog_name else metadata["series_name"]
            clean_df["series_name_api"] = metadata["series_name"]
            clean_df["series_title_api"] = metadata["title"]
            clean_df["frequency"] = row.frequency
            clean_df["unit"] = row.unit
            clean_df["theme"] = row.theme
            clean_df["priority"] = row.priority
            clean_df["source"] = "BCRP"

            out_file = settings.processed_dir / f"{row.series_code}.parquet"
            clean_df.to_parquet(out_file, index=False)

            all_clean.append(clean_df)
            status_rows.append(
                {
                    "series_code": row.series_code,
                    "status": "ok",
                    "rows": len(clean_df),
                    "message": "",
                }
            )
            print(f"Serie {row.series_code} procesada: {len(clean_df)} filas")
        except Exception as exc:
            status_rows.append(
                {
                    "series_code": row.series_code,
                    "status": "error",
                    "rows": 0,
                    "message": str(exc),
                }
            )
            print(f"Serie {row.series_code} con error: {exc}")

    status_df = pd.DataFrame(status_rows)
    status_df.to_csv(settings.processed_dir / "etl_status.csv", index=False)

    if not all_clean:
        raise RuntimeError("No se procesaron series correctamente. Revisa data/processed/etl_status.csv")

    consolidated = pd.concat(all_clean, ignore_index=True)
    consolidated.to_parquet(settings.processed_dir / "bcrp_consolidado.parquet", index=False)
    consolidated.to_csv(settings.processed_dir / "bcrp_consolidado.csv", index=False)

    ok_count = (status_df["status"] == "ok").sum()
    error_count = (status_df["status"] == "error").sum()
    print(f"Pipeline completado. Series OK: {ok_count}, Series con error: {error_count}")


if __name__ == "__main__":
    run_pipeline()

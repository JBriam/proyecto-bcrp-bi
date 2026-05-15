from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _resolve_path(raw_path: str, default_relative: str) -> Path:
    """Resolve environment paths relative to project root when needed."""
    candidate = Path(raw_path or default_relative)
    if candidate.is_absolute():
        return candidate
    return PROJECT_ROOT / candidate


@dataclass(frozen=True)
class Settings:
    """Configuración de entorno para el proyecto."""

    base_url: str = os.getenv(
        "BCRP_BASE_URL", "https://estadisticas.bcrp.gob.pe/estadisticas/series/api"
    )
    output_format: str = os.getenv("BCRP_OUTPUT_FORMAT", "json")
    raw_dir: Path = _resolve_path(os.getenv("RAW_DIR", ""), "data/raw")
    processed_dir: Path = _resolve_path(os.getenv("PROCESSED_DIR", ""), "data/processed")


def get_settings() -> Settings:
    return Settings()

"""
Utility — CSV data loader
Resolves the correct folder based on sample parameter (national | rural)
"""

from pathlib import Path
from typing import Literal

import pandas as pd
from fastapi import HTTPException

# ── Rutas base ────────────────────────────────────────────────────────────────
BASE_NACIONAL = Path("data/output")
BASE_RURAL = Path("data/output_rural")

SampleType = Literal["national", "rural"]

FILES = {
    "perfiles": "tabla_perfiles_clases.csv",
    "ajuste_lca": "lca_resumen_ajuste.csv",
    "rend_clase": "lca_rendimiento_por_clase.csv",
    "irt_ret": "irt_parametros_retenidos.csv",
    "irt_todos": "irt_parametros_todos.csv",
    "efa_cargas": "efa_cargas_factoriales.csv",
    "anova": "tabla_anova_factores.csv",
    "ctx_escuela": "tabla_contexto_escuela.csv",
    "ctx_comunidad": "tabla_contexto_comunidad.csv",
}


def base_path(sample: SampleType) -> Path:
    return BASE_RURAL if sample == "rural" else BASE_NACIONAL


def load_csv(sample: SampleType, key: str) -> pd.DataFrame:
    """Load a CSV file for the given sample. Raises 404 if not found."""
    path = base_path(sample) / FILES[key]
    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"File '{FILES[key]}' not found for sample='{sample}'. "
            f"Expected at: {path}",
        )
    return pd.read_csv(path, index_col=0)


def sample_meta(sample: SampleType) -> dict:
    """Return basic metadata for a sample."""
    if sample == "rural":
        return {
            "sample": "rural",
            "description": "Rural and semi-rural subsample of Peru",
            "filter": "SC001Q01TA: village/hamlet/rural area + small town",
            "n_students": 3720,
            "n_classes": 4,
            "n_items_irt": 129,
        }
    return {
        "sample": "national",
        "description": "Full national sample of Peru",
        "filter": "CNT = PER",
        "n_students": 6968,
        "n_classes": 7,
        "n_items_irt": 152,
    }

"""
Router: /irt
Item Response Theory results.
"""

from fastapi import APIRouter, Query
from data_loader import load_csv, SampleType

router = APIRouter()


@router.get("/summary", summary="IRT results summary")
def irt_summary(
    sample: SampleType = Query("rural", description="Sample: 'national' or 'rural'"),
):
    """
    Returns a summary of IRT calibration results including model types used,
    discrimination threshold, and retention statistics for both 2PL and GRM models.
    """
    df_todos = load_csv(sample, "irt_todos")
    df_ret   = load_csv(sample, "irt_ret")

    UMBRAL = 0.50

    resumen = {}
    for modelo in ["2PL", "GRM"]:
        sub_todos = df_todos[df_todos["modelo"] == modelo]
        sub_ret   = df_ret[df_ret["modelo"]   == modelo]
        resumen[modelo] = {
            "item_type"    : "Dichotomous (0/1)" if modelo == "2PL" else "Polytomous (3-10 categories)",
            "total_items"  : int(len(sub_todos)),
            "retained"     : int(len(sub_ret)),
            "discarded"    : int(len(sub_todos) - len(sub_ret)),
            "mean_discrimination_retained": round(float(sub_ret["discriminacion"].mean()), 3) if len(sub_ret) > 0 else None,
        }

    return {
        "sample"               : sample,
        "discrimination_threshold": UMBRAL,
        "models"               : resumen,
        "total_input"          : int(len(df_todos)),
        "total_retained"       : int(len(df_ret)),
        "total_discarded"      : int(len(df_todos) - len(df_ret)),
        "mean_discrimination"  : round(float(df_ret["discriminacion"].mean()), 3),
        "min_discrimination"   : round(float(df_ret["discriminacion"].min()), 3),
        "max_discrimination"   : round(float(df_ret["discriminacion"].max()), 3),
        "note": (
            "Items with discrimination parameter a < 0.50 were discarded. "
            "Higher discrimination values indicate better ability to differentiate "
            "between students of different proficiency levels."
        ),
    }


@router.get("/items", summary="List retained IRT items")
def irt_items(
    sample : SampleType = Query("rural", description="Sample: 'national' or 'rural'"),
    modelo : str        = Query(None, description="Filter by model: '2PL' or 'GRM'"),
    sort_by: str        = Query("discriminacion", description="Sort by: 'discriminacion' or 'dificultad'"),
    top_n  : int        = Query(20, ge=5, le=200, description="Number of items to return"),
):
    """
    Returns retained IRT items sorted by discrimination parameter (descending).
    Optionally filter by model type (2PL or GRM).
    """
    df = load_csv(sample, "irt_ret")

    if modelo:
        modelo_upper = modelo.upper()
        df = df[df["modelo"] == modelo_upper]
        if df.empty:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=404,
                detail=f"No retained items found for model='{modelo}' in sample='{sample}'."
            )

    if sort_by not in ["discriminacion", "dificultad"]:
        sort_by = "discriminacion"

    df_sorted = df.sort_values(sort_by, ascending=False).head(top_n)

    items = []
    for item, row in df_sorted.iterrows():
        items.append({
            "item"          : str(item) if not isinstance(item, str) else item,
            "model"         : str(row.get("modelo", "")),
            "discrimination": round(float(row["discriminacion"]), 3),
            "difficulty"    : round(float(row["dificultad"]), 3),
            "n_categories"  : int(row["n_categorias"]) if "n_categorias" in row else None,
        })

    return {
        "sample"          : sample,
        "model_filter"    : modelo or "all",
        "sorted_by"       : sort_by,
        "items_returned"  : len(items),
        "items"           : items,
    }


@router.get("/top-discriminating", summary="Top discriminating items across all blocks")
def top_discriminating(
    sample: SampleType = Query("rural", description="Sample: 'national' or 'rural'"),
    n     : int        = Query(10, ge=3, le=50, description="Number of top items"),
):
    """
    Returns the N items with the highest discrimination parameter,
    regardless of model type. These are the items that best differentiate
    between students of different proficiency levels.
    """
    df = load_csv(sample, "irt_ret")
    top = df.nlargest(n, "discriminacion")

    items = []
    for item, row in top.iterrows():
        items.append({
            "item"          : str(item) if not isinstance(item, str) else item,
            "model"         : str(row.get("modelo", "")),
            "discrimination": round(float(row["discriminacion"]), 3),
            "difficulty"    : round(float(row["dificultad"]), 3),
        })

    return {
        "sample"         : sample,
        "top_n"          : n,
        "items"          : items,
        "interpretation" : (
            "Items with discrimination a > 1.0 are considered highly discriminating. "
            "Items with a = 5.0 hit the upper bound set by the girth library."
        ),
    }

"""
Router: /efa
Exploratory Factor Analysis results.
"""

import math
from fastapi import APIRouter, Query
from data_loader import load_csv, SampleType

router = APIRouter()

# Nombres interpretativos de factores — rural
FACTOR_NAMES_RURAL = {
    "F1_estudiante" : "Cultural capital and home resources",
    "F2_estudiante" : "Mathematics learning strategies",
    "F3_estudiante" : "Digital resources at home",
    "F4_estudiante" : "Sense of school belonging",
    "F5_estudiante" : "Exposure to school violence",
    "F6_estudiante" : "Participation in mathematics classes",
    "F7_estudiante" : "Peer relationships and social belonging",
    "F8_estudiante" : "Parental education level",
    "F9_estudiante" : "Mathematics self-concept",
    "F10_estudiante": "Participation in extracurricular mathematics activities",
    "F1_escuela_b"  : "Formative teacher feedback",
    "F2_escuela_b"  : "Instructional leadership of the principal",
    "F3_escuela_b"  : "Teacher collaboration",
    "F4_escuela_b"  : "ICT availability in the classroom",
    "F5_escuela_b"  : "Frequency of digital resource use",
    "F6_escuela_b"  : "School-family communication",
    "F1_escuela_c"  : "School governance and funding type",
    "F2_escuela_c"  : "School adaptations during COVID-19",
    "F3_escuela_c"  : "Post-COVID pedagogical practices",
    "F4_escuela_c"  : "Student wellbeing support programmes",
    "F5_escuela_c"  : "Perceived obstacles and lack of external support",
    "F6_escuela_c"  : "Advanced pedagogical use of ICT",
    "F1_finanzas"   : "Understanding of basic financial concepts",
    "F2_finanzas"   : "Application of financial knowledge",
    "F3_finanzas"   : "Money management and personal savings",
    "F4_finanzas"   : "Financial decision-making under risk",
    "F5_finanzas"   : "Understanding of complex financial products",
    "F6_finanzas"   : "Long-term financial planning",
    "F7_finanzas"   : "Access to and use of financial services",
    "F8_finanzas"   : "Financial experiences in the household",
    "F1_otros"      : "Student educational trajectory",
}

# Nombres interpretativos de factores — nacional
FACTOR_NAMES_NATIONAL = {
    "F1_estudiante" : "Creative activities outside school",
    "F2_estudiante" : "Cultural capital and home resources",
    "F3_estudiante" : "Exposure to school violence and bullying",
    "F4_estudiante" : "Mathematics learning strategies",
    "F5_estudiante" : "Educational expectations and aspirations",
    "F6_estudiante" : "Digital resources at home",
    "F7_estudiante" : "Sense of school belonging",
    "F8_estudiante" : "Participation in mathematics classes",
    "F9_estudiante" : "Mathematics anxiety",
    "F1_escuela_a"  : "Digital technology use in school",
    "F2_escuela_a"  : "Use of standardised assessments",
    "F3_escuela_a"  : "Shortage of educational resources",
    "F4_escuela_a"  : "Shortage of teaching staff",
    "F5_escuela_a"  : "School governance autonomy",
    "F6_escuela_a"  : "Principal inclusive attitudes",
    "F1_escuela_b"  : "Formative teacher feedback",
    "F2_escuela_b"  : "Instructional leadership of the principal",
    "F3_escuela_b"  : "Teacher collaboration",
    "F4_escuela_b"  : "ICT availability in the classroom",
    "F5_escuela_b"  : "Frequency of digital resource use",
    "F6_escuela_b"  : "School-family communication",
    "F1_escuela_c"  : "School governance and funding type",
    "F2_escuela_c"  : "School adaptations during COVID-19",
    "F3_escuela_c"  : "Post-COVID pedagogical practices",
    "F4_escuela_c"  : "Student wellbeing support programmes",
    "F5_escuela_c"  : "Obstacles to mathematics learning",
    "F6_escuela_c"  : "Advanced pedagogical use of ICT",
    "F1_finanzas"   : "Understanding of basic financial concepts",
    "F2_finanzas"   : "Application of financial knowledge",
    "F3_finanzas"   : "Financial decision-making under risk",
    "F4_finanzas"   : "Money management and personal savings",
    "F5_finanzas"   : "Understanding of complex financial products",
    "F6_finanzas"   : "Long-term financial planning",
    "F7_finanzas"   : "Financial experiences in the household",
    "F8_finanzas"   : "Access to and use of financial services",
    "F2_otros"      : "Student educational trajectory",
    "F5_otros"      : "Class size",
}


def get_factor_names(sample: SampleType) -> dict:
    return FACTOR_NAMES_RURAL if sample == "rural" else FACTOR_NAMES_NATIONAL


@router.get("/factors", summary="List all identified EFA factors")
def list_factors(
    sample: SampleType = Query("rural", description="Sample: 'national' or 'rural'"),
    block : str        = Query(None,    description="Filter by block: estudiante, escuela_b, escuela_c, finanzas, otros"),
):
    """
    Returns all latent factors identified by EFA with their interpretive names,
    block of origin, and number of items with loading ≥ 0.40.
    """
    df = load_csv(sample, "efa_cargas")
    names = get_factor_names(sample)

    factor_cols = [c for c in df.columns if c.startswith("F") and "_" in c
                   and c in names]

    result = []
    bloques_vistos = set()

    for col in factor_cols:
        bloque = "_".join(col.split("_")[1:])
        if block and bloque != block:
            continue

        df_bloque = df[df["bloque"] == bloque]
        n_items = int((df_bloque[col].abs() >= 0.40).sum()) if col in df_bloque.columns else 0

        result.append({
            "factor_id"  : col,
            "name"       : names.get(col, col),
            "block"      : bloque,
            "n_items"    : n_items,
        })
        bloques_vistos.add(bloque)

    return {
        "sample"      : sample,
        "total_factors": len(result),
        "blocks"      : sorted(bloques_vistos),
        "factors"     : result,
    }


@router.get("/factors/{factor_id}", summary="Get top items for a specific factor")
def factor_detail(
    factor_id: str,
    sample    : SampleType = Query("rural", description="Sample: 'national' or 'rural'"),
    top_n     : int        = Query(8, ge=3, le=20, description="Number of top items to return"),
):
    """
    Returns the top items with highest absolute loading for a specific factor,
    along with the factor's interpretive name and block.

    Example: `/efa/factors/F1_estudiante?sample=rural`
    """
    df    = load_csv(sample, "efa_cargas")
    names = get_factor_names(sample)

    if factor_id not in df.columns:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=404,
            detail=f"Factor '{factor_id}' not found for sample='{sample}'. "
                   f"Use GET /efa/factors to see available factors."
        )

    bloque = "_".join(factor_id.split("_")[1:])
    df_bloque = df[df["bloque"] == bloque].copy()

    df_bloque["abs_loading"] = df_bloque[factor_id].abs()
    top = df_bloque.nlargest(top_n, "abs_loading")

    items = []
    for item, row in top.iterrows():
        loading = float(row[factor_id])
        if math.isnan(loading):
            continue
        items.append({
            "item"        : item,
            "loading"     : round(loading, 3),
            "abs_loading" : round(abs(loading), 3),
            "selected"    : bool(row.get("seleccionado", abs(loading) >= 0.40)),
        })

    return {
        "factor_id"  : factor_id,
        "name"       : names.get(factor_id, factor_id),
        "block"      : bloque,
        "sample"     : sample,
        "top_items"  : items,
        "note"       : "Loading sign indicates direction. Absolute value indicates strength.",
    }


@router.get("/blocks", summary="Summary of EFA results by block")
def blocks_summary(
    sample: SampleType = Query("rural", description="Sample: 'national' or 'rural'"),
):
    """
    Returns EFA summary per questionnaire block: KMO adequacy, number of
    factors extracted, and number of items retained.
    """
    kmo_info = {
        "rural": {
            "estudiante": {"kmo": 0.760, "bartlett_p": "<0.001", "factors": 10, "items": 47, "status": "adequate"},
            "escuela_a" : {"kmo": 0.485, "bartlett_p": "<0.001", "factors": 0,  "items": 0,  "status": "omitted — KMO below threshold (0.50). Reflects institutional homogeneity of rural schools."},
            "escuela_b" : {"kmo": 0.546, "bartlett_p": "<0.001", "factors": 6,  "items": 34, "status": "acceptable"},
            "escuela_c" : {"kmo": 0.557, "bartlett_p": "<0.001", "factors": 6,  "items": 49, "status": "acceptable"},
            "finanzas"  : {"kmo": 0.895, "bartlett_p": "<0.001", "factors": 8,  "items": 51, "status": "excellent"},
            "otros"     : {"kmo": 0.664, "bartlett_p": "<0.001", "factors": 5,  "items": 17, "status": "adequate"},
        },
        "national": {
            "estudiante": {"kmo": 0.809, "bartlett_p": "<0.001", "factors": 10, "items": 59, "status": "adequate"},
            "escuela_a" : {"kmo": 0.809, "bartlett_p": "<0.001", "factors": 6,  "items": 32, "status": "adequate"},
            "escuela_b" : {"kmo": None,  "bartlett_p": "<0.001", "factors": 6,  "items": 31, "status": "adequate"},
            "escuela_c" : {"kmo": None,  "bartlett_p": "<0.001", "factors": 6,  "items": 41, "status": "adequate"},
            "finanzas"  : {"kmo": 0.895, "bartlett_p": "<0.001", "factors": 8,  "items": 51, "status": "excellent"},
            "otros"     : {"kmo": 0.664, "bartlett_p": "<0.001", "factors": 5,  "items": 21, "status": "adequate"},
        },
    }

    data = kmo_info[sample]
    total_factors = sum(v["factors"] for v in data.values())
    total_items   = sum(v["items"]   for v in data.values())

    return {
        "sample"        : sample,
        "total_factors" : total_factors,
        "total_items"   : total_items,
        "rotation"      : "Oblimin",
        "loading_threshold": 0.40,
        "kmo_threshold" : 0.50,
        "blocks"        : data,
    }

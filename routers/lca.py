"""
Router: /lca
Latent Class Analysis results.
"""

from fastapi import APIRouter, HTTPException, Query

from data_loader import SampleType, load_csv

router = APIRouter()

CLASS_LABELS = {
    "rural": {
        2: "Class 1 — Outstanding performance",
        0: "Class 2 — Medium performance",
        1: "Class 3 — Medium-low performance",
        3: "Class 4 — Low performance",
    },
    "national": {
        2: "Class 1 — Outstanding performance",
        6: "Class 2 — High performance",
        3: "Class 3 — Medium-high performance A",
        1: "Class 4 — Medium-high performance B",
        0: "Class 5 — Medium performance",
        4: "Class 6 — Medium-low performance",
        5: "Class 7 — Low performance",
    },
}

CLASS_PROFILES = {
    "rural": {
        "Class 1 — Outstanding performance": {
            "mean_pisa_score": 446.2,
            "n_students": 768,
            "pct_sample": 20.6,
            "lca_id": 2,
            "key_factors": [
                {
                    "factor": "School governance and funding type",
                    "z_score": 1.76,
                    "level": "High (private school)",
                },
                {
                    "factor": "Formative teacher feedback",
                    "z_score": 0.93,
                    "level": "High",
                },
                {
                    "factor": "Cultural capital and home resources",
                    "z_score": 0.78,
                    "level": "High",
                },
                {
                    "factor": "Perceived obstacles (low)",
                    "z_score": 0.80,
                    "level": "High (few obstacles)",
                },
                {
                    "factor": "Parental education level",
                    "z_score": 0.57,
                    "level": "Moderate-high",
                },
            ],
            "interpretation": (
                "Students in rural private schools with high-quality teacher feedback and "
                "strong family cultural capital. The dominant structural factor is private "
                "school attendance (93.5% of this class). High performance despite rural context "
                "is primarily explained by institutional type, not student-level characteristics."
            ),
            "key_finding": "High performance in rural areas is almost exclusively associated with private school attendance.",
        },
        "Class 2 — Medium performance": {
            "mean_pisa_score": 398.3,
            "n_students": 938,
            "pct_sample": 25.2,
            "lca_id": 0,
            "key_factors": [
                {
                    "factor": "Understanding of basic financial concepts",
                    "z_score": 0.65,
                    "level": "High",
                },
                {
                    "factor": "Financial decision-making under risk",
                    "z_score": 0.53,
                    "level": "Moderate-high",
                },
                {
                    "factor": "School governance (public school)",
                    "z_score": -0.48,
                    "level": "Public school",
                },
                {
                    "factor": "Formative teacher feedback",
                    "z_score": -0.37,
                    "level": "Low",
                },
                {
                    "factor": "Cultural capital and home resources",
                    "z_score": 0.23,
                    "level": "Moderate",
                },
            ],
            "interpretation": (
                "100% public school students with relatively high financial literacy, "
                "possibly transmitted through practical household financial management "
                "in rural contexts. Low teacher feedback despite moderate cultural capital. "
                "62.5% in small towns (vs rural areas), suggesting slightly better access to services."
            ),
            "key_finding": "Financial literacy as practical capital transmitted through family in rural contexts, independent of school quality.",
        },
        "Class 3 — Medium-low performance": {
            "mean_pisa_score": 382.2,
            "n_students": 639,
            "pct_sample": 17.2,
            "lca_id": 1,
            "key_factors": [
                {
                    "factor": "Post-COVID pedagogical practices",
                    "z_score": -1.12,
                    "level": "Very low",
                },
                {
                    "factor": "School adaptations during COVID-19",
                    "z_score": -0.35,
                    "level": "Low",
                },
                {
                    "factor": "ICT availability in the classroom",
                    "z_score": -0.32,
                    "level": "Low",
                },
                {"factor": "Teacher collaboration", "z_score": -0.40, "level": "Low"},
                {
                    "factor": "Advanced pedagogical use of ICT",
                    "z_score": 0.55,
                    "level": "High when available",
                },
            ],
            "interpretation": (
                "Schools that failed to adopt post-COVID pedagogical practices (z=-1.12, "
                "most extreme value in the entire dataset). Low ICT access and teacher collaboration. "
                "Paradoxically, when ICT is available it is used effectively (z=+0.55). "
                "58.8% in purely rural communities — the most rural class in the sample. "
                "Represents concentrated pandemic educational impact in rural Peru."
            ),
            "key_finding": "Concentrated post-COVID pedagogical lag in purely rural communities. The pandemic did not affect all rural students equally.",
        },
        "Class 4 — Low performance": {
            "mean_pisa_score": 354.7,
            "n_students": 1375,
            "pct_sample": 37.0,
            "lca_id": 3,
            "key_factors": [
                {
                    "factor": "Understanding of basic financial concepts",
                    "z_score": -0.66,
                    "level": "Low",
                },
                {
                    "factor": "Application of financial knowledge",
                    "z_score": -0.41,
                    "level": "Low",
                },
                {
                    "factor": "Cultural capital and home resources",
                    "z_score": -0.47,
                    "level": "Low",
                },
                {
                    "factor": "Parental education level",
                    "z_score": -0.26,
                    "level": "Low",
                },
                {
                    "factor": "Post-COVID pedagogical practices",
                    "z_score": 0.52,
                    "level": "Moderate (school tried)",
                },
            ],
            "interpretation": (
                "Largest class (37% of rural students). Accumulation of disadvantages across "
                "all family capital dimensions: cultural, educational, and financial. "
                "Despite school attempting post-COVID adaptations (z=+0.52), structural family "
                "barriers prevent academic improvement. 100% public school. "
                "54.3% in purely rural communities."
            ),
            "key_finding": "School interventions alone cannot compensate for the accumulation of family disadvantages. The most vulnerable rural profile.",
        },
    },
}


@router.get("/model-selection", summary="LCA model selection criteria")
def model_selection(
    sample: SampleType = Query("rural", description="Sample: 'national' or 'rural'"),
):
    """
    Returns BIC, AIC, and entropy for all tested LCA models,
    along with the selected model and its justification.
    """
    df = load_csv(sample, "ajuste_lca")
    df = df.reset_index(drop=True)

    models = []
    for _, row in df.iterrows():
        models.append(
            {
                # "n_classes": int(row["n_clases"]),
                "BIC": round(float(row["BIC"]), 2),
                "AIC": round(float(row["AIC"]), 2),
                "entropy": round(float(row["Entropía"]), 4),
            }
        )

    selected = 4 if sample == "rural" else 7
    justification = (
        (
            "Models with 5+ classes produced at least one class below the 5% minimum "
            "size threshold (n<186), indicating insufficient statistical power for "
            "finer-grained profiles in the rural subsample (n=3,720). "
            "The 4-class model is the most complex model with all classes above 5%."
        )
        if sample == "rural"
        else (
            "BIC increased at 8 classes (point of inflection), indicating that adding "
            "an 8th class does not improve model fit. Entropy of 0.980 and all classes "
            "above 5% minimum size confirm the 7-class solution."
        )
    )

    return {
        "sample": sample,
        "models_tested": models,
        "selected_model": selected,
        "selection_criteria": [
            "BIC minimum",
            "Entropy ≥ 0.80",
            "Minimum class size ≥ 5%",
        ],
        "justification": justification,
        "anova_validation": {
            "F": 397.59 if sample == "national" else 327.43,
            "p_value": "<0.001",
            "interpretation": "Classes differ significantly in academic performance.",
        },
    }


@router.get("/classes", summary="Summary of all latent classes")
def classes_summary(
    sample: SampleType = Query("rural", description="Sample: 'national' or 'rural'"),
):
    """
    Returns a summary of all latent classes with their mean PISA score,
    size, and percentage of the sample.
    """
    df = load_csv(sample, "rend_clase")
    df = df.reset_index()
    labels = CLASS_LABELS[sample]

    classes = []
    for _, row in df.sort_values("Media", ascending=False).iterrows():
        lca_id = (
            int(row.iloc[0])
            if hasattr(row.iloc[0], "item")
            else int(row.index[0])
            if isinstance(row.name, int)
            else None
        )
        try:
            lca_id = (
                int(row["clase_lca"]) if "clase_lca" in row.index else int(row.iloc[0])
            )
        except Exception:
            lca_id = None

        classes.append(
            {
                "lca_internal_id": lca_id,
                "label": labels.get(lca_id, f"Class {lca_id}"),
                "mean_pisa_score": round(float(row["Media"]), 1),
                "sd": round(float(row["SD"]), 1),
                "n_students": int(row["N"]),
                "pct_sample": round(
                    float(row["N"]) / (3720 if sample == "rural" else 6968) * 100, 1
                ),
            }
        )

    return {
        "sample": sample,
        "n_classes": len(classes),
        "pisa_score_range": {
            "min": min(c["mean_pisa_score"] for c in classes),
            "max": max(c["mean_pisa_score"] for c in classes),
        },
        "classes": classes,
        "note": "Classes ordered by mean PISA score (descending).",
    }


@router.get(
    "/classes/{class_label}", summary="Detailed profile of a specific latent class"
)
def class_detail(
    class_label: str,
    sample: SampleType = Query("rural", description="Sample: 'national' or 'rural'"),
):
    """
    Returns the full profile of a specific latent class including key latent variables,
    interpretation, and main research finding.

    Available class labels (rural):
    - `Class 1 — Outstanding performance`
    - `Class 2 — Medium performance`
    - `Class 3 — Medium-low performance`
    - `Class 4 — Low performance`

    Example: `/lca/classes/Class 4 — Low performance?sample=rural`
    """
    if sample not in CLASS_PROFILES:
        raise HTTPException(
            status_code=404,
            detail=f"Detailed profiles not yet available for sample='{sample}'. "
            f"Currently available: rural",
        )

    profiles = CLASS_PROFILES[sample]
    if class_label not in profiles:
        raise HTTPException(
            status_code=404,
            detail=f"Class '{class_label}' not found. "
            f"Available: {list(profiles.keys())}",
        )

    return {
        "sample": sample,
        "class": class_label,
        "profile": profiles[class_label],
    }


@router.get(
    "/discriminating-variables",
    summary="Top latent variables discriminating between classes",
)
def discriminating_variables(
    sample: SampleType = Query("rural", description="Sample: 'national' or 'rural'"),
    top_n: int = Query(15, ge=5, le=31, description="Number of top variables"),
):
    """
    Returns the latent variables (EFA factors) that most strongly differentiate
    between latent classes, ranked by ANOVA F-statistic.
    """
    df = load_csv(sample, "anova")
    df = df.reset_index(drop=True)

    top = df.head(top_n)
    variables = []
    for _, row in top.iterrows():
        variables.append(
            {
                "factor": str(row.get("factor", "")),
                "name": str(row.get("nombre", "")),
                "F_statistic": round(float(row["F"]), 2),
                "p_value": "<0.001"
                if float(row["p_valor"]) < 0.001
                else round(float(row["p_valor"]), 4),
                "range_means": round(float(row["rango_medias"]), 3),
            }
        )

    return {
        "sample": sample,
        "top_n": top_n,
        "method": "One-way ANOVA on standardised factor scores by latent class",
        "variables": variables,
        "note": "F-statistic indicates the degree to which each latent variable discriminates between classes. Higher F = stronger discrimination.",
    }


@router.get(
    "/profiles-heatmap", summary="Full profile matrix (z-scores by factor and class)"
)
def profiles_heatmap(
    sample: SampleType = Query("rural", description="Sample: 'national' or 'rural'"),
):
    """
    Returns the complete profile matrix: standardised z-scores for each latent
    variable (EFA factor) by latent class. This is the data underlying Figure 5.

    Interpretation scale:
    - z > 0.50  → High
    - 0.20 to 0.50 → Moderate
    - -0.20 to 0.20 → Neutral
    - -0.50 to -0.20 → Moderate-low
    - z < -0.50 → Low
    """
    df = load_csv(sample, "perfiles")

    result = {}
    for col in df.columns:
        result[col] = {}
        for factor, val in df[col].items():
            try:
                z = round(float(val), 3)
                if z > 0.50:
                    level = "High"
                elif z > 0.20:
                    level = "Moderate"
                elif z > -0.20:
                    level = "Neutral"
                elif z > -0.50:
                    level = "Moderate-low"
                else:
                    level = "Low"
                result[col][str(factor)] = {"z_score": z, "level": level}
            except (ValueError, TypeError):
                pass

    return {
        "sample": sample,
        "interpretation_scale": {
            "High": "z > 0.50",
            "Moderate": "0.20 to 0.50",
            "Neutral": "-0.20 to 0.20",
            "Moderate-low": "-0.50 to -0.20",
            "Low": "z < -0.50",
        },
        "profiles": result,
    }

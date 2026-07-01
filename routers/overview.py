"""
Router: /overview
General summary of the research and available results.
"""

from fastapi import APIRouter, Query
from data_loader import sample_meta, SampleType

router = APIRouter()


@router.get("/", summary="Research overview and sample summary")
def overview(sample: SampleType = Query("rural", description="Sample: 'national' or 'rural'")):
    """
    Returns a general summary of the research pipeline and results
    for the selected sample.

    - **national**: Full Peru sample (n=6,968), 7 latent classes
    - **rural**: Rural/semi-rural subsample (n=3,720), 4 latent classes
    """
    meta = sample_meta(sample)

    pipeline = {
        "step_1_preprocessing": {
            "description"     : "Automated filtering and cleaning",
            "input_vars"      : 7147,
            "output_vars"     : 592 if sample == "national" else 573,
            "missing_threshold": "40%",
            "imputation"      : "Median substitution (7.12% mean missing)",
        },
        "step_2_efa": {
            "description"   : "Exploratory Factor Analysis by questionnaire blocks",
            "rotation"      : "Oblimin",
            "loading_threshold": 0.40,
            "kmo_threshold" : 0.50,
            "blocks"        : 6 if sample == "national" else 5,
            "items_selected": 235 if sample == "national" else 198,
            "factors"       : 36 if sample == "national" else 31,
            "note"          : "School A block omitted in rural sample (KMO=0.485)" if sample == "rural" else None,
        },
        "step_3_irt": {
            "description"        : "Item Response Theory calibration",
            "models"             : ["2PL (dichotomous)", "GRM (polytomous)"],
            "discrimination_threshold": 0.50,
            "items_input"        : 235 if sample == "national" else 198,
            "items_retained"     : meta["n_items_irt"],
            "mean_discrimination": 1.029 if sample == "national" else 1.109,
        },
        "step_4_lca": {
            "description"   : "Latent Class Analysis",
            "models_tested" : "2 to 10 classes" if sample == "national" else "2 to 8 classes",
            "selection_criteria": ["BIC", "Relative entropy", "Minimum class size ≥5%"],
            "final_classes" : meta["n_classes"],
            "entropy"       : 0.980 if sample == "national" else 0.975,
            "anova_f"       : 397.59 if sample == "national" else 327.43,
            "anova_p"       : "<0.001",
            "performance_anchor": "Mean of 30 Plausible Values (Math + Reading + Science)",
        },
    }

    return {
        "research": {
            "title"   : "Latent Variable Identification for Academic Performance in Rural Peru: "
                        "An Integrated EFA-IRT-LCA Approach Using PISA 2022 Data",
            "data"    : "PISA 2022 Peru — STU_QQQ + SCH_QQQ + TCH_QQQ",
            "method"  : "EFA → IRT → LCA sequential pipeline",
            "target"  : "Identify latent variables explaining academic performance",
        },
        "sample"  : meta,
        "pipeline": pipeline,
    }

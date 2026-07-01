"""
Router: /context
Contextual characterisation of latent classes by school and community type.
"""

from fastapi import APIRouter, Query
from data_loader import load_csv, SampleType

router = APIRouter()


@router.get("/school-type", summary="School type distribution by latent class")
def school_type(
    sample: SampleType = Query("rural", description="Sample: 'national' or 'rural'"),
):
    """
    Returns the distribution of school type (public/private) within each
    latent class as percentages.

    Key finding for rural sample:
    - Class 1 (outstanding): 93.5% private schools
    - Classes 2, 3, 4: 100% public schools
    """
    df = load_csv(sample, "ctx_escuela")
    df = df.reset_index()

    result = []
    for _, row in df.iterrows():
        clase = str(row.iloc[0])
        distribusion = {}
        for col in df.columns[1:]:
            try:
                distribusion[str(col)] = round(float(row[col]), 1)
            except (ValueError, TypeError):
                pass
        result.append({
            "class"       : clase,
            "distribution": distribusion,
        })

    return {
        "sample"      : sample,
        "variable"    : "SC013Q01TA — School type (public/private)",
        "unit"        : "Percentage within each latent class",
        "classes"     : result,
        "key_finding" : (
            "In the rural sample, 93.5% of Class 1 (outstanding performance) students "
            "attend private schools, while Classes 2, 3, and 4 are composed entirely "
            "of public school students (100%). This stark stratification suggests that "
            "private school attendance is the primary structural determinant of "
            "academic achievement in rural Peru."
        ) if sample == "rural" else (
            "In the national sample, school type shows a less binary distribution "
            "than in the rural subsample, with mixed classes across performance levels."
        ),
    }


@router.get("/community-type", summary="Community type distribution by latent class")
def community_type(
    sample: SampleType = Query("rural", description="Sample: 'national' or 'rural'"),
):
    """
    Returns the distribution of community type (rural/small town) within each
    latent class as percentages.

    Key finding: Lower-performing classes show higher concentration
    in purely rural communities.
    """
    df = load_csv(sample, "ctx_comunidad")
    df = df.reset_index()

    result = []
    for _, row in df.iterrows():
        clase = str(row.iloc[0])
        distribucion = {}
        for col in df.columns[1:]:
            try:
                distribucion[str(col)] = round(float(row[col]), 1)
            except (ValueError, TypeError):
                pass
        result.append({
            "class"       : clase,
            "distribution": distribucion,
        })

    return {
        "sample"      : sample,
        "variable"    : "SC001Q01TA — Community size/type",
        "unit"        : "Percentage within each latent class",
        "classes"     : result,
        "key_finding" : (
            "Lower-performing classes show higher concentrations in purely rural "
            "communities: Class 3 (58.8% rural) and Class 4 (54.3% rural), "
            "compared to Class 2 (37.5% rural). Within rural Peru, a gradient "
            "of rurality further differentiates academic performance profiles."
        ) if sample == "rural" else None,
    }


@router.get("/summary", summary="Full contextual summary for a sample")
def context_summary(
    sample: SampleType = Query("rural", description="Sample: 'national' or 'rural'"),
):
    """
    Returns a combined contextual summary including both school type and
    community type distributions across all latent classes.
    """
    df_school = load_csv(sample, "ctx_escuela").reset_index()
    df_comm   = load_csv(sample, "ctx_comunidad").reset_index()

    school_data = {}
    for _, row in df_school.iterrows():
        clase = str(row.iloc[0])
        school_data[clase] = {
            str(col): round(float(row[col]), 1)
            for col in df_school.columns[1:]
            if col != df_school.columns[0]
        }

    comm_data = {}
    for _, row in df_comm.iterrows():
        clase = str(row.iloc[0])
        comm_data[clase] = {
            str(col): round(float(row[col]), 1)
            for col in df_comm.columns[1:]
            if col != df_comm.columns[0]
        }

    return {
        "sample"        : sample,
        "school_type"   : school_data,
        "community_type": comm_data,
        "findings"      : {
            "school_type"   : (
                "93.5% of the highest-performing class attends private schools; "
                "all other classes are 100% public."
            ) if sample == "rural" else "Mixed distribution across classes.",
            "community_type": (
                "Lower-performing classes concentrate in purely rural communities "
                "(Classes 3 and 4: ~55-59% rural vs Class 2: 37.5% rural)."
            ) if sample == "rural" else "Urban concentration in higher-performing classes.",
        },
    }

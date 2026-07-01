"""
API — Latent Variable Identification for Academic Performance in Rural Peru
PISA 2022 | EFA + IRT + LCA
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import overview, efa, irt, lca, context

app = FastAPI(
    title="PISA 2022 Peru — Latent Variables API",
    description=(
        "API for querying results of latent variable analysis applied to PISA 2022 data. "
        "Includes Exploratory Factor Analysis (EFA), Item Response Theory (IRT), "
        "and Latent Class Analysis (LCA) for both the national and rural samples of Peru."
    ),
    version="1.0.0",
    contact={
        "name": "Research — Latent Variable Identification PISA 2022 Peru",
    },
    license_info={
        "name": "MIT",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Routers
app.include_router(overview.router,  prefix="/overview",  tags=["Overview"])
app.include_router(efa.router,       prefix="/efa",       tags=["EFA — Exploratory Factor Analysis"])
app.include_router(irt.router,       prefix="/irt",       tags=["IRT — Item Response Theory"])
app.include_router(lca.router,       prefix="/lca",       tags=["LCA — Latent Class Analysis"])
app.include_router(context.router,   prefix="/context",   tags=["Context — School & Community"])


@app.get("/", tags=["Root"])
def root():
    return {
        "title"      : "PISA 2022 Peru — Latent Variables API",
        "version"    : "1.0.0",
        "samples"    : ["national", "rural"],
        "docs"       : "/docs",
        "endpoints"  : {
            "overview" : "/overview",
            "efa"      : "/efa",
            "irt"      : "/irt",
            "lca"      : "/lca",
            "context"  : "/context",
        },
        "description": (
            "Query results of EFA + IRT + LCA analyses on PISA 2022 Peru data. "
            "Use ?sample=national or ?sample=rural on all endpoints."
        ),
    }

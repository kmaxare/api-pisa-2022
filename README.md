# PISA 2022 Peru — Latent Variables API

API for querying results of EFA + IRT + LCA analyses on PISA 2022 data.

## Project structure

```
api_pisa/
├── main.py              # FastAPI application
├── data_loader.py       # CSV reader utility
├── requirements.txt     # Dependencies
├── routers/
│   ├── overview.py      # /overview
│   ├── efa.py           # /efa
│   ├── irt.py           # /irt
│   ├── lca.py           # /lca
│   └── context.py       # /context
├── data/
│   ├── output/          # National sample CSVs
│   └── output_rural/    # Rural sample CSVs
```

## Required CSV files

Place these files in the correct folder:

**data/output/** (national sample):
- tabla_perfiles_clases.csv
- lca_resumen_ajuste.csv
- lca_rendimiento_por_clase.csv
- irt_parametros_retenidos.csv
- irt_parametros_todos.csv
- efa_cargas_factoriales.csv
- tabla_anova_factores.csv
- tabla_contexto_escuela.csv
- tabla_contexto_comunidad.csv

**data/output_rural/** (rural sample):
- Same files as above

## Run locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the API
uvicorn main:app --reload --port 8000

# 3. Open in browser
# API docs (Swagger): http://localhost:8000/docs
# API docs (ReDoc):   http://localhost:8000/redoc
# Root endpoint:      http://localhost:8000/
```

## Available endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Root — list of all endpoints |
| `GET /overview?sample=rural` | Research and pipeline summary |
| `GET /efa/factors?sample=rural` | All EFA factors with names |
| `GET /efa/factors/{factor_id}?sample=rural` | Top items for a factor |
| `GET /efa/blocks?sample=rural` | EFA results by block |
| `GET /irt/summary?sample=rural` | IRT calibration summary |
| `GET /irt/items?sample=rural` | Retained IRT items |
| `GET /irt/top-discriminating?sample=rural` | Top discriminating items |
| `GET /lca/model-selection?sample=rural` | BIC/AIC/Entropy by n classes |
| `GET /lca/classes?sample=rural` | All latent classes summary |
| `GET /lca/classes/{label}?sample=rural` | Detailed class profile |
| `GET /lca/discriminating-variables?sample=rural` | Top ANOVA-ranked variables |
| `GET /lca/profiles-heatmap?sample=rural` | Full z-score profile matrix |
| `GET /context/school-type?sample=rural` | School type by class |
| `GET /context/community-type?sample=rural` | Community type by class |
| `GET /context/summary?sample=rural` | Combined context summary |

All endpoints accept `?sample=national` or `?sample=rural`.

## Deploy to a server (basic — VPS/cloud)

```bash
# On your server (Ubuntu):
# 1. Install Python and pip
sudo apt update && sudo apt install python3-pip -y

# 2. Upload your project folder to the server
# (use scp, FileZilla, or git)

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run with uvicorn on port 80 (or any open port)
uvicorn main:app --host 0.0.0.0 --port 8000

# 5. To keep it running after closing terminal:
nohup uvicorn main:app --host 0.0.0.0 --port 8000 &
```

Note: For production deployment with SSL and domain, additional configuration
is needed (nginx + certbot). Ask for help when you reach this step.

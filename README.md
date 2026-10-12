# Enterprise Data Mesh Architecture

A **local, full-stack data mesh demonstration** with domain-owned data products, contracts, quality controls, a product catalog, FastAPI, Streamlit, Docker, pytest, GitHub Actions, optional open-weight AI review and an Azure cloud blueprint.

> **Status:** Prototype committed to GitHub. No cloud services have been provisioned and local Docker/CI execution has not yet been independently verified. Real enterprise mesh governance and authentication remain future work.

## Architecture

```text
Open CC0 sales data ------> Sales domain Bronze -> Silver -> Gold data product
Open CC0 inventory data --> Inventory domain Bronze -> Silver -> Gold data product
                           |                              |
                    Domain contracts                Product catalog
                          +------------+-----------------+
                                       |
                          FastAPI /api/products
                                       |
                           Streamlit catalog UI
                                       |
                          Optional Ollama AI review
```

## Included public data

The repo includes **original fictional CC0 datasets**, [sales.csv](data/public/sales.csv) (8 orders) and [inventory.csv](data/public/inventory.csv) (6 SKUs), with [provenance and licensing](data/public/README.md). They are synthetic fixtures, not real business operations or external production benchmarks.

## Run on Windows PowerShell

```powershell
git clone https://github.com/Khadija162/Enterprise-Data-Mesh-Architecture.git
cd Enterprise-Data-Mesh-Architecture
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m mesh.pipeline
.\.venv\Scripts\python.exe -m pytest -q
```

The pipeline generates per-domain Bronze, Silver and Gold Parquet files and `artifacts/catalog.json`.

Run backend and frontend separately:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload
.\.venv\Scripts\python.exe -m streamlit run frontend/app.py
```

Or, after running the pipeline once, start Docker:

```powershell
docker compose up --build
```

API documentation: http://localhost:8000/docs
Frontend: http://localhost:8501

## Domain data products

- **Sales**: independent `sales-data-team` ownership, source contract, duplicate-key/range checks, and Gold totals grouped by order status.
- **Inventory**: independent `inventory-data-team` ownership, source contract, stock/reorder validity checks, and Gold restock counts by warehouse.
- **Catalog**: JSON data product metadata, owner, schema, quality status, row counts, source provenance and generated artifact location.
- **AI reviewer**: optional read-only incident commentary; no automatic changes to products or policy.

## Enable an open-weight model locally

Default `LLM_MODE=mock` works without an API key or GPU. To enable a local Ollama model:

```powershell
ollama pull qwen2.5:3b
$env:LLM_MODE="ollama"
$env:OLLAMA_MODEL="qwen2.5:3b"
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload
```

This applies to the host-side FastAPI server, not the default Docker Compose environment.

## Azure cloud plan

Production target: domain ingestion with Azure Data Factory/Event Hubs, segregated ADLS Gen2 storage, Databricks Delta Lake domain products, Microsoft Purview data catalog and governance, Microsoft Entra ID permissions, Azure Container Apps frontend/backend, Azure Monitor, and Key Vault. `infra/terraform/` currently defines **only a resource group and ADLS Gen2 filesystem**, with no resources deployed or billed by this change.

This is **not a fully governed enterprise mesh**: it lacks authenticated self-service provisioning, lineage, domain-level access policies, SLA monitoring, versioned contracts, and platform isolation. Review [architecture and roadmap](docs/architecture.md).

## Testing and deployment status

GitHub files are committed, but tests, CI status, Docker startup and cloud provisioning have not been independently confirmed. This API has no authentication; do not expose it to the public internet as-is.

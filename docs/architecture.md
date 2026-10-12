# Data Mesh architecture and implementation boundaries

Implemented locally: two domain-owned data products (sales and inventory), independent contracts and owners, Bronze/Silver/Gold Parquet layers per domain, rejected-row quarantine, JSON product catalog, FastAPI catalog API, Streamlit product discovery frontend, mock or Ollama read-only quality reviewer, Docker and GitHub Actions tests.

Cloud blueprint (not deployed): Azure Data Factory / Event Hubs domain ingestion -> ADLS Gen2 isolated domain zones -> Azure Databricks and Delta Lake -> Microsoft Purview catalog, federated access policies and Entra ID governance -> Azure Container Apps catalog and dashboard -> Azure Monitor + Key Vault. Terraform only describes one resource group and shared ADLS storage starter; it does not yet enforce production domain isolation or Purview policies.

Data mesh principles: domain ownership, data as a product, self-service infrastructure, federated computational governance. The demo illustrates domain ownership and product metadata but is not a complete organizational mesh. Add domain-specific ACLs, product SLAs, lineage, ownership approval and contract versioning for real enterprise use.

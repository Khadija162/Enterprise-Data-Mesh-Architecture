"""Local read-only data product catalog API; requires authentication before public hosting."""
import json
import os
from pathlib import Path
import requests
from fastapi import FastAPI, HTTPException
from mesh.ai import explain

app = FastAPI(title="Enterprise Data Mesh Catalog", version="0.1.0")

def catalog():
    file = Path(os.getenv("CATALOG_PATH", "artifacts/catalog.json"))
    return json.loads(file.read_text(encoding="utf-8")) if file.is_file() else None

@app.get("/health")
def health():
    return {"status": "ok", "catalog_ready": catalog() is not None}

@app.get("/api/products")
def products():
    data = catalog()
    return {"products": data["products"] if data else []}

@app.get("/api/products/{domain}")
def domain_product(domain: str):
    data = catalog()
    item = next((p for p in (data["products"] if data else []) if p["domain"] == domain), None)
    if item is None:
        raise HTTPException(404, "Unknown domain")
    return item

@app.post("/api/ai/review")
def review():
    data = catalog()
    if not data:
        raise HTTPException(404, "Generate the catalog first")
    try:
        return explain(data)
    except (requests.RequestException, ValueError, KeyError) as exc:
        raise HTTPException(502, "AI inference unavailable") from exc

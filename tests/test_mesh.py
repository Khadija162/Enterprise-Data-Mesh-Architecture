import pandas as pd
from fastapi.testclient import TestClient
from backend.main import app
from mesh.pipeline import build
from mesh.ai import explain

def make_data(path):
    path.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([{"order_id": 1, "customer_id": "C1", "amount": 10, "status": "paid"},
                  {"order_id": 2, "customer_id": "C2", "amount": -1, "status": "paid"}]).to_csv(path/"sales.csv", index=False)
    pd.DataFrame([{"sku": "A", "warehouse": "W1", "stock_units": 4, "reorder_point": 10}]).to_csv(path/"inventory.csv", index=False)

def test_domain_contracts(tmp_path):
    source = tmp_path/"input"
    make_data(source)
    data = build(str(source), str(tmp_path/"lake"), str(tmp_path/"catalog.json"))
    assert len(data["products"]) == 2
    assert data["products"][0]["rejected_rows"] == 1
    assert data["products"][1]["valid_rows"] == 1

def test_catalog_api(tmp_path, monkeypatch):
    make_data(tmp_path/"input")
    path = tmp_path/"catalog.json"
    build(str(tmp_path/"input"), str(tmp_path/"lake"), str(path))
    monkeypatch.setenv("CATALOG_PATH", str(path))
    client = TestClient(app)
    assert len(client.get("/api/products").json()["products"]) == 2
    assert client.get("/api/products/sales").status_code == 200
    assert client.get("/api/products/unknown").status_code == 404

def test_mock_ai(monkeypatch):
    monkeypatch.setenv("LLM_MODE", "mock")
    assert explain({"products":[{"domain":"sales","raw_rows":2,"valid_rows":1,"rejected_rows":1,"quality_status":"review"}]})["requires_human_review"]

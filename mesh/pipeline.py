"""Contract-driven multi-domain data products, local Parquet layers, catalog provenance."""
import json
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd

CONTRACTS = {
    "sales": {"required": ["order_id", "customer_id", "amount", "status"], "id": "order_id", "numeric": "amount"},
    "inventory": {"required": ["sku", "warehouse", "stock_units", "reorder_point"], "id": "sku", "numeric": "stock_units"},
}

def build(source="data/public", output="data", catalog_path="artifacts/catalog.json"):
    root = Path(output)
    catalog = {"generated_at": datetime.now(timezone.utc).isoformat(), "products": []}
    for domain, contract in CONTRACTS.items():
        input_file = Path(source) / f"{domain}.csv"
        frame = pd.read_csv(input_file)
        missing = set(contract["required"]) - set(frame.columns)
        if missing:
            raise ValueError(f"{domain} missing contract fields: {sorted(missing)}")
        for layer in ("bronze", "silver", "gold"):
            (root / layer / domain).mkdir(parents=True, exist_ok=True)
        frame.to_parquet(root / "bronze" / domain / "records.parquet", index=False)
        valid = frame[contract["id"]].notna()
        valid &= pd.to_numeric(frame[contract["numeric"]], errors="coerce").ge(0)
        valid &= ~frame[contract["id"]].duplicated(keep="first")
        if domain == "sales":
            valid &= frame["status"].isin(["placed", "paid", "shipped", "cancelled"])
            valid &= frame["customer_id"].notna()
        else:
            valid &= pd.to_numeric(frame["reorder_point"], errors="coerce").ge(0)
            valid &= frame["warehouse"].notna()
        clean = frame.loc[valid].copy()
        clean.to_parquet(root / "silver" / domain / "records.parquet", index=False)
        frame.loc[~valid].to_parquet(root / "silver" / domain / "rejected.parquet", index=False)
        if domain == "sales":
            clean["amount"] = pd.to_numeric(clean["amount"])
            gold = clean.groupby("status", as_index=False).agg(records=("order_id", "size"), total_amount=("amount", "sum"))
        else:
            clean["stock_units"] = pd.to_numeric(clean["stock_units"])
            clean["reorder_point"] = pd.to_numeric(clean["reorder_point"])
            clean["needs_restock"] = clean["stock_units"] < clean["reorder_point"]
            gold = clean.groupby("warehouse", as_index=False).agg(skus=("sku", "size"), restock_skus=("needs_restock", "sum"))
        gold.to_parquet(root / "gold" / domain / "summary.parquet", index=False)
        catalog["products"].append({
            "domain": domain, "owner": f"{domain}-data-team",
            "product": f"{domain}-summary-v1", "schema": contract["required"],
            "source": str(input_file), "license": "CC0 (original synthetic example)",
            "raw_rows": int(len(frame)), "valid_rows": int(len(clean)),
            "rejected_rows": int((~valid).sum()),
            "quality_status": "pass" if valid.all() else "review",
            "gold_path": str(root / "gold" / domain / "summary.parquet")
        })
    target = Path(catalog_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(catalog, indent=2), encoding="utf-8")
    return catalog

if __name__ == "__main__":
    print(json.dumps(build(), indent=2))

"""Streamlit data mesh product catalog."""
import os
import requests
import pandas as pd
import streamlit as st
st.set_page_config(page_title="Data Mesh Catalog", layout="wide")
st.title("Enterprise Data Mesh · Product Catalog")
st.caption("Domain-owned products · Contracts · Quality · AI review")
api = os.getenv("API_URL", "http://localhost:8000")
try:
    response = requests.get(api + "/api/products", timeout=8)
    response.raise_for_status()
    records = response.json()["products"]
except (requests.RequestException, KeyError):
    records = []
if records:
    a, b, c = st.columns(3)
    a.metric("Data products", len(records))
    b.metric("Healthy products", sum(p["quality_status"] == "pass" for p in records))
    c.metric("Rejected source records", sum(p["rejected_rows"] for p in records))
    frame = pd.DataFrame(records)
    st.dataframe(frame[["domain","product","owner","raw_rows","valid_rows","rejected_rows","quality_status"]], use_container_width=True)
    selected = st.selectbox("Inspect domain", [p["domain"] for p in records])
    st.json(next(p for p in records if p["domain"] == selected))
    if st.button("AI: review mesh quality"):
        try:
            result = requests.post(api + "/api/ai/review", timeout=100)
            result.raise_for_status()
            st.json(result.json())
        except requests.RequestException as exc:
            st.error(str(exc))
else:
    st.info("Run python -m mesh.pipeline first to generate the catalog.")

import streamlit as st

st.set_page_config(page_title="Ecommerce Dashboard", layout="wide")
st.title("Ecommerce Operations Dashboard")
st.caption("Draft analytics surface with marketplace and SKU segmentation")

metrics = [
    "gross_margin", "net_margin", "sell_through", "aging_days",
    "return_rate", "shipping_fee_ratio", "conversion_rate", "cac"
]

seg = st.multiselect("Segmentation", ["marketplace", "sku"], default=["marketplace", "sku"])
st.write("Active segmentation:", seg)
for m in metrics:
    st.metric(label=m, value="pending")

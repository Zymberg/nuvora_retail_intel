from PIL import Image
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ----------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------
logo = Image.open("1.png")

st.set_page_config(
    page_title="Nuvora | Sales Opportunity Board",
    layout="wide",
    page_icon=logo  # pass the image object directly, not as a string
)

NAVY_BG = "#0b132b"
NAVY_PANEL = "#1c2541"
TEXT_MAIN = "#e5e8ef"
TEXT_MUTED = "#9aa5b1"
ACC_TEAL = "#3a86ff"
ACC_AMBER = "#fb8500"
ACC_GREEN = "#06d6a0"
ACC_CORAL = "#ff6b6b"
BORDER = "#24304b"

# ======================================================
# CSS
# ======================================================
st.markdown(f"""
<style>
  html, body, [class*="css"] {{
    background-color: {NAVY_BG};
    color: {TEXT_MAIN};
    font-family: "Inter","Segoe UI",system-ui,-apple-system,sans-serif;
  }}
  [data-testid="stSidebar"] {{
    background-color: {NAVY_PANEL};
    border-right: 1px solid {BORDER};
  }}
  .metric-card {{
    background: {NAVY_PANEL};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 12px 16px;
    text-align: center;
  }}
  .metric-title {{ color:{TEXT_MUTED}; font-size:13px; }}
  .metric-value {{ font-size:28px; font-weight:800; margin-top:2px; }}
  .section-title {{ font-size:18px; font-weight:700; color:{NAVY_BG}; margin-bottom:10px; }}
  .panel {{ background:{NAVY_PANEL}; border:1px solid {BORDER}; border-radius:10px; padding:16px; }}
  .watermark {{ position:fixed; right:16px; bottom:8px; color:{TEXT_MUTED}; opacity:.45; font-size:12px; }}
</style>
""", unsafe_allow_html=True)

# ======================================================
# HEADER
# ======================================================
st.markdown(f"""
<div style='background:{NAVY_PANEL};border-radius:10px;padding:10px 20px;margin-bottom:12px;'>
  <h2 style='color:{ACC_AMBER};margin:0;'>Nuvora | Sales Opportunity Board</h2>
</div>
""", unsafe_allow_html=True)

# ======================================================
# DEMO DATA (More realistic)
# ======================================================


@st.cache_data
def build_demo_data(seed=42):
    rng = np.random.default_rng(seed)
    stores = [f"Outlet_{i}" for i in range(1, 26)]
    regions = ["East", "Central", "West"]
    products = ["LumaBoost", "ZenPro", "NaturaBite",
                "HydraEdge", "CoreFuel", "VitaBlend"]
    months = pd.date_range("2024-01-01", "2024-12-01", freq="MS")

    # Product performance bias (some underperform intentionally)
    product_bias = {
        "LumaBoost": 1.05,   # strong performer
        "ZenPro": 0.95,      # slightly below target
        "NaturaBite": 0.85,  # underperformer
        "HydraEdge": 1.00,   # on target
        "CoreFuel": 0.90,    # below target
        "VitaBlend": 0.80    # weakest
    }

    data = []
    for s in stores:
        region = rng.choice(regions, p=[0.4, 0.3, 0.3])
        base_multiplier = rng.normal(1.0, 0.2)  # store-level bias

        for p in products:
            product_base = {"LumaBoost": 420, "ZenPro": 380, "NaturaBite": 310,
                            "HydraEdge": 350, "CoreFuel": 270, "VitaBlend": 230}[p]

            for m in months:
                month_num = m.month

                # Seasonality
                seasonal_factor = 1.0
                if p == "LumaBoost" and month_num in [5, 6, 7, 8]:
                    seasonal_factor = 1.15
                elif p == "CoreFuel" and month_num in [11, 12, 1]:
                    seasonal_factor = 1.2
                elif month_num in [11, 12]:
                    seasonal_factor = 1.1  # general holiday uplift

                # Region effect
                region_factor = {"East": 1.1,
                                 "Central": 0.95, "West": 1.0}[region]

                # Promotion spikes (~10% random months)
                promo_boost = 1.0
                if rng.random() < 0.1:
                    promo_boost = rng.uniform(1.2, 1.4)

                # Shelf ratio (slightly correlated to performance)
                shelf_ratio = np.clip(rng.normal(0.9, 0.15), 0.4, 1.3)

                # Actual sales — includes product_bias (key change)
                sales = product_base * base_multiplier * seasonal_factor * \
                    region_factor * promo_boost * \
                    product_bias[p] * rng.uniform(0.8, 1.2)

                data.append([s, region, p, m, max(0, sales), shelf_ratio])

    df = pd.DataFrame(data, columns=[
                      "Store", "Region", "Product", "Month", "Actual_Sales", "Shelf_Ratio"])

    targets = pd.DataFrame({
        "Product": products,
        "Target_Sales": [400, 360, 300, 340, 280, 240],
        "Target_Shelf": [1.0, 1.0, 1.0, 0.9, 0.9, 0.8]
    })
    df = df.merge(targets, on="Product", how="left")

    # Grading logic
    df["Sales_Grade"] = pd.cut(df["Actual_Sales"]/df["Target_Sales"],
                               bins=[0, 0.6, 0.8, 1.0, 1.3, np.inf],
                               labels=["E", "D", "C", "B", "A"])
    df["Shelf_Grade"] = pd.cut(df["Shelf_Ratio"]/df["Target_Shelf"],
                               bins=[0, 0.7, 0.9, 1.0, 1.1, np.inf],
                               labels=["E", "D", "C", "B", "A"])
    return df

df = build_demo_data()

# ======================================================
# SIDEBAR
# ======================================================

with st.sidebar:
    st.markdown(
        f"<h3 style='color:#ffffff;margin-top:0;'>Filters</h3>",
        unsafe_allow_html=True
    )
    selected_month = st.selectbox(
        "Month", sorted(df["Month"].unique()), index=11,
        label_visibility="visible"
    )
    selected_region = st.selectbox(
        "Region", ["All"] + sorted(df["Region"].unique())
    )
    selected_product = st.selectbox(
        "Product", ["All"] + sorted(df["Product"].unique())
    )
    st.markdown(
        "<p style='color:#ffffff; font-size:12px;'>© 2025 Nuvora Analytics</p>",
        unsafe_allow_html=True
    )
st.markdown("""
<style>
label, div[data-testid="stMarkdownContainer"] p {
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)


df_view = df[df["Month"] == selected_month].copy()
if selected_region != "All":
    df_view = df_view[df_view["Region"] == selected_region]
if selected_product != "All":
    df_view = df_view[df_view["Product"] == selected_product]

# ======================================================
# KPI SECTION
# ======================================================
avg_sales = df_view["Actual_Sales"].mean()
avg_goal = df_view["Target_Sales"].mean()
avg_perf = avg_sales / avg_goal if avg_goal > 0 else 0
shelf_alignment = (df_view["Sales_Grade"] ==
                   df_view["Shelf_Grade"]).mean() * 100

perf_color = ACC_GREEN if avg_perf >= 1 else ACC_AMBER if avg_perf >= 0.85 else ACC_CORAL
align_color = ACC_GREEN if shelf_alignment >= 85 else ACC_AMBER if shelf_alignment >= 70 else ACC_CORAL

k1, k2, k3 = st.columns(3)
k1.markdown(
    f"<div class='metric-card'><div class='metric-title'>Average Sales</div><div class='metric-value' style='color:{ACC_TEAL};'>${avg_sales:,.0f}</div></div>", unsafe_allow_html=True)
k2.markdown(
    f"<div class='metric-card'><div class='metric-title'>Goal Achievement</div><div class='metric-value' style='color:{perf_color};'>{avg_perf*100:.1f}%</div></div>", unsafe_allow_html=True)
k3.markdown(
    f"<div class='metric-card'><div class='metric-title'>Shelf Alignment</div><div class='metric-value' style='color:{align_color};'>{shelf_alignment:.1f}%</div></div>", unsafe_allow_html=True)
st.markdown("<hr style='border:1px solid #24304b;opacity:.3;'>",
            unsafe_allow_html=True)

# ======================================================
# SALES PERFORMANCE
# ======================================================
col1, col2 = st.columns([0.6, 0.4], gap="large")

with col1:
    st.markdown("<div class='section-title'>Product Sales vs Goal</div>",
                unsafe_allow_html=True)
    cat_perf = df_view.groupby("Product", as_index=False).agg(
        {"Actual_Sales": "mean", "Target_Sales": "mean"})
    cat_perf["Gap_to_Target"] = cat_perf["Target_Sales"] - \
        cat_perf["Actual_Sales"]
    cat_perf["Goal_%"] = (cat_perf["Actual_Sales"] /
                          cat_perf["Target_Sales"])*100
    fig1 = px.bar(cat_perf, x="Product", y="Goal_%", color="Gap_to_Target",
                  color_continuous_scale=["#06d6a0", "#fb8500", "#ff6b6b"],
                  text=cat_perf["Goal_%"].round(1).astype(str)+"%")
    fig1.update_layout(template="plotly_dark", paper_bgcolor=NAVY_PANEL,
                       plot_bgcolor=NAVY_PANEL, font_color=TEXT_MAIN, height=420,
                       yaxis_title="Goal Achievement (%)", xaxis_title=None)
    fig1.update_traces(textposition="outside")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown("<div class='section-title'>Regional Sales vs Goal</div>",
                unsafe_allow_html=True)
    reg_perf = df_view.groupby("Region", as_index=False).agg(
        {"Actual_Sales": "mean", "Target_Sales": "mean"})
    reg_perf["Goal_%"] = (reg_perf["Actual_Sales"] /
                          reg_perf["Target_Sales"])*100
    fig2 = px.bar(reg_perf, x="Region", y="Goal_%", text_auto=True,
                  color="Goal_%", color_continuous_scale="Bluered")
    fig2.update_layout(template="plotly_dark", paper_bgcolor=NAVY_PANEL,
                       font_color=TEXT_MAIN, height=420, yaxis_title="Goal Achievement (%)")
    st.plotly_chart(fig2, use_container_width=True)

# ======================================================
# ALIGNMENT INSIGHT
# ======================================================
st.markdown("<div class='section-title'>Sales vs Shelf Alignment</div>",
            unsafe_allow_html=True)
alignment = df_view.groupby(
    ["Sales_Grade", "Shelf_Grade"]).size().reset_index(name="Count")
fig3 = px.density_heatmap(alignment, x="Shelf_Grade", y="Sales_Grade", z="Count",
                          color_continuous_scale="YlOrBr", text_auto=True)
fig3.update_layout(template="plotly_dark", paper_bgcolor=NAVY_PANEL,
                   plot_bgcolor=NAVY_PANEL, font_color=TEXT_MAIN,
                   height=420, margin=dict(l=10, r=10, t=30, b=10))
st.plotly_chart(fig3, use_container_width=True)

# Alignment Summary
grade_map = {"A": 5, "B": 4, "C": 3, "D": 2, "E": 1}
df_corr = df_view.replace({"Sales_Grade": grade_map, "Shelf_Grade": grade_map})
corr = df_corr["Sales_Grade"].corr(
    df_corr["Shelf_Grade"]) if len(df_corr) > 0 else 0
corr_strength = "Strong" if corr > 0.7 else "Moderate" if corr > 0.4 else "Weak"
st.markdown(
    f"**Alignment Strength:** <span style='color:{ACC_AMBER};font-weight:600;'>{corr_strength} ({corr:.2f})</span>", unsafe_allow_html=True)

# ======================================================
# TOP OPPORTUNITIES
# ======================================================
st.markdown("<div class='section-title'>Top 10 Opportunity Stores</div>",
            unsafe_allow_html=True)
df_view["Gap_to_Goal"] = df_view["Target_Sales"] - df_view["Actual_Sales"]
df_view["Action"] = np.where(df_view["Shelf_Grade"].isin(["D", "E"]),
                             "Check shelf setup & restock",
                             np.where(df_view["Sales_Grade"].isin(["D", "E"]),
                                      "Sales push / promo opportunity",
                                      "Maintain performance"))
top_opps = df_view.sort_values("Gap_to_Goal", ascending=False).head(10)
styled = top_opps[["Store", "Region", "Product", "Actual_Sales", "Target_Sales",
                   "Sales_Grade", "Shelf_Grade", "Gap_to_Goal", "Action"]].style.format(
                       {"Actual_Sales": "${:,.0f}", "Target_Sales": "${:,.0f}", "Gap_to_Goal": "${:,.0f}"})
st.dataframe(styled, use_container_width=True, height=420)

# ======================================================
# FOOTER
# ======================================================
st.markdown(
    f"<div class='watermark'>Nuvora | Sales Intelligence • {datetime.now().year}</div>", unsafe_allow_html=True)

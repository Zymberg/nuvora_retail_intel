from PIL import Image
import time
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from PIL import Image
import streamlit as st

# ======================================================
# CONFIGURATION
# ======================================================
FILE_PATH = "retail_sales_demo.csv"

SALES_COL = "ECC_SALES_USD"

logo = Image.open("1.png")

st.set_page_config(
    page_title="Nuvora | Retail Intelligence",
    layout="wide",
    page_icon=logo
)
# ======================================================
# THEME — EXECUTIVE NAVY++ (Solid Corporate)
# ======================================================
NAVY_BG     = "#0b132b"  # app background
NAVY_PANEL  = "#1c2541"  # panels/cards/tables
TEXT_MAIN   = "#e5e8ef"
TEXT_MUTED  = "#9aa5b1"
LABEL_LIGHT = "#dce4f2"  # sidebar labels
ACC_TEAL    = "#3a86ff"
ACC_AMBER   = "#ffb703"
ACC_GREEN   = "#06d6a0"
ACC_CORAL = "#d04b04"
BORDER      = "#24304b"

st.markdown(f"""
<style>
  html, body, [class*="css"] {{
    background: {NAVY_BG};
    color: {TEXT_MAIN};
    font-family: "Inter","Segoe UI",system-ui,-apple-system,sans-serif;
  }}

  /* Persistent top header aligned with content */
    .brand-header {{
    position: sticky;
    top: 0;
    z-index: 999;
    background: {NAVY_PANEL};
    border-bottom: 1px solid {BORDER};
    padding: 10px 18px;
    margin: 0 auto 12px auto;   /* centers header */
    width: 100%;                 /* adjust width (90–95%) */
    border-radius: 10px;        /* optional: rounded corners */
    }}
    .brand-title {{
      font-weight: 800;
      font-size: 20px;
      letter-spacing: 0.3px;
      color: #ff9500; /* single orange tone */
    }}
  .brand-sub {{
    color: {TEXT_MUTED}; font-size: 12px; margin-top: 2px;
  }}

  /* Sidebar — readable labels, refresh spinner */
  [data-testid="stSidebar"] {{
    background: {NAVY_PANEL};
    border-right: 1px solid {BORDER};
  }}
  [data-testid="stSidebar"] h1, 
  [data-testid="stSidebar"] h2, 
  [data-testid="stSidebar"] h3, 
  [data-testid="stSidebar"] label {{
    color: {LABEL_LIGHT} !important;
  }}
  .filters-row {{
    display: flex; align-items: center; gap: 8px; margin-bottom: 6px;
  }}
  .spinner {{
    width: 14px; height: 14px; border: 2px solid {ACC_TEAL}55; border-top-color: {ACC_TEAL};
    border-radius: 50%; animation: spin .8s linear 1;
  }}
  @keyframes spin {{ to {{ transform: rotate(360deg); }} }}

  /* Panels / metrics / tables — solid, consistent borders */
  .panel, .metric-card {{
    background: {NAVY_PANEL};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 14px;
  }}
  .metric-title {{
    color: {TEXT_MUTED}; font-size: 13px; margin-bottom: 6px;
  }}
  .metric-value {{
    font-size: 28px; font-weight: 800; color: {ACC_TEAL};
  }}
  .section-title {{
    font-size: 18px; font-weight: 700; color: {ACC_AMBER}; margin: 2px 0 0px 0; /* added gap below titles */
    text-align: left;
  }}
  .section-title.center {{
    text-align: center; display: flex; align-items: center; justify-content: center; min-height: 28px;
  }}
  .small-muted {{ color: {TEXT_MUTED}; font-size: 12px; }}
  .divider {{ border-top: 1px solid {BORDER}; margin: 8px 0 10px; }}

  /* Animations */
  .fade-in {{ animation: fadeIn .6s ease-out both; }}
  .slide-up {{ animation: slideUp .6s ease-out both; }}
  @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
  @keyframes slideUp {{ from {{ transform: translateY(10px); opacity: 0; }} to {{ transform: translateY(0); opacity: 1; }} }}

  /* Dataframe theme — solid (no stripes) */
  div[data-testid="stDataFrame"] > div > div > div > div {{
    background: {NAVY_PANEL} !important;
    color: {TEXT_MAIN} !important;
    border-radius: 10px;
    border: 1px solid {BORDER};
  }}
  thead tr th {{
    background: {NAVY_PANEL} !important;
    color: {TEXT_MAIN} !important;
    border-bottom: 1px solid {BORDER} !important;
  }}
  tbody tr td {{
    border-bottom: 1px solid {BORDER} !important;
  }}
  tbody tr:hover td {{
    background: #223055 !important;
  }}

  /* Plotly containers */
  .plotly-container {{
    background: {NAVY_PANEL};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 12px;
  }}

  /* Next Steps cards */
  .steps-grid {{
    display: grid; grid-template-columns: 1fr; gap: 10px;
  }}
  .step-card {{
    background: {NAVY_PANEL};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 10px 12px;
    display: flex; align-items: center; gap: 10px;
    transition: transform .15s ease, border-color .15s ease;
  }}
  .step-card:hover {{
    transform: translateY(-1px);
    border-color: {ACC_TEAL};
  }}
  .step-icon {{
    color: {ACC_TEAL}; font-size: 16px; line-height: 1;
  }}
  .step-text {{
    color: {TEXT_MAIN}; font-size: 14px;
  }}

  /* Footer watermark */
  .watermark {{
    position: fixed; right: 14px; bottom: 8px;
    color: {TEXT_MUTED}; opacity: .45; font-size: 12px;
    pointer-events: none;
  }}
</style>
""", unsafe_allow_html=True)

# ======================================================
# PERSISTENT HEADER
# ======================================================
st.markdown(f"""
<style>
.brand-header {{
    text-align: center;
    margin-top: 10px;
    margin-bottom: 15px;
    line-height: 1.4;
}}

.brand-title {{
    font-weight: 800;
    font-size: 24px;
    letter-spacing: 0.6px;
    color: #ff9500; /* solid orange */
    display: inline-block;
}}
</style>

<div class="brand-header fade-in">
  <div class="brand-title">nuvora&nbsp;|&nbsp;Retail&nbsp;Intelligence</div>
</div>
""", unsafe_allow_html=True)



# ======================================================
# LOAD DATA
# ======================================================
@st.cache_data
def load_sales_data(path: str, sales_col: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["INVOICE_MONTH"])
    # Retail-safe renames (distinct from original project)
    rename_map = {
        "SHIP_TO_ACCOUNT_NUMBER": "OUTLET_ID",
        "SHIP_TO_ACCOUNT_NAME": "OUTLET_NAME",
        "DISEASE_CATEGORY": "CATEGORY_SEGMENT",
        "SHIP_TO_SALES_TERRITORY": "REGION_ID",
        "SHIP_TO_SALES_TERRITORY_DESCRIPTION": "REGION_NAME"
    }
    df = df.rename(columns=rename_map)
    df["Month"] = df["INVOICE_MONTH"].dt.month
    df["Year"]  = df["INVOICE_MONTH"].dt.year
    df["NET_SALES"] = pd.to_numeric(df[sales_col], errors="coerce").fillna(0.0)
    df["CATEGORY_SEGMENT"] = df["CATEGORY_SEGMENT"].fillna("Unspecified")
    df["OUTLET_NAME"] = df["OUTLET_NAME"].fillna(df["OUTLET_ID"].astype(str))
    return df

df = load_sales_data(FILE_PATH, SALES_COL)

# ======================================================
# SIDEBAR FILTERS (with spinner)
# ======================================================
with st.sidebar:
    st.markdown('<div class="filters-row"><h3 style="margin:0;">Filters</h3><div class="spinner"></div></div>', unsafe_allow_html=True)
    min_year, max_year = int(df["Year"].min()), int(df["Year"].max())
    year = st.selectbox("Analysis Year", list(range(max_year, min_year - 1, -1)), index=0)
    months_in_year = sorted(df.loc[df["Year"] == year, "Month"].unique())
    end_month = st.slider("YTD through month", min_value=min(months_in_year),
                          max_value=max(months_in_year), value=max(months_in_year))
    regions = ["All Regions"] + sorted(df["REGION_NAME"].unique())
    selected_region = st.selectbox("Region", regions)
    segments = ["All Segments"] + sorted(df["CATEGORY_SEGMENT"].unique())
    selected_segment = st.selectbox("Category Segment", segments)
    min_potential = st.slider("Minimum Opportunity ($)", 0, 50000, 0, step=1000)
    st.markdown(
    f"""
    <hr style="border:1px solid {BORDER}; margin-top:12px; margin-bottom:8px; opacity:0.3;">
    <div style='text-align:center; color:{LABEL_LIGHT}; font-size:12px; opacity:0.7;'>
        © 2025 <span style='color:{ACC_TEAL}; font-weight:600;'>Nuvora</span> Analytics
    </div>
    """,
    unsafe_allow_html=True
    )

# ======================================================
# HELPERS
# ======================================================
def month_end(ts: pd.Timestamp) -> pd.Timestamp:
    return pd.Timestamp(year=ts.year, month=ts.month, day=1) + pd.offsets.MonthEnd(0)

def cash(x):
    if pd.isna(x): return "-"
    if x >= 1_000_000: return f"${x/1_000_000:.1f}M"
    if x >= 1_000:     return f"${x/1_000:.0f}K"
    return f"${x:,.0f}"

def animate_metric(container, title, value, color=ACC_TEAL, duration=0.8):
    """Count-up animation for KPIs (supports $, % or raw)."""
    import re
    raw = str(value)
    nums = re.findall(r"[-]?\d+\.?\d*", raw.replace(",", ""))
    if not nums:
        with container:
            st.markdown(f"<div class='metric-card fade-in'><div class='metric-title'>{title}</div><div class='metric-value' style='color:{color};'>{value}</div></div>", unsafe_allow_html=True)
        return
    try:
        target = float(nums[0])
    except:
        target = 0.0
    steps = 30
    sleep = max(0.01, duration/steps)
    ph = container.empty()
    for i in range(steps+1):
        t = i/steps
        eased = 1 - (1-t)**3  # ease-out cubic
        v = target * eased
        if "$" in raw:   disp = f"${v:,.0f}"
        elif "%" in raw: disp = f"{v:+.1f}%"
        else:            disp = f"{v:,.0f}"
        ph.markdown(f"<div class='metric-card fade-in'><div class='metric-title'>{title}</div><div class='metric-value' style='color:{color};'>{disp}</div></div>", unsafe_allow_html=True)
        time.sleep(sleep)
    ph.markdown(f"<div class='metric-card'><div class='metric-title'>{title}</div><div class='metric-value' style='color:{color};'>{value}</div></div>", unsafe_allow_html=True)

# ======================================================
# DERIVE YTD METRICS
# ======================================================
cy_mask = (df["Year"] == year) & (df["Month"] <= end_month)
ly_mask = (df["Year"] == year-1) & (df["Month"] <= end_month)
df_cy, df_ly = df.loc[cy_mask].copy(), df.loc[ly_mask].copy()

# Days since last CY purchase
period_end = pd.Timestamp(year=year, month=end_month, day=1) + pd.offsets.MonthEnd(0)
purchases = df_cy.loc[df_cy["NET_SALES"]>0, ["OUTLET_ID","INVOICE_MONTH"]] \
                 .assign(ME=lambda x: x["INVOICE_MONTH"].map(month_end)).drop_duplicates()
last_me = purchases.groupby("OUTLET_ID")["ME"].max()
last_buy = last_me.to_frame().assign(Days_No_Purchase=(period_end - last_me).dt.days)

# Sales + peer benchmarks + opportunity
cy_sales = df_cy.groupby("OUTLET_ID")["NET_SALES"].sum().rename("CY_Sales")
ly_sales = df_ly.groupby("OUTLET_ID")["NET_SALES"].sum().rename("LY_Sales")
meta = df[["OUTLET_ID","OUTLET_NAME","REGION_NAME"]].drop_duplicates("OUTLET_ID")
stores = meta.merge(cy_sales, on="OUTLET_ID", how="left") \
             .merge(ly_sales, on="OUTLET_ID", how="left") \
             .merge(last_buy, on="OUTLET_ID", how="left") \
             .fillna({"CY_Sales":0.0, "LY_Sales":0.0, "Days_No_Purchase":(end_month-1)*30.4375})

region_avg = stores.groupby("REGION_NAME")["CY_Sales"].mean().rename("Region_Avg")
stores = stores.merge(region_avg, on="REGION_NAME", how="left")
stores["Vs_Peers_%"] = np.where(stores["Region_Avg"]>0, (stores["CY_Sales"]/stores["Region_Avg"]-1)*100, 0)
stores["Vs_LY_%"]    = np.where(stores["LY_Sales"]>0, (stores["CY_Sales"]/stores["LY_Sales"]-1)*100, np.nan)

p75 = stores.groupby("REGION_NAME")["CY_Sales"].quantile(0.75).rename("Region_P75")
stores = stores.merge(p75, on="REGION_NAME", how="left")
stores["Opportunity"] = (stores["Region_P75"] - stores["CY_Sales"]).clip(lower=0)

# Apply filters
if selected_region != "All Regions":
    stores = stores[stores["REGION_NAME"] == selected_region]
# (Segment filter only affects visuals, not store-level scoring)
stores = stores[stores["Opportunity"] >= min_potential]

# Category grain (for charts)
cy_grain = df_cy.groupby(["OUTLET_ID","OUTLET_NAME","REGION_NAME","CATEGORY_SEGMENT","Month"], as_index=False)["NET_SALES"].sum()
if selected_region != "All Regions":
    cy_grain = cy_grain[cy_grain["REGION_NAME"] == selected_region]
if selected_segment != "All Segments":
    cy_grain = cy_grain[cy_grain["CATEGORY_SEGMENT"] == selected_segment]

# ======================================================
# KPI RIBBON (animated) — tightened spacing below
# ======================================================
tot_sales  = stores["CY_Sales"].sum() if len(stores) else 0
tot_opp    = stores["Opportunity"].sum() if len(stores) else 0
avg_peers  = stores["Vs_Peers_%"].mean() if len(stores) else 0
avg_growth = stores["Vs_LY_%"].mean() if len(stores) else 0
avg_days   = stores["Days_No_Purchase"].mean() if len(stores) else 0

k1,k2,k3,k4,k5 = st.columns(5)
animate_metric(k1, "YTD Sales", cash(tot_sales), color=ACC_TEAL)
animate_metric(k2, "Opportunity Pool", cash(tot_opp), color=ACC_AMBER)
animate_metric(k3, "Avg vs Peers", f"{avg_peers:+.1f}%", color=ACC_GREEN)
animate_metric(k4, "Avg vs LY", f"{avg_growth:+.1f}%", color=ACC_CORAL)
animate_metric(k5, "Avg Days w/o Purchase", f"{avg_days:.0f}", color=TEXT_MAIN)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ======================================================
# TABS
# ======================================================
tab1, tab2, tab3 = st.tabs(["Overview", "Top Performers", "Outlet Deep Dive"])

# ======================================================
# TAB 1 — OVERVIEW (Donut + Regional)
# ======================================================
with tab1:
    c1, c2 = st.columns([0.52, 0.48], gap="large")

    # Donut: Opportunity Mix by Category (with extra gap under title)
    with c1:
        st.markdown("<div class='panel fade-in'><div class='section-title'>Opportunity Mix by Category</div>", unsafe_allow_html=True)
        # create gap between title and chart
        st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

        cat_sales = cy_grain.groupby("CATEGORY_SEGMENT")["NET_SALES"].sum().sort_values(ascending=False)
        total_sales = cat_sales.sum() or 1
        opp_pool = stores["Opportunity"].sum()
        opp_by_cat = (cat_sales/total_sales) * opp_pool
        donut_df = pd.DataFrame({"Category": cat_sales.index, "Opportunity": opp_by_cat.values})
        fig_donut = go.Figure(go.Pie(
            labels=donut_df["Category"],
            values=donut_df["Opportunity"],
            hole=0.55,
            textinfo="label+percent",
            hovertemplate="<b>%{label}</b><br>$%{value:,.0f}<extra></extra>"
        ))
        fig_donut.update_traces(marker=dict(colors=[
            "#3a86ff","#00b4d8","#90e0ef","#caf0f8","#ffb703","#fb8500","#06d6a0","#ffd166"
        ], line=dict(color=NAVY_PANEL, width=2)))
        fig_donut.update_layout(template="plotly_dark", paper_bgcolor=NAVY_PANEL, font_color=TEXT_MAIN,
                                showlegend=False, height=420, margin=dict(l=6,r=6,t=6,b=6))
        st.plotly_chart(fig_donut, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Regional Snapshot: Sales vs Opportunity (with extra gap under title, light text)
    with c2:
        st.markdown("<div class='panel fade-in'><div class='section-title'>Regional Performance Snapshot</div>", unsafe_allow_html=True)
        st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

        region_perf = stores.groupby("REGION_NAME", as_index=False).agg(
            Total_Sales=("CY_Sales","sum"),
            Total_Opp=("Opportunity","sum"),
            Avg_Growth=("Vs_LY_%","mean")
        ).sort_values("Total_Sales", ascending=True)
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(
            y=region_perf["REGION_NAME"], x=region_perf["Total_Sales"], orientation="h",
            name="YTD Sales", marker_color=ACC_TEAL,
            text=[cash(x) for x in region_perf["Total_Sales"]], textposition="auto",
            hovertemplate="<b>%{y}</b><br>Sales: %{x:,.0f}<extra></extra>"
        ))
        fig.add_trace(go.Scatter(
            y=region_perf["REGION_NAME"], x=region_perf["Total_Opp"], mode="markers+lines",
            name="Opportunity", marker=dict(color=ACC_AMBER, size=8), line=dict(color=ACC_AMBER, width=2),
            hovertemplate="<b>%{y}</b><br>Opp: %{x:,.0f}<extra></extra>"
        ))
        fig.update_layout(
            template="plotly_dark", paper_bgcolor=NAVY_PANEL, plot_bgcolor=NAVY_PANEL,
            height=420, margin=dict(l=10,r=10,t=24,b=10), xaxis_title="Value ($)",
            font=dict(color=TEXT_MAIN), legend=dict(font=dict(color=TEXT_MAIN)),
        )
        fig.update_xaxes(tickfont=dict(color=TEXT_MAIN))
        fig.update_yaxes(tickfont=dict(color=TEXT_MAIN))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# TAB 2 — TOP PERFORMERS (Solid table + centered header)
# ======================================================
with tab2:
    st.markdown("<div class='panel fade-in'><div class='section-title'>Top Outlets by Opportunity</div>", unsafe_allow_html=True)
    st.markdown("<div></div>", unsafe_allow_html=True)  
    top_stores = stores.sort_values("Opportunity", ascending=False).head(20).copy()
    top_stores["Rank"] = range(1, len(top_stores)+1)
    st.dataframe(
        top_stores[["Rank","OUTLET_NAME","REGION_NAME","CY_Sales","Opportunity","Vs_LY_%","Vs_Peers_%","Days_No_Purchase"]]
            .style.format({"CY_Sales":"${:,.0f}","Opportunity":"${:,.0f}",
                           "Vs_LY_%":"{:+.1f}%","Vs_Peers_%":"{:+.1f}%","Days_No_Purchase":"{:.0f}"}),
        use_container_width=True, height=520
    )
    st.download_button("📥 Download CSV", data=top_stores.to_csv(index=False),
                       file_name="nuvora_top_outlets.csv", mime="text/csv")
    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# TAB 3 — OUTLET DEEP DIVE (AI action with lighter text & next-steps cards)
# ======================================================
with tab3:
    st.markdown(f"<div class='panel fade-in'><div class='section-title' style='color:{ACC_AMBER};'>Outlet Deep Dive</div>", unsafe_allow_html=True)
    choice = st.selectbox("Choose Outlet", ["Select..."] + stores["OUTLET_NAME"].tolist())

    if choice != "Select...":
        s = stores[stores["OUTLET_NAME"] == choice].iloc[0]
        sid = s["OUTLET_ID"]

        # ====== Subcolumns: Chart + AI Insights ======
        c1, c2 = st.columns([0.58, 0.42], gap="large")

        # --- Left: Sales by Category ---
        # --- Left: Sales + Opportunity by Category ---
        with c1:
            st.markdown(
                f"<div class='section-title' style='color:{NAVY_BG};'>YTD Sales & Opportunity by Category</div>", unsafe_allow_html=True)

            # --- Build sales + opportunity data ---
            detail_cat = (
                df_cy[df_cy["OUTLET_ID"] == sid]
                .groupby("CATEGORY_SEGMENT", as_index=False)["NET_SALES"].sum()
                .sort_values("NET_SALES", ascending=True)
            )

            # Estimate opportunity share by category (based on outlet sales mix)
            outlet_total = detail_cat["NET_SALES"].sum() or 1
            outlet_opp = float(s["Opportunity"])
            detail_cat["Opportunity"] = (detail_cat["NET_SALES"] / outlet_total) * outlet_opp

            # --- Dual-axis figure ---
            fig = make_subplots(specs=[[{"secondary_y": True}]])

            # Bars → YTD Sales
            fig.add_trace(
                go.Bar(
                    y=detail_cat["CATEGORY_SEGMENT"],
                    x=detail_cat["NET_SALES"],
                    name="YTD Sales",
                    orientation="h",
                    marker_color=ACC_TEAL,
                    text=[cash(x) for x in detail_cat["NET_SALES"]],
                    textposition="auto",
                    hovertemplate="<b>%{y}</b><br>Sales: $%{x:,.0f}<extra></extra>"
                ),
                secondary_y=False
            )

            # Scatter → Opportunity
            fig.add_trace(
                go.Scatter(
                    y=detail_cat["CATEGORY_SEGMENT"],
                    x=detail_cat["Opportunity"],
                    name="Opportunity",
                    mode="markers+lines",
                    marker=dict(color=ACC_AMBER, size=10, line=dict(color=NAVY_BG, width=1.5)),
                    line=dict(color=ACC_AMBER, width=2, dash="dot"),
                    hovertemplate="<b>%{y}</b><br>Opportunity: $%{x:,.0f}<extra></extra>"
                ),
                secondary_y=True
            )

            # --- Layout ---
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor=NAVY_PANEL,
                plot_bgcolor=NAVY_PANEL,
                height=460,
                margin=dict(l=10, r=20, t=30, b=30),
                font_color=TEXT_MAIN,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            fig.update_xaxes(title_text="Sales ($)", showgrid=True)
            fig.update_yaxes(title_text=None)

            st.plotly_chart(fig, use_container_width=True)


        # --- Right: AI Recommendation + Metrics ---
        with c2:
            st.markdown(
                f"<div class='section-title' style='color:{NAVY_BG};'>AI Recommendation</div>", unsafe_allow_html=True)

            # === SMART SCORING ===
            score = (
                0.5 * (s["Opportunity"] / (stores["Opportunity"].quantile(0.95) + 1e-9)) +
                0.25 * (s["Days_No_Purchase"] / 90) +
                0.15 * max(0, - (s["Vs_LY_%"] if pd.notna(s["Vs_LY_%"]) else 0) / 50) +
                0.10 * max(0, - s["Vs_Peers_%"] / 40)
            )
            score = float(np.clip(score, 0, 1))
            conf = int(score * 100)

            if score >= 0.75:
                action, color, note, steps = (
                    "🎯 Strategic Recovery Plan", ACC_CORAL,
                    "High missed potential with inactivity or decline.",
                    ["Targeted promo for top 2 segments",
                     "Incentivize bulk order next cycle",
                     "Schedule account call within 2 weeks"]
                )
            elif score >= 0.55:
                action, color, note, steps = (
                    "💡 Upsell / Cross-Sell Campaign", ACC_AMBER,
                    "Moderate performance with untapped potential.",
                    ["Bundle pricing for mid-tier SKUs",
                     "Cross-sell complementary lines",
                     "Run digital push campaign"]
                )
            elif score >= 0.35:
                action, color, note, steps = (
                    "🤝 Maintain & Monitor", ACC_GREEN,
                    "Stable vs peers and last year — maintain cadence.",
                    ["Monthly review call",
                     "Share best sellers by region",
                     "Track order frequency"]
                )
            else:
                action, color, note, steps = (
                    "⚙️ Portfolio Optimization", ACC_AMBER,
                    "Low risk and limited upside; optimize shelf & assortment.",
                    ["Audit slow movers",
                     "Rationalize SKUs under threshold",
                     "Optimize product placement"]
                )

            # === ACTION CARD ===
            st.markdown(
                f"""
                <div class='panel slide-up' style='border-color:{color}; margin-top:10px;'>
                    <h3 style='margin:0;color:{color};'>{action}</h3>
                    <p class='small-muted' style='margin:6px 0 10px 0; color:{TEXT_MAIN};'>{note}</p>
                    <div style='color:{TEXT_MAIN}; margin-bottom:6px;'>Confidence: <b style='color:{color};'>{conf}%</b></div>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.progress(score)

            # === NEXT STEPS ===
            st.markdown(f"<div class='section-title' style='color:{ACC_AMBER};'>Next Steps</div>", unsafe_allow_html=True)
            st.markdown("<div class='steps-grid slide-up'>", unsafe_allow_html=True)
            for step in steps:
                st.markdown(f"<div class='step-card' style='margin-bottom:3px;'><div class='step-icon'>✓</div><div class='step-text'>{step}</div></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# WATERMARK
# ======================================================
st.markdown("<div class='watermark'>Nuvora</div>", unsafe_allow_html=True)


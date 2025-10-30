# ==========================================================
# Nuvora Insight Cloud — Executive Dashboard (Unified Deep Navy Theme)
# ==========================================================
from PIL import Image
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.linear_model import LinearRegression

from PIL import Image
import streamlit as st

# ----------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------
logo = Image.open("1.png")

st.set_page_config(
    page_title="Nuvora Insight Cloud",
    layout="wide",
    page_icon=logo  
)

# ----------------------------------------------------------
# COLOR SYSTEM (Unified)
# ----------------------------------------------------------
BG = "#0b132b"
PANEL = "#1a2238"
ACCENT_CYAN = "#f87c17"
ACCENT_AMBER = "#ffb703"
GREEN = "#00ffae"
RED = "#ff4d6d"
TEXT_MAIN = "#eaf0f9"
TEXT_MUTED = "#9aa4b6"

# ----------------------------------------------------------
# GLOBAL STYLE
# ----------------------------------------------------------
st.markdown(f"""
<style>
html, body, [class*="css"] {{
  background-color:{BG};
  color:{TEXT_MAIN};
  font-family:'Inter','Segoe UI',sans-serif;
}}
h1 {{
  color:{ACCENT_CYAN};
  font-size:2.2rem;
  font-weight:700;
  margin-bottom:0.5rem;
}}
h2,h3,h4 {{
  color:{ACCENT_AMBER};
  font-weight:600;
  letter-spacing:0.3px;
}}
.section {{
  background:{TEXT_MAIN};
  border:1px solid {ACCENT_CYAN}22;
  border-radius:14px;
  padding:26px 30px;
  margin-bottom:24px;
  box-shadow:0 0 18px rgba(0,224,255,0.05);
}}
.metric {{
  text-align:center;
  background:{PANEL};
  border-radius:12px;
  padding:18px;
  border:1px solid {ACCENT_CYAN}33;
  box-shadow:inset 0 0 10px rgba(0,0,0,0.3);
}}
.metric .val {{ font-size:26px; font-weight:700; color:{ACCENT_CYAN}; }}
.metric .lab {{ font-size:12px; text-transform:uppercase; color:{TEXT_MUTED}; letter-spacing:0.6px; }}
hr {{ border:none; height:1px; background:rgba(255,255,255,0.08); margin:20px 0; }}
.stSelectbox label, .stSlider label {{ color:{ACCENT_AMBER}; font-weight:500; }}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------
# DATAFRAME STYLING (Dark)
# ----------------------------------------------------------


def style_dark(df):
    return df.style.set_table_styles([
        {'selector': 'thead th', 'props': [('background-color', ACCENT_AMBER),
                                           ('color', BG),
                                           ('font-weight', '700'),
                                           ('text-align', 'center')]},
        {'selector': 'tbody td', 'props': [('background-color', PANEL),
                                           ('color', TEXT_MAIN),
                                           ('border', f'0.5px solid {ACCENT_CYAN}22')]}],
        overwrite=False)

# ----------------------------------------------------------
# DATA GENERATION
# ----------------------------------------------------------


@st.cache_data
def generate_demo():
    np.random.seed(42)
    dates = pd.date_range("2024-01-01", periods=365)
    menu = ["Burger", "Wrap", "Salad", "Tacos",
            "Latte", "Smoothie", "Pasta", "Dessert"]
    data = []
    for d in dates:
        for item in menu:
            price = np.random.uniform(8, 20)
            units = np.random.poisson(18)
            sales = price * units
            margin = sales * np.random.uniform(0.4, 0.6)
            promo = np.random.choice([0, 1], p=[0.85, 0.15])
            data.append([d, item, price, units, sales, margin, promo])
    df = pd.DataFrame(
        data, columns=["DATE", "ITEM", "PRICE", "UNITS", "SALES", "MARGIN", "PROMO"])
    df["WEEK"] = df["DATE"].dt.to_period("W").apply(lambda r: r.start_time)
    return df


df = generate_demo()
weekly = df.groupby("WEEK", as_index=False).agg(
    SALES=("SALES", "sum"), MARGIN=("MARGIN", "sum"))

# ----------------------------------------------------------
# HELPERS
# ----------------------------------------------------------


def slope(series):
    x = np.arange(len(series)).reshape(-1, 1)
    return LinearRegression().fit(x, series).coef_[0]


def plot_style(fig):
    fig.update_layout(
        template="plotly_dark",
        height=420,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_MAIN),
        margin=dict(t=40, l=20, r=20, b=40),
        shapes=[dict(type="rect", xref="paper", yref="paper",
                     x0=0, y0=0, x1=1, y1=1, line=dict(color=ACCENT_CYAN, width=0.6))]
    )
    return fig


# ----------------------------------------------------------
# SIDEBAR NAVIGATION
# ----------------------------------------------------------

# Load logo
logo = Image.open("1.png")

st.sidebar.image(logo, use_container_width=True)

st.sidebar.markdown("</div>", unsafe_allow_html=True)


page = st.sidebar.radio("Navigation", [
                        "Overview", "Menu Insights", "Pricing Lab", "Competitor View", "Data Access"])
st.sidebar.markdown("</div>", unsafe_allow_html=True)

# ==========================================================
# 1. OVERVIEW
# ==========================================================
if page == "Overview":
    st.title("Executive Overview")
    st.caption("Business health and performance summary.")

    total_sales = df["SALES"].sum()
    avg_margin = (df["MARGIN"].sum() / df["SALES"].sum()) * 100
    total_units = df["UNITS"].sum()
    promo_share = df["PROMO"].mean() * 100
    trend = slope(weekly["SALES"])

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(
        f"<div class='metric'><div class='val'>${total_sales:,.0f}</div><div class='lab'>Total Sales</div></div>", unsafe_allow_html=True)
    c2.markdown(
        f"<div class='metric'><div class='val'>{avg_margin:.1f}%</div><div class='lab'>Average Margin</div></div>", unsafe_allow_html=True)
    c3.markdown(
        f"<div class='metric'><div class='val'>{total_units:,.0f}</div><div class='lab'>Units Sold</div></div>", unsafe_allow_html=True)
    c4.markdown(
        f"<div class='metric'><div class='val'>{promo_share:.1f}%</div><div class='lab'>Promo Share</div></div>", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    trend_text = "📈 Increasing" if trend > 0 else "📉 Decreasing"
    st.markdown(
        f"**Revenue Trend:** {trend_text} ({trend/1e6:.2f}M weekly slope)")

    fig = px.line(weekly, x="WEEK", y="SALES", title="Weekly Revenue Trend",
                  color_discrete_sequence=[ACCENT_AMBER])
    st.plotly_chart(plot_style(fig), use_container_width=True)

# ==========================================================
# 2. MENU INSIGHTS
# ==========================================================
elif page == "Menu Insights":
    st.title("Menu Insights")
    st.caption("Performance and profitability across product categories.")

    summary = df.groupby("ITEM", as_index=False).agg(
        SALES=("SALES", "sum"), UNITS=("UNITS", "sum"), MARGIN=("MARGIN", "sum"))
    summary["MARGIN_PCT"] = summary["MARGIN"] / summary["SALES"] * 100

    q_sales = summary["SALES"].quantile([0.25, 0.75])
    q_margin = summary["MARGIN_PCT"].quantile([0.25, 0.75])

    def classify(r):
        if r["SALES"] >= q_sales[0.75] and r["MARGIN_PCT"] >= q_margin[0.75]:
            return "Star"
        if r["SALES"] >= q_sales[0.75]:
            return "Workhorse"
        if r["MARGIN_PCT"] >= q_margin[0.75]:
            return "Hidden Gem"
        return "Low Performer"

    summary["SEGMENT"] = summary.apply(classify, axis=1)

    fig = px.scatter(summary, x="SALES", y="MARGIN_PCT", size="UNITS", color="SEGMENT",
                     color_discrete_sequence=[
                         ACCENT_AMBER, ACCENT_CYAN, GREEN, RED],
                     title="Sales vs Margin by Segment")
    st.plotly_chart(plot_style(fig), use_container_width=True)
    st.dataframe(style_dark(summary.sort_values("SALES", ascending=False)))

# ==========================================================
# 3. PRICING LAB
# ==========================================================
elif page == "Pricing Lab":
    st.title("Pricing Lab")
    st.caption("Estimate revenue and demand shifts based on price changes.")

    item = st.selectbox("Select Item", sorted(df["ITEM"].unique()))
    base_df = df[df["ITEM"] == item]
    base_price = base_df["PRICE"].mean()
    base_units = base_df["UNITS"].mean()
    elasticity = -1.2

    pct = st.slider("Price Change (%)", -25, 25, 0)
    new_price = base_price * (1 + pct / 100)
    new_units = base_units * (1 + elasticity * (pct / 100))
    new_rev = new_price * new_units
    base_rev = base_price * base_units
    rev_delta = new_rev - base_rev

    c1, c2, c3 = st.columns(3)
    c1.metric("Baseline Revenue", f"${base_rev:,.0f}")
    c2.metric("Projected Revenue",
              f"${new_rev:,.0f}", f"{(rev_delta / base_rev) * 100:+.1f}%")
    c3.metric("New Price", f"${new_price:.2f}")

    st.markdown(
        f"**Interpretation:** A {pct:+.0f}% price shift implies ≈ {elasticity * pct:+.1f}% volume change. Use for margin optimization.")

# ==========================================================
# 4. COMPETITOR VIEW
# ==========================================================
elif page == "Competitor View":
    st.title("Competitor Benchmarks")
    st.caption("Compare pricing and margin positioning against peers.")

    your_price = df["PRICE"].mean()
    peer_price = np.random.uniform(10, 18)
    price_gap = (your_price / peer_price - 1) * 100
    your_margin = (df["MARGIN"].sum() / df["SALES"].sum()) * 100
    peer_margin = your_margin + np.random.uniform(-3, 3)

    st.markdown(f"""
    <div class='section'>
    <b>Market Comparison</b><br><br>
    • Avg Price: ${your_price:.2f} vs peers ${peer_price:.2f} ({price_gap:+.1f}%)<br>
    • Avg Margin: {your_margin:.1f}% vs {peer_margin:.1f}%<br><br>
    <span style='color:{TEXT_MUTED};'>Strategic Note:</span>  
    Your pricing sits in the {'premium' if price_gap>0 else 'value'} tier. Adjust bundling and campaigns accordingly.
    </div>
    """, unsafe_allow_html=True)

# ==========================================================
# 5. DATA ACCESS
# ==========================================================
else:
    st.title("Data Access")
    st.caption("Export data for external analysis or integrations.")
    st.download_button("Download Sales Data", df.to_csv(
        index=False).encode("utf-8"), "nuvora_data.csv", "text/csv")
    st.dataframe(style_dark(df.sample(100).sort_values("DATE")))

import streamlit as st
import pandas as pd
import numpy as np

import plotly.express as px
import plotly.graph_objects as go

from prophet import Prophet
from scipy.stats import zscore

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Executive Intelligence",
    page_icon="🚀",
    layout="wide"
)

# =========================================================
# FUTURISTIC ELITE CSS
# =========================================================

st.markdown("""
<style>

/* =========================================================
MAIN BACKGROUND
========================================================= */

.stApp {
    background:
        radial-gradient(circle at top left, rgba(59,130,246,0.15), transparent 25%),
        radial-gradient(circle at top right, rgba(139,92,246,0.12), transparent 25%),
        radial-gradient(circle at bottom left, rgba(16,185,129,0.12), transparent 25%),
        linear-gradient(135deg, #020617 0%, #0F172A 50%, #111827 100%);
    color: white;
}

/* =========================================================
SIDEBAR
========================================================= */

[data-testid="stSidebar"] {
    background: rgba(15, 23, 42, 0.85);
    border-right: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(20px);
}

/* =========================================================
BLOCK CONTAINER
========================================================= */

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* =========================================================
HEADER
========================================================= */

.main-title {
    font-size: 58px;
    font-weight: 800;
    line-height: 1.1;
    color: white;
    margin-bottom: 10px;
    animation: glow 3s ease-in-out infinite alternate;
}

.sub-title {
    font-size: 20px;
    color: #94A3B8;
    margin-bottom: 30px;
}

/* =========================================================
GLOW ANIMATION
========================================================= */

@keyframes glow {

    from {
        text-shadow:
            0 0 10px rgba(59,130,246,0.5),
            0 0 20px rgba(59,130,246,0.3);
    }

    to {
        text-shadow:
            0 0 20px rgba(139,92,246,0.7),
            0 0 40px rgba(139,92,246,0.4);
    }
}

/* =========================================================
GLASS CARD
========================================================= */

.glass-card {

    background: rgba(255,255,255,0.06);

    border:
        1px solid rgba(255,255,255,0.08);

    backdrop-filter: blur(18px);

    border-radius: 28px;

    padding: 28px;

    box-shadow:
        0 8px 32px rgba(0,0,0,0.35),
        0 0 24px rgba(59,130,246,0.08);

    transition: 0.35s ease;

    position: relative;

    overflow: hidden;

    min-height: 210px;

    display: flex;
    flex-direction: column;
    justify-content: center;
}

.glass-card:hover {

    transform: translateY(-8px);

    box-shadow:
        0 12px 36px rgba(0,0,0,0.45),
        0 0 30px rgba(139,92,246,0.18);
}

.glass-card::before {

    content: "";

    position: absolute;

    width: 180px;
    height: 180px;

    background:
        radial-gradient(
            rgba(59,130,246,0.18),
            transparent
        );

    top: -50px;
    right: -50px;
}

.glass-card * {
    position: relative;
    z-index: 2;
}

/* =========================================================
METRIC
========================================================= */

.metric-label {

    font-size: 17px;

    color: #94A3B8;

    margin-bottom: 18px;

    font-weight: 500;
}

.metric-value {

    font-size: 30px;

    font-weight: 800;

    line-height: 1.2;

    background:
        linear-gradient(
            90deg,
            #60A5FA,
            #A78BFA
        );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;

    word-break: break-word;

    overflow-wrap: break-word;
}

/* =========================================================
SECTION TITLE
========================================================= */

.section-title {

    font-size: 30px;
    font-weight: 700;
    margin-top: 10px;
    margin-bottom: 20px;
    color: white;
}

/* =========================================================
INSIGHT PANEL
========================================================= */

.insight-box {

    background:
        linear-gradient(
            135deg,
            rgba(59,130,246,0.12),
            rgba(139,92,246,0.10)
        );

    border:
        1px solid rgba(255,255,255,0.08);

    padding: 24px;

    border-radius: 24px;

    backdrop-filter: blur(12px);

    box-shadow:
        0 8px 24px rgba(0,0,0,0.25);

    color: white;
}

/* =========================================================
TAB STYLE
========================================================= */

.stTabs [data-baseweb="tab"] {
    font-size: 16px;
    font-weight: 600;
}

/* =========================================================
HIDE STREAMLIT
========================================================= */

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div class="main-title">
🚀 AI Executive Intelligence Platform
</div>

<div class="sub-title">
Futuristic forecasting, anomaly detection, and business intelligence system for modern e-commerce analytics.
</div>
""", unsafe_allow_html=True)

# =========================================================
# LOAD DATA
# =========================================================

df = pd.read_csv(
    "data/raw/ecommerce_sales.csv",
    sep=';',
    encoding='latin1'
)

# =========================================================
# CLEANING
# =========================================================

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(' ', '_')
)

df['waktu_pesanan_dibuat'] = pd.to_datetime(
    df['waktu_pesanan_dibuat'],
    errors='coerce'
)

df['total_pembayaran'] = (
    df['total_pembayaran']
    .astype(str)
    .str.replace('Rp', '', regex=False)
    .str.replace('.', '', regex=False)
    .str.replace(',', '', regex=False)
    .str.strip()
)

df['total_pembayaran'] = pd.to_numeric(
    df['total_pembayaran'],
    errors='coerce'
)

df = df.dropna(
    subset=[
        'waktu_pesanan_dibuat',
        'total_pembayaran'
    ]
)

# =========================================================
# SIDEBAR FILTER
# =========================================================

st.sidebar.title("⚙️ Executive Filter")

province = st.sidebar.multiselect(
    "🌍 Province",
    options=df['provinsi'].dropna().unique(),
    default=df['provinsi'].dropna().unique()
)

payment = st.sidebar.multiselect(
    "💳 Payment Method",
    options=df['metode_pembayaran'].dropna().unique(),
    default=df['metode_pembayaran'].dropna().unique()
)

filtered_df = df[
    (df['provinsi'].isin(province)) &
    (df['metode_pembayaran'].isin(payment))
]

# =========================================================
# DAILY SALES
# =========================================================

daily_sales = filtered_df.groupby(
    'waktu_pesanan_dibuat'
)['total_pembayaran'].sum().reset_index()

daily_sales.columns = ['date', 'revenue']

# =========================================================
# FORECASTING
# =========================================================

forecast_df = daily_sales.copy()

forecast_df.columns = ['ds', 'y']

model = Prophet()

model.fit(forecast_df)

future = model.make_future_dataframe(
    periods=30
)

forecast = model.predict(future)

# =========================================================
# ANOMALY DETECTION
# =========================================================

daily_sales['z_score'] = zscore(
    daily_sales['revenue']
)

daily_sales['anomaly'] = np.where(
    abs(daily_sales['z_score']) > 3,
    'Anomaly',
    'Normal'
)

# =========================================================
# KPI
# =========================================================

total_revenue = daily_sales['revenue'].sum()

avg_revenue = daily_sales['revenue'].mean()

forecast_30 = forecast.tail(30)['yhat'].sum()

anomaly_count = len(
    daily_sales[
        daily_sales['anomaly'] == 'Anomaly'
    ]
)

# =========================================================
# KPI CARD FUNCTION
# =========================================================

def render_card(title, value):

    st.markdown(f"""
<div class="glass-card">

<div class="metric-label">
{title}
</div>

<div class="metric-value">
{value}
</div>

</div>
""", unsafe_allow_html=True)

# =========================================================
# KPI SECTION
# =========================================================

st.markdown("""
<div class="section-title">
📌 Executive Overview
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    render_card(
        "Total Revenue",
        f"Rp {total_revenue:,.0f}"
    )

with col2:
    render_card(
        "Average Daily Revenue",
        f"Rp {avg_revenue:,.0f}"
    )

with col3:
    render_card(
        "Forecast 30 Days",
        f"Rp {forecast_30:,.0f}"
    )

with col4:
    render_card(
        "Revenue Anomaly",
        anomaly_count
    )

# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Analytics",
    "📈 Forecasting",
    "🚨 Anomaly",
    "🧠 AI Insight"
])

# =========================================================
# ANALYTICS TAB
# =========================================================

with tab1:

    st.markdown("""
    <div class="section-title">
    🌍 Revenue by Province
    </div>
    """, unsafe_allow_html=True)

    province_sales = filtered_df.groupby(
        'provinsi'
    )['total_pembayaran'].sum().sort_values(
        ascending=False
    ).head(10)

    fig1 = px.bar(
        province_sales,
        orientation='h',
        template='plotly_dark',
        color=province_sales.values
    )

    fig1.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        height=600
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

# =========================================================
# FORECAST TAB
# =========================================================

with tab2:

    st.markdown("""
    <div class="section-title">
    🤖 AI Revenue Forecasting
    </div>
    """, unsafe_allow_html=True)

    fig2 = go.Figure()

    fig2.add_trace(go.Scatter(
        x=forecast_df['ds'],
        y=forecast_df['y'],
        mode='lines',
        name='Actual Revenue'
    ))

    fig2.add_trace(go.Scatter(
        x=forecast['ds'],
        y=forecast['yhat'],
        mode='lines',
        name='Forecast Revenue'
    ))

    fig2.add_trace(go.Scatter(
        x=forecast['ds'],
        y=forecast['yhat_upper'],
        mode='lines',
        line=dict(width=0),
        showlegend=False
    ))

    fig2.add_trace(go.Scatter(
        x=forecast['ds'],
        y=forecast['yhat_lower'],
        mode='lines',
        fill='tonexty',
        line=dict(width=0),
        name='Confidence Interval'
    ))

    fig2.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        height=600
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# =========================================================
# ANOMALY TAB
# =========================================================

with tab3:

    st.markdown("""
    <div class="section-title">
    🚨 Revenue Anomaly Detection
    </div>
    """, unsafe_allow_html=True)

    fig3 = px.scatter(
        daily_sales,
        x='date',
        y='revenue',
        color='anomaly',
        template='plotly_dark',
        color_discrete_map={
            'Normal': '#22C55E',
            'Anomaly': '#EF4444'
        }
    )

    fig3.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        height=600
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

# =========================================================
# AI INSIGHT TAB
# =========================================================

with tab4:

    st.markdown("""
    <div class="section-title">
    🧠 AI Strategic Insight
    </div>
    """, unsafe_allow_html=True)

    growth = (
        forecast.tail(30)['yhat'].mean() -
        forecast_df['y'].mean()
    )

    if growth > 0:

        st.markdown(f"""
        <div class="insight-box">

        <h3>📈 Positive Revenue Forecast</h3>

        <p>
        AI forecasting indicates positive growth potential
        with estimated future increase of:

        <br><br>

        <strong>
        Rp {growth:,.0f}
        </strong>

        </p>

        <hr>

        <ul>
            <li>Optimize inventory scaling strategy</li>
            <li>Focus marketing on high-performing provinces</li>
            <li>Monitor anomaly spikes for campaign analysis</li>
            <li>Improve payment experience optimization</li>
        </ul>

        </div>
        """, unsafe_allow_html=True)

    else:

        st.markdown("""
        <div class="insight-box">

        <h3>⚠️ Revenue Slowdown Warning</h3>

        <p>
        AI forecasting indicates slowing business momentum.
        Strategic optimization is recommended.
        </p>

        </div>
        """, unsafe_allow_html=True)

# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🚀 M. Wildan Nabila | Futuristic AI Executive Intelligence Platform"
)
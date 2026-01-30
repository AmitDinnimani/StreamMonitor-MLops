import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
import json
from datetime import datetime
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_DIR/"monitoring"/"monitoring.db"
REFRESH_INTERVAL = 40  # seconds
FEATURES = [f"feature{i}" for i in range(1, 9)]

# -------------------------------
# DATABASE CONNECTION
# -------------------------------
@st.cache_resource
def get_connection():
    """Create a cached SQLite connection."""
    return sqlite3.connect(DB_PATH, check_same_thread=False)

# -------------------------------
# DATA LOADERS
# -------------------------------
@st.cache_resource
def get_connection():
    """Return a persistent SQLite connection."""
    return sqlite3.connect(DB_PATH, check_same_thread=False)

@st.cache_data(ttl=REFRESH_INTERVAL)
def load_predictions():
    conn = get_connection()
    df = pd.read_sql(
        "SELECT timestamp, prediction FROM predictions ORDER BY timestamp DESC LIMIT 1000",
        conn,
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    return df

@st.cache_data(ttl=REFRESH_INTERVAL)
def load_metrics():
    conn = get_connection()
    df = pd.read_sql(
        """
        SELECT timestamp, median_value, mean_value, std_value, drift_score, mean_ratio, 
               median_ratio, std_ratio, alert, mean_drift_vals, median_drift_vals, std_drift_vals
        FROM metrics
        ORDER BY timestamp ASC
        """,
        conn,
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")

    # Parse JSON strings
    df["mean_drift_vals"] = df["mean_drift_vals"].apply(json.loads)
    df["median_drift_vals"] = df["median_drift_vals"].apply(json.loads)
    df["std_drift_vals"] = df["std_drift_vals"].apply(json.loads)
    return df


def get_baseline_median(df):
    return df["median_value"].iloc[0] if not df.empty else None

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="StreamMonitor Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📈 StreamMonitor – Real-Time ML Monitoring")
st.caption("Live prediction monitoring with streaming median, mean, std & drift detection")

# -------------------------------
# AUTO REFRESH
# -------------------------------
st.markdown(
    f"""<meta http-equiv="refresh" content="{REFRESH_INTERVAL}">""",
    unsafe_allow_html=True,
)

# -------------------------------
# LOAD DATA
# -------------------------------
pred_df = load_predictions()
metrics_df = load_metrics()

# -------------------------------
# TOP ROW: Prediction Distribution & Median Trend
# -------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Prediction Distribution (Last 1000 Predictions)")
    if not pred_df.empty:
        # Ensure predictions are numeric
        pred_df["prediction"] = pd.to_numeric(pred_df["prediction"], errors="coerce")
        pred_df = pred_df.dropna(subset=["prediction"])  # drop any invalid values

        if not pred_df.empty:
            hist = pd.cut(pred_df["prediction"], bins=20).value_counts().sort_index()
            hist.index = hist.index.astype(str)  # convert IntervalIndex to string
            st.bar_chart(hist)
        else:
            st.info("No valid numeric prediction data yet")
    else:
        st.info("No prediction data yet")

with col2:
    st.subheader("📉 Streaming Median Trend")
    if not metrics_df.empty:
        baseline = get_baseline_median(metrics_df)
        st.line_chart(metrics_df.set_index("timestamp")["median_value"])
        st.caption(f"Baseline Median: **{baseline:.3f}**")
    else:
        st.info("No metrics yet")

st.divider()

# -------------------------------
# SECOND ROW: Mean, Median, Std Trend
# -------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Mean Trend")
    if not metrics_df.empty:
        st.line_chart(metrics_df.set_index("timestamp")["mean_value"])
    else:
        st.info("No metrics yet")

with col2:
    st.subheader("Median Trend")
    if not metrics_df.empty:
        st.line_chart(metrics_df.set_index("timestamp")["median_value"])
    else:
        st.info("No metrics yet")

with col3:
    st.subheader("Std Trend")
    if not metrics_df.empty:
        st.line_chart(metrics_df.set_index("timestamp")["std_value"])
    else:
        st.info("No metrics yet")

st.divider()

# -------------------------------
# FEATURE-WISE DRIFT
# -------------------------------
st.subheader("🔹 Feature-Wise Drift (Last Measurement)")
if not metrics_df.empty:
    last_row = metrics_df.iloc[-1]

    # Mean drift per feature
    mean_drift_df = pd.DataFrame({
        "feature": FEATURES,
        "mean_drift": last_row["mean_drift_vals"],
        "median_drift": last_row["median_drift_vals"],
        "std_drift": last_row["std_drift_vals"]
    })

    st.markdown("**Mean Drift per Feature**")
    fig = px.bar(mean_drift_df, x="feature", y="mean_drift", title="Mean Drift per Feature",
                 color="mean_drift", color_continuous_scale="Reds")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Median Drift per Feature**")
    fig = px.bar(mean_drift_df, x="feature", y="median_drift", title="Median Drift per Feature",
                 color="median_drift", color_continuous_scale="Reds")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Std Drift per Feature**")
    fig = px.bar(mean_drift_df, x="feature", y="std_drift", title="Std Drift per Feature",
                 color="std_drift", color_continuous_scale="Reds")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No metrics yet")

st.divider()

# -------------------------------
# DRIFT ALERTS
# -------------------------------
st.subheader("🚨 Drift Alerts")
if not metrics_df.empty:
    latest = metrics_df.iloc[-1]
    current_status = "🚨 DRIFT DETECTED" if latest["alert"] else "✅ NO DRIFT"
    st.metric(
        label="Current Drift Status",
        value=current_status,
        delta=f"Drift Score: {latest['drift_score']:.4f}"
    )

    # Drift score over time
    drift_df = metrics_df.copy()
    drift_df["status"] = drift_df["alert"].map({0: "No Drift", 1: "Drift"})
    fig = px.scatter(drift_df, x="timestamp", y="drift_score", color="status",
                     color_discrete_map={"No Drift": "green", "Drift": "red"},
                     title="Drift Score Over Time")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No drift metrics yet")

st.divider()

# -------------------------------
# FOOTER
# -------------------------------
st.caption(
    f"Auto-refresh every {REFRESH_INTERVAL}s • SQLite backend • Feature-wise streaming median, mean, std & drift"
)

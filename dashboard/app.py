import duckdb
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

DB_PATH = Path("data/job_market.duckdb")

st.set_page_config(
    page_title="Job Market Pulse",
    page_icon="📊",
    layout="wide",
)

# ── Data loading ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=3600)
def load_data():
    if not DB_PATH.exists():
        return pd.DataFrame(), pd.DataFrame()
    conn = duckdb.connect(str(DB_PATH), read_only=True)
    history = conn.execute("SELECT * FROM job_market_history ORDER BY fetched_at").df()
    runs = conn.execute("SELECT * FROM pipeline_runs ORDER BY started_at").df()
    conn.close()
    return history, runs


history, runs = load_data()

# ── Header ────────────────────────────────────────────────────────────────────

st.title("📊 Job Market Pulse")
st.caption(
    "Tracking demand, salaries, and remote trends across 10 tech stacks — updated daily via Adzuna API."
)

if history.empty:
    st.warning("No data yet. Run `python run_pipeline.py` to populate the database.")
    st.stop()

# Latest run snapshot
latest_run_id = runs.iloc[-1]["run_id"] if not runs.empty else None
latest = history[history["run_id"] == latest_run_id] if latest_run_id else history

# ── Section 1: KPI Row ───────────────────────────────────────────────────────

st.subheader("Today's Snapshot")
k1, k2, k3, k4 = st.columns(4)

top_stack = latest.groupby("tech_stack")["job_count"].sum().idxmax()
k1.metric("Top Stack", top_stack, help="Most total listings today")

pay_df = latest.dropna(subset=["salary_avg"])
if not pay_df.empty:
    highest_pay = pay_df.groupby("tech_stack")["salary_avg"].mean().idxmax()
    avg_sal = pay_df.groupby("tech_stack")["salary_avg"].mean().max()
    k2.metric("Highest Paying", highest_pay, f"${avg_sal:,.0f} avg")
else:
    k2.metric("Highest Paying", "N/A", "No salary data")

remote_df = latest.groupby("tech_stack")["remote_pct"].mean()
most_remote = remote_df.idxmax()
k3.metric("Most Remote-Friendly", most_remote, f"{remote_df.max():.0f}% remote")

# Biggest mover (week-over-week demand_score change)
if len(runs) >= 2:
    prev_run_id = runs.iloc[-2]["run_id"]
    prev = history[history["run_id"] == prev_run_id]
    curr_score = latest.groupby("tech_stack")["demand_score"].mean()
    prev_score = prev.groupby("tech_stack")["demand_score"].mean()
    delta = (curr_score - prev_score).dropna()
    if not delta.empty:
        mover = delta.abs().idxmax()
        k4.metric("Biggest Mover", mover, f"{delta[mover]:+.1f} pts")
    else:
        k4.metric("Biggest Mover", "—", "Need 2+ runs")
else:
    k4.metric("Biggest Mover", "—", "Need 2+ runs")

st.divider()

# ── Section 2: Demand Ranking ─────────────────────────────────────────────────

st.subheader("Demand Ranking — Normalized Score (latest run)")

demand = (
    latest.groupby("tech_stack")["demand_score"]
    .mean()
    .reset_index()
    .sort_values("demand_score", ascending=True)
)
fig_demand = px.bar(
    demand,
    x="demand_score",
    y="tech_stack",
    orientation="h",
    color="demand_score",
    color_continuous_scale="Blues",
    labels={"demand_score": "Demand Score (0–100)", "tech_stack": ""},
    text="demand_score",
)
fig_demand.update_traces(texttemplate="%{text:.1f}", textposition="outside")
fig_demand.update_layout(coloraxis_showscale=False, height=400)
st.plotly_chart(fig_demand, use_container_width=True)

st.divider()

# ── Section 3: Trend Over Time ────────────────────────────────────────────────

st.subheader("Demand Trend Over Time")

if len(runs) < 2:
    st.info("Trend chart needs at least 2 pipeline runs. Come back tomorrow!")
else:
    trend = (
        history.groupby(["fetched_at", "tech_stack"])["demand_score"]
        .mean()
        .reset_index()
    )
    trend["fetched_at"] = pd.to_datetime(trend["fetched_at"]).dt.date

    selected_stacks = st.multiselect(
        "Filter stacks",
        options=sorted(trend["tech_stack"].unique()),
        default=sorted(trend["tech_stack"].unique()),
    )
    trend_filtered = trend[trend["tech_stack"].isin(selected_stacks)]
    fig_trend = px.line(
        trend_filtered,
        x="fetched_at",
        y="demand_score",
        color="tech_stack",
        markers=True,
        labels={"fetched_at": "Date", "demand_score": "Demand Score", "tech_stack": "Stack"},
    )
    fig_trend.update_layout(height=400)
    st.plotly_chart(fig_trend, use_container_width=True)

st.divider()

# ── Section 4: Remote vs On-Site ─────────────────────────────────────────────

st.subheader("Remote Friendliness by Stack")

remote = (
    latest[latest["location"] != "remote"]
    .groupby("tech_stack")["remote_pct"]
    .mean()
    .reset_index()
    .sort_values("remote_pct", ascending=True)
)
fig_remote = px.bar(
    remote,
    x="remote_pct",
    y="tech_stack",
    orientation="h",
    color="remote_pct",
    color_continuous_scale="Greens",
    labels={"remote_pct": "Remote-Friendly Listings (%)", "tech_stack": ""},
    text="remote_pct",
)
fig_remote.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
fig_remote.update_layout(coloraxis_showscale=False, height=400)
st.plotly_chart(fig_remote, use_container_width=True)

st.divider()

# ── Section 5: Salary Intelligence ──────────────────────────────────────────

st.subheader("Salary Intelligence")

sal = latest.dropna(subset=["salary_avg"])
if sal.empty:
    st.info("No salary data in current snapshot. Adzuna salary coverage varies by region.")
else:
    sal_agg = (
        sal.groupby("tech_stack")
        .agg(
            salary_avg=("salary_avg", "mean"),
            salary_min=("salary_min", "min"),
            salary_max=("salary_max", "max"),
            salary_disclosed_pct=("salary_disclosed_pct", "mean"),
        )
        .reset_index()
        .sort_values("salary_avg", ascending=False)
    )

    fig_sal = go.Figure()
    fig_sal.add_trace(go.Bar(
        name="Avg Salary",
        x=sal_agg["tech_stack"],
        y=sal_agg["salary_avg"],
        marker_color="steelblue",
        text=sal_agg["salary_avg"].apply(lambda x: f"${x:,.0f}"),
        textposition="outside",
    ))
    fig_sal.update_layout(
        yaxis_title="Annual Salary (USD)",
        height=400,
        yaxis_tickformat="$,.0f",
    )
    st.plotly_chart(fig_sal, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.caption("Salary disclosed % by stack")
        disc = sal_agg[["tech_stack", "salary_disclosed_pct"]].copy()
        disc["salary_disclosed_pct"] = disc["salary_disclosed_pct"].apply(lambda x: f"{x:.1f}%")
        st.dataframe(disc.set_index("tech_stack"), use_container_width=True)

st.divider()

# ── Section 6: City Heatmap ───────────────────────────────────────────────────

st.subheader("City Heatmap — Job Count by Stack × City")

heatmap_df = (
    latest[latest["location"] != "remote"]
    .pivot_table(index="location", columns="tech_stack", values="job_count", aggfunc="sum")
    .fillna(0)
)
fig_heat = px.imshow(
    heatmap_df,
    color_continuous_scale="Blues",
    labels={"color": "Job Count"},
    aspect="auto",
    text_auto=True,
)
fig_heat.update_layout(height=500)
st.plotly_chart(fig_heat, use_container_width=True)

st.divider()

# ── Footer ────────────────────────────────────────────────────────────────────

if not runs.empty:
    last_run = runs.iloc[-1]
    st.caption(
        f"Last updated: {last_run['finished_at']} · "
        f"Total pipeline runs: {len(runs)} · "
        f"Data source: Adzuna API"
    )

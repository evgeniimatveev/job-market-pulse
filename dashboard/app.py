import duckdb
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime

DB_PATH = Path("data/job_market.duckdb")

st.set_page_config(
    page_title="Job Market Pulse",
    page_icon="📊",
    layout="wide",
)

# ── Brand colors per stack ────────────────────────────────────────────────────
STACK_COLORS = {
    "Python":    "#3776AB",
    "SQL":       "#E38C00",
    "AWS":       "#FF9900",
    "Azure":     "#0078D4",
    "Tableau":   "#E97627",
    "Power BI":  "#F2C811",
    "dbt":       "#FF694B",
    "Spark":     "#E25A1C",
    "Airflow":   "#017CEE",
    "Snowflake": "#29B5E8",
}

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Hero header */
.hero {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    border-radius: 16px;
    padding: 2rem 2.5rem 1.5rem;
    margin-bottom: 1.5rem;
}
.hero h1 {
    font-size: 2.6rem;
    font-weight: 800;
    color: #ffffff;
    margin: 0 0 0.3rem 0;
    letter-spacing: -1px;
}
.hero p {
    color: #94a3b8;
    font-size: 1rem;
    margin: 0;
}
.hero .badge {
    display: inline-block;
    background: rgba(41, 181, 232, 0.15);
    border: 1px solid #29B5E8;
    color: #29B5E8;
    border-radius: 20px;
    padding: 0.2rem 0.8rem;
    font-size: 0.8rem;
    margin-top: 0.7rem;
    font-weight: 600;
}

/* KPI cards */
.kpi-card {
    background: linear-gradient(145deg, #1e293b, #0f172a);
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    text-align: center;
    transition: border-color 0.2s;
}
.kpi-card:hover { border-color: #29B5E8; }
.kpi-label {
    color: #64748b;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.4rem;
}
.kpi-icon { font-size: 1.4rem; margin-bottom: 0.3rem; }
.kpi-value {
    font-size: 1.9rem;
    font-weight: 800;
    color: #f1f5f9;
    line-height: 1.1;
}
.kpi-sub {
    font-size: 0.78rem;
    color: #29B5E8;
    margin-top: 0.25rem;
    font-weight: 500;
}

/* Section headers */
.section-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: #e2e8f0;
    margin: 0.5rem 0 0.2rem 0;
}
.section-sub {
    color: #64748b;
    font-size: 0.85rem;
    margin-bottom: 1rem;
}

/* Divider */
.custom-divider {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, #334155, transparent);
    margin: 1.5rem 0;
}
</style>
""", unsafe_allow_html=True)

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

# ── Hero Header ───────────────────────────────────────────────────────────────
last_updated = ""
if not runs.empty:
    ts = pd.to_datetime(runs.iloc[-1]["finished_at"]).strftime("%b %d %Y, %I:%M %p UTC")
    last_updated = f'<span class="badge">🔄 Last updated: {ts}</span>'

st.markdown(f"""
<div class="hero">
    <h1>📊 Job Market Pulse</h1>
    <p>Daily tracking of tech job demand, salaries & remote trends — 10 stacks × 10 US cities + remote</p>
    {last_updated}
</div>
""", unsafe_allow_html=True)

if history.empty:
    st.warning("No data yet. Run `python run_pipeline.py` to populate the database.")
    st.stop()

latest_run_id = runs.iloc[-1]["run_id"] if not runs.empty else None
latest = history[history["run_id"] == latest_run_id] if latest_run_id else history

# ── KPI Row ───────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)

top_stack = latest.groupby("tech_stack")["job_count"].sum().idxmax()
top_count = int(latest.groupby("tech_stack")["job_count"].sum().max())

pay_df = latest.dropna(subset=["salary_avg"])
if not pay_df.empty:
    sal_by_stack = pay_df.groupby("tech_stack")["salary_avg"].mean()
    highest_pay_stack = sal_by_stack.idxmax()
    highest_pay_val = sal_by_stack.max()
    pay_sub = f"${highest_pay_val:,.0f} avg salary"
else:
    highest_pay_stack = "N/A"
    pay_sub = "No salary data"

remote_df = latest[latest["location"] != "remote"].groupby("tech_stack")["remote_pct"].mean()
most_remote = remote_df.idxmax()
remote_val = remote_df.max()

# Biggest mover
if len(runs) >= 2:
    prev_run_id = runs.iloc[-2]["run_id"]
    prev = history[history["run_id"] == prev_run_id]
    curr_score = latest.groupby("tech_stack")["demand_score"].mean()
    prev_score = prev.groupby("tech_stack")["demand_score"].mean()
    delta = (curr_score - prev_score).dropna()
    if not delta.empty:
        mover = delta.abs().idxmax()
        mover_val = delta[mover]
        mover_sub = f"{mover_val:+.1f} pts vs yesterday"
    else:
        mover, mover_sub = "—", "Need 2+ runs"
else:
    mover, mover_sub = "—", "Need 2+ runs"

with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">🏆</div>
        <div class="kpi-label">Top Stack</div>
        <div class="kpi-value">{top_stack}</div>
        <div class="kpi-sub">{top_count:,} listings today</div>
    </div>""", unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">💰</div>
        <div class="kpi-label">Highest Paying</div>
        <div class="kpi-value">{highest_pay_stack}</div>
        <div class="kpi-sub">{pay_sub}</div>
    </div>""", unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">🌐</div>
        <div class="kpi-label">Most Remote-Friendly</div>
        <div class="kpi-value">{most_remote}</div>
        <div class="kpi-sub">{remote_val:.0f}% remote listings</div>
    </div>""", unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">📈</div>
        <div class="kpi-label">Biggest Mover</div>
        <div class="kpi-value">{mover}</div>
        <div class="kpi-sub">{mover_sub}</div>
    </div>""", unsafe_allow_html=True)

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

# ── Section 2: Demand Ranking ──────────────────────────────────────────────────
st.markdown('<div class="section-title">Demand Ranking</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Normalized score 0–100 · Python = baseline · Latest run only</div>', unsafe_allow_html=True)

demand = (
    latest.groupby("tech_stack")["job_count"].sum()
    .reset_index()
    .sort_values("job_count", ascending=True)
)
demand["demand_score"] = (
    (demand["job_count"] - demand["job_count"].min()) /
    (demand["job_count"].max() - demand["job_count"].min()) * 100
).round(1)
demand["color"] = demand["tech_stack"].map(STACK_COLORS)
demand["label"] = demand.apply(lambda r: f'{r["demand_score"]:.0f}  ({r["job_count"]:,} jobs)', axis=1)

fig_demand = go.Figure(go.Bar(
    x=demand["demand_score"],
    y=demand["tech_stack"],
    orientation="h",
    marker_color=demand["color"].tolist(),
    text=demand["label"],
    textposition="outside",
    textfont=dict(size=12, color="#94a3b8"),
    hovertemplate="<b>%{y}</b><br>Score: %{x:.1f}<br>Jobs: %{customdata:,}<extra></extra>",
    customdata=demand["job_count"],
))
fig_demand.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    height=420,
    margin=dict(l=10, r=120, t=10, b=10),
    xaxis=dict(
        showgrid=True, gridcolor="#1e293b",
        title="Demand Score (0–100)",
        color="#64748b", range=[0, 130],
    ),
    yaxis=dict(showgrid=False, color="#e2e8f0", tickfont=dict(size=13)),
    font=dict(family="Inter, sans-serif"),
)
st.plotly_chart(fig_demand, width='stretch')

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

# ── Section 3: Trend Over Time ─────────────────────────────────────────────────
st.markdown('<div class="section-title">Demand Trend Over Time</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">How demand score evolves daily — gets more valuable as history grows</div>', unsafe_allow_html=True)

if len(runs) < 2:
    st.info("Trend chart activates after 2 pipeline runs. Check back tomorrow!")
else:
    # Join history with runs to get clean run timestamps
    runs_ts = runs[["run_id", "started_at"]].copy()
    runs_ts["started_at"] = pd.to_datetime(runs_ts["started_at"], utc=True)
    hist_with_ts = history.merge(runs_ts, on="run_id")

    trend = (
        hist_with_ts.groupby(["started_at", "tech_stack"])["demand_score"]
        .mean()
        .reset_index()
        .rename(columns={"started_at": "run_time"})
    )

    # Label: "May 26 19:48" style
    trend["label"] = trend["run_time"].dt.strftime("%d %b %H:%M")
    unique_times = trend["run_time"].sort_values().unique()
    tickvals = list(unique_times)
    ticktext = [pd.Timestamp(t).strftime("%d %b\n%H:%M") for t in tickvals]

    all_stacks = sorted(trend["tech_stack"].unique())
    selected = st.multiselect("Filter stacks", all_stacks, default=all_stacks, key="trend_filter")
    trend_f = trend[trend["tech_stack"].isin(selected)]

    fig_trend = go.Figure()
    for stack in selected:
        s = trend_f[trend_f["tech_stack"] == stack].sort_values("run_time")
        color = STACK_COLORS.get(stack, "#888")
        fig_trend.add_trace(go.Scatter(
            x=s["run_time"], y=s["demand_score"],
            name=stack, mode="lines+markers",
            line=dict(color=color, width=2.5),
            marker=dict(size=9, color=color, line=dict(color="#0f172a", width=1.5)),
            hovertemplate=f"<b>{stack}</b><br>%{{x|%b %d %H:%M}}<br>Score: %{{y:.1f}}<extra></extra>",
        ))
    fig_trend.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=420,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(
            showgrid=True, gridcolor="#1e293b", color="#64748b",
            tickvals=tickvals, ticktext=ticktext,
            tickfont=dict(size=11),
        ),
        yaxis=dict(showgrid=True, gridcolor="#1e293b", title="Demand Score", color="#64748b"),
        legend=dict(bgcolor="rgba(15,23,42,0.8)", bordercolor="#334155", borderwidth=1),
        font=dict(family="Inter, sans-serif"),
    )
    st.plotly_chart(fig_trend, width='stretch')

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

# ── Section 4: Remote Friendliness ────────────────────────────────────────────
st.markdown('<div class="section-title">Remote Friendliness</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">% of on-site listings mentioning remote / hybrid / WFH in title or description</div>', unsafe_allow_html=True)

remote = (
    latest[latest["location"] != "remote"]
    .groupby("tech_stack")["remote_pct"]
    .mean()
    .reset_index()
    .sort_values("remote_pct", ascending=True)
)
remote["color"] = remote["tech_stack"].map(STACK_COLORS)

fig_remote = go.Figure(go.Bar(
    x=remote["remote_pct"],
    y=remote["tech_stack"],
    orientation="h",
    marker_color=remote["color"].tolist(),
    text=remote["remote_pct"].apply(lambda x: f"{x:.1f}%"),
    textposition="outside",
    textfont=dict(size=12, color="#94a3b8"),
    hovertemplate="<b>%{y}</b><br>Remote: %{x:.1f}%<extra></extra>",
))
fig_remote.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    height=400,
    margin=dict(l=10, r=80, t=10, b=10),
    xaxis=dict(
        showgrid=True, gridcolor="#1e293b",
        title="Remote-Friendly Listings (%)",
        color="#64748b", range=[0, 45],
    ),
    yaxis=dict(showgrid=False, color="#e2e8f0", tickfont=dict(size=13)),
    font=dict(family="Inter, sans-serif"),
)
st.plotly_chart(fig_remote, width='stretch')

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

# ── Section 5: Salary Intelligence ────────────────────────────────────────────
st.markdown('<div class="section-title">Salary Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Average salary with min–max range · Only listings that disclose compensation</div>', unsafe_allow_html=True)

sal = latest.dropna(subset=["salary_avg"])
if sal.empty:
    st.info("No salary data in this snapshot.")
else:
    sal_agg = (
        sal.groupby("tech_stack")
        .agg(salary_avg=("salary_avg","mean"), salary_min=("salary_min","min"), salary_max=("salary_max","max"), pct=("salary_disclosed_pct","mean"))
        .reset_index()
        .sort_values("salary_avg", ascending=True)
    )
    sal_agg["color"] = sal_agg["tech_stack"].map(STACK_COLORS)

    fig_sal = go.Figure()
    # Range bars (min → max)
    for _, row in sal_agg.iterrows():
        fig_sal.add_trace(go.Scatter(
            x=[row["salary_min"], row["salary_max"]],
            y=[row["tech_stack"], row["tech_stack"]],
            mode="lines",
            line=dict(color=row["color"], width=6),
            showlegend=False,
            hoverinfo="skip",
        ))
    # Avg dot
    fig_sal.add_trace(go.Scatter(
        x=sal_agg["salary_avg"],
        y=sal_agg["tech_stack"],
        mode="markers+text",
        marker=dict(size=14, color=sal_agg["color"].tolist(), line=dict(color="#0f172a", width=2)),
        text=sal_agg["salary_avg"].apply(lambda v: f"${v/1000:.0f}k"),
        textposition="middle right",
        textfont=dict(size=11, color="#e2e8f0"),
        hovertemplate="<b>%{y}</b><br>Avg: $%{x:,.0f}<extra></extra>",
        showlegend=False,
    ))
    # Disclosed % annotation
    for _, row in sal_agg.iterrows():
        fig_sal.add_annotation(
            x=row["salary_min"], y=row["tech_stack"],
            text=f'{row["pct"]:.0f}%',
            showarrow=False, xanchor="right", xshift=-8,
            font=dict(size=10, color="#64748b"),
        )

    fig_sal.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=420,
        margin=dict(l=10, r=100, t=10, b=40),
        xaxis=dict(
            showgrid=True, gridcolor="#1e293b",
            tickformat="$,.0f", title="Annual Salary (USD)",
            color="#64748b",
        ),
        yaxis=dict(showgrid=False, color="#e2e8f0", tickfont=dict(size=13)),
        font=dict(family="Inter, sans-serif"),
        annotations=list(fig_sal.layout.annotations) + [
            dict(
                x=0.01, y=-0.08, xref="paper", yref="paper",
                text="← numbers on left = % of listings disclosing salary",
                showarrow=False, font=dict(size=10, color="#475569"),
            )
        ],
    )
    st.plotly_chart(fig_sal, width='stretch')

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

# ── Section 6: City Heatmap ────────────────────────────────────────────────────
st.markdown('<div class="section-title">City Heatmap</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Total job listings by tech stack × city — darker = more demand</div>', unsafe_allow_html=True)

heatmap_df = (
    latest[latest["location"] != "remote"]
    .pivot_table(index="location", columns="tech_stack", values="job_count", aggfunc="sum")
    .fillna(0)
)
col_order = [c for c in sorted(STACK_COLORS.keys()) if c in heatmap_df.columns]
heatmap_df = heatmap_df[col_order]

fig_heat = px.imshow(
    heatmap_df,
    color_continuous_scale=[[0, "#0f172a"], [0.15, "#1e3a5f"], [0.4, "#1d6fa4"], [0.7, "#2196d3"], [1.0, "#29B5E8"]],
    labels={"color": "Job Count"},
    aspect="auto",
    text_auto=True,
)
fig_heat.update_traces(
    texttemplate="%{z:,}",
    textfont=dict(size=11, color="white"),
)
fig_heat.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    height=480,
    margin=dict(l=10, r=10, t=10, b=10),
    coloraxis_colorbar=dict(
        title=dict(text="Jobs", font=dict(color="#64748b")),
        tickformat=",",
        bgcolor="rgba(0,0,0,0)",
        outlinecolor="#334155",
        tickcolor="#64748b",
        tickfont=dict(color="#64748b"),
    ),
    xaxis=dict(color="#94a3b8", tickfont=dict(size=12)),
    yaxis=dict(color="#94a3b8", tickfont=dict(size=12)),
    font=dict(family="Inter, sans-serif"),
)
st.plotly_chart(fig_heat, width='stretch')

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
total_jobs = int(history["job_count"].sum())
total_runs = len(runs)
st.markdown(
    f'<div style="text-align:center;color:#475569;font-size:0.8rem;">'
    f'📊 {total_jobs:,} job records · {total_runs} pipeline runs · '
    f'Data: <a href="https://www.adzuna.com" style="color:#29B5E8;">Adzuna API</a> · '
    f'Built by <a href="https://github.com/evgeniimatveev" style="color:#29B5E8;">Evgenii Matveev</a>'
    f'</div>',
    unsafe_allow_html=True,
)

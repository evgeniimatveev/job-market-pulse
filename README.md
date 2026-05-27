---
title: Job Market Pulse
emoji: 📊
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# 📊 Job Market Pulse

> *I tracked 10,000+ data job listings daily to find out what the market actually pays for data skills.*

**Live dashboard tracking demand, salaries, and remote trends across 10 tech stacks in the US job market — updated every morning.**

---

## What it tracks

| Dimension | Detail |
|-----------|--------|
| **Tech stacks** | Python · SQL · Tableau · Power BI · dbt · Spark · Airflow · Snowflake · AWS · Azure |
| **Cities** | New York · LA · Chicago · SF · Seattle · Austin · Boston · Denver · Atlanta · Dallas + Remote |
| **Metrics** | Job count · Demand score · Salary avg/min/max · Remote % · Salary disclosure rate |
| **Update frequency** | Daily at 7:00 AM PST via GitHub Actions |

---

## Dashboard sections

1. **KPI Row** — Top stack today · Highest paying · Most remote-friendly · Biggest weekly mover  
2. **Demand Ranking** — Normalized 0–100 score, not raw counts — stacks are comparable  
3. **Trend Over Time** — The main feature: history accumulates, gets more valuable monthly  
4. **Remote Friendliness** — Which skills travel best  
5. **Salary Intelligence** — Range + % of listings that actually disclose salary  
6. **City Heatmap** — 10 stacks × 10 cities: where each skill concentrates  

---

## Architecture

```
Adzuna API (110 calls/day)
    ↓
src/extract.py → src/transform.py → src/load.py
    ↓
DuckDB (job_market.duckdb) — stored on HuggingFace Dataset
    ↓
GitHub Actions (daily cron) → download DB → run → upload DB
    ↓
Streamlit dashboard on HuggingFace Spaces
```

**Key design choice:** DuckDB file lives on a HuggingFace Dataset repo, downloaded before each run and re-uploaded after — zero database hosting cost, full history preserved.

---

## Findings (Day 1 — May 26 2026)

| Stack | Total US Jobs | Avg Salary | Remote % |
|-------|-------------|------------|---------|
| Python | 27,718 | — | 31% |
| AWS | 21,959 | $187k | 13% |
| SQL | 19,443 | $142k | 25% |
| Azure | 13,401 | $150k | 21% |
| dbt | 1,712 | — | 12% |

*New York dominates every stack. Python + SQL are most remote-friendly.*

---

## Tech stack

`Python` · `DuckDB` · `Streamlit` · `Plotly` · `GitHub Actions` · `HuggingFace Spaces` · `Docker` · `Adzuna API`

---

*Data from [Adzuna](https://www.adzuna.com/) — updated daily. Salary data only where disclosed by employers.*

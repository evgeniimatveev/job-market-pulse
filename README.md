---
title: Job Market Pulse
emoji: 📊
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

![Job Market Pulse Banner](assets/banner.png)

## 🔴 Live Demo → [huggingface.co/spaces/evgeniimatveevusa/job-market-pulse](https://huggingface.co/spaces/evgeniimatveevusa/job-market-pulse)

---

## What it does

Pulls **110 API calls per day** from Adzuna, stores everything in DuckDB, and serves a Streamlit dashboard — fully automated, zero manual steps, $0 hosting cost.

> *"I tracked 10,000+ US tech job listings daily to find out what the market actually pays for data skills."*

---

## Dashboard

![Hero and KPIs](assets/hero_kpi.png)

![Demand Ranking](assets/demand_ranking.png)

<table>
<tr>
<td><img src="assets/remote.png"/></td>
<td><img src="assets/salary.png"/></td>
</tr>
</table>

![City Heatmap](assets/heatmap.png)

---

## What it tracks

| Dimension | Detail |
|-----------|--------|
| **Tech stacks** | Python · SQL · Tableau · Power BI · dbt · Spark · Airflow · Snowflake · AWS · Azure |
| **Cities** | New York · LA · Chicago · SF · Seattle · Austin · Boston · Denver · Atlanta · Dallas + Remote |
| **Metrics** | Job count · Demand score · Salary avg/min/max · Remote % · Salary disclosure rate |
| **Cadence** | Daily at 7:00 AM PST via GitHub Actions |

---

## Architecture

```
Adzuna API  ──►  extract.py  ──►  transform.py  ──►  load.py
                                                        │
                                                   DuckDB file
                                                        │
                          ┌─────────────────────────────┤
                          │                             │
                   HuggingFace Dataset           GitHub Actions
                   (persistent storage)          (daily cron)
                          │
                   HuggingFace Space
                   (Streamlit dashboard)
```

**Key design decision:** DuckDB file lives on a HuggingFace Dataset — downloaded before each run, updated after. Zero database hosting cost, full history preserved indefinitely.

---

## Demand Score formula

```
demand_score = (stack_count - min_count) / (max_count - min_count) × 100
```

Normalized per run so stacks are always comparable regardless of absolute count differences. Python = 100 baseline.

---

## Day 1 findings (May 26 2026)

| Rank | Stack | Jobs | Avg Salary | Remote % |
|------|-------|------|-----------|---------|
| #1 | Python | 27,764 | $137k | 31% |
| #2 | AWS | 21,999 | $187k | 13% |
| #3 | SQL | 19,472 | $142k | 25% |
| #4 | Azure | 13,424 | $150k | 21% |
| #10 | dbt | 1,712 | $128k | 12% |

*New York dominates every single stack. Python + SQL most remote-friendly. Airflow & dbt most niche.*

---

## Tech stack

`Python` · `DuckDB` · `Streamlit` · `Plotly` · `GitHub Actions` · `HuggingFace Spaces` · `Docker` · `Adzuna API`

---

*Data from [Adzuna](https://www.adzuna.com/) · Updated daily · Built by [Evgenii Matveev](https://github.com/evgeniimatveev)*

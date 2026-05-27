"""
Generate portfolio thumbnail — Bloomberg terminal / live market feed style.
Unique from: weather (KPI cards + bars), uber (radar chart).
Output: assets/portfolio_thumb.png  ~1400x560px
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

W, H = 1400, 560
fig = plt.figure(figsize=(W / 100, H / 100), dpi=100)
fig.patch.set_facecolor("#0f172a")
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
ax.set_facecolor("#0f172a")

STACK_COLORS = {
    "Python":   "#3776AB", "AWS":      "#FF9900", "SQL":      "#E38C00",
    "Azure":    "#0078D4", "Tableau":  "#E97627", "Spark":    "#E25A1C",
    "Power BI": "#F2C811", "Snowflake":"#29B5E8", "Airflow":  "#017CEE",
    "dbt":      "#FF694B",
}

# ── Top multi-color accent bar ────────────────────────────────────────────────
seg_w = W / 10
for i, c in enumerate(STACK_COLORS.values()):
    ax.add_patch(plt.Rectangle((i * seg_w, H - 5), seg_w, 5, color=c, zorder=5))

# ── LIVE indicator (top right) ────────────────────────────────────────────────
ax.add_patch(plt.Circle((W - 38, H - 22), 7, color="#22c55e", zorder=6))
ax.text(W - 24, H - 22, "LIVE", color="#22c55e", fontsize=10,
        fontweight="bold", fontfamily="monospace", va="center")

# ── Top bar: section headers ───────────────────────────────────────────────────
bar_y = H - 12
ax.text(16, bar_y, "JOB MARKET PULSE",
        color="#94a3b8", fontsize=9, fontfamily="monospace", va="center")
ax.text(500, bar_y, "US TECH HIRING INTELLIGENCE  |  10 stacks  11 cities  daily",
        color="#475569", fontsize=9, fontfamily="monospace", va="center")

# ═══════════════════════════════════════════════════════════════════════════════
# LEFT PANEL  x=0..340
# ═══════════════════════════════════════════════════════════════════════════════
lx = 28

# Cyan accent stripe
ax.add_patch(plt.Rectangle((lx, H - 120), 6, 92, color="#29B5E8"))

# Title
ax.text(lx + 18, H - 38, "JOB", color="#f8fafc",
        fontsize=38, fontweight="black", va="top")
ax.text(lx + 18, H - 82, "MARKET", color="#f8fafc",
        fontsize=38, fontweight="black", va="top")
ax.text(lx + 18, H - 126, "PULSE", color="#29B5E8",
        fontsize=38, fontweight="black", va="top")

# Tagline
ax.text(lx, H - 146,
        "Adzuna API  x  10 stacks  x  11 US cities",
        color="#64748b", fontsize=10.5, va="top", fontfamily="monospace")

# Divider
ax.plot([lx, 330], [H - 162, H - 162], color="#1e293b", linewidth=1)

# Big KPI stats
kpis = [
    ("110K+", "jobs tracked"),
    ("$187K", "peak avg salary"),
    ("31%",   "Python remote"),
    ("$0",    "hosting cost"),
]
ky = H - 180
for val, label in kpis:
    ax.text(lx, ky, val, color="#29B5E8", fontsize=22,
            fontweight="bold", va="top")
    ax.text(lx + 10, ky - 28, label, color="#475569",
            fontsize=10, va="top", fontfamily="monospace")
    ky -= 68

# Tech badges (2-row grid)
badges = [
    ("Python",     "#3776AB"), ("DuckDB",   "#FFCC00"),
    ("Streamlit",  "#FF4B4B"), ("GH Actions","#2EA043"),
    ("Docker",     "#2496ED"), ("Adzuna",   "#29B5E8"),
]
bx_start = lx
by_start = 28
for i, (label, color) in enumerate(badges):
    col = i % 3; row = i // 3
    bx2 = bx_start + col * 102
    by2 = by_start + row * 34
    ax.add_patch(FancyBboxPatch((bx2, by2 - 10), 94, 26,
        boxstyle="round,pad=3", linewidth=1.2,
        edgecolor=color, facecolor="#0f172a"))
    ax.text(bx2 + 47, by2 + 3, label, color=color,
            fontsize=9, fontweight="bold", ha="center", va="center")

# ── Vertical separator ─────────────────────────────────────────────────────────
sep_x = 342
ax.plot([sep_x, sep_x], [15, H - 18], color="#1e293b", linewidth=1.5)

# ═══════════════════════════════════════════════════════════════════════════════
# RIGHT PANEL — Market Ticker Board  x=358..1390
# ═══════════════════════════════════════════════════════════════════════════════
rx = 362

# Column headers
col_name   = rx + 10
col_bar    = rx + 130
col_salary = rx + 710
col_remote = rx + 820
col_jobs   = rx + 940
col_score  = rx + 1010

hdr_y = H - 22
ax.text(col_name,   hdr_y, "STACK",          color="#475569", fontsize=9, fontfamily="monospace", va="center")
ax.text(col_bar,    hdr_y, "DEMAND",         color="#475569", fontsize=9, fontfamily="monospace", va="center")
ax.text(col_salary, hdr_y, "AVG SAL",        color="#475569", fontsize=9, fontfamily="monospace", va="center")
ax.text(col_remote, hdr_y, "REMOTE",         color="#475569", fontsize=9, fontfamily="monospace", va="center")
ax.text(col_jobs,   hdr_y, "LISTINGS",       color="#475569", fontsize=9, fontfamily="monospace", va="center")
ax.text(col_score,  hdr_y, "SCORE",          color="#475569", fontsize=9, fontfamily="monospace", va="center")

# Header underline
ax.plot([rx, rx + 1028], [H - 30, H - 30], color="#1e293b", linewidth=1)

# Data rows
rows = [
    # name,    score, jobs,  salary, remote_pct
    ("Python",   100, 27764,  137,  31),
    ("AWS",       78, 21999,  187,  13),
    ("SQL",       68, 19472,  142,  25),
    ("Azure",     45, 13424,  150,  21),
    ("Tableau",   17,  6237,  135,  18),
    ("Spark",     17,  6196,  132,  15),
    ("Power BI",  12,  4813,  120,  22),
    ("Snowflake",  7,  3580,  154,  16),
    ("Airflow",    2,  1845,  159,  12),
    ("dbt",        2,  1712,  128,  12),
]

bar_max_px = 560
row_h = 46
top_y = H - 36

rank_colors = ["#F59E0B", "#9CA3AF", "#CD7F32"]  # gold, silver, bronze

for i, (name, score, jobs, salary, remote) in enumerate(rows):
    ry_center = top_y - i * row_h - row_h / 2
    color = STACK_COLORS[name]
    is_top3 = i < 3

    # Alternating row background
    bg_color = "#111827" if i % 2 == 0 else "#0f172a"
    ax.add_patch(plt.Rectangle((rx - 4, top_y - i * row_h - row_h + 2),
                               1035, row_h - 1,
                               color=bg_color, zorder=0))

    # Rank badge (top 3 get colored, rest grey)
    rank_col = rank_colors[i] if i < 3 else "#334155"
    ax.add_patch(FancyBboxPatch((col_name - 28, ry_center - 11), 22, 22,
        boxstyle="round,pad=2", linewidth=0,
        facecolor=rank_col, zorder=2))
    ax.text(col_name - 17, ry_center, f"{i+1}",
            color="#0f172a" if i < 3 else "#64748b",
            fontsize=9, fontweight="bold",
            ha="center", va="center", zorder=3)

    # Stack name
    ax.text(col_name, ry_center, name,
            color=color, fontsize=13 if is_top3 else 11,
            fontweight="bold" if is_top3 else "normal",
            va="center")

    # Demand bar — background track
    bar_h_px = 16 if is_top3 else 12
    bw = bar_max_px * score / 100
    bar_y_pos = ry_center - bar_h_px / 2
    ax.add_patch(plt.Rectangle((col_bar, bar_y_pos), bar_max_px, bar_h_px,
        color="#1e293b", zorder=1))
    # Fill
    ax.add_patch(plt.Rectangle((col_bar, bar_y_pos), bw, bar_h_px,
        color=color, alpha=0.9, zorder=2))
    # Score label inside bar
    if bw > 40:
        ax.text(col_bar + bw - 5, ry_center, f"{score}",
                color="#0f172a", fontsize=8, fontweight="bold",
                ha="right", va="center", zorder=3)

    # Salary
    sal_col = "#f8fafc" if is_top3 else "#64748b"
    ax.text(col_salary, ry_center, f"${salary}k",
            color=sal_col, fontsize=12 if is_top3 else 10,
            fontweight="bold" if is_top3 else "normal",
            fontfamily="monospace", va="center")

    # Remote % with mini color bar
    remote_bar_w = 70 * remote / 35  # max ~35%
    ax.add_patch(plt.Rectangle((col_remote, ry_center - 5), 70, 10,
        color="#1e293b", zorder=1))
    ax.add_patch(plt.Rectangle((col_remote, ry_center - 5), remote_bar_w, 10,
        color="#22c55e", alpha=0.7, zorder=2))
    ax.text(col_remote + 78, ry_center, f"{remote}%",
            color="#22c55e" if remote >= 25 else "#64748b",
            fontsize=10, fontfamily="monospace", va="center")

    # Listings count
    ax.text(col_jobs, ry_center, f"{jobs:,}",
            color=sal_col, fontsize=10 if is_top3 else 9,
            fontfamily="monospace", va="center")

    # Demand score
    ax.text(col_score, ry_center, f"{score}/100",
            color=color if is_top3 else "#475569",
            fontsize=10, fontfamily="monospace",
            fontweight="bold" if is_top3 else "normal",
            va="center")

    # Row bottom divider
    ax.plot([rx - 4, rx + 1032],
            [top_y - i * row_h - row_h + 1, top_y - i * row_h - row_h + 1],
            color="#1e293b", linewidth=0.5)

# Bottom footer
ax.text(rx, 10,
        "Data: Adzuna API  *  Normalized demand score: (stack - min) / (max - min) x 100  *  Updated daily 07:00 AM PST",
        color="#334155", fontsize=8.5, fontfamily="monospace", va="bottom")

# ── Save ───────────────────────────────────────────────────────────────────────
out = "assets/portfolio_thumb.png"
plt.savefig(out, dpi=100, bbox_inches="tight",
            facecolor="#0f172a", pad_inches=0)
plt.close()
print("Portfolio thumbnail saved to", out)

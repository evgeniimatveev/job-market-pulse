"""Generate README banner — leaderboard/scoreboard style, unique from weather pipeline."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

W, H = 1500, 560
fig = plt.figure(figsize=(W/100, H/100), dpi=100)
fig.patch.set_facecolor("#0d1117")
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
ax.set_facecolor("#0d1117")

STACK_COLORS = {
    "Python": "#3776AB", "AWS": "#FF9900", "SQL": "#E38C00",
    "Azure": "#0078D4", "Tableau": "#E97627", "Spark": "#E25A1C",
    "Power BI": "#F2C811", "Snowflake": "#29B5E8",
    "Airflow": "#017CEE", "dbt": "#FF694B",
}

# ── Top accent bar — gradient of all stack colors ─────────────────────────────
seg_w = W / 10
for i, c in enumerate(STACK_COLORS.values()):
    ax.add_patch(plt.Rectangle((i * seg_w, H - 6), seg_w, 6, color=c))

# ═══════════════════════════════════════════════════════════════════════════════
# LEFT PANEL  (x=0..520)
# ═══════════════════════════════════════════════════════════════════════════════
lx = 40

# Icon + project name
# Accent box instead of emoji
ax.add_patch(FancyBboxPatch((lx, H - 68), 8, 52,
    boxstyle="square,pad=0", linewidth=0, facecolor="#29B5E8"))
ax.text(lx + 18, H - 30, "JOB MARKET", color="#ffffff",
        fontsize=36, fontweight="black", va="top", linespacing=0.9)
ax.text(lx + 18, H - 72, "PULSE",
        color="#29B5E8", fontsize=36, fontweight="black", va="top")

# Tagline
ax.text(lx, H - 118,
        '"I tracked 10,000+ US tech job listings daily\n to find out what the market really pays."',
        color="#8b949e", fontsize=12, va="top", style="italic", linespacing=1.6)

# Vertical divider
ax.plot([lx, lx + 460], [H - 165, H - 165], color="#21262d", linewidth=1)

# Stats row — 4 pill-style stats
stats = [("10", "stacks"), ("11", "cities"), ("Daily", "updates"), ("$0", "hosting")]
pill_x = lx
for val, label in stats:
    ax.add_patch(FancyBboxPatch((pill_x, H - 215), 100, 42,
        boxstyle="round,pad=4", linewidth=1,
        edgecolor="#21262d", facecolor="#161b22"))
    ax.text(pill_x + 50, H - 186, val,
            color="#29B5E8", fontsize=15, fontweight="bold",
            ha="center", va="top")
    ax.text(pill_x + 50, H - 208, label,
            color="#484f58", fontsize=9, ha="center", va="top")
    pill_x += 112

ax.plot([lx, lx + 460], [H - 222, H - 222], color="#21262d", linewidth=1)

# Description block
desc_lines = [
    "Adzuna API  →  110 calls / day",
    "DuckDB  ·  history accumulates daily",
    "Streamlit dashboard on HuggingFace",
    "GitHub Actions  ·  runs every morning",
]
for i, line in enumerate(desc_lines):
    ax.text(lx, H - 248 - i * 22, line,
            color="#6e7681", fontsize=11, va="top", fontfamily="monospace")

# Tech badges — bottom of left panel
badges = [
    ("Python",   "#3776AB"), ("DuckDB",     "#FFCC00"),
    ("Streamlit","#FF4B4B"), ("GH Actions", "#2EA043"),
    ("Docker",   "#2496ED"), ("Adzuna API", "#29B5E8"),
]
bx, by = lx, 62
for i, (label, color) in enumerate(badges):
    col = i % 3; row = i // 3
    bx2 = lx + col * 150
    by2 = by + row * 36
    ax.add_patch(FancyBboxPatch((bx2, by2 - 12), 138, 28,
        boxstyle="round,pad=3", linewidth=1.2,
        edgecolor=color, facecolor="#0d1117"))
    ax.text(bx2 + 69, by2 + 2, label,
            color=color, fontsize=10, fontweight="bold",
            ha="center", va="center")

# ── Vertical separator line ───────────────────────────────────────────────────
sep_x = 530
ax.plot([sep_x, sep_x], [30, H - 20], color="#21262d", linewidth=1.5)

# ═══════════════════════════════════════════════════════════════════════════════
# RIGHT PANEL — Leaderboard  (x=550..1480)
# ═══════════════════════════════════════════════════════════════════════════════
rx = 555

# Header
ax.text(rx, H - 28, "DEMAND LEADERBOARD",
        color="#3fb950", fontsize=11, fontweight="bold",
        fontfamily="monospace", va="top")
ax.text(rx + 370, H - 28, "avg salary",
        color="#484f58", fontsize=10, fontfamily="monospace", va="top")
ax.text(rx + 510, H - 28, "listings",
        color="#484f58", fontsize=10, fontfamily="monospace", va="top")

ax.plot([rx, 1470], [H - 42, H - 42], color="#21262d", linewidth=1)

# Leaderboard data
rows = [
    ("Python",   100, 27764, 137),
    ("AWS",       78, 21999, 187),
    ("SQL",       68, 19472, 142),
    ("Azure",     45, 13424, 150),
    ("Tableau",   17,  6237, 135),
    ("Spark",     17,  6196, 132),
    ("Power BI",  12,  4813, 120),
    ("Snowflake",  7,  3580, 154),
    ("Airflow",    2,  1845, 159),
    ("dbt",        2,  1712, 128),
]

bar_max = 820
row_h = 46
top_y = H - 52

rank_colors = ["#F2C811", "#8b949e", "#E97627"]  # gold, silver, bronze

for i, (name, score, jobs, salary) in enumerate(rows):
    ry = top_y - i * row_h
    color = STACK_COLORS[name]
    is_top3 = i < 3

    # Row background (alternating)
    if i % 2 == 0:
        ax.add_patch(plt.Rectangle((rx - 4, ry - row_h + 6), 924, row_h - 2,
            color="#0d1117", zorder=0))

    # Rank number
    rank_col = rank_colors[i] if i < 3 else "#484f58"
    ax.text(rx + 14, ry - row_h/2 + 5, f"#{i+1}",
            color=rank_col, fontsize=13 if is_top3 else 11,
            fontweight="bold" if is_top3 else "normal",
            fontfamily="monospace", ha="center", va="center")

    # Stack name
    ax.text(rx + 44, ry - row_h/2 + 5, name,
            color=color, fontsize=13 if is_top3 else 11,
            fontweight="bold" if is_top3 else "normal",
            va="center")

    # Bar
    bar_x = rx + 150
    bar_y = ry - row_h + 14
    bar_h_px = 18 if is_top3 else 14
    bw = bar_max * score / 100

    # Background track
    ax.add_patch(plt.Rectangle((bar_x, bar_y), bar_max, bar_h_px,
        color="#161b22", zorder=1))
    # Fill
    ax.add_patch(plt.Rectangle((bar_x, bar_y), bw, bar_h_px,
        color=color, alpha=0.85, zorder=2))
    # Score label on bar
    if bw > 60:
        ax.text(bar_x + bw - 8, bar_y + bar_h_px/2, f"{score}",
                color="#0d1117", fontsize=9, fontweight="bold",
                ha="right", va="center", zorder=3)

    # Salary
    ax.text(rx + 380, ry - row_h/2 + 5, f"${salary}k",
            color="#e6edf3" if is_top3 else "#6e7681",
            fontsize=12 if is_top3 else 10,
            fontweight="bold" if is_top3 else "normal",
            fontfamily="monospace", va="center")

    # Job count
    ax.text(rx + 520, ry - row_h/2 + 5, f"{jobs:,}",
            color="#e6edf3" if is_top3 else "#6e7681",
            fontsize=12 if is_top3 else 10,
            fontfamily="monospace", va="center")

    # Row divider
    ax.plot([rx - 4, rx + 928], [ry - row_h + 5, ry - row_h + 5],
            color="#21262d", linewidth=0.5)

# Bottom note
ax.text(rx, 12,
        "Normalized 0-100  *  Python = baseline  *  Updated daily 07:00 AM PST via GitHub Actions",
        color="#484f58", fontsize=9, fontfamily="monospace", va="bottom")

# ── Save ──────────────────────────────────────────────────────────────────────
out = "assets/banner.png"
plt.savefig(out, dpi=100, bbox_inches="tight",
            facecolor="#0d1117", pad_inches=0)
plt.close()
print("Banner saved to", out)

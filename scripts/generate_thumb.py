"""
Portfolio thumbnail — PULSE MONITOR design.
Heartbeat waveform with 10 stack colors. No numbers, no axes.
Unique vs: weather (bars), uber (radar), olist (line chart).
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

W, H = 1280, 640
fig = plt.figure(figsize=(W / 100, H / 100), dpi=100)
fig.patch.set_facecolor("#060d1a")
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
ax.set_facecolor("#060d1a")

# Stack data: color, demand score (controls peak height)
STACKS = [
    ("Python",    "#3776AB", 100),
    ("AWS",       "#FF9900",  78),
    ("SQL",       "#E38C00",  68),
    ("Azure",     "#0078D4",  45),
    ("Tableau",   "#E97627",  17),
    ("Spark",     "#E25A1C",  17),
    ("Power BI",  "#F2C811",  12),
    ("Snowflake", "#29B5E8",   7),
    ("Airflow",   "#017CEE",   2),
    ("dbt",       "#FF694B",   2),
]

# ── Subtle scanline texture ───────────────────────────────────────────────────
for y in range(0, H, 4):
    ax.plot([0, W], [y, y], color="#ffffff", linewidth=0.3, alpha=0.018)

# ── TOP: project title ────────────────────────────────────────────────────────
# Cyan accent bar at very top
ax.add_patch(plt.Rectangle((0, H - 5), W, 5, color="#29B5E8"))

# Corner label
ax.text(28, H - 22, "JOB MARKET PULSE",
        color="#29B5E8", fontsize=13, fontweight="bold",
        fontfamily="monospace", va="center")
ax.text(W - 28, H - 22, "LIVE  ●",
        color="#22c55e", fontsize=11, fontweight="bold",
        fontfamily="monospace", va="center", ha="right")

# Horizontal rule below header
ax.plot([0, W], [H - 34, H - 34], color="#0f2040", linewidth=1.5)

# ── CENTER: big title block ───────────────────────────────────────────────────
cy = H * 0.72
ax.text(W / 2, cy + 28, "JOB MARKET",
        color="#f0f6ff", fontsize=68, fontweight="black",
        ha="center", va="center", alpha=0.95)
ax.text(W / 2, cy - 44, "PULSE",
        color="#29B5E8", fontsize=68, fontweight="black",
        ha="center", va="center", alpha=0.97)

# Tagline
ax.text(W / 2, cy - 92,
        "10 tech stacks  ·  11 US cities  ·  daily automated refresh",
        color="#334155", fontsize=12, ha="center", va="center",
        fontfamily="monospace")

# ── WAVEFORM: full-width EKG-style pulse ──────────────────────────────────────
baseline_y = H * 0.24
waveform_h = H * 0.19   # max peak height

x = np.linspace(0, W, 4000)

# Each stack has a Gaussian peak; space evenly across width
centers = np.linspace(80, W - 80, len(STACKS))
sigma = 48

# Thin baseline
ax.plot([0, W], [baseline_y, baseline_y], color="#0a2040", linewidth=1.2, zorder=1)

for i, ((name, color, score), cx) in enumerate(zip(STACKS, centers)):
    peak_height = waveform_h * score / 100
    bump = peak_height * np.exp(-0.5 * ((x - cx) / sigma) ** 2)

    # Glow layers (outer → inner)
    for lw, alpha in [(20, 0.04), (12, 0.09), (6, 0.20), (2.5, 0.75), (1.2, 1.0)]:
        ax.plot(x, baseline_y + bump, color=color,
                linewidth=lw, alpha=alpha, zorder=2, solid_capstyle="round")

    # Filled area under peak (soft glow below)
    ax.fill_between(x, baseline_y, baseline_y + bump,
                    color=color, alpha=0.06, zorder=1)

    # Stack color dot on baseline
    ax.plot(cx, baseline_y, "o", color=color, markersize=5, zorder=4, alpha=0.7)

# Flatline segments between peaks (connect baseline dots)
ax.plot([0, centers[0] - sigma * 2], [baseline_y, baseline_y],
        color="#1a4060", linewidth=1, zorder=1)
ax.plot([centers[-1] + sigma * 2, W], [baseline_y, baseline_y],
        color="#1a4060", linewidth=1, zorder=1)

# ── BOTTOM: stack color strip ─────────────────────────────────────────────────
strip_y = 14
strip_h = 18
seg_w = W / len(STACKS)
for i, (_, color, _) in enumerate(STACKS):
    # Badge-style rounded strip
    ax.add_patch(plt.Rectangle((i * seg_w + 2, strip_y), seg_w - 4, strip_h,
        color=color, alpha=0.75))

# ── Save ──────────────────────────────────────────────────────────────────────
out = "assets/portfolio_thumb.png"
plt.savefig(out, dpi=100, bbox_inches="tight",
            facecolor="#060d1a", pad_inches=0)
plt.close()
print("Saved:", out)

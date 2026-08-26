#!/usr/bin/env python3
"""E7 DHT vs ECO comparison charts — Merit brand."""
import os, sys, datetime as dt
BASE = "/tmp/claude-0/-home-user-stock-visualizer/83d1a957-9071-5bce-8533-fee1b20429a3/scratchpad"
sys.path.insert(0, BASE)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.font_manager as fm
for f in os.listdir(os.path.join(BASE, "fonts")):
    try: fm.fontManager.addfont(os.path.join(BASE, "fonts", f))
    except Exception: pass
from dht_data import PEERS_1Y, DHT_1Y_WEEKLY, PEER_WEEKS_START

ROYAL, MIDNIGHT, RED, ORANGE, BLUE_GREY, COOL_GREY, LIGHT_GREY = "#0001FF", "#000041", "#B9444A", "#D46B2A", "#3B4557", "#9AA2A5", "#DDDDDD"
matplotlib.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Noto Sans", "DejaVu Sans", "Arial"],
    "axes.edgecolor": BLUE_GREY, "axes.labelcolor": MIDNIGHT, "axes.titlecolor": MIDNIGHT,
    "axes.titleweight": "bold", "xtick.color": BLUE_GREY, "ytick.color": BLUE_GREY,
    "grid.color": LIGHT_GREY, "grid.linewidth": 0.6, "axes.grid": True, "axes.axisbelow": True,
    "figure.facecolor": "white", "axes.facecolor": "white", "legend.frameon": False,
})

dates = [dt.date.fromisoformat(PEER_WEEKS_START) + dt.timedelta(weeks=i) for i in range(len(DHT_1Y_WEEKLY))]
dht_idx = [v / DHT_1Y_WEEKLY[0] * 100 for v in DHT_1Y_WEEKLY]
eco = PEERS_1Y["ECO"]
eco_idx = [v / eco[0] * 100 for v in eco]

# Quarterly dividend yield on current price (last 8 quarters)
qlabels = ["Q3'24", "Q4'24", "Q1'25", "Q2'25", "Q3'25", "Q4'25", "Q1'26", "Q2'26"]
dht_dps = [0.22, 0.17, 0.15, 0.24, 0.18, 0.41, 0.64, 1.22]
eco_dps = [0.45, 0.35, 0.32, 0.70, 0.75, 1.55, 2.00, 5.25]
DHT_PX, ECO_PX = 19.25, 62.60
dht_y = [d / DHT_PX * 100 for d in dht_dps]
eco_y = [d / ECO_PX * 100 for d in eco_dps]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.8, 3.8))
ax1.plot(dates, dht_idx, color=ROYAL, lw=2.2, label=f"DHT ({dht_idx[-1]-100:+.0f}%)")
ax1.plot(dates, eco_idx, color=RED, lw=1.6, label=f"ECO ({eco_idx[-1]-100:+.0f}%)")
ax1.set_title("Σχετική απόδοση 12μήνου (βάση=100)", fontsize=11, pad=8)
ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax1.xaxis.set_major_formatter(mdates.DateFormatter("%m/%y"))
ax1.legend(loc="upper left", fontsize=9)

x = range(len(qlabels))
w = 0.38
ax2.bar([i - w/2 for i in x], dht_y, width=w, color=ROYAL, label="DHT")
ax2.bar([i + w/2 for i in x], eco_y, width=w, color=RED, label="ECO")
ax2.set_xticks(list(x)); ax2.set_xticklabels(qlabels, fontsize=8.5)
ax2.set_title("Τριμηνιαίο μέρισμα ως % τρέχουσας τιμής", fontsize=11, pad=8)
ax2.set_ylabel("%")
for i, v in enumerate(dht_y):
    if v > 2: ax2.text(i - w/2, v + 0.12, f"{v:.1f}", ha="center", fontsize=7.5, color=MIDNIGHT, fontweight="bold")
for i, v in enumerate(eco_y):
    if v > 2: ax2.text(i + w/2, v + 0.12, f"{v:.1f}", ha="center", fontsize=7.5, color=RED, fontweight="bold")
ax2.legend(loc="upper left", fontsize=9)
fig.text(0.01, 0.006, "Data as of 26/08/2026 · Πηγή: Interactive Brokers (τιμές, μερίσματα) · DHT 19,25 USD, ECO 62,60 USD", fontsize=7.5, color=COOL_GREY)
fig.tight_layout(rect=(0, 0.045, 1, 1))
out = os.path.join(BASE, "report", "chart_e7.png")
fig.savefig(out, dpi=170)
print("written", out)

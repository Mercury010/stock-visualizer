#!/usr/bin/env python3
"""Peer relative performance chart (indexed 1Y) — Merit brand."""
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

ROYAL, MIDNIGHT, RED = "#0001FF", "#000041", "#B9444A"
ORANGE, VIOLET, BLUE_GREY, COOL_GREY, LIGHT_GREY = "#D46B2A", "#544D84", "#3B4557", "#9AA2A5", "#DDDDDD"
matplotlib.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Noto Sans", "DejaVu Sans", "Arial"],
    "axes.edgecolor": BLUE_GREY, "axes.labelcolor": MIDNIGHT,
    "axes.titlecolor": MIDNIGHT, "axes.titleweight": "bold",
    "xtick.color": BLUE_GREY, "ytick.color": BLUE_GREY,
    "grid.color": LIGHT_GREY, "grid.linewidth": 0.6,
    "axes.grid": True, "axes.axisbelow": True,
    "figure.facecolor": "white", "axes.facecolor": "white",
    "legend.frameon": False,
})
dates = [dt.date.fromisoformat(PEER_WEEKS_START) + dt.timedelta(weeks=i) for i in range(len(DHT_1Y_WEEKLY))]
series = {"DHT": DHT_1Y_WEEKLY, **PEERS_1Y}
styles = {"DHT": (ROYAL, 2.4), "FRO": (RED, 1.2), "INSW": (ORANGE, 1.2), "TNK": (VIOLET, 1.2), "ECO": (COOL_GREY, 1.2)}
fig, ax = plt.subplots(figsize=(9.6, 4.4))
for name, vals in series.items():
    idx = [v / vals[0] * 100 for v in vals]
    c, lw = styles[name]
    ax.plot(dates, idx, color=c, lw=lw, label=f"{name} ({idx[-1]-100:+.0f}%)")
ax.set_title("Σχετική απόδοση 12 μηνών — DHT έναντι peers (βάση=100)", fontsize=12, pad=10)
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%y"))
ax.legend(loc="upper left", fontsize=9, ncols=2)
ax.axhline(100, color=LIGHT_GREY, lw=0.8)
fig.text(0.01, 0.005, "Data as of 25/08/2026 · Πηγή: Interactive Brokers", fontsize=8, color=COOL_GREY)
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig(os.path.join(BASE, "charts", "chart_peers.png"), dpi=170)
print("ok")

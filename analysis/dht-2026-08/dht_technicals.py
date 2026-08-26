#!/usr/bin/env python3
"""DHT Holdings — technical indicators + Merit-branded chart pack.

Cells:
  1. Configuration
  2. Load IBKR data
  3. Indicators (SMA, RSI, MACD, drawdown, performance)
  4. Charts (5Y weekly, 1Y daily + volume, dividend history)
"""

# ── 1. Configuration ────────────────────────────────────────────────
import os
import sys

BASE = "/tmp/claude-0/-home-user-stock-visualizer/83d1a957-9071-5bce-8533-fee1b20429a3/scratchpad"
OUT_DIR = os.path.join(BASE, "charts")
FONT_DIR = os.path.join(BASE, "fonts")
DPI = 170

sys.path.insert(0, BASE)
os.makedirs(OUT_DIR, exist_ok=True)

# ── 2. Load data ────────────────────────────────────────────────────
import datetime as dt

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from cycler import cycler

from dht_data import (SNAPSHOT, DIVIDENDS, WEEKLY_START, WEEKLY_CLOSE,
                      DAILY_DATES, DAILY_CLOSE, DAILY_VOLUME)

# Merit brand kit (merit-report-design §5)
for f in os.listdir(FONT_DIR):
    try:
        fm.fontManager.addfont(os.path.join(FONT_DIR, f))
    except Exception as exc:
        print("font skip:", f, exc)

ROYAL, MIDNIGHT, RED = "#0001FF", "#000041", "#B9444A"
ORANGE, BLUE_GREY, COOL_GREY, LIGHT_GREY = "#D46B2A", "#3B4557", "#9AA2A5", "#DDDDDD"
matplotlib.rcParams.update({
    "axes.prop_cycle": cycler(color=[ROYAL, RED, ORANGE, "#544D84", BLUE_GREY, COOL_GREY]),
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

weekly_dates = [dt.date.fromisoformat(WEEKLY_START) + dt.timedelta(weeks=i)
                for i in range(len(WEEKLY_CLOSE))]
daily_dates = [dt.date.fromisoformat(d) for d in DAILY_DATES]
close = DAILY_CLOSE

# ── 3. Indicators ───────────────────────────────────────────────────
def sma(series, n):
    out = [None] * len(series)
    for i in range(n - 1, len(series)):
        out[i] = sum(series[i - n + 1:i + 1]) / n
    return out

def rsi14(series, n=14):
    gains, losses = [], []
    for i in range(1, len(series)):
        ch = series[i] - series[i - 1]
        gains.append(max(ch, 0)); losses.append(max(-ch, 0))
    if len(gains) < n:
        return None
    ag, al = sum(gains[:n]) / n, sum(losses[:n]) / n
    for i in range(n, len(gains)):
        ag = (ag * (n - 1) + gains[i]) / n
        al = (al * (n - 1) + losses[i]) / n
    return 100.0 if al == 0 else 100 - 100 / (1 + ag / al)

def ema_series(series, n):
    k = 2 / (n + 1)
    out = [series[0]]
    for x in series[1:]:
        out.append(out[-1] + k * (x - out[-1]))
    return out

sma20, sma50, sma200 = sma(close, 20), sma(close, 50), sma(close, 200)
rsi = rsi14(close)
ema12, ema26 = ema_series(close, 12), ema_series(close, 26)
macd_line = [a - b for a, b in zip(ema12, ema26)]
signal = ema_series(macd_line, 9)
macd_now, signal_now = macd_line[-1], signal[-1]

peak, mdd = close[0], 0.0
for px in close:
    peak = max(peak, px)
    mdd = min(mdd, px / peak - 1)

ttm_div = sum(d[2] for d in DIVIDENDS[-4:])
last = close[-1]
perf = {
    "last_close": last,
    "sma20": round(sma20[-1], 2), "sma50": round(sma50[-1], 2), "sma200": round(sma200[-1], 2),
    "vs_sma20_pct": round((last / sma20[-1] - 1) * 100, 1),
    "vs_sma50_pct": round((last / sma50[-1] - 1) * 100, 1),
    "vs_sma200_pct": round((last / sma200[-1] - 1) * 100, 1),
    "rsi14": round(rsi, 1),
    "macd": round(macd_now, 3), "macd_signal": round(signal_now, 3),
    "macd_state": "bullish" if macd_now > signal_now else "bearish",
    "ret_1m_pct": round((last / close[-22] - 1) * 100, 1),
    "ret_3m_pct": round((last / close[-64] - 1) * 100, 1),
    "ret_6m_pct": round((last / close[-127] - 1) * 100, 1),
    "ret_12m_pct": round((last / close[0] - 1) * 100, 1),
    "ret_5y_pct": round((last / WEEKLY_CLOSE[0] - 1) * 100, 1),
    "max_dd_1y_pct": round(mdd * 100, 1),
    "ttm_dividend": round(ttm_div, 2),
    "ttm_yield_pct": round(ttm_div / last * 100, 1),
}
print("TECHNICALS:", perf)

AS_OF = "Data as of 25/08/2026 · Πηγή: Interactive Brokers"

def stamp(ax_or_fig, x=0.01, y=0.005):
    fig = ax_or_fig if isinstance(ax_or_fig, plt.Figure) else ax_or_fig.figure
    fig.text(x, y, AS_OF, fontsize=8, color=COOL_GREY)

# ── 4. Charts ───────────────────────────────────────────────────────
# 4.1 — 5Y weekly
fig, ax = plt.subplots(figsize=(9.6, 3.9))
ax.plot(weekly_dates, WEEKLY_CLOSE, color=ROYAL, lw=1.6)
ax.fill_between(weekly_dates, WEEKLY_CLOSE, min(WEEKLY_CLOSE) * 0.95,
                color=ROYAL, alpha=0.06)
ax.set_title("DHT — Τιμή μετοχής 5 ετών (εβδομαδιαία, NYSE)", fontsize=12, pad=10)
ax.set_ylabel("USD")
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.set_xlim(weekly_dates[0], weekly_dates[-1])
ax.annotate(f"${last:.2f}", xy=(weekly_dates[-1], WEEKLY_CLOSE[-1]),
            xytext=(-58, 12), textcoords="offset points",
            fontsize=10, fontweight="bold", color=MIDNIGHT)
stamp(fig)
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig(os.path.join(OUT_DIR, "chart_5y.png"), dpi=DPI)
plt.close(fig)

# 4.2 — 1Y daily with SMAs + volume
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9.6, 5.2), sharex=True,
                               gridspec_kw={"height_ratios": [3.2, 1]})
ax1.plot(daily_dates, close, color=ROYAL, lw=1.5, label="DHT")
ax1.plot(daily_dates, sma50, color=ORANGE, lw=1.1, label="SMA50")
ax1.plot(daily_dates, sma200, color=BLUE_GREY, lw=1.1, label="SMA200")
ax1.set_title("DHT — 12 μήνες: τιμή, κινητοί μέσοι, όγκος", fontsize=12, pad=10)
ax1.set_ylabel("USD")
ax1.legend(loc="upper left", fontsize=9)
vol_colors = [ROYAL if (i == 0 or close[i] >= close[i - 1]) else RED
              for i in range(len(close))]
ax2.bar(daily_dates, [v / 1e6 for v in DAILY_VOLUME], color=vol_colors,
        width=1.0, alpha=0.65)
ax2.set_ylabel("Όγκος (εκ.)")
ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
ax2.xaxis.set_major_formatter(mdates.DateFormatter("%m/%y"))
stamp(fig)
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig(os.path.join(OUT_DIR, "chart_1y.png"), dpi=DPI)
plt.close(fig)

# 4.3 — dividend history (quarterly DPS)
fig, ax = plt.subplots(figsize=(9.6, 3.7))
labels = [d[3] for d in DIVIDENDS]
vals = [d[2] for d in DIVIDENDS]
bars = ax.bar(range(len(vals)), vals, color=ROYAL, width=0.62)
bars[-1].set_color(ORANGE)  # highlight latest quarter
ax.set_xticks(range(len(vals)))
ax.set_xticklabels([l.replace(" 20", "'") for l in labels], rotation=45,
                   ha="right", fontsize=8)
ax.set_title("DHT — Τριμηνιαίο μέρισμα ανά μετοχή (USD)", fontsize=12, pad=10)
for i, v in enumerate(vals):
    if v >= 0.15:
        ax.text(i, v + 0.015, f"{v:.2f}", ha="center", fontsize=7.5,
                color=MIDNIGHT, fontweight="bold")
ax.set_ylim(0, max(vals) * 1.18)
stamp(fig)
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig(os.path.join(OUT_DIR, "chart_div.png"), dpi=DPI)
plt.close(fig)

print("Charts written to", OUT_DIR)

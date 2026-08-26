#!/usr/bin/env python3
"""E6 options overlay computations + payoff chart (DHT, 26/08/2026)."""
import os, math
BASE = "/tmp/claude-0/-home-user-stock-visualizer/83d1a957-9071-5bce-8533-fee1b20429a3/scratchpad"

S = 18.70
R = 0.04
DIV_EST = 1.10   # est. Q3 dividend ex ~mid-Nov (C. estimate from bookings)
DIV_LOW = 0.85   # options-implied

def N(x): return 0.5 * (1 + math.erf(x / math.sqrt(2)))

def bs(F, K, sigma, T, cp):
    d1 = (math.log(F/K) + 0.5*sigma*sigma*T) / (sigma*math.sqrt(T))
    d2 = d1 - sigma*math.sqrt(T)
    df = math.exp(-R*T)
    if cp == 'C':
        px = df*(F*N(d1) - K*N(d2)); delta = df*N(d1)
    else:
        px = df*(K*N(-d2) - F*N(-d1)); delta = -df*N(-d1)
    theta_yr = None
    return px, delta, d1

# Forwards net of expected dividends
T_sep, T_dec, T_jan = 23/365, 114/365, 142/365
F_sep = S*math.exp(R*T_sep)                    # no div before Sep expiry
F_dec = S*math.exp(R*T_dec) - DIV_EST*math.exp(R*(T_dec-80/365))
F_jan = S*math.exp(R*T_jan) - DIV_EST*math.exp(R*(T_jan-80/365))
print(f"Forwards: Sep {F_sep:.2f}, Dec {F_dec:.2f} (div est {DIV_EST}), Jan {F_jan:.2f}")
F_dec_low = S*math.exp(R*T_dec) - DIV_LOW
print(f"Dec forward with implied div {DIV_LOW}: {F_dec_low:.2f}")

# Deltas at quoted IVs
rows = [
    ("Sep 17P", F_sep, 17, 0.434, T_sep, 'P'),
    ("Sep 18P", F_sep, 18, 0.412, T_sep, 'P'),
    ("Sep 20C", F_sep, 20, 0.398, T_sep, 'C'),
    ("Sep 21C", F_sep, 21, 0.442, T_sep, 'C'),
    ("Dec 15P", F_dec, 15, 0.460, T_dec, 'P'),
    ("Dec 16P", F_dec, 16, 0.445, T_dec, 'P'),
    ("Dec 17P", F_dec, 17, 0.438, T_dec, 'P'),
    ("Dec 18P", F_dec, 18, 0.423, T_dec, 'P'),
    ("Dec 20C", F_dec, 20, 0.421, T_dec, 'C'),
    ("Dec 21C", F_dec, 21, 0.418, T_dec, 'C'),
    ("Dec 22C", F_dec, 22, 0.431, T_dec, 'C'),
    ("Jan 17P", F_jan, 17, 0.431, T_jan, 'P'),
    ("Jan 20C", F_jan, 20, 0.415, T_jan, 'C'),
    ("Jan 22C", F_jan, 22, 0.413, T_jan, 'C'),
]
print("\nContract  modelPx  delta")
for name, F, K, iv, T, cp in rows:
    px, d, _ = bs(F, K, iv, T, cp)
    print(f"{name}: {px:5.2f}  {d:+.2f}")

# Strategy P&L at Dec expiry (per share, incl. DIV_EST received by stockholders before expiry)
prices = [13, 14, 15, 16, 17, 18, 18.70, 20, 21, 22, 24]
strat = {}
strat["Stock"] = [p - S + DIV_EST for p in prices]
strat["Stock+17P (ask 1,35)"] = [p - S + DIV_EST - 1.35 + max(17-p, 0) for p in prices]
strat["Collar 17P/20C (net -0,45)"] = [min(p, 20) - S + DIV_EST - 1.35 + 0.90 + max(17-p, 0) for p in prices]
strat["CSP 18P (bid 1,60)"] = [1.60 - max(18-p, 0) for p in prices]
strat["CC 21C (bid 0,65)"] = [min(p, 21) - S + DIV_EST + 0.65 for p in prices]
print("\nP&L per share at Dec expiry (incl. div est $1.10):")
print("Price:   " + "  ".join(f"{p:6.2f}" for p in prices))
for k, v in strat.items():
    print(f"{k:28s}" + "  ".join(f"{x:+6.2f}" for x in v))

# CSP yields
print("\nCSP: Dec 17P bid 1.15 -> yield on cash 1.15/17 = {:.1%} /114d = {:.0%} ann., BE {:.2f} (-{:.0%} vs spot)".format(1.15/17, (1.15/17)*365/114, 17-1.15, 1-(17-1.15)/S))
print("CSP: Dec 18P bid 1.60 -> {:.1%}/114d = {:.0%} ann., BE {:.2f} (-{:.0%})".format(1.60/18, (1.60/18)*365/114, 18-1.60, 1-(18-1.60)/S))
print("CSP: Sep 18P bid 0.40 -> {:.1%}/23d = {:.0%} ann., BE {:.2f}".format(0.40/18, (0.40/18)*365/23, 18-0.40))

# Covered call yields
print("\nCC Sep 20C bid 0.25: {:.2%}/23d = {:.0%} ann.; cap at 20 (+7.0%)".format(0.25/S, (0.25/S)*365/23))
print("CC Dec 21C bid 0.65: {:.2%}/114d = {:.0%} ann.; cap at 21 (+12.3%) + div".format(0.65/S, (0.65/S)*365/114))

# Strangle
cost = 0.95 + 0.85
print(f"\nStrangle Dec 16P/21C ask: {cost:.2f} ({cost/S:.1%} of spot), BE {16-cost:.2f} / {21+cost:.2f}")

# ── Payoff chart ──
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
for f in os.listdir(os.path.join(BASE, "fonts")):
    try: fm.fontManager.addfont(os.path.join(BASE, "fonts", f))
    except Exception: pass
ROYAL, MIDNIGHT, RED, ORANGE, VIOLET, BLUE_GREY, COOL_GREY, LIGHT_GREY = "#0001FF", "#000041", "#B9444A", "#D46B2A", "#544D84", "#3B4557", "#9AA2A5", "#DDDDDD"
matplotlib.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Noto Sans", "DejaVu Sans", "Arial"],
    "axes.edgecolor": BLUE_GREY, "axes.labelcolor": MIDNIGHT, "axes.titlecolor": MIDNIGHT,
    "axes.titleweight": "bold", "xtick.color": BLUE_GREY, "ytick.color": BLUE_GREY,
    "grid.color": LIGHT_GREY, "grid.linewidth": 0.6, "axes.grid": True, "axes.axisbelow": True,
    "figure.facecolor": "white", "axes.facecolor": "white", "legend.frameon": False,
})
import numpy as np
px = np.linspace(12, 25, 300)
stock = (px - S + DIV_EST) / S * 100
prot  = (px - S + DIV_EST - 1.35 + np.maximum(17-px, 0)) / S * 100
coll  = (np.minimum(px, 20) - S + DIV_EST - 0.45 + np.maximum(17-px, 0)) / S * 100
csp   = (1.60 - np.maximum(18-px, 0)) / 18 * 100

fig, ax = plt.subplots(figsize=(9.6, 4.6))
ax.plot(px, stock, color=COOL_GREY, lw=1.4, ls="--", label="Μετοχή μόνο")
ax.plot(px, prot, color=ROYAL, lw=2.0, label="Μετοχή + Dec 17P (protective put)")
ax.plot(px, coll, color=VIOLET, lw=2.0, label="Collar: μετοχή + 17P − 20C")
ax.plot(px, csp, color=ORANGE, lw=2.0, label="Cash-secured put Dec 18P (νέα θέση)")
ax.axhline(0, color=BLUE_GREY, lw=0.8)
ax.axvline(S, color=LIGHT_GREY, lw=1.2)
ax.annotate(f"spot 18,70", (S, ax.get_ylim()[0]*0.0+13), textcoords="offset points", xytext=(4, 0), fontsize=8.5, color=BLUE_GREY, rotation=90)
ax.set_title("Αποτέλεσμα στη λήξη Dec '26 (% επί κεφαλαίου, με εκτιμώμενο μέρισμα Q3 $1,10)", fontsize=11.5, pad=10)
ax.set_xlabel("Τιμή DHT στη λήξη 18/12/2026 (USD)")
ax.set_ylabel("P&L (%)")
ax.legend(loc="lower right", fontsize=9)
ax.set_ylim(-32, 32)
fig.text(0.01, 0.005, "Υπολογισμοί C. σε live quotes IBKR 26/08/2026 (mid/συντηρητικές πλευρές) · χωρίς προμήθειες", fontsize=7.5, color=COOL_GREY)
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig(os.path.join(BASE, "report", "chart_e6.png"), dpi=170)
print("\nchart_e6.png written")

#!/usr/bin/env python3
"""DHT valuation computations: trailing metrics, NAV build, dividend scenarios + sensitivity chart."""
import os, sys
BASE = "/tmp/claude-0/-home-user-stock-visualizer/83d1a957-9071-5bce-8533-fee1b20429a3/scratchpad"
sys.path.insert(0, BASE)

PX = 19.25
SH = 161.2356  # million shares (30/6/2026)

# --- Trailing reported EPS (co-reported quarters) ---
eps_q = {"Q3-25": 44.8/161.2, "Q4-25": 0.41, "Q1-26": 1.02, "Q2-26": 1.23}
eps_ttm = sum(eps_q.values())
ord_ttm = 0.18 + 0.41 + 0.64 + 1.22
ni_ttm = 44.8 + 66.1 + 164.5 + 198.3
print(f"Trailing reported EPS: {eps_ttm:.2f} -> P/E {PX/eps_ttm:.1f}x")
print(f"Trailing ordinary EPS/DPS: {ord_ttm:.2f} -> P/E {PX/ord_ttm:.1f}x, yield {ord_ttm/PX*100:.1f}%")
print(f"Trailing NI: {ni_ttm:.1f}M; ROE on ~$1.0-1.13bn avg equity: {ni_ttm/1065*100:.0f}%")

mcap = SH * PX
net_debt = 434.8 - 161.7
ev = mcap + net_debt
print(f"MCap ${mcap/1000:.2f}bn; net debt ${net_debt:.0f}M; EV ${ev/1000:.2f}bn")

# --- NAV build (broker age-curve marks, Aug 2026: 5yo=143, 10yo=113, resale=168, newbuild=128.5) ---
# Fleet: 4x2026, 6x2018 (incl Nokota), 8x2015-16 (6 HHI + Osprey + Harrier), 5x2011-12
fleet_lo = 4*155 + 6*120 + 8*105 + 5*82
fleet_hi = 4*168 + 6*135 + 8*118 + 5*95
oth_assets = 150.0   # receivables/bunkers est
tot_liab = 478.3
for tag, fl in (("low", fleet_lo), ("high", fleet_hi)):
    nav = fl + 161.7 + oth_assets - tot_liab
    print(f"NAV {tag}: fleet ${fl}M -> NAV ${nav:.0f}M = ${nav/SH:.2f}/sh -> P/NAV {PX/(nav/SH):.2f}x")
# company-ratio anchor: leverage 14.1% MTM
mtm_assets = 434.8 / 0.141
nav_co = mtm_assets - tot_liab
print(f"Company-ratio anchor: MTM assets ${mtm_assets:.0f}M -> NAV ${nav_co:.0f}M = ${nav_co/SH:.2f}/sh -> P/NAV {PX/(nav_co/SH):.2f}x")

# --- Annualized dividend scenarios (ordinary EPS ~= DPS under 100% policy) ---
# Assumptions: ~8,030 revenue days/yr (23 ships x ~349), 51% spot (4,100) / 49% TC (3,930)
# TC book 2026: ~$90k blended (locked highs); mid-cycle TC assumed to reprice with spot (noted)
spot_days, tc_days = 4100, 3930
opex, ga, dep, interest = 75.0, 22.0, 120.0, 18.0
print("\nScenario table (annualized, indicative):")
for spot, tc, label in [
    (162.6, 90.8, "Q2 2026 run-rate"),
    (150.0, 90.0, "Q3 2026 booked area"),
    (100.0, 80.0, "Strong-but-normalizing"),
    (67.5, 55.0, "Mid-cycle (Jefferies pre-war)"),
    (45.0, 45.0, "FY2024-25 average"),
    (30.0, 40.0, "P&L breakeven zone"),
]:
    tce = (spot_days*spot + tc_days*tc)/1000.0
    ebitda = tce - opex - ga
    ni = ebitda - dep - interest
    eps = max(ni, 0)/SH
    print(f"  spot ${spot:>6.1f}k/TC ${tc:>5.1f}k: TCE ${tce:>6.0f}M, EBITDA ${ebitda:>6.0f}M, EPS ${eps:>5.2f}, yield {eps/PX*100:>5.1f}%  [{label}]")

# EPS sensitivity per $10k/day
print(f"\nSensitivity: +$10,000/day on spot days = ${spot_days*10/1000:.0f}M = ${spot_days*10/1000/SH:.2f}/sh EPS")
print(f"Sensitivity: +$10,000/day full fleet = ${(spot_days+tc_days)*10/1000:.0f}M = ${(spot_days+tc_days)*10/1000/SH:.2f}/sh EPS")

# Covenant cushion
fleet_mid = (fleet_lo+fleet_hi)/2
vmc_need = 434.8 * 1.35
print(f"\nVMC covenant: collateral must be >= ${vmc_need:.0f}M vs fleet ~${fleet_mid:.0f}M -> values could fall {(1-vmc_need/fleet_mid)*100:.0f}% before breach (indicative)")

# --- Chart: yield vs spot rate ---
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
for f in os.listdir(os.path.join(BASE, "fonts")):
    try: fm.fontManager.addfont(os.path.join(BASE, "fonts", f))
    except Exception: pass
ROYAL, MIDNIGHT, RED, ORANGE, BLUE_GREY, COOL_GREY, LIGHT_GREY = "#0001FF", "#000041", "#B9444A", "#D46B2A", "#3B4557", "#9AA2A5", "#DDDDDD"
matplotlib.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Noto Sans", "DejaVu Sans", "Arial"],
    "axes.edgecolor": BLUE_GREY, "axes.labelcolor": MIDNIGHT, "axes.titlecolor": MIDNIGHT,
    "axes.titleweight": "bold", "xtick.color": BLUE_GREY, "ytick.color": BLUE_GREY,
    "grid.color": LIGHT_GREY, "grid.linewidth": 0.6, "axes.grid": True, "axes.axisbelow": True,
    "figure.facecolor": "white", "axes.facecolor": "white", "legend.frameon": False,
})
spots = list(range(25, 175, 5))
def eps_at(spot, tc):
    tce = (spot_days*spot + tc_days*tc)/1000.0
    return max(tce - opex - ga - dep - interest, 0)/SH
def tc_map(s):
    return min(90.0, max(40.0, 0.5 * s + 21.0))
ys = [eps_at(s, tc_map(s)) / PX * 100 for s in spots]
fig, ax = plt.subplots(figsize=(9.6, 3.9))
ax.plot(spots, ys, color=ROYAL, lw=2)
for sx, lbl in [(45, "μέσο 2024–25"), (67.5, "mid-cycle"), (150, "Q3'26 booked")]:
    yv = eps_at(sx, tc_map(sx))/PX*100
    ax.scatter([sx], [yv], color=ORANGE, zorder=5)
    ax.annotate(f"{lbl}\n{yv:.0f}%", (sx, yv), textcoords="offset points", xytext=(6, 8), fontsize=8.5, color=MIDNIGHT)
ax.axhline(12.7, color=RED, lw=1, ls="--")
ax.annotate("τρέχουσα trailing απόδοση 12,7%", (26, 13.2), fontsize=8.5, color=RED)
ax.set_title("Ενδεικτική μερισματική απόδοση DHT στα $19,25 ανά επίπεδο spot VLCC", fontsize=12, pad=10)
ax.set_xlabel("Spot TCE ($ χιλ./ημέρα)")
ax.set_ylabel("Απόδοση (%)")
fig.text(0.01, 0.005, "Εκτίμηση C. βάσει στοιχείων εταιρίας (ημέρες εσόδων, breakevens) · indicative", fontsize=8, color=COOL_GREY)
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig(os.path.join(BASE, "charts", "chart_sens.png"), dpi=170)
print("chart_sens.png written")

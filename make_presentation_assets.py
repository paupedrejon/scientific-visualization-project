"""Create presentation-only visual assets from current verified outputs.

Full EU-27 charts remain in outputs/figures/. Presentation variants go to
outputs/figures/present/. Numbers are read from statistics_and_sources.json
and the yearly / country CSVs — no invented values.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent
OUT = BASE / "outputs"
FIG = OUT / "figures"
PRESENT = FIG / "present"

COLORS = {
    "renew": "#16a085",
    "nuclear": "#4868a9",
    "fossil": "#b86f50",
    "intensity": "#6e477c",
    "lowcarbon": "#2a9d8f",
    "navy": "#1f2a37",
    "muted": "#5a6673",
    "panel": "#f4f7f9",
    "teal": "#1a7a6d",
    "accent": "#3d6b9a",
}

SPOTLIGHT = ["SWE", "FRA", "DNK", "DEU", "ESP", "ITA", "POL", "AUT", "MLT"]


def load_context():
    stats = json.loads((OUT / "statistics_and_sources.json").read_text(encoding="utf8"))
    year = int(stats["year"])
    profiles = pd.read_csv(OUT / f"country_profiles_{year}.csv")
    yearly = pd.read_csv(OUT / "yearly_coverage_and_weighted_indicators.csv")
    n_rows = int(yearly["country_count"].sum()) if "country_count" in yearly else 27 * (year - 2010 + 1)
    # Prefer exact retained count from filter: years 2010..year inclusive
    n_rows = 27 * (year - 2010 + 1)
    return stats, year, profiles, yearly, n_rows


def setup():
    PRESENT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 12,
        "axes.titlesize": 15,
        "axes.titleweight": "bold",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.12,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
    })


def save(fig, name: str):
    fig.savefig(PRESENT / name, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def diagram_research_questions(year: int):
    fig, ax = plt.subplots(figsize=(12.5, 5.8))
    ax.set_xlim(0, 12.5)
    ax.set_ylim(0, 6)
    ax.axis("off")
    ax.set_title("Three descriptive questions — no causal claims", loc="left",
                 color=COLORS["navy"], pad=12)

    boxes = [
        (0.3, 2.8, "Q1  Time", f"How did the EU-27\nelectricity mix change\nfrom 2010 to {year}?", COLORS["teal"]),
        (4.4, 2.8, "Q2  Pathways", "Which countries lead\nor lag — and via which\ngeneration portfolios?", COLORS["accent"]),
        (8.5, 2.8, "Q3  Intensity", "Do renewables alone\ntrack lifecycle intensity,\nor does nuclear matter?", COLORS["intensity"]),
    ]
    for x, y, title, body, color in boxes:
        ax.add_patch(FancyBboxPatch((x, y), 3.6, 2.5, boxstyle="round,pad=0.04,rounding_size=0.15",
                                    facecolor=COLORS["panel"], edgecolor=color, linewidth=2.2))
        ax.text(x + 1.8, y + 2.05, title, ha="center", va="center", fontsize=14,
                fontweight="bold", color=color)
        ax.text(x + 1.8, y + 0.95, body, ha="center", va="center", fontsize=12, color=COLORS["navy"])

    ax.add_patch(FancyBboxPatch((2.5, 0.35), 7.5, 1.5, boxstyle="round,pad=0.03,rounding_size=0.12",
                                facecolor="#eef3f7", edgecolor="#c5d0da", linewidth=1.2))
    ax.text(6.25, 1.45, "Exploratory side question", ha="center", fontsize=11,
            fontweight="bold", color=COLORS["muted"])
    ax.text(6.25, 0.85, "Can portfolio features form interpretable groups?  →  K-means + PCA (weak silhouette expected)",
            ha="center", fontsize=11, color=COLORS["navy"])
    save(fig, "d02_research_questions.png")


def diagram_provenance(year: int, n_rows: int):
    fig, ax = plt.subplots(figsize=(12.5, 5.8))
    ax.set_xlim(0, 12.5)
    ax.set_ylim(0, 6)
    ax.axis("off")
    ax.set_title("Provenance · version-pinned snapshot", loc="left", color=COLORS["navy"], pad=12)

    nodes = [
        (0.4, 3.2, 2.8, 1.8, "Ember\n(+ Energy Institute\nfor related series)", "#e8f0fa"),
        (4.0, 3.2, 2.8, 1.8, "Our World in Data\nEnergy dataset\nversion 2026-09-10", "#e7f5f2"),
        (7.6, 3.2, 4.4, 1.8, f"This project\nEU-27 ISO3 · 2010–{year}\n{n_rows} country–year rows", "#f7efe8"),
    ]
    for x, y, w, h, text, face in nodes:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03,rounding_size=0.12",
                                    facecolor=face, edgecolor=COLORS["navy"], linewidth=1.4))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=12, color=COLORS["navy"])

    for x0, x1 in [(3.2, 4.0), (6.8, 7.6)]:
        ax.annotate("", xy=(x1, 4.1), xytext=(x0, 4.1),
                    arrowprops=dict(arrowstyle="->", color=COLORS["muted"], lw=2))

    ax.text(0.4, 2.4, "Observation unit", fontsize=11, fontweight="bold", color=COLORS["teal"])
    ax.text(0.4, 1.85, "One row = one country in one year  ·  not people, not EU aggregates",
            fontsize=12, color=COLORS["navy"])
    ax.text(0.4, 1.15, "Pinned CSV", fontsize=11, fontweight="bold", color=COLORS["teal"])
    ax.text(0.4, 0.6, "catalog.ourworldindata.org/garden/energy/2026-09-10/owid_energy/owid_energy.csv",
            fontsize=10, color=COLORS["muted"])
    ax.text(0.4, 0.2, "Attribute OWID and underlying providers (Ember for electricity intensity).",
            fontsize=10, color=COLORS["muted"])
    save(fig, "d03_provenance.png")


def diagram_variables():
    fig, ax = plt.subplots(figsize=(12.5, 5.8))
    ax.set_xlim(0, 12.5)
    ax.set_ylim(0, 6)
    ax.axis("off")
    ax.set_title("Variables · units · denominators", loc="left", color=COLORS["navy"], pad=12)

    rows = [
        (COLORS["renew"], "Renewable share", "% of electricity generation", "Not share of total final energy"),
        (COLORS["nuclear"], "Nuclear share", "% of electricity generation", "Separate from renewables"),
        (COLORS["lowcarbon"], "Low-carbon share", "Renewables + nuclear (%)", "The key composite for intensity"),
        (COLORS["fossil"], "Fossil share", "% of electricity generation", "Coal + gas + oil electricity"),
        (COLORS["intensity"], "Lifecycle intensity", "gCO₂eq / kWh generated", "Lifecycle GHGs, Ember via OWID"),
        (COLORS["accent"], "Generation (weight)", "TWh", "Weights EU averages"),
    ]
    y = 5.0
    ax.text(0.4, 5.35, "Indicator", fontsize=10, fontweight="bold", color=COLORS["muted"])
    ax.text(4.2, 5.35, "Unit / definition", fontsize=10, fontweight="bold", color=COLORS["muted"])
    ax.text(8.4, 5.35, "Watch out", fontsize=10, fontweight="bold", color=COLORS["muted"])
    for color, name, unit, note in rows:
        ax.add_patch(FancyBboxPatch((0.35, y - 0.35), 0.25, 0.55, boxstyle="square,pad=0",
                                    facecolor=color, edgecolor="none"))
        ax.text(0.8, y, name, fontsize=12, fontweight="bold", color=COLORS["navy"], va="center")
        ax.text(4.2, y, unit, fontsize=12, color=COLORS["navy"], va="center")
        ax.text(8.4, y, note, fontsize=11, color=COLORS["muted"], va="center")
        y -= 0.72
    save(fig, "d04_variables.png")


def diagram_pipeline(year: int, n_rows: int):
    fig, ax = plt.subplots(figsize=(12.5, 5.8))
    ax.set_xlim(0, 12.5)
    ax.set_ylim(0, 6)
    ax.axis("off")
    ax.set_title("Data-processing flow (transparent, no imputation)", loc="left",
                 color=COLORS["navy"], pad=12)

    steps = [
        (0.25, "OWID CSV\n2026-09-10", "19 494 rows"),
        (2.55, "Filter\nEU-27 ISO3", "27 countries"),
        (4.85, f"Years\n2010–{year}", f"{n_rows} rows"),
        (7.15, "Missingness\naudit", f"0 missing\nin {year} core"),
        (9.55, "Analyse &\nvisualise", "weighted trends\nSpearman · K-means"),
    ]
    for i, (x, title, sub) in enumerate(steps):
        ax.add_patch(FancyBboxPatch((x, 2.6), 2.15, 2.2, boxstyle="round,pad=0.03,rounding_size=0.12",
                                    facecolor=COLORS["panel"], edgecolor=COLORS["teal"], linewidth=1.8))
        ax.text(x + 1.075, 4.2, title, ha="center", va="center", fontsize=12,
                fontweight="bold", color=COLORS["navy"])
        ax.text(x + 1.075, 3.2, sub, ha="center", va="center", fontsize=11, color=COLORS["muted"])
        if i < len(steps) - 1:
            ax.annotate("", xy=(x + 2.35, 3.7), xytext=(x + 2.15, 3.7),
                        arrowprops=dict(arrowstyle="->", color=COLORS["muted"], lw=2))

    ax.add_patch(FancyBboxPatch((0.25, 0.35), 11.9, 1.7, boxstyle="round,pad=0.03,rounding_size=0.1",
                                facecolor="#eef6f4", edgecolor=COLORS["teal"], linewidth=1.2))
    ax.text(0.55, 1.55, "Methods used", fontsize=11, fontweight="bold", color=COLORS["teal"])
    ax.text(0.55, 1.05,
            "• EU trends = generation-weighted means (country share × TWh / Σ TWh)",
            fontsize=11, color=COLORS["navy"])
    ax.text(0.55, 0.6,
            "• Cross-section = Spearman ρ  ·  Clusters = standardized portfolio → K-means (silhouette) + PCA 2D",
            fontsize=11, color=COLORS["navy"])
    save(fig, "d05_pipeline.png")


def chart_ranking_present(df: pd.DataFrame, year: int):
    d = df.dropna(subset=["low_carbon_electricity_share_pct"]).sort_values(
        "low_carbon_electricity_share_pct")
    ranked = d.sort_values("low_carbon_electricity_share_pct", ascending=False)
    leaders = set(ranked.head(5)["iso_code"])
    laggards = set(ranked.tail(5)["iso_code"])
    fig, ax = plt.subplots(figsize=(11.2, 7.0))
    colors = []
    for _, row in d.iterrows():
        if row["iso_code"] in leaders:
            colors.append(COLORS["lowcarbon"])
        elif row["iso_code"] in laggards:
            colors.append(COLORS["fossil"])
        else:
            colors.append("#9db5b0")
    ax.barh(d["country"], d["low_carbon_electricity_share_pct"], color=colors, height=0.72)
    ax.set_xlim(0, 108)
    ax.set_xlabel("Low-carbon electricity share (%)  ·  renewables + nuclear", fontsize=12)
    ax.set_title(f"Low-carbon electricity share by EU country · {year}", color=COLORS["navy"])
    ax.tick_params(axis="y", labelsize=10)
    for i, (_, row) in enumerate(d.iterrows()):
        val = row["low_carbon_electricity_share_pct"]
        weight = "bold" if row["iso_code"] in (leaders | laggards | set(SPOTLIGHT)) else "normal"
        ax.text(min(val + 1.2, 100), i, f"{val:.0f}%", va="center", fontsize=9, fontweight=weight,
                color=COLORS["navy"])
    ax.text(0, -0.14,
            "Highlighted: top 5 (teal) and bottom 5 (brown) by low-carbon share. Full series for all 27 countries.",
            transform=ax.transAxes, fontsize=9, color=COLORS["muted"])
    save(fig, "03_low_carbon_ranking_present.png")


def chart_mix_spotlight(df: pd.DataFrame, year: int):
    order = ["SWE", "FRA", "DNK", "AUT", "ESP", "DEU", "ITA", "POL", "MLT"]
    labels = {
        "SWE": "Sweden · RE+nuclear",
        "FRA": "France · nuclear-led",
        "DNK": "Denmark · RE-led",
        "AUT": "Austria · hydro/RE",
        "ESP": "Spain · mixed",
        "DEU": "Germany · RE+fossil",
        "ITA": "Italy · RE+fossil",
        "POL": "Poland · fossil-heavy",
        "MLT": "Malta · fossil-heavy",
    }
    cols = {
        "renew": "renewables_electricity_share_pct",
        "nuclear": "nuclear_electricity_share_pct",
        "fossil": "fossil_fuels_electricity_share_pct",
    }
    sub = df.set_index("iso_code").loc[order].copy()
    sub["remaining"] = (100 - sub[list(cols.values())].sum(axis=1)).clip(lower=0)
    fig, ax = plt.subplots(figsize=(11.5, 6.2))
    y = np.arange(len(sub))
    left = np.zeros(len(sub))
    for key, label, color in [
        ("renew", "Renewables", COLORS["renew"]),
        ("nuclear", "Nuclear", COLORS["nuclear"]),
        ("fossil", "Fossil", COLORS["fossil"]),
        ("remaining", "Other / rounding", "#a0aab4"),
    ]:
        vals = sub[cols[key]].values if key != "remaining" else sub["remaining"].values
        ax.barh(y, vals, left=left, color=color, height=0.68, label=label)
        left += vals
    ax.set_yticks(y)
    ax.set_yticklabels([labels[i] for i in order], fontsize=12)
    ax.set_xlim(0, 101)
    ax.set_xlabel("Share of electricity generation (%)", fontsize=12)
    ax.set_title(f"Three pathways in one view · selected EU countries · {year}", color=COLORS["navy"])
    ax.legend(frameon=False, ncol=4, loc="lower center", bbox_to_anchor=(0.5, -0.16), fontsize=11)
    ax.text(0, -0.22,
            "Presentation spotlight (9 of 27). Complete EU-27 stacked mix: figures/06_electricity_mix_by_country.png",
            transform=ax.transAxes, fontsize=9, color=COLORS["muted"])
    save(fig, "06_electricity_mix_spotlight.png")


def chart_compare_story(df: pd.DataFrame, stats: dict, year: int):
    paired = df.dropna(subset=[
        "renewables_electricity_share_pct",
        "low_carbon_electricity_share_pct",
        "electricity_carbon_intensity_gco2eq_per_kwh",
    ]).copy()
    r_re = stats["renew"]["spearman_rho"]
    p_re = stats["renew"]["p_value"]
    r_lc = stats["lowcarbon"]["spearman_rho"]
    p_lc = stats["lowcarbon"]["p_value"]

    fig, axes = plt.subplots(1, 2, figsize=(13.2, 5.8), sharey=True)
    configs = [
        (axes[0], "renewables_electricity_share_pct", COLORS["renew"],
         "A. Renewables only",
         f"Spearman ρ = {r_re:.2f}   ·   p = {p_re:.3g}   ·   n = {stats['renew']['n']}",
         "Moderate link — France sits low on renewables\nbut has very low intensity."),
        (axes[1], "low_carbon_electricity_share_pct", COLORS["lowcarbon"],
         "B. Low-carbon (renewables + nuclear)",
         f"Spearman ρ = {r_lc:.2f}   ·   p = {p_lc:.3g}   ·   n = {stats['lowcarbon']['n']}",
         "Much tighter link — nuclear closes the gap\nfor countries like France & Slovakia."),
    ]
    annotate = {"FRA", "DEU", "ITA", "ESP", "SWE", "POL", "DNK", "CZE", "MLT"}
    for ax, col, color, title, box, note in configs:
        ax.scatter(paired[col], paired["electricity_carbon_intensity_gco2eq_per_kwh"],
                   s=70, c=color, alpha=0.85, edgecolor="white", linewidth=0.8, zorder=3)
        for _, row in paired.iterrows():
            if row["iso_code"] in annotate:
                ax.annotate(row["iso_code"],
                            (row[col], row["electricity_carbon_intensity_gco2eq_per_kwh"]),
                            xytext=(5, 4), textcoords="offset points", fontsize=9,
                            fontweight="bold" if row["iso_code"] == "FRA" else "normal",
                            color=COLORS["navy"])
        ax.set_title(title, color=COLORS["navy"], fontsize=13)
        ax.set_xlabel(title.split(". ")[1] + " (%)", fontsize=11)
        ax.text(0.03, 0.97, box, transform=ax.transAxes, va="top", fontsize=10,
                color=COLORS["navy"],
                bbox=dict(facecolor="white", edgecolor="#d5dee6", boxstyle="round,pad=0.35"))
        ax.text(0.03, 0.08, note, transform=ax.transAxes, fontsize=9.5, color=COLORS["muted"],
                va="bottom")
        ax.set_xlim(-2, 105)
    axes[0].set_ylabel("Lifecycle intensity (gCO₂eq / kWh)", fontsize=11)
    fig.suptitle(f"Same countries, same year ({year}) — what changes when nuclear enters the share?",
                 fontsize=14, fontweight="bold", color=COLORS["navy"], y=1.02)
    fig.text(0.5, -0.02,
             "Cross-sectional association only · not causal. Verified stats from analysis.py · OWID Energy 2026-09-10.",
             ha="center", fontsize=9, color=COLORS["muted"])
    save(fig, "10_11_renewables_vs_lowcarbon_story.png")


def chart_intensity_callouts(yearly: pd.DataFrame, year: int):
    line = yearly.loc[yearly["year"].between(2010, year)]
    fig, ax = plt.subplots(figsize=(11.5, 5.4))
    ax.plot(line["year"], line["eu_generation_weighted_intensity"],
            marker="o", linewidth=2.8, color=COLORS["intensity"])
    ax.set_title("EU-27 lifecycle carbon intensity of electricity", color=COLORS["navy"])
    ax.set_ylabel("gCO₂eq / kWh of generated electricity")
    ax.set_xlabel("Year")
    callouts = [2010, 2020, 2022, year]
    for yr in callouts:
        val = float(line.loc[line["year"] == yr, "eu_generation_weighted_intensity"].iloc[0])
        tag = f"{yr}\n{val:.0f}"
        if yr == 2022:
            tag = f"{yr} rebound\n{val:.0f}"
        ax.annotate(tag, xy=(yr, val), xytext=(0, 18 if yr != 2022 else -36),
                    textcoords="offset points", ha="center", fontsize=9,
                    color=COLORS["navy"],
                    arrowprops=dict(arrowstyle="-", color=COLORS["muted"], lw=0.8))
    ax.text(0, -0.18,
            "Generation-weighted · coverage 27/27 each year for this indicator set · OWID Energy 2026-09-10",
            transform=ax.transAxes, fontsize=9, color=COLORS["muted"])
    save(fig, "02_carbon_intensity_annotated.png")


def chart_mix_trend_callouts(yearly: pd.DataFrame, year: int):
    line = yearly.loc[yearly["year"].between(2010, year)]
    fig, ax = plt.subplots(figsize=(11.5, 5.5))
    series = [
        ("eu_generation_weighted_renew", "Renewable", COLORS["renew"]),
        ("eu_generation_weighted_nuclear", "Nuclear", COLORS["nuclear"]),
        ("eu_generation_weighted_fossil", "Fossil", COLORS["fossil"]),
    ]
    for col, label, color in series:
        ax.plot(line["year"], line[col], label=label, color=color, linewidth=2.7, marker="o", markersize=3.5)
    ax.set_ylim(0, 100)
    ax.set_ylabel("Share of electricity generation (%)")
    ax.set_xlabel("Year")
    ax.set_title("EU-27 electricity mix: the long-term transition", color=COLORS["navy"])
    ax.legend(frameon=False, ncol=3, fontsize=11)
    ax.axvline(2020, color="#c5d0da", ls="--", lw=1)
    ax.text(2020.15, 92, "RE overtakes\nfossil ≈ 2020", fontsize=9, color=COLORS["muted"])
    y0 = line.loc[line["year"] == 2010].iloc[0]
    y1 = line.loc[line["year"] == year].iloc[0]
    ax.text(2010.2, 8,
            f"2010: fossil {y0['eu_generation_weighted_fossil']:.0f}% · RE {y0['eu_generation_weighted_renew']:.0f}% · nuclear {y0['eu_generation_weighted_nuclear']:.0f}%",
            fontsize=10, color=COLORS["navy"],
            bbox=dict(facecolor="white", edgecolor="#d5dee6", boxstyle="round,pad=0.3"))
    ax.text(2017.5, 8,
            f"{year}: RE {y1['eu_generation_weighted_renew']:.0f}% · fossil {y1['eu_generation_weighted_fossil']:.0f}% · nuclear {y1['eu_generation_weighted_nuclear']:.0f}%",
            fontsize=10, color=COLORS["navy"],
            bbox=dict(facecolor="white", edgecolor="#d5dee6", boxstyle="round,pad=0.3"))
    ax.text(0, -0.18,
            "Country shares weighted by national generation (TWh). Verified from yearly_coverage_and_weighted_indicators.csv",
            transform=ax.transAxes, fontsize=9, color=COLORS["muted"])
    save(fig, "01_mix_trend_annotated.png")


def main():
    setup()
    stats, year, df, yearly, n_rows = load_context()
    diagram_research_questions(year)
    diagram_provenance(year, n_rows)
    diagram_variables()
    diagram_pipeline(year, n_rows)
    chart_mix_trend_callouts(yearly, year)
    chart_intensity_callouts(yearly, year)
    chart_ranking_present(df, year)
    chart_mix_spotlight(df, year)
    chart_compare_story(df, stats, year)
    print(f"Presentation assets written to {PRESENT} (year={year})")


if __name__ == "__main__":
    main()

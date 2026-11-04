# Verified findings — EU-27 electricity transition

**Analysis year (cross-section):** 2024  
**Temporal window for trends:** 2010–2024  
**Dataset version:** Our World in Data *Energy* dataset, **2026-09-10**  
**Pinned CSV:** https://catalog.ourworldindata.org/garden/energy/2026-09-10/owid_energy/owid_energy.csv  
**Catalog / codebook:** https://catalog.ourworldindata.org/energy/owid_energy/  
**Primary electricity provenance (per OWID):** Ember (and Energy Institute Statistical Review for related energy series); lifecycle carbon intensity draws on Ember. Attribute OWID **and** underlying providers.  
**Script run:** `python analysis.py --year 2024`  
**No fabricated numbers:** all statistics below come from `outputs/` produced by that run.

---

## Sample and coverage

| Item | Value |
| --- | --- |
| Raw CSV rows (global) | 19 494 |
| Raw CSV columns | 130 |
| Analytical sample | EU-27 ISO3 × years 2010–2024 |
| Country–year rows retained | **405** (27 × 15) |
| Countries in 2024 | **27/27** |
| Missing values in 2024 for generation, renewable/nuclear/fossil/low-carbon shares, intensity, solar/wind/hydro | **0** |
| Coverage 2010–2024 for those indicators | **27/27 every year** |

Observations are **country–years**, not people. Shares are **of electricity generation**, not of total final energy. `low_carbon_electricity_share_pct` = renewables **+ nuclear**. Intensity is **lifecycle gCO₂eq / kWh generated**.

---

## Finding 1 — Europe’s generation mix shifted from fossil-led to renewable-led

Generation-weighted EU-27 shares (`yearly_coverage_and_weighted_indicators.csv`):

| Indicator | 2010 | 2024 | Change |
| --- | ---: | ---: | ---: |
| Renewable share | 22.2% | **48.0%** | +25.9 pp |
| Nuclear share | 29.0% | 23.4% | −5.6 pp |
| Fossil share | 48.8% | **28.6%** | −20.3 pp |
| Low-carbon share | 51.2% | **71.4%** | +20.3 pp |

Renewables overtook nuclear around 2013–14 and fossil around 2020 (brief convergence 2021–22; renewables clearly ahead by 2023–24). Chart: `figures/01_eu_electricity_mix_trend.png`.

---

## Finding 2 — Lifecycle carbon intensity fell, with a 2021–22 setback

Generation-weighted EU-27 intensity:

| Year | gCO₂eq / kWh |
| --- | ---: |
| 2010 | 369.3 |
| 2020 | 261.2 |
| 2022 | 291.6 |
| 2024 | **211.2** |

Net change 2010→2024: about **−43%**. Intensity rose again in 2021–22 (energy-crisis period visible in the series) then dropped sharply through 2023–24. Chart: `figures/02_carbon_intensity_trend.png`.

---

## Finding 3 — Country pathways diverge; renewables alone only partly track intensity

### 2024 low-carbon ranking (selected)

| Rank | Country | Low-carbon % | Intensity (gCO₂eq/kWh) |
| --- | --- | ---: | ---: |
| 1 | Sweden | 98.8 | 34.9 |
| 2 | Finland | 95.3 | 66.6 |
| 3 | France | 94.9 | 40.5 |
| … | … | … | … |
| 25 | Poland | 31.1 | 608.2 |
| 26 | Cyprus | 24.0 | 511.2 |
| 27 | Malta | 15.5 | 488.6 |

Charts: `03_low_carbon_ranking.png`, `06_electricity_mix_by_country.png`.

Three descriptive pathways visible in the 2024 mix: high-renewable / little nuclear (e.g. Denmark, Luxembourg, Austria, Portugal); nuclear-heavy low fossil (e.g. France, Slovakia); fossil-heavy (e.g. Malta, Cyprus, Poland).

### Spearman associations (2024, n = 27)

| Pair | ρ | p-value | n |
| --- | ---: | ---: | ---: |
| Renewable share vs intensity | **−0.46** | 0.0148 | 27 |
| Low-carbon (renewables + nuclear) vs intensity | **−0.93** | 4.86×10⁻¹² | 27 |

Including nuclear **strengthens** the monotonic association with lifecycle intensity. France illustrates the gap: ~27% renewables but ~95% low-carbon and ~40 gCO₂eq/kWh. Charts: `04_renewables_vs_intensity.png`, `05_lowcarbon_vs_intensity.png`.

**Not causal:** portfolio composition and lifecycle intensity are conceptually linked; ρ describes cross-section association only. Small n; exploratory; possible confounding (imports, technology mix within “fossil”, etc.).

---

## Clustering (exploratory) — weak separation

- Features (standardized): solar, wind, hydro, nuclear, fossil shares (2024); n = 27 complete cases.
- Best k by silhouette among {2,3,4,5}: **k = 4**, silhouette **0.30** (all candidates ≈ 0.28–0.30).
- PCA 2D variance explained: **67.2%** (PC1 ~40%, PC2 ~27%).
- Chart: `07_country_clusters_pca.png`; membership: `clusters_2024.csv`.

**Interpretation:** silhouette ≈ 0.30 is **weak**. Clusters are a visual aid for portfolio similarities, **not** evidence of natural discrete groups. Prefer describing continuous mix differences over hard cluster labels in conclusions.

Illustrative membership (not definitive typology):

- Higher wind/solar, lower fossil: e.g. DNK, LTU, LUX, PRT, ESP  
- Nuclear-prominent: e.g. FRA, SVK, BEL, BGR, CZE, HUN, FIN  
- Higher fossil share: e.g. MLT, CYP, POL, IRL, GRC, ITA, NLD, EST, DEU  
- Hydro / mixed low-fossil: e.g. AUT, HRV, LVA, SWE, ROU, SVN  

---

## Limitations (must state in presentation)

1. Generation shares ≠ consumption / final energy; net imports alter demand-side carbon exposure.  
2. Lifecycle intensity is not identical to direct combustion CO₂.  
3. Complete 2010–2024 coverage here does **not** generalize to other OWID energy variables.  
4. Correlations and clusters are descriptive; no causal identification.  
5. Weak silhouette → do not oversell “four electricity regimes.”  
6. Environment note: on this Windows host, pandas 3.x / some newer wheels were blocked by Application Control; analysis used pandas 2.2.x. Requirements pinned to `pandas>=2.1,<3`.

---

## Output inventory

- `outputs/statistics_and_sources.json`  
- `outputs/yearly_coverage_and_weighted_indicators.csv`  
- `outputs/country_profiles_2024.csv`  
- `outputs/clusters_2024.csv`  
- `outputs/figures/01_eu_electricity_mix_trend.png` … `07_country_clusters_pca.png`

# Verified findings — EU-27 electricity transition

**Analysis year (cross-section):** 2025  
**Temporal window for trends:** 2010–2025  
**Dataset version:** Our World in Data *Energy* dataset, **2026-09-10**  
**Pinned CSV:** https://catalog.ourworldindata.org/garden/energy/2026-09-10/owid_energy/owid_energy.csv  
**Catalog / codebook:** https://catalog.ourworldindata.org/energy/owid_energy/  
**Primary electricity provenance (per OWID):** Ember (and Energy Institute Statistical Review for related energy series); lifecycle carbon intensity draws on Ember.  
**Script run:** `python analysis.py --year 2025`  
All statistics below come from `outputs/` produced by that run.

## Scope change note

Previous deliverables used **2010–2024** (cross-section 2024). After auditing the pinned CSV, **all analysis variables are complete for EU-27 in 2025** (27/27, 0 missing; see `missingness_2025_eu27_audit.csv`). The pipeline was therefore extended to **2010–2025**.  
Previous 2024-scoped outputs are preserved unchanged under `outputs/archive_through_2024/` (local archive; not required on the remote). No imputation was used.

---

## Sample and coverage

| Item | Value |
| --- | --- |
| Analytical sample | EU-27 ISO3 × years 2010–2025 |
| Country–year rows retained | **432** (27 × 16) |
| Countries in 2025 | **27/27** |
| Missing values in 2025 for generation, renewable/nuclear/fossil/low-carbon shares, intensity, solar/wind/hydro | **0** |
| Coverage 2010–2025 for those indicators | **27/27 every year** |

Observations are **country–years**. Shares are **of electricity generation**. `low_carbon_electricity_share_pct` = renewables **+ nuclear**. Intensity is **lifecycle gCO₂eq / kWh generated**.

### Missingness audit · EU-27 · 2025

| Variable | Non-missing | Missing |
| --- | ---: | ---: |
| electricity_generation_twh | 27 | 0 |
| renewables_electricity_share_pct | 27 | 0 |
| nuclear_electricity_share_pct | 27 | 0 |
| fossil_fuels_electricity_share_pct | 27 | 0 |
| low_carbon_electricity_share_pct | 27 | 0 |
| electricity_carbon_intensity_gco2eq_per_kwh | 27 | 0 |
| solar_electricity_share_pct | 27 | 0 |
| wind_electricity_share_pct | 27 | 0 |
| hydro_electricity_share_pct | 27 | 0 |

---

## Finding 1 — Long-term mix shift; 2025 looks like a plateau year

Generation-weighted EU-27 shares:

| Indicator | 2010 | 2024 | 2025 | 2010→2025 |
| --- | ---: | ---: | ---: | ---: |
| Renewable share | 22.2% | 48.0% | **47.7%** | +25.6 pp |
| Nuclear share | 29.0% | 23.4% | **23.3%** | −5.7 pp |
| Fossil share | 48.8% | 28.6% | **28.9%** | −19.9 pp |
| Low-carbon share | 51.2% | 71.4% | **71.1%** | +19.9 pp |

Relative to 2024, 2025 shows a **small dip** in renewables/low-carbon and a **small rise** in fossil at EU aggregate level — not a reversal of the 2010–2024 transition, but a plateau/pause. Chart: `figures/01_eu_electricity_mix_trend.png`.

---

## Finding 2 — Lifecycle intensity still lower than 2010

Generation-weighted EU-27 intensity:

| Year | gCO₂eq / kWh |
| --- | ---: |
| 2010 | 369.3 |
| 2020 | 261.2 |
| 2022 | 291.6 |
| 2024 | 211.2 |
| 2025 | **209.9** |

Net change 2010→2025: about **−43%**. 2025 is slightly below 2024. Chart: `figures/02_carbon_intensity_trend.png`.

---

## Finding 3 — Country pathways diverge; nuclear still matters for intensity

### 2025 low-carbon ranking (selected)

| Rank | Country | Low-carbon % | Intensity (gCO₂eq/kWh) |
| --- | --- | ---: | ---: |
| 1 | Sweden | 98.8 | 35.3 |
| 2 | Finland | 96.3 | 57.5 |
| 3 | France | 94.9 | 41.4 |
| 4 | Luxembourg | 91.6 | 123.4 |
| 5 | Denmark | 91.2 | 114.4 |
| … | … | … | … |
| 25 | Poland | 31.5 | 588.6 |
| 26 | Cyprus | 27.7 | 489.0 |
| 27 | Malta | 16.0 | 484.0 |

### Spearman associations (2025, n = 27)

| Pair | ρ | p-value | n |
| --- | ---: | ---: | ---: |
| Renewable share vs intensity | **−0.46** | 0.0158 | 27 |
| Low-carbon (renewables + nuclear) vs intensity | **−0.93** | 1.73×10⁻¹² | 27 |

Including nuclear still **strengthens** the monotonic association. Charts: `04_…png`, `05_…png`.

**Not causal:** descriptive cross-section only.

---

## Clustering (exploratory) — still weak

- Features: solar, wind, hydro, nuclear, fossil shares (2025); n = 27.
- Best *k* by silhouette among {2,3,4,5}: **k = 5**, silhouette **0.30** (candidates ≈ 0.27–0.30).
- PCA 2D variance: **66.5%**.
- Chart: `07_country_clusters_pca.png`; membership: `clusters_2025.csv`.

Silhouette ≈ 0.30 remains **weak**. Prefer continuous portfolio descriptions over hard cluster labels.

---

## Limitations

1. Generation shares ≠ consumption / imports.  
2. Lifecycle intensity ≠ stack-only CO₂.  
3. Complete coverage for these electricity columns does not generalize to all OWID energy variables.  
4. Correlations and clusters are descriptive.  
5. Weak silhouette → do not oversell discrete regimes.  
6. 2025 vs 2024 EU aggregates moved only slightly; avoid over-interpreting one-year changes.

---

## Output inventory

- `outputs/missingness_2025_eu27_audit.csv`  
- `outputs/statistics_and_sources.json`  
- `outputs/yearly_coverage_and_weighted_indicators.csv`  
- `outputs/country_profiles_2025.csv`  
- `outputs/clusters_2025.csv`  
- `outputs/figures/01_…` through `07_…`  
- `outputs/EU27_Electricity_Transition.pptx` / `.pdf`  
- Previous scope archive: `outputs/archive_through_2024/` (local)

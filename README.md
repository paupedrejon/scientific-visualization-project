# Scientific Visualization: Europe's Electricity Transition

**Working title:** *How green is Europe's electricity? A visual and interpretable analysis of EU-27 countries.*

## Research questions

1. How has the EU-27 electricity mix evolved since 2010?
2. Which countries have the largest shares of renewables, nuclear and fossil generation?
3. Does renewable share correlate with lifecycle carbon intensity? Does including nuclear improve the relationship?
4. Can European countries be grouped into interpretable electricity profiles?

## Precise source and provenance

- **Dataset:** Our World in Data (OWID), *Energy dataset*, September 10, 2026 edition. **Version-pinned source CSV:** https://catalog.ourworldindata.org/garden/energy/2026-09-10/owid_energy/owid_energy.csv
- **Official catalog, with codebook and source-specific attribution:** https://catalog.ourworldindata.org/energy/owid_energy/
- **Codebook:** https://catalog.ourworldindata.org/energy/owid_energy/owid_energy.codebook.csv
- **Original sources of the electricity indicators:** Ember (Yearly Electricity Data Europe / Yearly Electricity Data), Energy Institute Statistical Review of World Energy and several historical datasets, processed/harmonized by OWID. The carbon-intensity series specifically draws on Ember. Check the catalog for the provenance of EACH indicator.
- **License:** consult catalog per-indicator metadata and license; attribute underlying providers as well as OWID.
- **Temporal scope for this project:** 2010 to 2024 (modifiable). **Geographic scope:** the 27 EU member states, identified by ISO-3166-1 alpha-3 codes.
- **Observations:** country-year records, not people. The count of retained rows is computed by the script; do not copy the global catalog figure as the analytical sample size.

NOTE: `renewables_electricity_share_pct` is **the share of electricity generation**, not the overall renewable share of all final energy consumption. `low_carbon_electricity_share_pct` includes renewables **and nuclear**. `electricity_carbon_intensity_gco2eq_per_kwh` measures **lifecycle greenhouse-gas emissions per kWh generated**, in gCO2-equivalent. Do not mix these definitions in the presentation.

## How to run in Cursor / VS Code

1. Open this folder in Cursor.
2. In the terminal run:
   ```bash
   python -m pip install -r requirements.txt
   python analysis.py --year 2024
   ```
3. The first run downloads the frozen OWID CSV into `data/owid_energy.csv` (Internet required) and creates `outputs/figures/` with PNG charts, and `outputs/` with statistical results, coverage table and cleaned country profiles.
4. If the automatic download fails: open the source CSV URL above in a browser, download the file, and save it as `data/owid_energy.csv`.
5. Open `outputs/statistics_and_sources.json`, inspect the actual results, read `outputs/yearly_coverage_and_weighted_indicators.csv`, and verify data coverage before drawing conclusions.

## Expected output graphs

1. `01_eu_electricity_mix_trend.png` – weighted EU share of renewable, nuclear, fossil electricity.
2. `02_carbon_intensity_trend.png` – lifecycle carbon intensity time series.
3. `03_low_carbon_ranking.png` – EU-27 country ranking.
4. `04_renewables_vs_intensity.png` – Spearman association: renewables vs lifecycle intensity.
5. `05_lowcarbon_vs_intensity.png` – compare with total low-carbon electricity (nuclear included).
6. `06_electricity_mix_by_country.png` – country generation portfolio composition.
7. `07_country_clusters_pca.png` – K-means + PCA exploratory visualization, if enough complete observations.

## Analytical method, to describe in the presentation

- Source/definitions; country-year dataset, columns, data types.
- Filter EU-27 by ISO3, 2010–2024; flag missing observations, no fabricated or arbitrary imputations.
- Weighted trend: country generation share × country's electricity generation; divided by sum of valid generation in that year. Countries with missing values are excluded for that indicator/year, so coverage can change. Be transparent about coverage before claiming a constant population of 27 over the years.
- Spearman correlation for monotonic cross-country associations in a specified year; p-values should not be oversold due to small sample, exploratory testing and potential dependence/confounding.
- K-means on standardized country electricity-portfolio features (solar, wind, hydro, nuclear, fossil); examine silhouette for 2–5 clusters, show PCA 2D for visual interpretation and discuss limitations. Low silhouette = weak separation. The cluster labels don't prove natural groupings.
- No causality: generation portfolio and lifecycle intensity are conceptually related, so correlations are **descriptive**, not evidence of a new causal mechanism.

## Suggested deadlines

- Mon 2: agree topic with teammate, download data, confirm sources.
- Tue 3: run script, inspect charts & missing values, choose narrative.
- Wed 4: create slide outline and first draft.
- Thu 5 (exam): no planned project work.
- Fri 6–Sun 8 (Barcelona): leave only asynchronous review/feedback.
- Mon 9: finalize slides, validate statements and captions.
- Tue 10: rehearsal and backup PDF export.
- Wed 11: presentation.

## Critical caveat

This is a **starter kit**, not a verified empirical analysis. In this environment the external CSV could not be downloaded, so NO factual numerical findings have been calculated and no actual figures are bundled. The script contains no invented figures; run it with the real CSV and verify outputs before claiming results.

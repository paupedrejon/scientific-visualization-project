# How green is Europe's electricity?

Scientific Visualization project on the EU-27 electricity mix (2010–2024).

We look at how generation has shifted toward renewables, how countries differ, and whether renewable share (and low-carbon share, including nuclear) lines up with lifecycle carbon intensity.

## Data

[Our World in Data – Energy dataset](https://catalog.ourworldindata.org/energy/owid_energy/), version **2026-09-10** (electricity mostly from Ember).

Pinned CSV: https://catalog.ourworldindata.org/garden/energy/2026-09-10/owid_energy/owid_energy.csv

## Run it

```bash
pip install -r requirements.txt
python analysis.py --year 2024
python build_presentation.py
```

Charts and tables land in `outputs/`. Slides are in `outputs/EU27_Electricity_Transition.pptx` (PDF next to it).

## Notes

- Shares are of **electricity generation**, not total energy use.
- Low-carbon = renewables + nuclear.
- Intensity is lifecycle **gCO₂eq/kWh**.
- Correlations are descriptive, not causal. Clustering is exploratory (weak silhouette).

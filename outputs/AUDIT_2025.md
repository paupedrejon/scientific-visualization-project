# AUDIT 2025 — Slides 10, 11 and 12

**Scope of this audit:** statistical analysis underlying presentation slides 10–12 for cross-section year **2025** only.  
**Code audited:** `analysis.py` (Spearman block ≈ L153–176; K-means + PCA block ≈ L197–230).  
**Data:** `data/owid_energy.csv` (OWID Energy, version **2026-09-10**).  
**Saved results compared:** `outputs/statistics_and_sources.json`, `outputs/clusters_2025.csv`.  
**Independent recalc outputs:** `outputs/audit_2025_recalc.json`, `outputs/audit_2025_clusters_table.csv`.  

**No code or presentation files were modified for this audit.** No values were imputed. No results were invented.

---

## 0. Mapping: slides → analysis artefacts

| Slide | Claim type | Produced by | Primary artefacts |
| --- | --- | --- | --- |
| **10** Renewables vs intensity | Spearman ρ, p, n=27 | `analysis.py` L155–176 (`key='renew'`) | Fig `04_renewables_vs_intensity.png`; `statistics_and_sources.json` → `renew` |
| **11** Low-carbon vs intensity | Spearman ρ, p, n=27 | same loop (`key='lowcarbon'`) | Fig `05_lowcarbon_vs_intensity.png`; JSON → `lowcarbon` |
| **12** K-means + PCA | k, silhouette, PCA % | `analysis.py` L197–230 | Fig `07_country_clusters_pca.png`; JSON → `clustering`; `clusters_2025.csv` |

Filter for all three: EU-27 ISO3 ∩ `year == 2025` (`analysis.py` L267; generation of `year_data` at L99).

---

## 1. Dataset columns used

### 1.1 Slides 10–11 (Spearman)

| Role | Column name in OWID CSV | Code key in `C` |
| --- | --- | --- |
| X (slide 10) | `renewables_electricity_share_pct` | `renew` |
| X (slide 11) | `low_carbon_electricity_share_pct` | `lowcarbon` |
| Y (both) | `electricity_carbon_intensity_gco2eq_per_kwh` | `intensity` |
| Country id / labels | `iso_code`, `country` | — |
| Year filter | `year` | — |

**Not used** in slides 10–11: generation (TWh), solar/wind/hydro separately, clustering features.

**Pairwise complete cases:** `dropna(subset=[X, intensity])` (`analysis.py` L158). For 2025: **0 rows dropped**, **n = 27**.

### 1.2 Slide 12 (K-means + PCA)

| Feature used in clustering / PCA | Column name |
| --- | --- |
| 1 | `solar_electricity_share_pct` |
| 2 | `wind_electricity_share_pct` |
| 3 | `hydro_electricity_share_pct` |
| 4 | `nuclear_electricity_share_pct` |
| 5 | `fossil_fuels_electricity_share_pct` |

Code reference:

```197:201:analysis.py
    # Figure 6 - exploratory clustering of five electricity portfolio variables.
    mix_cols = [C[x] for x in ('solar','wind','hydro','nuclear','fossil')]
    cluster_d = year_data.dropna(subset=mix_cols).copy()
    if len(cluster_d) >= 12:
        standardized = StandardScaler().fit_transform(cluster_d[mix_cols])
```

**Not included** among the five features: aggregate `renewables_electricity_share_pct`, bioenergy / other renewables, intensity.  
For 2025: **27/27** complete on these five columns.

---

## 2. Spearman correlations — recalculation

**Method in code:** `scipy.stats.spearmanr(x, y)` on pairwise-complete country rows (`analysis.py` L159).  
Default two-sided p-value for the Spearman rank correlation (scipy).

### 2.1 Independent recalculation (2025, n=27)

| Association | ρ (recalc) | p (recalc) | n | ρ (saved JSON) | Match |
| --- | ---: | ---: | ---: | ---: | --- |
| Renewables share vs intensity | **−0.4597069597069597** | **0.01584450894242061** | 27 | −0.4597069597069597 | **Exact** |
| Low-carbon share vs intensity | **−0.9316239316239315** | **1.727048666117455×10⁻¹²** | 27 | −0.9316239316239315 | **Exact** |

Rounded as typically shown on slides: ρ ≈ **−0.46** (p ≈ 0.016) and ρ ≈ **−0.93** (p ≈ 1.7×10⁻¹²).

### 2.2 Interpretation constraints (not calculation errors)

- Cross-section of **n = 27** countries; p-values are sensitive to small-n and should not be oversold.
- Spearman measures **monotonic** association, not linear slope and not causation.
- Slide 11’s X (`low_carbon`) **includes nuclear by definition**, so a tighter link with lifecycle intensity is partly definitional / compositional, not an independent “discovery” of a new mechanism.

---

## 3. K-means preprocessing (slide 12)

### 3.1 Feature selection

Five **percentage-of-generation** shares: solar, wind, hydro, nuclear, fossil (see §1.2).  
Countries with any NA in these five are dropped; in 2025 none were.

### 3.2 StandardScaler

```201:201:analysis.py
        standardized = StandardScaler().fit_transform(cluster_d[mix_cols])
```

- **What it does:** for each feature \(j\), \(z_{ij} = (x_{ij} - \bar x_j) / s_j\) with population std (`sklearn` default, `with_std=True`, `with_mean=True`).
- **Why:** K-means uses Euclidean distance; features are on similar %-point scales but have different variances (e.g. nuclear spreads more than solar in this sample). Scaling prevents high-variance features from dominating.

**Fitted 2025 scale parameters (recalc):**

| Feature | mean (`scaler.mean_`) | scale (`scaler.scale_`) |
| --- | ---: | ---: |
| solar | 14.319 | 7.518 |
| wind | 17.288 | 14.460 |
| hydro | 13.082 | 15.589 |
| nuclear | 16.248 | 21.694 |
| fossil | 31.723 | 20.975 |

After scaling: column means ≈ 0, column stds = 1 (verified).

### 3.3 KMeans hyperparameters

```203:209:analysis.py
        for k in range(2,min(5,len(cluster_d)-1)+1):
            labels = KMeans(n_clusters=k, n_init=20, random_state=42).fit_predict(standardized)
            if len(set(labels)) > 1:
                scores[k] = float(silhouette_score(standardized, labels))
        if scores:
            k = max(scores, key=scores.get)
            cluster_d['cluster'] = KMeans(n_clusters=k,n_init=20,random_state=42).fit_predict(standardized) + 1
```

| Parameter | Value | Meaning |
| --- | --- | --- |
| `n_clusters` | candidate \(k \in \{2,3,4,5\}\) | Number of groups |
| `n_init` | **20** | Number of centroid initializations; best inertia kept |
| `random_state` | **42** | Fixes initialization seed → reproducible labels |
| Other defaults | `algorithm='lloyd'` (sklearn ≥1.3 typical default path) | Standard EM-style K-means |
| Label shift | `+ 1` | Clusters reported as 1…k (not 0…k−1) |

Silhouette is computed on the **same standardized matrix** used for K-means (`silhouette_score(standardized, labels)`).

---

## 4. Silhouette scores for k = 2…5 (recalculated)

| k | Silhouette (recalc) | Silhouette (saved JSON) | Match |
| ---: | ---: | ---: | --- |
| 2 | 0.2691081114394806 | 0.2691081114394806 | Exact |
| 3 | 0.28865849471444094 | 0.28865849471444094 | Exact |
| 4 | 0.2729514211338842 | 0.2729514211338842 | Exact |
| **5** | **0.2988777366819775** | **0.2988777366819775** | Exact |

All scores are in a **narrow band ≈ 0.27–0.30** (weak separation by usual rules of thumb).

---

## 5. Why k = 5 was selected

**Rule in code:** `k = max(scores, key=scores.get)` — choose the candidate with the **maximum silhouette**.

- Max is **k = 5** with silhouette **0.298877…**
- Next best is k = 3 (0.2887), then k = 4 (0.2730), then k = 2 (0.2691).

**Verification:** independent recalculation with the same `StandardScaler` + `KMeans(n_init=20, random_state=42)` reproduces the same ranking and the same winning k.

**Caveat (methodological, not a bug):** the margin over k=3 is only ≈ **0.010**. Selecting “best of weak” silhouettes does **not** imply five natural regimes exist. The presentation correctly flags silhouette ≈ 0.30 as weak.

---

## 6. PCA explained variance (PC1, PC2)

Code fits PCA on the **same standardized features** (not on raw %):

```210:212:analysis.py
            pcs = PCA(n_components=2).fit_transform(standardized)
            model = PCA(n_components=2).fit(standardized)
            cluster_d['pc1'],cluster_d['pc2'] = pcs[:,0],pcs[:,1]
```

### 6.1 Recalculated ratios

| Component | Explained variance ratio |
| --- | ---: |
| **PC1** | **0.3971618014330294** (≈ **39.7%**) |
| **PC2** | **0.2676983906174745** (≈ **26.8%**) |
| **PC1 + PC2** | **0.664860192050504** (≈ **66.5%**) |

Saved JSON stores only the sum under `pca_two_components_variance` = 0.664860192050504 — **matches**. Axis labels on fig 07 use the per-component percentages via `model.explained_variance_ratio_`.

### 6.2 Loadings (audit only; interpret cautiously)

On standardized features `[solar, wind, hydro, nuclear, fossil]`:

- **PC1:** ≈ (−0.52, −0.20, +0.40, +0.54, −0.49) → higher nuclear/hydro, lower solar/fossil.
- **PC2:** ≈ (0.00, +0.74, +0.28, −0.37, −0.48) → higher wind, lower nuclear/fossil.

### 6.3 Minor code note (not affecting saved numbers)

PCA is fit **twice** (`fit_transform` then a separate `fit`). Results are identical for this deterministic SVD; it is redundant, not a numerical error. Cluster assignments are **not** computed in PCA space; PCA is for 2D display only.

---

## 7. Country table (cluster, PC1, PC2, five features)

Full machine-readable export (recalculated; labels match `clusters_2025.csv` within float noise ≤ 1e−15):

**File:** `outputs/audit_2025_clusters_table.csv`

Columns: `country`, `iso_code`, `cluster`, `pc1`, `pc2`,  
`solar_electricity_share_pct`, `wind_electricity_share_pct`, `hydro_electricity_share_pct`,  
`nuclear_electricity_share_pct`, `fossil_fuels_electricity_share_pct`.

### 7.1 Cluster membership (k=5), 2025

| Cluster | Countries (ISO3) | n |
| ---: | --- | ---: |
| 1 | CYP, DEU, EST, GRC, IRL, ITA, MLT, NLD, POL | 9 |
| 2 | CZE, FIN, FRA, SVK, SVN | 5 |
| 3 | AUT, HRV, LVA, PRT, ROU, SWE | 6 |
| 4 | DNK, LTU, LUX | 3 |
| 5 | BEL, BGR, HUN, ESP | 4 |

**Check vs saved file:** 0 cluster-label mismatches; max \|ΔPC1\| / \|ΔPC2\| ≈ 1e−15.

---

## 8. Methodological limitations and calculation checks

### 8.1 Calculation integrity

| Check | Result |
| --- | --- |
| Spearman ρ / p vs `statistics_and_sources.json` | **Exact match** |
| Silhouette grid k=2…5 vs JSON | **Exact match** |
| Selected k | **5**, same rule (`argmax` silhouette) |
| PCA PC1+PC2 vs JSON | **Exact match** |
| Cluster labels / PC coords vs `clusters_2025.csv` | **Identical** (float noise only) |

**No calculation errors found** in the 2025 Spearman or K-means/PCA pipeline relative to the saved outputs used by the slides.

### 8.2 Methodological limitations (should stay explicit on slides)

1. **Small n (27)** for both Spearman and clustering; silhouette differences across k are tiny.
2. **Weak structure:** all silhouettes ≈ 0.27–0.30 → clusters are exploratory visual aids, not validated typologies.
3. **Compositional / incomplete feature set:** the five clustering features are **not a closed electricity mix**. Sum of solar+wind+hydro+nuclear+fossil in 2025 ranges roughly **73–100%** (e.g. Luxembourg ≈ 73%). Bioenergy and other renewables are omitted, so K-means does not see the full portfolio.
4. **Related to (3):** `renewables_electricity_share_pct` is **not** equal to solar+wind+hydro (median gap ≈ 5.8 pp in this sample) because renewables include bioenergy etc.
5. **Definitional overlap (slides 10–11):** comparing renewables-only vs low-carbon (RE+nuclear) against intensity is informative, but low-carbon’s stronger ρ is expected when nuclear is low-lifecycle and enters X by construction.
6. **No generation weights in slides 10–12:** each country is one point (Malta = France). That is appropriate for cross-country association/clustering, but differs from EU trend slides that weight by TWh.
7. **No uncertainty on cluster assignment;** `random_state=42` fixes one solution, not the uniqueness of partitions.
8. **PCA is descriptive display only;** K-means was run in 5-D standardized space, not on PC1–PC2.
9. **p-values** assume standard scipy Spearman tests; they ignore spatial/dependence structure among neighbouring countries.

### 8.3 What this audit does *not* claim

- Does not re-fit alternative distance metrics, hierarchical clustering, or bootstrap silhouettes.
- Does not alter slide text, figures, or `analysis.py`.
- Does not treat 2025 cluster IDs as comparable to 2024 cluster IDs (different year → different fit; labels are arbitrary).

---

## 9. Reproducibility commands

```bash
python analysis.py --year 2025
# Then independently (as done for this audit):
# StandardScaler + KMeans(n_init=20, random_state=42) + silhouette for k=2..5
# spearmanr on the column pairs listed in §1.1
```

Pinned source CSV:  
https://catalog.ourworldindata.org/garden/energy/2026-09-10/owid_energy/owid_energy.csv

---

## 10. Bottom line

- Slides **10–11** correctly report 2025 Spearman results: ρ≈−0.46 (renewables) and ρ≈−0.93 (low-carbon), n=27; **recalculated identically**.
- Slide **12** correctly reports **k=5** as the max-silhouette choice among {2,3,4,5}, silhouette≈**0.30**, PCA 2D≈**66.5%** (PC1≈39.7%, PC2≈26.8%); **recalculated identically**.
- **No arithmetic bugs** detected versus saved outputs.
- Main scientific caveats are **weak silhouette**, **small n**, **incomplete/compositional feature set for clustering**, and **non-causal** reading of correlations.

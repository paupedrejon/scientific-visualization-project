"""EU-27 electricity transition analysis (Scientific Visualization project).

Data: Our World in Data Energy dataset, version 2026-09-10.
Source: https://catalog.ourworldindata.org/energy/owid_energy/
Usage: python analysis.py --year 2024

Statistics and figures are computed from the downloaded CSV. Missing required
columns raise an error instead of being filled in.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

BASE = Path(__file__).resolve().parent
DATA_DIR = BASE / "data"
OUT = BASE / "outputs"
FIG = OUT / "figures"
DATA_URL = "https://catalog.ourworldindata.org/garden/energy/2026-09-10/owid_energy/owid_energy.csv"
CODEBOOK_URL = "https://catalog.ourworldindata.org/garden/energy/2026-09-10/owid_energy/owid_energy.codebook.csv"
EU_27 = {
    'AUT','BEL','BGR','HRV','CYP','CZE','DNK','EST','FIN','FRA','DEU',
    'GRC','HUN','IRL','ITA','LVA','LTU','LUX','MLT','NLD','POL','PRT',
    'ROU','SVK','SVN','ESP','SWE'
}
C = {
    'year': 'year', 'name': 'country', 'iso': 'iso_code',
    'generation': 'electricity_generation_twh',
    'renew': 'renewables_electricity_share_pct',
    'nuclear': 'nuclear_electricity_share_pct',
    'fossil': 'fossil_fuels_electricity_share_pct',
    'lowcarbon': 'low_carbon_electricity_share_pct',
    'intensity': 'electricity_carbon_intensity_gco2eq_per_kwh',
    'solar': 'solar_electricity_share_pct',
    'wind': 'wind_electricity_share_pct',
    'hydro': 'hydro_electricity_share_pct'
}
COLORS = {'renew':'#16a085','nuclear':'#4868a9','fossil':'#b86f50',
          'intensity':'#6e477c','lowcarbon':'#2a9d8f','other':'#a0aab4'}


def download_data() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / 'owid_energy.csv'
    if path.is_file():
        print(f'Using cached raw data: {path}')
        return path
    print('Downloading frozen OWID source (only on first run) ...')
    try:
        import requests
        with requests.get(DATA_URL, stream=True, timeout=90) as response:
            response.raise_for_status()
            with path.open('wb') as f:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
    except Exception as exc:
        path.unlink(missing_ok=True)
        raise RuntimeError(
            'Unable to download the dataset. Manually download the CSV from:\n'
            f'{DATA_URL}\nSave it as {path}\nOriginal error: {exc}'
        ) from exc
    return path


def save_chart(fig, filename: str):
    fig.savefig(FIG / filename, dpi=190, bbox_inches='tight', facecolor='white')
    plt.close(fig)


def setup_plot():
    plt.rcParams.update({
        'font.family': 'DejaVu Sans', 'font.size': 11, 'axes.titlesize': 16,
        'axes.titleweight': 'bold', 'axes.spines.top': False,
        'axes.spines.right': False, 'axes.grid': True,
        'grid.alpha': .14, 'figure.facecolor': 'white',
        'axes.facecolor': 'white', 'savefig.facecolor': 'white'
    })


def weighted_share(sub: pd.DataFrame, col: str) -> float:
    pair = sub[[C['generation'], col]].dropna()
    pair = pair[pair[C['generation']] > 0]
    return float(np.average(pair[col], weights=pair[C['generation']])) if len(pair) else math.nan


def generate(df: pd.DataFrame, year: int) -> None:
    year_data = df.loc[df['year'] == year].copy()
    if len(year_data) < 20:
        raise RuntimeError(f'Only {len(year_data)} EU country records available for {year}; choose another year.')
    n_all = len(df)
    n_countries = year_data['iso_code'].nunique()
    print(f'EU-27 country-year rows: {n_all}. Coverage in {year}: {n_countries}/27 countries')
    print('Missing per variable for chosen year:')
    print(year_data[list(C.values())[3:]].isna().sum().to_string())

    # Coverage audit: missing values are excluded per indicator/year (no imputation).
    years = []
    for yr, sub in df.groupby('year'):
        record = {'year': int(yr), 'country_count': int(len(sub))}
        for key in ('renew','nuclear','fossil','lowcarbon','intensity'):
            record[f'countries_with_{key}'] = int(sub[C[key]].notna().sum())
            record[f'eu_generation_weighted_{key}'] = weighted_share(sub, C[key])
        years.append(record)
    yearly = pd.DataFrame(years).sort_values('year')
    yearly.to_csv(OUT / 'yearly_coverage_and_weighted_indicators.csv', index=False)
    year_data.sort_values('country').to_csv(OUT / f'country_profiles_{year}.csv', index=False)

    # Figure 1 - trend; weighted shares by generation, not average of countries.
    line = yearly.loc[yearly['year'].between(2010, year)]
    fig, ax = plt.subplots(figsize=(11, 5.6))
    for key, label in [('renew','Renewable'),('nuclear','Nuclear'),('fossil','Fossil')]:
        ax.plot(line['year'], line[f'eu_generation_weighted_{key}'],
                label=label, color=COLORS[key], linewidth=2.7, marker='o', markersize=3)
    ax.set(title='EU-27 electricity mix: the long-term transition',
           ylabel='Share of electricity generation (%)', xlabel='Year', ylim=(0, 100))
    ax.legend(frameon=False, ncol=3)
    ax.text(0, -.21, 'Country shares weighted by national electricity generation (TWh). Only available country-year records.',
            transform=ax.transAxes, fontsize=9, color='#56606b')
    save_chart(fig, '01_eu_electricity_mix_trend.png')

    # Figure 2 - total carbon intensity annual trend, weighted by generation.
    fig, ax = plt.subplots(figsize=(11, 5.2))
    ax.plot(line['year'], line['eu_generation_weighted_intensity'],
            marker='o', linewidth=2.8, color=COLORS['intensity'])
    ax.set(title='EU-27 lifecycle carbon intensity of electricity',
           ylabel='gCO₂eq / kWh of generated electricity', xlabel='Year')
    ax.text(0, -.22, 'Generation-weighted country averages; lifecycle emissions. Report yearly coverage before interpreting.',
            transform=ax.transAxes, fontsize=9, color='#56606b')
    save_chart(fig, '02_carbon_intensity_trend.png')

    # Figure 3 - all-country 2024 rank; no hidden rows.
    d = year_data.dropna(subset=[C['lowcarbon']]).sort_values(C['lowcarbon'])
    fig, ax = plt.subplots(figsize=(11, 10))
    ax.barh(d['country'], d[C['lowcarbon']], color=COLORS['renew'], height=.73)
    ax.set(title=f'Low-carbon electricity share by EU country · {year}',
           xlabel='Share (%)', xlim=(0, 105))
    for i, val in enumerate(d[C['lowcarbon']]):
        ax.text(min(val + 1, 100), i, f'{val:.0f}%', va='center', fontsize=8)
    save_chart(fig, '03_low_carbon_ranking.png')

    # Figure 4 - compare what correlates with carbon intensity, using two scatters.
    stats = {}
    for key, label, out_name in [
        ('renew','Renewable share','04_renewables_vs_intensity.png'),
        ('lowcarbon','Low-carbon share (renewables + nuclear)','05_lowcarbon_vs_intensity.png')]:
        paired = year_data.dropna(subset=[C[key],C['intensity']]).copy()
        r, p = spearmanr(paired[C[key]], paired[C['intensity']]) if len(paired) >= 5 else (math.nan, math.nan)
        stats[key] = {'n':int(len(paired)), 'spearman_rho':float(r), 'p_value':float(p)}
        fig, ax = plt.subplots(figsize=(10.6, 6.3))
        ax.scatter(paired[C[key]], paired[C['intensity']], s=58,
                   c=COLORS['lowcarbon'] if key=='lowcarbon' else COLORS['renew'],
                   alpha=.84, edgecolor='white', linewidth=.7)
        for _, row in paired.iterrows():
            if row['iso_code'] in {'FRA','DEU','ITA','ESP','SWE','POL','DNK','CZE'}:
                ax.annotate(row['iso_code'],(row[C[key]],row[C['intensity']]),
                            xytext=(5,4),textcoords='offset points',fontsize=8)
        ax.set(title=f'{label} vs. carbon intensity · {year}',
               xlabel=f'{label} (%)', ylabel='gCO₂eq / kWh')
        ax.text(.01,.97, f'Spearman ρ = {r:.2f}  |  p = {p:.3g}  |  n = {len(paired)}',
                transform=ax.transAxes, va='top', fontsize=10, color='#454c58',
                bbox=dict(facecolor='white', edgecolor='none', alpha=.9))
        ax.text(0,-.19,'Cross-sectional association, not a causal effect. Countries are observations.',
                transform=ax.transAxes, fontsize=9, color='#56606b')
        save_chart(fig,out_name)

    # Figure 5 - 100% mix by source, missing excluded, remainder shown explicitly.
    mixes = year_data.dropna(subset=[C['renew'],C['nuclear'],C['fossil']]).copy()
    mixes['remaining'] = 100 - mixes[[C['renew'],C['nuclear'],C['fossil']]].sum(axis=1)
    mixes = mixes.loc[mixes['remaining'] >= -1.5].copy()
    mixes['remaining'] = mixes['remaining'].clip(lower=0)
    mixes.sort_values(C['fossil'], inplace=True)
    fig, ax = plt.subplots(figsize=(11, 10))
    left = np.zeros(len(mixes))
    for key,label,col in [('renew','Renewables',COLORS['renew']),
                          ('nuclear','Nuclear',COLORS['nuclear']),
                          ('fossil','Fossil',COLORS['fossil']),
                          ('remaining','Other / rounding',COLORS['other'])]:
        v = mixes[C[key]].values if key!='remaining' else mixes['remaining'].values
        ax.barh(mixes['country'],v,left=left,label=label,color=col,height=.7)
        left += v
    ax.set(title=f'Electricity generation mix across EU-27 · {year}', xlabel='Share (%)', xlim=(0,101))
    ax.legend(frameon=False, ncol=4, loc='lower center', bbox_to_anchor=(.5,-.12))
    save_chart(fig, '06_electricity_mix_by_country.png')

    # Figure 6 - exploratory clustering of five electricity portfolio variables.
    mix_cols = [C[x] for x in ('solar','wind','hydro','nuclear','fossil')]
    cluster_d = year_data.dropna(subset=mix_cols).copy()
    if len(cluster_d) >= 12:
        standardized = StandardScaler().fit_transform(cluster_d[mix_cols])
        scores = {}
        for k in range(2,min(5,len(cluster_d)-1)+1):
            labels = KMeans(n_clusters=k, n_init=20, random_state=42).fit_predict(standardized)
            if len(set(labels)) > 1:
                scores[k] = float(silhouette_score(standardized, labels))
        if scores:
            k = max(scores, key=scores.get)
            cluster_d['cluster'] = KMeans(n_clusters=k,n_init=20,random_state=42).fit_predict(standardized) + 1
            pcs = PCA(n_components=2).fit_transform(standardized)
            model = PCA(n_components=2).fit(standardized)
            cluster_d['pc1'],cluster_d['pc2'] = pcs[:,0],pcs[:,1]
            fig, ax = plt.subplots(figsize=(10,7))
            cmap = plt.get_cmap('tab10')
            for i, sub in cluster_d.groupby('cluster'):
                ax.scatter(sub['pc1'],sub['pc2'],s=62,alpha=.85,label=f'Cluster {i}',color=cmap((i-1)%10))
                for _, row in sub.iterrows():
                    ax.annotate(row['iso_code'],(row['pc1'],row['pc2']),xytext=(4,4),textcoords='offset points',fontsize=8)
            ax.set(title=f'EU electricity profiles · K-means + PCA ({year})',
                   xlabel=f'PC1 ({model.explained_variance_ratio_[0]:.0%} variance)',
                   ylabel=f'PC2 ({model.explained_variance_ratio_[1]:.0%} variance)')
            ax.legend(frameon=False)
            ax.text(0,-.20,f'k={k}, silhouette={scores[k]:.2f}; clustering is exploratory, not a ground-truth classification.',
                    transform=ax.transAxes,fontsize=9,color='#56606b')
            save_chart(fig,'07_country_clusters_pca.png')
            cluster_d[['country','iso_code','cluster','pc1','pc2']+mix_cols].to_csv(
                OUT/f'clusters_{year}.csv',index=False)
            stats['clustering']={'k':int(k),'silhouette_score':float(scores[k]),
                                 'candidate_silhouettes':scores,'n':int(len(cluster_d)),
                                 'pca_two_components_variance':float(sum(model.explained_variance_ratio_))}

    stats['source'] = DATA_URL
    stats['dataset_version'] = '2026-09-10'
    stats['year'] = year
    stats['eu_country_rows_selected'] = n_countries
    stats['assumptions'] = [
        'EU27 only, filtered using ISO3 country codes; regional aggregates excluded.',
        'All charts derive exclusively from the OWID Energy 2026-09-10 extract.',
        '2010–selected year trends are generation-weighted from available country-year records.',
        'Lifecycle carbon intensity includes CO2-equivalent greenhouse gases.',
        '2024 cross-sectional correlations are descriptive and do not demonstrate causality.',
        'K-means on portfolios is exploratory; interpret small samples and silhouette cautiously.'
    ]
    (OUT/'statistics_and_sources.json').write_text(json.dumps(stats,indent=2,ensure_ascii=False),encoding='utf8')
    print('\nReady. Graphs and statistics saved to:',OUT)
    print('Spearman correlations:')
    for key in ('renew','lowcarbon'):
        print(key,stats[key])
    if 'clustering' in stats:
        print('Clustering:',stats['clustering'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--year', type=int, default=2024,
                        help='Cross-section year (default 2024 to avoid partial 2025 coverage)')
    args = parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    FIG.mkdir(parents=True,exist_ok=True)
    setup_plot()
    source_file = download_data()
    df = pd.read_csv(source_file,low_memory=False)
    required = list(C.values())
    absent = sorted(set(required)-set(df.columns))
    if absent:
        raise RuntimeError(f'Source schema changed; missing required columns: {absent}. Consult OWID codebook.')
    df = df[df['iso_code'].isin(EU_27) & df['year'].between(2010,args.year)].copy()
    for col in required[3:]:
        df[col] = pd.to_numeric(df[col],errors='coerce')
    generate(df,args.year)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Analysis Results - Non-interactive version
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from scipy import stats
from scipy.stats import pearsonr, spearmanr, ttest_ind, mannwhitneyu
import warnings
warnings.filterwarnings('ignore')
import json

# File paths
BASE_PATH = "/Users/jamesacer/Library/CloudStorage/OneDrive-Personal/Syntropy_Haze_OneDrive/SH_GitHub/data_for_blinded_flame_analysis_Jan13/"
OUTPUT_PATH = BASE_PATH + "analysis_output/"

import os
os.makedirs(OUTPUT_PATH, exist_ok=True)

def parse_timestamp(ts_str):
    if pd.isna(ts_str):
        return None
    try:
        if ':' in str(ts_str):
            if '2026' in str(ts_str):
                return pd.to_datetime(ts_str)
            else:
                return pd.to_datetime(f"2026-01-12 {ts_str}")
    except:
        return None

# Load timestamp data
timestamps_df = pd.read_excel(f"{BASE_PATH}COPY_timestamps_flame_play.xlsm")

# Extract markers
run1_markers = []
run2_markers = []
for idx in range(5, len(timestamps_df)):
    label = timestamps_df.iloc[idx, 1]
    ts1 = timestamps_df.iloc[idx, 2]
    ts2 = timestamps_df.iloc[idx, 8]

    if not pd.isna(label):
        if not pd.isna(ts1):
            parsed_ts = parse_timestamp(ts1)
            if parsed_ts:
                run1_markers.append({'label': str(label).strip(), 'timestamp': parsed_ts})

        if not pd.isna(ts2):
            parsed_ts = parse_timestamp(ts2)
            if parsed_ts:
                run2_markers.append({'label': str(label).strip(), 'timestamp': parsed_ts})

# Load light meter data
light_files = {
    'Run1_A': 'lightmeter_2026-01-12_00-47-53_TwinFlame1_CandleA.csv',
    'Run1_B': 'lightmeter_2026-01-12_00-48-13_TwinFlame1_CandleB.csv',
    'Run2_A': 'lightmeter_2026-01-12_02-11-46_TwinFlame2_CandleA.csv',
    'Run2_B': 'lightmeter_2026-01-12_02-12-00_TwinFlame2_CandleB.csv'
}

end_times = {
    'Run1_A': datetime.strptime('2026-01-12 00:47:53', '%Y-%m-%d %H:%M:%S'),
    'Run1_B': datetime.strptime('2026-01-12 00:48:13', '%Y-%m-%d %H:%M:%S'),
    'Run2_A': datetime.strptime('2026-01-12 02:11:46', '%Y-%m-%d %H:%M:%S'),
    'Run2_B': datetime.strptime('2026-01-12 02:12:00', '%Y-%m-%d %H:%M:%S')
}

light_data = {}
for key, filename in light_files.items():
    df = pd.read_csv(f"{BASE_PATH}{filename}")
    duration = df['time'].max()
    start_time = end_times[key] - timedelta(seconds=duration)
    df['timestamp'] = pd.to_datetime(start_time) + pd.to_timedelta(df['time'], unit='s')
    light_data[key] = df

# Classify periods
def classify_periods(df, markers):
    df['period'] = 'Unknown'

    for i in range(len(markers) - 1):
        start = markers[i]['timestamp']
        end = markers[i + 1]['timestamp']
        label = markers[i]['label'].lower()
        mask = (df['timestamp'] >= start) & (df['timestamp'] < end)

        if 'start control' in label:
            df.loc[mask, 'period'] = 'Control'
        elif 'start 1st light' in label:
            df.loc[mask, 'period'] = 'Condition_A'
        elif 'start 2nd light' in label:
            df.loc[mask, 'period'] = 'Condition_B'
        elif 'start 1st + 2nd' in label or 'double' in label.lower():
            df.loc[mask, 'period'] = 'Condition_AB'
        elif 'end' in label:
            df.loc[mask, 'period'] = 'Lag/Control'

    return df

light_data['Run1_A'] = classify_periods(light_data['Run1_A'], run1_markers)
light_data['Run1_B'] = classify_periods(light_data['Run1_B'], run1_markers)
light_data['Run2_A'] = classify_periods(light_data['Run2_A'], run2_markers)
light_data['Run2_B'] = classify_periods(light_data['Run2_B'], run2_markers)

# Statistical Analysis
def analyze_conditions(df):
    results = {}
    control_data = df[df['period'] == 'Control']['lux']

    if len(control_data) > 0:
        results['control_mean'] = control_data.mean()
        results['control_std'] = control_data.std()
        results['control_median'] = control_data.median()
        results['control_n'] = len(control_data)

    for condition in ['Condition_A', 'Condition_B', 'Condition_AB']:
        cond_data = df[df['period'] == condition]['lux']
        if len(cond_data) > 0 and len(control_data) > 0:
            results[f'{condition}_mean'] = cond_data.mean()
            results[f'{condition}_std'] = cond_data.std()
            results[f'{condition}_median'] = cond_data.median()
            results[f'{condition}_n'] = len(cond_data)

            pooled_std = np.sqrt((control_data.var() + cond_data.var()) / 2)
            if pooled_std > 0:
                results[f'{condition}_effect_size'] = (cond_data.mean() - control_data.mean()) / pooled_std

            t_stat, p_val = ttest_ind(control_data, cond_data)
            results[f'{condition}_ttest_pval'] = p_val

            u_stat, p_val_mw = mannwhitneyu(control_data, cond_data)
            results[f'{condition}_mannwhitney_pval'] = p_val_mw

            results[f'{condition}_percent_change'] = ((cond_data.mean() - control_data.mean()) / control_data.mean()) * 100

    return results

# Cross-correlation Analysis
def analyze_correlation(df_a, df_b):
    merged = pd.merge_asof(
        df_a.sort_values('timestamp')[['timestamp', 'lux', 'period']].rename(columns={'lux': 'lux_a'}),
        df_b.sort_values('timestamp')[['timestamp', 'lux']].rename(columns={'lux': 'lux_b'}),
        on='timestamp',
        direction='nearest',
        tolerance=pd.Timedelta('100ms')
    )

    correlations = {}
    for period in merged['period'].unique():
        if period != 'Unknown':
            period_data = merged[merged['period'] == period]
            if len(period_data) > 10:
                pearson_r, pearson_p = pearsonr(period_data['lux_a'], period_data['lux_b'])
                spearman_r, spearman_p = spearmanr(period_data['lux_a'], period_data['lux_b'])
                correlations[period] = {
                    'pearson_r': float(pearson_r),
                    'pearson_p': float(pearson_p),
                    'spearman_r': float(spearman_r),
                    'spearman_p': float(spearman_p),
                    'n_samples': int(len(period_data))
                }

    return correlations

# Run all analyses and save results
all_results = {
    'statistical_analysis': {},
    'correlation_analysis': {}
}

print("\n" + "="*80)
print("STATISTICAL ANALYSIS RESULTS")
print("="*80)

for key, df in light_data.items():
    results = analyze_conditions(df)
    all_results['statistical_analysis'][key] = results

    print(f"\n{key} Analysis:")
    print(f"  Control: mean={results.get('control_mean', 0):.2f} ± {results.get('control_std', 0):.2f} (n={results.get('control_n', 0)})")

    for condition in ['Condition_A', 'Condition_B', 'Condition_AB']:
        if f'{condition}_mean' in results:
            print(f"  {condition}:")
            print(f"    Mean: {results[f'{condition}_mean']:.2f} ± {results[f'{condition}_std']:.2f} (n={results[f'{condition}_n']})")
            print(f"    % Change from Control: {results[f'{condition}_percent_change']:.1f}%")
            print(f"    Effect Size (Cohen's d): {results.get(f'{condition}_effect_size', 0):.3f}")
            p_val = results[f'{condition}_ttest_pval']
            sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "ns"
            print(f"    Statistical Significance: p={p_val:.6f} {sig}")

print("\n" + "="*80)
print("CROSS-CORRELATION ANALYSIS")
print("="*80)

for run_num in [1, 2]:
    correlations = analyze_correlation(
        light_data[f'Run{run_num}_A'],
        light_data[f'Run{run_num}_B']
    )
    all_results['correlation_analysis'][f'Run{run_num}'] = correlations

    print(f"\nRun {run_num} Sensor Correlations:")
    for period, corr_data in correlations.items():
        r = corr_data['pearson_r']
        p = corr_data['pearson_p']
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
        print(f"  {period}:")
        print(f"    Pearson r = {r:.3f} (p = {p:.6f}) {sig}")
        print(f"    Spearman r = {corr_data['spearman_r']:.3f} (p = {corr_data['spearman_p']:.6f})")
        print(f"    N = {corr_data['n_samples']}")

# Save results to JSON
with open(f'{OUTPUT_PATH}analysis_results.json', 'w') as f:
    json.dump(all_results, f, indent=2, default=str)

print("\n" + "="*80)
print("KEY FINDINGS SUMMARY")
print("="*80)

# Summarize key findings
significant_effects = []
for key, results in all_results['statistical_analysis'].items():
    for condition in ['Condition_A', 'Condition_B', 'Condition_AB']:
        if f'{condition}_ttest_pval' in results and results[f'{condition}_ttest_pval'] < 0.05:
            significant_effects.append({
                'sensor': key,
                'condition': condition,
                'percent_change': results[f'{condition}_percent_change'],
                'p_value': results[f'{condition}_ttest_pval'],
                'effect_size': results.get(f'{condition}_effect_size', 0)
            })

if significant_effects:
    print("\nStatistically Significant Effects (p < 0.05):")
    for effect in sorted(significant_effects, key=lambda x: abs(x['percent_change']), reverse=True):
        print(f"  • {effect['sensor']} - {effect['condition']}: {effect['percent_change']:.1f}% change (d={effect['effect_size']:.3f}, p={effect['p_value']:.6f})")

# Pattern observations
print("\nSensor Correlation Patterns:")
for run_num in [1, 2]:
    corrs = all_results['correlation_analysis'][f'Run{run_num}']
    strong_corrs = [(period, data['pearson_r']) for period, data in corrs.items() if abs(data['pearson_r']) > 0.5]
    if strong_corrs:
        print(f"  Run {run_num}: Strong correlations (|r| > 0.5) found in {', '.join([f'{p} (r={r:.3f})' for p, r in strong_corrs])}")

print("\nAnalysis complete! Results saved to:", OUTPUT_PATH)
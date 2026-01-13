#!/usr/bin/env python3
"""
Complete Blind Analysis of Luminosity Data with Visualizations
Author: Claude
Date: January 13, 2025
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from scipy import stats
from scipy.signal import correlate, detrend, find_peaks
from scipy.stats import pearsonr, spearmanr, ttest_ind, mannwhitneyu
import warnings
warnings.filterwarnings('ignore')

# Set up plotting style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 10)

# File paths
BASE_PATH = "/Users/jamesacer/Library/CloudStorage/OneDrive-Personal/Syntropy_Haze_OneDrive/SH_GitHub/data_for_blinded_flame_analysis_Jan13/"
OUTPUT_PATH = BASE_PATH + "analysis_output/"

# Create output directory
import os
os.makedirs(OUTPUT_PATH, exist_ok=True)

def parse_timestamp(ts_str):
    """Parse timestamp string to datetime object"""
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

# Load and parse timestamp data
print("Loading and parsing timestamp data...")
timestamps_df = pd.read_excel(f"{BASE_PATH}COPY_timestamps_flame_play.xlsm")

# Extract Run 1 timestamps
run1_markers = []
for idx in range(5, len(timestamps_df)):
    label = timestamps_df.iloc[idx, 1]
    ts = timestamps_df.iloc[idx, 2]
    if not pd.isna(label) and not pd.isna(ts):
        parsed_ts = parse_timestamp(ts)
        if parsed_ts:
            run1_markers.append({'label': str(label).strip(), 'timestamp': parsed_ts})

# Extract Run 2 timestamps
run2_markers = []
for idx in range(5, len(timestamps_df)):
    label = timestamps_df.iloc[idx, 1]
    ts = timestamps_df.iloc[idx, 8]
    if not pd.isna(label) and not pd.isna(ts):
        parsed_ts = parse_timestamp(ts)
        if parsed_ts:
            run2_markers.append({'label': str(label).strip(), 'timestamp': parsed_ts})

# Load light meter data
print("\nLoading light meter data...")
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

# Function to classify periods
def classify_periods(df, markers):
    df['period'] = 'Unknown'
    df['detailed_period'] = 'Unknown'

    for i in range(len(markers) - 1):
        start = markers[i]['timestamp']
        end = markers[i + 1]['timestamp']
        label = markers[i]['label'].lower()
        mask = (df['timestamp'] >= start) & (df['timestamp'] < end)

        if 'start control' in label:
            df.loc[mask, 'period'] = 'Control'
            df.loc[mask, 'detailed_period'] = label
        elif 'start 1st light' in label:
            df.loc[mask, 'period'] = 'Condition_A'
            df.loc[mask, 'detailed_period'] = label
        elif 'start 2nd light' in label:
            df.loc[mask, 'period'] = 'Condition_B'
            df.loc[mask, 'detailed_period'] = label
        elif 'start 1st + 2nd' in label or 'double' in label.lower():
            df.loc[mask, 'period'] = 'Condition_AB'
            df.loc[mask, 'detailed_period'] = label
        elif 'end' in label:
            df.loc[mask, 'period'] = 'Lag/Control'
            df.loc[mask, 'detailed_period'] = 'lag_period'

    return df

# Classify periods
light_data['Run1_A'] = classify_periods(light_data['Run1_A'], run1_markers)
light_data['Run1_B'] = classify_periods(light_data['Run1_B'], run1_markers)
light_data['Run2_A'] = classify_periods(light_data['Run2_A'], run2_markers)
light_data['Run2_B'] = classify_periods(light_data['Run2_B'], run2_markers)

# Statistical Analysis
def analyze_conditions(df, run_name, sensor_name):
    results = {}
    control_data = df[df['period'] == 'Control']['lux']

    if len(control_data) > 0:
        results['control_mean'] = control_data.mean()
        results['control_std'] = control_data.std()
        results['control_median'] = control_data.median()

    for condition in ['Condition_A', 'Condition_B', 'Condition_AB']:
        cond_data = df[df['period'] == condition]['lux']
        if len(cond_data) > 0 and len(control_data) > 0:
            results[f'{condition}_mean'] = cond_data.mean()
            results[f'{condition}_std'] = cond_data.std()
            results[f'{condition}_median'] = cond_data.median()

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
def analyze_correlation(df_a, df_b, run_name):
    """Analyze correlation between two sensors"""
    # Align timestamps
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
                    'pearson_r': pearson_r,
                    'pearson_p': pearson_p,
                    'spearman_r': spearman_r,
                    'spearman_p': spearman_p,
                    'n_samples': len(period_data)
                }

    return correlations, merged

# MAIN VISUALIZATION FUNCTION
def create_visualizations():
    """Create comprehensive visualizations"""

    # 1. Time series plot for each run
    for run_num in [1, 2]:
        fig, axes = plt.subplots(3, 1, figsize=(18, 12), sharex=True)

        # Get data for this run
        df_a = light_data[f'Run{run_num}_A']
        df_b = light_data[f'Run{run_num}_B']

        # Get markers for this run
        markers = run1_markers if run_num == 1 else run2_markers

        # Plot sensor A
        ax = axes[0]
        ax.plot(df_a['timestamp'], df_a['lux'], 'b-', alpha=0.6, linewidth=0.5, label='Sensor A')
        ax.set_ylabel('Luminosity (lux)', fontsize=12)
        ax.set_title(f'Run {run_num} - Sensor A', fontsize=14, fontweight='bold')

        # Add condition shading
        for period, color in [('Control', 'gray'), ('Condition_A', 'red'),
                               ('Condition_B', 'green'), ('Condition_AB', 'purple')]:
            period_data = df_a[df_a['period'] == period]
            if len(period_data) > 0:
                for i, group in period_data.groupby((period_data['timestamp'].diff() > pd.Timedelta(seconds=10)).cumsum()):
                    ax.axvspan(group['timestamp'].min(), group['timestamp'].max(),
                              alpha=0.2, color=color, label=period if i == 0 else '')

        # Plot sensor B
        ax = axes[1]
        ax.plot(df_b['timestamp'], df_b['lux'], 'r-', alpha=0.6, linewidth=0.5, label='Sensor B')
        ax.set_ylabel('Luminosity (lux)', fontsize=12)
        ax.set_title(f'Run {run_num} - Sensor B', fontsize=14, fontweight='bold')

        # Add condition shading
        for period, color in [('Control', 'gray'), ('Condition_A', 'red'),
                               ('Condition_B', 'green'), ('Condition_AB', 'purple')]:
            period_data = df_b[df_b['period'] == period]
            if len(period_data) > 0:
                for i, group in period_data.groupby((period_data['timestamp'].diff() > pd.Timedelta(seconds=10)).cumsum()):
                    ax.axvspan(group['timestamp'].min(), group['timestamp'].max(),
                              alpha=0.2, color=color)

        # Plot both sensors together
        ax = axes[2]
        ax.plot(df_a['timestamp'], df_a['lux'], 'b-', alpha=0.6, linewidth=0.5, label='Sensor A')
        ax.plot(df_b['timestamp'], df_b['lux'], 'r-', alpha=0.6, linewidth=0.5, label='Sensor B')
        ax.set_ylabel('Luminosity (lux)', fontsize=12)
        ax.set_xlabel('Time', fontsize=12)
        ax.set_title(f'Run {run_num} - Both Sensors', fontsize=14, fontweight='bold')
        ax.legend(loc='upper right')

        # Add vertical lines for markers
        for marker in markers:
            for ax in axes:
                ax.axvline(marker['timestamp'], color='black', linestyle='--', alpha=0.3, linewidth=0.5)

        axes[0].legend(loc='upper right')
        plt.tight_layout()
        plt.savefig(f"{OUTPUT_PATH}run{run_num}_timeseries.png", dpi=300, bbox_inches='tight')
        plt.show()

    # 2. Box plots comparing conditions
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    for idx, (key, df) in enumerate(light_data.items()):
        ax = axes[idx // 2, idx % 2]

        # Prepare data for box plot
        plot_data = []
        labels = []
        for period in ['Control', 'Condition_A', 'Condition_B', 'Condition_AB']:
            period_data = df[df['period'] == period]['lux']
            if len(period_data) > 0:
                plot_data.append(period_data)
                labels.append(period)

        if plot_data:
            bp = ax.boxplot(plot_data, labels=labels, patch_artist=True)
            colors = ['gray', 'red', 'green', 'purple']
            for patch, color in zip(bp['boxes'], colors[:len(bp['boxes'])]):
                patch.set_facecolor(color)
                patch.set_alpha(0.5)

            ax.set_ylabel('Luminosity (lux)', fontsize=11)
            ax.set_title(f'{key}', fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3)

    plt.suptitle('Luminosity Distribution by Condition', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_PATH}condition_boxplots.png", dpi=300, bbox_inches='tight')
    plt.show()

    # 3. Correlation heatmap
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    for idx, run_num in enumerate([1, 2]):
        correlations, merged = analyze_correlation(
            light_data[f'Run{run_num}_A'],
            light_data[f'Run{run_num}_B'],
            f'Run{run_num}'
        )

        # Create heatmap data
        periods = list(correlations.keys())
        pearson_vals = [correlations[p]['pearson_r'] for p in periods]
        spearman_vals = [correlations[p]['spearman_r'] for p in periods]

        ax = axes[idx]
        im = ax.imshow([[p, s] for p, s in zip(pearson_vals, spearman_vals)],
                      cmap='coolwarm', vmin=-1, vmax=1, aspect='auto')

        ax.set_xticks([0, 1])
        ax.set_xticklabels(['Pearson', 'Spearman'])
        ax.set_yticks(range(len(periods)))
        ax.set_yticklabels(periods)
        ax.set_title(f'Run {run_num} - Sensor Correlations', fontsize=12, fontweight='bold')

        # Add text annotations
        for i, period in enumerate(periods):
            ax.text(0, i, f'{pearson_vals[i]:.3f}', ha='center', va='center')
            ax.text(1, i, f'{spearman_vals[i]:.3f}', ha='center', va='center')

        plt.colorbar(im, ax=ax)

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_PATH}correlation_heatmap.png", dpi=300, bbox_inches='tight')
    plt.show()

# Run all analyses
print("\n" + "="*80)
print("STATISTICAL ANALYSIS RESULTS")
print("="*80)

analysis_results = {}
for key, df in light_data.items():
    run = key.split('_')[0]
    sensor = key.split('_')[1]
    results = analyze_conditions(df, run, sensor)
    analysis_results[key] = results

    print(f"\n{key} Analysis:")
    print(f"  Control: mean={results.get('control_mean', 0):.2f} ± {results.get('control_std', 0):.2f}")

    for condition in ['Condition_A', 'Condition_B', 'Condition_AB']:
        if f'{condition}_mean' in results:
            print(f"  {condition}:")
            print(f"    Mean: {results[f'{condition}_mean']:.2f} ± {results[f'{condition}_std']:.2f}")
            print(f"    % Change: {results[f'{condition}_percent_change']:.2f}%")
            print(f"    Effect Size: {results.get(f'{condition}_effect_size', 0):.3f}")
            print(f"    p-value (t-test): {results[f'{condition}_ttest_pval']:.6f}")

# Cross-correlation results
print("\n" + "="*80)
print("CROSS-CORRELATION ANALYSIS")
print("="*80)

for run_num in [1, 2]:
    correlations, _ = analyze_correlation(
        light_data[f'Run{run_num}_A'],
        light_data[f'Run{run_num}_B'],
        f'Run{run_num}'
    )
    print(f"\nRun {run_num} Sensor Correlations:")
    for period, corr_data in correlations.items():
        print(f"  {period}:")
        print(f"    Pearson r = {corr_data['pearson_r']:.3f} (p = {corr_data['pearson_p']:.6f})")
        print(f"    Spearman r = {corr_data['spearman_r']:.3f} (p = {corr_data['spearman_p']:.6f})")
        print(f"    N samples = {corr_data['n_samples']}")

# Create visualizations
print("\nGenerating visualizations...")
create_visualizations()

print("\n" + "="*80)
print("Analysis complete! Visualizations saved to:", OUTPUT_PATH)
print("="*80)
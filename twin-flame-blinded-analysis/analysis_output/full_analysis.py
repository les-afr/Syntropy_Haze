#!/usr/bin/env python3
"""
Full Blind Analysis of Luminosity Data
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

def parse_timestamp(ts_str):
    """Parse timestamp string to datetime object"""
    if pd.isna(ts_str):
        return None
    try:
        # Try different formats
        if ':' in str(ts_str):
            if '2026' in str(ts_str):
                return pd.to_datetime(ts_str)
            else:
                # It's just a time, add today's date
                return pd.to_datetime(f"2026-01-12 {ts_str}")
    except:
        return None

# Load and parse timestamp data
print("Loading and parsing timestamp data...")
timestamps_df = pd.read_excel(f"{BASE_PATH}COPY_timestamps_flame_play.xlsm")

# Extract Run 1 timestamps (column 3 = Unnamed: 2)
run1_markers = []
for idx in range(5, len(timestamps_df)):
    label = timestamps_df.iloc[idx, 1]  # Unnamed: 1 has the labels
    ts = timestamps_df.iloc[idx, 2]  # Unnamed: 2 has Run 1 timestamps

    if not pd.isna(label) and not pd.isna(ts):
        parsed_ts = parse_timestamp(ts)
        if parsed_ts:
            run1_markers.append({'label': str(label).strip(), 'timestamp': parsed_ts})

# Extract Run 2 timestamps (column 9 = Unnamed: 8)
run2_markers = []
for idx in range(5, len(timestamps_df)):
    label = timestamps_df.iloc[idx, 1]  # Unnamed: 1 has the labels
    ts = timestamps_df.iloc[idx, 8]  # Unnamed: 8 has Run 2 timestamps

    if not pd.isna(label) and not pd.isna(ts):
        parsed_ts = parse_timestamp(ts)
        if parsed_ts:
            run2_markers.append({'label': str(label).strip(), 'timestamp': parsed_ts})

print(f"Run 1 markers: {len(run1_markers)}")
for m in run1_markers:
    print(f"  {m['label']}: {m['timestamp']}")

print(f"\nRun 2 markers: {len(run2_markers)}")
for m in run2_markers:
    print(f"  {m['label']}: {m['timestamp']}")

# Load light meter data
print("\nLoading light meter data...")
light_files = {
    'Run1_A': 'lightmeter_2026-01-12_00-47-53_TwinFlame1_CandleA.csv',
    'Run1_B': 'lightmeter_2026-01-12_00-48-13_TwinFlame1_CandleB.csv',
    'Run2_A': 'lightmeter_2026-01-12_02-11-46_TwinFlame2_CandleA.csv',
    'Run2_B': 'lightmeter_2026-01-12_02-12-00_TwinFlame2_CandleB.csv'
}

# Calculate light meter start times
end_times = {
    'Run1_A': datetime.strptime('2026-01-12 00:47:53', '%Y-%m-%d %H:%M:%S'),
    'Run1_B': datetime.strptime('2026-01-12 00:48:13', '%Y-%m-%d %H:%M:%S'),
    'Run2_A': datetime.strptime('2026-01-12 02:11:46', '%Y-%m-%d %H:%M:%S'),
    'Run2_B': datetime.strptime('2026-01-12 02:12:00', '%Y-%m-%d %H:%M:%S')
}

light_data = {}
for key, filename in light_files.items():
    df = pd.read_csv(f"{BASE_PATH}{filename}")

    # Calculate absolute timestamps for each measurement
    duration = df['time'].max()
    start_time = end_times[key] - timedelta(seconds=duration)
    df['timestamp'] = pd.to_datetime(start_time) + pd.to_timedelta(df['time'], unit='s')

    light_data[key] = df
    print(f"{key}: {len(df)} measurements from {df['timestamp'].min()} to {df['timestamp'].max()}")

# Function to classify periods based on markers
def classify_periods(df, markers):
    """Add period classification to dataframe based on markers"""
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
            df.loc[mask, 'period'] = 'Condition_A'  # First light = Condition A
            df.loc[mask, 'detailed_period'] = label
        elif 'start 2nd light' in label:
            df.loc[mask, 'period'] = 'Condition_B'  # Second light = Condition B
            df.loc[mask, 'detailed_period'] = label
        elif 'start 1st + 2nd' in label or 'double' in label.lower():
            df.loc[mask, 'period'] = 'Condition_AB'
            df.loc[mask, 'detailed_period'] = label
        elif 'end' in label:
            # Lag period - treat as control per instructions
            df.loc[mask, 'period'] = 'Lag/Control'
            df.loc[mask, 'detailed_period'] = 'lag_period'

    return df

# Classify periods for each dataset
print("\nClassifying periods...")
light_data['Run1_A'] = classify_periods(light_data['Run1_A'], run1_markers)
light_data['Run1_B'] = classify_periods(light_data['Run1_B'], run1_markers)
light_data['Run2_A'] = classify_periods(light_data['Run2_A'], run2_markers)
light_data['Run2_B'] = classify_periods(light_data['Run2_B'], run2_markers)

# Check period distributions
for key, df in light_data.items():
    print(f"\n{key} period distribution:")
    print(df['period'].value_counts())

# Statistical Analysis Function
def analyze_conditions(df, run_name, sensor_name):
    """Perform statistical analysis on different conditions"""
    results = {}

    # Get baseline from control periods
    control_data = df[df['period'] == 'Control']['lux']
    if len(control_data) > 0:
        results['control_mean'] = control_data.mean()
        results['control_std'] = control_data.std()
        results['control_median'] = control_data.median()

    # Analyze each condition
    for condition in ['Condition_A', 'Condition_B', 'Condition_AB']:
        cond_data = df[df['period'] == condition]['lux']
        if len(cond_data) > 0 and len(control_data) > 0:
            results[f'{condition}_mean'] = cond_data.mean()
            results[f'{condition}_std'] = cond_data.std()
            results[f'{condition}_median'] = cond_data.median()

            # Calculate effect size (Cohen's d)
            pooled_std = np.sqrt((control_data.var() + cond_data.var()) / 2)
            if pooled_std > 0:
                results[f'{condition}_effect_size'] = (cond_data.mean() - control_data.mean()) / pooled_std

            # Statistical tests
            t_stat, p_val = ttest_ind(control_data, cond_data)
            results[f'{condition}_ttest_pval'] = p_val

            u_stat, p_val_mw = mannwhitneyu(control_data, cond_data)
            results[f'{condition}_mannwhitney_pval'] = p_val_mw

            # Percent change from baseline
            results[f'{condition}_percent_change'] = ((cond_data.mean() - control_data.mean()) / control_data.mean()) * 100

    return results

# Analyze all datasets
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
    print(f"  Control: mean={results.get('control_mean', 0):.2f}, std={results.get('control_std', 0):.2f}")

    for condition in ['Condition_A', 'Condition_B', 'Condition_AB']:
        if f'{condition}_mean' in results:
            print(f"  {condition}:")
            print(f"    Mean: {results[f'{condition}_mean']:.2f}")
            print(f"    % Change: {results[f'{condition}_percent_change']:.2f}%")
            print(f"    Effect Size: {results.get(f'{condition}_effect_size', 0):.3f}")
            print(f"    t-test p-value: {results[f'{condition}_ttest_pval']:.4f}")
            print(f"    Mann-Whitney p-value: {results[f'{condition}_mannwhitney_pval']:.4f}")

print("\n" + "="*80)
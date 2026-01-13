#!/usr/bin/env python3
"""
Create Visualizations for Analysis Results
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 10)

BASE_PATH = "/Users/jamesacer/Library/CloudStorage/OneDrive-Personal/Syntropy_Haze_OneDrive/SH_GitHub/data_for_blinded_flame_analysis_Jan13/"
OUTPUT_PATH = BASE_PATH + "analysis_output/"

# Load the analysis results
with open(f'{OUTPUT_PATH}corrected_results.json', 'r') as f:
    results = json.load(f)

# Create a summary visualization of all effects
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Effect sizes across all conditions
ax = axes[0, 0]
conditions = ['Condition_1st', 'Condition_2nd', 'Condition_Both']
sensors = ['Run1_A', 'Run1_B', 'Run2_A', 'Run2_B']
colors = ['blue', 'red', 'green', 'purple']

x = np.arange(len(conditions))
width = 0.2

for i, sensor in enumerate(sensors):
    effect_sizes = []
    for condition in conditions:
        key = f'{condition}_effect_size'
        if key in results['statistical_analysis'][sensor]:
            effect_sizes.append(results['statistical_analysis'][sensor][key])
        else:
            effect_sizes.append(0)

    ax.bar(x + i * width, effect_sizes, width, label=sensor, color=colors[i], alpha=0.7)

ax.set_xlabel('Condition')
ax.set_ylabel('Effect Size (Cohen\'s d)')
ax.set_title('Effect Sizes Across Conditions', fontweight='bold')
ax.set_xticks(x + width * 1.5)
ax.set_xticklabels(conditions)
ax.legend()
ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax.grid(True, alpha=0.3)

# Plot 2: Percent changes
ax = axes[0, 1]
for i, sensor in enumerate(sensors):
    percent_changes = []
    for condition in conditions:
        key = f'{condition}_percent_change'
        if key in results['statistical_analysis'][sensor]:
            percent_changes.append(results['statistical_analysis'][sensor][key])
        else:
            percent_changes.append(0)

    ax.bar(x + i * width, percent_changes, width, label=sensor, color=colors[i], alpha=0.7)

ax.set_xlabel('Condition')
ax.set_ylabel('Percent Change from Control (%)')
ax.set_title('Luminosity Changes from Baseline', fontweight='bold')
ax.set_xticks(x + width * 1.5)
ax.set_xticklabels(conditions)
ax.legend()
ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax.grid(True, alpha=0.3)

# Plot 3: Sensor correlations
ax = axes[1, 0]
correlation_data = []
correlation_labels = []

for run in ['Run1', 'Run2']:
    if run in results['correlation_analysis']:
        for period in ['Control', 'Condition_1st', 'Condition_2nd', 'Condition_Both']:
            if period in results['correlation_analysis'][run]:
                r = results['correlation_analysis'][run][period]['pearson_r']
                correlation_data.append(r)
                correlation_labels.append(f"{run}_{period[:4]}")

if correlation_data:
    bars = ax.bar(range(len(correlation_data)), correlation_data, alpha=0.7)
    for i, (bar, val) in enumerate(zip(bars, correlation_data)):
        if val > 0:
            bar.set_color('green')
        else:
            bar.set_color('red')

    ax.set_xlabel('Run and Condition')
    ax.set_ylabel('Pearson Correlation (r)')
    ax.set_title('Sensor A-B Correlations', fontweight='bold')
    ax.set_xticks(range(len(correlation_labels)))
    ax.set_xticklabels(correlation_labels, rotation=45, ha='right')
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax.grid(True, alpha=0.3)

# Plot 4: Significance heatmap
ax = axes[1, 1]
p_values = []
labels_y = []
labels_x = conditions

for sensor in sensors:
    row = []
    for condition in conditions:
        key = f'{condition}_ttest_pval'
        if key in results['statistical_analysis'][sensor]:
            row.append(results['statistical_analysis'][sensor][key])
        else:
            row.append(1.0)
    p_values.append(row)
    labels_y.append(sensor)

# Convert p-values to -log10 for better visualization
log_p_values = [[-np.log10(p) if p > 0 else 10 for p in row] for row in p_values]

im = ax.imshow(log_p_values, cmap='YlOrRd', aspect='auto')
ax.set_xticks(range(len(labels_x)))
ax.set_xticklabels(labels_x)
ax.set_yticks(range(len(labels_y)))
ax.set_yticklabels(labels_y)
ax.set_title('Statistical Significance (-log10 p-value)', fontweight='bold')

# Add text annotations
for i in range(len(labels_y)):
    for j in range(len(labels_x)):
        p_val = p_values[i][j]
        if p_val < 0.001:
            text = '***'
        elif p_val < 0.01:
            text = '**'
        elif p_val < 0.05:
            text = '*'
        else:
            text = 'ns'
        ax.text(j, i, text, ha='center', va='center', color='white' if log_p_values[i][j] > 2 else 'black')

plt.colorbar(im, ax=ax, label='-log10(p-value)')

plt.suptitle('Blind Analysis Results Summary', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{OUTPUT_PATH}summary_results.png', dpi=300, bbox_inches='tight')
print(f"Summary visualization saved to {OUTPUT_PATH}summary_results.png")

# Create individual time series plots for each run
for run_num in [1, 2]:
    # Load the actual data for time series
    light_files = {
        f'Run{run_num}_A': f'lightmeter_2026-01-12_00-47-53_TwinFlame1_CandleA.csv' if run_num == 1 else f'lightmeter_2026-01-12_02-11-46_TwinFlame2_CandleA.csv',
        f'Run{run_num}_B': f'lightmeter_2026-01-12_00-48-13_TwinFlame1_CandleB.csv' if run_num == 1 else f'lightmeter_2026-01-12_02-12-00_TwinFlame2_CandleB.csv'
    }

    fig, axes = plt.subplots(2, 1, figsize=(18, 10), sharex=True)

    for idx, (key, filename) in enumerate(light_files.items()):
        df = pd.read_csv(f"{BASE_PATH}{filename}")

        # Calculate timestamps
        end_time = datetime.strptime(
            '2026-01-12 00:47:53' if (run_num == 1 and 'A' in key) else
            '2026-01-12 00:48:13' if (run_num == 1 and 'B' in key) else
            '2026-01-12 02:11:46' if (run_num == 2 and 'A' in key) else
            '2026-01-12 02:12:00',
            '%Y-%m-%d %H:%M:%S'
        )
        duration = df['time'].max()
        start_time = end_time - timedelta(seconds=duration)
        df['timestamp'] = pd.to_datetime(start_time) + pd.to_timedelta(df['time'], unit='s')

        ax = axes[idx]
        sensor_letter = key.split('_')[1]

        # Plot the data
        ax.plot(df['timestamp'], df['lux'], color='blue' if sensor_letter == 'A' else 'red',
               alpha=0.6, linewidth=0.5, label=f'Sensor {sensor_letter}')

        # Add condition periods as shaded regions
        run1_periods = [
            ('2026-01-12 00:36:42', '2026-01-12 00:37:50', 'Control', 'gray'),
            ('2026-01-12 00:38:33', '2026-01-12 00:40:10', '1st Light', 'orange'),
            ('2026-01-12 00:40:53', '2026-01-12 00:42:00', 'Control', 'gray'),
            ('2026-01-12 00:42:11', '2026-01-12 00:43:11', '2nd Light', 'green'),
            ('2026-01-12 00:43:36', '2026-01-12 00:44:39', 'Control', 'gray'),
            ('2026-01-12 00:45:02', '2026-01-12 00:46:03', 'Both', 'purple'),
            ('2026-01-12 00:46:17', '2026-01-12 00:47:29', 'Control', 'gray')
        ]

        run2_periods = [
            ('2026-01-12 02:02:44', '2026-01-12 02:03:48', 'Control', 'gray'),
            ('2026-01-12 02:03:54', '2026-01-12 02:04:54', '1st Light', 'orange'),
            ('2026-01-12 02:05:02', '2026-01-12 02:06:06', 'Control', 'gray'),
            ('2026-01-12 02:06:14', '2026-01-12 02:07:13', '2nd Light', 'green'),
            ('2026-01-12 02:07:26', '2026-01-12 02:08:28', 'Control', 'gray'),
            ('2026-01-12 02:08:43', '2026-01-12 02:09:54', 'Both', 'purple'),
            ('2026-01-12 02:10:03', '2026-01-12 02:11:01', 'Control', 'gray')
        ]

        periods = run1_periods if run_num == 1 else run2_periods

        for start, end, label, color in periods:
            ax.axvspan(pd.to_datetime(start), pd.to_datetime(end),
                      alpha=0.2, color=color, label=label if idx == 0 else '')

        ax.set_ylabel('Luminosity (lux)', fontsize=12)
        ax.set_title(f'Run {run_num} - Sensor {sensor_letter}', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

        if idx == 0:
            # Remove duplicate labels
            handles, labels = ax.get_legend_handles_labels()
            by_label = dict(zip(labels, handles))
            ax.legend(by_label.values(), by_label.keys(), loc='upper right')

    axes[1].set_xlabel('Time', fontsize=12)
    plt.suptitle(f'Run {run_num} Time Series', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_PATH}run{run_num}_timeseries.png', dpi=300, bbox_inches='tight')
    print(f"Run {run_num} time series saved to {OUTPUT_PATH}run{run_num}_timeseries.png")

print("\nAll visualizations created successfully!")
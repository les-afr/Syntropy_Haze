#!/usr/bin/env python3
"""
Debug Run 1 timestamp synchronization
"""

import pandas as pd
from datetime import datetime, timedelta

BASE_PATH = "/Users/jamesacer/Library/CloudStorage/OneDrive-Personal/Syntropy_Haze_OneDrive/SH_GitHub/data_for_blinded_flame_analysis_Jan13/"

# Load timestamp data
timestamps_df = pd.read_excel(f"{BASE_PATH}COPY_timestamps_flame_play.xlsm")

print("Run 1 timestamps from Excel (column 3):")
for idx in range(5, len(timestamps_df)):
    label = timestamps_df.iloc[idx, 1]
    ts = timestamps_df.iloc[idx, 2]
    if not pd.isna(label) and not pd.isna(ts):
        print(f"  {label}: {ts}")

print("\nRun 1 Light Meter Time Ranges:")
# Load Run 1 light meter data
for sensor in ['A', 'B']:
    filename = f'lightmeter_2026-01-12_00-47-53_TwinFlame1_Candle{sensor}.csv' if sensor == 'A' else f'lightmeter_2026-01-12_00-48-13_TwinFlame1_Candle{sensor}.csv'
    df = pd.read_csv(f"{BASE_PATH}{filename}")

    end_time = datetime.strptime(f'2026-01-12 00:47:53' if sensor == 'A' else '2026-01-12 00:48:13', '%Y-%m-%d %H:%M:%S')
    duration = df['time'].max()
    start_time = end_time - timedelta(seconds=duration)

    print(f"  Sensor {sensor}:")
    print(f"    Start: {start_time}")
    print(f"    End: {end_time}")
    print(f"    Duration: {duration:.1f} seconds")

print("\n" + "="*60)
print("The issue: Run 1 timestamps in the Excel file are in HH:MM:SS format")
print("without the date, while the light meter data is from 2026-01-12.")
print("Need to add the date to the Run 1 timestamps to synchronize properly.")
print("="*60)
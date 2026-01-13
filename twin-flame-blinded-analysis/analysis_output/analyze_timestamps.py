#!/usr/bin/env python3
"""
Deep dive into timestamp data structure
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

BASE_PATH = "/Users/jamesacer/Library/CloudStorage/OneDrive-Personal/Syntropy_Haze_OneDrive/SH_GitHub/data_for_blinded_flame_analysis_Jan13/"

# Load timestamp data
print("Loading and examining timestamp data in detail...")
timestamps_df = pd.read_excel(f"{BASE_PATH}COPY_timestamps_flame_play.xlsm")

# Print all data to understand structure
print("\nFull timestamp data:")
print(timestamps_df.to_string())

# Let's try to identify which columns are for which run
print("\n" + "="*80 + "\n")
print("Column analysis:")
for col in timestamps_df.columns:
    print(f"\n{col}:")
    non_null = timestamps_df[col].dropna()
    if len(non_null) > 0:
        print(f"  Non-null entries: {len(non_null)}")
        print(f"  First few non-null values:")
        for val in non_null.head(5):
            print(f"    {val}")

# Based on the README, column 3 and 8 should have the absolute timestamps
print("\n" + "="*80 + "\n")
print("Looking for the absolute timestamp columns (3rd data column for each run)...")

# Let's examine the structure more systematically
print("\nExamining data starting from row 5 (where actual data seems to begin):")
data_rows = timestamps_df.iloc[5:]
print(data_rows.to_string())

# Extract the end times from filenames to understand synchronization
end_times = {
    'Run1_A': datetime.strptime('2026-01-12 00:47:53', '%Y-%m-%d %H:%M:%S'),
    'Run1_B': datetime.strptime('2026-01-12 00:48:13', '%Y-%m-%d %H:%M:%S'),
    'Run2_A': datetime.strptime('2026-01-12 02:11:46', '%Y-%m-%d %H:%M:%S'),
    'Run2_B': datetime.strptime('2026-01-12 02:12:00', '%Y-%m-%d %H:%M:%S')
}

print("\n" + "="*80 + "\n")
print("Light meter end times (from filenames):")
for key, time in end_times.items():
    print(f"  {key}: {time}")

# Load light meter data to get recording duration
light_files = {
    'Run1_A': 'lightmeter_2026-01-12_00-47-53_TwinFlame1_CandleA.csv',
    'Run1_B': 'lightmeter_2026-01-12_00-48-13_TwinFlame1_CandleB.csv',
    'Run2_A': 'lightmeter_2026-01-12_02-11-46_TwinFlame2_CandleA.csv',
    'Run2_B': 'lightmeter_2026-01-12_02-12-00_TwinFlame2_CandleB.csv'
}

print("\nLight meter recording durations and start times:")
for key, filename in light_files.items():
    df = pd.read_csv(f"{BASE_PATH}{filename}")
    duration = df['time'].max()
    start_time = end_times[key] - timedelta(seconds=duration)
    print(f"  {key}:")
    print(f"    Duration: {duration:.2f} seconds")
    print(f"    Start time: {start_time}")
    print(f"    End time: {end_times[key]}")
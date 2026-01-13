#!/usr/bin/env python3
"""
Blind Analysis of Luminosity Data
Author: Claude
Date: January 13, 2025
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from scipy import stats
from scipy.signal import correlate, detrend
import warnings
warnings.filterwarnings('ignore')

# Set up plotting style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)

# File paths
BASE_PATH = "/Users/jamesacer/Library/CloudStorage/OneDrive-Personal/Syntropy_Haze_OneDrive/SH_GitHub/data_for_blinded_flame_analysis_Jan13/"

# Load timestamp data
print("Loading timestamp/marker data...")
timestamps_df = pd.read_excel(f"{BASE_PATH}COPY_timestamps_flame_play.xlsm")
print(f"Timestamp columns: {timestamps_df.columns.tolist()}")
print(f"Shape: {timestamps_df.shape}")
print("\nFirst few rows:")
print(timestamps_df.head(10))
print("\n" + "="*80 + "\n")

# Load light meter data
print("Loading light meter data...")
light_files = {
    'Run1_A': 'lightmeter_2026-01-12_00-47-53_TwinFlame1_CandleA.csv',
    'Run1_B': 'lightmeter_2026-01-12_00-48-13_TwinFlame1_CandleB.csv',
    'Run2_A': 'lightmeter_2026-01-12_02-11-46_TwinFlame2_CandleA.csv',
    'Run2_B': 'lightmeter_2026-01-12_02-12-00_TwinFlame2_CandleB.csv'
}

light_data = {}
for key, filename in light_files.items():
    df = pd.read_csv(f"{BASE_PATH}{filename}")
    light_data[key] = df
    print(f"\n{key} ({filename}):")
    print(f"  Columns: {df.columns.tolist()}")
    print(f"  Shape: {df.shape}")
    print(f"  First few rows:")
    print(df.head())

print("\n" + "="*80 + "\n")

# Examine the structure of light meter data more closely
print("Examining light meter data structure...")
for key, df in light_data.items():
    print(f"\n{key}:")
    print(f"  Data types: {df.dtypes.to_dict()}")
    if 'Lux' in df.columns:
        print(f"  Lux range: {df['Lux'].min():.2f} - {df['Lux'].max():.2f}")
        print(f"  Lux mean: {df['Lux'].mean():.2f}")
        print(f"  Lux std: {df['Lux'].std():.2f}")
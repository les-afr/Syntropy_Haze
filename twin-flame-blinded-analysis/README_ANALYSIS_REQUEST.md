# Blinded Data Analysis Request

## Overview
This folder contains luminosity data from two experimental runs involving two light sources (designated A and B) under various conditions. We're intentionally withholding certain details about the experimental setup to ensure unbiased analysis, but will share full context after the analysis is complete.

## Your Task
Please analyze the provided data to identify:
1. **Significant patterns or changes in luminosity** that correlate with condition changes
2. **Relationships between the two sensors' readings** (correlation, anti-correlation, or other patterns)
3. **Any anomalous or interesting behaviors** in the light measurements
4. **Statistical significance** of any patterns found

## Data Files

### Light Meter Data
Four CSV files containing continuous luminosity measurements (in lux) at ~10Hz:
- `lightmeter_2026-01-12_00-47-53_TwinFlame1_CandleA.csv` - Run 1, Sensor A
- `lightmeter_2026-01-12_00-48-13_TwinFlame1_CandleB.csv` - Run 1, Sensor B
- `lightmeter_2026-01-12_02-11-46_TwinFlame2_CandleA.csv` - Run 2, Sensor A
- `lightmeter_2026-01-12_02-12-00_TwinFlame2_CandleB.csv` - Run 2, Sensor B

### Timestamp Files
- `run1_timestamps.csv` - Condition changes for Run 1
- `run2_timestamps.csv` - Condition changes for Run 2
- `synchronization_info.md` - Information for aligning light meter data with timestamps

### Experimental Conditions
Each run included several phases:
- **Control periods**: Baseline measurements
- **Condition A**: A specific experimental condition applied
- **Condition B**: A different experimental condition applied
- **Condition AB**: Both conditions applied simultaneously

**Important Note**: In Run 2, the order in which Conditions A and B were applied to the sensors was reversed from Run 1.

## Analysis Suggestions
1. **Synchronize the data**: Use the synchronization info to align light meter readings with condition timestamps
2. **Calculate baseline**: Use control periods to establish baseline luminosity for each sensor
3. **Analyze changes**: Look for significant changes during different conditions
4. **Cross-correlation**: Examine relationships between Sensor A and B readings
5. **Statistical tests**: Apply appropriate tests for significance

## Output Request
Please provide:
- Visualizations showing luminosity changes over time with condition markers
- Statistical analysis of changes during different conditions
- Any notable patterns or anomalies discovered
- Your interpretation of what might be happening

## Note on Participation
This analysis is completely optional - only proceed if you're interested! We're conducting this blinded analysis for scientific rigor, and we'll share the full experimental context afterward. The experiment involves an interesting phenomenon we're trying to validate through independent analysis.

Thank you for considering this request! Feel free to approach the analysis however seems most appropriate to you.

---
*After completing your analysis, we'll share the full context and discuss the findings together.*
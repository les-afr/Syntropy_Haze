# Data Synchronization Information

## Important Note
The timestamp CSVs reference time in seconds from the start of each experimental run's first control period (Time_seconds = 0 at Control_1_Start). The light meter recordings started at different times and need to be aligned using the offsets below.

## Run 1 (Twin Flame 1)
- Sensor A recording: lightmeter_2026-01-12_00-47-53_TwinFlame1_CandleA.csv
  - Started at: 00:47:53 (absolute clock time)
  - **Offset from experiment start: +634 seconds** (light meter started 634 seconds AFTER Control_1_Start)

- Sensor B recording: lightmeter_2026-01-12_00-48-13_TwinFlame1_CandleB.csv
  - Started at: 00:48:13 (absolute clock time)
  - **Offset from experiment start: +654 seconds** (light meter started 654 seconds AFTER Control_1_Start)
  - Started 20 seconds after Sensor A

## Run 2 (Twin Flame 2)
- Sensor A recording: lightmeter_2026-01-12_02-11-46_TwinFlame2_CandleA.csv
  - Started at: 02:11:46 (absolute clock time)
  - **Offset from experiment start: +194 seconds** (light meter started 194 seconds AFTER Control_1_Start)

- Sensor B recording: lightmeter_2026-01-12_02-12-00_TwinFlame2_CandleB.csv
  - Started at: 02:12:00 (absolute clock time)
  - **Offset from experiment start: +219 seconds** (light meter started 219 seconds AFTER Control_1_Start)
  - Started 14 seconds after Sensor A

## How to Align the Data
1. The timestamp CSVs show when each condition started/ended relative to the beginning of the experiment
2. The light meter CSVs contain continuous readings but started recording at different times
3. To align: subtract the appropriate offset from the light meter timestamps to get experimental time
   - Example: For Run 1 Sensor A, experimental_time = light_meter_time - 634 seconds

## Additional Notes
- Video recordings were made of the experiments but are not included in this dataset
- The timestamps have been validated against these videos for accuracy
- Each light meter CSV contains continuous luminosity readings at approximately 10Hz
- Note the gaps between some conditions in the timestamp files - these represent actual transition periods

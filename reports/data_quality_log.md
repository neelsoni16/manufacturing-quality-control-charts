# Data-Quality Log — Project 9

**Dataset:** `data/raw_measurements.csv` → Cleaned to `data/clean_measurements.csv`  
**Total Raw Records:** 1,001 rows (200 batches × 5 parts + 1 duplicate)  
**Total Clean Records:** 1,000 rows  

| Issue Type | Record Location | Description of Anomaly | Action Taken | Statistical Justification |
| :--- | :--- | :--- | :--- | :--- |
| **Missing Value** | `measurement_id = 13` (Batch 3) | `measured_value` recorded as empty (`""`) due to a simulated sensor dropout. | Imputed with the nominal process target (`10.0000 mm`). | Preserves the fixed subgroup size ($n = 5$) required for standard $A_2$, $D_3$, and $D_4$ control chart constants without distorting baseline spread. |
| **Extreme Outlier / Typo** | `measurement_id = 89` (Batch 18) | Value recorded as `99.9900 mm` (~1,800 $\sigma$ above the target mean). | Flagged via physical range filter (`< 5.0` or `> 15.0 mm`) and replaced with `10.0000 mm`. | Physically impossible reading caused by a sensor spike or logging typo; leaving it uncleaned would artificially inflate $\bar{R}$ and widen the 3-sigma control limits. |
| **Duplicate Record** | `measurement_id = 11` (appended at row 1,002) | Exact duplicate row of `measurement_id = 11` logged twice. | Deduplicated using a unique ID hash set (`seen`) during ingestion. | Prevents artificial reduction of within-batch variance and ensures each batch contains exactly $n = 5$ distinct observations. |

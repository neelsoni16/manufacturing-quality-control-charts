# Manufacturing Quality Control with Control Charts (Project 9)

**Course:** Probability & Statistics (BTech CSE)  
**Institution:** School of Engineering, JG University  

## Project Overview
This project implements a Statistical Process Control (SPC) monitoring pipeline to detect manufacturing process shifts before defects occur. It combines relational database storage (SQLite), a sliding-window data structure (`collections.deque`), and statistical control charts ($\bar{X}$, $R$, and two-sided tabular CUSUM) to compare theoretical false-alarm rates ($0.27\%$ under $3\sigma$ limits) against empirical simulations.

## Repository Structure
```text
├── data/
│   ├── raw_measurements.csv       # Simulated raw sensor data with injected shift & noise
│   ├── clean_measurements.csv     # Cleaned dataset after anomaly & duplicate handling
│   └── quality_control.db         # SQLite database populated from schema.sql
├── sql/
│   ├── schema.sql                 # CREATE TABLE relational schema (5 tables)
│   └── analytical_queries.sql     # 5 analytical queries (JOINs, aggregations, window functions)
├── src/
│   └── main.py                    # End-to-end Python pipeline (fixed seed = 42)
├── notebooks/
│   └── Project9_Quality_Control.ipynb  # Interactive Google Colab / Jupyter notebook
├── reports/
│   ├── Proposal.md                # Initial problem statement, hypotheses & methods
│   ├── data_quality_log.md        # Log of missing, outlier & duplicate fixes
│   ├── control_charts.png         # Generated X-bar, R, and CUSUM plots
│   ├── er_diagram.png             # Relational database ER diagram
│   └── Final_Report.pdf           # Final 6–10 page project report & presentation slides
├── README.md
└── requirements.txt

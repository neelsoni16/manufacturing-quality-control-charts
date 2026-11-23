Project Proposal: Manufacturing Quality Control with Control Charts
Course: Probability & Statistics (BTech CSE)
Institution: School of Engineering, JG University
Project Number & Title: Project 9 — Manufacturing Quality Control with Control Charts
Team Members:
Member 1 (Repository Setup & Proposal)
Member 2 (Data Engineering & Data-Quality Log)
Member 3 (DBMS Architecture & Analytical SQL)
Member 4 (Python Monitoring Pipeline & DSA)
Member 5 (Statistical Validation, Visualisations & Presentation)
1. Problem Statement & Motivation
In high-precision manufacturing industries—such as automotive, pharmaceutical, and semiconductor production—maintaining consistent output quality is critical. Every production process naturally exhibits minor random fluctuations ("common-cause variation"), which are acceptable. However, equipment wear, calibration drift, or raw material defects can introduce sudden or gradual shifts in the process mean or spread ("assignable-cause variation"). If undetected, these shifts lead to defective batches, scrap costs, and safety failures.
Statistical Process Control (SPC) addresses this problem by monitoring live measurements against statistically derived baseline limits rather than waiting for post-production inspection.
Core Statistical Question:
How accurately and rapidly can traditional Shewhart ($\bar{X}$ and $R$) control charts and Cumulative Sum (CUSUM) control charts distinguish true process shifts from natural random variation without generating excessive false alarms?
2. Dataset Plan & Data Quality Strategy
To evaluate both controlled baseline behavior and shift detection under realistic manufacturing conditions, our project will use a two-part data strategy:
Primary Dataset (Simulated Process Data with Injected Shift): We will generate a realistic time-stamped manufacturing dataset simulating continuous part measurements (e.g., shaft diameter in mm) grouped into subgroup batches of size $n = 5$. The dataset will consist of:
Phase I (In-Control Baseline): $100$ subgroups ($500$ observations) generated from a stable normal process $\mathcal{N}(\mu_0, \sigma_0^2)$ to establish control limits.
Phase II (Monitoring & Injected Drift): $100$ subgroups ($500$ observations) where a deliberate mean shift (testing both small shifts of $0.5\sigma$–$1.0\sigma$ and large shifts of $\ge 2.0\sigma$) is injected mid-stream.
Secondary Real-World Benchmark (Optional Validation): We will also test our pipeline against real sensor readings from the UCI SECOM or UCI Steel Plates manufacturing dataset.
Data-Quality Handling: Realistic imperfections—such as missing sensor timestamps, duplicate readings, and extreme recording typos—will be audited and cleaned. Every cleaning decision will be documented in a dedicated Data-Quality Log.
3. Hypotheses & Estimands
In accordance with statistical rigor standards, our formal hypotheses and key performance metrics (estimands) are defined prior to analysis:
Hypothesis 1 (Process Stability Test):
Null Hypothesis ($H_0$): The manufacturing process remains in statistical control ($\mu = \mu_0$ and $\sigma = \sigma_0$); all observed variations in subgroup means ($\bar{X}$) and ranges ($R$) are due solely to common-cause random noise.
Alternative Hypothesis ($H_1$): The manufacturing process has gone out of control ($\mu \neq \mu_0$ or $\sigma > \sigma_0$) due to an assignable process shift.
Hypothesis 2 (Chart Sensitivity Comparison):
Null Hypothesis ($H_0$): $\bar{X}$ and CUSUM charts require the same Average Run Length ($\text{ARL}_1$) to detect a small sustained mean shift ($\le 1.0\sigma$).
Alternative Hypothesis ($H_1$): Because CUSUM accumulates small deviations over time, it will achieve a significantly lower $\text{ARL}_1$ (faster shift detection) than the $\bar{X}$ chart for small drifts.
Key Estimands: In-control false-alarm rate ($\alpha$), Average Run Length in control ($\text{ARL}_0$), and Average Run Length out of control ($\text{ARL}_1$).
4. Planned Methods (Statistics, DBMS & DSA)
A. Statistical Methods
Descriptive & Sampling Foundations: Compute baseline grand mean ($\bar{\bar{X}}$), average subgroup range ($\bar{R}$), and estimated process standard deviation ($\hat{\sigma} = \bar{R}/d_2$), applying the Central Limit Theorem to model the sampling distribution of subgroup means.
Assumption Checks: Verify normality (via Q-Q plots / Shapiro-Wilk test) and independence of baseline observations before computing parametric limits.
Control Charts & Run Rules:
$\bar{X}$ and $R$ Charts: Establish three-sigma ($\pm 3\sigma$) control limits ($\text{UCL}, \text{CL}, \text{LCL}$) and evaluate Western Electric / Nelson run rules to detect sudden shifts and spread changes.
CUSUM Chart: Implement two-sided tabular CUSUM ($C^+$ and $C^-$) with reference value $k = 0.5\sigma$ and decision interval $h = 5\sigma$ to detect small, persistent drifts.
B. Database Management System (DBMS)
We will design a normalized relational schema (in PostgreSQL / SQLite) comprising five tables:
Production_Lines (line metadata and target specifications)
Sample_Batches (time-stamped subgroup summaries: batch_id, line_id, recorded_at, is_baseline, batch_mean, batch_range)
Measurements (individual raw sensor readings linked to each batch)
Control_Limits (computed $\text{UCL}$, $\text{CL}$, and $\text{LCL}$ values per chart type)
Control_Alerts (logged out-of-control points and violated rules)
We will write at least 5 analytical SQL queries utilizing JOINs, GROUP BY aggregations, and window functions to extract shift summaries, rolling averages, and alert frequencies.
C. Data Structures & Algorithms (DSA)
To simulate real-time factory monitoring efficiently without recomputing historical arrays from scratch, we will use a sliding-window double-ended queue (collections.deque in Python) of fixed maximum length $w$ to maintain rolling means, rolling standard deviations, and run-rule checks in $O(1)$ amortized time per incoming batch.
5. Expected Results (Theory vs. Experiment Validation)
We will validate our empirical Python simulation against established statistical theory:
In-Control False-Alarm Rate: Under a normal distribution with $\pm 3\sigma$ limits, the theoretical probability of a point falling outside control limits by pure chance is $P(\vert{}Z\vert{} > 3) \approx \mathbf{0.27\%}$ per point (corresponding to $\text{ARL}_0 \approx 370$ batches). By running $10,000+$ simulated in-control points, we expect our observed false-alarm rate to converge closely to $0.27\%$, and we will explain any minor discrepancies caused by finite baseline estimation error.
Shift Detection Speed: For large shifts ($\ge 2.5\sigma$), we expect the $\bar{X}$ chart to flag the anomaly within $1$–$2$ batches. For small shifts ($0.5\sigma$–$1.0\sigma$), we expect the $\bar{X}$ chart to lag significantly (requiring dozens of batches), whereas CUSUM is expected to trigger an alert substantially faster.

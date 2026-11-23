--Since you already have Python installed on your Windows laptop, use Python's built-in sqlite3
-- 1. Production Lines
CREATE TABLE Production_Lines (
    line_id INTEGER PRIMARY KEY,
    line_name TEXT,
    target_value REAL
);

-- 2. Sample Batches (Subgroups)
CREATE TABLE Sample_Batches (
    batch_id INTEGER PRIMARY KEY,
    line_id INTEGER,
    recorded_time TEXT,
    is_baseline INTEGER, -- 1 = Baseline, 0 = Live Monitoring
    batch_mean REAL,
    batch_range REAL,
    FOREIGN KEY (line_id) REFERENCES Production_Lines(line_id)
);

-- 3. Individual Measurements
CREATE TABLE Measurements (
    measurement_id INTEGER PRIMARY KEY,
    batch_id INTEGER,
    measured_value REAL,
    FOREIGN KEY (batch_id) REFERENCES Sample_Batches(batch_id)
);

-- 4. Control Limits (UCL, Center Line, LCL)
CREATE TABLE Control_Limits (
    limit_id INTEGER PRIMARY KEY,
    line_id INTEGER,
    chart_type TEXT, -- 'X-bar', 'R-chart', or 'CUSUM'
    ucl REAL,
    center_line REAL,
    lcl REAL,
    FOREIGN KEY (line_id) REFERENCES Production_Lines(line_id)
);

-- 5. Out-of-Control Alerts
CREATE TABLE Control_Alerts (
    alert_id INTEGER PRIMARY KEY,
    batch_id INTEGER,
    chart_type TEXT,
    reason TEXT,
    FOREIGN KEY (batch_id) REFERENCES Sample_Batches(batch_id)
);

-- 1. Calculate Mean (X-bar) and Range (R) for every batch
SELECT 
    b.batch_id,
    l.line_name,
    AVG(m.measured_value) AS x_bar,
    MAX(m.measured_value) - MIN(m.measured_value) AS batch_range
FROM Sample_Batches b
JOIN Production_Lines l ON b.line_id = l.line_id
JOIN Measurements m ON b.batch_id = m.batch_id
GROUP BY b.batch_id, l.line_name;


-- 2. Find overall Baseline Mean and Average Range (Phase I)
SELECT 
    line_id,
    COUNT(batch_id) AS total_batches,
    AVG(batch_mean) AS grand_mean,
    AVG(batch_range) AS avg_range
FROM Sample_Batches
WHERE is_baseline = 1
GROUP BY line_id;


-- 3. Rolling 5-Batch Moving Average (Window Function)
SELECT 
    batch_id,
    batch_mean,
    AVG(batch_mean) OVER (ORDER BY batch_id ROWS 4 PRECEDING) AS rolling_avg
FROM Sample_Batches;


-- 4. Count Out-of-Control Alerts by Chart Type (X-bar vs CUSUM)
SELECT 
    a.chart_type,
    COUNT(a.alert_id) AS total_alerts,
    MIN(b.batch_id) AS first_alert_batch
FROM Control_Alerts a
JOIN Sample_Batches b ON a.batch_id = b.batch_id
GROUP BY a.chart_type;


-- 5. Check Baseline False-Alarm Percentage (Theory vs Experiment)
SELECT 
    COUNT(b.batch_id) AS baseline_batches,
    SUM(CASE WHEN b.batch_mean > c.ucl OR b.batch_mean < c.lcl THEN 1 ELSE 0 END) AS false_alarms,
    ROUND(100.0 * SUM(CASE WHEN b.batch_mean > c.ucl OR b.batch_mean < c.lcl THEN 1 ELSE 0 END) / COUNT(b.batch_id), 2) AS false_alarm_pct
FROM Sample_Batches b
JOIN Control_Limits c ON b.line_id = c.line_id
WHERE b.is_baseline = 1 AND c.chart_type = 'X-bar';

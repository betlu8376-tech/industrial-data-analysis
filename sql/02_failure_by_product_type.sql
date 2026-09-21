SELECT
        product_type,
        COUNT(*) AS total_nums,
        SUM(CASE
                WHEN machine_failure=1 THEN 1
                ELSE 0
                END) AS failure_counts,
        ROUND(100.00* SUM(CASE
                WHEN machine_failure=1 THEN 1
                ELSE 0
                END
                )/COUNT(*),2) AS failure_rate_percent
FROM machine_records
GROUP BY product_type
ORDER BY failure_rate_percent DESC;

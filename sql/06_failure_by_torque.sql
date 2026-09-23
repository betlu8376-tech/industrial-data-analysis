SELECT
        CASE
            WHEN torque_nm<20 THEN "0-19"
            WHEN torque_nm<40 THEN "20-39"
            WHEN torque_nm<60 THEN "40-59"
            WHEN torque_nm<80 THEN "60-79"
        ELSE "80+"
        END AS torque_nm_group,
        COUNT(*) AS total_nums,
        SUM(machine_failure) AS failure_counts,
        ROUND(100.0*SUM(machine_failure)/COUNT(*),2) AS failure_rate_percent
FROM machine_records
GROUP BY torque_nm_group

ORDER BY MIN(torque_nm);


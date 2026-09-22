SELECT
        CASE
            WHEN tool_wear_min<50 THEN "0-49"
            WHEN tool_wear_min<100 THEN "50-99"
            WHEN tool_wear_min<150 THEN "100-149"
            WHEN tool_wear_min<200 THEN "150-199"
--            WHEN tool_wear_min<250 THEN "200-249"
            ELSE "200+"
        END AS tool_wear_group,
        COUNT(*) AS total_nums,
        SUM(machine_failure) AS failure_counts,
        ROUND(100.0*SUM(machine_failure)/COUNT(*),2) AS failure_rate_percent
FROM machine_records
GROUP BY tool_wear_group

ORDER BY MIN(tool_wear_min);

SELECT
    COUNT(*) AS total_count,

    SUM(
        CASE
            WHEN machine_failure = 0 THEN 1
            ELSE 0
        END
    ) AS normal_count,

    SUM(
        CASE
            WHEN machine_failure = 1 THEN 1
            ELSE 0
        END
    ) AS failure_count,

    ROUND(
        100.0 * SUM(
            CASE
                WHEN machine_failure = 1 THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS failure_rate_percent
FROM machine_records;

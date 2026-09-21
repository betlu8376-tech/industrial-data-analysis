SELECT
    'TWF' AS failure_type,
    COUNT(tool_wear_failure) AS total_counts,
    SUM(tool_wear_failure) AS failure_counts,
    ROUND(100.0*SUM(tool_wear_failure)/COUNT(tool_wear_failure),2)  AS failure_percent
FROM machine_records

UNION ALL

SELECT
    'HDF',
    COUNT(heat_dissipation_failure),
    SUM(heat_dissipation_failure),

    ROUND(100.0*SUM(heat_dissipation_failure)/COUNT(heat_dissipation_failure),2)
FROM machine_records

UNION ALL

SELECT
    'PWF',
    COUNT(power_failure),
    SUM(power_failure),

    ROUND(100.0*SUM(power_failure)/COUNT(power_failure),2)
FROM machine_records

UNION ALL

SELECT
    'OSF',
    COUNT(overstrain_failure),
    SUM(overstrain_failure),

    ROUND(100.0*SUM(overstrain_failure)/COUNT(overstrain_failure),2)
FROM machine_records

UNION ALL

SELECT
    'RNF',
    COUNT(random_failure),
    SUM(random_failure),

    ROUND(100.0*SUM(random_failure)/COUNT(random_failure),2)
FROM machine_records

ORDER BY failure_counts DESC;
SELECT
    CASE
        WHEN machine_failure = 0 THEN 'Normal'
        ELSE 'Failure'
    END AS machine_status,

    COUNT(*) AS record_count,

    ROUND(AVG(air_temperature_k), 2)
        AS avg_air_temperature_k,

    ROUND(AVG(process_temperature_k), 2)
        AS avg_process_temperature_k,

    ROUND(AVG(rotational_speed_rpm), 2)
        AS avg_rotational_speed_rpm,

    ROUND(AVG(torque_nm), 2)
        AS avg_torque_nm,

    ROUND(AVG(tool_wear_min), 2)
        AS avg_tool_wear_min

FROM machine_records
GROUP BY machine_failure
ORDER BY machine_failure;
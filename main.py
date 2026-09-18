import pandas as pd

machine_data = {
    "machine_id": [101, 102, 103, 104],
    "temperature": [65.2, 72.5, 88.1, 69.7],
    "rotational_speed": [1450, 1500, 1380, 1600],
    "failure": [0, 0, 1, 0],
}

machine_df = pd.DataFrame(machine_data)

print("设备运行数据：")
print(machine_df)

print("\n所有设备的温度：")
print(machine_df["temperature"])

failed_machines = machine_df[machine_df["failure"] == 0]
print("故障设备：")
print(failed_machines)

average_temperature = machine_df["temperature"].mean()
print(f"\n设备平均温度：{average_temperature:.2f}")

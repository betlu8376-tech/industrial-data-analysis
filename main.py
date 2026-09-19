
from pathlib import Path

import pandas as pd


project_root = Path(__file__).resolve().parent
data_path = project_root / "data" / "raw" / "ai4i2020.csv"

machine_df = pd.read_csv(data_path)



# print("前5行数据：")
# print(machine_df.head())
#
# print(f"\n数据规模：{machine_df.shape[0]}行，{machine_df.shape[1]}列")
#
# print("\n字段名称：")
# print(machine_df.columns.tolist())
#
# print("\n字段类型和缺失情况：")
# machine_df.info()


failure_count=machine_df["Machine failure"].value_counts().sort_index()
print("\n设备状态数量：")
print(failure_count)

normal_rate = (machine_df["Machine failure"]==0).mean()
print(f"\n设备合格率：{normal_rate:.2%}")

# 统计不同产品类型的数量
type_counts = machine_df["Type"].value_counts()
print("\n产品类型数量：")
print(type_counts)




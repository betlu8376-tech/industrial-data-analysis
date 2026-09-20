from contextlib import closing
from pathlib import Path
import sqlite3

import pandas as pd


project_root = Path(__file__).resolve().parent
csv_path = project_root / "data" / "raw" / "ai4i2020.csv"
database_path = (
    project_root / "data" / "processed" / "industrial_data.db"
)

# 读取原始CSV
machine_df = pd.read_csv(csv_path)

# 将原始列名改成适合SQL使用的格式
machine_df = machine_df.rename(
    columns={
        "UDI": "udi",
        "Product ID": "product_id",
        "Type": "product_type",
        "Air temperature [K]": "air_temperature_k",
        "Process temperature [K]": "process_temperature_k",
        "Rotational speed [rpm]": "rotational_speed_rpm",
        "Torque [Nm]": "torque_nm",
        "Tool wear [min]": "tool_wear_min",
        "Machine failure": "machine_failure",
        "TWF": "tool_wear_failure",
        "HDF": "heat_dissipation_failure",
        "PWF": "power_failure",
        "OSF": "overstrain_failure",
        "RNF": "random_failure",
    }
)

database_path.parent.mkdir(parents=True, exist_ok=True)

with closing(sqlite3.connect(database_path)) as connection:
    machine_df.to_sql(
        name="machine_records",
        con=connection,
        if_exists="replace",
        index=False,
    )

    connection.commit()

    row_count = connection.execute(
        "SELECT COUNT(*) FROM machine_records"
    ).fetchone()[0]

print(f"数据库创建成功：{database_path}")
print(f"machine_records 表共有 {row_count} 行")
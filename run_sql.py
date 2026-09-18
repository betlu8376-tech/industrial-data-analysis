from contextlib import closing
from pathlib import Path
import sqlite3

import pandas as pd


project_root = Path(__file__).resolve().parent

database_path = (
    project_root / "data" / "processed" / "industrial_data.db"
)

sql_path = project_root / "sql" / "01_failure_summary.sql"

if not database_path.exists():
    raise FileNotFoundError(
        "数据库不存在，请先运行 prepare_database.py"
    )

query = sql_path.read_text(encoding="utf-8")

with closing(sqlite3.connect(database_path)) as connection:
    result_df = pd.read_sql_query(query, connection)

print("SQL查询结果：")
print(result_df.to_string(index=False))
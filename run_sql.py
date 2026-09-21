from contextlib import closing
from pathlib import Path
import sqlite3

import pandas as pd


project_root = Path(__file__).resolve().parent

database_path = (
    project_root / "data" / "processed" / "industrial_data.db"
)

# sql_path = project_root / "sql" / "01_failure_summary.sql"
# sql_path = project_root / "sql" / "02_failure_by_product_type.sql"
# sql_path = project_root / "sql" / "03_failure_type_summary.sql"
sql_path = project_root / "sql" / "04_failure_condition_comparison.sql"

if not database_path.exists():
    raise FileNotFoundError(
        "数据库不存在，请先运行 prepare_database.py"
    )

query = sql_path.read_text(encoding="utf-8")

with closing(sqlite3.connect(database_path)) as connection:
    result_df = pd.read_sql_query(query, connection)

print("SQL查询结果：")
print(result_df.to_string(index=True))#index决定是否显示编号


#set export path
# output_path = project_root / "reports" / "failure_by_product_type.csv"
# output_path = project_root / "reports" / "failure_type_summary.csv"
output_path = project_root / "reports" / "04_failure_condition_comparison.csv"

# ensure path exist
output_path.parent.mkdir(parents=True, exist_ok=True)

# output to csv
result_df.to_csv(output_path, index=False, encoding="utf-8-sig")

print(f"\n分析结果已保存到：{output_path}")
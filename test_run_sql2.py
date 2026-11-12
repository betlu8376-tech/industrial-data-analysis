from pathlib import Path

from run_sql2 import DATABASE_PATH, PROJECT_ROOT, execute_query

import pytest
import pandas as pd
import sqlite3
from contextlib import closing


def test_failure_summary() -> None:
    """检查故障汇总查询的关键结果。"""
    sql_path = PROJECT_ROOT / "sql" / "01_failure_summary.sql"
    result = execute_query(DATABASE_PATH, sql_path)

    assert result.loc[0, "total_count"] == 10_000
    assert result.loc[0, "failure_count"] == 339



# def test_missing_sql() -> None:
#     """缺少 SQL 文件时应给出明确错误。"""
#     missing_sql = PROJECT_ROOT / "sql" / "not_exists.sql"
#
#     try:
#         execute_query(DATABASE_PATH, missing_sql)
#     except FileNotFoundError as error:
#         assert "SQL 文件不存在" in str(error)
#     else:
#         raise AssertionError("缺少 SQL 文件时没有报错")


def test_missing_sql() -> None:
    missing_sql = PROJECT_ROOT / "sql" / "not_exists.sql"
    with pytest.raises(FileNotFoundError,match="SQL 文件不存在"):
        execute_query(DATABASE_PATH, missing_sql)


def test_torque_group_order() -> None:
    """检查扭矩区间按数值顺序排列。"""
    sql_path = PROJECT_ROOT / "sql" / "06_failure_by_torque.sql"
    result = execute_query(DATABASE_PATH, sql_path)

    assert result["torque_nm_group"].tolist() == [
        "0-19", "20-39", "40-59", "60-79",
    ]

def test_non_sql_file() -> None:
    with pytest.raises(ValueError):
# 在这里调用 execute_query(...)
        sql_path = PROJECT_ROOT / "README.md"
        execute_query(DATABASE_PATH, sql_path)



def test_execute_query_special_path(tmp_path:Path) -> None:
    database_path = tmp_path / "工业 数据 #1.db"
    with closing(sqlite3.connect(database_path)) as connection:
        connection.execute(
            "CREATE TABLE sample (id INTEGER PRIMARY KEY, value INTEGER)"
        )
        connection.execute(
            "INSERT INTO sample (id, value) VALUES (1, 10)"
        )
        connection.commit()

    tmp_sql_path=tmp_path/"select.sql"
    with open (tmp_sql_path,"w",encoding="utf-8") as s:
        s.write("SELECT id, value FROM sample;")
    dataframe=execute_query(database_path, tmp_sql_path)
    assert dataframe.to_dict(orient="records") == [{"id": 1, "value": 10}]


def test_execute_query_rejects_write(tmp_path:Path) -> None:
    database_path = tmp_path / "工业 数据 #1.db"
    with closing(sqlite3.connect(database_path)) as connection:
        connection.execute(
            "CREATE TABLE sample (id INTEGER PRIMARY KEY, value INTEGER)"
        )
        connection.execute(
            "INSERT INTO sample (id, value) VALUES (1, 10)"
        )
        connection.commit()
    tmp_sql_path1=tmp_path/"select1.sql"
    tmp_sql_path2=tmp_path/"select2.sql"
    with open (tmp_sql_path1,"w",encoding="utf-8") as s1:
        s1.write("SELECT id, value FROM sample;")
    with open (tmp_sql_path2,"w",encoding="utf-8") as s2:
        s2.write("UPDATE sample SET value = 99 WHERE id = 1;")
    with pytest.raises(pd.errors.DatabaseError, match="readonly"):
        execute_query(database_path, tmp_sql_path2)
    dataframe = execute_query(database_path, tmp_sql_path1)
    assert dataframe.to_dict(orient="records") == [{"id": 1, "value": 10}]


if __name__ == "__main__":
    test_failure_summary()
    test_missing_sql()
    test_torque_group_order()
    test_non_sql_file()
    print("测试通过")


from run_sql2 import DATABASE_PATH, PROJECT_ROOT, execute_query

import pytest


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

if __name__ == "__main__":
    test_failure_summary()
    test_missing_sql()
    test_torque_group_order()
    test_non_sql_file()
    print("测试通过")


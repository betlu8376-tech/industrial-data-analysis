import argparse
from contextlib import closing
from pathlib import Path
import sqlite3
import sys

import pandas as pd

import logging

import os


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_DATABASE_PATH = (
    PROJECT_ROOT / "data" / "processed" / "industrial_data.db"
)
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", str(DEFAULT_DATABASE_PATH)))


OUTPUT_NAMES = {
    "02_failure_by_product_type": "failure_by_product_type.csv",
    "03_failure_type_summary": "failure_type_summary.csv",
}

def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(
        description="执行 SQL 文件并导出 CSV。",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--sql",
        type=Path,
        help="执行指定 SQL，例如 sql/06_failure_by_torque.sql",
    )
    group.add_argument(
        "--all",
        action="store_true",
        help="依次执行 sql 文件夹中的全部 SQL",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "reports",
        help="CSV 输出目录，默认为项目下的 reports"
    )
    return parser.parse_args()


def execute_query(
    database_path: Path,
    sql_path: Path,
) -> pd.DataFrame:
    """执行 SQL 查询并返回查询结果。"""
    if not database_path.is_file():
        raise FileNotFoundError(
            "数据库不存在，请先运行 prepare_database.py"
        )

    if not sql_path.is_file():
        raise FileNotFoundError(f"SQL 文件不存在：{sql_path}")

    if sql_path.suffix.lower() != ".sql":
        raise ValueError(f"文件不是 SQL 文件：{sql_path}")

    query = sql_path.read_text(encoding="utf-8")

    with closing(sqlite3.connect(database_path)) as connection:
        return pd.read_sql_query(query, connection)


def save_result(
    result_df: pd.DataFrame,
    output_path: Path,
) -> None:
    """将查询结果保存为 CSV 文件。"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result_df.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )


def main() -> int:
    """执行命令行程序。"""
    args = parse_args()

    if args.all:
        sql_paths = sorted((PROJECT_ROOT / "sql").glob("*.sql"))
    else:
        sql_path = (
            args.sql
            if args.sql.is_absolute()
            else PROJECT_ROOT / args.sql
        )
        sql_paths = [sql_path]

    if not sql_paths:
        print("执行失败：sql 文件夹中没有 SQL 文件", file=sys.stderr)
        return 1

    for sql_path in sql_paths:
        output_name = OUTPUT_NAMES.get(
            sql_path.stem,
            f"{sql_path.stem}.csv",
        )
        output_path = args.output/ output_name

        try:
            result_df = execute_query(DATABASE_PATH, sql_path)
            save_result(result_df, output_path)
        except (
            OSError,
            UnicodeError,
            ValueError,
            sqlite3.Error,
            pd.errors.DatabaseError,
        ) as error:
            # print(
            #     f"执行 {sql_path.name} 失败：{error}",
            #     file=sys.stderr,
            # )

            logging.error(
                "执行 %s 失败：%s",
                sql_path.name,
                error,
            )
            return 1

        print(f"\n已执行：{sql_path.name}")
        print(result_df.to_string(index=True))
        print(f"分析结果已保存到：{output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

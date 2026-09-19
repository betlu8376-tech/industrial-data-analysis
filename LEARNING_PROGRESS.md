# 学习进度与下次接续说明

> 最后更新：2026-09-18（Asia/Shanghai）  
> 用途：每次继续学习前先阅读本文件，快速恢复项目背景、当前进度和下一步任务。

## 1. 学习者背景与目标

- 专业：控制科学与工程，硕士二年级。
- 当前基础：学过 Python 基础，正在学习 SQL 和数据结构，刚开始系统学习 Pandas。
- 每日可投入时间：5–6 小时。
- 求职方向：优先准备数据分析/工业数据分析实习，并结合控制专业背景做工业设备数据项目。
- 学习方式：边做项目边学习 Pandas、SQL 和 Git；每一步都需要解释关键 Python 概念和 Git 操作。SQL 基础语法不用逐句解释，遇到新知识点或主动提问时再讲。

## 2. 当前项目

- 项目名称：Industrial Data Analysis
- 本地路径：`D:\Documents\ChatGPT\PythonProject`
- GitHub：`https://github.com/betlu8376-tech/industrial-data-analysis`
- 当前分支：`main`
- 远程仓库：`origin`
- 创建本总结前，工作区干净且 `main` 已与 `origin/main` 同步。当前仅新增的 `LEARNING_PROGRESS.md` 尚未提交，留待下次与代码清理一起提交。
- 最新提交：`633bf2f feat: add SQLite data pipeline and failure analysis`

### 已完成的提交

1. `997aa06 feat: add first pandas analysis`
   - 创建 `.gitignore`、`README.md`、`main.py`。
2. `564a5b9 工业数据`
   - 添加 `data/raw/ai4i2020.csv`。
3. `633bf2f feat: add SQLite data pipeline and failure analysis`
   - 添加 CSV→SQLite 数据管道、SQL 查询和执行脚本。

## 3. Python 环境

- 当前使用：Python 3.13.15。
- PyCharm 解释器：`D:\Documents\ChatGPT\PythonProject\.venv313\Scripts\python.exe`
- 旧环境：`.venv` 使用 Python 3.14，安装 Pandas 时下载源码包并卡在构建依赖；目前不用。
- 当前环境：`.venv313`，已成功安装预编译 wheel。
- 已安装的主要包：
  - pandas 3.0.6
  - numpy 2.5.3
  - matplotlib 3.11.2
  - seaborn 0.13.2
  - jupyter 1.1.1

两个虚拟环境都已写入 `.gitignore`，不会提交到 Git。

## 4. 数据集

- 名称：UCI AI4I 2020 Predictive Maintenance Dataset。
- 文件：`data/raw/ai4i2020.csv`
- 大小：522,048 字节，约 510 KB。
- 数据规模：10,000 行、14 列。
- 缺失值：所有字段均为 10,000 non-null，没有缺失值。
- 主要指标：
  - 正常记录：9,661
  - 故障记录：339
  - 故障率：3.39%
  - 正常率：96.61%
  - 产品类型：L=6,000，M=2,997，H=1,003

### 原始字段

`UDI`、`Product ID`、`Type`、`Air temperature [K]`、`Process temperature [K]`、`Rotational speed [rpm]`、`Torque [Nm]`、`Tool wear [min]`、`Machine failure`、`TWF`、`HDF`、`PWF`、`OSF`、`RNF`。

## 5. 当前项目文件

```text
PythonProject/
├── data/
│   ├── raw/ai4i2020.csv
│   └── processed/industrial_data.db   # 生成文件，已忽略
├── notebooks/
├── reports/figures/
├── sql/01_failure_summary.sql
├── .gitignore
├── README.md
├── main.py
├── prepare_dataset.py
├── run_sql.py
└── LEARNING_PROGRESS.md
```

### 文件职责

- `main.py`：使用 Pandas 读取 CSV，查看数据规模、设备状态数量、正常率和产品类型数量。
- `prepare_dataset.py`：读取 CSV、规范字段名，并创建 `data/processed/industrial_data.db` 中的 `machine_records` 表。
- `sql/01_failure_summary.sql`：用 SQL 统计总数、正常数、故障数和故障率。
- `run_sql.py`：读取 `.sql` 文件，连接 SQLite，通过 Pandas 显示查询结果。
- `.gitignore`：忽略虚拟环境、PyCharm 配置、缓存、敏感文件和生成的 `.db` 文件。

## 6. 今天完成的 Pandas 内容

- 用字典创建 `DataFrame`。
- 使用 `pd.read_csv()` 读取真实 CSV。
- 使用 `head()`、`shape`、`columns`、`info()` 做数据概览。
- 使用 `value_counts()` 统计分类数量。
- 使用布尔条件筛选：`machine_df["Machine failure"] == 0`。
- 理解布尔值求平均：`True=1`、`False=0`，所以 `.mean()` 可计算比例。
- 理解格式化字符串：`f"{rate:.2%}"` 将小数显示为保留两位的百分比。
- 计算设备故障率、正常率和产品类型数量。
- 使用 `rename(columns={...})` 将原始列名转换为 SQL 友好的 snake_case 字段名。
- 使用 `DataFrame.to_sql()` 将数据写入 SQLite。

## 7. 数据库学习进度

### 此前已经掌握

- `SELECT`、`WHERE`、`IN`、`BETWEEN`、`ORDER BY`。
- 聚合函数、`GROUP BY`、`HAVING`。
- `INNER JOIN`、`LEFT JOIN`。
- 子查询。
- `CASE WHEN` 条件聚合。
- 主键、外键。
- `COALESCE`。

### 今天完成

- 理解 CSV 不是数据库表，需要先导入 SQLite。
- 使用 Python 标准库 `sqlite3` 创建和连接数据库。
- 将 Pandas DataFrame 写入 `machine_records` 表。
- 使用 `if_exists="replace"` 避免重复导入。
- 使用 `index=False` 避免写入 Pandas 行号。
- 将 SQL 独立保存在 `sql/` 文件夹，由 Python 读取和执行。
- 完成第一条项目 SQL：设备总数、正常数、故障数和故障率汇总。

### 数据库下一阶段

1. 按 `product_type` 分组计算数量和故障率。
2. 比较正常与故障设备的温度、转速、扭矩和刀具磨损均值。
3. 学习并应用 `DISTINCT`、`LIKE`、`LIMIT`、`NULL` 处理。
4. 进入 CTE 和窗口函数。
5. 学习事务、索引以及基础查询优化。

## 8. Git 学习进度

### 此前已经掌握

- `git status`、`git diff`、`git add`、`git commit`。
- 创建分支、合并分支和解决冲突。
- `.gitignore`。
- GitHub 的 push、fetch、pull 基本流程。

### 今天完成

- 初始化并整理真实项目仓库。
- 理解工作区、暂存区和提交记录的区别。
- 使用 `git rm -r -f --cached .idea` 仅从 Git 索引移除 IDE 配置。
- 配置 `user.name` 和 `user.email`。
- 将分支从 `master` 重命名为 `main`。
- 添加远程仓库 `origin`。
- 理解首次 push 前必须先有 commit；解决 `src refspec main does not match any`。
- 完成首次提交和后续项目提交，并成功推送到 GitHub。
- 理解 `git diff --cached --stat`：查看即将提交的文件和修改量。
- 理解 `git diff --staged`：查看暂存区的具体差异；在分页器中按 `q` 退出。
- 理解 PowerShell 文件名包含空格时需要加引号。

### Git 下一阶段

1. 每完成一个可运行的小功能就提交一次。
2. 使用功能分支开发下一项分析。
3. 在 GitHub 练习 Pull Request 流程。
4. 改进提交信息，继续使用 `feat:`、`fix:`、`docs:` 等前缀。

## 9. 今天遇到的问题和结论

- PyCharm 的 Python 控制台只能输入 Python，不能直接执行 `python -m pip ...`；安装命令应放在终端。
- Python 3.14 当时没有匹配的 Pandas wheel，导致下载源码包并尝试构建；切换到 Python 3.13 后解决。
- Conda 镜像曾卡在 `Collecting package metadata`；最终使用 Python 3.13 虚拟环境和清华 PyPI 镜像安装 wheel。
- Jupyter 会安装很多依赖，这是其内核、终端、服务器和交互组件所需的正常依赖链。
- `.gitignore` 不会自动移除已经暂存的文件，需要使用 `git rm --cached`。
- Git 作者身份只用于提交记录，不是 GitHub 登录凭据。
- `Machine failure` 为 0/1 时，平均值等于故障率；条件表达式 `(machine_failure == 0).mean()` 等于正常率。
- Pandas `Series` 是一维数据，调用 `.mean()` 不需要 `axis=1`。

## 10. 下次开始时优先处理

当前仓库虽然干净并已推送，但最新提交中还有两个代码质量问题。下次先修复，再继续分析。

### 任务1：统一脚本名称

实际文件名是 `prepare_dataset.py`，但 `run_sql.py` 的错误提示写的是 `prepare_database.py`。推荐将文件统一改为 `prepare_database.py`：

```powershell
git mv prepare_dataset.py prepare_database.py
```

### 任务2：清理 `main.py`

- 删除未使用的 `from operator import index`。
- `failure_count` 改为 `failure_counts`。
- `failure_rate` 实际计算正常率，应改为 `qualified_rate` 或 `normal_rate`。
- 补充运算符两边的空格，减少多余空行。

### 任务3：验证并提交修复

```powershell
python prepare_database.py
python run_sql.py
git add -A
git diff --cached --stat
git commit -m "fix: clean data pipeline scripts"
git push
```

### 任务4：继续项目分析

创建 `sql/02_failure_rate_by_type.sql`，按产品类型分析故障率；随后使用 Pandas/Seaborn 生成第一张图并保存到 `reports/figures/`。

## 11. 下次快速恢复命令

```powershell
cd D:\Documents\ChatGPT\PythonProject
git status
git log --oneline --decorate -5
```

然后阅读本文件的“下次开始时优先处理”部分。

给 Codex 的开场指令可直接写：

```text
请先读取项目根目录的 LEARNING_PROGRESS.md，然后从“下次开始时优先处理”继续带我做。
```

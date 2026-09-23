# Industrial Data Analysis

基于 AI4I 2020 预测性维护数据集，使用 Python、Pandas、SQLite 和 Matplotlib 分析工业设备的运行状态与故障特征。

## 项目目标

- 使用 Pandas 完成数据读取与处理
- 使用 SQLite 进行分组统计和指标计算
- 分析产品类型、故障类型及运行条件与设备故障的关系
- 使用 Matplotlib 展示分析结果
- 使用 Git 和 GitHub 管理项目版本

## 数据集

项目使用 AI4I 2020 Predictive Maintenance Dataset，共包含 10,000 条设备运行记录。

主要字段包括：

- 产品类型
- 空气温度与加工温度
- 转速
- 扭矩
- 刀具磨损时间
- 设备故障状态
- 不同故障类型

## 技术栈

- Python
- Pandas
- SQLite
- Matplotlib
- Git
- GitHub

## 分析流程

```text
原始 CSV 数据
    ↓
数据清洗与字段规范化
    ↓
写入 SQLite 数据库
    ↓
SQL 分组与指标计算
    ↓
导出分析结果 CSV
    ↓
Pandas 读取结果
    ↓
Matplotlib 数据可视化
```

## 主要分析结果

### 1. 整体故障情况

数据集中共有 10,000 条记录，其中 339 条发生设备故障，整体故障率为 **3.39%**。

### 2. 不同产品类型的故障率

| 产品类型 | 记录数 | 故障数 | 故障率 |
|---|---:|---:|---:|
| L | 6000 | 235 | 3.92% |
| M | 2997 | 83 | 2.77% |
| H | 1003 | 21 | 2.09% |

L 类产品的故障率最高，H 类产品的故障率最低。

![Failure rate by product type](reports/figures/failure_by_product_type.png)

### 3. 不同故障类型

| 故障类型 | 故障数 | 占全部记录比例 |
|---|---:|---:|
| HDF | 115 | 1.15% |
| OSF | 98 | 0.98% |
| PWF | 95 | 0.95% |
| TWF | 46 | 0.46% |
| RNF | 19 | 0.19% |

HDF 是出现次数最多的故障类型。不同故障类型可能同时出现在同一条记录中，因此各类故障数之和可能大于设备故障记录总数。

![Failure type summary](reports/figures/failure_type_summary.png)

### 4. 正常与故障状态的运行条件

与正常组相比，故障组表现出以下特征：

- 平均扭矩提高约 **26.60%**
- 平均刀具磨损时间提高约 **34.76%**
- 平均转速降低约 **2.84%**
- 温度差异相对较小

![Failure condition comparison](reports/figures/04_failure_condition_comparison.png)

### 5. 刀具磨损与故障率

刀具磨损低于 200 分钟时，故障率约为 `2.21%–2.66%`。

当刀具磨损达到 200 分钟以上时，故障率上升至 **15.36%**。

![Failure rate by tool wear](reports/figures/05_failure_by_tool_wear.png)

### 6. 扭矩与故障率

| 扭矩区间 | 记录数 | 故障数 | 故障率 |
|---|---:|---:|---:|
| 0–19 N·m | 228 | 34 | 14.91% |
| 20–39 N·m | 4712 | 28 | 0.59% |
| 40–59 N·m | 4821 | 177 | 3.67% |
| 60–79 N·m | 239 | 100 | 41.84% |

故障率在极低和极高扭矩区间明显升高，其中 `60–79 N·m` 区间的故障率最高。

![Failure rate by torque](reports/figures/06_failure_by_torque.png)

## 项目结构

```text
industrial-data-analysis/
├── data/
│   ├── raw/                         # 原始数据
│   └── processed/                   # SQLite 数据库
├── reports/
│   ├── figures/                     # 分析图表
│   └── *.csv                        # SQL 查询结果
├── sql/                             # SQL 分析脚本
├── prepare_database.py              # 数据清洗与数据库创建
├── run_sql.py                       # 执行 SQL 并导出结果
├── plot_failure_rate.py             # 基础故障率图表
├── 04_plot_condition_comparison.py  # 运行条件对比图
├── 05_plot_failure_by_tool_wear.py  # 刀具磨损分析图
├── 06_plot_failure_by_torque.py     # 扭矩分析图
└── README.md
```

## 运行方法

### 1. 安装依赖

```powershell
pip install pandas matplotlib
```

### 2. 创建 SQLite 数据库

```powershell
python prepare_database.py
```

### 3. 执行 SQL 分析

在 `run_sql.py` 中选择需要执行的 SQL 文件和输出 CSV 路径，然后运行：

```powershell
python run_sql.py
```

也可以使用 `run_sql2.py`，无需修改脚本中的路径：
### 执行指定 SQL
```powershell
python run_sql2.py --sql sql/06_failure_by_torque.sql
```
### 按顺序执行全部 SQL
```powershell
python run_sql2.py --all
```
### 4. 生成图表

例如生成扭矩分析图：

```powershell
python 06_plot_failure_by_torque.py
```

生成的图片保存在：

```text
reports/figures/
```

## 分析结论

分析结果表明，设备故障与刀具磨损和扭矩具有明显关联：

- 高刀具磨损状态下故障率显著上升
- 极低或极高扭矩状态下故障风险较高
- 故障组的平均扭矩和刀具磨损时间明显高于正常组
- 产品类型之间存在一定的故障率差异

以上结果表示统计关联，不能单独证明因果关系。

## 后续改进

- 自动化执行全部 SQL 分析
- 增加数据分布和相关性分析
- 增加异常值检测
- 尝试建立设备故障预测模型
- 制作交互式数据分析仪表板
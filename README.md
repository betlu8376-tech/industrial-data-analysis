# Industrial Data Analysis

基于 AI4I 2020 预测性维护数据集，使用 Python、Pandas、SQLite 和 Matplotlib 分析工业设备的运行状态与故障特征，并通过 FastAPI 提供统计查询和故障率计算接口。

## 项目目标

- 使用 Pandas 完成数据读取与处理
- 使用 SQLite 进行分组统计和指标计算
- 分析产品类型、故障类型及运行条件与设备故障的关系
- 使用 Matplotlib 展示分析结果
- 使用 Git 和 GitHub 管理项目版本
- 使用 FastAPI 提供 JSON 接口，通过 Pydantic 校验输入与输出
- 使用 pytest 自动测试 SQL 查询和接口行为

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
- FastAPI、Uvicorn
- Pydantic
- pytest、HTTPX（接口测试）
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
├── run_sql2.py                      # 支持命令行参数的 SQL 执行工具
├── api.py                           # FastAPI 查询与计算接口
├── test_run_sql2.py                 # SQL 工具测试
├── test_api.py                      # 接口测试
├── plot_failure_rate.py             # 基础故障率图表
├── 04_plot_condition_comparison.py  # 运行条件对比图
├── 05_plot_failure_by_tool_wear.py  # 刀具磨损分析图
├── 06_plot_failure_by_torque.py     # 扭矩分析图
└── README.md
```

## 运行方法

### 1. 安装依赖

```powershell
python -m pip install pandas matplotlib
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
### 指定 CSV 输出目录

在项目根目录运行时，可以用 `--output` 指定 CSV 的保存目录：

```powershell
python run_sql2.py --sql sql/01_failure_summary.sql --output reports/custom
```

不提供 `--output` 时，CSV 默认保存到项目的 `reports` 目录。

### 指定数据库路径

默认使用 `data/processed/industrial_data.db`。在项目根目录的 PowerShell 中，可以设置 `DATABASE_PATH` 后运行：

```powershell
$env:DATABASE_PATH = "data\processed\industrial_data.db"
python run_sql2.py --sql sql/01_failure_summary.sql
```

若要使用其他数据库，请将变量值改为对应的 SQLite 文件路径。该数据库需要包含 SQL 查询所用的表和字段。设置的变量只在当前终端及其启动的程序中生效；清除后恢复默认路径：

```powershell
Remove-Item Env:\DATABASE_PATH
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

## API 服务

API 提供两类功能：读取数据库中的统计结果，以及根据客户端提交的数量计算故障率。所有业务接口返回 JSON。

### 1. 安装接口与测试依赖

在项目目录中，使用已选定的 Python 环境执行：

```powershell
python -m pip install fastapi uvicorn pydantic pillow pytest httpx
```

当前 `api.py` 还包含 `PIL.ImtImagePlugin` 的导入，因此启动时需要 Pillow。这个导入没有参与接口逻辑；移除该导入后，接口本身不再需要 Pillow。

### 2. 启动服务

从项目根目录运行：

```powershell
python -m uvicorn api:app --host 127.0.0.1 --port 8000
```

`api:app` 表示加载 `api.py` 中的 `app` 对象。`127.0.0.1` 只供当前电脑访问，`8000` 是服务端口。按 `Ctrl+C` 停止服务；上述命令未开启自动重载，修改接口代码后需要保存并重启。

如果 PowerShell 的 Conda 初始化失败，可以直接指定当前开发环境的解释器。以下路径仅适用于本机，其他电脑应替换为自己的环境路径：

```powershell
& 'D:\anaconda\envs\industrial-ai\python.exe' -m uvicorn api:app --host 127.0.0.1 --port 8000
```

服务启动后，打开 [交互式接口文档](http://127.0.0.1:8000/docs)。展开接口，点击 **Try it out**，填写参数或请求体，再点击 **Execute** 发送真实请求。

### 3. 接口说明

| 方法 | 路径 | 功能 |
|---|---|---|
| GET | `/summary` | 查询整体故障统计 |
| GET | `/summary/{metric_name}` | 查询单个统计指标 |
| POST | `/failure-rate` | 根据提交的数量计算故障率，不读取或写入数据库 |

两个 GET 接口依赖 SQLite 数据库和 `sql/01_failure_summary.sql`。数据库默认位于 `data/processed/industrial_data.db`，可通过 `DATABASE_PATH` 环境变量指定其他数据库，规则与 SQL 工具相同。

#### GET /summary

浏览器访问 [整体统计](http://127.0.0.1:8000/summary)，当前数据集的响应为：

```json
{
  "total_count": 10000,
  "normal_count": 9661,
  "failure_count": 339,
  "failure_rate_percent": 3.39
}
```

可选查询参数 `decimals` 为整数，默认值为 `2`，允许范围为 `0` 到 `2`。例如访问 [保留一位小数的统计](http://127.0.0.1:8000/summary?decimals=1)，故障率为 `3.4`。参数为 `abc`、`-1` 或 `3` 时返回 `422`。

#### GET /summary/{metric_name}

`metric_name` 是路径参数，可选值为 `total_count`、`normal_count`、`failure_count` 和 `failure_rate_percent`。

例如访问 [故障数量](http://127.0.0.1:8000/summary/failure_count)，响应为：

```json
{"failure_count": 339}
```

指标不存在时返回 `404` 和 `{"detail": "Metric not found"}`。

#### POST /failure-rate

在 `/docs` 中选择 **POST /failure-rate**，提交 JSON 请求体：

```json
{
  "total_count": 10000,
  "failure_count": 339
}
```

成功时返回 `200`：

```json
{"failure_rate_percent": 3.39}
```

计算公式为 `100 × failure_count / total_count`，结果使用 Python 的 `round(..., 2)` 舍入，不保证显示固定两位小数。

输入规则：

- 两个字段均必填，类型为整数。
- `total_count` 必须大于 `0`。
- `failure_count` 必须大于等于 `0`，且不能超过 `total_count`。
- `failure_count` 为 `0` 时故障率为 `0%`，等于总数时为 `100%`。

字段校验失败时返回 `422`，错误信息指出字段位置。故障数超过总数时也返回 `422`，响应为：

```json
{"detail": "failure_count cannot exceed total_count"}
```

浏览器地址栏直接访问 `/failure-rate` 会发送 GET 请求，而该接口只接受 POST，因此返回 `405 Method Not Allowed`。请使用 `/docs` 或支持 POST 的客户端。

### 4. 自动测试

在项目根目录执行：

```powershell
python -m pytest test_run_sql2.py test_api.py -v
```

接口测试通过 `TestClient` 直接调用应用，不需要先启动 Uvicorn。当前共 10 个测试：4 个 SQL 工具测试、6 个接口测试。接口测试覆盖正常计算、故障数超过总数、总数为零、故障数为负数、零故障和全部故障。

本机也可以直接指定解释器：

```powershell
& 'D:\anaconda\envs\industrial-ai\python.exe' -m pytest test_run_sql2.py test_api.py -v
```

预期结果为 `10 passed`。若同时出现依赖库的弃用警告，应结合测试结果区分警告与失败；警告本身不等于测试失败。

## 分析结论

分析结果表明，设备故障与刀具磨损和扭矩具有明显关联：

- 高刀具磨损状态下故障率显著上升
- 极低或极高扭矩状态下故障风险较高
- 故障组的平均扭矩和刀具磨损时间明显高于正常组
- 产品类型之间存在一定的故障率差异

以上结果表示统计关联，不能单独证明因果关系。

## 后续改进

- 增加数据分布和相关性分析
- 增加异常值检测
- 尝试建立设备故障预测模型
- 制作交互式数据分析仪表板

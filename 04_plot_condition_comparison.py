from pathlib import Path
from matplotlib import pyplot as plt
import pandas as pd


project_root = Path(__file__).resolve().parent
csv_path = (
    project_root
    / "reports"
    / "04_failure_condition_comparison.csv"
)

condition_df = pd.read_csv(csv_path)
condition_df = condition_df.set_index("machine_status")

metric_columns = [
    "avg_air_temperature_k",
    "avg_process_temperature_k",
    "avg_rotational_speed_rpm",
    "avg_torque_nm",
    "avg_tool_wear_min",
]

normal_values = condition_df.loc["Normal", metric_columns]
failure_values = condition_df.loc["Failure", metric_columns]

# 计算故障组相对正常组的变化百分比
difference_percent = (
    (failure_values - normal_values)
    / normal_values
    * 100
)

plot_df = pd.DataFrame(
    {
        "metric": [
            "Air Temperature",
            "Process Temperature",
            "Rotational Speed",
            "Torque",
            "Tool Wear",
        ],
        "difference_percent": difference_percent.to_numpy(),
    }
)




figure_path = (
    project_root
    / "reports"
    / "figures"
    / "04_failure_condition_comparison.png"
)

# 正值使用橙色，负值使用蓝色
colors = [
    "#E69F00" if value >= 0 else "#0072B2"
    for value in plot_df["difference_percent"]
]

fig, ax = plt.subplots(figsize=(8, 5))

bars = ax.barh( #barh 横向绘制柱状图，bar纵向
    plot_df["metric"],
    plot_df["difference_percent"],
    color=colors,
)

# 在0的位置画参考线
ax.axvline(0, color="black", linewidth=0.8)

# 在柱子旁显示百分比
ax.bar_label(
    bars,
    fmt="%.2f%%",
    padding=2,
)

ax.set_xlabel("Difference from Normal (%)")
ax.set_ylabel("Operating Condition")
ax.set_title("Operating Condition Difference: Failure vs Normal")
ax.set_xlim(-10, 40)

# 让第一个指标显示在最上面
ax.invert_yaxis()

fig.tight_layout()

figure_path.parent.mkdir(parents=True, exist_ok=True)

fig.savefig(
    figure_path,
    dpi=300,
    bbox_inches="tight",
)

print(f"图表已保存到：{figure_path}")

plt.show()

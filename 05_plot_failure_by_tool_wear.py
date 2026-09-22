from pathlib import Path
from matplotlib import pyplot as plt
import pandas as pd


project_root = Path(__file__).resolve().parent

csv_path=(
    project_root
    / "reports"
    / "05_failure_by_tool_wear.csv"
)

figure_path = (
    project_root
    / "reports"
    / "figures"
    / "05_failure_by_tool_wear.png"
)

wear_df = pd.read_csv(csv_path)
print(wear_df)


fig, ax = plt.subplots(figsize=(8, 5))

ax.plot(
    wear_df["tool_wear_group"],
    wear_df["failure_rate_percent"],
    color="#0072B2",
    marker="o",
    markersize=8,
    linewidth=3,
)

# 突出显示最高磨损组
ax.scatter(
    wear_df["tool_wear_group"].iloc[-1],
    wear_df["failure_rate_percent"].iloc[-1],
    color="#E69F00",
    s=90,
    zorder=3,
)

# 为每个点添加故障率和样本量
for group, rate, count in zip(
    wear_df["tool_wear_group"],
    wear_df["failure_rate_percent"],
    wear_df["total_nums"],
):
    ax.annotate(
        f"{rate:.2f}%\n(n={count})",
        xy=(group, rate),
        xytext=(0, 10),
        textcoords="offset points",
        ha="center",
    )

max_rate = wear_df["failure_rate_percent"].max()
ax.set_ylim(0, max_rate * 1.3)

ax.set_xlabel("Tool Wear (min)")
ax.set_ylabel("Failure Rate (%)")
ax.set_title("Failure Rate Trend by Tool Wear")

ax.yaxis.grid(
    True,
    linestyle="--",
    alpha=0.3,
)
ax.set_axisbelow(True)


fig.tight_layout()

figure_path.parent.mkdir(
    parents=True,
    exist_ok=True,
)

fig.savefig(
    figure_path,
    dpi=300,
    bbox_inches="tight",
)

print(f"图表已保存到：{figure_path}")

plt.show()

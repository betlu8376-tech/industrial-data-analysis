from pathlib import Path
from matplotlib import pyplot as plt
import pandas as pd


project_root = Path(__file__).resolve().parent

csv_path=(
    project_root
    / "reports"
    / "06_failure_by_torque.csv"
)

figure_path = (
    project_root
    / "reports"
    / "figures"
    / "06_failure_by_torque.png"
)

torque_df = pd.read_csv(csv_path)
print(torque_df)

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(
    torque_df["torque_nm_group"],
    torque_df["failure_rate_percent"],
    color=["#D55E00", "#0072B2", "#0072B2", "#D55E00"]
)


labels = [
    f"{rate:.2f}%\n(n={count})"
    for rate, count in zip(
        torque_df["failure_rate_percent"],
        torque_df["total_nums"],
    )
]


ax.bar_label(
    bars,
    labels=labels,
    color="black",
    padding=2
)

ax.set_xlabel("Torque (nm)")
ax.set_ylabel("failure_percent(%)")
ax.set_title("Failure by Torque")
max_rate = torque_df["failure_rate_percent"].max()
ax.set_ylim(0, max_rate * 1.2)


fig.tight_layout()

figure_path.parent.mkdir(parents=True, exist_ok=True)

fig.savefig(
    figure_path,
    dpi=600,
    bbox_inches="tight",
)

print(f"图表已保存到：{figure_path}")

plt.show()


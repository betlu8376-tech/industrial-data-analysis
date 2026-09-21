from pathlib import Path
from matplotlib import pyplot as plt
import pandas as pd

project_root = Path(__file__).resolve().parent
# csv_path = project_root / "reports" / "failure_by_product_type.csv"
csv_path = project_root / "reports" / "failure_type_summary.csv"

result_df = pd.read_csv(csv_path)

# print(result_df.shape)
# print(result_df.head(2))
# print(result_df.tail(2))
# print(result_df)

# fig, ax = plt.subplots(figsize=(6, 4))
# bars=ax.bar(result_df["product_type"], result_df["failure_rate_percent"])
# # 在柱子上方显示数值，并留出空间
# ax.bar_label(bars, fmt="%.2f%%", padding=3)
# ax.set_ylim(0, 4.5)
# ax.set_xlabel("Product Type")
# ax.set_ylabel("Failure Rate(%)")
# ax.set_title("Failure Rate by Product Type")



fig, ax = plt.subplots(figsize=(12, 8))
bars=ax.bar(result_df["failure_type"], result_df["failure_percent"])
ax.bar_label(bars,fmt="%.2f%%", padding=3)
ax.set_ylim=(0,1.5)
ax.set_xlabel("Failure Type")
ax.set_ylabel("Failure Percent(%)")
ax.set_title("Failure Rate By Failure Type")


# fig_path=project_root / "reports"/"figures" / "failure_by_product_type.png"
fig_path=project_root / "reports"/"figures" / "failure_type_summary.png"

fig.tight_layout()
fig.savefig(
    fig_path,
    dpi=500,#每英寸的像素点
    bbox_inches="tight",#裁掉多余的空白，避免裁掉标题和其他文字
)
plt.show()

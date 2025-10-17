import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns

# 基准值（来自完整场景）
baseline_precision = 34.23
baseline_recall = 46.34
baseline_f1 = 39.38

# 原始数据（按表格逐行录入）
data = [
    # w/o positive scenarios
    {"Scenario": "#1", "Type": "Positive", "Precision": 77.78, "Recall": 8.54, "F1": 15.38},  # 原表未填Recall/F1
    {"Scenario": "#2", "Type": "Positive", "Precision": 66.67, "Recall": 2.44, "F1": 4.71},
    {"Scenario": "#3", "Type": "Positive", "Precision": 36.96, "Recall": 41.46, "F1": 39.08},

    # w/o negative scenarios
    {"Scenario": "E0", "Type": "Negative", "Precision": 25.47, "Recall": 50.00, "F1": 33.74},
    {"Scenario": "E1.1", "Type": "Negative", "Precision": 28.24, "Recall": 45.12, "F1": 34.74},
    {"Scenario": "E1.2", "Type": "Negative", "Precision": 23.30, "Recall": 50.00, "F1": 31.78},
    {"Scenario": "E1.3", "Type": "Negative", "Precision": 40.28, "Recall": 35.37, "F1": 37.66},
    {"Scenario": "E1.4", "Type": "Negative", "Precision": 35.82, "Recall": 29.27, "F1": 32.21},
    {"Scenario": "E1.6", "Type": "Negative", "Precision": 22.73, "Recall": 42.68, "F1": 29.67},
    {"Scenario": "E1.8", "Type": "Negative", "Precision": 32.95, "Recall": 35.37, "F1": 34.12},
    {"Scenario": "E1.10", "Type": "Negative", "Precision": 34.44, "Recall": 37.80, "F1": 36.05},
    {"Scenario": "E1.11", "Type": "Negative", "Precision": 31.19, "Recall": 41.46, "F1": 35.60},
    {"Scenario": "E1.12", "Type": "Negative", "Precision": 34.82, "Recall": 45.12, "F1": 38.34},
    {"Scenario": "E2.1", "Type": "Negative", "Precision": 33.33, "Recall": 47.56, "F1": 39.20},
    {"Scenario": "E4.1", "Type": "Negative", "Precision": 36.71, "Recall": 35.37, "F1": 36.02}
]

# 转换为DataFrame
df = pd.DataFrame(data)

# 计算Δ值
df["ΔPrecision"] = baseline_precision - df["Precision"]
df["ΔRecall"] = baseline_recall - df["Recall"]
df["ΔF1"] = baseline_f1 - df["F1"]

# 过滤无效数据（原表中场景#1的Recall/F1为空）
df = df.dropna(subset=["ΔRecall", "ΔF1"])

# 设置可视化参数
df["Color"] = df["ΔF1"].apply(lambda x: "red" if x < 0 else "green")  # 颜色编码
df["BubbleSize"] = (abs(df["ΔF1"]) * 15).clip(50, 500)  # 气泡大小（限制最小/最大值）

# 绘制分面散点图
plt.figure(figsize=(14, 8))
sns.set_style("whitegrid")
ax = sns.scatterplot(
    data=df,
    x="ΔPrecision",
    y="ΔRecall",
    hue="Type",  # 按正/负场景分组颜色
    size="BubbleSize",  # 气泡大小反映|ΔF1|
    sizes=(50, 500),  # 气泡尺寸范围
    alpha=0.8,
    edgecolor="black",
    palette={"Positive": "purple", "Negative": "gray"}  # 自定义颜色
)

# 添加场景标签
for line in range(len(df)):
    ax.text(
        df["ΔPrecision"].iloc[line] + 0.5,
        df["ΔRecall"].iloc[line] + 0.5,
        df["Scenario"].iloc[line],
        horizontalalignment='left',
        size=9,
        color="black"
    )

# 添加基准线和标注
plt.axvline(0, color="gray", ls="--", lw=1, alpha=0.5)
plt.axhline(0, color="gray", ls="--", lw=1, alpha=0.5)
plt.xlabel("ΔPrecision (%)", fontsize=12, labelpad=10)
plt.ylabel("ΔRecall (%)", fontsize=12, labelpad=10)
#plt.title("Impact of Removing Scenarios: Precision-Recall Tradeoff with F1 Impact\n"
#          f"Baseline (Full Scenarios): Precision={baseline_precision}%, Recall={baseline_recall}%, F1={baseline_f1}%",
#          fontsize=14, pad=20)

# 自定义图例
handles, labels = ax.get_legend_handles_labels()
legend1 = ax.legend(
    handles[1:3], ["Positive", "Negative"],
    title="Scenario Type",
    loc="upper left",
    bbox_to_anchor=(1.02, 1)
)
ax.add_artist(legend1)

# 添加气泡大小图例
from matplotlib.lines import Line2D

bubble_legend = [
    Line2D([0], [0],
           marker="o",
           markersize=np.sqrt(50) / 2,
           markerfacecolor="grey",
           markeredgecolor="black",
           linestyle="None",
           label="Small"),
    Line2D([0], [0],
           marker="o",
           markersize=np.sqrt(250) / 2,
           markerfacecolor="grey",
           markeredgecolor="black",
           linestyle="None",
           label="Large")
]
ax.legend(handles=bubble_legend, loc="upper left", bbox_to_anchor=(1.02, 0.7), title="ΔF1")

# 调整坐标轴范围
x_min, x_max = ax.get_xlim()
y_min, y_max = ax.get_ylim()
ax.set_xlim(x_min - 5, x_max + 5)
ax.set_ylim(y_min - 5, y_max + 5)

# 调整布局
plt.tight_layout()
plt.show()
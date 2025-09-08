import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. 加载数据
data_path = r'D:\DATA\Polar\BaseBM\S39_BM_RegionMonthly.csv'
data = pd.read_csv(data_path)

# 2. 转换 Date 列为日期格式
data['Date'] = pd.to_datetime(data['Date'])

# 3. 按月份分组
data['Month'] = data['Date'].dt.to_period('M')  # 提取月份（年-月）

# 4. 设置绘图风格
sns.set(style="whitegrid")

# 5. 按月份排序
months = sorted(data['Month'].unique())  # 使用 sorted() 对 Period 类型进行排序

# 计算子图网格的行和列
n_months = len(months)
n_cols = 3  # 每行显示 3 个图
n_rows = (n_months // n_cols) + (n_months % n_cols > 0)  # 根据月份数量计算行数

# 6. 创建一个大的画布
fig, axes = plt.subplots(nrows=n_rows, ncols=n_cols, figsize=(15, 5 * n_rows))

# 展平 axes 数组（以便更方便的索引）
axes = axes.flatten()

# 7. 绘制每个月的数据
for i, month in enumerate(months):
    monthly_data = data[data['Month'] == month]

    # 绘制条形图：每个地区的物种丰富度
    sns.barplot(x='Region', y='Species_Richness', data=monthly_data, palette='viridis', ax=axes[i])

    # 设置标题和标签
    axes[i].set_title(f"Species Richness in {month}", fontsize=10)
    axes[i].set_xlabel("Region", fontsize=8)
    axes[i].set_ylabel("Species Richness", fontsize=8)
    axes[i].tick_params(axis='x', rotation=45)  # 旋转x轴标签

    # 设定每个图的 x 轴和 y 轴的范围一致
    axes[i].set_ylim(data['Species_Richness'].min() - 1, data['Species_Richness'].max() + 1)

# 8. 去掉多余的空白子图（如果有的话）
for j in range(i + 1, len(axes)):
    fig.delaxes(axes[j])

# 9. 调整子图之间的间距和整体布局
plt.subplots_adjust(hspace=0.6, wspace=0.3, top=0.95, bottom=0.05)  # 增加上下间距，避免重叠

# 10. 显示大图
plt.show()

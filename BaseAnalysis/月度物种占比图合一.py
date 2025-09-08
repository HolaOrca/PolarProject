import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.colors import ListedColormap
import seaborn as sns  # 高级调色板生成

# 读取CSV文件
data = pd.read_csv(r"D:\DATA\Polar\BaseBM\S39_BM_Avians_ratio_Monthly.csv")

# 数据预处理
data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
data = data.dropna(subset=['Date', 'Species', 'percentage'])
data['Month'] = data['Date'].dt.to_period('M')
monthly_groups = data.groupby('Month')

# 提取所有物种的唯一值
unique_species = data['Species'].unique()

# 设置画布
num_months = len(monthly_groups)
cols = 3  # 每行3个饼图
rows = (num_months + cols - 1) // cols
fig, axes = plt.subplots(rows, cols, figsize=(20, 6 * rows))
axes = axes.flatten()

# 颜色设置 - 使用高级渐变调色板
palette = sns.color_palette("Spectral", n_colors=len(unique_species))  # Spectral 适合学术用
species_colors = {species: palette[i] for i, species in enumerate(unique_species)}

# 绘制饼图
for idx, (month, group) in enumerate(monthly_groups):
    species = group['Species']
    percentages = group['percentage']

    # 自定义函数：仅占比大于10%时显示标签
    def autopct_func(pct):
        return f'{pct:.1f}%' if pct > 10 else ''

    wedges, _, autotexts = axes[idx].pie(
        percentages,
        autopct=lambda pct: autopct_func(pct),
        startangle=90,
        colors=[species_colors[sp] for sp in species]
    )
    # 调整文字标签颜色
    for autotext in autotexts:
        autotext.set_color("black")
        autotext.set_fontsize(8)
    axes[idx].set_title(f"{month}", fontsize=12, fontweight='bold')

# 删除多余的空子图
for i in range(idx + 1, len(axes)):
    fig.delaxes(axes[i])

# 添加图例到右侧
legend_handles = [Patch(facecolor=species_colors[sp], edgecolor='none', label=sp) for sp in unique_species]
fig.legend(
    handles=legend_handles,
    title="Species",
    loc="center left",
    bbox_to_anchor=(1.05, 0.5),
    fontsize=10,
    frameon=False
)

# 调整整体布局并保存图像
plt.tight_layout()
output_file = r"D:\DATA\Polar\BaseBM\output\Refined_Species_Distribution_Enhanced.png"
plt.savefig(output_file, dpi=600, bbox_inches='tight')
plt.close()

print(f"Enhanced pie chart saved to {output_file}")

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import os

# 读取 CSV 文件
input_file_path = r'D:\DATA\Polar\BaseBM\S39_BM_pre.csv'
data = pd.read_csv(input_file_path)

# 过滤掉 Count 为 0 的记录，并使用 .copy() 创建新 DataFrame
filtered_data = data[data['Count'] > 0].copy()

# 修改 'Date' 列以避免警告
filtered_data['Date'] = pd.to_datetime('2023-' + filtered_data['Date'], format='%Y-%d-%b')

# 分组计算每个月的物种丰富度
species_richness_month = filtered_data.groupby(filtered_data['Date'].dt.to_period('M'))['Species'].nunique().reset_index(name='Species_Richness')
species_richness_month['Date'] = species_richness_month['Date'].dt.to_timestamp()
species_richness_month = species_richness_month.sort_values(by='Date')

# 设置字体（支持中文）
font = FontProperties(fname=r'C:\Windows\Fonts\simhei.ttf', size=12)

# 绘图
plt.figure(figsize=(10, 6))  # 设置图形大小
plt.plot(
    species_richness_month['Date'],
    species_richness_month['Species_Richness'],
    marker='o', linestyle='-', label='Species Richness'
)

# 添加标题和标签
plt.title('Monthly variation in species richness', fontproperties=font)
plt.xlabel('Date', fontproperties=font)
plt.ylabel('Species Richness', fontproperties=font)

# 统一标注位置在数据点上方
for i, row in species_richness_month.iterrows():
    plt.text(row['Date'], row['Species_Richness'] + 0.5,  # 上方偏移 0.5
             f"{row['Species_Richness']}",
             ha='center', va='bottom', fontproperties=font)

# 设置 y 轴上限为 18
plt.ylim(0, 18)

# 美化图形
plt.xticks(rotation=45)
plt.grid(alpha=0.5, linestyle='--')
plt.legend(prop=font)
plt.tight_layout()

# 保存图表结果为文件
output_dir = os.path.dirname(input_file_path)  # 获取输入文件的目录
output_file_path = os.path.join(output_dir, 'S39_BM_Monthly.csv')  # 生成输出文件路径

# 输出计算结果到 CSV 文件
species_richness_month.to_csv(output_file_path, index=False)

# 显示图形
plt.show()

# 输出结果的保存路径
print(f"图表已保存，计算结果已保存在 {output_file_path}")

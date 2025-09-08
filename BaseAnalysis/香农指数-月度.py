import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

# 读取 CSV 文件
data = pd.read_csv(r'D:\DATA\Polar\BaseBM\S39_BM_pre.csv')

# 过滤掉 Count 为 0 的记录，并使用 .copy() 创建新 DataFrame
filtered_data = data[data['Count'] > 0].copy()

# 计算每月的香农多样性
def calculate_shannon_diversity(group):
    proportions = group['Count'] / float(group['Count'].sum())
    shannon_index = -np.sum(proportions * np.log(proportions))
    return pd.Series({
        'Shannon_Diversity': shannon_index
    })

# 将 'Date' 转换为日期格式以便按月分组
filtered_data['Date'] = pd.to_datetime('2023-' + filtered_data['Date'], format='%Y-%d-%b')

# 按月分组并计算香农多样性
shannon_diversity_month = filtered_data.groupby(filtered_data['Date'].dt.to_period('M')).apply(calculate_shannon_diversity).reset_index()

# 按日期升序排序
shannon_diversity_month = shannon_diversity_month.sort_values(by='Date')
# 显示结果
print(shannon_diversity_month)

# 可视化
font = FontProperties(fname=r'C:\Windows\Fonts\simhei.ttf', size=14)  # 路径根据你的系统调整

plt.figure(figsize=(10, 6))  # 设置图形大小

# 绘制图表
plt.plot(shannon_diversity_month['Date'].astype(str), shannon_diversity_month['Shannon_Diversity'], marker='o')

# 设置标题和标签，标题使用中文字体，坐标轴使用英文
plt.title('Monthly Shannon Diversity Change', fontproperties=font)
plt.xlabel('Month')
plt.ylabel('Shannon Diversity')

# 显示月度数据
for i, row in shannon_diversity_month.iterrows():
    plt.text(row['Date'].strftime('%Y-%m'), row['Shannon_Diversity'], f"{row['Shannon_Diversity']:.2f}",
             ha='center', va='bottom')

plt.xticks(rotation=45)  # 旋转x轴标签以便于阅读
plt.tight_layout()  # 调整布局以防止标签被切割

plt.show()
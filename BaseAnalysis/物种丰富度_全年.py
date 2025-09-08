import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

# 读取 CSV 文件
data = pd.read_csv(r'D:\DATA\Polar\BaseBM\S39_BM_pre.csv')

# 过滤掉 Count 为 0 的记录，并使用 .copy() 创建新 DataFrame
filtered_data = data[data['Count'] > 0].copy()

# 计算全年全区域物种丰富度
species_richness_year_all = filtered_data['Species'].nunique()
print(f"全年全区域物种丰富度：{species_richness_year_all}")
#读取文件S39_BM_RegionMonthly，将每月的Region的Species_Richness占比计算出来，并输出到同路径名为S39_BM_RegionRateMonthly.csv的文件中
import pandas as pd
import os

# 读取 S39_BM_RegionMonthly.csv 文件
input_file_path = r'D:\DATA\Polar\BaseBM\S39_BM_RegionMonthly.csv'
data = pd.read_csv(input_file_path)

# 检查数据的前几行，确保读取正确
print(data.head())

# 计算每月的总物种丰富度
total_species_richness_per_month = data.groupby('Date')['Species_Richness'].transform('sum')

# 计算每个地区的物种丰富度占比
data['Region_Rate'] = data['Species_Richness'] / total_species_richness_per_month

# 保留必要的列：地区、日期、物种丰富度占比
region_rate_data = data[['Region', 'Date', 'Region_Rate']]

# 输出到同路径的 S39_BM_RegionRateMonthly.csv 文件
output_dir = os.path.dirname(input_file_path)  # 获取输入文件的目录
output_file_path = os.path.join(output_dir, 'S39_BM_RegionRateMonthly.csv')  # 生成输出文件路径

# 保存计算结果到 CSV 文件
region_rate_data.to_csv(output_file_path, index=False)

# 输出文件保存路径
print(f"物种丰富度占比已保存到 {output_file_path}")

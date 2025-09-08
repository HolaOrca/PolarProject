import pandas as pd
import os

# 读取 CSV 文件
input_file_path = r'D:\DATA\Polar\BaseBM\S39_BM_pre.csv'
data = pd.read_csv(input_file_path)

# 过滤掉 Count 为 0 的记录，并使用 .copy() 创建新 DataFrame
filtered_data = data[data['Count'] > 0].copy()

# 将 'Date' 转换为日期格式
filtered_data['Date'] = pd.to_datetime('2023-' + filtered_data['Date'], format='%Y-%d-%b')

# 分组计算每个Region每月的物种丰富度
species_richness_by_region_month = filtered_data.groupby(['Region', filtered_data['Date'].dt.to_period('M')])['Species'].nunique().reset_index()
species_richness_by_region_month.columns = ['Region', 'Date', 'Species_Richness']

# 定义一个函数来拆分和排序Region名称，保持字母大小写
def region_sort_key(region):
    number = ''
    letter = ''
    for char in region:
        if char.isdigit():
            number += char
        else:
            letter += char
    return (int(number) if number else 0, letter)

# 排序，先按Region然后按Date，考虑字母大小写
# 先创建一个新的列用于排序
species_richness_by_region_month['Sort_Region'] = species_richness_by_region_month['Region'].apply(region_sort_key)

# 排序
species_richness_by_region_month = species_richness_by_region_month.sort_values(
    by=['Sort_Region', 'Date']
)

# 移除临时排序列
species_richness_by_region_month = species_richness_by_region_month.drop(columns=['Sort_Region'])

# 获取输入文件的目录
output_dir = os.path.dirname(input_file_path)

# 生成输出文件路径
output_file_path = os.path.join(output_dir, 'S39_BM_RegionMonthly.csv')

# 输出结果到CSV
species_richness_by_region_month.to_csv(output_file_path, index=False)

# 显示结果
print(f"结果已保存至 {output_file_path}")

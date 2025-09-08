import pandas as pd

# 读取 CSV 文件
data = pd.read_csv(r'D:\DATA\Polar\BaseBM\S39_BM_pre.csv')

# 过滤掉 Count 为 0 的记录
filtered_data = data[data['Count'] > 0]

# 计算每个Region的全年物种丰富度
species_richness_by_region = filtered_data.groupby('Region')['Species'].nunique().reset_index()

# 重命名列以反映我们计算的是丰富度
species_richness_by_region.columns = ['Region', 'Species_Richness']

#地区的命名使用的格式是文本，但实际上，从人类阅读的理解上是数字加字母。请将结果展示以地区排序，使用的规则是先以数字排序，数字相同的用内部的字母排序
# 定义一个函数来拆分和排序Region名称
def region_sort_key(region):
    number = ''
    letter = ''
    for char in region:
        if char.isdigit():
            number += char
        else:
            letter = char
    return (int(number) if number else 0, letter)

# 按自定义规则排序
species_richness_by_region = species_richness_by_region.sort_values(by='Region', key=lambda x: x.map(region_sort_key))

# 显示结果
print(species_richness_by_region)

#可视化
import matplotlib.pyplot as plt
plt.figure(figsize=(12, 6))  # 设置图形大小

# 绘制条形图
plt.bar(species_richness_by_region['Region'], species_richness_by_region['Species_Richness'], color='skyblue')

# 设置标题和标签
plt.title('Species Richness by Region')
plt.xlabel('Region')
plt.ylabel('Species Richness')

# 调整每个条形上的数值标签
for i, v in enumerate(species_richness_by_region['Species_Richness']):
    plt.text(i, v, str(v), ha='center', va='bottom')

# 旋转x轴标签以便于阅读
plt.xticks(rotation=45)

plt.tight_layout()  # 调整布局以防止标签被切割
plt.show()


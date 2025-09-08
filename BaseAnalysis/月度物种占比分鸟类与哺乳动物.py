import pandas as pd

# 读取数据
data = pd.read_csv(r"D:\DATA\Polar\BaseBM\S39_BM_pre.csv")

# 处理日期格式：假设日期格式为 DD-MMM，并添加一个默认年份（如2023）
data['Date'] = data['Date'].apply(lambda x: f"{x}-2023")

# 将Date列转换为日期格式
data['Date'] = pd.to_datetime(data['Date'], format='%d-%b-%Y', errors='coerce')

# 如果Date列中有NaT，表示有无法解析的日期，删除这些行
data = data.dropna(subset=['Date'])

# 确保Species列和Class列没有空值
data = data.dropna(subset=['Species', 'Class'])

# 定义输出文件路径
output_mammals = r"D:\DATA\Polar\BaseBM\S39_BM_Mammals_ratio_Monthly.csv"
output_avians = r"D:\DATA\Polar\BaseBM\S39_BM_Avians_ratio_Monthly.csv"

# 按照类别（Class）进行分组：Mammals 和 Avians
for category, output_file in [('Mammals', output_mammals), ('Avians', output_avians)]:
    # 筛选指定类别的数据
    category_data = data[data['Class'] == category]

    # 按月份和物种分组，并计算每个月每个物种的总数
    monthly_species_count = category_data.groupby(['Date', 'Species'])['Count'].sum().reset_index()

    if monthly_species_count.empty:
        print(f"No valid data found for {category}.")
    else:
        # 计算每个月所有物种的总数
        monthly_total_count = monthly_species_count.groupby('Date')['Count'].transform('sum')

        # 计算每个月各物种的数量占比
        monthly_species_count['percentage'] = monthly_species_count['Count'] / monthly_total_count * 100

        # 输出结果到指定文件
        monthly_species_count.to_csv(output_file, index=False)
        print(f"Result for {category} saved to {output_file}")

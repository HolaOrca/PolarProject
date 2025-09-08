import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
from matplotlib import font_manager

# 读取已保存的CSV文件
data = pd.read_csv(r"D:\DATA\Polar\BaseBM\S39_BM_Mammals_ratio_Monthly.csv")   #修改输入文件即可

# 将Date列转换为日期格式
data['Date'] = pd.to_datetime(data['Date'], errors='coerce')

# 确保没有空值
data = data.dropna(subset=['Date', 'Species', 'percentage'])

# 提取月份（例如：2024-01-01 转换为 2024-01）
data['Month'] = data['Date'].dt.to_period('M')

# 按照月份分组，每个月的物种占比数据
monthly_groups = data.groupby('Month')

# 创建保存饼图的路径
output_dir = r"D:\DATA\Polar\BaseBM\output\Monthly_Pie_Charts\\"

# 获取颜色调色板
colors = cm.get_cmap('tab20', len(data['Species'].unique()))

# 为每个月份绘制饼图
for month, group in monthly_groups:
    # 获取物种和占比
    species = group['Species']
    percentages = group['percentage']

    # 自定义函数：只有占比大于 10% 的物种才显示标签
    def autopct_func(pct, allpercentages=percentages):
        if pct > 10:
            return f'{pct:.1f}%'
        else:
            return ''  # 不显示小于 10% 的物种占比标签

    # 为每个物种分配颜色
    species_colors = [colors(i) for i in range(len(species))]

    # 绘制饼图
    plt.figure(figsize=(8, 8))
    wedges, texts, autotexts = plt.pie(percentages, autopct=lambda pct: autopct_func(pct), startangle=90,
                                       colors=species_colors)

    # 设置图例字体为斜体
    font_properties = font_manager.FontProperties(style='italic')

    # 设置物种名称为图例，使用斜体字体
    plt.legend(wedges, species, title="Species", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), prop=font_properties)

    # 设置图表标题
    plt.title(f"Species Distribution for {month}")

    # 调整布局，防止图例遮挡
    plt.tight_layout()

    # 保存饼图到文件，提升分辨率到300dpi
    pie_chart_filename = f"{output_dir}Species_Distribution_{month}.png"
    plt.savefig(pie_chart_filename, dpi=300)  # 设置分辨率为300dpi
    plt.close()  # 关闭当前图形

    print(f"Saved pie chart for {month} to {pie_chart_filename}")

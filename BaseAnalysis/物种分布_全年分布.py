import pandas as pd

# 加载CSV文件
data_path = r'D:\DATA\Polar\BaseBM\S39_BM_pre.csv'
df = pd.read_csv(data_path)

# 检查数据的前几行，了解结构
print(df.head())

# 检查是否有缺失值
print(df.isnull().sum())

# 检查数据类型
print(df.dtypes)

# 检查是否有重复的行
print(df.duplicated().sum())

# 物种在不同区域的数量分布
species_region_count = df.groupby(['Region', 'Species'])['Count'].sum().reset_index()

# 查看分组后的结果
print(species_region_count.head())

# 假设年份是相同的，给日期添加年份信息
df['Date'] = pd.to_datetime(df['Date'] + '-2023', format='%d-%b-%Y')

# 按年月分组并汇总
monthly_species_count = df.groupby([df['Date'].dt.strftime('%Y-%m'), 'Species'])['Count'].sum().reset_index()

# 查看结果
print(monthly_species_count.head())

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# 2. Shapefile加载
shapefile_path = r'D:\DATA\Polar\polar_basemap_shp\SCAR\SCAR_Antarcticacoastline_high_res_polygon_v7_6\KingGeorgeIsland\KingGeorgeIS.shp'
base_map = gpd.read_file(shapefile_path)

# 确保底图坐标系为WGS 84 (EPSG:4326)
base_map = base_map.to_crs(epsg=4326)

# 检查底图加载情况
print("Base map loaded successfully.")

# 3. 数据汇总：经纬度和物种
species_geo_count = df.groupby(['X', 'Y', 'Species'])['Count'].sum().reset_index()

# 检查汇总后的数据
print("Grouped data preview:")
print(species_geo_count.head())

# 检查经纬度范围
print(f"Longitude range: {species_geo_count['X'].min()} to {species_geo_count['X'].max()}")
print(f"Latitude range: {species_geo_count['Y'].min()} to {species_geo_count['Y'].max()}")

# 4. 绘图
fig, ax = plt.subplots(figsize=(12, 10))

# 绘制Shapefile底图
base_map.plot(ax=ax, color='lightgray', edgecolor='black')

# 绘制物种分布（散点图）
for species in species_geo_count['Species'].unique():
    species_data = species_geo_count[species_geo_count['Species'] == species]
    ax.scatter(
        species_data['X'],
        species_data['Y'],
        s=species_data['Count'] * 0.8,  # 再次缩小点的大小
        label=species,
        alpha=0.6  # 调整透明度
    )

# 手动设置更精确的地图范围
min_long = species_geo_count['X'].min() - 0.03  # 更小的边界范围
max_long = species_geo_count['X'].max() + 0.03
min_lat = species_geo_count['Y'].min() - 0.03
max_lat = species_geo_count['Y'].max() + 0.03

ax.set_xlim(min_long, max_long)
ax.set_ylim(min_lat, max_lat)

# 添加标题和图例
ax.set_title('Species Distribution on Fildes Peninsula', fontsize=14)  # 更新标题
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.legend(title='Species', bbox_to_anchor=(1.05, 1), loc='upper left')

plt.tight_layout()
plt.show()



# 导入必要的库
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# 1. 加载数据
excel_path = r'D:\\DATA\\Polar\\BaseBM\\S39_BM_RegionMonthly.xlsx'
shapefile_path = r'D:\\DATA\\Polar\\polar_basemap_shp\\SCAR\\SCAR_Antarcticacoastline_high_res_polygon_v7_6\\KingGeorgeIsland\\KingGeorgeIS.shp'

# 加载 Excel 数据
data = pd.read_excel(excel_path)
data['Date'] = pd.to_datetime(data['Date'])  # 确保日期格式正确

# 转换为 GeoDataFrame
data_gdf = gpd.GeoDataFrame(
    data,
    geometry=gpd.points_from_xy(data['X'], data['Y']),
    crs="EPSG:4326"  # 假设 WGS84 坐标系
)

# 加载 SHP 文件
shapefile = gpd.read_file(shapefile_path)

# 确保底图与数据使用相同坐标系
shapefile = shapefile.to_crs(data_gdf.crs)

# 2. 筛选一个时间点的数据（例如最新日期）
latest_date = data_gdf['Date'].max()
latest_data = data_gdf[data_gdf['Date'] == latest_date]

# 3. 绘制地图
fig, ax = plt.subplots(figsize=(12, 10))

# 计算数据范围
min_lon, max_lon = latest_data['X'].min(), latest_data['X'].max()
min_lat, max_lat = latest_data['Y'].min(), latest_data['Y'].max()

# 缩放视角到数据范围
buffer = 0.05  # 添加缓冲区以避免点太靠近边界
ax.set_xlim(min_lon - buffer, max_lon + buffer)
ax.set_ylim(min_lat - buffer, max_lat + buffer)

# 绘制底图
shapefile.plot(ax=ax, color='lightgrey', edgecolor='black', alpha=0.8)

# 绘制点数据
latest_data.plot(
    ax=ax,
    column='Species_Richness',  # 根据物种丰富度设置颜色
    cmap='coolwarm',  # 配色方案
    markersize=latest_data['Species_Richness'] * 5,  # 根据丰富度调整点大小
    legend=True
)

# 添加图例和标题
ax.set_title(f"Species Richness on {latest_date.strftime('%Y-%m-%d')}", fontsize=16)
ax.set_xlabel("Longitude", fontsize=12)
ax.set_ylabel("Latitude", fontsize=12)

# 显示图像
plt.show()

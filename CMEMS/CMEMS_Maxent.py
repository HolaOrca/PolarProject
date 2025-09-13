#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正版罗斯海适生区分析与可视化系统
Corrected Ross Sea Habitat Suitability Analysis and Visualization System

直接基于观测数据进行适宜性分析，避免不合理的插值假设
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import os
import warnings

warnings.filterwarnings('ignore')

# 尝试导入scipy用于插值
try:
    from scipy.interpolate import griddata
    from scipy.ndimage import gaussian_filter
    from scipy.spatial.distance import cdist

    SCIPY_AVAILABLE = True
    print("使用SciPy进行高质量插值")
except ImportError:
    SCIPY_AVAILABLE = False
    print("SciPy不可用，使用基础方法")


class CorrectedHabitatAnalyzer:
    """
    修正版栖息地适宜性分析器
    基于实际观测数据，使用合理的建模方法
    """

    def __init__(self, csv_file_path):
        self.csv_file = csv_file_path
        self.data = None
        self.species_data = {}
        self.habitat_suitability = {}

        # 创建海洋学配色方案
        self.ocean_cmap = self._create_ocean_colormap()

    def _create_ocean_colormap(self):
        """创建海洋学风格配色方案"""
        colors = [
            '#000080',  # 深蓝 (低适宜性)
            '#0040FF',  # 蓝色
            '#0080FF',  # 浅蓝
            '#00FFFF',  # 青色
            '#40FF40',  # 绿色
            '#80FF00',  # 黄绿
            '#FFFF00',  # 黄色
            '#FF8000',  # 橙色
            '#FF4000',  # 红橙
            '#FF0000',  # 红色 (高适宜性)
        ]
        return LinearSegmentedColormap.from_list('ocean_habitat', colors, N=256)

    def load_and_analyze_data(self):
        """
        加载数据并进行预处理
        """
        print("加载和分析观测数据...")

        if not os.path.exists(self.csv_file):
            print(f"错误：文件不存在 {self.csv_file}")
            return False

        try:
            # 读取数据
            self.data = pd.read_csv(self.csv_file)
            print(f"成功加载 {len(self.data)} 条记录")

            # 数据清理
            self.data = self.data.dropna(subset=['LAT', 'LONG', 'Species'])
            print(f"清理后保留 {len(self.data)} 条有效记录")

            # 按物种分组分析
            self._analyze_by_species()

            return True

        except Exception as e:
            print(f"数据加载失败: {e}")
            return False

    def _analyze_by_species(self):
        """
        按物种分析数据
        """
        print("分析各物种分布特征...")

        species_counts = self.data['Species'].value_counts()
        print(f"发现 {len(species_counts)} 个物种")

        # 只分析观测数量足够的物种
        min_observations = 15
        valid_species = species_counts[species_counts >= min_observations].index.tolist()

        print(f"观测数量≥{min_observations}的物种有 {len(valid_species)} 个:")
        for species in valid_species[:10]:  # 显示前10个
            count = species_counts[species]
            print(f"  {species}: {count} 次观测")

        # 为每个有效物种准备数据
        for species in valid_species:
            species_data = self.data[self.data['Species'] == species].copy()

            # 计算环境变量统计
            env_stats = self._calculate_environmental_stats(species_data)

            self.species_data[species] = {
                'data': species_data,
                'count': len(species_data),
                'env_stats': env_stats,
                'lat_range': (species_data['LAT'].min(), species_data['LAT'].max()),
                'lon_range': (species_data['LONG'].min(), species_data['LONG'].max())
            }

    def _calculate_environmental_stats(self, species_data):
        """
        计算物种的环境变量统计
        """
        env_vars = ['TempW', 'Salinity', 'Detph', 'pH', 'CHL', 'O2Con']
        env_stats = {}

        for var in env_vars:
            if var in species_data.columns:
                values = species_data[var].dropna()
                if len(values) > 5:
                    env_stats[var] = {
                        'mean': values.mean(),
                        'std': values.std(),
                        'min': values.min(),
                        'max': values.max(),
                        'q25': values.quantile(0.25),
                        'q75': values.quantile(0.75)
                    }

        return env_stats

    def generate_species_suitability_maps(self, resolution=0.08):
        """
        基于观测数据生成物种适宜性地图
        使用核密度估计和环境适宜性建模
        """
        print(f"生成物种适宜性地图，分辨率: {resolution}度...")

        for species_name, species_info in self.species_data.items():
            print(f"处理物种: {species_name}")

            species_data = species_info['data']

            # 确定该物种的地理范围
            lat_min, lat_max = species_info['lat_range']
            lon_min, lon_max = species_info['lon_range']

            # 扩展边界
            lat_margin = (lat_max - lat_min) * 0.15
            lon_margin = (lon_max - lon_min) * 0.15

            lat_min -= lat_margin
            lat_max += lat_margin
            lon_min -= lon_margin
            lon_max += lon_margin

            # 创建预测网格
            lat_grid = np.arange(lat_min, lat_max, resolution)
            lon_grid = np.arange(lon_min, lon_max, resolution)
            lon_mesh, lat_mesh = np.meshgrid(lon_grid, lat_grid)

            # 计算适宜性
            suitability = self._calculate_habitat_suitability(
                species_data, species_info['env_stats'],
                lat_mesh, lon_mesh
            )

            # 保存结果
            self.habitat_suitability[species_name] = {
                'lat_grid': lat_grid,
                'lon_grid': lon_grid,
                'suitability': suitability,
                'lat_mesh': lat_mesh,
                'lon_mesh': lon_mesh,
                'observations': species_data[['LAT', 'LONG', 'Counts']].copy()
            }

    def _calculate_habitat_suitability(self, species_data, env_stats, lat_mesh, lon_mesh):
        """
        计算栖息地适宜性
        结合地理距离和环境适宜性
        """
        # 提取观测点坐标
        obs_lats = species_data['LAT'].values
        obs_lons = species_data['LONG'].values
        obs_counts = species_data['Counts'].fillna(1).values

        # 1. 计算基于观测密度的适宜性
        suitability_density = self._calculate_density_suitability(
            obs_lats, obs_lons, obs_counts, lat_mesh, lon_mesh
        )

        # 2. 计算基于环境条件的适宜性
        suitability_env = self._calculate_environmental_suitability(
            species_data, env_stats, lat_mesh, lon_mesh
        )

        # 3. 综合两种适宜性
        # 使用几何平均数结合密度和环境适宜性
        combined_suitability = np.sqrt(suitability_density * suitability_env)

        # 标准化到0-1范围
        if combined_suitability.max() > 0:
            combined_suitability = combined_suitability / combined_suitability.max()

        return combined_suitability

    def _calculate_density_suitability(self, obs_lats, obs_lons, obs_counts, lat_mesh, lon_mesh):
        """
        基于观测点密度计算适宜性
        """
        if SCIPY_AVAILABLE:
            # 使用高斯核密度估计
            points = np.column_stack([obs_lons, obs_lats])
            grid_points = np.column_stack([lon_mesh.ravel(), lat_mesh.ravel()])

            # 计算距离权重
            distances = cdist(grid_points, points)

            # 使用自适应带宽
            bandwidth = np.std(distances) * 0.3
            weights = np.exp(-0.5 * (distances / bandwidth) ** 2)

            # 考虑观测计数
            weighted_density = np.sum(weights * obs_counts, axis=1)
            density_grid = weighted_density.reshape(lat_mesh.shape)

        else:
            # 简化的距离权重方法
            density_grid = np.zeros_like(lat_mesh)

            for i in range(lat_mesh.shape[0]):
                for j in range(lat_mesh.shape[1]):
                    lat, lon = lat_mesh[i, j], lon_mesh[i, j]

                    # 计算到所有观测点的距离
                    distances = np.sqrt((obs_lats - lat) ** 2 + (obs_lons - lon) ** 2)

                    # 使用反距离权重
                    weights = 1.0 / (distances + 0.01)
                    density_grid[i, j] = np.sum(weights * obs_counts)

        # 应用平滑
        if SCIPY_AVAILABLE:
            density_grid = gaussian_filter(density_grid, sigma=1.0)

        return density_grid

    def _calculate_environmental_suitability(self, species_data, env_stats, lat_mesh, lon_mesh):
        """
        基于环境条件计算适宜性
        """
        # 如果没有足够的环境数据，返回均匀分布
        if len(env_stats) < 2:
            return np.ones_like(lat_mesh) * 0.5

        # 简化方法：基于地理位置的环境梯度估算
        env_suitability = np.ones_like(lat_mesh)

        # 基于纬度的温度梯度 (南极地区)
        if 'TempW' in env_stats:
            temp_optimal = env_stats['TempW']['mean']
            temp_tolerance = env_stats['TempW']['std']

            # 简单的纬度-温度关系 (越往南越冷)
            estimated_temp = -2.0 + (lat_mesh + 80) * 0.5  # 简化的温度模型
            temp_suitability = np.exp(-0.5 * ((estimated_temp - temp_optimal) / (temp_tolerance + 0.1)) ** 2)
            env_suitability *= temp_suitability

        # 基于深度的适宜性 (假设近岸较浅)
        if 'Detph' in env_stats:
            depth_optimal = env_stats['Detph']['mean']
            depth_tolerance = env_stats['Detph']['std']

            # 简化的深度模型 (距离海岸越远越深)
            estimated_depth = 200 + np.abs(lat_mesh + 77) * 100  # 简化的深度模型
            depth_suitability = np.exp(-0.5 * ((estimated_depth - depth_optimal) / (depth_tolerance + 50)) ** 2)
            env_suitability *= depth_suitability

        return env_suitability

    def create_oceanographic_maps(self, species_list=None):
        """
        创建海洋学风格的适宜性地图
        """
        if species_list is None:
            species_list = list(self.habitat_suitability.keys())[:6]

        print(f"创建海洋学风格地图，共 {len(species_list)} 个物种")

        for species_name in species_list:
            if species_name not in self.habitat_suitability:
                continue

            self._create_single_species_map(species_name)

        # 创建多物种对比图
        if len(species_list) > 1:
            self._create_species_comparison_map(species_list[:4])

    def _create_single_species_map(self, species_name):
        """
        创建单个物种的海洋学风格地图
        """
        print(f"生成 {species_name} 的适宜性地图...")

        habitat_data = self.habitat_suitability[species_name]

        # 创建图形
        fig, ax = plt.subplots(figsize=(14, 10))

        # 绘制等值线填充
        levels = np.linspace(0, 1, 21)
        contourf = ax.contourf(
            habitat_data['lon_mesh'], habitat_data['lat_mesh'],
            habitat_data['suitability'],
            levels=levels, cmap=self.ocean_cmap, extend='max'
        )

        # 添加关键等值线
        key_levels = [0.2, 0.4, 0.6, 0.8]
        contours = ax.contour(
            habitat_data['lon_mesh'], habitat_data['lat_mesh'],
            habitat_data['suitability'],
            levels=key_levels, colors='black', linewidths=0.8, alpha=0.7
        )
        ax.clabel(contours, inline=True, fontsize=9, fmt='%.1f')

        # 添加观测点
        obs_data = habitat_data['observations']
        scatter = ax.scatter(
            obs_data['LONG'], obs_data['LAT'],
            c='white', s=30, marker='o',
            edgecolors='black', linewidth=1,
            zorder=10, alpha=0.8
        )

        # 设置坐标轴
        ax.set_xlabel('经度 (°E)', fontsize=12, fontweight='bold')
        ax.set_ylabel('纬度 (°N)', fontsize=12, fontweight='bold')
        ax.set_title(f'{species_name}\n栖息地适宜性分布', fontsize=14, fontweight='bold')

        # 添加网格
        ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)

        # 色标
        cbar = plt.colorbar(contourf, ax=ax, shrink=0.8, aspect=25, pad=0.02)
        cbar.set_label('适宜性指数', fontsize=11, fontweight='bold')

        # 设置色标刻度
        cbar.set_ticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
        cbar.set_ticklabels(['0.0\n不适宜', '0.2', '0.4', '0.6', '0.8', '1.0\n高适宜'])

        # 添加统计信息
        stats_text = self._get_map_statistics(species_name, habitat_data)
        ax.text(0.02, 0.02, stats_text, transform=ax.transAxes,
                verticalalignment='bottom', fontsize=9,
                bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.9))

        plt.tight_layout()

        # 保存图片
        filename = f'habitat_suitability_{species_name.replace(" ", "_")}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"已保存: {filename}")

        return fig

    def _get_map_statistics(self, species_name, habitat_data):
        """
        生成地图统计信息
        """
        suitability = habitat_data['suitability']
        obs_count = len(habitat_data['observations'])

        # 计算适宜性统计
        high_suit = np.sum(suitability >= 0.7)
        mod_suit = np.sum((suitability >= 0.4) & (suitability < 0.7))
        total_pixels = suitability.size
        mean_suit = np.mean(suitability)
        max_suit = np.max(suitability)

        stats_lines = [
            f"观测点: {obs_count}",
            f"平均适宜性: {mean_suit:.3f}",
            f"最大适宜性: {max_suit:.3f}",
            f"高适宜区: {high_suit / total_pixels * 100:.1f}%",
            f"中适宜区: {mod_suit / total_pixels * 100:.1f}%"
        ]

        return '\n'.join(stats_lines)

    def _create_species_comparison_map(self, species_list):
        """
        创建物种对比地图
        """
        print(f"创建 {len(species_list)} 个物种对比图...")

        ncols = 2
        nrows = (len(species_list) + ncols - 1) // ncols

        fig, axes = plt.subplots(nrows, ncols, figsize=(16, 8 * nrows))
        if nrows == 1:
            axes = axes.reshape(1, -1)

        for i, species_name in enumerate(species_list):
            row = i // ncols
            col = i % ncols
            ax = axes[row, col]

            if species_name not in self.habitat_suitability:
                ax.text(0.5, 0.5, f'{species_name}\n数据不可用',
                        ha='center', va='center', transform=ax.transAxes)
                continue

            habitat_data = self.habitat_suitability[species_name]

            # 简化的等值线图
            contourf = ax.contourf(
                habitat_data['lon_mesh'], habitat_data['lat_mesh'],
                habitat_data['suitability'],
                levels=15, cmap=self.ocean_cmap, alpha=0.9
            )

            # 观测点
            obs_data = habitat_data['observations']
            ax.scatter(obs_data['LONG'], obs_data['LAT'],
                       c='white', s=15, marker='o',
                       edgecolors='black', linewidth=0.5, alpha=0.8)

            ax.set_title(species_name, fontsize=12, fontweight='bold')
            ax.set_xlabel('经度 (°E)', fontsize=10)
            ax.set_ylabel('纬度 (°N)', fontsize=10)
            ax.grid(True, alpha=0.3)

        # 隐藏多余子图
        for i in range(len(species_list), nrows * ncols):
            row = i // ncols
            col = i % ncols
            axes[row, col].set_visible(False)

        # 整体色标
        cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])
        cbar = fig.colorbar(contourf, cax=cbar_ax)
        cbar.set_label('适宜性指数', fontsize=12)

        fig.suptitle('物种栖息地适宜性对比', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.subplots_adjust(right=0.9)

        filename = 'species_habitat_comparison.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"已保存对比图: {filename}")

        return fig

    def export_habitat_data(self):
        """
        导出适宜性数据为CSV格式
        """
        print("导出适宜性数据...")

        for species_name, habitat_data in self.habitat_suitability.items():
            # 创建DataFrame
            lat_mesh = habitat_data['lat_mesh']
            lon_mesh = habitat_data['lon_mesh']
            suitability = habitat_data['suitability']

            # 展平数据
            data_records = []
            for i in range(lat_mesh.shape[0]):
                for j in range(lat_mesh.shape[1]):
                    data_records.append({
                        'Latitude': lat_mesh[i, j],
                        'Longitude': lon_mesh[i, j],
                        'Suitability': suitability[i, j]
                    })

            df = pd.DataFrame(data_records)

            # 保存CSV
            filename = f'corrected_habitat_{species_name.replace(" ", "_")}.csv'
            df.to_csv(filename, index=False)
            print(f"已保存: {filename}")

        # 导出观测点数据
        obs_filename = 'ross_sea_observations.csv'
        self.data[['Species', 'LAT', 'LONG', 'Counts']].to_csv(obs_filename, index=False)
        print(f"已保存观测点数据: {obs_filename}")


def main():
    """
    主函数
    """
    print("修正版罗斯海适生区分析与可视化系统")
    print("=" * 50)

    # 数据文件路径
    data_paths = [
        r'E:/Work/PRIC/Science/Paper/2025/JTRES/JTRES.csv',
        r'C:/pythoncode/CMEMS/JTRES.csv',
        './JTRES.csv'
    ]

    # 找到存在的数据文件
    csv_file = None
    for path in data_paths:
        if os.path.exists(path):
            csv_file = path
            break

    if csv_file is None:
        print("错误：找不到数据文件 JTRES.csv")
        print("请检查以下路径:")
        for path in data_paths:
            print(f"  {path}")
        return None

    print(f"使用数据文件: {csv_file}")

    # 创建分析器
    analyzer = CorrectedHabitatAnalyzer(csv_file)

    # 加载和分析数据
    if not analyzer.load_and_analyze_data():
        return None

    # 生成适宜性地图
    analyzer.generate_species_suitability_maps(resolution=0.06)

    # 创建可视化
    analyzer.create_oceanographic_maps()

    # 导出数据
    analyzer.export_habitat_data()

    print("\n分析完成！")
    print("生成的文件:")
    print("  - habitat_suitability_*.png (各物种适宜性地图)")
    print("  - species_habitat_comparison.png (物种对比图)")
    print("  - corrected_habitat_*.csv (修正后的适宜性数据)")
    print("  - ross_sea_observations.csv (观测点数据)")

    return analyzer


if __name__ == "__main__":
    analyzer = main()
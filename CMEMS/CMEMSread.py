#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CMEMS南极海域环境参数完整分析系统
包含11个环境参数的统一颜色条月度对比分析
"""

# ============================================================================
# 导入所有必要的库
# ============================================================================
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

# 设置matplotlib参数
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# ============================================================================
# 数据分析函数
# ============================================================================

def analyze_all_variables(ds):
    """分析数据集中的所有变量"""
    print("完整数据集分析")
    print("=" * 80)

    # 所有变量的详细信息
    all_variables = {
        'bottomT': ('底层温度', '°C', 'temperature', '2D'),
        'mlotst': ('混合层深度', 'm', 'depth', '2D'),
        'siconc': ('海冰浓度', '0-1', 'fraction', '2D'),
        'sithick': ('海冰厚度', 'm', 'thickness', '2D'),
        'so': ('盐度', 'PSU', 'salinity', '3D'),
        'thetao': ('海水位温', '°C', 'temperature', '3D'),
        'uo': ('东向流速', 'm/s', 'velocity', '3D'),
        'usi': ('海冰东向速度', 'm/s', 'ice_velocity', '2D'),
        'vo': ('北向流速', 'm/s', 'velocity', '3D'),
        'vsi': ('海冰北向速度', 'm/s', 'ice_velocity', '2D'),
        'zos': ('海表面高度', 'm', 'sea_level', '2D')
    }

    print("数据变量完整列表:")
    print(f"{'变量名':>10} | {'中文名称':>12} | {'单位':>8} | {'类型':>6} | {'维度':>4} | {'数据范围'}")
    print("-" * 80)

    for var_name, (chinese_name, unit, var_type, dim_type) in all_variables.items():
        if var_name in ds.data_vars:
            var_data = ds[var_name]
            dims = f"({', '.join(var_data.dims)})"

            # 计算数据范围
            valid_data = var_data.where(~np.isnan(var_data))
            if valid_data.size > 0:
                min_val = float(valid_data.min())
                max_val = float(valid_data.max())
                mean_val = float(valid_data.mean())
                data_range = f"{min_val:.3f} ~ {max_val:.3f} (均值: {mean_val:.3f})"
            else:
                data_range = "无有效数据"

            print(f"{var_name:>10} | {chinese_name:>12} | {unit:>8} | {var_type:>6} | {dim_type:>4} | {data_range}")

    # 时间和空间信息
    print(f"\n时间维度: {len(ds.time)} 个月 ({str(ds.time.values[0])[:7]} 至 {str(ds.time.values[-1])[:7]})")
    print(f"深度维度: {len(ds.depth)} 层 ({ds.depth.min().values:.1f}m 至 {ds.depth.max().values:.1f}m)")
    print(
        f"空间范围: {ds.latitude.min().values:.2f}° ~ {ds.latitude.max().values:.2f}°N, {ds.longitude.min().values:.2f}° ~ {ds.longitude.max().values:.2f}°E")

    return all_variables


def create_summary_table(ds):
    """创建所有变量的数据摘要表"""

    ds_subset = ds.sel(longitude=slice(160, 175), latitude=slice(-85, -60))

    print("\n" + "=" * 100)
    print("南极海域环境参数数据摘要表")
    print("=" * 100)

    print(
        f"{'变量名':<12} {'中文名称':<15} {'单位':<8} {'最小值':<12} {'最大值':<12} {'均值':<12} {'标准差':<12} {'月变化幅度'}")
    print("-" * 100)

    all_variables = {
        'thetao': ('海水位温(表层)', '°C', 0),
        'so': ('盐度(表层)', 'PSU', 0),
        'uo': ('东向流速(表层)', 'm/s', 0),
        'vo': ('北向流速(表层)', 'm/s', 0),
        'bottomT': ('底层温度', '°C', None),
        'mlotst': ('混合层深度', 'm', None),
        'siconc': ('海冰浓度', '0-1', None),
        'sithick': ('海冰厚度', 'm', None),
        'usi': ('海冰东向速度', 'm/s', None),
        'vsi': ('海冰北向速度', 'm/s', None),
        'zos': ('海表面高度', 'm', None)
    }

    for var, (chinese_name, unit, depth_idx) in all_variables.items():
        if var in ds_subset.data_vars:
            try:
                if depth_idx is not None:
                    data = ds_subset[var].isel(depth=depth_idx)
                else:
                    data = ds_subset[var]

                # 计算统计量
                valid_data = data.where(~np.isnan(data))
                if valid_data.size > 0:
                    min_val = float(valid_data.min())
                    max_val = float(valid_data.max())
                    mean_val = float(valid_data.mean())
                    std_val = float(valid_data.std())

                    # 计算月变化幅度
                    monthly_means = []
                    for i in range(len(ds.time)):
                        month_mean = data.isel(time=i).mean()
                        if not np.isnan(month_mean):
                            monthly_means.append(float(month_mean))

                    if monthly_means:
                        month_range = max(monthly_means) - min(monthly_means)
                    else:
                        month_range = 0

                    print(
                        f"{var:<12} {chinese_name:<15} {unit:<8} {min_val:<12.4f} {max_val:<12.4f} {mean_val:<12.4f} {std_val:<12.4f} {month_range:<12.4f}")

            except Exception as e:
                print(
                    f"{var:<12} {chinese_name:<15} {unit:<8} {'错误':<12} {'错误':<12} {'错误':<12} {'错误':<12} {'错误'}")


# ============================================================================
# 可视化函数 - 统一颜色条版本
# ============================================================================

def plot_monthly_comparison_unified(ds, var='thetao', depth_idx=0):
    """绘制月度对比图（统一颜色条版本）"""

    # 变量配置
    var_configs = {
        'thetao': ('海水位温', '°C', 'RdYlBu_r'),
        'so': ('盐度', 'PSU', 'viridis'),
        'uo': ('东向流速', 'm/s', 'RdBu_r'),
        'vo': ('北向流速', 'm/s', 'RdBu_r'),
        'bottomT': ('底层温度', '°C', 'coolwarm'),
        'mlotst': ('混合层深度', 'm', 'plasma'),
        'siconc': ('海冰浓度', '0-1', 'Blues'),
        'sithick': ('海冰厚度', 'm', 'viridis'),
        'usi': ('海冰东向速度', 'm/s', 'RdBu_r'),
        'vsi': ('海冰北向速度', 'm/s', 'RdBu_r'),
        'zos': ('海表面高度', 'm', 'RdBu_r')
    }

    if var not in ds.data_vars:
        print(f"变量 {var} 不存在于数据集中")
        return

    title, unit, cmap = var_configs.get(var, (var, '', 'viridis'))

    # 获取数据并计算统一的颜色范围
    if var in ['thetao', 'so', 'uo', 'vo'] and depth_idx is not None:
        data_all = ds[var].isel(depth=depth_idx).sel(longitude=slice(160, 175), latitude=slice(-85, -60))
        depth_info = f' (深度: {ds.depth.values[depth_idx]:.1f}m)'
    else:
        data_all = ds[var].sel(longitude=slice(160, 175), latitude=slice(-85, -60))
        depth_info = ''

    # 计算统一的颜色范围
    vmin = float(data_all.min())
    vmax = float(data_all.max())
    print(f"  {var}: 数据范围 {vmin:.4f} ~ {vmax:.4f}")

    # 绘图设置
    n_months = len(ds.time)
    projection = ccrs.SouthPolarStereo(central_longitude=167.5)
    fig = plt.figure(figsize=(22, 8))

    # 绘制每个月的数据
    ims = []
    for i in range(n_months):
        ax = fig.add_subplot(1, n_months, i + 1, projection=projection)

        # 获取当月数据
        if var in ['thetao', 'so', 'uo', 'vo'] and depth_idx is not None:
            data = ds[var].isel(time=i, depth=depth_idx)
        else:
            data = ds[var].isel(time=i)

        data_subset = data.sel(longitude=slice(160, 175), latitude=slice(-85, -60))

        try:
            # 使用统一的颜色范围
            im = data_subset.plot(
                ax=ax, cmap=cmap, transform=ccrs.PlateCarree(),
                add_colorbar=False, vmin=vmin, vmax=vmax
            )
            ims.append(im)

            # 添加地理要素
            ax.add_feature(cfeature.LAND, color='lightgray', alpha=0.8)
            ax.add_feature(cfeature.COASTLINE, linewidth=1.0)
            ax.set_extent([160, 175, -85, -60], crs=ccrs.PlateCarree())

            # 月份标题
            month_str = str(ds.time.values[i])[:7]
            ax.set_title(f'{month_str}', fontsize=12)

        except Exception as e:
            ax.text(0.5, 0.5, f'绘制错误', ha='center', va='center', transform=ax.transAxes)

    # 添加统一的颜色条
    if ims:
        cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])
        cbar = fig.colorbar(ims[0], cax=cbar_ax)
        cbar.set_label(f'{title} ({unit})', fontsize=12, rotation=270, labelpad=20)

    # 标题
    plt.suptitle(f'{title} ({unit}){depth_info} - 月度对比 [范围: {vmin:.3f}~{vmax:.3f}]', fontsize=16, y=0.95)
    plt.tight_layout()
    plt.subplots_adjust(right=0.9)
    plt.show()


def plot_all_variables_monthly(ds):
    """绘制所有变量的月度对比"""

    # 所有要分析的变量
    all_vars = [
        # 3D变量 (取表层)
        ('thetao', 0, '海水位温(表层)'),
        ('so', 0, '盐度(表层)'),
        ('uo', 0, '东向流速(表层)'),
        ('vo', 0, '北向流速(表层)'),
        # 2D变量
        ('bottomT', None, '底层温度'),
        ('mlotst', None, '混合层深度'),
        ('siconc', None, '海冰浓度'),
        ('sithick', None, '海冰厚度'),
        ('usi', None, '海冰东向速度'),
        ('vsi', None, '海冰北向速度'),
        ('zos', None, '海表面高度')
    ]

    print(f"\n正在生成 {len(all_vars)} 个环境参数的月度对比图...")

    for i, (var, depth_idx, description) in enumerate(all_vars):
        if var in ds.data_vars:
            print(f"  {i + 1:2d}. 绘制 {description}...")
            plot_monthly_comparison_unified(ds, var=var, depth_idx=depth_idx)
        else:
            print(f"  {i + 1:2d}. 跳过 {description} (数据不存在)")


def plot_time_series_analysis(ds, lon=170, lat=-70):
    """绘制时间序列分析"""

    # 选择最近的格点
    point = ds.sel(longitude=lon, latitude=lat, method='nearest')
    actual_lon = float(point.longitude.values)
    actual_lat = float(point.latitude.values)

    fig, axes = plt.subplots(4, 3, figsize=(20, 16))
    fig.suptitle(f'所有环境参数月度时间序列 ({actual_lon:.1f}°E, {actual_lat:.1f}°N)', fontsize=16)

    axes_flat = axes.flatten()

    # 所有变量配置
    all_time_series = [
        ('thetao', '海水位温 (°C)', 0, 'blue'),
        ('so', '表层盐度 (PSU)', 0, 'red'),
        ('uo', '表层东向流速 (m/s)', 0, 'green'),
        ('vo', '表层北向流速 (m/s)', 0, 'orange'),
        ('bottomT', '底层温度 (°C)', None, 'brown'),
        ('mlotst', '混合层深度 (m)', None, 'purple'),
        ('siconc', '海冰浓度', None, 'cyan'),
        ('sithick', '海冰厚度 (m)', None, 'pink'),
        ('usi', '海冰东向速度 (m/s)', None, 'gray'),
        ('vsi', '海冰北向速度 (m/s)', None, 'olive'),
        ('zos', '海表面高度 (m)', None, 'navy')
    ]

    for i, (var, ylabel, depth_idx, color) in enumerate(all_time_series):
        if var in ds.data_vars and i < len(axes_flat):
            ax = axes_flat[i]

            try:
                # 获取数据
                if depth_idx is not None:
                    data = point[var].isel(depth=depth_idx)
                else:
                    data = point[var]

                # 绘制时间序列
                ax.plot(ds.time, data, color=color, linewidth=3, marker='o', markersize=8)
                ax.set_ylabel(ylabel)
                ax.set_title(ylabel)
                ax.grid(True, alpha=0.3)
                ax.tick_params(axis='x', rotation=45)

                # 添加数值标注
                for j, (time_val, val) in enumerate(zip(ds.time.values, data.values)):
                    if not np.isnan(val):
                        ax.annotate(f'{val:.3f}',
                                    (time_val, val),
                                    textcoords="offset points",
                                    xytext=(0, 15),
                                    ha='center',
                                    fontsize=9)

            except Exception as e:
                ax.text(0.5, 0.5, f'数据错误', ha='center', va='center', transform=ax.transAxes)

    # 隐藏多余的子图
    for i in range(len(all_time_series), len(axes_flat)):
        axes_flat[i].set_visible(False)

    plt.tight_layout()
    plt.show()


def plot_vertical_structure_analysis(ds, lon=170, lat=-70):
    """绘制垂直结构分析"""

    # 选择最近的格点
    point = ds.sel(longitude=lon, latitude=lat, method='nearest')
    actual_lon = float(point.longitude.values)
    actual_lat = float(point.latitude.values)

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(f'垂直结构分析 ({actual_lon:.1f}°E, {actual_lat:.1f}°N)', fontsize=14)

    # 3D变量
    depth_vars = ['thetao', 'so', 'uo', 'vo']
    var_names = ['海水位温 (°C)', '盐度 (PSU)', '东向流速 (m/s)', '北向流速 (m/s)']
    colors_list = [['blue', 'red', 'green', 'orange', 'purple'],
                   ['darkblue', 'darkred', 'darkgreen', 'darkorange', 'indigo'],
                   ['lightblue', 'lightcoral', 'lightgreen', 'moccasin', 'plum'],
                   ['navy', 'maroon', 'forestgreen', 'chocolate', 'mediumpurple']]

    axes_flat = axes.flatten()

    for idx, var in enumerate(depth_vars):
        if var in point.data_vars and idx < len(axes_flat):
            ax = axes_flat[idx]
            colors = colors_list[idx]

            try:
                # 绘制所有月份的剖面
                for i in range(len(ds.time)):
                    profile = point[var].isel(time=i)
                    month_str = str(ds.time.values[i])[:7]

                    # 只显示上层1000m的数据
                    depth_mask = ds.depth.values <= 1000
                    if np.any(depth_mask):
                        profile_subset = profile.where(ds.depth <= 1000, drop=True)
                        ax.plot(profile_subset, profile_subset.depth,
                                color=colors[i], linewidth=2, marker='o',
                                markersize=3, label=month_str, alpha=0.8)

                ax.invert_yaxis()
                ax.set_xlabel(var_names[idx])
                ax.set_ylabel('深度 (m)')
                ax.set_title(f'{var_names[idx]} 垂直剖面对比')
                ax.legend(fontsize=10, loc='best')
                ax.grid(True, alpha=0.3)

                # 设置合理的深度范围
                max_depth = min(1000, ds.depth.max().values)
                ax.set_ylim(0, max_depth)

            except Exception as e:
                ax.text(0.5, 0.5, f'绘制错误\n{var}', ha='center', va='center', transform=ax.transAxes)
                ax.set_title(f'{var_names[idx]} (错误)')

    plt.tight_layout()
    plt.show()


def plot_simple_analysis(ds):
    """绘制简化的附加分析"""

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('附加分析', fontsize=16)

    ds_subset = ds.sel(longitude=slice(160, 175), latitude=slice(-85, -60))

    # 1. 海冰覆盖率统计
    ax1 = axes[0, 0]
    if 'siconc' in ds_subset.data_vars:
        try:
            coverage_15 = []
            coverage_50 = []
            for i in range(len(ds.time)):
                ice_data = ds_subset['siconc'].isel(time=i)
                total_pixels = (~np.isnan(ice_data)).sum()
                ice_pixels_15 = (ice_data >= 0.15).sum()
                ice_pixels_50 = (ice_data >= 0.5).sum()

                cov_15 = float(ice_pixels_15 / total_pixels * 100) if total_pixels > 0 else 0
                cov_50 = float(ice_pixels_50 / total_pixels * 100) if total_pixels > 0 else 0

                coverage_15.append(cov_15)
                coverage_50.append(cov_50)

            months = [str(t)[:7] for t in ds.time.values]
            ax1.plot(range(len(ds.time)), coverage_15, 'b-o', linewidth=2, label='海冰边缘(≥15%)')
            ax1.plot(range(len(ds.time)), coverage_50, 'r-s', linewidth=2, label='中等海冰(≥50%)')

            ax1.set_xlabel('月份')
            ax1.set_ylabel('覆盖率 (%)')
            ax1.set_title('海冰覆盖率变化')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            ax1.set_xticks(range(len(ds.time)))
            ax1.set_xticklabels(months, rotation=45)

        except Exception as e:
            ax1.text(0.5, 0.5, '海冰统计错误', ha='center', va='center', transform=ax1.transAxes)

    # 2. 温度-盐度散点图
    ax2 = axes[0, 1]
    if 'thetao' in ds_subset.data_vars and 'so' in ds_subset.data_vars:
        try:
            temp_surface = ds_subset['thetao'].isel(time=0, depth=0)
            salt_surface = ds_subset['so'].isel(time=0, depth=0)

            temp_flat = temp_surface.values.flatten()
            salt_flat = salt_surface.values.flatten()

            valid_mask = ~(np.isnan(temp_flat) | np.isnan(salt_flat))
            temp_valid = temp_flat[valid_mask]
            salt_valid = salt_flat[valid_mask]

            if len(temp_valid) > 0:
                ax2.scatter(salt_valid, temp_valid, alpha=0.6, s=10, c='blue')
                ax2.set_xlabel('盐度 (PSU)')
                ax2.set_ylabel('温度 (°C)')
                ax2.set_title('温度-盐度关系图')
                ax2.grid(True, alpha=0.3)

        except Exception as e:
            ax2.text(0.5, 0.5, 'T-S图错误', ha='center', va='center', transform=ax2.transAxes)

    # 3. 区域平均时间序列
    ax3 = axes[1, 0]
    try:
        variables = ['thetao', 'siconc', 'zos']
        colors = ['red', 'blue', 'green']

        for var, color in zip(variables, colors):
            if var in ds_subset.data_vars:
                if var == 'thetao':
                    data = ds_subset[var].isel(depth=0)
                    label = '海表温度'
                else:
                    data = ds_subset[var]
                    label = var

                regional_mean = data.mean(['latitude', 'longitude'])
                ax3.plot(range(len(ds.time)), regional_mean, color=color,
                         linewidth=2, marker='o', label=label)

        ax3.set_xlabel('月份')
        ax3.set_ylabel('数值')
        ax3.set_title('主要变量区域平均变化')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.set_xticks(range(len(ds.time)))
        ax3.set_xticklabels([str(t)[:7] for t in ds.time.values], rotation=45)

    except Exception as e:
        ax3.text(0.5, 0.5, '时间序列错误', ha='center', va='center', transform=ax3.transAxes)

    # 4. 深度平均温度
    ax4 = axes[1, 1]
    if 'thetao' in ds_subset.data_vars:
        try:
            depth_avg_temp = []
            for i in range(len(ds.time)):
                temp_3d = ds_subset['thetao'].isel(time=i)
                # 简单的深度平均（上层200m）
                upper_temp = temp_3d.where(ds.depth <= 200)
                avg_temp = float(upper_temp.mean())
                depth_avg_temp.append(avg_temp)

            ax4.plot(range(len(ds.time)), depth_avg_temp, 'r-o', linewidth=2, markersize=6)
            ax4.set_xlabel('月份')
            ax4.set_ylabel('温度 (°C)')
            ax4.set_title('上层平均温度变化')
            ax4.grid(True, alpha=0.3)
            ax4.set_xticks(range(len(ds.time)))
            ax4.set_xticklabels([str(t)[:7] for t in ds.time.values], rotation=45)

            # 添加数值标注
            for i, temp in enumerate(depth_avg_temp):
                if not np.isnan(temp):
                    ax4.annotate(f'{temp:.2f}', (i, temp),
                                 textcoords="offset points", xytext=(0, 10),
                                 ha='center', fontsize=9)

        except Exception as e:
            ax4.text(0.5, 0.5, '深度平均错误', ha='center', va='center', transform=ax4.transAxes)

    plt.tight_layout()
    plt.show()


# ============================================================================
# 主程序
# ============================================================================

def main():
    """主程序函数"""

    # 文件路径
    file_path = 'E:/Work/PRIC/Science/Paper/2025/JTRES/donwload/cmems_mod_glo_phy_myint_0.083deg_P1M-m_1757650472394.nc'

    # 读取数据
    try:
        print("正在读取CMEMS数据...")
        ds = xr.open_dataset(file_path)
        print("✓ 数据读取成功！")
    except Exception as e:
        print(f"✗ 数据读取失败: {e}")
        print("请检查文件路径是否正确，以及是否安装了必要的库：")
        print("  conda install -c conda-forge xarray netcdf4 cartopy matplotlib")
        return

    print("南极海域环境参数完整分析系统")
    print("=" * 80)

    # 1. 数据结构分析
    print("\n第1步: 数据结构分析")
    all_variables = analyze_all_variables(ds)

    # 2. 数据摘要表
    print("\n第2步: 生成数据摘要表")
    create_summary_table(ds)

    # 3. 月度对比分析（统一颜色条）
    print("\n第3步: 生成月度对比分析（统一颜色条）")
    print("特色功能：所有月度对比图使用统一的颜色条范围，便于对比！")
    plot_all_variables_monthly(ds)

    # 4. 时间序列分析
    print("\n第4步: 生成时间序列分析")
    plot_time_series_analysis(ds, lon=170, lat=-70)

    # 5. 垂直结构分析
    print("\n第5步: 生成垂直结构分析")
    plot_vertical_structure_analysis(ds, lon=170, lat=-70)

    # 6. 附加分析
    print("\n第6步: 生成附加统计分析")
    plot_simple_analysis(ds)

    # 分析完成报告
    print("\n" + "=" * 80)
    print("🎉 南极海域环境参数完整分析已完成！")
    print("=" * 80)

    print("生成的分析内容包括:")
    print("📊 第1-2步: 基础数据分析")
    print("  • 11个环境参数的详细结构分析表")
    print("  • 完整的数据摘要统计表")
    print()
    print("🎨 第3步: 月度对比分析（核心功能）")
    print("  • 11个环境参数的5个月空间分布对比")
    print("  • 统一颜色条设计，便于直观对比月度差异")
    print("  • 南极极地立体投影，包含地理边界")
    print()
    print("📈 第4步: 时间序列分析")
    print("  • 特定位置所有11个变量的月度变化")
    print("  • 包含数值标注和趋势分析")
    print()
    print("🌊 第5步: 垂直结构分析")
    print("  • 4个3D变量的垂直剖面月度对比")
    print("  • 深度范围限制在1000m以内")
    print()
    print("📊 第6步: 附加统计分析")
    print("  • 海冰覆盖率统计分析")
    print("  • 温度-盐度关系散点图")
    print("  • 主要变量的区域平均时间序列")
    print("  • 上层海水平均温度变化")

    print(f"\n📊 数据概览:")
    print(f"时间范围: {str(ds.time.values[0])[:7]} 至 {str(ds.time.values[-1])[:7]} ({len(ds.time)} 个月)")
    print(
        f"空间范围: 纬度 {ds.latitude.min().values:.1f}°~{ds.latitude.max().values:.1f}°, 经度 {ds.longitude.min().values:.1f}°~{ds.longitude.max().values:.1f}°")
    print(f"深度范围: {ds.depth.min().values:.1f}m ~ {ds.depth.max().values:.1f}m ({len(ds.depth)} 层)")

    print("\n🎨 统一颜色条的优势:")
    print("✓ 同一变量不同月份使用相同的颜色范围")
    print("✓ 便于直观对比月度之间的数值差异")
    print("✓ 避免了每月独立缩放造成的视觉误导")
    print("✓ 在图标题中显示实际数据范围信息")
    print("✓ 右侧共享颜色条设计，节省空间")

    print("\n📋 包含的11个环境参数:")
    param_list = [
        "1. thetao - 海水位温 (3D变量，显示表层)",
        "2. so - 盐度 (3D变量，显示表层)",
        "3. uo - 东向流速 (3D变量，显示表层)",
        "4. vo - 北向流速 (3D变量，显示表层)",
        "5. bottomT - 底层温度 (2D变量)",
        "6. mlotst - 混合层深度 (2D变量)",
        "7. siconc - 海冰浓度 (2D变量)",
        "8. sithick - 海冰厚度 (2D变量)",
        "9. usi - 海冰东向速度 (2D变量)",
        "10. vsi - 海冰北向速度 (2D变量)",
        "11. zos - 海表面高度 (2D变量)"
    ]

    for param in param_list:
        print(f"   {param}")

    print("\n💡 使用建议:")
    print("• 观察海表温度的季节性变化模式")
    print("• 分析海冰浓度与温度的相互关系")
    print("• 研究混合层深度的时空分布特征")
    print("• 探索海流系统的垂直结构变化")
    print("• 对比不同变量的月度变异性")

    print("\n📁 数据保存:")
    print("所有图表已在屏幕显示，如需保存请在绘图函数中添加:")
    print("plt.savefig('filename.png', dpi=300, bbox_inches='tight')")

    print("\n🚀 分析系统运行完成！")
    print("感谢使用南极海域环境参数分析系统！")


# ============================================================================
# 程序入口点
# ============================================================================

if __name__ == "__main__":
    """程序入口点"""
    print("=" * 80)
    print("CMEMS南极海域环境参数完整分析系统 v2.0")
    print("=" * 80)
    print("功能特色:")
    print("• 11个环境参数的月度对比分析")
    print("• 统一颜色条设计，便于对比")
    print("• 垂直结构和时间序列分析")
    print("• 南极极地投影和地理要素")
    print("• 完整的统计分析报告")
    print("=" * 80)
    print()

    # 运行主程序
    main()
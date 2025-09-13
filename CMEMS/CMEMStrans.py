#!/usr/bin/env python3
"""
按月度输出所有参数层的哥白尼海洋数据转换器
生成每个月、每个深度层的环境变量文件，用于MaxEnt时序分析
"""

try:
    import numpy as np

    print("✅ NumPy 加载成功")
except ImportError as e:
    print(f"❌ NumPy 导入失败: {e}")
    exit(1)

try:
    import netCDF4 as nc

    print("✅ NetCDF4 加载成功")
except ImportError as e:
    print(f"❌ NetCDF4 导入失败: {e}")
    print("请安装: pip install netcdf4")
    exit(1)

import os
from pathlib import Path
import warnings
from datetime import datetime
import calendar

warnings.filterwarnings('ignore')

# 你的数据文件路径
DATA_FILE = r"E:/Work/PRIC/Science/Paper/2025/JTRES/donwload/cmems_mod_glo_phy_myint_0.083deg_P1M-m_1757650472394.nc"
OUTPUT_DIR = r"E:/Work/PRIC/Science/Paper/2025/JTRES/maxent_monthly_layers"


class MonthlyLayersConverter:
    def __init__(self, data_path, output_dir):
        self.data_path = data_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.ds = None
        self.time_info = []

    def open_dataset(self):
        """打开数据集并分析时间维度"""
        try:
            print(f"正在打开文件: {self.data_path}")
            self.ds = nc.Dataset(self.data_path, 'r')
            print("✅ 文件打开成功!")

            # 分析时间维度
            self.analyze_time_dimension()
            return True
        except Exception as e:
            print(f"❌ 文件打开失败: {e}")
            return False

    def analyze_time_dimension(self):
        """分析时间维度信息"""
        time_vars = ['time', 'time_counter', 't']
        time_var_name = None

        for var_name in time_vars:
            if var_name in self.ds.variables:
                time_var_name = var_name
                break

        if not time_var_name:
            print("❌ 找不到时间维度")
            return

        time_var = self.ds.variables[time_var_name]
        print(f"\n📅 时间维度分析:")
        print(f"  变量名: {time_var_name}")
        print(f"  时间点数: {len(time_var)}")

        # 获取时间单位和参考时间
        if hasattr(time_var, 'units'):
            print(f"  时间单位: {time_var.units}")

            try:
                # 尝试解析时间
                from datetime import datetime, timedelta
                import re

                # 解析时间单位（如：days since 1950-01-01）
                units_str = time_var.units
                if 'since' in units_str:
                    parts = units_str.split('since')
                    time_unit = parts[0].strip()
                    ref_date_str = parts[1].strip()

                    # 解析参考日期
                    ref_date = datetime.strptime(ref_date_str.split()[0], '%Y-%m-%d')

                    # 转换时间值
                    time_values = time_var[:]

                    self.time_info = []
                    for i, time_val in enumerate(time_values):
                        if 'days' in time_unit:
                            actual_date = ref_date + timedelta(days=float(time_val))
                        elif 'hours' in time_unit:
                            actual_date = ref_date + timedelta(hours=float(time_val))
                        elif 'seconds' in time_unit:
                            actual_date = ref_date + timedelta(seconds=float(time_val))
                        else:
                            actual_date = ref_date + timedelta(days=float(time_val))

                        self.time_info.append({
                            'index': i,
                            'datetime': actual_date,
                            'year': actual_date.year,
                            'month': actual_date.month,
                            'month_name': calendar.month_name[actual_date.month],
                            'date_str': actual_date.strftime('%Y%m')
                        })

                    print(
                        f"  时间范围: {self.time_info[0]['datetime'].strftime('%Y-%m-%d')} 至 {self.time_info[-1]['datetime'].strftime('%Y-%m-%d')}")
                    print(f"  包含月份:")
                    for time_info in self.time_info:
                        print(
                            f"    {time_info['index']}: {time_info['datetime'].strftime('%Y-%m')} ({time_info['month_name']})")

            except Exception as e:
                print(f"  时间解析警告: {e}")
                # 如果无法解析时间，创建简单的索引
                self.time_info = []
                for i in range(len(time_var)):
                    self.time_info.append({
                        'index': i,
                        'datetime': None,
                        'year': None,
                        'month': None,
                        'month_name': f'TimeStep_{i}',
                        'date_str': f't{i:02d}'
                    })

        self.time_var_name = time_var_name

    def analyze_depth_dimension(self):
        """分析深度维度"""
        depth_vars = ['depth', 'lev', 'deptht', 'depthu', 'depthv', 'z']
        depth_info = {}

        for depth_var_name in depth_vars:
            if depth_var_name in self.ds.variables:
                depth_var = self.ds.variables[depth_var_name]
                depth_values = depth_var[:]

                depth_info[depth_var_name] = {
                    'values': depth_values,
                    'count': len(depth_values),
                    'range': (float(depth_values.min()), float(depth_values.max())),
                    'units': getattr(depth_var, 'units', 'unknown')
                }

                print(f"\n🌊 深度维度: {depth_var_name}")
                print(f"  层数: {len(depth_values)}")
                print(
                    f"  深度范围: {depth_values.min():.2f} - {depth_values.max():.2f} {depth_info[depth_var_name]['units']}")
                if len(depth_values) <= 20:
                    print(f"  深度值: {[f'{d:.1f}' for d in depth_values]}")
                else:
                    print(f"  前10层深度: {[f'{d:.1f}' for d in depth_values[:10]]}")

        return depth_info

    def analyze_structure(self):
        """完整的结构分析"""
        print("\n" + "=" * 80)
        print("📊 数据集完整结构分析")
        print("=" * 80)

        print(f"📁 文件: {Path(self.data_path).name}")

        # 维度信息
        print(f"\n📐 维度信息:")
        for dim_name in self.ds.dimensions:
            dim = self.ds.dimensions[dim_name]
            print(f"  {dim_name}: {len(dim)} {'(无限)' if dim.isunlimited() else ''}")

        # 坐标变量
        print(f"\n🗺️ 坐标变量:")
        coord_info = {}
        for var_name in self.ds.variables:
            var = self.ds.variables[var_name]
            if len(var.dimensions) == 1 and var_name in self.ds.dimensions:
                coord_info[var_name] = {
                    'shape': var.shape,
                    'units': getattr(var, 'units', 'no units'),
                    'range': (float(var[:].min()), float(var[:].max())) if var.size > 0 else (None, None)
                }
                print(f"  {var_name}: {var.shape} [{coord_info[var_name]['units']}]")
                if var.size <= 10:
                    print(f"    值: {var[:]}")
                elif coord_info[var_name]['range'][0] is not None:
                    print(f"    范围: {coord_info[var_name]['range'][0]:.4f} ~ {coord_info[var_name]['range'][1]:.4f}")

        # 深度维度详情
        depth_info = self.analyze_depth_dimension()

        # 数据变量
        print(f"\n🌊 数据变量:")
        data_vars = []
        for var_name in self.ds.variables:
            var = self.ds.variables[var_name]
            if len(var.dimensions) > 1:
                data_vars.append(var_name)
                print(f"  📈 {var_name}:")
                print(f"    形状: {var.shape}")
                print(f"    维度: {var.dimensions}")
                print(f"    数据类型: {var.dtype}")
                if hasattr(var, 'long_name'):
                    print(f"    描述: {var.long_name}")
                if hasattr(var, 'units'):
                    print(f"    单位: {var.units}")
                if hasattr(var, '_FillValue'):
                    print(f"    缺失值: {var._FillValue}")
                print()

        return data_vars, depth_info

    def get_monthly_data(self, var_name, time_idx, depth_idx=None):
        """获取指定月份和深度的数据"""
        if var_name not in self.ds.variables:
            return None, None, None

        var = self.ds.variables[var_name]
        dims = var.dimensions

        print(f"  📊 提取数据: {var_name}")
        print(f"    时间索引: {time_idx} ({self.time_info[time_idx]['month_name']})")
        if depth_idx is not None:
            print(f"    深度索引: {depth_idx}")

        # 构建索引
        indices = {}
        for i, dim_name in enumerate(dims):
            if dim_name == self.time_var_name:
                indices[i] = time_idx
            elif dim_name in ['depth', 'lev', 'deptht', 'depthu', 'depthv', 'z']:
                if depth_idx is not None:
                    indices[i] = depth_idx
                else:
                    indices[i] = slice(None)  # 所有深度
            else:
                indices[i] = slice(None)  # 所有其他维度

        # 构建切片
        slices = []
        for i in range(len(dims)):
            slices.append(indices.get(i, slice(None)))

        # 提取数据
        try:
            data = var[tuple(slices)]

            # 获取经纬度
            lon_names = ['longitude', 'lon', 'nav_lon', 'x']
            lat_names = ['latitude', 'lat', 'nav_lat', 'y']

            lons = None
            lats = None

            for lon_name in lon_names:
                if lon_name in self.ds.variables:
                    lons = self.ds.variables[lon_name][:]
                    break

            for lat_name in lat_names:
                if lat_name in self.ds.variables:
                    lats = self.ds.variables[lat_name][:]
                    break

            # 确保数据是2D的
            while len(data.shape) > 2:
                if data.shape[0] == 1:
                    data = data[0]
                else:
                    break

            print(f"    提取后形状: {data.shape}")

            return data, lons, lats

        except Exception as e:
            print(f"    ❌ 数据提取失败: {e}")
            return None, None, None

    def save_monthly_layer(self, data, lons, lats, var_name, time_info, depth_idx=None, depth_value=None):
        """保存月度图层"""

        # 处理缺失值
        data = np.where(np.isnan(data), -9999, data)
        data = np.where(np.isinf(data), -9999, data)

        # 确保纬度从北到南
        if len(lats) > 1 and lats[0] < lats[-1]:
            lats = lats[::-1]
            data = np.flipud(data)

        # 生成文件名
        if depth_idx is not None:
            if depth_value is not None:
                filename = f"{var_name}_{time_info['date_str']}_d{depth_idx}_{depth_value:.1f}m.asc"
            else:
                filename = f"{var_name}_{time_info['date_str']}_d{depth_idx}.asc"
        else:
            filename = f"{var_name}_{time_info['date_str']}.asc"

        # 创建月份子目录
        month_dir = self.output_dir / time_info['date_str']
        month_dir.mkdir(exist_ok=True)

        output_file = month_dir / filename

        # 栅格参数
        ncols = len(lons)
        nrows = len(lats)
        xllcorner = float(lons.min())
        yllcorner = float(lats.min())
        cellsize = float(abs(lons[1] - lons[0])) if len(lons) > 1 else 0.083

        # 写入文件
        with open(output_file, 'w') as f:
            f.write(f"ncols {ncols}\n")
            f.write(f"nrows {nrows}\n")
            f.write(f"xllcorner {xllcorner:.6f}\n")
            f.write(f"yllcorner {yllcorner:.6f}\n")
            f.write(f"cellsize {cellsize:.6f}\n")
            f.write(f"NODATA_value -9999\n")

            for row in data:
                row_str = " ".join([f"{val:.4f}" if val != -9999 else "-9999"
                                    for val in row])
                f.write(row_str + "\n")

        print(f"    ✅ 保存: {filename}")
        return output_file

    def convert_all_monthly_layers(self, variables=None, depth_layers='all', max_depth_layers=10):
        """
        转换所有月度图层

        Parameters:
        -----------
        variables : list
            要转换的变量列表，None表示所有变量
        depth_layers : str or list
            深度层设置：'all'=所有层, 'surface'=仅表层, [0,1,2]=指定层
        max_depth_layers : int
            最大深度层数限制
        """

        if not self.open_dataset():
            return []

        # 分析数据结构
        available_vars, depth_info = self.analyze_structure()

        # 选择变量
        if variables is None:
            # 推荐的海洋变量
            recommended = ['thetao', 'so', 'uo', 'vo', 'zos', 'mlotst', 'bottomT', 'sob']
            variables = [v for v in recommended if v in available_vars]
            if not variables:
                variables = available_vars[:8]  # 取前8个变量

        print(f"\n🎯 将转换的变量: {variables}")
        print(f"📅 时间步长: {len(self.time_info)} 个月")

        converted_files = []
        total_operations = 0
        successful_operations = 0

        # 为每个变量处理
        for var_name in variables:
            print(f"\n{'=' * 60}")
            print(f"🔄 处理变量: {var_name}")
            print('=' * 60)

            var = self.ds.variables[var_name]
            var_dims = var.dimensions

            # 确定是否有深度维度
            has_depth = any(depth_dim in var_dims for depth_dim in ['depth', 'lev', 'deptht', 'depthu', 'depthv', 'z'])

            if has_depth:
                # 确定使用的深度层
                depth_dim_name = None
                for depth_name in ['depth', 'lev', 'deptht', 'depthu', 'depthv', 'z']:
                    if depth_name in var_dims and depth_name in depth_info:
                        depth_dim_name = depth_name
                        break

                if depth_dim_name:
                    depth_values = depth_info[depth_dim_name]['values']

                    if depth_layers == 'surface':
                        depth_indices = [0]
                    elif depth_layers == 'all':
                        depth_indices = list(range(min(len(depth_values), max_depth_layers)))
                    elif isinstance(depth_layers, list):
                        depth_indices = [i for i in depth_layers if i < len(depth_values)]
                    else:
                        depth_indices = [0]

                    print(f"  🌊 深度层设置: {len(depth_indices)} 层")
                    for i in depth_indices[:5]:  # 显示前5层
                        print(f"    层 {i}: {depth_values[i]:.1f} {depth_info[depth_dim_name]['units']}")
                    if len(depth_indices) > 5:
                        print(f"    ... 还有 {len(depth_indices) - 5} 层")
                else:
                    depth_indices = [None]
                    print(f"  ⚠️ 深度维度识别失败，跳过深度处理")
            else:
                depth_indices = [None]
                print(f"  📊 无深度维度")

            # 为每个时间步和深度层生成文件
            for time_info in self.time_info:
                for depth_idx in depth_indices:
                    total_operations += 1

                    try:
                        # 获取数据
                        data, lons, lats = self.get_monthly_data(var_name, time_info['index'], depth_idx)

                        if data is not None and lons is not None and lats is not None:
                            # 获取深度值
                            depth_value = None
                            if depth_idx is not None and depth_dim_name:
                                depth_value = depth_info[depth_dim_name]['values'][depth_idx]

                            # 保存文件
                            output_file = self.save_monthly_layer(
                                data, lons, lats, var_name, time_info, depth_idx, depth_value
                            )
                            converted_files.append(output_file)
                            successful_operations += 1

                    except Exception as e:
                        print(f"    ❌ 失败: {e}")

        # 关闭数据集
        self.ds.close()

        # 生成报告
        self.generate_monthly_report(converted_files, total_operations, successful_operations)

        return converted_files

    def generate_monthly_report(self, converted_files, total_ops, successful_ops):
        """生成月度转换报告"""
        report_file = self.output_dir / "monthly_conversion_report.txt"

        # 按月份组织文件
        monthly_files = {}
        for file_path in converted_files:
            # 从路径中提取月份信息
            month_str = file_path.parent.name
            if month_str not in monthly_files:
                monthly_files[month_str] = []
            monthly_files[month_str].append(file_path.name)

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("🌊 哥白尼海洋数据月度图层转换报告\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"📁 源文件: {self.data_path}\n")
            f.write(f"📂 输出目录: {self.output_dir}\n")
            f.write(f"⏰ 转换时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write(f"📊 转换统计:\n")
            f.write(f"  总操作数: {total_ops}\n")
            f.write(f"  成功数: {successful_ops}\n")
            f.write(f"  成功率: {successful_ops / total_ops * 100:.1f}%\n")
            f.write(f"  生成文件数: {len(converted_files)}\n\n")

            f.write(f"📅 月度文件分布:\n")
            for month_str in sorted(monthly_files.keys()):
                f.write(f"\n  📆 {month_str}/ ({len(monthly_files[month_str])} 文件)\n")
                for filename in sorted(monthly_files[month_str])[:10]:  # 显示前10个
                    f.write(f"    - {filename}\n")
                if len(monthly_files[month_str]) > 10:
                    f.write(f"    ... 还有 {len(monthly_files[month_str]) - 10} 个文件\n")

            f.write(f"\n📋 MaxEnt时序分析使用说明:\n")
            f.write("1. 每个月份有单独的子目录\n")
            f.write("2. 文件命名格式: 变量名_年月_深度层.asc\n")
            f.write("3. 可以按月份批量导入MaxEnt进行时序对比\n")
            f.write("4. 建议先选择关键变量和深度层进行测试\n")
            f.write("5. 注意文件数量较大，建议分批处理\n\n")

            f.write(f"📁 目录结构:\n")
            f.write(f"  {self.output_dir.name}/\n")
            for month_str in sorted(monthly_files.keys())[:5]:
                f.write(f"  ├── {month_str}/ ({len(monthly_files[month_str])} files)\n")
            if len(monthly_files) > 5:
                f.write(f"  ├── ... ({len(monthly_files) - 5} more months)\n")
            f.write(f"  └── monthly_conversion_report.txt\n")

        print(f"\n📄 详细报告已保存: {report_file}")


def main():
    """主函数"""
    print("🌊 哥白尼海洋数据月度图层转换器")
    print("=" * 50)
    print("此工具将为每个月份和深度层生成单独的MaxEnt环境图层文件")
    print("=" * 50)

    converter = MonthlyLayersConverter(DATA_FILE, OUTPUT_DIR)

    # 配置参数
    config = {
        'variables': None,  # None = 自动选择推荐变量
        'depth_layers': 'surface',  # 'all', 'surface', 或 [0,1,2,3,4]
        'max_depth_layers': 5  # 最大深度层数限制
    }

    # 高级配置选项（根据需要取消注释）:

    # 1. 指定特定变量
    # config['variables'] = ['thetao', 'so', 'uo', 'vo']

    # 2. 包含多个深度层
    # config['depth_layers'] = [0, 1, 2, 3, 4]  # 前5层

    # 3. 包含所有可用深度层（注意：文件数量会很大！）
    # config['depth_layers'] = 'all'
    # config['max_depth_layers'] = 10

    print(f"\n⚙️ 转换配置:")
    print(f"  变量选择: {'自动推荐' if config['variables'] is None else config['variables']}")
    print(f"  深度层: {config['depth_layers']}")
    if config['depth_layers'] == 'all':
        print(f"  最大深度层数: {config['max_depth_layers']}")

    # 执行转换
    print(f"\n🚀 开始转换...")
    converted_files = converter.convert_all_monthly_layers(**config)

    if converted_files:
        print(f"\n🎉 转换完成!")
        print(f"✅ 成功生成 {len(converted_files)} 个月度环境图层文件")
        print(f"📂 文件保存位置: {OUTPUT_DIR}")
        print(f"\n💡 提示: 文件按月份组织在子目录中，便于MaxEnt时序分析")
    else:
        print(f"\n❌ 转换失败，请检查数据文件")


if __name__ == "__main__":
    main()
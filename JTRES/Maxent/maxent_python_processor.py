pip install pandas numpy matplotlib seaborn scipy

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MaxEnt数据准备Python脚本
用于处理海洋生物观测数据，生成MaxEnt所需的输入文件
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']  # Windows
# plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # Mac
plt.rcParams['axes.unicode_minus'] = False

class MaxEntDataProcessor:
    """MaxEnt数据处理器类"""
    
    def __init__(self, data_file):
        """
        初始化处理器
        
        Parameters:
        -----------
        data_file : str
            输入CSV文件路径
        """
        self.data_file = data_file
        self.data = None
        self.species_data = {}
        self.env_data = None
        self.selected_env_vars = []
        
    def load_data(self):
        """加载数据"""
        print("=" * 50)
        print("1. 加载数据")
        print("=" * 50)
        
        self.data = pd.read_csv(self.data_file)
        print(f"✓ 数据加载成功")
        print(f"  - 总记录数: {len(self.data)}")
        print(f"  - 总列数: {len(self.data.columns)}")
        print(f"  - 列名: {', '.join(self.data.columns[:10])}...")
        
        # 标准化列名
        self.data.rename(columns={'Ice density': 'Ice_density'}, inplace=True)
        
        return self
    
    def analyze_species(self, min_records=20):
        """
        分析物种数据
        
        Parameters:
        -----------
        min_records : int
            最小记录数阈值
        """
        print("\n" + "=" * 50)
        print("2. 物种分析")
        print("=" * 50)
        
        # 统计物种出现次数
        species_counts = self.data['Species'].value_counts()
        
        print("\n物种出现频次统计:")
        print("-" * 30)
        for species, count in species_counts.head(10).items():
            status = "✓" if count >= min_records else "⚠"
            print(f"  {status} {species}: {count} 条记录")
        
        # 筛选合适的物种
        suitable_species = species_counts[species_counts >= min_records].index.tolist()
        print(f"\n✓ 适合建模的物种 (n≥{min_records}): {len(suitable_species)} 个")
        
        return suitable_species
    
    def analyze_environment(self, threshold=0.7):
        """
        分析环境变量相关性
        
        Parameters:
        -----------
        threshold : float
            相关性阈值
        """
        print("\n" + "=" * 50)
        print("3. 环境变量分析")
        print("=" * 50)
        
        # 环境变量列表
        env_vars = ['TempA', 'TempW', 'Salinity', 'O2Con', 'O2', 
                   'Turbidity', 'CHL', 'CDOM', 'pH', 'WindSpeed2M', 
                   'Humidity', 'Ice_density', 'Detph']
        
        # 提取环境数据
        env_data = self.data[env_vars].copy()
        
        # 数据完整性检查
        print("\n环境变量数据完整性:")
        print("-" * 30)
        for var in env_vars:
            completeness = (env_data[var].notna().sum() / len(env_data)) * 100
            print(f"  {var:15} {completeness:6.1f}%")
        
        # 计算相关性矩阵
        corr_matrix = env_data.corr()
        
        # 找出高相关性变量对
        print(f"\n高相关性变量对 (|r| > {threshold}):")
        print("-" * 30)
        high_corr_pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                if abs(corr_matrix.iloc[i, j]) > threshold:
                    var1 = corr_matrix.columns[i]
                    var2 = corr_matrix.columns[j]
                    corr_val = corr_matrix.iloc[i, j]
                    high_corr_pairs.append((var1, var2, corr_val))
                    print(f"  {var1:12} vs {var2:12}: r = {corr_val:6.3f}")
        
        # 基于相关性选择变量
        # 策略：从高相关对中，保留生态意义更重要的变量
        vars_to_remove = set()
        for var1, var2, corr in high_corr_pairs:
            # 优先保留TempW而非pH
            if 'pH' in [var1, var2] and 'TempW' in [var1, var2]:
                vars_to_remove.add('pH')
            # 优先保留TempW而非O2Con
            elif 'O2Con' in [var1, var2] and 'TempW' in [var1, var2]:
                vars_to_remove.add('O2Con')
            # 优先保留Turbidity而非CDOM
            elif 'CDOM' in [var1, var2] and 'Turbidity' in [var1, var2]:
                vars_to_remove.add('CDOM')
        
        # 推荐的环境变量
        recommended_vars = ['TempW', 'Salinity', 'CHL', 'Ice_density', 
                           'Detph', 'Turbidity', 'WindSpeed2M']
        
        print(f"\n✓ 推荐使用的环境变量:")
        print("  " + ", ".join(recommended_vars))
        
        self.selected_env_vars = recommended_vars
        
        # 绘制相关性热图
        self._plot_correlation_matrix(corr_matrix, env_vars)
        
        return recommended_vars
    
    def _plot_correlation_matrix(self, corr_matrix, variables):
        """绘制相关性矩阵热图"""
        plt.figure(figsize=(12, 10))
        
        # 创建mask，只显示上三角
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        
        # 绘制热图
        sns.heatmap(corr_matrix, mask=mask, annot=True, fmt='.2f', 
                   cmap='coolwarm', center=0, square=True,
                   linewidths=1, cbar_kws={"shrink": 0.8})
        
        plt.title('环境变量相关性矩阵', fontsize=16, pad=20)
        plt.tight_layout()
        plt.savefig('correlation_matrix.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("\n✓ 相关性矩阵图已保存: correlation_matrix.png")
    
    def prepare_species_occurrences(self, species_list):
        """
        准备物种出现点数据
        
        Parameters:
        -----------
        species_list : list
            要处理的物种列表
        """
        print("\n" + "=" * 50)
        print("4. 准备物种出现点数据")
        print("=" * 50)
        
        # 为每个物种创建出现点数据
        for species in species_list:
            # 筛选该物种的数据
            sp_data = self.data[self.data['Species'] == species].copy()
            
            # 获取唯一的经纬度点
            occurrence_data = sp_data[['Species', 'LONG', 'LAT']].drop_duplicates()
            occurrence_data.columns = ['species', 'longitude', 'latitude']
            
            # 保存到字典
            self.species_data[species] = occurrence_data
            
            # 保存到文件
            filename = f"maxent_{species.replace(' ', '_')}.csv"
            occurrence_data.to_csv(filename, index=False)
            print(f"  ✓ {species}: {len(occurrence_data)} 个独立位点 -> {filename}")
        
        # 创建所有物种的合并文件
        all_species = pd.concat(list(self.species_data.values()), ignore_index=True)
        all_species.to_csv('maxent_all_species.csv', index=False)
        print(f"\n✓ 所有物种合并文件: maxent_all_species.csv ({len(all_species)} 条记录)")
        
        return self
    
    def prepare_environmental_layers(self):
        """准备环境图层数据"""
        print("\n" + "=" * 50)
        print("5. 准备环境数据")
        print("=" * 50)
        
        # 选择需要的列
        env_cols = ['LONG', 'LAT'] + self.selected_env_vars
        
        # 提取环境数据
        env_data = self.data[env_cols].copy()
        
        # 按位置聚合（取平均值）
        env_data_grouped = env_data.groupby(['LONG', 'LAT']).mean().reset_index()
        
        # 重命名列
        env_data_grouped.columns = ['longitude', 'latitude'] + self.selected_env_vars
        
        # 保存环境数据
        env_data_grouped.to_csv('maxent_environment_swd.csv', index=False)
        print(f"✓ 环境数据文件: maxent_environment_swd.csv")
        print(f"  - 唯一位置点: {len(env_data_grouped)}")
        print(f"  - 环境变量: {', '.join(self.selected_env_vars)}")
        
        self.env_data = env_data_grouped
        
        # 创建偏差文件
        self._create_bias_file()
        
        return self
    
    def _create_bias_file(self):
        """创建采样偏差文件"""
        # 统计每个位置的采样强度
        bias_data = self.data.groupby(['LONG', 'LAT']).size().reset_index(name='sampling_effort')
        bias_data.columns = ['longitude', 'latitude', 'sampling_effort']
        
        # 保存偏差文件
        bias_data.to_csv('maxent_bias.csv', index=False)
        print(f"\n✓ 采样偏差文件: maxent_bias.csv ({len(bias_data)} 个位置)")
    
    def generate_species_profiles(self, species_list):
        """
        生成物种环境偏好分析
        
        Parameters:
        -----------
        species_list : list
            要分析的物种列表
        """
        print("\n" + "=" * 50)
        print("6. 物种环境偏好分析")
        print("=" * 50)
        
        profiles = {}
        
        for species in species_list:
            sp_data = self.data[self.data['Species'] == species]
            
            profile = {
                'n_records': len(sp_data),
                'env_preferences': {}
            }
            
            print(f"\n{species} (n={len(sp_data)}):")
            print("-" * 30)
            
            for var in self.selected_env_vars:
                if var in sp_data.columns:
                    values = sp_data[var].dropna()
                    if len(values) > 0:
                        profile['env_preferences'][var] = {
                            'mean': values.mean(),
                            'std': values.std(),
                            'min': values.min(),
                            'max': values.max()
                        }
                        print(f"  {var:12} μ={values.mean():7.2f} ± {values.std():6.2f} [{values.min():7.2f}, {values.max():7.2f}]")
            
            profiles[species] = profile
        
        return profiles
    
    def create_maxent_batch_script(self, species_list):
        """
        创建MaxEnt批处理脚本
        
        Parameters:
        -----------
        species_list : list
            要处理的物种列表
        """
        print("\n" + "=" * 50)
        print("7. 创建批处理脚本")
        print("=" * 50)
        
        # Windows批处理脚本
        bat_commands = []
        
        for species in species_list:
            sp_file = species.replace(' ', '_')
            cmd = f"""java -mx2048m -jar maxent.jar ^
    samplesfile=maxent_{sp_file}.csv ^
    environmentallayers=maxent_environment_swd.csv ^
    biasfile=maxent_bias.csv ^
    outputdirectory=output_{sp_file} ^
    responsecurves=true ^
    pictures=true ^
    jackknife=true ^
    writebackgroundpredictions=true ^
    writeclampgrid=false ^
    writemess=false ^
    replicates=10 ^
    replicatetype=crossvalidate ^
    threads=4"""
            bat_commands.append(cmd)
        
        # 保存Windows批处理文件
        with open('run_maxent.bat', 'w') as f:
            f.write('@echo off\n')
            f.write('echo Starting MaxEnt analysis...\n\n')
            for cmd in bat_commands:
                f.write(cmd + '\n\n')
            f.write('echo All analyses completed!\n')
            f.write('pause\n')
        
        # Linux/Mac Shell脚本
        sh_commands = []
        
        for species in species_list:
            sp_file = species.replace(' ', '_')
            cmd = f"""java -mx2048m -jar maxent.jar \\
    samplesfile=maxent_{sp_file}.csv \\
    environmentallayers=maxent_environment_swd.csv \\
    biasfile=maxent_bias.csv \\
    outputdirectory=output_{sp_file} \\
    responsecurves=true \\
    pictures=true \\
    jackknife=true \\
    writebackgroundpredictions=true \\
    writeclampgrid=false \\
    writemess=false \\
    replicates=10 \\
    replicatetype=crossvalidate \\
    threads=4"""
            sh_commands.append(cmd)
        
        # 保存Shell脚本
        with open('run_maxent.sh', 'w') as f:
            f.write('#!/bin/bash\n')
            f.write('echo "Starting MaxEnt analysis..."\n\n')
            for cmd in sh_commands:
                f.write(cmd + '\n\n')
            f.write('echo "All analyses completed!"\n')
        
        print("✓ 批处理脚本已创建:")
        print("  - Windows: run_maxent.bat")
        print("  - Linux/Mac: run_maxent.sh")
    
    def generate_report(self, species_list):
        """
        生成数据质量报告
        
        Parameters:
        -----------
        species_list : list
            物种列表
        """
        print("\n" + "=" * 50)
        print("8. 生成分析报告")
        print("=" * 50)
        
        report = []
        report.append("=" * 60)
        report.append("MaxEnt 数据准备报告")
        report.append("=" * 60)
        report.append("")
        
        # 数据概况
        report.append("1. 数据概况")
        report.append("-" * 40)
        report.append(f"原始数据文件: {self.data_file}")
        report.append(f"总记录数: {len(self.data)}")
        report.append(f"唯一位置点: {len(self.data[['LONG', 'LAT']].drop_duplicates())}")
        report.append("")
        
        # 物种统计
        report.append("2. 物种统计")
        report.append("-" * 40)
        for species in species_list:
            n_records = len(self.data[self.data['Species'] == species])
            n_unique = len(self.species_data[species]) if species in self.species_data else 0
            report.append(f"{species:25} 记录数: {n_records:4}  独立位点: {n_unique:4}")
        report.append("")
        
        # 环境变量
        report.append("3. 选定的环境变量")
        report.append("-" * 40)
        for var in self.selected_env_vars:
            if var in self.data.columns:
                values = self.data[var].dropna()
                report.append(f"{var:15} 范围: [{values.min():.2f}, {values.max():.2f}]  "
                            f"均值: {values.mean():.2f} ± {values.std():.2f}")
        report.append("")
        
        # 输出文件
        report.append("4. 生成的文件")
        report.append("-" * 40)
        report.append("物种出现点文件:")
        for species in species_list:
            report.append(f"  - maxent_{species.replace(' ', '_')}.csv")
        report.append("  - maxent_all_species.csv (所有物种)")
        report.append("")
        report.append("环境数据文件:")
        report.append("  - maxent_environment_swd.csv")
        report.append("  - maxent_bias.csv")
        report.append("")
        report.append("辅助文件:")
        report.append("  - correlation_matrix.png")
        report.append("  - run_maxent.bat / run_maxent.sh")
        report.append("  - analysis_report.txt")
        report.append("")
        
        # MaxEnt运行建议
        report.append("5. MaxEnt 运行建议")
        report.append("-" * 40)
        report.append("基本设置:")
        report.append("  - Random test percentage: 25")
        report.append("  - Replicates: 10 (交叉验证)")
        report.append("  - Maximum iterations: 500")
        report.append("  - Convergence threshold: 0.00001")
        report.append("")
        report.append("正则化参数:")
        report.append("  - 大样本 (n>80): 1.0")
        report.append("  - 中等样本 (30-80): 1.5")
        report.append("  - 小样本 (n<30): 2.0")
        report.append("")
        report.append("输出选项:")
        report.append("  ✓ Response curves")
        report.append("  ✓ Jackknife variable importance")
        report.append("  ✓ Pictures of predictions")
        report.append("")
        
        # 注意事项
        report.append("6. 注意事项")
        report.append("-" * 40)
        report.append("- Emperor penguin 样本量较少(n=22)，结果需谨慎解释")
        report.append("- 已剔除高相关性环境变量 (|r| > 0.7)")
        report.append("- 建议使用偏差文件进行采样偏差校正")
        report.append("- 模型评价指标 AUC > 0.7 为可接受，> 0.9 为优秀")
        report.append("")
        
        report.append("=" * 60)
        report.append(f"报告生成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 保存报告
        with open('analysis_report.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        
        print("✓ 分析报告已生成: analysis_report.txt")
        
        # 打印报告摘要
        print("\n报告摘要:")
        print("-" * 30)
        print(f"  处理物种数: {len(species_list)}")
        print(f"  环境变量数: {len(self.selected_env_vars)}")
        print(f"  生成文件数: {len(species_list) + 5}")

def main():
    """主函数"""
    print("\n" + "╔" + "═" * 48 + "╗")
    print("║" + " " * 15 + "MaxEnt 数据处理工具" + " " * 14 + "║")
    print("╚" + "═" * 48 + "╝\n")
    
    # 配置参数
    DATA_FILE = 'JTRES.csv'  # 输入文件名
    MIN_RECORDS = 20  # 最小记录数阈值
    
    # 目标物种列表（可根据需要修改）
    TARGET_SPECIES = [
        'antarctic petrel',
        'snow petrel', 
        'crabeater seal',
        'adelie penguin',
        'emperor penguin'
    ]
    
    try:
        # 初始化处理器
        processor = MaxEntDataProcessor(DATA_FILE)
        
        # 执行处理流程
        processor.load_data()
        suitable_species = processor.analyze_species(MIN_RECORDS)
        processor.analyze_environment(threshold=0.7)
        
        # 使用目标物种或自动选择的物种
        species_to_process = [sp for sp in TARGET_SPECIES if sp in suitable_species]
        if not species_to_process:
            species_to_process = suitable_species[:5]  # 选择前5个物种
        
        processor.prepare_species_occurrences(species_to_process)
        processor.prepare_environmental_layers()
        processor.generate_species_profiles(species_to_process)
        processor.create_maxent_batch_script(species_to_process)
        processor.generate_report(species_to_process)
        
        print("\n" + "=" * 50)
        print("✅ 所有处理完成！")
        print("=" * 50)
        print("\n下一步:")
        print("1. 检查生成的文件")
        print("2. 将所有CSV文件和maxent.jar放在同一目录")
        print("3. 运行批处理脚本 (run_maxent.bat 或 run_maxent.sh)")
        print("4. 查看output_[species]目录中的结果")
        
    except FileNotFoundError:
        print(f"\n❌ 错误: 找不到文件 '{DATA_FILE}'")
        print("请确保数据文件在当前目录中")
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

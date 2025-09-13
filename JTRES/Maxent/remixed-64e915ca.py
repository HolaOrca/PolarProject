#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MaxEnt数据处理GUI工具 - SWD格式支持版
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
import os
import sys


class MaxEntGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MaxEnt 数据处理工具")
        self.root.geometry("1000x700")

        # 数据存储
        self.data = None
        self.processed_data = None
        self.env_vars = {}

        # 创建界面
        self.create_interface()

    def create_interface(self):
        """创建主界面"""
        # 主标题
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text="MaxEnt 数据处理工具",
                               font=('Arial', 18, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(pady=15)

        # 创建笔记本控件
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建各个标签页
        self.create_load_tab()
        self.create_species_tab()
        self.create_env_tab()
        self.create_process_tab()
        self.create_export_tab()

        # 状态栏
        self.status_var = tk.StringVar(value="准备就绪")
        status_bar = tk.Label(self.root, textvariable=self.status_var,
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_load_tab(self):
        """创建数据加载标签页"""
        load_frame = ttk.Frame(self.notebook)
        self.notebook.add(load_frame, text="1. 加载数据")

        # 文件选择区域
        file_frame = tk.LabelFrame(load_frame, text="选择数据文件", font=('Arial', 12, 'bold'))
        file_frame.pack(fill=tk.X, padx=20, pady=20)

        self.file_path = tk.StringVar()

        tk.Label(file_frame, text="CSV文件路径:", font=('Arial', 11)).pack(anchor='w', padx=10, pady=5)

        path_frame = tk.Frame(file_frame)
        path_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Entry(path_frame, textvariable=self.file_path, font=('Arial', 10)).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(path_frame, text="浏览...", command=self.browse_file).pack(side=tk.RIGHT, padx=(5, 0))

        tk.Button(file_frame, text="加载数据", font=('Arial', 12, 'bold'),
                  bg='#27ae60', fg='white', command=self.load_data).pack(pady=10)

        # 数据信息显示区域
        self.info_text = tk.Text(load_frame, height=15, font=('Courier', 10))
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 添加滚动条
        scrollbar = tk.Scrollbar(self.info_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.info_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.info_text.yview)

    def create_species_tab(self):
        """创建物种选择标签页"""
        species_frame = ttk.Frame(self.notebook)
        self.notebook.add(species_frame, text="2. 选择物种")

        # 说明
        tk.Label(species_frame, text="选择要分析的物种（建议选择样本量≥20的物种）",
                 font=('Arial', 12, 'bold')).pack(pady=10)

        # 物种列表框架
        list_frame = tk.Frame(species_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 创建列表框和滚动条
        self.species_listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE, font=('Arial', 10))
        scrollbar_species = tk.Scrollbar(list_frame, orient=tk.VERTICAL)

        self.species_listbox.config(yscrollcommand=scrollbar_species.set)
        scrollbar_species.config(command=self.species_listbox.yview)

        self.species_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_species.pack(side=tk.RIGHT, fill=tk.Y)

        # 按钮
        btn_frame = tk.Frame(species_frame)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="刷新物种列表", command=self.refresh_species_list).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="选择推荐物种", command=self.select_recommended_species).pack(side=tk.LEFT, padx=5)

    def create_env_tab(self):
        """创建环境变量选择标签页"""
        env_frame = ttk.Frame(self.notebook)
        self.notebook.add(env_frame, text="3. 环境变量")

        tk.Label(env_frame, text="选择环境变量", font=('Arial', 12, 'bold')).pack(pady=10)

        # 环境变量复选框区域
        self.env_frame = tk.Frame(env_frame)
        self.env_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 按钮
        tk.Button(env_frame, text="刷新环境变量", command=self.refresh_env_vars).pack(pady=10)

    def create_process_tab(self):
        """创建数据处理标签页"""
        process_frame = ttk.Frame(self.notebook)
        self.notebook.add(process_frame, text="4. 处理数据")

        tk.Label(process_frame, text="数据处理选项", font=('Arial', 12, 'bold')).pack(pady=10)

        # 处理选项
        options_frame = tk.LabelFrame(process_frame, text="处理选项", font=('Arial', 11))
        options_frame.pack(fill=tk.X, padx=20, pady=10)

        self.remove_duplicates = tk.BooleanVar(value=True)
        self.remove_na = tk.BooleanVar(value=True)

        tk.Checkbutton(options_frame, text="移除重复记录", variable=self.remove_duplicates).pack(anchor='w', padx=10,
                                                                                                 pady=5)
        tk.Checkbutton(options_frame, text="移除缺失值", variable=self.remove_na).pack(anchor='w', padx=10, pady=5)

        # 处理按钮
        tk.Button(process_frame, text="开始处理数据", font=('Arial', 12, 'bold'),
                  bg='#f39c12', fg='white', command=self.process_data).pack(pady=20)

        # 结果显示
        self.process_result = tk.Text(process_frame, height=15, font=('Courier', 10))
        self.process_result.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def create_export_tab(self):
        """创建导出标签页"""
        export_frame = ttk.Frame(self.notebook)
        self.notebook.add(export_frame, text="5. 导出文件")

        tk.Label(export_frame, text="导出MaxEnt文件", font=('Arial', 12, 'bold')).pack(pady=10)

        # 输出目录选择
        dir_frame = tk.LabelFrame(export_frame, text="输出目录", font=('Arial', 11))
        dir_frame.pack(fill=tk.X, padx=20, pady=10)

        self.output_dir = tk.StringVar(value=os.getcwd())

        path_frame2 = tk.Frame(dir_frame)
        path_frame2.pack(fill=tk.X, padx=10, pady=10)

        tk.Entry(path_frame2, textvariable=self.output_dir, font=('Arial', 10)).pack(side=tk.LEFT, fill=tk.X,
                                                                                     expand=True)
        tk.Button(path_frame2, text="选择目录", command=self.browse_output_dir).pack(side=tk.RIGHT, padx=(5, 0))

        # 导出按钮
        tk.Button(export_frame, text="生成MaxEnt文件", font=('Arial', 12, 'bold'),
                  bg='#27ae60', fg='white', command=self.export_files).pack(pady=20)

        # 导出结果
        self.export_result = tk.Text(export_frame, height=10, font=('Courier', 10))
        self.export_result.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def browse_file(self):
        """浏览文件"""
        filename = filedialog.askopenfilename(
            title="选择CSV文件",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.file_path.set(filename)

    def load_data(self):
        """加载数据"""
        if not self.file_path.get():
            messagebox.showwarning("警告", "请先选择数据文件！")
            return

        try:
            self.status_var.set("正在加载数据...")
            self.root.update()

            # 加载数据
            self.data = pd.read_csv(self.file_path.get())

            # 标准化列名
            if 'Ice density' in self.data.columns:
                self.data.rename(columns={'Ice density': 'Ice_density'}, inplace=True)

            # 显示数据信息
            self.info_text.delete(1.0, tk.END)

            info = f"""数据加载成功！

文件信息：
- 文件名: {os.path.basename(self.file_path.get())}
- 总记录数: {len(self.data)}
- 总列数: {len(self.data.columns)}

列名:
{', '.join(self.data.columns.tolist())}

数据预览（前5行）:
{self.data.head().to_string()}

基本统计:
{self.data.describe()}
"""

            self.info_text.insert(tk.END, info)

            # 自动刷新其他标签页
            self.refresh_species_list()
            self.refresh_env_vars()

            self.status_var.set(f"数据加载成功！共 {len(self.data)} 条记录")

            # 自动切换到下一个标签页
            self.notebook.select(1)

        except Exception as e:
            messagebox.showerror("错误", f"加载数据失败：\n{str(e)}")
            self.status_var.set("数据加载失败")

    def refresh_species_list(self):
        """刷新物种列表"""
        if self.data is None:
            return

        self.species_listbox.delete(0, tk.END)

        if 'Species' in self.data.columns:
            species_counts = self.data['Species'].value_counts()

            for species, count in species_counts.items():
                status = "✓" if count >= 20 else "⚠"
                self.species_listbox.insert(tk.END, f"{status} {species} (n={count})")

    def select_recommended_species(self):
        """选择推荐的物种（样本量≥20）"""
        if self.data is None:
            return

        self.species_listbox.selection_clear(0, tk.END)

        if 'Species' in self.data.columns:
            species_counts = self.data['Species'].value_counts()

            for i, (species, count) in enumerate(species_counts.items()):
                if count >= 20:
                    self.species_listbox.selection_set(i)

    def refresh_env_vars(self):
        """刷新环境变量列表"""
        if self.data is None:
            return

        # 清空现有的复选框
        for widget in self.env_frame.winfo_children():
            widget.destroy()

        self.env_vars = {}

        # 环境变量列表
        possible_env_vars = ['TempA', 'TempW', 'Salinity', 'O2Con', 'O2',
                             'Turbidity', 'CHL', 'CDOM', 'pH', 'WindSpeed2M',
                             'Humidity', 'Ice_density', 'Detph']

        available_vars = [var for var in possible_env_vars if var in self.data.columns]

        # 推荐变量
        recommended = ['TempW', 'Salinity', 'CHL', 'Ice_density', 'Detph']

        for var in available_vars:
            var_bool = tk.BooleanVar()
            if var in recommended:
                var_bool.set(True)

            # 计算完整性
            completeness = (self.data[var].notna().sum() / len(self.data)) * 100

            status = "✓ 推荐" if var in recommended else "○"

            cb = tk.Checkbutton(self.env_frame,
                                text=f"{status} {var} (完整性: {completeness:.1f}%)",
                                variable=var_bool, font=('Arial', 10))
            cb.pack(anchor='w', padx=10, pady=2)

            self.env_vars[var] = var_bool

    def process_data(self):
        """处理数据"""
        if self.data is None:
            messagebox.showwarning("警告", "请先加载数据！")
            return

        try:
            # 获取选择的物种
            selected_indices = self.species_listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("警告", "请先选择要分析的物种！")
                return

            # 获取物种名称
            selected_species = []
            if 'Species' in self.data.columns:
                species_list = self.data['Species'].value_counts().index.tolist()
                selected_species = [species_list[i] for i in selected_indices]

            # 获取选择的环境变量
            selected_env_vars = [var for var, bool_var in self.env_vars.items() if bool_var.get()]

            if not selected_env_vars:
                messagebox.showwarning("警告", "请先选择环境变量！")
                return

            self.status_var.set("正在处理数据...")
            self.root.update()

            # 筛选数据
            columns_to_keep = ['Species', 'LONG', 'LAT'] + selected_env_vars
            self.processed_data = self.data[self.data['Species'].isin(selected_species)][columns_to_keep].copy()

            initial_count = len(self.processed_data)

            # 处理选项
            if self.remove_duplicates.get():
                before_dup = len(self.processed_data)
                self.processed_data = self.processed_data.drop_duplicates()
                removed_dups = before_dup - len(self.processed_data)
            else:
                removed_dups = 0

            if self.remove_na.get():
                before_na = len(self.processed_data)
                self.processed_data = self.processed_data.dropna()
                removed_na = before_na - len(self.processed_data)
            else:
                removed_na = 0

            final_count = len(self.processed_data)

            # 显示处理结果
            self.process_result.delete(1.0, tk.END)

            result_text = f"""数据处理完成！

处理统计:
- 初始记录数: {initial_count}
- 移除重复: {removed_dups} 条
- 移除缺失值: {removed_na} 条
- 最终记录数: {final_count}
- 数据保留率: {(final_count / initial_count) * 100:.1f}%

包含内容:
- 物种数: {len(selected_species)}
- 环境变量数: {len(selected_env_vars)}
- 唯一位置数: {len(self.processed_data[['LONG', 'LAT']].drop_duplicates())}

选择的物种:
{chr(10).join([f"- {sp}: {len(self.processed_data[self.processed_data['Species'] == sp])} 条记录" for sp in selected_species])}

选择的环境变量:
{chr(10).join([f"- {var}" for var in selected_env_vars])}

处理后数据预览:
{self.processed_data.head().to_string()}
"""

            self.process_result.insert(tk.END, result_text)

            self.status_var.set(f"数据处理完成！{final_count} 条记录")

            # 自动切换到导出标签页
            self.notebook.select(4)

        except Exception as e:
            messagebox.showerror("错误", f"数据处理失败：\n{str(e)}")
            self.status_var.set("数据处理失败")

    def browse_output_dir(self):
        """选择输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_dir.set(directory)

    def export_files(self):
        """导出文件 - 同时生成SWD格式和传统格式"""
        if self.processed_data is None:
            messagebox.showwarning("警告", "请先处理数据！")
            return

        try:
            self.status_var.set("正在导出文件...")
            self.root.update()

            output_path = self.output_dir.get()
            if not os.path.exists(output_path):
                os.makedirs(output_path)

            self.export_result.delete(1.0, tk.END)
            exported_files = []

            # 获取选择的环境变量
            selected_env_vars = [var for var, bool_var in self.env_vars.items() if bool_var.get()]

            # 1. 导出物种分布文件 (同时生成SWD和传统格式)
            species_dir = os.path.join(output_path, "species_occurrence")
            if not os.path.exists(species_dir):
                os.makedirs(species_dir)

            unique_species = self.processed_data['Species'].unique()

            for species in unique_species:
                species_data = self.processed_data[self.processed_data['Species'] == species]

                # 安全文件名
                safe_name = "".join(c for c in species if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_name = safe_name.replace(' ', '_')

                # A. SWD格式：species, longitude, latitude, env_var1, env_var2, ...
                swd_data = pd.DataFrame({
                    'species': species_data['Species'],
                    'longitude': species_data['LONG'],
                    'latitude': species_data['LAT']
                })

                # 添加环境变量列
                for env_var in selected_env_vars:
                    swd_data[env_var] = species_data[env_var].values

                swd_filename = f"{safe_name}_swd.csv"
                swd_filepath = os.path.join(species_dir, swd_filename)
                swd_data.to_csv(swd_filepath, index=False)
                exported_files.append(f"species_occurrence/{swd_filename}")

                # B. 传统格式：仅 species, longitude, latitude
                coords_data = pd.DataFrame({
                    'species': species_data['Species'],
                    'longitude': species_data['LONG'],
                    'latitude': species_data['LAT']
                })

                coords_filename = f"{safe_name}_coords.csv"
                coords_filepath = os.path.join(species_dir, coords_filename)
                coords_data.to_csv(coords_filepath, index=False)
                exported_files.append(f"species_occurrence/{coords_filename}")

            # 2. 导出环境数据文件 (同时生成SWD和传统格式)
            env_dir = os.path.join(output_path, "environmental_layers")
            if not os.path.exists(env_dir):
                os.makedirs(env_dir)

            # 获取唯一的环境数据点
            env_data = self.processed_data[['LONG', 'LAT'] + selected_env_vars].drop_duplicates()

            # A. SWD格式背景数据
            env_swd = pd.DataFrame({
                'species': 'background',  # MaxEnt要求的背景标识
                'longitude': env_data['LONG'],
                'latitude': env_data['LAT']
            })

            # 添加环境变量
            for env_var in selected_env_vars:
                env_swd[env_var] = env_data[env_var].values

            env_swd_filepath = os.path.join(env_dir, "background_swd.csv")
            env_swd.to_csv(env_swd_filepath, index=False)
            exported_files.append("environmental_layers/background_swd.csv")

            # B. 传统格式环境数据
            env_traditional = env_data.rename(columns={'LONG': 'longitude', 'LAT': 'latitude'})
            env_traditional_filepath = os.path.join(env_dir, "environmental_data.csv")
            env_traditional.to_csv(env_traditional_filepath, index=False)
            exported_files.append("environmental_layers/environmental_data.csv")

            # C. 环境变量信息文件
            env_info_path = os.path.join(env_dir, "layers_info.txt")
            with open(env_info_path, 'w', encoding='utf-8') as f:
                f.write("MaxEnt环境图层信息\n")
                f.write("=" * 40 + "\n\n")
                f.write("环境变量列表：\n")
                for var in selected_env_vars:
                    min_val = self.processed_data[var].min()
                    max_val = self.processed_data[var].max()
                    mean_val = self.processed_data[var].mean()
                    f.write(f"\n{var}:\n")
                    f.write(f"  - 最小值: {min_val:.4f}\n")
                    f.write(f"  - 最大值: {max_val:.4f}\n")
                    f.write(f"  - 平均值: {mean_val:.4f}\n")
                    f.write(f"  - 数据类型: 连续变量\n")

            exported_files.append("environmental_layers/layers_info.txt")

            # 3. 导出背景点文件 (额外的背景数据)
            background_dir = os.path.join(output_path, "background_points")
            if not os.path.exists(background_dir):
                os.makedirs(background_dir)

            # 背景点：所有的环境数据点（不包含物种信息）
            background_data = env_data.rename(columns={'LONG': 'longitude', 'LAT': 'latitude'})

            bg_filepath = os.path.join(background_dir, "background_points.csv")
            background_data.to_csv(bg_filepath, index=False)
            exported_files.append("background_points/background_points.csv")

            # 只有坐标的背景点文件
            bg_coords = background_data[['longitude', 'latitude']]
            bg_coords_path = os.path.join(background_dir, "background_coords_only.csv")
            bg_coords.to_csv(bg_coords_path, index=False)
            exported_files.append("background_points/background_coords_only.csv")

            # 4. 导出MaxEnt使用说明
            readme_path = os.path.join(output_path, "README_MaxEnt.txt")
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write("MaxEnt 建模文件使用说明\n")
                f.write("=" * 50 + "\n\n")
                f.write("本文件夹包含以下MaxEnt建模所需文件：\n\n")

                f.write("1. species_occurrence/ - 物种分布文件\n")
                f.write("   *_swd.csv: SWD格式文件，包含物种名、坐标和环境变量\n")
                f.write("   *_coords.csv: 传统格式，仅包含物种名和坐标\n\n")

                f.write("2. environmental_layers/ - 环境图层数据\n")
                f.write("   background_swd.csv: SWD格式背景数据\n")
                f.write("   environmental_data.csv: 传统格式环境数据\n")
                f.write("   layers_info.txt: 环境变量的详细信息\n\n")

                f.write("3. background_points/ - 额外背景点数据\n")
                f.write("   background_points.csv: 包含环境变量的背景点\n")
                f.write("   background_coords_only.csv: 仅包含坐标的背景点\n\n")

                f.write("MaxEnt使用方法：\n\n")
                f.write("方法1 - 使用SWD格式（推荐，解决格式兼容问题）：\n")
                f.write("1. 启动MaxEnt软件\n")
                f.write("2. Samples: 选择 species_occurrence/*_swd.csv 文件\n")
                f.write("3. Environmental layers: 选择 environmental_layers/background_swd.csv\n")
                f.write("4. 设置输出目录并运行建模\n\n")

                f.write("方法2 - 使用传统格式：\n")
                f.write("1. Samples: 选择 species_occurrence/*_coords.csv 文件\n")
                f.write("2. Environmental layers: 选择 environmental_layers/environmental_data.csv\n")
                f.write("3. 设置输出目录并运行建模\n\n")

                f.write("重要提示：\n")
                f.write("- 如果使用SWD格式，样本和背景数据都必须是SWD格式！\n")
                f.write("- 如果出现'SWD format'错误，请使用SWD格式文件\n")
                f.write("- 推荐使用SWD格式以避免兼容性问题\n\n")

                f.write(f"数据概况：\n")
                f.write(f"- 处理时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"- 物种数: {len(self.processed_data['Species'].unique())}\n")
                f.write(f"- 总记录数: {len(self.processed_data)}\n")
                f.write(f"- 环境变量数: {len(selected_env_vars)}\n")
                f.write(f"- 唯一位置数: {len(self.processed_data[['LONG', 'LAT']].drop_duplicates())}\n")

            exported_files.append("README_MaxEnt.txt")

            # 5. 导出摘要报告
            summary_path = os.path.join(output_path, "data_summary.txt")

            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write("MaxEnt 数据处理摘要报告\n")
                f.write("=" * 40 + "\n\n")
                f.write(f"处理时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"总记录数: {len(self.processed_data)}\n")
                f.write(f"物种数: {len(self.processed_data['Species'].unique())}\n")
                f.write(f"环境变量数: {len(selected_env_vars)}\n")
                f.write(f"唯一位置数: {len(self.processed_data[['LONG', 'LAT']].drop_duplicates())}\n\n")

                f.write("物种分布统计:\n")
                for species, count in self.processed_data['Species'].value_counts().items():
                    f.write(f"  {species}: {count} 条记录\n")

                f.write(f"\n选择的环境变量:\n")
                for var in selected_env_vars:
                    min_val = self.processed_data[var].min()
                    max_val = self.processed_data[var].max()
                    completeness = (self.processed_data[var].notna().sum() / len(self.processed_data)) * 100
                    f.write(f"  {var}: 范围[{min_val:.2f}, {max_val:.2f}], 完整性{completeness:.1f}%\n")

            exported_files.append("data_summary.txt")

            # 显示导出结果
            result_text = f"""MaxEnt文件导出完成！

输出目录: {output_path}

导出的文件结构:
{chr(10).join([f"- {f}" for f in exported_files])}

总共导出: {len(exported_files)} 个文件

📂 文件说明:
species_occurrence/ (物种分布数据)
   ├── *_swd.csv     ← SWD格式(推荐使用)  
   └── *_coords.csv  ← 传统格式(备用)

environmental_layers/ (环境图层数据)
   ├── background_swd.csv      ← SWD格式背景数据
   ├── environmental_data.csv  ← 传统格式环境数据
   └── layers_info.txt         ← 环境变量信息

background_points/ (额外背景数据)
   ├── background_points.csv      ← 完整背景点
   └── background_coords_only.csv ← 仅坐标背景点

README_MaxEnt.txt ← 详细使用说明
data_summary.txt  ← 数据处理摘要

🎯 MaxEnt使用建议:
✅ 推荐使用SWD格式避免兼容性问题
   - Samples: *_swd.csv
   - Environmental layers: background_swd.csv

⚠️ 如果SWD格式有问题，使用传统格式:
   - Samples: *_coords.csv  
   - Environmental layers: environmental_data.csv

现在可以在MaxEnt中使用这些文件进行建模了！
"""

            self.export_result.insert(tk.END, result_text)

            self.status_var.set(f"MaxEnt文件导出完成！共 {len(exported_files)} 个文件")

            messagebox.showinfo("成功",
                                f"MaxEnt文件已成功导出到:\n{output_path}\n\n包含SWD和传统两种格式\n请查看README_MaxEnt.txt了解使用方法")

        except Exception as e:
            messagebox.showerror("错误", f"文件导出失败：\n{str(e)}")
            self.status_var.set("文件导出失败")


def main():
    """主函数"""
    try:
        root = tk.Tk()
        app = MaxEntGUI(root)

        def on_closing():
            if messagebox.askokcancel("退出", "确定要退出程序吗？"):
                root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()

    except Exception as e:
        print(f"程序启动失败: {e}")
        input("按回车键退出...")


if __name__ == "__main__":
    main()
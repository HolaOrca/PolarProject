#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MaxEnt ASC文件可视化工具
MaxEnt ASC File Visualization Tool

读取MaxEnt输出的.asc格式适生区文件，生成海洋学风格地图
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import threading


class ASCReader:
    """ASC文件读取器"""

    def __init__(self):
        self.data = None
        self.header = {}

    def read_asc_file(self, filepath):
        """读取ASC格式文件"""
        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()

            # 读取头信息
            header_lines = 6  # ASC文件前6行是头信息
            self.header = {}

            for i in range(header_lines):
                line = lines[i].strip()
                if line:
                    parts = line.split()
                    key = parts[0].lower()
                    value = float(parts[1]) if '.' in parts[1] else int(parts[1])
                    self.header[key] = value

            # 读取数据部分
            data_lines = lines[header_lines:]
            data = []

            for line in data_lines:
                line = line.strip()
                if line:
                    row = [float(x) for x in line.split()]
                    data.append(row)

            self.data = np.array(data)

            # 处理NODATA值
            nodata_value = self.header.get('nodata_value', -9999)
            self.data[self.data == nodata_value] = np.nan

            return True

        except Exception as e:
            print(f"读取ASC文件失败: {e}")
            return False

    def get_coordinates(self):
        """获取坐标信息"""
        if not self.header:
            return None, None

        ncols = int(self.header['ncols'])
        nrows = int(self.header['nrows'])
        xllcorner = self.header['xllcorner']
        yllcorner = self.header['yllcorner']
        cellsize = self.header['cellsize']

        # 生成经纬度坐标
        lons = np.arange(xllcorner, xllcorner + ncols * cellsize, cellsize)
        lats = np.arange(yllcorner, yllcorner + nrows * cellsize, cellsize)

        return lons, lats


class MaxEntVisualizer:
    """MaxEnt可视化器"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MaxEnt ASC文件可视化工具")
        self.root.geometry("600x500")

        self.asc_reader = ASCReader()
        self.current_file = None

        # 创建海洋学配色方案
        self.ocean_cmap = self._create_ocean_colormap()

        self._setup_gui()

    def _create_ocean_colormap(self):
        """创建海洋学配色方案"""
        colors = [
            '#000080',  # 深蓝
            '#0040FF',  # 蓝色
            '#0080FF',  # 浅蓝
            '#00FFFF',  # 青色
            '#40FF40',  # 绿色
            '#80FF00',  # 黄绿
            '#FFFF00',  # 黄色
            '#FF8000',  # 橙色
            '#FF4000',  # 红橙
            '#FF0000',  # 红色
        ]
        return LinearSegmentedColormap.from_list('ocean_habitat', colors, N=256)

    def _setup_gui(self):
        """设置图形用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 标题
        title_label = ttk.Label(main_frame, text="MaxEnt ASC文件可视化工具",
                                font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # 文件选择区域
        file_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="10")
        file_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))

        ttk.Button(file_frame, text="选择ASC文件",
                   command=self.select_file).grid(row=0, column=0, padx=(0, 10))

        self.file_label = ttk.Label(file_frame, text="未选择文件")
        self.file_label.grid(row=0, column=1, sticky=tk.W)

        # 文件信息区域
        info_frame = ttk.LabelFrame(main_frame, text="文件信息", padding="10")
        info_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))

        self.info_text = tk.Text(info_frame, height=8, width=70, state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=scrollbar.set)

        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 可视化选项
        options_frame = ttk.LabelFrame(main_frame, text="可视化选项", padding="10")
        options_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))

        # 配色方案选择
        ttk.Label(options_frame, text="配色方案:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.colormap_var = tk.StringVar(value="海洋学风格")
        colormap_combo = ttk.Combobox(options_frame, textvariable=self.colormap_var,
                                      values=["海洋学风格", "经典彩虹", "蓝绿色系", "红黄色系"],
                                      state="readonly", width=15)
        colormap_combo.grid(row=0, column=1, padx=(0, 20))

        # 分辨率选择
        ttk.Label(options_frame, text="图片分辨率:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.dpi_var = tk.StringVar(value="300")
        dpi_combo = ttk.Combobox(options_frame, textvariable=self.dpi_var,
                                 values=["150", "300", "600"], state="readonly", width=8)
        dpi_combo.grid(row=0, column=3)

        # 显示等值线
        self.show_contours_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="显示等值线",
                        variable=self.show_contours_var).grid(row=1, column=0, sticky=tk.W, pady=(10, 0))

        # 显示数据范围
        self.show_colorbar_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="显示色标",
                        variable=self.show_colorbar_var).grid(row=1, column=1, sticky=tk.W, pady=(10, 0))

        # 操作按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)

        self.visualize_button = ttk.Button(button_frame, text="生成可视化",
                                           command=self.visualize_threaded, state=tk.DISABLED)
        self.visualize_button.grid(row=0, column=0, padx=(0, 10))

        ttk.Button(button_frame, text="退出",
                   command=self.root.quit).grid(row=0, column=1)

        # 进度条
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

        # 状态栏
        self.status_label = ttk.Label(main_frame, text="就绪")
        self.status_label.grid(row=6, column=0, columnspan=2, pady=(10, 0))

    def select_file(self):
        """选择ASC文件"""
        filetypes = [
            ('ASC files', '*.asc'),
            ('All files', '*.*')
        ]

        filename = filedialog.askopenfilename(
            title="选择MaxEnt ASC文件",
            filetypes=filetypes
        )

        if filename:
            self.current_file = filename
            self.file_label.config(text=os.path.basename(filename))

            # 读取文件信息
            if self.asc_reader.read_asc_file(filename):
                self._display_file_info()
                self.visualize_button.config(state=tk.NORMAL)
                self.status_label.config(text="文件加载成功")
            else:
                messagebox.showerror("错误", "无法读取ASC文件")
                self.status_label.config(text="文件加载失败")

    def _display_file_info(self):
        """显示文件信息"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)

        info_lines = []
        info_lines.append(f"文件路径: {self.current_file}")
        info_lines.append("\n头信息:")

        for key, value in self.asc_reader.header.items():
            info_lines.append(f"  {key}: {value}")

        if self.asc_reader.data is not None:
            data = self.asc_reader.data
            info_lines.append(f"\n数据信息:")
            info_lines.append(f"  数据形状: {data.shape}")
            info_lines.append(f"  数据范围: {np.nanmin(data):.4f} - {np.nanmax(data):.4f}")
            info_lines.append(f"  平均值: {np.nanmean(data):.4f}")
            info_lines.append(f"  标准差: {np.nanstd(data):.4f}")

            valid_pixels = np.sum(~np.isnan(data))
            total_pixels = data.size
            info_lines.append(f"  有效像素: {valid_pixels}/{total_pixels} ({valid_pixels / total_pixels * 100:.1f}%)")

        self.info_text.insert(tk.END, "\n".join(info_lines))
        self.info_text.config(state=tk.DISABLED)

    def visualize_threaded(self):
        """在线程中运行可视化（避免界面卡顿）"""
        self.progress.start()
        self.visualize_button.config(state=tk.DISABLED)
        self.status_label.config(text="正在生成可视化...")

        thread = threading.Thread(target=self.visualize)
        thread.start()

    def visualize(self):
        """生成可视化"""
        try:
            # 获取坐标
            lons, lats = self.asc_reader.get_coordinates()
            data = self.asc_reader.data

            # 创建坐标网格
            lon_mesh, lat_mesh = np.meshgrid(lons, lats[::-1])  # 翻转纬度以匹配数据

            # 选择配色方案
            colormap_name = self.colormap_var.get()
            if colormap_name == "海洋学风格":
                cmap = self.ocean_cmap
            elif colormap_name == "经典彩虹":
                cmap = plt.cm.jet
            elif colormap_name == "蓝绿色系":
                cmap = plt.cm.viridis
            else:  # 红黄色系
                cmap = plt.cm.YlOrRd

            # 创建图形
            fig, ax = plt.subplots(figsize=(14, 10))

            # 绘制等值线填充
            levels = np.linspace(np.nanmin(data), np.nanmax(data), 20)
            contourf = ax.contourf(lon_mesh, lat_mesh, data,
                                   levels=levels, cmap=cmap, extend='both')

            # 添加等值线（如果选择）
            if self.show_contours_var.get():
                key_levels = np.linspace(np.nanmin(data), np.nanmax(data), 6)[1:-1]  # 排除最大最小值
                contours = ax.contour(lon_mesh, lat_mesh, data,
                                      levels=key_levels, colors='black',
                                      linewidths=0.5, alpha=0.6)
                ax.clabel(contours, inline=True, fontsize=8, fmt='%.3f')

            # 设置坐标轴
            ax.set_xlabel('经度 (°E)', fontsize=12, fontweight='bold')
            ax.set_ylabel('纬度 (°N)', fontsize=12, fontweight='bold')

            # 设置标题
            filename = os.path.basename(self.current_file)
            species_name = filename.replace('.asc', '').replace('_', ' ')
            ax.set_title(f'{species_name}\n栖息地适宜性分布', fontsize=14, fontweight='bold')

            # 添加网格
            ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)

            # 添加色标（如果选择）
            if self.show_colorbar_var.get():
                cbar = plt.colorbar(contourf, ax=ax, shrink=0.8, aspect=25, pad=0.02)
                cbar.set_label('适宜性指数', fontsize=11, fontweight='bold')
                cbar.ax.tick_params(labelsize=10)

            # 设置坐标轴格式
            ax.tick_params(axis='both', which='major', labelsize=10)

            plt.tight_layout()

            # 保存图片
            output_filename = f"maxent_visualization_{species_name.replace(' ', '_')}.png"
            dpi = int(self.dpi_var.get())
            plt.savefig(output_filename, dpi=dpi, bbox_inches='tight', facecolor='white')

            # 显示图片
            plt.show()

            # 更新状态
            self.root.after(0, lambda: self._visualization_complete(output_filename))

        except Exception as e:
            self.root.after(0, lambda: self._visualization_error(str(e)))

    def _visualization_complete(self, filename):
        """可视化完成后的回调"""
        self.progress.stop()
        self.visualize_button.config(state=tk.NORMAL)
        self.status_label.config(text=f"可视化完成，已保存: {filename}")
        messagebox.showinfo("完成", f"可视化图片已保存为:\n{filename}")

    def _visualization_error(self, error_msg):
        """可视化出错后的回调"""
        self.progress.stop()
        self.visualize_button.config(state=tk.NORMAL)
        self.status_label.config(text="可视化失败")
        messagebox.showerror("错误", f"生成可视化时出错:\n{error_msg}")

    def run(self):
        """运行GUI"""
        self.root.mainloop()


def main():
    """主函数"""
    app = MaxEntVisualizer()
    app.run()


if __name__ == "__main__":
    main()
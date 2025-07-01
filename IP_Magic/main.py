import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import ip_converter
import cidr_calculator
import vlsm_calculator
import settings_manager
import re

class IP_Magic_Tool:
    def __init__(self, root):
        self.root = root
        self.root.title("IP Magic Tool")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # 加载设置
        self.settings = settings_manager.load_settings()
        self.auto_copy = tk.BooleanVar(value=self.settings.get('auto_copy', False))

        # 创建UI
        self.create_widgets()

        # 绑定事件
        self.ip_input.bind('<KeyRelease>', self.on_ip_input_change)
        self.subnet_input.bind('<KeyRelease>', self.on_subnet_input_change)

    def create_widgets(self):
        # 上部：IP地址输入
        input_frame = ttk.LabelFrame(self.root, text="输入IP地址")
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(input_frame, text="IP地址:").pack(side=tk.LEFT, padx=5)
        self.ip_input = ttk.Entry(input_frame, width=80)
        self.ip_input.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # 下部：结果显示区域
        result_frame = ttk.Frame(self.root)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 配置列权重，实现平均分配宽度
        result_frame.grid_columnconfigure(0, weight=1)
        result_frame.grid_columnconfigure(1, weight=1)
        result_frame.grid_columnconfigure(2, weight=1)
        result_frame.grid_rowconfigure(0, weight=1)

        # 左侧：二进制转换结果
        self.bin_frame = ttk.LabelFrame(result_frame, text="二进制结果:")
        self.bin_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.bin_result = scrolledtext.ScrolledText(self.bin_frame, wrap=tk.WORD)
        self.bin_result.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 中间：CIDR计算结果
        self.cidr_frame = ttk.LabelFrame(result_frame, text="CIDR计算结果:")
        self.cidr_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.cidr_result = scrolledtext.ScrolledText(self.cidr_frame, wrap=tk.WORD)
        self.cidr_result.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 右侧：VLSM计算区域
        vlsm_frame = ttk.LabelFrame(result_frame, text="VLSM计算")
        vlsm_frame.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)

        # VLSM子网掩码输入
        ttk.Label(vlsm_frame, text="子网掩码:").pack(anchor=tk.W, padx=5, pady=2)
        self.subnet_input = ttk.Entry(vlsm_frame, width=20)
        self.subnet_input.pack(anchor=tk.W, padx=5, pady=2)

        # VLSM结果
        ttk.Label(vlsm_frame, text="VLSM结果:").pack(anchor=tk.W, padx=5, pady=2)
        self.vlsm_result = scrolledtext.ScrolledText(vlsm_frame, wrap=tk.WORD, height=8)
        self.vlsm_result.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)

        # VLSM更多结果按钮
        self.more_vlsm_btn = ttk.Button(vlsm_frame, text="显示更多结果", command=self.show_more_vlsm)
        self.more_vlsm_btn.pack(anchor=tk.E, padx=5, pady=5)

        # 自动复制复选框
        self.auto_copy_check = ttk.Checkbutton(self.root, text="自动复制结果到剪贴板",
                                              variable=self.auto_copy, command=self.on_auto_copy_toggle)
        self.auto_copy_check.pack(anchor=tk.W, padx=10, pady=5)

    def on_ip_input_change(self, event=None):
        ip_text = self.ip_input.get().strip()
        if not ip_text:
            self.clear_results()
            return

        # 解析多个IP地址（支持空格、逗号分隔）
        ip_addresses = re.split(r'[ ,，]+', ip_text)
        valid_ips = [ip for ip in ip_addresses if ip_converter.is_valid_ip(ip)]

        # 处理IP转换
        bin_results = []
        for ip in valid_ips:
            bin_ip = ip_converter.ip_to_binary(ip)
            bin_results.append(f"IP: {ip}\n二进制: {bin_ip}\n")
        self.bin_result.delete(1.0, tk.END)
        self.bin_result.insert(tk.END, '\n'.join(bin_results))

        # 处理CIDR计算
        cidr_results = []
        for ip in valid_ips:
            cidr_info = cidr_calculator.calculate_cidr(ip)
            cidr_results.append(f"IP: {ip}\n{cidr_info}\n")
        self.cidr_result.delete(1.0, tk.END)
        self.cidr_result.insert(tk.END, '\n'.join(cidr_results))

        # 触发VLSM计算
        self.on_subnet_input_change()

        # 自动复制
        if self.auto_copy.get():
            self.copy_results_to_clipboard()

    def on_subnet_input_change(self, event=None):
        ip_text = self.ip_input.get().strip()
        subnet_text = self.subnet_input.get().strip()

        if not ip_text or not subnet_text:
            self.vlsm_result.delete(1.0, tk.END)
            return

        # 解析多个IP地址
        ip_addresses = re.split(r'[ ,，]+', ip_text)
        valid_ips = [ip for ip in ip_addresses if ip_converter.is_valid_ip(ip)]

        # 处理VLSM计算
        vlsm_results = []
        self.all_vlsm_results = []
        for ip in valid_ips:
            try:
                results = vlsm_calculator.calculate_vlsm(ip, subnet_text)
                self.all_vlsm_results.extend(results)
                # 只显示前5个结果
                display_results = results[:5]
                for i, res in enumerate(display_results):
                    vlsm_results.append(f"子网 {i+1}:")
                    vlsm_results.append(f"网络地址: {res['network']}")
                    vlsm_results.append(f"广播地址: {res['broadcast']}")
                    vlsm_results.append(f"子网掩码: {res['mask']}")
                    vlsm_results.append(f"主机数量/范围: {res['host_range']}\n")
                # 如果有更多结果，提示用户
                if len(results) > 5:
                    vlsm_results.append(f"... 还有 {len(results)-5} 个子网结果未显示 ...\n")
            except Exception as e:
                vlsm_results.append(f"VLSM计算错误: {str(e)}\n")

        self.vlsm_result.delete(1.0, tk.END)
        self.vlsm_result.insert(tk.END, '\n'.join(vlsm_results))

    def show_more_vlsm(self):
        if not hasattr(self, 'all_vlsm_results') or not self.all_vlsm_results:
            messagebox.showinfo("提示", "没有VLSM结果可显示")
            return

        # 创建新窗口显示完整VLSM结果表格
        top = tk.Toplevel(self.root)
        top.title("完整VLSM计算结果")
        top.geometry("800x400")

        # 创建表格
        tree = ttk.Treeview(top, columns=('network', 'broadcast', 'mask', 'host_range'), show='headings')
        tree.heading('network', text='网络地址')
        tree.heading('broadcast', text='广播地址')
        tree.heading('mask', text='子网掩码')
        tree.heading('host_range', text='主机数量/范围')

        tree.column('network', width=150)
        tree.column('broadcast', width=150)
        tree.column('mask', width=100)
        tree.column('host_range', width=200)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(top, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 填充数据
        for i, res in enumerate(self.all_vlsm_results):
            tree.insert('', tk.END, values=(res['network'], res['broadcast'], res['mask'], res['host_range']))

    def clear_results(self):
        self.bin_result.delete(1.0, tk.END)
        self.cidr_result.delete(1.0, tk.END)
        self.vlsm_result.delete(1.0, tk.END)

    def on_auto_copy_toggle(self):
        self.settings['auto_copy'] = self.auto_copy.get()
        settings_manager.save_settings(self.settings)
        if self.auto_copy.get():
            self.copy_results_to_clipboard()

    def copy_results_to_clipboard(self):
        # 复制所有结果到剪贴板
        results = f"二进制结果:\n{self.bin_result.get(1.0, tk.END)}\n"
        results += f"CIDR计算结果:\n{self.cidr_result.get(1.0, tk.END)}\n"
        results += f"VLSM计算结果:\n{self.vlsm_result.get(1.0, tk.END)}"
        self.root.clipboard_clear()
        self.root.clipboard_append(results)

if __name__ == "__main__":
    root = tk.Tk()
    app = IP_Magic_Tool(root)
    root.mainloop()
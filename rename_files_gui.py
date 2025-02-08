import os
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk


class FileRenamerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("文件批量重命名工具")
        self.root.geometry("800x600")  # 增加默认窗口大小
        
        # 使主窗口可调整大小
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # 文件夹选择区域
        folder_frame = ttk.Frame(main_frame)
        folder_frame.grid(row=0, column=0, sticky="ew", pady=5)
        
        self.folder_path = tk.StringVar()
        folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_path)
        folder_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        browse_btn = ttk.Button(folder_frame, text="选择文件夹", command=self.browse_folder)
        browse_btn.grid(row=0, column=1)
        
        folder_frame.grid_columnconfigure(0, weight=1)
        
        # 命名模式区域
        pattern_frame = ttk.LabelFrame(main_frame, text="命名设置", padding="5")
        pattern_frame.grid(row=1, column=0, sticky="ew", pady=5)
        
        # 文件名模式输入
        pattern_input_frame = ttk.Frame(pattern_frame)
        pattern_input_frame.grid(row=0, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        
        ttk.Label(pattern_input_frame, text="文件名模式:").grid(row=0, column=0, padx=(0,5))
        self.pattern = tk.StringVar(value="file_{:03d}")
        pattern_entry = ttk.Entry(pattern_input_frame, textvariable=self.pattern)
        pattern_entry.grid(row=0, column=1, sticky="ew", padx=5)
        
        ttk.Label(pattern_input_frame, text="起始编号:").grid(row=0, column=2, padx=5)
        self.start_num = tk.StringVar(value="1")
        start_num_entry = ttk.Entry(pattern_input_frame, textvariable=self.start_num, width=8)
        start_num_entry.grid(row=0, column=3, padx=(0,5))
        
        pattern_input_frame.grid_columnconfigure(1, weight=1)
        
        # 帮助信息
        help_frame = ttk.Frame(pattern_frame)
        help_frame.grid(row=1, column=0, columnspan=4, sticky="ew", padx=5)
        
        help_text = (
            "文件名规则:\n"
            "1. 直接输入文件名，将自动添加序号\n"
            "   例如: 'photo' → photo1, photo2, ...\n"
            "2. 使用格式化选项自定义序号格式:\n"
            "   - {: d}  → 1, 2, 3, ...\n"
            "   - {:02d} → 01, 02, 03, ...\n"
            "   - {:03d} → 001, 002, 003, ...\n"
            "   例如: 'photo_{:03d}' → photo_001, photo_002, ..."
        )
        help_label = ttk.Label(help_frame, text=help_text, justify="left")
        help_label.grid(row=0, column=0, sticky="w")
        
        # 预览区域
        preview_frame = ttk.LabelFrame(main_frame, text="预览", padding="5")
        preview_frame.grid(row=2, column=0, sticky="nsew", pady=5)
        
        # 创建预览列表
        self.preview_tree = ttk.Treeview(preview_frame, columns=("原文件名", "新文件名"), show="headings")
        self.preview_tree.heading("原文件名", text="原文件名")
        self.preview_tree.heading("新文件名", text="新文件名")
        self.preview_tree.grid(row=0, column=0, sticky="nsew")
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.preview_tree.configure(yscrollcommand=scrollbar.set)
        
        preview_frame.grid_columnconfigure(0, weight=1)
        preview_frame.grid_rowconfigure(0, weight=1)
        
        # 按钮区域
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, sticky="ew", pady=5)
        
        preview_btn = ttk.Button(btn_frame, text="预览", command=self.preview_rename)
        preview_btn.pack(side=tk.LEFT, padx=5)
        
        execute_btn = ttk.Button(btn_frame, text="执行重命名", command=self.execute_rename)
        execute_btn.pack(side=tk.LEFT, padx=5)
        
        # 配置主框架的网格权重
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(2, weight=1)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)
            self.preview_rename()

    def get_new_filename(self, index, ext):
        try:
            # 验证起始编号
            try:
                start_num = int(self.start_num.get())
                if start_num < 0:
                    raise ValueError("起始编号不能为负数")
            except ValueError as e:
                messagebox.showerror("错误", f"起始编号无效: {str(e)}")
                return None

            # 获取用户输入的文件名模式
            pattern = self.pattern.get().strip()
            if not pattern:
                messagebox.showerror("错误", "文件名不能为空")
                return None

            # 处理文件名
            try:
                # 检查是否包含格式化占位符
                if '{' in pattern and '}' in pattern:
                    new_name = pattern.format(index + start_num - 1)
                else:
                    # 如果没有格式化占位符，在文件名后添加数字
                    new_name = f"{pattern}{index + start_num - 1}"
            except Exception as e:
                messagebox.showerror("错误", f"文件名格式错误: {str(e)}")
                return None

            # 验证生成的文件名是否合法
            if not self.is_valid_filename(new_name):
                messagebox.showerror("错误", "生成的文件名包含非法字符")
                return None

            return new_name + ext

        except Exception as e:
            messagebox.showerror("错误", f"生成文件名时出错: {str(e)}")
            return None

    def is_valid_filename(self, filename):
        # 检查文件名是否包含非法字符
        invalid_chars = '<>:"/\\|?*'
        return not any(char in filename for char in invalid_chars)

    def preview_rename(self):
        folder = self.folder_path.get()
        if not folder:
            messagebox.showwarning("警告", "请先选择文件夹！")
            return
            
        # 清空预览列表
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
            
        try:
            # 获取文件列表
            files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
            files.sort()
            
            # 检查潜在冲突
            new_names = set()
            for index, filename in enumerate(files):
                _, ext = os.path.splitext(filename)
                new_filename = self.get_new_filename(index + 1, ext)
                if not new_filename:
                    return
                
                if new_filename in new_names:
                    messagebox.showerror("错误", f"检测到文件名冲突：{new_filename}")
                    return
                new_names.add(new_filename)
            
            # 显示预览
            for index, filename in enumerate(files):
                _, ext = os.path.splitext(filename)
                new_filename = self.get_new_filename(index + 1, ext)
                self.preview_tree.insert("", tk.END, values=(filename, new_filename))
                
        except Exception as e:
            messagebox.showerror("错误", f"预览时出错：{str(e)}")

    def execute_rename(self):
        folder = self.folder_path.get()
        if not folder:
            messagebox.showwarning("警告", "请先选择文件夹！")
            return
            
        if not self.preview_tree.get_children():
            messagebox.showwarning("警告", "请先预览更改！")
            return
            
        if not messagebox.askyesno("确认", "确定要执行重命名操作吗？此操作不可撤销！"):
            return
            
        try:
            files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
            files.sort()
            
            for index, filename in enumerate(files):
                _, ext = os.path.splitext(filename)
                new_filename = self.get_new_filename(index + 1, ext)
                
                src = os.path.join(folder, filename)
                dst = os.path.join(folder, new_filename)
                
                if os.path.exists(dst) and src.lower() != dst.lower():
                    messagebox.showerror("错误", f"目标文件已存在：'{dst}'")
                    return
                    
                os.rename(src, dst)
            
            messagebox.showinfo("成功", "文件重命名完成！")
            self.preview_rename()  # 刷新预览
            
        except Exception as e:
            messagebox.showerror("错误", f"重命名时出错：{str(e)}")

def main():
    root = tk.Tk()
    app = FileRenamerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 
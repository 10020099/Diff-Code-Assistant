import os
import glob
import difflib
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import pyperclip


def scan_directory(root, exclude_patterns):
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        if any(glob.fnmatch.fnmatch(rel_dir, pat) for pat in exclude_patterns):
            continue
        for filename in filenames:
            relpath = os.path.relpath(os.path.join(dirpath, filename), root)
            if any(glob.fnmatch.fnmatch(relpath, pat) for pat in exclude_patterns):
                continue
            files.append(os.path.join(dirpath, filename))
    return files


def build_tree(paths, root):
    tree = ''
    sorted_paths = sorted([os.path.relpath(p, root) for p in paths])
    prev_parts = []
    for rel in sorted_paths:
        parts = rel.split(os.sep)
        for i, part in enumerate(parts):
            prefix = '    ' * i
            if prev_parts[:i+1] != parts[:i+1]:
                tree += f"{prefix}{part}\n"
        prev_parts = parts
    return tree


def generate_context_from_paths(paths, root):
    tree_str = build_tree(paths, root)
    ctx = f"*#*#*begin TREE*#*#*\n{tree_str}*#*#*end TREE*#*#*\n"
    for path in paths:
        rel = os.path.relpath(path, root)
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                data = f.read()
        except Exception as e:
            data = f"<Failed to read file: {e}>"
        ctx += f"*#*#*begin FILE {rel}*#*#*\n{data}\n*#*#*end FILE {rel}*#*#*\n\n"
    return ctx


class ShotgunApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Diff Code Assistant")
        self.geometry("900x700")
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both", padx=10, pady=10)
        for step in ["Step1", "Step2", "Step3", "Step4"]:
            self.tabview.add(step)
        
        # Step1: 可勾选文件树
        f1 = self.tabview.tab("Step1")
        self.folder_entry = ctk.CTkEntry(f1, placeholder_text="项目文件夹路径")
        self.folder_entry.pack(fill="x", padx=5, pady=5)
        self.browse_btn = ctk.CTkButton(f1, text="浏览", command=self.browse_folder)
        self.browse_btn.pack(padx=5, pady=5)
        self.load_tree_btn = ctk.CTkButton(f1, text="加载文件树", command=self.load_tree)
        self.load_tree_btn.pack(padx=5, pady=5)
        self.tree_frame = ctk.CTkScrollableFrame(f1, height=300)
        self.tree_frame.pack(expand=True, fill="both", padx=5, pady=5)
        self.gen_ctx_btn = ctk.CTkButton(f1, text="准备上下文", command=self.do_step1)
        self.gen_ctx_btn.pack(padx=5, pady=5)
        self.context_box = ctk.CTkTextbox(f1, wrap="none")
        self.context_box.pack(expand=True, fill="both", padx=5, pady=5)
        
        # Step2: 生成提示并复制
        f2 = self.tabview.tab("Step2")
        self.prompt_entry = ctk.CTkEntry(f2, placeholder_text="输入对LLM的指令")
        self.prompt_entry.pack(fill="x", padx=5, pady=5)
        self.step2_btn = ctk.CTkButton(f2, text="生成提示", command=self.do_step2)
        self.step2_btn.pack(padx=5, pady=5)
        self.prompt_out_box = ctk.CTkTextbox(f2, wrap="none")
        self.prompt_out_box.pack(expand=True, fill="both", padx=5, pady=5)
        
        # Step3: 预览Diff差异
        f3 = self.tabview.tab("Step3")
        self.llm_diff_box = ctk.CTkTextbox(f3, wrap="none")
        self.llm_diff_box.pack(expand=True, fill="both", padx=5, pady=5)
        self.step3_btn = ctk.CTkButton(f3, text="预览Diff差异", command=self.do_step3)
        self.step3_btn.pack(padx=5, pady=5)
        # 预览框，支持行高亮
        self.preview_box = tk.Text(f3, wrap="none")
        self.preview_box.pack(expand=True, fill="both", padx=5, pady=5)
        self.preview_box.tag_config('add', foreground='green')
        self.preview_box.tag_config('del', foreground='red')
        
        # Step4: 生成应用补丁的 LLM 提示
        f4 = self.tabview.tab("Step4")
        self.step4_btn = ctk.CTkButton(f4, text="生成应用提示", command=self.do_step4)
        self.step4_btn.pack(padx=5, pady=5)
        self.apply_prompt_box = ctk.CTkTextbox(f4, wrap="none")
        self.apply_prompt_box.pack(expand=True, fill="both", padx=5, pady=5)
        
        self.all_paths = []
        self.check_vars = {}
        self.context = ""
        self.diff = ""
    
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_entry.delete(0, ctk.END)
            self.folder_entry.insert(0, folder)
    
    def load_tree(self):
        root = self.folder_entry.get()
        if not os.path.isdir(root):
            messagebox.showwarning("错误", "请选择有效文件夹")
            return
        for widget in self.tree_frame.winfo_children():
            widget.destroy()
        self.all_paths = scan_directory(root, [])
        rel_paths = sorted([os.path.relpath(p, root) for p in self.all_paths])
        self.check_vars = {}
        for rel in rel_paths:
            parts = rel.split(os.sep)
            indent = len(parts) - 1
            var = tk.BooleanVar(value=True)
            cb = ctk.CTkCheckBox(self.tree_frame, text=("    " * indent) + parts[-1], variable=var)
            cb.pack(anchor="w", padx=5, pady=1)
            self.check_vars[rel] = var
        messagebox.showinfo("加载完成", f"共加载 {len(rel_paths)} 个文件")
    
    def do_step1(self):
        root = self.folder_entry.get()
        if not self.check_vars:
            messagebox.showwarning("错误", "请先加载文件树")
            return
        include_paths = [os.path.join(root, rel) for rel, var in self.check_vars.items() if var.get()]
        self.context = generate_context_from_paths(include_paths, root)
        self.context_box.delete("0.0", ctk.END)
        self.context_box.insert("0.0", self.context)
        self.tabview.set("Step2")
    
    def do_step2(self):
        prompt_text = self.prompt_entry.get()
        full_prompt = f"{self.context}\n{prompt_text}"
        self.prompt_out_box.delete("0.0", ctk.END)
        self.prompt_out_box.insert("0.0", full_prompt)
        pyperclip.copy(full_prompt)
        messagebox.showinfo("提示已复制", "已复制完整提示到剪贴板，请在网页 LLM 对话框中粘贴并获取 diff 结果。")
        self.tabview.set("Step3")
    
    def do_step3(self):
        self.diff = self.llm_diff_box.get("0.0", "end").strip()
        # 清空预览框并高亮显示 diff
        self.preview_box.delete("1.0", "end")
        for line in self.diff.split('\n'):
            if line.startswith('+'):
                self.preview_box.insert('end', line + '\n', 'add')
            elif line.startswith('-'):
                self.preview_box.insert('end', line + '\n', 'del')
            else:
                self.preview_box.insert('end', line + '\n')
        # 前往 Step4
        self.tabview.set("Step4")
    
    def do_step4(self):
        # 生成用于让 LLM 根据 diff 应用补丁的提示，并复制到剪贴板
        prompt_text = f"请根据以下 diff 对项目文件进行应用：\n{self.diff}"
        self.apply_prompt_box.delete("0.0", ctk.END)
        self.apply_prompt_box.insert("0.0", prompt_text)
        pyperclip.copy(prompt_text)
        messagebox.showinfo("提示已复制", "已复制应用补丁的提示到剪贴板，请在网页 LLM 对话框中粘贴并获取更新后的代码。")
    
if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = ShotgunApp()
    app.mainloop() 
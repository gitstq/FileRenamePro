#!/usr/bin/env python3
"""
FileRenamePro - 图形用户界面

使用tkinter构建的跨平台GUI界面
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from typing import List, Optional
import threading

from renamer import FileRenamer, RenameRule, RenameMode


class FileListFrame(ttk.Frame):
    """文件列表框架"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.files: List[str] = []
        self._create_widgets()
    
    def _create_widgets(self):
        """创建界面组件"""
        # 标题
        ttk.Label(self, text="📁 文件列表", font=('Arial', 12, 'bold')).pack(anchor='w', pady=5)
        
        # 按钮框架
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', pady=5)
        
        ttk.Button(btn_frame, text="添加文件", command=self._add_files).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="添加目录", command=self._add_directory).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="清空", command=self._clear_files).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="移除选中", command=self._remove_selected).pack(side='left', padx=2)
        
        # 文件列表
        list_frame = ttk.Frame(self)
        list_frame.pack(fill='both', expand=True, pady=5)
        
        # 滚动条
        scrollbar_y = ttk.Scrollbar(list_frame)
        scrollbar_y.pack(side='right', fill='y')
        
        scrollbar_x = ttk.Scrollbar(list_frame, orient='horizontal')
        scrollbar_x.pack(side='bottom', fill='x')
        
        # 列表框
        self.listbox = tk.Listbox(
            list_frame,
            selectmode='extended',
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
            font=('Consolas', 10)
        )
        self.listbox.pack(side='left', fill='both', expand=True)
        
        scrollbar_y.config(command=self.listbox.yview)
        scrollbar_x.config(command=self.listbox.xview)
        
        # 计数标签
        self.count_label = ttk.Label(self, text="共 0 个文件")
        self.count_label.pack(anchor='w', pady=5)
    
    def _add_files(self):
        """添加文件"""
        files = filedialog.askopenfilenames(title="选择文件")
        for f in files:
            if f not in self.files:
                self.files.append(f)
                self.listbox.insert('end', os.path.basename(f))
        self._update_count()
    
    def _add_directory(self):
        """添加目录"""
        directory = filedialog.askdirectory(title="选择目录")
        if directory:
            for filename in os.listdir(directory):
                filepath = os.path.join(directory, filename)
                if os.path.isfile(filepath) and filepath not in self.files:
                    self.files.append(filepath)
                    self.listbox.insert('end', filename)
            self._update_count()
    
    def _clear_files(self):
        """清空文件列表"""
        self.files.clear()
        self.listbox.delete(0, 'end')
        self._update_count()
    
    def _remove_selected(self):
        """移除选中的文件"""
        selected = self.listbox.curselection()
        for index in reversed(selected):
            self.files.pop(index)
            self.listbox.delete(index)
        self._update_count()
    
    def _update_count(self):
        """更新计数"""
        self.count_label.config(text=f"共 {len(self.files)} 个文件")
    
    def get_files(self) -> List[str]:
        """获取文件列表"""
        return self.files.copy()


class RuleFrame(ttk.Frame):
    """规则配置框架"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._create_widgets()
    
    def _create_widgets(self):
        """创建界面组件"""
        # 标题
        ttk.Label(self, text="⚙️ 重命名规则", font=('Arial', 12, 'bold')).pack(anchor='w', pady=5)
        
        # 模式选择
        mode_frame = ttk.LabelFrame(self, text="重命名模式", padding=10)
        mode_frame.pack(fill='x', pady=5)
        
        self.mode_var = tk.StringVar(value='replace')
        modes = [
            ('replace', '简单替换'),
            ('regex', '正则表达式'),
            ('serial', '序号命名'),
            ('date', '日期命名'),
            ('hash', '文件哈希'),
            ('random', '随机字符串'),
            ('case', '大小写转换'),
            ('insert', '插入文本'),
        ]
        
        for val, text in modes:
            ttk.Radiobutton(
                mode_frame, text=text, value=val,
                variable=self.mode_var,
                command=self._on_mode_change
            ).pack(anchor='w', pady=2)
        
        # 参数配置
        self.params_frame = ttk.LabelFrame(self, text="参数配置", padding=10)
        self.params_frame.pack(fill='x', pady=5)
        
        # 动态参数控件
        self.param_widgets = {}
        self._create_param_widgets()
        
        # 预览和执行按钮
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', pady=10)
        
        ttk.Button(btn_frame, text="🔍 预览", command=self._preview).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="✅ 执行", command=self._execute).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="↩️ 撤销", command=self._undo).pack(side='left', padx=5)
        
        # 回调函数
        self.preview_callback = None
        self.execute_callback = None
        self.undo_callback = None
        
        # 初始化显示
        self._on_mode_change()
    
    def _create_param_widgets(self):
        """创建参数控件"""
        # 查找/替换
        self.param_widgets['find'] = self._create_labeled_entry("查找内容:")
        self.param_widgets['replace'] = self._create_labeled_entry("替换内容:")
        
        # 前缀/后缀
        self.param_widgets['prefix'] = self._create_labeled_entry("前缀:")
        self.param_widgets['suffix'] = self._create_labeled_entry("后缀:")
        
        # 序号参数
        self.param_widgets['start'] = self._create_labeled_entry("起始序号:", "1")
        self.param_widgets['step'] = self._create_labeled_entry("步长:", "1")
        self.param_widgets['digits'] = self._create_labeled_entry("序号位数:", "3")
        
        # 日期格式
        self.param_widgets['date_format'] = self._create_labeled_entry("日期格式:", "%Y%m%d")
        
        # 哈希参数
        self.param_widgets['hash_algo'] = self._create_labeled_combobox(
            "哈希算法:", ["md5", "sha1", "sha256"], "md5"
        )
        self.param_widgets['hash_length'] = self._create_labeled_entry("哈希长度:", "8")
        
        # 随机字符串长度
        self.param_widgets['random_length'] = self._create_labeled_entry("随机长度:", "8")
        
        # 大小写模式
        self.param_widgets['case_mode'] = self._create_labeled_combobox(
            "大小写模式:", ["lower", "upper", "title", "camel"], "lower"
        )
        
        # 插入参数
        self.param_widgets['insert_pos'] = self._create_labeled_entry("插入位置:", "0")
        self.param_widgets['insert_text'] = self._create_labeled_entry("插入文本:")
    
    def _create_labeled_entry(self, label: str, default: str = "") -> ttk.Entry:
        """创建带标签的输入框"""
        frame = ttk.Frame(self.params_frame)
        frame.pack(fill='x', pady=2)
        ttk.Label(frame, text=label, width=12).pack(side='left')
        entry = ttk.Entry(frame)
        entry.pack(side='left', fill='x', expand=True, padx=5)
        entry.insert(0, default)
        return entry
    
    def _create_labeled_combobox(self, label: str, values: List[str], 
                                  default: str = "") -> ttk.Combobox:
        """创建带标签的下拉框"""
        frame = ttk.Frame(self.params_frame)
        frame.pack(fill='x', pady=2)
        ttk.Label(frame, text=label, width=12).pack(side='left')
        combo = ttk.Combobox(frame, values=values, state='readonly')
        combo.pack(side='left', fill='x', expand=True, padx=5)
        combo.set(default)
        return combo
    
    def _on_mode_change(self):
        """模式改变时的处理"""
        mode = self.mode_var.get()
        
        # 隐藏所有参数控件
        for widget in self.param_widgets.values():
            widget.master.pack_forget()
        
        # 根据模式显示相应的控件
        if mode == 'replace':
            self.param_widgets['find'].master.pack(fill='x', pady=2)
            self.param_widgets['replace'].master.pack(fill='x', pady=2)
        
        elif mode == 'regex':
            self.param_widgets['find'].master.pack(fill='x', pady=2)
            self.param_widgets['replace'].master.pack(fill='x', pady=2)
        
        elif mode == 'serial':
            self.param_widgets['prefix'].master.pack(fill='x', pady=2)
            self.param_widgets['suffix'].master.pack(fill='x', pady=2)
            self.param_widgets['start'].master.pack(fill='x', pady=2)
            self.param_widgets['step'].master.pack(fill='x', pady=2)
            self.param_widgets['digits'].master.pack(fill='x', pady=2)
        
        elif mode == 'date':
            self.param_widgets['prefix'].master.pack(fill='x', pady=2)
            self.param_widgets['suffix'].master.pack(fill='x', pady=2)
            self.param_widgets['date_format'].master.pack(fill='x', pady=2)
        
        elif mode == 'hash':
            self.param_widgets['prefix'].master.pack(fill='x', pady=2)
            self.param_widgets['suffix'].master.pack(fill='x', pady=2)
            self.param_widgets['hash_algo'].master.pack(fill='x', pady=2)
            self.param_widgets['hash_length'].master.pack(fill='x', pady=2)
        
        elif mode == 'random':
            self.param_widgets['prefix'].master.pack(fill='x', pady=2)
            self.param_widgets['suffix'].master.pack(fill='x', pady=2)
            self.param_widgets['random_length'].master.pack(fill='x', pady=2)
        
        elif mode == 'case':
            self.param_widgets['case_mode'].master.pack(fill='x', pady=2)
        
        elif mode == 'insert':
            self.param_widgets['insert_pos'].master.pack(fill='x', pady=2)
            self.param_widgets['insert_text'].master.pack(fill='x', pady=2)
    
    def get_rule(self) -> RenameRule:
        """获取当前规则"""
        mode_map = {
            'replace': RenameMode.REPLACE,
            'regex': RenameMode.REGEX,
            'serial': RenameMode.SERIAL,
            'date': RenameMode.DATE,
            'hash': RenameMode.HASH,
            'random': RenameMode.RANDOM,
            'case': RenameMode.CASE,
            'insert': RenameMode.INSERT,
        }
        
        def get_value(key, default=""):
            widget = self.param_widgets.get(key)
            if widget:
                return widget.get() or default
            return default
        
        def get_int(key, default=0):
            try:
                return int(get_value(key, str(default)))
            except ValueError:
                return default
        
        return RenameRule(
            mode=mode_map.get(self.mode_var.get(), RenameMode.REPLACE),
            find=get_value('find'),
            replace=get_value('replace'),
            prefix=get_value('prefix'),
            suffix=get_value('suffix'),
            start_num=get_int('start', 1),
            step=get_int('step', 1),
            digits=get_int('digits', 3),
            date_format=get_value('date_format', '%Y%m%d'),
            hash_algo=get_value('hash_algo', 'md5'),
            hash_length=get_int('hash_length', 8),
            random_length=get_int('random_length', 8),
            case_mode=get_value('case_mode', 'lower'),
            insert_pos=get_int('insert_pos', 0),
            insert_text=get_value('insert_text'),
        )
    
    def _preview(self):
        """预览"""
        if self.preview_callback:
            self.preview_callback()
    
    def _execute(self):
        """执行"""
        if self.execute_callback:
            self.execute_callback()
    
    def _undo(self):
        """撤销"""
        if self.undo_callback:
            self.undo_callback()


class PreviewFrame(ttk.Frame):
    """预览框架"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._create_widgets()
    
    def _create_widgets(self):
        """创建界面组件"""
        # 标题
        ttk.Label(self, text="👁️ 预览", font=('Arial', 12, 'bold')).pack(anchor='w', pady=5)
        
        # 预览文本框
        self.text = scrolledtext.ScrolledText(
            self,
            wrap='none',
            font=('Consolas', 10),
            height=15
        )
        self.text.pack(fill='both', expand=True, pady=5)
        self.text.config(state='disabled')
    
    def clear(self):
        """清空预览"""
        self.text.config(state='normal')
        self.text.delete(1.0, 'end')
        self.text.config(state='disabled')
    
    def set_preview(self, results: List[tuple]):
        """设置预览内容"""
        self.clear()
        self.text.config(state='normal')
        
        self.text.insert('end', f"{'原文件名':<40} {'新文件名':<40}\n")
        self.text.insert('end', "=" * 80 + "\n")
        
        for old, new in results:
            old_display = (old[:37] + '...') if len(old) > 40 else old
            new_display = (new[:37] + '...') if len(new) > 40 else new
            self.text.insert('end', f"{old_display:<40} {new_display:<40}\n")
        
        self.text.config(state='disabled')


class FileRenameProGUI:
    """主GUI类"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FileRenamePro - 智能文件批量重命名工具 v1.0.0")
        self.root.geometry("900x700")
        
        # 初始化重命名器
        self.renamer = FileRenamer()
        
        self._create_widgets()
    
    def _create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # 左右分栏
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=5)
        
        # 文件列表
        self.file_list = FileListFrame(left_frame)
        self.file_list.pack(fill='both', expand=True)
        
        # 规则配置
        self.rule_frame = RuleFrame(left_frame)
        self.rule_frame.pack(fill='x', pady=10)
        
        # 设置回调
        self.rule_frame.preview_callback = self._on_preview
        self.rule_frame.execute_callback = self._on_execute
        self.rule_frame.undo_callback = self._on_undo
        
        # 预览区域
        self.preview_frame = PreviewFrame(right_frame)
        self.preview_frame.pack(fill='both', expand=True)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief='sunken')
        status_bar.pack(side='bottom', fill='x')
    
    def _on_preview(self):
        """预览按钮回调"""
        files = self.file_list.get_files()
        if not files:
            messagebox.showwarning("警告", "请先添加文件")
            return
        
        rule = self.rule_frame.get_rule()
        results = self.renamer.preview(files, rule)
        self.preview_frame.set_preview(results)
        self.status_var.set(f"预览: {len(results)} 个文件")
    
    def _on_execute(self):
        """执行按钮回调"""
        files = self.file_list.get_files()
        if not files:
            messagebox.showwarning("警告", "请先添加文件")
            return
        
        if not messagebox.askyesno("确认", "确定要执行重命名操作吗?"):
            return
        
        rule = self.rule_frame.get_rule()
        operations = self.renamer.rename(files, rule)
        
        success_count = sum(1 for op in operations if op.success)
        fail_count = len(operations) - success_count
        
        if fail_count == 0:
            messagebox.showinfo("成功", f"成功重命名 {success_count} 个文件")
        else:
            messagebox.showwarning("部分失败", f"成功: {success_count}, 失败: {fail_count}")
        
        self.status_var.set(f"执行完成: 成功 {success_count}, 失败 {fail_count}")
        
        # 刷新预览
        self._on_preview()
    
    def _on_undo(self):
        """撤销按钮回调"""
        undone = self.renamer.undo()
        if undone:
            messagebox.showinfo("成功", f"已撤销 {len(undone)} 个文件的重命名")
            self.status_var.set(f"已撤销 {len(undone)} 个文件")
            self._on_preview()
        else:
            messagebox.showwarning("警告", "没有可撤销的操作")
    
    def run(self):
        """运行GUI"""
        self.root.mainloop()


def main():
    """主函数"""
    app = FileRenameProGUI()
    app.run()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
FileRenamePro - 智能文件批量重命名工具核心模块

核心功能：
- 批量文件重命名
- 正则表达式支持
- 多种命名模式（序号、日期、哈希、随机字符串）
- 预览功能
- 撤销操作
"""

import os
import re
import json
import hashlib
import random
import string
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional, Callable, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum


class RenameMode(Enum):
    """重命名模式"""
    REPLACE = "replace"           # 简单替换
    REGEX = "regex"               # 正则表达式
    SERIAL = "serial"             # 序号命名
    DATE = "date"                 # 日期命名
    HASH = "hash"                 # 哈希命名
    RANDOM = "random"             # 随机字符串
    CASE = "case"                 # 大小写转换
    INSERT = "insert"             # 插入文本


@dataclass
class RenameRule:
    """重命名规则"""
    mode: RenameMode
    find: str = ""                    # 查找内容
    replace: str = ""                 # 替换内容
    prefix: str = ""                  # 前缀
    suffix: str = ""                  # 后缀
    start_num: int = 1                # 起始序号
    step: int = 1                     # 步长
    digits: int = 3                   # 序号位数
    date_format: str = "%Y%m%d"       # 日期格式
    hash_algo: str = "md5"            # 哈希算法
    hash_length: int = 8              # 哈希长度
    random_length: int = 8            # 随机字符串长度
    case_mode: str = "lower"          # 大小写模式
    insert_pos: int = 0               # 插入位置
    insert_text: str = ""             # 插入文本
    ignore_ext: bool = False          # 是否忽略扩展名
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['mode'] = self.mode.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RenameRule':
        """从字典创建"""
        data = data.copy()
        data['mode'] = RenameMode(data['mode'])
        return cls(**data)


@dataclass
class RenameOperation:
    """重命名操作记录"""
    old_path: str
    new_path: str
    timestamp: str
    success: bool = False
    error: str = ""


class FileRenamer:
    """文件重命名器"""
    
    def __init__(self, history_file: Optional[str] = None):
        self.history_file = history_file or os.path.expanduser("~/.filerenamepro_history.json")
        self.history: List[List[RenameOperation]] = []
        self._load_history()
    
    def _load_history(self):
        """加载历史记录"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.history = [
                        [RenameOperation(**op) for op in batch]
                        for batch in data
                    ]
            except Exception:
                self.history = []
    
    def _save_history(self):
        """保存历史记录"""
        try:
            data = [
                [asdict(op) for op in batch]
                for batch in self.history
            ]
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"警告: 无法保存历史记录: {e}")
    
    def _get_filename_parts(self, filepath: str) -> Tuple[str, str]:
        """获取文件名和扩展名"""
        filename = os.path.basename(filepath)
        name, ext = os.path.splitext(filename)
        return name, ext
    
    def _generate_serial(self, index: int, rule: RenameRule) -> str:
        """生成序号"""
        num = rule.start_num + index * rule.step
        return str(num).zfill(rule.digits)
    
    def _generate_date(self, rule: RenameRule) -> str:
        """生成日期字符串"""
        return datetime.now().strftime(rule.date_format)
    
    def _generate_hash(self, filepath: str, rule: RenameRule) -> str:
        """生成文件哈希"""
        try:
            hasher = hashlib.new(rule.hash_algo)
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    hasher.update(chunk)
            return hasher.hexdigest()[:rule.hash_length]
        except Exception:
            return ""
    
    def _generate_random(self, rule: RenameRule) -> str:
        """生成随机字符串"""
        chars = string.ascii_letters + string.digits
        return ''.join(random.choices(chars, k=rule.random_length))
    
    def _apply_case(self, name: str, rule: RenameRule) -> str:
        """应用大小写转换"""
        if rule.case_mode == "lower":
            return name.lower()
        elif rule.case_mode == "upper":
            return name.upper()
        elif rule.case_mode == "title":
            return name.title()
        elif rule.case_mode == "camel":
            words = re.split(r'[_\-\s]+', name)
            return words[0].lower() + ''.join(w.capitalize() for w in words[1:])
        return name
    
    def _apply_rule(self, filepath: str, index: int, rule: RenameRule) -> str:
        """应用重命名规则"""
        name, ext = self._get_filename_parts(filepath)
        
        if rule.mode == RenameMode.REPLACE:
            # 简单替换
            new_name = name.replace(rule.find, rule.replace)
        
        elif rule.mode == RenameMode.REGEX:
            # 正则表达式替换
            try:
                new_name = re.sub(rule.find, rule.replace, name)
            except re.error as e:
                raise ValueError(f"无效的正则表达式: {e}")
        
        elif rule.mode == RenameMode.SERIAL:
            # 序号命名
            serial = self._generate_serial(index, rule)
            if rule.find:
                new_name = name.replace(rule.find, serial)
            else:
                # 当没有find时，直接使用序号作为文件名主体
                new_name = serial
        
        elif rule.mode == RenameMode.DATE:
            # 日期命名
            date_str = self._generate_date(rule)
            if rule.find:
                new_name = name.replace(rule.find, date_str)
            else:
                # 当没有find时，直接使用日期作为文件名主体
                new_name = date_str
        
        elif rule.mode == RenameMode.HASH:
            # 哈希命名
            hash_str = self._generate_hash(filepath, rule)
            if rule.find:
                new_name = name.replace(rule.find, hash_str)
            else:
                # 当没有find时，直接使用哈希作为文件名主体
                new_name = hash_str
        
        elif rule.mode == RenameMode.RANDOM:
            # 随机字符串命名
            rand_str = self._generate_random(rule)
            if rule.find:
                new_name = name.replace(rule.find, rand_str)
            else:
                # 当没有find时，直接使用随机字符串作为文件名主体
                new_name = rand_str
        
        elif rule.mode == RenameMode.CASE:
            # 大小写转换 - 只转换文件名部分，保留扩展名
            new_name = self._apply_case(name, rule)
            # 对于CASE模式，扩展名也转换
            ext = self._apply_case(ext, rule)
        
        elif rule.mode == RenameMode.INSERT:
            # 插入文本
            pos = rule.insert_pos
            if pos < 0:
                pos = len(name) + pos + 1
            new_name = name[:pos] + rule.insert_text + name[pos:]
        
        else:
            new_name = name
        
        # 添加前缀和后缀（CASE模式除外，因为已经处理过扩展名）
        if rule.mode != RenameMode.CASE:
            new_name = rule.prefix + new_name + rule.suffix
        
        # 处理扩展名
        if rule.ignore_ext:
            return new_name
        return new_name + ext
    
    def preview(self, files: List[str], rule: RenameRule) -> List[Tuple[str, str]]:
        """
        预览重命名结果
        
        Args:
            files: 文件路径列表
            rule: 重命名规则
        
        Returns:
            [(原文件名, 新文件名), ...]
        """
        results = []
        for i, filepath in enumerate(files):
            try:
                new_name = self._apply_rule(filepath, i, rule)
                old_name = os.path.basename(filepath)
                results.append((old_name, new_name))
            except Exception as e:
                results.append((os.path.basename(filepath), f"[错误: {e}]"))
        return results
    
    def rename(self, files: List[str], rule: RenameRule, 
               dry_run: bool = False) -> List[RenameOperation]:
        """
        执行重命名
        
        Args:
            files: 文件路径列表
            rule: 重命名规则
            dry_run: 是否为预览模式
        
        Returns:
            操作记录列表
        """
        operations = []
        
        for i, filepath in enumerate(files):
            op = RenameOperation(
                old_path=filepath,
                new_path="",
                timestamp=datetime.now().isoformat()
            )
            
            try:
                if not os.path.exists(filepath):
                    raise FileNotFoundError(f"文件不存在: {filepath}")
                
                # 生成新文件名
                new_name = self._apply_rule(filepath, i, rule)
                dir_path = os.path.dirname(filepath)
                new_path = os.path.join(dir_path, new_name)
                
                # 检查目标文件是否已存在
                if new_path != filepath and os.path.exists(new_path):
                    raise FileExistsError(f"目标文件已存在: {new_name}")
                
                op.new_path = new_path
                
                if not dry_run:
                    os.rename(filepath, new_path)
                
                op.success = True
                
            except Exception as e:
                op.error = str(e)
            
            operations.append(op)
        
        # 保存到历史记录
        if not dry_run and any(op.success for op in operations):
            self.history.append(operations)
            self._save_history()
        
        return operations
    
    def undo(self) -> Optional[List[RenameOperation]]:
        """
        撤销上一次操作
        
        Returns:
            撤销的操作记录，如果没有可撤销的操作则返回None
        """
        if not self.history:
            return None
        
        last_batch = self.history.pop()
        undone_ops = []
        
        for op in reversed(last_batch):
            if op.success and os.path.exists(op.new_path):
                try:
                    os.rename(op.new_path, op.old_path)
                    undone_ops.append(op)
                except Exception as e:
                    print(f"撤销失败 {op.new_path}: {e}")
        
        self._save_history()
        return undone_ops
    
    def get_history(self) -> List[List[RenameOperation]]:
        """获取操作历史"""
        return self.history
    
    def clear_history(self):
        """清空历史记录"""
        self.history = []
        self._save_history()


class BatchRenamer:
    """批量重命名器 - 支持多规则链式处理"""
    
    def __init__(self):
        self.renamer = FileRenamer()
        self.rules: List[RenameRule] = []
    
    def add_rule(self, rule: RenameRule):
        """添加规则"""
        self.rules.append(rule)
    
    def clear_rules(self):
        """清空规则"""
        self.rules = []
    
    def preview(self, files: List[str]) -> List[Tuple[str, str]]:
        """预览所有规则应用后的结果"""
        if not self.rules:
            return [(os.path.basename(f), os.path.basename(f)) for f in files]
        
        results = []
        for filepath in files:
            name, ext = os.path.splitext(os.path.basename(filepath))
            original_name = name
            
            for i, rule in enumerate(self.rules):
                # 临时构造文件路径用于规则应用
                temp_path = os.path.join(os.path.dirname(filepath), name + ext)
                new_name = self.renamer._apply_rule(temp_path, 0, rule)
                name = os.path.splitext(new_name)[0]
            
            results.append((original_name + ext, name + ext))
        
        return results
    
    def rename(self, files: List[str], dry_run: bool = False) -> List[RenameOperation]:
        """执行批量重命名"""
        if not self.rules:
            return []
        
        # 依次应用所有规则
        current_files = files.copy()
        all_operations = []
        
        for rule in self.rules:
            operations = self.renamer.rename(current_files, rule, dry_run=True)
            
            if not dry_run:
                operations = self.renamer.rename(current_files, rule, dry_run=False)
            
            # 更新文件列表为新的路径
            for i, op in enumerate(operations):
                if op.success:
                    current_files[i] = op.new_path
            
            all_operations.extend(operations)
        
        return all_operations


def main():
    """命令行测试"""
    import tempfile
    
    # 创建测试文件
    with tempfile.TemporaryDirectory() as tmpdir:
        test_files = []
        for i in range(5):
            filepath = os.path.join(tmpdir, f"test_file_{i}.txt")
            with open(filepath, 'w') as f:
                f.write(f"content {i}")
            test_files.append(filepath)
        
        print("原始文件:")
        for f in test_files:
            print(f"  {os.path.basename(f)}")
        
        # 测试序号命名
        renamer = FileRenamer()
        rule = RenameRule(
            mode=RenameMode.SERIAL,
            prefix="doc_",
            suffix="_v1",
            start_num=1,
            digits=3
        )
        
        print("\n预览结果:")
        preview = renamer.preview(test_files, rule)
        for old, new in preview:
            print(f"  {old} -> {new}")
        
        print("\n执行重命名...")
        ops = renamer.rename(test_files, rule)
        for op in ops:
            status = "✓" if op.success else "✗"
            print(f"  {status} {os.path.basename(op.old_path)} -> {os.path.basename(op.new_path)}")
        
        print("\n撤销操作...")
        undone = renamer.undo()
        if undone:
            print(f"  已撤销 {len(undone)} 个文件")


if __name__ == "__main__":
    main()

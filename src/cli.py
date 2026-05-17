#!/usr/bin/env python3
"""
FileRenamePro - 命令行界面

提供直观的命令行操作界面，支持：
- 批量文件选择
- 规则配置
- 预览功能
- 执行重命名
- 撤销操作
"""

import os
import sys
import argparse
import json
from typing import List, Optional
from pathlib import Path

from renamer import (
    FileRenamer, RenameRule, RenameMode,
    BatchRenamer
)


def print_banner():
    """打印欢迎横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   📁 FileRenamePro - 智能文件批量重命名工具 v1.0.0          ║
║                                                              ║
║   支持正则表达式、序号、日期、哈希等多种命名模式            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_help():
    """打印帮助信息"""
    help_text = """
使用说明:

  filerenamepro [选项] <文件或目录...>

常用选项:
  -m, --mode MODE          重命名模式 (replace|regex|serial|date|hash|random|case|insert)
  -f, --find TEXT          查找文本/正则表达式
  -r, --replace TEXT       替换文本
  -p, --prefix TEXT        文件名前缀
  -s, --suffix TEXT        文件名后缀
  --preview                预览模式（不实际执行）
  --undo                   撤销上一次操作
  --history                查看操作历史

模式说明:
  replace    简单文本替换
  regex      正则表达式替换
  serial     序号命名 (支持 --start, --step, --digits)
  date       日期命名 (支持 --date-format)
  hash       文件哈希命名 (支持 --hash-algo, --hash-length)
  random     随机字符串命名 (支持 --random-length)
  case       大小写转换 (支持 --case-mode)
  insert     插入文本 (支持 --insert-pos, --insert-text)

示例:
  # 简单替换
  filerenamepro -m replace -f "old" -r "new" *.txt

  # 正则表达式替换
  filerenamepro -m regex -f "\\d+" -r "NUM" *.jpg

  # 序号命名
  filerenamepro -m serial --prefix "img_" --digits 3 *.png

  # 日期命名
  filerenamepro -m date --date-format "%Y%m%d" --prefix "backup_" *

  # 预览模式
  filerenamepro -m serial --prefix "doc_" --preview *.pdf

  # 撤销操作
  filerenamepro --undo
"""
    print(help_text)


def get_files_from_args(args: List[str]) -> List[str]:
    """从参数获取文件列表"""
    files = []
    for arg in args:
        path = Path(arg)
        if path.is_dir():
            # 如果是目录，获取目录下的所有文件
            files.extend([str(f) for f in path.iterdir() if f.is_file()])
        elif path.is_file():
            files.append(str(path))
    
    # 去重并保持顺序
    seen = set()
    unique_files = []
    for f in files:
        if f not in seen:
            seen.add(f)
            unique_files.append(f)
    
    return unique_files


def create_rule_from_args(args) -> RenameRule:
    """从参数创建重命名规则"""
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
    
    mode = mode_map.get(args.mode, RenameMode.REPLACE)
    
    rule = RenameRule(
        mode=mode,
        find=args.find or "",
        replace=args.replace or "",
        prefix=args.prefix or "",
        suffix=args.suffix or "",
        start_num=args.start or 1,
        step=args.step or 1,
        digits=args.digits or 3,
        date_format=args.date_format or "%Y%m%d",
        hash_algo=args.hash_algo or "md5",
        hash_length=args.hash_length or 8,
        random_length=args.random_length or 8,
        case_mode=args.case_mode or "lower",
        insert_pos=args.insert_pos or 0,
        insert_text=args.insert_text or "",
        ignore_ext=args.ignore_ext or False,
    )
    
    return rule


def print_preview(files: List[str], rule: RenameRule):
    """打印预览结果"""
    renamer = FileRenamer()
    results = renamer.preview(files, rule)
    
    print("\n📋 重命名预览:")
    print("-" * 80)
    print(f"{'序号':<6} {'原文件名':<35} {'新文件名':<35}")
    print("-" * 80)
    
    for i, (old, new) in enumerate(results, 1):
        # 截断过长的文件名
        old_display = (old[:32] + '...') if len(old) > 35 else old
        new_display = (new[:32] + '...') if len(new) > 35 else new
        print(f"{i:<6} {old_display:<35} {new_display:<35}")
    
    print("-" * 80)
    print(f"共 {len(results)} 个文件\n")


def print_results(operations):
    """打印执行结果"""
    print("\n📋 执行结果:")
    print("-" * 80)
    
    success_count = sum(1 for op in operations if op.success)
    fail_count = len(operations) - success_count
    
    for op in operations:
        old_name = os.path.basename(op.old_path)
        if op.success:
            new_name = os.path.basename(op.new_path)
            status = "✅"
            print(f"{status} {old_name} -> {new_name}")
        else:
            status = "❌"
            print(f"{status} {old_name} [错误: {op.error}]")
    
    print("-" * 80)
    print(f"成功: {success_count} | 失败: {fail_count}\n")


def interactive_mode():
    """交互式模式"""
    print_banner()
    print("🚀 进入交互式模式\n")
    
    renamer = FileRenamer()
    
    while True:
        print("\n请选择操作:")
        print("  1. 批量重命名文件")
        print("  2. 撤销上一次操作")
        print("  3. 查看操作历史")
        print("  4. 退出")
        
        choice = input("\n请输入选项 (1-4): ").strip()
        
        if choice == '1':
            # 获取文件路径
            path_input = input("请输入文件或目录路径 (支持通配符,多个用空格分隔): ").strip()
            if not path_input:
                print("❌ 路径不能为空")
                continue
            
            import glob
            files = []
            for pattern in path_input.split():
                if os.path.isdir(pattern):
                    files.extend([os.path.join(pattern, f) for f in os.listdir(pattern) 
                                 if os.path.isfile(os.path.join(pattern, f))])
                else:
                    files.extend(glob.glob(pattern))
            
            if not files:
                print("❌ 未找到文件")
                continue
            
            print(f"\n找到 {len(files)} 个文件")
            
            # 选择模式
            print("\n选择重命名模式:")
            print("  1. 简单替换 (replace)")
            print("  2. 正则表达式 (regex)")
            print("  3. 序号命名 (serial)")
            print("  4. 日期命名 (date)")
            print("  5. 文件哈希 (hash)")
            print("  6. 随机字符串 (random)")
            print("  7. 大小写转换 (case)")
            print("  8. 插入文本 (insert)")
            
            mode_choice = input("\n请选择模式 (1-8): ").strip()
            mode_map = {
                '1': RenameMode.REPLACE,
                '2': RenameMode.REGEX,
                '3': RenameMode.SERIAL,
                '4': RenameMode.DATE,
                '5': RenameMode.HASH,
                '6': RenameMode.RANDOM,
                '7': RenameMode.CASE,
                '8': RenameMode.INSERT,
            }
            
            mode = mode_map.get(mode_choice, RenameMode.REPLACE)
            rule = RenameRule(mode=mode)
            
            # 根据模式获取参数
            if mode in [RenameMode.REPLACE, RenameMode.REGEX]:
                rule.find = input("查找内容: ").strip()
                rule.replace = input("替换内容: ").strip()
            
            elif mode == RenameMode.SERIAL:
                rule.prefix = input("前缀 (可选): ").strip()
                rule.suffix = input("后缀 (可选): ").strip()
                start = input("起始序号 (默认1): ").strip()
                rule.start_num = int(start) if start else 1
                digits = input("序号位数 (默认3): ").strip()
                rule.digits = int(digits) if digits else 3
            
            elif mode == RenameMode.DATE:
                rule.prefix = input("前缀 (可选): ").strip()
                rule.suffix = input("后缀 (可选): ").strip()
                date_fmt = input("日期格式 (默认%Y%m%d): ").strip()
                rule.date_format = date_fmt or "%Y%m%d"
            
            elif mode == RenameMode.HASH:
                rule.prefix = input("前缀 (可选): ").strip()
                rule.suffix = input("后缀 (可选): ").strip()
                algo = input("哈希算法 (md5/sha1/sha256, 默认md5): ").strip()
                rule.hash_algo = algo or "md5"
                length = input("哈希长度 (默认8): ").strip()
                rule.hash_length = int(length) if length else 8
            
            elif mode == RenameMode.RANDOM:
                rule.prefix = input("前缀 (可选): ").strip()
                rule.suffix = input("后缀 (可选): ").strip()
                length = input("随机字符串长度 (默认8): ").strip()
                rule.random_length = int(length) if length else 8
            
            elif mode == RenameMode.CASE:
                print("大小写模式: lower(小写), upper(大写), title(首字母大写), camel(驼峰)")
                case = input("模式 (默认lower): ").strip()
                rule.case_mode = case or "lower"
            
            elif mode == RenameMode.INSERT:
                pos = input("插入位置 (0开头, -1结尾): ").strip()
                rule.insert_pos = int(pos) if pos else 0
                rule.insert_text = input("插入文本: ").strip()
            
            # 预览
            print_preview(files, rule)
            
            # 确认执行
            confirm = input("是否执行重命名? (y/n): ").strip().lower()
            if confirm == 'y':
                operations = renamer.rename(files, rule)
                print_results(operations)
            else:
                print("已取消")
        
        elif choice == '2':
            undone = renamer.undo()
            if undone:
                print(f"✅ 已撤销 {len(undone)} 个文件的重命名")
            else:
                print("❌ 没有可撤销的操作")
        
        elif choice == '3':
            history = renamer.get_history()
            if not history:
                print("暂无操作历史")
            else:
                print(f"\n共有 {len(history)} 次操作记录")
                for i, batch in enumerate(history, 1):
                    success = sum(1 for op in batch if op.success)
                    print(f"  {i}. {success}/{len(batch)} 个文件成功")
        
        elif choice == '4':
            print("👋 再见!")
            break
        
        else:
            print("❌ 无效选项")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        prog='filerenamepro',
        description='FileRenamePro - 智能文件批量重命名工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  filerenamepro -m serial --prefix "img_" --digits 3 *.png
  filerenamepro -m regex -f "\\d+" -r "NUM" --preview *.jpg
  filerenamepro --undo
        """
    )
    
    # 基本选项
    parser.add_argument('files', nargs='*', help='要重命名的文件或目录')
    parser.add_argument('-m', '--mode', default='replace',
                       choices=['replace', 'regex', 'serial', 'date', 'hash', 'random', 'case', 'insert'],
                       help='重命名模式 (默认: replace)')
    parser.add_argument('-f', '--find', help='查找文本/正则表达式')
    parser.add_argument('-r', '--replace', help='替换文本')
    parser.add_argument('-p', '--prefix', help='文件名前缀')
    parser.add_argument('-s', '--suffix', help='文件名后缀')
    
    # 序号模式选项
    parser.add_argument('--start', type=int, help='起始序号')
    parser.add_argument('--step', type=int, help='序号步长')
    parser.add_argument('--digits', type=int, help='序号位数')
    
    # 日期模式选项
    parser.add_argument('--date-format', help='日期格式 (如 %%Y%%m%%d)')
    
    # 哈希模式选项
    parser.add_argument('--hash-algo', choices=['md5', 'sha1', 'sha256'], help='哈希算法')
    parser.add_argument('--hash-length', type=int, help='哈希长度')
    
    # 随机模式选项
    parser.add_argument('--random-length', type=int, help='随机字符串长度')
    
    # 大小写模式选项
    parser.add_argument('--case-mode', choices=['lower', 'upper', 'title', 'camel'],
                       help='大小写转换模式')
    
    # 插入模式选项
    parser.add_argument('--insert-pos', type=int, help='插入位置')
    parser.add_argument('--insert-text', help='插入文本')
    
    # 其他选项
    parser.add_argument('--ignore-ext', action='store_true', help='忽略扩展名')
    parser.add_argument('--preview', action='store_true', help='预览模式')
    parser.add_argument('--undo', action='store_true', help='撤销上一次操作')
    parser.add_argument('--history', action='store_true', help='查看操作历史')
    parser.add_argument('--interactive', '-i', action='store_true', help='交互式模式')
    parser.add_argument('--version', '-v', action='store_true', help='显示版本')
    
    args = parser.parse_args()
    
    # 显示版本
    if args.version:
        print("FileRenamePro v1.0.0")
        return
    
    # 交互式模式
    if args.interactive or (not args.files and not args.undo and not args.history):
        interactive_mode()
        return
    
    # 撤销操作
    if args.undo:
        renamer = FileRenamer()
        undone = renamer.undo()
        if undone:
            print(f"✅ 已撤销 {len(undone)} 个文件的重命名")
        else:
            print("❌ 没有可撤销的操作")
        return
    
    # 查看历史
    if args.history:
        renamer = FileRenamer()
        history = renamer.get_history()
        if not history:
            print("暂无操作历史")
        else:
            print(f"共有 {len(history)} 次操作记录")
            for i, batch in enumerate(history, 1):
                success = sum(1 for op in batch if op.success)
                print(f"  {i}. {success}/{len(batch)} 个文件成功")
        return
    
    # 检查文件参数
    if not args.files:
        print("❌ 请指定要重命名的文件或目录")
        parser.print_help()
        return
    
    # 获取文件列表
    files = get_files_from_args(args.files)
    if not files:
        print("❌ 未找到文件")
        return
    
    # 创建规则
    rule = create_rule_from_args(args)
    
    # 预览或执行
    if args.preview:
        print_preview(files, rule)
    else:
        print_banner()
        print_preview(files, rule)
        
        confirm = input("\n是否执行重命名? (y/n): ").strip().lower()
        if confirm == 'y':
            renamer = FileRenamer()
            operations = renamer.rename(files, rule)
            print_results(operations)
        else:
            print("已取消")


if __name__ == "__main__":
    main()

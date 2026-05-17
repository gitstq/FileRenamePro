#!/usr/bin/env python3
"""
FileRenamePro - 构建脚本

支持构建:
- Windows: .exe
- macOS: .app
- Linux: 可执行文件
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path


def clean_build():
    """清理构建目录"""
    dirs_to_remove = ['build', 'dist', '__pycache__', '.pytest_cache']
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            print(f"清理 {dir_name}...")
            shutil.rmtree(dir_name)
    
    # 清理Python缓存
    for root, dirs, files in os.walk('.'):
        for d in dirs:
            if d == '__pycache__':
                shutil.rmtree(os.path.join(root, d))
        for f in files:
            if f.endswith('.pyc'):
                os.remove(os.path.join(root, f))
    
    print("清理完成")


def build_cli():
    """构建CLI版本"""
    print("构建CLI版本...")
    
    system = platform.system()
    
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--name', f'filerenamepro-{system.lower()}',
        '--add-data', 'src:src',
        '--hidden-import', 'renamer',
        '--hidden-import', 'cli',
        'main.py'
    ]
    
    if system == 'Windows':
        cmd[6] = 'src;src'  # Windows使用分号
    
    subprocess.run(cmd, check=True)
    print(f"CLI版本构建完成: dist/filerenamepro-{system.lower()}")


def build_gui():
    """构建GUI版本"""
    print("构建GUI版本...")
    
    system = platform.system()
    
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--windowed',
        '--name', f'filerenamepro-gui-{system.lower()}',
        '--add-data', 'src:src',
        '--hidden-import', 'renamer',
        '--hidden-import', 'gui',
        'main.py'
    ]
    
    if system == 'Windows':
        cmd[7] = 'src;src'
    
    subprocess.run(cmd, check=True)
    print(f"GUI版本构建完成: dist/filerenamepro-gui-{system.lower()}")


def run_tests():
    """运行测试"""
    print("运行单元测试...")
    result = subprocess.run([sys.executable, '-m', 'pytest', 'tests/', '-v'])
    return result.returncode == 0


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='FileRenamePro 构建脚本')
    parser.add_argument('--clean', action='store_true', help='清理构建目录')
    parser.add_argument('--cli', action='store_true', help='构建CLI版本')
    parser.add_argument('--gui', action='store_true', help='构建GUI版本')
    parser.add_argument('--all', action='store_true', help='构建所有版本')
    parser.add_argument('--test', action='store_true', help='运行测试')
    
    args = parser.parse_args()
    
    # 如果没有参数，显示帮助
    if not any([args.clean, args.cli, args.gui, args.all, args.test]):
        parser.print_help()
        return
    
    # 清理
    if args.clean:
        clean_build()
    
    # 运行测试
    if args.test:
        if not run_tests():
            print("测试失败，停止构建")
            return
    
    # 构建
    if args.all or args.cli:
        build_cli()
    
    if args.all or args.gui:
        build_gui()
    
    print("\n构建完成!")


if __name__ == "__main__":
    main()

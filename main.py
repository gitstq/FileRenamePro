#!/usr/bin/env python3
"""
FileRenamePro - 主入口文件

根据运行参数决定启动CLI或GUI模式
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """主函数"""
    # 检查是否有GUI参数
    if len(sys.argv) > 1 and sys.argv[1] in ['--gui', '-g']:
        from gui import main as gui_main
        gui_main()
    else:
        from cli import main as cli_main
        cli_main()

if __name__ == "__main__":
    main()

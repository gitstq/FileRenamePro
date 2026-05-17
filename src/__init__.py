"""
FileRenamePro - 智能文件批量重命名工具

一个功能强大的文件批量重命名工具，支持多种命名模式和预览功能。
"""

__version__ = "1.0.0"
__author__ = "gitstq"
__license__ = "MIT"

from .renamer import (
    FileRenamer,
    RenameRule,
    RenameMode,
    RenameOperation,
    BatchRenamer,
)

__all__ = [
    "FileRenamer",
    "RenameRule",
    "RenameMode",
    "RenameOperation",
    "BatchRenamer",
]

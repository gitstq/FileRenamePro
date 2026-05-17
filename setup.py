#!/usr/bin/env python3
"""
FileRenamePro 安装脚本
"""

from setuptools import setup, find_packages
import os

# 读取README文件
readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
if os.path.exists(readme_path):
    with open(readme_path, 'r', encoding='utf-8') as f:
        long_description = f.read()
else:
    long_description = "FileRenamePro - 智能文件批量重命名工具"

setup(
    name="filerenamepro",
    version="1.0.0",
    author="gitstq",
    author_email="",
    description="智能文件批量重命名工具 - 支持正则、序号、日期、哈希等多种命名模式",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gitstq/filerenamepro",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Utilities",
        "Topic :: System :: Filesystems",
    ],
    python_requires=">=3.7",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "flake8>=5.0",
            "black>=22.0",
            "mypy>=1.0",
        ],
        "build": [
            "pyinstaller>=5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "filerenamepro=cli:main",
            "frp=cli:main",
        ],
        "gui_scripts": [
            "filerenamepro-gui=gui:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)

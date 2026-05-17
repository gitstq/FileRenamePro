<div align="center">

# 📁 FileRenamePro

**智能文件批量重命名工具**

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

[English](#english) | [简体中文](#简体中文) | [繁體中文](#繁體中文)

</div>

---

<a name="简体中文"></a>
## 🎉 项目介绍

**FileRenamePro** 是一款功能强大的智能文件批量重命名工具，专为提高文件管理效率而设计。

### 💡 灵感来源

在日常工作和开发中，我们经常需要批量处理文件名 - 无论是整理照片、归档文档还是管理项目文件。市面上虽然有不少重命名工具，但要么功能单一，要么操作复杂。FileRenamePro 应运而生，提供直观、强大且易于使用的批量重命名解决方案。

### ✨ 自研差异化亮点

- **🔒 安全预览**: 重命名前可预览所有变更，避免误操作
- **↩️ 撤销支持**: 支持撤销上一次重命名操作
- **🎨 双模式界面**: 同时提供 CLI 命令行和 GUI 图形界面
- **⚡ 高性能**: 纯 Python 实现，无需额外依赖
- **🌍 跨平台**: 支持 Windows、macOS、Linux

---

## ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 📝 **简单替换** | 文本查找替换，支持批量修改 |
| 🔍 **正则表达式** | 强大的正则匹配替换功能 |
| 🔢 **序号命名** | 自动添加序号，支持自定义起始值、步长、位数 |
| 📅 **日期命名** | 使用当前日期/时间命名文件 |
| 🔐 **哈希命名** | 基于文件内容生成哈希值命名 |
| 🎲 **随机命名** | 生成随机字符串作为文件名 |
| 🔤 **大小写转换** | 支持小写、大写、首字母大写、驼峰命名 |
| 📌 **文本插入** | 在指定位置插入文本 |
| 👁️ **实时预览** | 重命名前预览所有变更 |
| ↩️ **撤销操作** | 一键撤销上一次重命名 |
| 📜 **历史记录** | 自动保存操作历史 |

---

## 🚀 快速开始

### 环境要求

- **Python**: 3.7 或更高版本
- **操作系统**: Windows / macOS / Linux

### 安装步骤

#### 方式一：使用 pip 安装（推荐）

```bash
pip install filerenamepro
```

#### 方式二：从源码安装

```bash
git clone https://github.com/gitstq/filerenamepro.git
cd filerenamepro
pip install -e .
```

#### 方式三：直接运行

```bash
git clone https://github.com/gitstq/filerenamepro.git
cd filerenamepro
python main.py
```

### 快速启动

#### CLI 命令行模式

```bash
# 简单替换
filerenamepro -m replace -f "old" -r "new" *.txt

# 序号命名
filerenamepro -m serial --prefix "img_" --digits 3 *.png

# 预览模式（不实际执行）
filerenamepro -m serial --prefix "doc_" --preview *.pdf

# 撤销操作
filerenamepro --undo
```

#### GUI 图形界面模式

```bash
# 启动图形界面
filerenamepro-gui

# 或使用主程序
python main.py --gui
```

---

## 📖 详细使用指南

### CLI 命令行用法

#### 基本语法

```bash
filerenamepro [选项] <文件或目录...>
```

#### 常用选项

| 选项 | 说明 |
|------|------|
| `-m, --mode` | 重命名模式 |
| `-f, --find` | 查找文本/正则表达式 |
| `-r, --replace` | 替换文本 |
| `-p, --prefix` | 文件名前缀 |
| `-s, --suffix` | 文件名后缀 |
| `--preview` | 预览模式 |
| `--undo` | 撤销上一次操作 |
| `-i, --interactive` | 交互式模式 |

#### 使用示例

**1. 简单替换**
```bash
# 将所有 "test" 替换为 "doc"
filerenamepro -m replace -f "test" -r "doc" *.txt
```

**2. 正则表达式替换**
```bash
# 将所有数字替换为 "NUM"
filerenamepro -m regex -f "\d+" -r "NUM" *.jpg
```

**3. 序号命名**
```bash
# 添加序号前缀，从 10 开始，步长 5，4 位数字
filerenamepro -m serial --prefix "img_" --start 10 --step 5 --digits 4 *.png
```

**4. 日期命名**
```bash
# 使用当前日期作为前缀
filerenamepro -m date --prefix "backup_" --date-format "%Y%m%d" *
```

**5. 文件哈希命名**
```bash
# 使用 MD5 哈希值命名
filerenamepro -m hash --hash-algo md5 --hash-length 8 *
```

**6. 随机字符串命名**
```bash
# 生成 10 位随机字符串
filerenamepro -m random --random-length 10 *
```

**7. 大小写转换**
```bash
# 转换为大写
filerenamepro -m case --case-mode upper *

# 转换为驼峰命名
filerenamepro -m case --case-mode camel *
```

**8. 插入文本**
```bash
# 在第 5 个字符位置插入 "NEW"
filerenamepro -m insert --insert-pos 5 --insert-text "NEW" *
```

### GUI 图形界面用法

1. **添加文件**: 点击"添加文件"或"添加目录"按钮选择要重命名的文件
2. **选择模式**: 在左侧选择重命名模式
3. **配置参数**: 根据模式填写相应参数
4. **预览**: 点击"预览"按钮查看重命名效果
5. **执行**: 确认无误后点击"执行"按钮
6. **撤销**: 如需撤销，点击"撤销"按钮

---

## 💡 设计思路与迭代规划

### 技术选型

- **Python 3.7+**: 跨平台、丰富的标准库
- **tkinter**: Python 内置 GUI 库，无需额外依赖
- **dataclass**: 现代化的数据类定义
- **type hints**: 完整的类型注解

### 架构设计

```
FileRenamePro/
├── src/
│   ├── renamer.py      # 核心重命名引擎
│   ├── cli.py          # 命令行界面
│   └── gui.py          # 图形界面
├── tests/              # 单元测试
├── scripts/            # 构建脚本
└── docs/               # 文档
```

### 后续迭代计划

- [ ] 支持更多哈希算法（SHA-256、SHA-512）
- [ ] 添加文件过滤器（按扩展名、大小、日期）
- [ ] 支持正则表达式捕获组
- [ ] 批量重命名模板保存/加载
- [ ] 多语言界面支持
- [ ] 插件系统

---

## 📦 打包与部署

### 构建可执行文件

```bash
# 安装构建依赖
pip install pyinstaller

# 构建 CLI 版本
python scripts/build.py --cli

# 构建 GUI 版本
python scripts/build.py --gui

# 构建所有版本
python scripts/build.py --all
```

### 运行测试

```bash
# 运行单元测试
python tests/test_renamer.py

# 或使用 pytest
pytest tests/
```

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 提交规范

- **feat**: 新功能
- **fix**: 修复问题
- **docs**: 文档更新
- **refactor**: 代码重构
- **test**: 测试相关

---

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

---

<a name="english"></a>
## 🎉 Introduction

**FileRenamePro** is a powerful intelligent batch file renaming tool designed to improve file management efficiency.

### ✨ Key Features

- **🔒 Safe Preview**: Preview all changes before renaming to avoid mistakes
- **↩️ Undo Support**: Undo the last renaming operation
- **🎨 Dual Interface**: Both CLI and GUI modes available
- **⚡ High Performance**: Pure Python implementation, no extra dependencies
- **🌍 Cross-Platform**: Windows, macOS, Linux support

### 🚀 Quick Start

```bash
# Install
pip install filerenamepro

# CLI usage
filerenamepro -m serial --prefix "img_" --digits 3 *.png

# GUI mode
filerenamepro-gui
```

---

<a name="繁體中文"></a>
## 🎉 專案介紹

**FileRenamePro** 是一款功能強大的智慧檔案批次重新命名工具，專為提高檔案管理效率而設計。

### ✨ 核心特性

- **🔒 安全預覽**: 重新命名前可預覽所有變更，避免誤操作
- **↩️ 撤銷支援**: 支援撤銷上一次重新命名操作
- **🎨 雙模式介面**: 同時提供 CLI 命令列和 GUI 圖形介面
- **⚡ 高效能**: 純 Python 實現，無需額外依賴
- **🌍 跨平台**: 支援 Windows、macOS、Linux

### 🚀 快速開始

```bash
# 安裝
pip install filerenamepro

# 命令列使用
filerenamepro -m serial --prefix "img_" --digits 3 *.png

# 圖形介面模式
filerenamepro-gui
```

---

<div align="center">

**Made with ❤️ by gitstq**

⭐ Star us on GitHub — it motivates us a lot!

</div>

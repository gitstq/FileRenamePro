# 🤝 贡献指南

感谢您对 FileRenamePro 的兴趣！我们欢迎各种形式的贡献。

## 如何贡献

### 报告问题

如果您发现了 bug 或有功能建议，请通过 GitHub Issues 提交：

1. 检查是否已有相关 Issue
2. 创建新 Issue，详细描述问题或建议
3. 如果是 bug，请提供复现步骤和环境信息

### 提交代码

1. **Fork** 本仓库
2. **Clone** 您的 fork
3. 创建新分支：`git checkout -b feature/your-feature`
4. 提交更改：`git commit -m "feat: add new feature"`
5. 推送到分支：`git push origin feature/your-feature`
6. 创建 Pull Request

### 代码规范

- 遵循 PEP 8 规范
- 添加适当的注释和文档
- 为新功能编写测试
- 确保所有测试通过

### 提交信息规范

使用 Angular 风格的提交信息：

- `feat:` 新功能
- `fix:` 修复问题
- `docs:` 文档更新
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建/工具相关

示例：
```
feat: add support for SHA-256 hashing
fix: resolve undo operation bug
docs: update README with new examples
```

## 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/gitstq/filerenamepro.git
cd filerenamepro

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
python tests/test_renamer.py
```

## 代码审查

所有 Pull Request 都需要经过审查才能合并。请耐心等待维护者的反馈。

## 许可证

通过贡献代码，您同意您的贡献将在 MIT 许可证下发布。

感谢您的贡献！🎉

# 发布到 PyPI 指南

本项目包含了自动化发布到 PyPI 的脚本。

## 脚本说明

### `publish.sh` - 主发布脚本
完整的发布脚本，包含构建、测试、检查和上传功能。

**用法:**
```bash
# 发布到正式 PyPI
./publish.sh

# 发布到 TestPyPI（测试）
./publish.sh --test
```

### `test-publish.sh` - 测试发布脚本
快捷脚本，直接发布到 TestPyPI 进行测试。

**用法:**
```bash
./test-publish.sh
```

### `bump-version.sh` - 版本管理脚本
自动更新版本号的脚本。

**用法:**
```bash
# 更新 patch 版本 (默认): 0.1.1 -> 0.1.2
./bump-version.sh
./bump-version.sh patch

# 更新 minor 版本: 0.1.1 -> 0.2.0
./bump-version.sh minor

# 更新 major 版本: 0.1.1 -> 1.0.0
./bump-version.sh major
```

## 发布流程

### 1. 准备发布

确保你的代码已经准备好发布：
- 所有功能已完成并测试
- 文档已更新
- 所有文件已提交到 git

### 2. 更新版本号

```bash
# 根据更改类型选择合适的版本更新
./bump-version.sh patch  # 修复 bug
./bump-version.sh minor  # 新功能
./bump-version.sh major  # 破坏性更改
```

### 3. 测试发布（推荐）

先发布到 TestPyPI 测试：

```bash
./test-publish.sh
```

测试安装：
```bash
pip install --index-url https://test.pypi.org/simple/ v2ex-tx2json==版本号
```

### 4. 正式发布

确认测试无问题后，发布到正式 PyPI：

```bash
./publish.sh
```

## 前置要求

### 必需的 Python 包
脚本会自动安装这些包，但你也可以手动安装：

```bash
pip install build twine toml
```

### PyPI 账户配置

1. 注册 PyPI 账户: https://pypi.org/account/register/
2. 注册 TestPyPI 账户: https://test.pypi.org/account/register/
3. 生成 API tokens:
   - PyPI: https://pypi.org/manage/account/token/
   - TestPyPI: https://test.pypi.org/manage/account/token/

4. 配置 `~/.pypirc`：

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-你的API-token

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-你的TestPyPI-API-token
```

## 脚本功能

### `publish.sh` 包含的功能：
- ✅ 检查必要工具（python3, build, twine）
- ✅ 自动安装缺失的包
- ✅ 清理旧的构建文件
- ✅ 运行测试（如果存在 pytest）
- ✅ 构建包（wheel 和 source distribution）
- ✅ 检查包的完整性
- ✅ 显示将要上传的文件
- ✅ 用户确认
- ✅ 上传到 PyPI 或 TestPyPI
- ✅ 彩色日志输出
- ✅ 错误处理

### 安全特性：
- 在每个关键步骤前都有确认
- 自动清理构建文件
- 完整的错误检查
- 测试优先的工作流

## 故障排除

### 常见问题

1. **"403 Forbidden" 错误**
   - 检查 API token 是否正确
   - 确认你有上传权限
   - 版本号可能已存在

2. **"Package already exists" 错误**
   - 更新版本号：`./bump-version.sh`
   - PyPI 不允许重复上传相同版本

3. **构建失败**
   - 检查 `pyproject.toml` 语法
   - 确保所有必需字段都存在

4. **测试失败**
   - 修复测试问题后再发布
   - 或临时跳过测试（不推荐）

### 手动操作

如果脚本出现问题，你也可以手动执行：

```bash
# 构建
python3 -m build

# 检查
python3 -m twine check dist/*

# 上传到 TestPyPI
python3 -m twine upload --repository testpypi dist/*

# 上传到 PyPI
python3 -m twine upload dist/*
```
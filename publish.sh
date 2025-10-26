#!/bin/bash

# PyPI 发布脚本 for v2ex-tx2json
# 用法: ./publish.sh [--test]
# --test: 发布到 TestPyPI 而不是正式 PyPI

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否为测试发布
TEST_PYPI=false
if [[ "$1" == "--test" ]]; then
    TEST_PYPI=true
    log_info "将发布到 TestPyPI"
else
    log_info "将发布到正式 PyPI"
fi

# 检查必要的工具
log_info "检查必要的工具..."

if ! command -v python3 &> /dev/null; then
    log_error "python3 未找到，请安装 Python 3.8+"
    exit 1
fi

if ! python3 -c "import build" 2>/dev/null; then
    log_warning "build 模块未安装，正在安装..."
    pip3 install --user build
fi

if ! python3 -c "import twine" 2>/dev/null; then
    log_warning "twine 模块未安装，正在安装..."
    pip3 install --user twine
fi

# 检查当前目录
if [[ ! -f "pyproject.toml" ]]; then
    log_error "未找到 pyproject.toml 文件，请在项目根目录运行此脚本"
    exit 1
fi

# 获取当前版本
CURRENT_VERSION=$(python3 -c "
import tomllib
with open('pyproject.toml', 'rb') as f:
    data = tomllib.load(f)
print(data['project']['version'])
" 2>/dev/null || python3 -c "
import toml
with open('pyproject.toml', 'r') as f:
    data = toml.load(f)
print(data['project']['version'])
")

log_info "当前版本: $CURRENT_VERSION"

# 清理旧的构建文件
log_info "清理旧的构建文件..."
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/

# 运行测试（如果存在）
if [[ -f "tests/test_core.py" ]] && command -v pytest &> /dev/null; then
    log_info "运行测试..."
    if ! pytest -q; then
        log_error "测试失败，取消发布"
        exit 1
    fi
    log_success "测试通过"
elif [[ -f "tests/test_core.py" ]]; then
    log_warning "pytest 未安装，跳过测试"
else
    log_warning "未找到测试文件，跳过测试"
fi

# 构建包
log_info "构建包..."
if ! python3 -m build; then
    log_error "构建失败"
    exit 1
fi

log_success "构建完成"

# 检查构建的包
log_info "检查构建的包..."
if ! python3 -m twine check dist/*; then
    log_error "包检查失败"
    exit 1
fi

log_success "包检查通过"

# 显示将要上传的文件
log_info "将要上传的文件:"
ls -la dist/

# 确认上传
if [[ "$TEST_PYPI" == "true" ]]; then
    read -p "确认上传到 TestPyPI? (y/N): " -n 1 -r
else
    read -p "确认上传到正式 PyPI? (y/N): " -n 1 -r
fi

echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "取消上传"
    exit 0
fi

# 上传到 PyPI
log_info "开始上传..."

if [[ "$TEST_PYPI" == "true" ]]; then
    # 上传到 TestPyPI
    log_info "上传到 TestPyPI..."
    if python3 -m twine upload --repository testpypi dist/*; then
        log_success "成功上传到 TestPyPI!"
        log_info "可以通过以下命令安装测试版本:"
        echo "pip install --index-url https://test.pypi.org/simple/ v2ex-tx2json==$CURRENT_VERSION"
    else
        log_error "上传到 TestPyPI 失败"
        exit 1
    fi
else
    # 上传到正式 PyPI
    log_info "上传到正式 PyPI..."
    if python3 -m twine upload dist/*; then
        log_success "成功上传到 PyPI!"
        log_info "可以通过以下命令安装:"
        echo "pip install v2ex-tx2json==$CURRENT_VERSION"
    else
        log_error "上传到 PyPI 失败"
        exit 1
    fi
fi

log_success "发布完成!"
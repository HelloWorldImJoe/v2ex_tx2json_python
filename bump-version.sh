#!/bin/bash

# 版本管理脚本
# 用法: ./bump-version.sh [major|minor|patch]

set -e

# 默认为 patch 版本更新
BUMP_TYPE=${1:-patch}

if [[ ! "$BUMP_TYPE" =~ ^(major|minor|patch)$ ]]; then
    echo "用法: $0 [major|minor|patch]"
    echo "  major: 1.0.0 -> 2.0.0"
    echo "  minor: 1.0.0 -> 1.1.0" 
    echo "  patch: 1.0.0 -> 1.0.1"
    exit 1
fi

# 检查是否有 Python tomllib 或 toml 模块
if ! python3 -c "import tomllib" 2>/dev/null && ! python3 -c "import toml" 2>/dev/null; then
    echo "正在安装 toml 模块..."
    pip3 install --user toml
fi

# 获取当前版本
CURRENT_VERSION=$(python3 -c "
try:
    import tomllib
    with open('pyproject.toml', 'rb') as f:
        data = tomllib.load(f)
except ImportError:
    import toml
    with open('pyproject.toml', 'r') as f:
        data = toml.load(f)
print(data['project']['version'])
")

echo "当前版本: $CURRENT_VERSION"

# 计算新版本
NEW_VERSION=$(python3 -c "
version = '$CURRENT_VERSION'.split('.')
major, minor, patch = int(version[0]), int(version[1]), int(version[2])

if '$BUMP_TYPE' == 'major':
    major += 1
    minor = 0
    patch = 0
elif '$BUMP_TYPE' == 'minor':
    minor += 1
    patch = 0
elif '$BUMP_TYPE' == 'patch':
    patch += 1

print(f'{major}.{minor}.{patch}')
")

echo "新版本: $NEW_VERSION"

# 更新 pyproject.toml
python3 -c "
import re

with open('pyproject.toml', 'r') as f:
    content = f.read()

# 替换版本号
content = re.sub(
    r'version = \"[^\"]+\"',
    f'version = \"$NEW_VERSION\"',
    content
)

with open('pyproject.toml', 'w') as f:
    f.write(content)
"

echo "✅ 版本已更新到 $NEW_VERSION"
echo "💡 现在可以运行 ./publish.sh 来发布新版本"
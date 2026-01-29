#!/bin/bash

###############################################################################
# 灵值生态园智能体 - 全景移植打包脚本
# 版本：v5.1
# 日期：2026-01-25
# 用途：打包完整的智能体项目，包含所有文件、文档、配置和依赖
###############################################################################

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 项目信息
PROJECT_NAME="灵值生态园智能体移植包"
VERSION="v5.1"
DATE=$(date +%Y%m%d_%H%M%S)
PACKAGE_NAME="${PROJECT_NAME}_全景移植_${VERSION}_${DATE}"
BUILD_DIR="build"
DIST_DIR="dist"
SOURCE_DIR="${PROJECT_NAME}"

# 打印欢迎信息
echo "========================================"
echo "  灵值生态园智能体 - 全景移植打包工具"
echo "  版本：${VERSION}"
echo "  日期：$(date +%Y-%m-%d)"
echo "========================================"
echo ""

# 检查源目录是否存在
if [ ! -d "$SOURCE_DIR" ]; then
    print_error "源目录 ${SOURCE_DIR} 不存在！"
    exit 1
fi

# 创建临时目录
print_info "创建临时目录..."
mkdir -p ${BUILD_DIR}
mkdir -p ${DIST_DIR}

# 复制项目文件
print_info "复制项目文件..."
mkdir -p ${BUILD_DIR}/${PROJECT_NAME}

# 复制核心目录
if [ -d "${SOURCE_DIR}/src" ]; then
    cp -r ${SOURCE_DIR}/src ${BUILD_DIR}/${PROJECT_NAME}/
    print_success "已复制 src/"
fi

if [ -d "${SOURCE_DIR}/config" ]; then
    cp -r ${SOURCE_DIR}/config ${BUILD_DIR}/${PROJECT_NAME}/
    print_success "已复制 config/"
fi

if [ -d "${SOURCE_DIR}/assets" ]; then
    cp -r ${SOURCE_DIR}/assets ${BUILD_DIR}/${PROJECT_NAME}/
    print_success "已复制 assets/"
fi

if [ -d "${SOURCE_DIR}/docs" ]; then
    cp -r ${SOURCE_DIR}/docs ${BUILD_DIR}/${PROJECT_NAME}/
    print_success "已复制 docs/"
fi

if [ -d "${SOURCE_DIR}/scripts" ]; then
    cp -r ${SOURCE_DIR}/scripts ${BUILD_DIR}/${PROJECT_NAME}/
    print_success "已复制 scripts/"
fi

if [ -d "${SOURCE_DIR}/知识库" ]; then
    cp -r ${SOURCE_DIR}/知识库 ${BUILD_DIR}/${PROJECT_NAME}/
    print_success "已复制 知识库/"
fi

if [ -d "${SOURCE_DIR}/01_智能体配置" ]; then
    cp -r ${SOURCE_DIR}/01_智能体配置 ${BUILD_DIR}/${PROJECT_NAME}/
    print_success "已复制 01_智能体配置/"
fi

# 复制根目录文件
print_info "复制根目录文件..."
cp ${SOURCE_DIR}/*.md ${BUILD_DIR}/${PROJECT_NAME}/ 2>/dev/null || true
cp ${SOURCE_DIR}/*.sh ${BUILD_DIR}/${PROJECT_NAME}/ 2>/dev/null || true
cp ${SOURCE_DIR}/*.json ${BUILD_DIR}/${PROJECT_NAME}/ 2>/dev/null || true
cp ${SOURCE_DIR}/requirements.txt ${BUILD_DIR}/${PROJECT_NAME}/ 2>/dev/null || true
cp ${SOURCE_DIR}/.gitignore ${BUILD_DIR}/${PROJECT_NAME}/ 2>/dev/null || true
print_success "已复制根目录文件"

# 创建必要的目录结构
print_info "创建目录结构..."
mkdir -p ${BUILD_DIR}/${PROJECT_NAME}/logs
mkdir -p ${BUILD_DIR}/${PROJECT_NAME}/tmp
mkdir -p ${BUILD_DIR}/${PROJECT_NAME}/backups

# 创建 README
print_info "创建 README..."
cat > ${BUILD_DIR}/${PROJECT_NAME}/README_移植包.md << 'EOF'
# 灵值生态园智能体 - 全景移植包

## 📦 包信息

- **项目名称**：灵值生态园智能体
- **版本**：v5.1
- **打包时间**：2026-01-25
- **包类型**：全景移植包（完整版）

## 🚀 快速开始

### 1. 解压文件
```bash
tar -xzf 灵值生态园智能体移植包_全景移植_v5.1_YYYYMMDD_HHMMSS.tar.gz
cd 灵值生态园智能体移植包
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 初始化数据库
```bash
cd src/auth
python init_data.py
python init_ecosystem.py
python init_project.py
```

### 4. 启动服务
```bash
cd ../..
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. 访问服务
- API 服务：http://localhost:8000
- API 文档：http://localhost:8000/docs

## 📋 重要提示

⚠️ **必须添加收款码文件**：
- 将 `个人微信收款码.jpg` 放到 `assets/` 目录
- 将 `个人支付宝收款码.jpg` 放到 `assets/` 目录

详细说明请参考：
- Windows部署指南.md
- 收款码配置检查清单.md
- 添加收款码文件说明.md

## 📚 文档目录

- **Windows部署指南.md** - Windows 系统部署指南
- **快速发布指南.md** - 快速启动指南
- **发布检查清单.md** - 发布检查清单
- **发布文档.md** - 详细发布文档
- **收款码配置检查清单.md** - 收款码配置指南
- **添加收款码文件说明.md** - 收款码文件添加指南

## 🔐 默认账号

- **邮箱**：xufeng@meiyueart.cn
- **密码**：Xf@071214
- **角色**：超级管理员

⚠️ **部署后请立即修改默认密码！**

## 📞 技术支持

- **邮箱**：meiyue@meiyueart.cn
- **官网**：www.meiyueart.cn
- **文档**：docs.meiyueart.cn

---

© 2026 媄月商业 版权所有
EOF

# 创建版本信息文件
print_info "创建版本信息文件..."
cat > ${BUILD_DIR}/${PROJECT_NAME}/VERSION.json << EOF
{
  "project_name": "灵值生态园智能体",
  "version": "v5.1",
  "build_date": "$(date +%Y-%m-%d)",
  "build_time": "$(date +%H:%M:%S)",
  "build_type": "全景移植包",
  "description": "完整的灵值生态园智能体项目，包含所有文件、文档、配置和依赖",
  "features": [
    "智能体核心功能（知识库检索、图像生成、联网搜索）",
    "权限管理系统（50+ API接口）",
    "生态机制系统（15+ API接口）",
    "项目参与和团队组建系统（10+ API接口）",
    "数据库管理系统（8+ API接口）",
    "收款码和支付方式说明",
    "完整的部署文档和指南"
  ],
  "requirements": {
    "python": ">=3.10",
    "platform": "Linux/Mac/Windows"
  },
  "contact": {
    "email": "meiyue@meiyueart.cn",
    "website": "www.meiyueart.cn",
    "docs": "docs.meiyueart.cn"
  }
}
EOF

# 创建打包清单
print_info "生成打包清单..."
cat > ${BUILD_DIR}/${PACKAGE_NAME}_文件清单.txt << EOF
# 灵值生态园智能体 - 全景移植包文件清单
# 版本：v5.1
# 打包时间：$(date +%Y-%m-%d %H:%M:%S)
# 生成工具：package.sh

========================================
文件统计
========================================

EOF

# 统计文件数量
TOTAL_FILES=$(find ${BUILD_DIR}/${PROJECT_NAME} -type f | wc -l)
TOTAL_DIRS=$(find ${BUILD_DIR}/${PROJECT_NAME} -type d | wc -l)
TOTAL_SIZE=$(du -sh ${BUILD_DIR}/${PROJECT_NAME} | cut -f1)

echo "总文件数：${TOTAL_FILES}" >> ${BUILD_DIR}/${PACKAGE_NAME}_文件清单.txt
echo "总目录数：${TOTAL_DIRS}" >> ${BUILD_DIR}/${PACKAGE_NAME}_文件清单.txt
echo "总大小：${TOTAL_SIZE}" >> ${BUILD_DIR}/${PACKAGE_NAME}_文件清单.txt
echo "" >> ${BUILD_DIR}/${PACKAGE_NAME}_文件清单.txt

echo "========================================
核心文件列表
========================================" >> ${BUILD_DIR}/${PACKAGE_NAME}_文件清单.txt

# 列出核心文件
echo "" >> ${BUILD_DIR}/${PACKAGE_NAME}_文件清单.txt
echo "【根目录文件】" >> ${BUILD_DIR}/${PACKAGE_NAME}_文件清单.txt
find ${BUILD_DIR}/${PROJECT_NAME} -maxdepth 1 -type f -name "*.md" -o -name "*.sh" -o -name "*.json" -o -name "requirements.txt" -o -name ".gitignore" | sort >> ${BUILD_DIR}/${PACKAGE_NAME}_文件清单.txt

echo "" >> ${BUILD_DIR}/${PACKAGE_NAME}_文件清单.txt
echo "【src/ 目录】" >> ${BUILD_DIR}/${PACKAGE_NAME}_文件清单.txt
find ${BUILD_DIR}/${PROJECT_NAME}/src -type f | sort >> ${BUILD_DIR}/${PACKAGE_NAME}_文件清单.txt

echo "" >> ${BUILD_DIR}/${PACKAGE_NAME}_文件清单.txt
echo "【config/ 目录】" >> ${BUILD_DIR}/${PACKAGE_NAME}_文件清单.txt
find ${BUILD_DIR}/${PROJECT_NAME}/config -type f | sort >> ${BUILD_DIR}/${PACKAGE_NAME}_文件清单.txt

echo "" >> ${BUILD_DIR}/${PACKAGE_NAME}_文件清单.txt
echo "【知识库/ 目录】" >> ${BUILD_DIR}/${PACKAGE_NAME}_文件清单.txt
find ${BUILD_DIR}/${PROJECT_NAME}/知识库 -type f | sort >> ${BUILD_DIR}/${PACKAGE_NAME}_文件清单.txt

echo "" >> ${BUILD_DIR}/${PACKAGE_NAME}_文件清单.txt
echo "【assets/ 目录】" >> ${BUILD_DIR}/${PROJECT_NAME}_文件清单.txt
find ${BUILD_DIR}/${PROJECT_NAME}/assets -type f | sort >> ${BUILD_DIR}/${PACKAGE_NAME}_文件清单.txt

echo "" >> ${BUILD_DIR}/${PACKAGE_NAME}_文件清单.txt
echo "【scripts/ 目录】" >> ${BUILD_DIR}/${PROJECT_NAME}/文件清单.txt
find ${BUILD_DIR}/${PROJECT_NAME}/scripts -type f | sort >> ${BUILD_DIR}/${PACKAGE_NAME}_文件清单.txt

echo "" >> ${BUILD_DIR}/${PACKAGE_NAME}_文件清单.txt
echo "【docs/ 目录】" >> ${BUILD_DIR}/${PACKAGE_NAME}_文件清单.txt
find ${BUILD_DIR}/${PROJECT_NAME}/docs -type f | sort >> ${BUILD_DIR}/${PACKAGE_NAME}_文件清单.txt

echo "" >> ${BUILD_DIR}/${PACKAGE_NAME}_文件清单.txt
echo "【01_智能体配置/ 目录】" >> ${BUILD_DIR}/${PACKAGE_NAME}_文件清单.txt
find ${BUILD_DIR}/${PROJECT_NAME}/01_智能体配置 -type f | sort >> ${BUILD_DIR}/${PACKAGE_NAME}_文件清单.txt

# 创建压缩包
print_info "创建压缩包..."
cd ${BUILD_DIR}
tar -czf ../${DIST_DIR}/${PACKAGE_NAME}.tar.gz ${PROJECT_NAME}

# 创建验证文件
print_info "创建验证文件..."
cd ..
cat > ${DIST_DIR}/${PACKAGE_NAME}_验证信息.txt << EOF
# 灵值生态园智能体 - 全景移植包验证信息
# 版本：v5.1
# 打包时间：$(date +%Y-%m-%d %H:%M:%S)

========================================
包信息
========================================
包名：${PACKAGE_NAME}.tar.gz
文件数：${TOTAL_FILES}
目录数：${TOTAL_DIRS}
大小：$(du -h ${DIST_DIR}/${PACKAGE_NAME}.tar.gz | cut -f1)

========================================
MD5 校验和
========================================
$(md5sum ${DIST_DIR}/${PACKAGE_NAME}.tar.gz | cut -d' ' -f1)

========================================
SHA256 校验和
========================================
$(sha256sum ${DIST_DIR}/${PACKAGE_NAME}.tar.gz | cut -d' ' -f1)

========================================
验证方法
========================================

# Linux/Mac
md5sum ${PACKAGE_NAME}.tar.gz
sha256sum ${PACKAGE_NAME}.tar.gz

# Windows PowerShell
Get-FileHash ${PACKAGE_NAME}.tar.gz -Algorithm MD5
Get-FileHash ${PACKAGE_NAME}.tar.gz -Algorithm SHA256

========================================
解压验证
========================================
# 解压后检查
ls -la ${PROJECT_NAME}/
cat ${PROJECT_NAME}/VERSION.json

EOF

# 复制文件清单到输出目录
cp ${BUILD_DIR}/${PACKAGE_NAME}_文件清单.txt ${DIST_DIR}/

# 清理临时目录
print_info "清理临时文件..."
rm -rf ${BUILD_DIR}

# 输出打包结果
echo ""
print_success "========================================"
print_success "  打包完成！"
print_success "========================================"
echo ""
echo "📦 包信息："
echo "  - 文件名：${DIST_DIR}/${PACKAGE_NAME}.tar.gz"
echo "  - 文件数：${TOTAL_FILES}"
echo "  - 目录数：${TOTAL_DIRS}"
echo "  - 大小：$(du -h ${DIST_DIR}/${PACKAGE_NAME}.tar.gz | cut -f1)"
echo ""
echo "📄 附加文件："
echo "  - ${DIST_DIR}/${PACKAGE_NAME}_文件清单.txt"
echo "  - ${DIST_DIR}/${PACKAGE_NAME}_验证信息.txt"
echo ""
echo "🚀 下一步："
echo "  1. 检查文件清单：cat ${DIST_DIR}/${PACKAGE_NAME}_文件清单.txt"
echo "  2. 验证包完整性：cat ${DIST_DIR}/${PACKAGE_NAME}_验证信息.txt"
echo "  3. 分发到目标环境"
echo ""
print_success "全景移植包打包完成！"
echo ""

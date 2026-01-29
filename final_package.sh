#!/bin/bash

###############################################################################
# 灵值生态园智能体 - 最终发布打包脚本
# 版本：v5.1
# 日期：2026-01-25
# 用途：打包所有文件用于正式发布
###############################################################################

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  灵值生态园智能体 - 最终发布打包${NC}"
echo -e "${BLUE}  版本：v5.1${NC}"
echo -e "${BLUE}  日期：$(date +%Y-%m-%d)${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 项目信息
VERSION="v5.1"
DATE=$(date +%Y%m%d_%H%M%S)
RELEASE_NAME="灵值生态园智能体_完整发布版_${VERSION}_${DATE}"
TEMP_DIR="temp_build"
FINAL_DIR="releases"

# 创建临时目录
echo -e "${BLUE}[INFO]${NC} 创建临时目录..."
mkdir -p ${TEMP_DIR}
mkdir -p ${FINAL_DIR}

# 复制所有文件
echo -e "${BLUE}[INFO]${NC} 复制项目文件..."

# 复制核心目录
cp -r src ${TEMP_DIR}/
cp -r config ${TEMP_DIR}/
cp -r assets ${TEMP_DIR}/
cp -r docs ${TEMP_DIR}/
cp -r scripts ${TEMP_DIR}/
cp -r 灵值生态园智能体移植包 ${TEMP_DIR}/

# 复制根目录文件
cp README.md ${TEMP_DIR}/
cp requirements.txt ${TEMP_DIR}/
cp .gitignore ${TEMP_DIR}/
cp 全景移植包使用指南.md ${TEMP_DIR}/

# 创建发布说明
echo -e "${BLUE}[INFO]${NC} 创建发布说明..."
cat > ${TEMP_DIR}/发布说明.txt << 'EOF'
灵值生态园智能体 - 完整发布版
========================================

版本：v5.1
发布日期：2026-01-25
类型：正式发布

快速开始
========================================

1. 解压文件
   tar -xzf 灵值生态园智能体_完整发布版_v5.1_*.tar.gz
   cd 灵值生态园智能体移植包

2. 安装依赖
   pip install -r requirements.txt

3. 添加收款码文件（必须！）
   - 将个人微信收款码.jpg 放到 assets/ 目录
   - 将个人支付宝收款码.jpg 放到 assets/ 目录

4. 初始化数据库
   cd src/auth
   python init_data.py
   python init_ecosystem.py
   python init_project.py
   cd ../..

5. 启动服务
   python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

6. 访问服务
   - API服务：http://localhost:8000
   - API文档：http://localhost:8000/docs

默认账号
========================================
邮箱：xufeng@meiyueart.cn
密码：Xf@071214

⚠️ 部署后请立即修改默认密码！

技术支持
========================================
邮箱：meiyue@meiyueart.cn
官网：www.meiyueart.cn
文档：docs.meiyueart.cn

详细文档
========================================
- 全景移植包使用指南.md
- 灵值生态园智能体移植包/README_移植指南.md
- 灵值生态园智能体移植包/Windows部署指南.md

========================================
版权所有 © 2026 媄月商业
========================================
EOF

# 创建版本文件
echo -e "${BLUE}[INFO]${NC} 创建版本信息..."
cat > ${TEMP_DIR}/VERSION.txt << EOF
灵值生态园智能体
========================================
项目名称：灵值生态园智能体
版本：v5.1
发布日期：2026-01-25
发布类型：正式发布

核心功能
========================================
- 智能体核心功能（知识库检索、图像生成、联网搜索）
- 权限管理系统（50+ API接口）
- 生态机制系统（15+ API接口）
- 项目参与和团队组建系统（10+ API接口）
- 数据库管理系统（8+ API接口）
- 收款码和支付方式说明

技术栈
========================================
- Python 3.10+
- FastAPI
- LangChain
- LangGraph
- SQLAlchemy

联系信息
========================================
邮箱：meiyue@meiyueart.cn
官网：www.meiyueart.cn
文档：docs.meiyueart.cn

========================================
版权所有 © 2026 媄月商业
========================================
EOF

# 创建安装脚本
echo -e "${BLUE}[INFO]${NC} 创建安装脚本..."
cat > ${TEMP_DIR}/install.sh << 'EOF'
#!/bin/bash
# 灵值生态园智能体 - 快速安装脚本

echo "========================================"
echo "  灵值生态园智能体 - 快速安装"
echo "========================================"
echo ""

# 检查 Python 版本
echo "[1/5] 检查 Python 版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "当前 Python 版本：$python_version"

# 安装依赖
echo ""
echo "[2/5] 安装依赖..."
pip3 install -r requirements.txt

# 初始化数据库
echo ""
echo "[3/5] 初始化数据库..."
cd src/auth
python3 init_data.py
python3 init_ecosystem.py
python3 init_project.py
cd ../..

echo ""
echo "[4/5] 添加收款码文件..."
echo "请将以下文件添加到 assets/ 目录："
echo "  - 个人微信收款码.jpg"
echo "  - 个人支付宝收款码.jpg"
read -p "按回车键继续..."

# 启动服务
echo ""
echo "[5/5] 启动服务..."
echo "服务地址：http://localhost:8000"
echo "API文档：http://localhost:8000/docs"
echo ""
read -p "是否立即启动服务？(y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
fi

echo ""
echo "========================================"
echo "  安装完成！"
echo "========================================"
EOF

chmod +x ${TEMP_DIR}/install.sh

# 创建 Windows 安装脚本
cat > ${TEMP_DIR}/install.bat << 'EOF'
@echo off
chcp 65001 >nul
echo ========================================
echo   灵值生态园智能体 - 快速安装
echo ========================================
echo.

echo [1/5] 检查 Python 版本...
python --version
if %errorlevel% neq 0 (
    echo 错误：未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

echo.
echo [2/5] 安装依赖...
pip install -r requirements.txt

echo.
echo [3/5] 初始化数据库...
cd src\auth
python init_data.py
python init_ecosystem.py
python init_project.py
cd ..\..

echo.
echo [4/5] 添加收款码文件...
echo 请将以下文件添加到 assets\ 目录：
echo   - 个人微信收款码.jpg
echo   - 个人支付宝收款码.jpg
pause

echo.
echo [5/5] 启动服务...
echo 服务地址：http://localhost:8000
echo API文档：http://localhost:8000/docs
echo.
set /p start="是否立即启动服务？(y/n): "
if /i "%start%"=="y" (
    python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
)

echo.
echo ========================================
echo   安装完成！
echo ========================================
pause
EOF

# 统计文件
echo -e "${BLUE}[INFO]${NC} 统计文件信息..."
TOTAL_FILES=$(find ${TEMP_DIR} -type f | wc -l)
TOTAL_DIRS=$(find ${TEMP_DIR} -type d | wc -l)
TOTAL_SIZE=$(du -sh ${TEMP_DIR} | cut -f1)

# 创建压缩包
echo -e "${BLUE}[INFO]${NC} 创建压缩包..."
cd ${TEMP_DIR}
tar -czf ../${FINAL_DIR}/${RELEASE_NAME}.tar.gz .
cd ..

# 计算校验和
echo -e "${BLUE}[INFO]${NC} 计算校验和..."
cd ${FINAL_DIR}
MD5_HASH=$(md5sum ${RELEASE_NAME}.tar.gz | cut -d' ' -f1)
SHA256_HASH=$(sha256sum ${RELEASE_NAME}.tar.gz | cut -d' ' -f1)

# 创建验证文件
cat > ${RELEASE_NAME}_验证信息.txt << EOF
灵值生态园智能体 - 发布包验证信息
========================================
包名：${RELEASE_NAME}.tar.gz
版本：v5.1
发布日期：$(date +%Y-%m-%d)
文件数：${TOTAL_FILES}
目录数：${TOTAL_DIRS}
大小：$(du -h ${RELEASE_NAME}.tar.gz | cut -f1)

MD5 校验和
========================================
${MD5_HASH}

SHA256 校验和
========================================
${SHA256_HASH}

验证方法
========================================
# Linux/Mac
md5sum ${RELEASE_NAME}.tar.gz
sha256sum ${RELEASE_NAME}.tar.gz

# Windows PowerShell
Get-FileHash ${RELEASE_NAME}.tar.gz -Algorithm MD5
Get-FileHash ${RELEASE_NAME}.tar.gz -Algorithm SHA256

解压后验证
========================================
# 解压
tar -xzf ${RELEASE_NAME}.tar.gz

# 查看文件列表
ls -la

# 查看版本信息
cat VERSION.txt
cat 发布说明.txt

========================================
版权所有 © 2026 媄月商业
========================================
EOF

cd ..

# 清理临时目录
echo -e "${BLUE}[INFO]${NC} 清理临时文件..."
rm -rf ${TEMP_DIR}

# 输出结果
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  打包完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "📦 发布包信息："
echo "  - 文件名：${FINAL_DIR}/${RELEASE_NAME}.tar.gz"
echo "  - 文件数：${TOTAL_FILES}"
echo "  - 目录数：${TOTAL_DIRS}"
echo "  - 大小：$(du -h ${FINAL_DIR}/${RELEASE_NAME}.tar.gz | cut -f1)"
echo ""
echo "📄 附加文件："
echo "  - ${FINAL_DIR}/${RELEASE_NAME}_验证信息.txt"
echo ""
echo "🔐 校验和："
echo "  - MD5：${MD5_HASH}"
echo "  - SHA256：${SHA256_HASH}"
echo ""
echo "🚀 下一步："
echo "  1. 下载发布包：${FINAL_DIR}/${RELEASE_NAME}.tar.gz"
echo "  2. 验证完整性：cat ${FINAL_DIR}/${RELEASE_NAME}_验证信息.txt"
echo "  3. 解压并安装：tar -xzf ${RELEASE_NAME}.tar.gz"
echo "  4. 运行安装脚本：./install.sh (Linux/Mac) 或 install.bat (Windows)"
echo ""
echo -e "${GREEN}✅ 发布包打包完成！${NC}"
echo ""

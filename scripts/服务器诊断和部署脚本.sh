#!/bin/bash

# ==============================================
# 情绪系统 v8.1 - 服务器诊断和部署脚本
# ==============================================

echo "==============================================="
echo "情绪系统 v8.1 - 服务器诊断"
echo "==============================================="

# 1. 检查项目路径
echo ""
echo "[1] 检查项目路径..."
if [ -d "/var/www/backend" ]; then
    echo "✅ 项目路径存在: /var/www/backend"
    ls -la /var/www/backend/
else
    echo "❌ 项目路径不存在: /var/www/backend"
    echo "正在搜索项目路径..."
    find / -name "app.py" -type f 2>/dev/null | grep -v snap | head -5
fi

# 2. 检查目录结构
echo ""
echo "[2] 检查目录结构..."
if [ -d "/var/www/backend" ]; then
    echo "后端目录结构:"
    ls -la /var/www/backend/src/ 2>/dev/null || echo "❌ src 目录不存在"
    ls -la /var/www/backend/src/storage/ 2>/dev/null || echo "❌ storage 目录不存在"
fi

# 3. 检查 Python 进程
echo ""
echo "[3] 检查 Python 进程..."
ps aux | grep python | grep -v unattended | grep -v grep

# 4. 检查数据库
echo ""
echo "[4] 检查数据库..."
which psql || echo "⚠️  psql 未安装，将安装..."
apt install -y postgresql-client-common postgresql-client 2>/dev/null || echo "⚠️  安装失败，可能需要手动安装"

# 5. 创建必要的目录
echo ""
echo "[5] 创建必要的目录..."
mkdir -p /var/www/backend/src/storage/database/shared
mkdir -p /var/www/backend/src/storage/database
mkdir -p /var/www/backend/src/tools
mkdir -p /var/www/backend/config
mkdir -p /var/www/backend/src/agents
mkdir -p /var/www/backend/scripts
echo "✅ 目录创建完成"

# 6. 测试数据库连接
echo ""
echo "[6] 测试数据库连接..."
export PGPASSWORD="Meiyue@root123"
if command -v psql &> /dev/null; then
    psql -h localhost -U postgres -d lingzhi_db -c "SELECT version();" 2>&1 | head -5
else
    echo "⚠️  psql 不可用，跳过数据库测试"
fi

# 7. 检查现有文件
echo ""
echo "[7] 检查现有文件..."
if [ -d "/var/www/backend" ]; then
    echo "查找 model.py:"
    find /var/www/backend -name "model.py" -type f 2>/dev/null | head -3
    echo ""
    echo "查找 emotion_tools.py:"
    find /var/www/backend -name "emotion_tools.py" -type f 2>/dev/null | head -3
    echo ""
    echo "查找 agent_llm_config.json:"
    find /var/www/backend -name "agent_llm_config.json" -type f 2>/dev/null | head -3
fi

echo ""
echo "==============================================="
echo "诊断完成"
echo "==============================================="

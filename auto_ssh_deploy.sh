#!/bin/bash
#
# 自动SSH部署脚本（交互式）
#

set -e

SERVER_HOST="123.56.142.143"
SERVER_USER="root"
SERVER_PORT="22"

DEPLOY_COMMAND='curl -fsSL "https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/deploy_frontend_from_storage_c62bf332.sh?sign=1770417491-0-0-0" | bash'

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║        灵值生态园 - 自动SSH部署工具                            ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo "服务器: $SERVER_HOST"
echo "用户: $SERVER_USER"
echo ""

# 检查是否安装了sshpass
if ! command -v sshpass &> /dev/null; then
    echo "⚠️  sshpass未安装，尝试安装..."
    apt-get update -qq && apt-get install -y -qq sshpass
fi

# 尝试自动SSH连接（使用密钥）
echo "🔍 尝试使用SSH密钥连接..."
if ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 $SERVER_USER@$SERVER_HOST "echo 'Connected via SSH key'" 2>/dev/null; then
    echo "✅ 使用SSH密钥连接成功"
    echo ""
    echo "📤 执行部署命令..."
    ssh $SERVER_USER@$SERVER_HOST "$DEPLOY_COMMAND"
    exit 0
fi

echo "❌ 无法使用SSH密钥连接"
echo ""
echo "📝 请提供SSH密码："

# 读取密码（不显示）
read -s -p "密码: " SSH_PASSWORD
echo ""

# 使用sshpass执行命令
echo ""
echo "📤 连接到服务器并执行部署..."
echo ""

sshpass -p "$SSH_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_HOST "$DEPLOY_COMMAND"

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                    部署完成                                      ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo "📱 现在请访问：https://meiyueart.com"
echo ""
echo "💡 清除浏览器缓存："
echo "   Windows: Ctrl + Shift + R"
echo "   Mac: Cmd + Shift + R"
echo ""

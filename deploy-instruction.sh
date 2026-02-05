#!/bin/bash
# ==========================================
#  梦幻版页面部署 - 在服务器上执行
# ==========================================

# 一键部署命令
DEPLOY_COMMAND='cd /root && wget https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/quick-deploy_ff392e4c.sh?sign=1770356381-9bd68d84c1-0-0faebe802da3a4846774e91460f53edc18d10274a85fbd8e40c1e84cd1f6e1ec -O deploy.sh && bash deploy.sh'

echo "=========================================="
echo "  🚀 梦幻版页面部署"
echo "=========================================="
echo ""
echo "服务器: 123.56.142.143"
echo "用户: root"
echo ""
echo "----------------------------------------"
echo "  执行以下命令完成部署："
echo "----------------------------------------"
echo ""
echo "$DEPLOY_COMMAND"
echo ""
echo "----------------------------------------"
echo "  或复制以下步骤："
echo "----------------------------------------"
echo ""
echo "步骤 1: 下载部署脚本"
echo "cd /root"
echo "wget https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/quick-deploy_ff392e4c.sh?sign=1770356381-9bd68d84c1-0-0faebe802da3a4846774e91460f53edc18d10274a85fbd8e40c1e84cd1f6e1ec -O deploy.sh"
echo ""
echo "步骤 2: 执行部署"
echo "bash deploy.sh"
echo ""
echo "----------------------------------------"
echo "  部署完成后访问："
echo "----------------------------------------"
echo ""
echo "🎨 https://meiyueart.com/dream-selector"
echo "🔐 https://meiyueart.com/login-full"
echo "📝 https://meiyueart.com/register-full"
echo ""
echo "提示：清除浏览器缓存 (Ctrl+Shift+R)"
echo ""
echo "=========================================="
echo ""

# 如果在服务器上，自动执行
if [ -f "/root/deploy.sh" ] && [ "$1" == "--auto" ]; then
    echo "自动执行部署..."
    bash /root/deploy.sh
fi

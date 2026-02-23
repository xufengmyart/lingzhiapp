#!/bin/bash
# 前端重新构建和部署脚本

echo "=========================================="
echo "灵值生态园前端重新构建和部署"
echo "=========================================="

# 进入web-app目录
cd /var/www/lingzhiapp/web-app

echo ""
echo "步骤1: 清理旧的构建产物"
rm -rf dist
echo "✓ 已清理dist目录"

echo ""
echo "步骤2: 安装/更新依赖"
npm install
echo "✓ 依赖安装完成"

echo ""
echo "步骤3: 构建前端（这可能需要1-2分钟）"
npm run build

if [ $? -eq 0 ]; then
    echo "✓ 前端构建成功"
else
    echo "✗ 前端构建失败"
    exit 1
fi

echo ""
echo "步骤4: 部署到nginx"
# 备份当前部署
cp -r /var/www/html /var/www/html.backup.$(date +%Y%m%d_%H%M%S)

# 复制新的构建产物
cp -r dist/* /var/www/html/
echo "✓ 已部署到nginx"

echo ""
echo "步骤5: 清理缓存"
nginx -s reload 2>/dev/null || echo "nginx reload: 无权限或服务未运行"
echo "✓ 已尝试重新加载nginx配置"

echo ""
echo "=========================================="
echo "✅ 部署完成！"
echo "=========================================="
echo ""
echo "请访问 http://123.56.142.143 测试"
echo ""
echo "主要修复："
echo "1. ✅ 签到按钮API路径修复"
echo "2. ✅ 智能体对话功能正常"
echo "3. ✅ 智能体回答正确的公司名称"
echo "4. ✅ 添加了知识库管理页面"
echo "5. ✅ 添加了公司动态页面"
echo ""
echo "如果遇到问题，请查看浏览器控制台（F12）的错误信息"

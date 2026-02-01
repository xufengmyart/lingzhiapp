#!/bin/bash

# 快速测试脚本 - 验证公网访问修复

# 切换到项目目录
cd "$(dirname "$0")"

echo "======================================"
echo "公网访问修复验证"
echo "======================================"

# 检查后端服务
echo ""
echo "1. 检查后端服务..."
if curl -s http://localhost:8001/api/health | grep -q "ok"; then
    echo "✓ 后端服务运行正常"
else
    echo "✗ 后端服务未运行或异常"
    echo "  请启动后端: cd admin-backend && python app.py"
    exit 1
fi

# 检查前端构建
echo ""
echo "2. 检查前端构建..."
if [ -d "public" ] && [ -f "public/index.html" ]; then
    echo "✓ 前端已构建 (输出目录: public)"
else
    echo "✗ 前端未构建"
    echo "  请构建前端: cd web-app && npm run build"
    exit 1
fi

# 测试登录API
echo ""
echo "3. 测试登录API..."
LOGIN_RESULT=$(curl -s -X POST http://localhost:8001/api/login \
    -H "Content-Type: application/json" \
    -d '{"username": "testuser2_updated", "password": "password123"}')

if echo "$LOGIN_RESULT" | grep -q "success.*true"; then
    echo "✓ 登录API正常"
else
    echo "✗ 登录API异常"
    echo "  响应: $LOGIN_RESULT"
    exit 1
fi

# 检查智能检测功能
echo ""
echo "4. 检查前端配置..."
if grep -q "getApiBaseURL" web-app/src/services/api.ts; then
    echo "✓ 智能检测功能已添加"
else
    echo "✗ 智能检测功能未添加"
    exit 1
fi

# 检查API配置页面
echo ""
echo "5. 检查API配置页面..."
if [ -f "web-app/src/pages/ApiConfig.tsx" ]; then
    echo "✓ API配置页面已创建"
else
    echo "✗ API配置页面未创建"
    exit 1
fi

echo ""
echo "======================================"
echo "验证完成！"
echo "======================================"
echo ""
echo "所有检查通过！"
echo ""
echo "后续步骤:"
echo "  1. 确保后端服务运行在 8001 端口"
echo "  2. 将 web-app/dist 部署到 Web 服务器"
echo "  3. 通过公网IP访问系统"
echo "  4. 如果仍有问题，访问 http://YOUR_DOMAIN/api-config"
echo ""
echo "详细文档:"
echo "  - docs/500_ERROR_SOLUTION.md"
echo "  - docs/PUBLIC_DEPLOYMENT.md"
echo "  - docs/QUICK_FIX_500_ERROR.md"
echo ""

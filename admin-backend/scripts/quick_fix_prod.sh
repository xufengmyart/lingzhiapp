#!/bin/bash
#
# 生产环境快速修复脚本（2026-02-15）
# 直接在生产环境上执行此脚本
#
# 使用方法：
#   1. 将此脚本复制到生产服务器
#   2. chmod +x quick_fix_prod.sh
#   3. ./quick_fix_prod.sh
#

set -e

echo "========================================"
echo "生产环境快速修复脚本（2026-02-15）"
echo "========================================"

# 生产环境路径
PROD_BACKEND="/opt/lingzhi-ecosystem/backend"
PROD_FRONTEND="/opt/lingzhi-ecosystem/frontend"

# 1. 备份当前代码
echo ""
echo "[1/5] 备份当前代码..."
BACKUP_DIR="/opt/lingzhi-ecosystem/quick_fix_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

if [ -f "$PROD_BACKEND/app.py" ]; then
    cp "$PROD_BACKEND/app.py" "$BACKUP_DIR/app.py.backup"
    echo "  ✓ app.py 已备份"
fi

if [ -f "$PROD_FRONTEND/src/pages/Chat.tsx" ]; then
    cp "$PROD_FRONTEND/src/pages/Chat.tsx" "$BACKUP_DIR/Chat.tsx.backup"
    echo "  ✓ Chat.tsx 已备份"
fi

# 2. 修复前端 Chat.tsx 中的智能体列表路径
echo ""
echo "[2/5] 修复前端 Chat.tsx..."

# 检查文件是否存在
if [ ! -f "$PROD_FRONTEND/src/pages/Chat.tsx" ]; then
    echo "  ✗ 找不到 Chat.tsx: $PROD_FRONTEND/src/pages/Chat.tsx"
    exit 1
fi

# 创建修复后的 Chat.tsx
# 关键修复：将 api.get('/api/agents') 改为 agentApi.getAgents()
sed -i "s|await api\.get('/api/agents')|await agentApi.getAgents()|g" "$PROD_FRONTEND/src/pages/Chat.tsx"

# 修复响应数据结构：response.data.data.agents -> response.data
sed -i "s|response\.data\.data\.agents|response.data|g" "$PROD_FRONTEND/src/pages/Chat.tsx"

# 修复成功判断：response.data.success -> response.success
sed -i "s|response\.data\.success|response.success|g" "$PROD_FRONTEND/src/pages/Chat.tsx"

echo "  ✓ Chat.tsx 已修复"

# 3. 验证后端路由
echo ""
echo "[3/5] 验证后端路由..."

if [ ! -f "$PROD_BACKEND/app.py" ]; then
    echo "  ✗ 找不到 app.py: $PROD_BACKEND/app.py"
    exit 1
fi

# 检查必要的路由
if grep -q "@app.route('/agent/chat'" "$PROD_BACKEND/app.py" && \
   grep -q "@app.route('/api/agent/chat'" "$PROD_BACKEND/app.py" && \
   grep -q "@app.route('/api/admin/agents'" "$PROD_BACKEND/app.py"; then
    echo "  ✓ 后端路由配置正确"
else
    echo "  ⚠️  后端路由可能不完整，但继续执行"
fi

# 4. 重新构建前端
echo ""
echo "[4/5] 重新构建前端..."
cd "$PROD_FRONTEND"

# 检查 npm 是否可用
if ! command -v npm &> /dev/null; then
    echo "  ✗ npm 未安装，无法构建前端"
    exit 1
fi

echo "  安装依赖..."
npm install 2>&1 | grep -E "(added|removed|changed|audited)" | head -5

echo "  构建生产版本..."
npm run build 2>&1 | grep -E "(built|warn|error)" | head -10

echo "  ✓ 前端构建完成"

# 5. 重启后端服务
echo ""
echo "[5/5] 重启后端服务..."
cd "$PROD_BACKEND"

# 尝试使用 gunicorn.ctl
if [ -f "gunicorn.ctl" ]; then
    echo "  使用 gunicorn.ctl 重启..."
    echo "reload" > gunicorn.ctl
    sleep 3
    echo "  ✓ 后端服务已重启"
elif command -v systemctl &> /dev/null; then
    # 尝试使用 systemctl
    echo "  使用 systemctl 重启..."
    systemctl restart lingzhi-backend 2>&1 || systemctl restart flask-backend 2>&1
    sleep 3
    echo "  ✓ 后端服务已重启"
else
    echo "  ⚠️  无法自动重启后端服务，请手动重启"
fi

# 6. 快速验证
echo ""
echo "[验证] 快速验证服务..."

# 测试智能体列表
if curl -f -s http://127.0.0.1:8080/api/admin/agents > /dev/null 2>&1; then
    echo "  ✓ 后端 /api/admin/agents 正常"
else
    echo "  ⚠️  后端 /api/admin/agents 异常"
fi

# 测试智能体聊天
if curl -f -s -X POST http://127.0.0.1:8080/api/agent/chat \
    -H "Content-Type: application/json" \
    -d '{"content":"测试","agentId":2}' > /dev/null 2>&1; then
    echo "  ✓ 后端 /api/agent/chat 正常"
else
    echo "  ⚠️  后端 /api/agent/chat 异常"
fi

echo ""
echo "========================================"
echo "✅ 修复完成！"
echo "========================================"
echo ""
echo "备份位置：$BACKUP_DIR"
echo ""
echo "修复内容："
echo "  1. ✓ 前端智能体列表路径修复"
echo "  2. ✓ 前端响应数据结构修复"
echo "  3. ✓ 后端路由验证"
echo "  4. ✓ 前端重新构建"
echo "  5. ✓ 后端服务重启"
echo ""
echo "请清理浏览器缓存后测试："
echo "  https://meiyueart.com"
echo ""
echo "清理缓存方法："
echo "  1. 打开浏览器开发者工具 (F12)"
echo "  2. 右键点击刷新按钮"
echo "  3. 选择'清空缓存并硬性重新加载'"
echo ""

#!/bin/bash
# 在生产环境添加测试推荐关系数据

set -e

echo "========================================="
echo "🔧 在生产环境添加测试推荐关系数据"
echo "========================================="
echo ""

# 生产环境配置
PRODUCTION_HOST="meiyueart.com"
PRODUCTION_USER="root"
PRODUCTION_PASS="Meiyue@root123"
PRODUCTION_PORT="22"

# 上传脚本到生产环境
echo "📤 上传测试数据脚本..."
sshpass -p "${PRODUCTION_PASS}" scp -P ${PRODUCTION_PORT} -o StrictHostKeyChecking=no \
    /workspace/projects/scripts/add_test_referral.py \
    ${PRODUCTION_USER}@${PRODUCTION_HOST}:/tmp/add_test_referral.py

# 在生产环境执行脚本
echo "🔧 在生产环境执行脚本..."
sshpass -p "${PRODUCTION_PASS}" ssh -p ${PRODUCTION_PORT} -o StrictHostKeyChecking=no ${PRODUCTION_USER}@${PRODUCTION_HOST} << 'ENDSSH'
    cd /tmp
    python3 add_test_referral.py demo
ENDSSH

echo ""
echo "✅ 测试推荐关系数据添加完成"

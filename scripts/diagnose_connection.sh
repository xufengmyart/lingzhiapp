#!/bin/bash

# 连接问题快速诊断脚本
# 用于快速定位连接被拒绝的原因

CLOUD_SERVER="123.56.142.143"

echo "========================================="
echo "  连接问题快速诊断"
echo "========================================="
echo ""

# 1. 测试Ping
echo "[1/5] 测试网络连接 (Ping)..."
if ping -c 3 ${CLOUD_SERVER} > /dev/null 2>&1; then
    echo "✓ Ping成功，网络连接正常"
else
    echo "✗ Ping失败，网络连接异常"
    exit 1
fi
echo ""

# 2. 测试SSH连接
echo "[2/5] 测试SSH连接..."
if ssh -o ConnectTimeout=5 -o BatchMode=yes root@${CLOUD_SERVER} "echo 'SSH连接成功'" 2>/dev/null; then
    echo "✓ SSH连接成功"
    SSH_AVAILABLE=true
else
    echo "⚠️  SSH连接失败（可能需要密码或密钥）"
    echo "  可以手动测试：ssh root@${CLOUD_SERVER}"
    SSH_AVAILABLE=false
fi
echo ""

# 3. 测试80端口
echo "[3/5] 测试HTTP端口 (80)..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://${CLOUD_SERVER} 2>&1)
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "✓ 80端口可访问，返回状态码: ${HTTP_CODE}"
    HTTP_AVAILABLE=true
else
    echo "✗ 80端口无法访问"
    if [ "$HTTP_CODE" = "000" ]; then
        echo "  原因：连接被拒绝或超时"
    else
        echo "  返回状态码: ${HTTP_CODE}"
    fi
    HTTP_AVAILABLE=false
fi
echo ""

# 4. 测试8001端口
echo "[4/5] 测试API端口 (8001)..."
API_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://${CLOUD_SERVER}:8001/api/login 2>&1)
if [ "$API_CODE" = "200" ] || [ "$API_CODE" = "404" ] || [ "$API_CODE" = "405" ]; then
    echo "✓ 8001端口可访问，返回状态码: ${API_CODE}"
    API_AVAILABLE=true
else
    echo "✗ 8001端口无法访问"
    if [ "$API_CODE" = "000" ]; then
        echo "  原因：连接被拒绝或超时"
    else
        echo "  返回状态码: ${API_CODE}"
    fi
    API_AVAILABLE=false
fi
echo ""

# 5. 诊断结果和建议
echo "[5/5] 诊断结果和建议"
echo "========================================="
echo ""

if [ "$HTTP_AVAILABLE" = true ] && [ "$API_AVAILABLE" = true ]; then
    echo "✅ 所有端口都可以正常访问！"
    echo ""
    echo "可以访问："
    echo "  - Web应用: http://${CLOUD_SERVER}"
    echo "  - API接口: http://${CLOUD_SERVER}:8001/api/"
    echo ""
elif [ "$HTTP_AVAILABLE" = false ] && [ "$SSH_AVAILABLE" = true ]; then
    echo "❌ 问题分析："
    echo "  - 网络连接正常（Ping成功）"
    echo "  - SSH连接正常"
    echo "  - 但HTTP端口无法访问"
    echo ""
    echo "🔍 最可能的原因："
    echo "  1. 阿里云安全组未开放80端口"
    echo "  2. 服务器防火墙未开放80端口"
    echo "  3. Nginx未运行或未监听80端口"
    echo ""
    echo "🚀 解决方案："
    echo ""
    echo "  方案1：开放阿里云安全组（推荐）"
    echo "  1. 登录阿里云控制台: https://ecs.console.aliyun.com/"
    echo "  2. ECS实例 -> 安全组 -> 配置规则"
    echo "  3. 添加入方向规则："
    echo "     - 端口范围: 80/80"
    echo "     - 协议类型: TCP"
    echo "     - 授权对象: 0.0.0.0/0"
    echo ""
    echo "  方案2：执行一键部署和修复脚本"
    echo "  cd /workspace/projects"
    echo "  ./scripts/quick_deploy_and_fix.sh"
    echo ""
    echo "  方案3：手动检查服务器状态"
    echo "  ssh root@${CLOUD_SERVER}"
    echo "  systemctl status nginx"
    echo "  netstat -tlnp | grep :80"
    echo ""
elif [ "$SSH_AVAILABLE" = false ]; then
    echo "❌ 问题分析："
    echo "  - SSH连接失败"
    echo ""
    echo "🔍 可能的原因："
    echo "  1. SSH密钥未配置"
    echo "  2. 服务器SSH服务未运行"
    echo "  3. 阿里云安全组未开放22端口"
    echo ""
    echo "🚀 解决方案："
    echo "  1. 配置SSH密钥："
    echo "     ssh-copy-id root@${CLOUD_SERVER}"
    echo ""
    echo "  2. 或手动登录测试："
    echo "     ssh root@${CLOUD_SERVER}"
    echo ""
else
    echo "⚠️  未知问题，请手动检查"
    echo ""
    echo "建议执行："
    echo "  cd /workspace/projects"
    echo "  ./scripts/quick_deploy_and_fix.sh"
    echo ""
fi

echo "========================================="
echo "详细文档请查看：docs/CONNECTION_REFUSED_FIX.md"
echo "========================================="

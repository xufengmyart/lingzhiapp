#!/bin/bash

# 云服务器检查脚本
# 用于排查连接被拒绝的问题

CLOUD_SERVER="123.56.142.143"

echo "========================================="
echo "  云服务器连接问题诊断"
echo "========================================="
echo ""

# 1. 检查SSH连接
echo "[1/6] 检查SSH连接..."
if ssh -o ConnectTimeout=5 -o BatchMode=yes root@${CLOUD_SERVER} "echo 'SSH连接成功'" 2>/dev/null; then
    echo "✓ SSH连接正常"
else
    echo "✗ SSH连接失败"
    echo "  请确保已配置SSH密钥或可以手动登录"
fi
echo ""

# 2. 检查开放的端口
echo "[2/6] 检查服务器开放的端口..."
ssh -o ConnectTimeout=5 -o BatchMode=yes root@${CLOUD_SERVER} << 'ENDSSH'
# 检查防火墙状态
if command -v firewall-cmd &> /dev/null; then
    echo "Firewalld状态:"
    firewall-cmd --list-ports 2>/dev/null || echo "未配置端口"
fi

if command -v iptables &> /dev/null; then
    echo "Iptables规则:"
    iptables -L -n | grep -E "dpt:(80|8001)" || echo "未找到80或8001端口规则"
fi

# 检查监听的端口
echo ""
echo "监听的端口:"
netstat -tlnp 2>/dev/null | grep -E ":80 |:8001 " || ss -tlnp 2>/dev/null | grep -E ":80 |:8001 " || echo "未找到80或8001端口监听"
ENDSSH
echo ""

# 3. 检查Web服务状态
echo "[3/6] 检查Web服务状态..."
ssh -o ConnectTimeout=5 -o BatchMode=yes root@${CLOUD_SERVER} << 'ENDSSH'
# 检查Nginx
echo "Nginx状态:"
if command -v nginx &> /dev/null; then
    systemctl status nginx 2>/dev/null | grep -E "Active|running" || echo "Nginx未运行"
    ps aux | grep nginx | grep -v grep || echo "Nginx进程不存在"
else
    echo "Nginx未安装"
fi

# 检查Python后端
echo ""
echo "Python后端状态:"
ps aux | grep "python.*app.py" | grep -v grep || echo "Python后端未运行"

# 检查端口占用
echo ""
echo "端口占用情况:"
netstat -tlnp 2>/dev/null | grep -E ":80 |:8001 " || ss -tlnp 2>/dev/null | grep -E ":80 |:8001 "
ENDSSH
echo ""

# 4. 检查项目文件
echo "[4/6] 检查项目文件..."
ssh -o ConnectTimeout=5 -o BatchMode=yes root@${CLOUD_SERVER} << 'ENDSSH'
if [ -d "/root/lingzhi-ecosystem" ]; then
    echo "✓ 项目目录存在"
    ls -la /root/lingzhi-ecosystem/
else
    echo "✗ 项目目录不存在，需要先部署"
fi
ENDSSH
echo ""

# 5. 测试本地端口访问
echo "[5/6] 测试服务器本地端口访问..."
ssh -o ConnectTimeout=5 -o BatchMode=yes root@${CLOUD_SERVER} << 'ENDSSH'
# 测试80端口
if curl -I http://127.0.0.1:80 --connect-timeout 2 2>/dev/null | head -1; then
    echo "✓ 本地80端口可访问"
else
    echo "✗ 本地80端口不可访问"
fi

# 测试8001端口
if curl -I http://127.0.0.1:8001/api/login --connect-timeout 2 2>/dev/null | head -1; then
    echo "✓ 本地8001端口可访问"
else
    echo "✗ 本地8001端口不可访问"
fi
ENDSSH
echo ""

# 6. 总结和建议
echo "[6/6] 诊断总结"
echo "========================================="
echo ""
echo "常见解决方案："
echo ""
echo "1. 如果阿里云安全组未开放80端口："
echo "   - 登录阿里云控制台"
echo "   - ECS实例 -> 安全组 -> 配置规则"
echo "   - 添加入方向规则：端口80/80，授权对象0.0.0.0/0"
echo ""
echo "2. 如果服务器防火墙阻止："
echo "   - 执行: systemctl stop firewalld (临时关闭)"
echo "   - 或执行: firewall-cmd --add-port=80/tcp --permanent"
echo ""
echo "3. 如果Web服务未运行："
echo "   - 检查服务状态: systemctl status nginx"
echo "   - 启动服务: systemctl start nginx"
echo ""
echo "4. 如果项目未部署："
echo "   - 执行部署脚本: ./scripts/deploy_to_cloud.sh"
echo ""

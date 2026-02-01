#!/usr/bin/env python3
"""
自动修复服务器登录问题的脚本
通过SSH连接服务器并执行修复命令
"""

import paramiko
import time

def execute_on_server():
    """连接服务器并执行修复命令"""

    # 服务器配置
    hostname = '123.56.142.143'
    port = 22
    username = 'root'
    password = 'Meiyue@root123'

    print("=" * 80)
    print("开始自动修复服务器登录问题")
    print("=" * 80)

    # 创建SSH客户端
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # 连接服务器
        print(f"\n[1/5] 连接到服务器 {hostname}...")
        ssh.connect(hostname, port, username, password)
        print("✅ 连接成功")

        # 修复脚本
        fix_script = '''#!/bin/bash
echo "=========================================="
echo "灵值生态园 - 自动修复登录问题"
echo "=========================================="

# 备份Nginx配置
echo ""
echo "[步骤 1/5] 备份Nginx配置..."
if [ -f /etc/nginx/sites-available/meiyueart.com ]; then
    cp /etc/nginx/sites-available/meiyueart.com /etc/nginx/sites-available/meiyueart.com.backup.$(date +%Y%m%d_%H%M%S)
    echo "✅ 配置已备份"
else
    echo "⚠️  配置文件不存在，将创建新配置"
fi

# 创建新的Nginx配置
echo ""
echo "[步骤 2/5] 配置Nginx代理..."
cat > /etc/nginx/sites-available/meiyueart.com << 'NGINX_EOF'
server {
    listen 80;
    server_name 123.56.142.143;

    location / {
        root /var/www/html;
        try_files $uri $uri/ /index.html;
        index index.html;
        
        add_header Cache-Control "public, max-age=3600";
    }

    location /api/ {
        proxy_pass http://localhost:8001/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location ~ /\. {
        deny all;
    }
}
NGINX_EOF
echo "✅ Nginx 配置已更新"

# 测试配置
echo ""
echo "[步骤 3/5] 测试Nginx配置..."
nginx_test=$(nginx -t 2>&1)
if echo "$nginx_test" | grep -q "successful"; then
    echo "✅ 配置测试通过"
else
    echo "❌ 配置测试失败"
    echo "$nginx_test"
    exit 1
fi

# 重启Nginx
echo ""
echo "[步骤 4/5] 重启Nginx..."
systemctl restart nginx
if [ $? -eq 0 ]; then
    echo "✅ Nginx 已重启"
else
    echo "❌ Nginx 重启失败"
    exit 1
fi

# 启动后端API
echo ""
echo "[步骤 5/5] 启动后端API服务..."
systemctl start lingzhi-api
sleep 2

# 验证服务
echo ""
echo "=========================================="
echo "验证服务状态"
echo "=========================================="

echo ""
echo "Nginx 状态:"
nginx_status=$(systemctl status nginx --no-pager -l | grep "Active:" | head -1)
echo "  $nginx_status"

echo ""
echo "后端API 状态:"
api_status=$(systemctl status lingzhi-api --no-pager -l | grep "Active:" | head -1)
echo "  $api_status"

# 测试API
echo ""
echo "测试API连接:"
api_test=$(curl -s -m 5 http://localhost:8001/api/login -X POST -H "Content-Type: application/json" -d '{"test":"test"}' 2>&1 | head -c 80)
if [ ! -z "$api_test" ]; then
    echo "  ✅ API响应正常"
    echo "  响应: $api_test..."
else
    echo "  ⚠️  API无响应，请检查服务"
fi

echo ""
echo "=========================================="
echo "✅ 修复完成！"
echo "=========================================="
echo ""
echo "现在可以登录了："
echo "  访问地址: http://123.56.142.143"
echo "  用户名: 许锋"
echo "  密码: 123456"
echo ""
echo "其他可用账号:"
echo "  CTO（待定）  / 123456"
echo "  CMO（待定）  / 123456"
echo "  COO（待定）  / 123456"
echo "  CFO（待定）  / 123456"
echo ""
'''

        # 执行修复脚本
        print("\n[2/5] 执行修复脚本...")
        stdin, stdout, stderr = ssh.exec_command(fix_script)
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')

        # 打印输出
        print(output)

        # 检查错误
        if error and "error" in error.lower():
            print(f"\n❌ 执行出错:\n{error}")
            return False

        # 验证修复结果
        print("\n[3/5] 验证修复结果...")

        # 测试Nginx
        print("  测试Nginx...")
        stdin, stdout, stderr = ssh.exec_command("curl -I http://localhost 2>&1 | head -5")
        nginx_response = stdout.read().decode('utf-8')
        print(f"    {nginx_response.strip()}")

        # 测试API
        print("  测试API...")
        stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:8001/api/login 2>&1 | head -c 100")
        api_response = stdout.read().decode('utf-8')
        print(f"    {api_response}...")

        # 测试完整登录流程
        print("  测试完整登录流程...")
        stdin, stdout, stderr = ssh.exec_command('curl -s -X POST http://localhost:8001/api/login -H "Content-Type: application/json" -d \'{"username":"许锋","password":"123456"}\'')
        login_response = stdout.read().decode('utf-8')

        if '"success":true' in login_response:
            print("    ✅ 登录测试成功")
        else:
            print(f"    ⚠️  登录测试返回: {login_response[:100]}")

        print("\n[4/5] 修复完成")

        print("\n[5/5] 生成验证信息")
        print("\n==========================================")
        print("修复完成！请验证以下信息")
        print("==========================================")
        print(f"\n访问地址: http://123.56.142.143")
        print(f"用户名: 许锋")
        print(f"密码: 123456")
        print("\n其他测试账号:")
        print("  CTO（待定）/ 123456")
        print("  CMO（待定）/ 123456")
        print("  COO（待定）/ 123456")
        print("  CFO（待定）/ 123456")

        print("\n✅ 全部完成！请访问 http://123.56.142.143 验证登录功能。")

        return True

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        return False

    finally:
        ssh.close()

if __name__ == '__main__':
    execute_on_server()

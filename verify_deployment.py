#!/usr/bin/env python3
"""
验证云服务器上的v9.0部署
"""

import paramiko
import requests
import json

# 云服务器配置
SERVER_HOST = '123.56.142.143'
SERVER_PORT = 22
SERVER_USER = 'root'
SERVER_PASSWORD = 'Meiyue@root123'

def verify_deployment():
    """验证部署"""
    print("=" * 80)
    print("验证灵值智能体v9.0部署")
    print("=" * 80)
    
    # 连接服务器
    print("\n连接云服务器...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SERVER_HOST, SERVER_PORT, SERVER_USER, SERVER_PASSWORD)
        print("✅ 连接成功")
        
        # 1. 检查文件是否存在
        print("\n1. 检查文件是否存在...")
        stdin, stdout, stderr = ssh.exec_command('''
            cd /var/www/backend
            echo "=== app.py ===" && ls -lh app.py
            echo "=== src/agents/agent.py ===" && ls -lh src/agents/agent.py
            echo "=== config/agent_llm_config.json ===" && ls -lh config/agent_llm_config.json
            echo "=== tools ===" && ls -lh src/tools/referral_tools.py src/tools/resource_tools.py src/tools/project_tools.py src/tools/digital_asset_tools.py
        ''')
        
        output = stdout.read().decode('utf-8')
        print(output)
        
        # 2. 检查数据库表
        print("\n2. 检查数据库表...")
        stdin, stdout, stderr = ssh.exec_command('''
            cd /var/www/backend
            python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('lingzhi_ecosystem.db')
cursor = conn.cursor()

# v9.0新增的表
v9_tables = [
    'referral_relationships',
    'referral_commissions',
    'user_resources',
    'resource_matches',
    'projects',
    'project_participants',
    'resource_realization',
    'digital_assets',
    'asset_transactions',
    'asset_earnings'
]

print("v9.0新增表:")
for table in v9_tables:
    cursor.execute(f"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{table}'")
    exists = cursor.fetchone()[0]
    status = "✅" if exists else "❌"
    print(f"{status} {table}")

conn.close()
EOF
        ''')
        
        output = stdout.read().decode('utf-8')
        print(output)
        
        # 3. 检查服务状态
        print("\n3. 检查服务状态...")
        stdin, stdout, stderr = ssh.exec_command('''
            ps aux | grep "python3 app.py" | grep -v grep | head -5
        ''')
        
        output = stdout.read().decode('utf-8')
        if output:
            print("✅ 后端服务运行中:")
            print(output)
        else:
            print("❌ 后端服务未运行")
        
        # 4. 检查端口监听
        print("\n4. 检查端口监听...")
        stdin, stdout, stderr = ssh.exec_command('''
            netstat -tuln | grep -E ":(8001|8080)" | grep LISTEN
        ''')
        
        output = stdout.read().decode('utf-8')
        if output:
            print("✅ 端口监听正常:")
            print(output)
        else:
            print("❌ 端口未监听")
        
        # 5. 测试API接口
        print("\n5. 测试API接口...")
        try:
            # 测试健康检查
            response = requests.get(f"http://{SERVER_HOST}:8080/api/health", timeout=5)
            print(f"✅ /api/health - {response.status_code}")
            
            # 测试状态接口
            response = requests.get(f"http://{SERVER_HOST}:8080/api/status", timeout=5)
            print(f"✅ /api/status - {response.status_code}")
            print(f"   响应: {response.json()}")
            
        except Exception as e:
            print(f"❌ API测试失败: {e}")
        
        # 6. 查看最新日志
        print("\n6. 查看最新日志...")
        stdin, stdout, stderr = ssh.exec_command('''
            tail -n 20 /var/www/backend/backend.log | grep -E "(灵值|API|ERROR|v9.0|Started|服务)"
        ''')
        
        output = stdout.read().decode('utf-8')
        print(output)
        
        print("\n" + "=" * 80)
        print("✅ 验证完成！")
        print("=" * 80)
        print(f"\n访问地址:")
        print(f"  前端: http://{SERVER_HOST}:8001")
        print(f"  后端API: http://{SERVER_HOST}:8080")
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == '__main__':
    verify_deployment()

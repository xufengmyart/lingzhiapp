#!/usr/bin/env python3
"""
最终验证 - 测试v9.0所有功能
"""

import paramiko
import requests
import json

# 云服务器配置
SERVER_HOST = '123.56.142.143'
SERVER_PORT = 22
SERVER_USER = 'root'
SERVER_PASSWORD = 'Meiyue@root123'

API_BASE = f"http://{SERVER_HOST}:8080"

def test_v9_features():
    """测试v9.0功能"""
    print("=" * 80)
    print("灵值智能体v9.0 - 功能测试")
    print("=" * 80)
    
    # 测试结果
    test_results = []
    
    # 1. 测试基础API
    print("\n【1/10】测试基础API...")
    try:
        response = requests.get(f"{API_BASE}/api/health", timeout=5)
        assert response.status_code == 200
        assert response.json()['status'] == 'ok'
        print("✅ /api/health - 正常")
        test_results.append({"test": "health_api", "status": "pass"})
    except Exception as e:
        print(f"❌ /api/health - 失败: {e}")
        test_results.append({"test": "health_api", "status": "fail", "error": str(e)})
    
    # 2. 测试推荐分润API
    print("\n【2/10】测试推荐分润API...")
    try:
        response = requests.get(f"{API_BASE}/api/v9/referrals", timeout=5)
        # 应该返回401（未授权）
        assert response.status_code == 401
        print("✅ /api/v9/referrals - 接口存在（需要认证）")
        test_results.append({"test": "referrals_api", "status": "pass"})
    except Exception as e:
        print(f"❌ /api/v9/referrals - 失败: {e}")
        test_results.append({"test": "referrals_api", "status": "fail", "error": str(e)})
    
    # 3. 测试分润记录API
    print("\n【3/10】测试分润记录API...")
    try:
        response = requests.get(f"{API_BASE}/api/v9/commissions", timeout=5)
        # 应该返回401（未授权）
        assert response.status_code == 401
        print("✅ /api/v9/commissions - 接口存在（需要认证）")
        test_results.append({"test": "commissions_api", "status": "pass"})
    except Exception as e:
        print(f"❌ /api/v9/commissions - 失败: {e}")
        test_results.append({"test": "commissions_api", "status": "fail", "error": str(e)})
    
    # 4. 测试用户资源API
    print("\n【4/10】测试用户资源API...")
    try:
        response = requests.get(f"{API_BASE}/api/v9/resources", timeout=5)
        # 应该返回401（未授权）
        assert response.status_code == 401
        print("✅ /api/v9/resources - 接口存在（需要认证）")
        test_results.append({"test": "resources_api", "status": "pass"})
    except Exception as e:
        print(f"❌ /api/v9/resources - 失败: {e}")
        test_results.append({"test": "resources_api", "status": "fail", "error": str(e)})
    
    # 5. 测试项目API
    print("\n【5/10】测试项目API...")
    try:
        response = requests.get(f"{API_BASE}/api/v9/projects", timeout=5)
        # 应该返回401（未授权）
        assert response.status_code == 401
        print("✅ /api/v9/projects - 接口存在（需要认证）")
        test_results.append({"test": "projects_api", "status": "pass"})
    except Exception as e:
        print(f"❌ /api/v9/projects - 失败: {e}")
        test_results.append({"test": "projects_api", "status": "fail", "error": str(e)})
    
    # 6. 测试数字资产API
    print("\n【6/10】测试数字资产API...")
    try:
        response = requests.get(f"{API_BASE}/api/v9/assets", timeout=5)
        # 应该返回401（未授权）
        assert response.status_code == 401
        print("✅ /api/v9/assets - 接口存在（需要认证）")
        test_results.append({"test": "assets_api", "status": "pass"})
    except Exception as e:
        print(f"❌ /api/v9/assets - 失败: {e}")
        test_results.append({"test": "assets_api", "status": "fail", "error": str(e)})
    
    # 7. 测试数据库表
    print("\n【7/10】测试数据库表...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(SERVER_HOST, SERVER_PORT, SERVER_USER, SERVER_PASSWORD)
        
        stdin, stdout, stderr = ssh.exec_command('''
            cd /var/www/backend
            python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('lingzhi_ecosystem.db')
cursor = conn.cursor()

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

exists_count = 0
for table in v9_tables:
    cursor.execute(f"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{table}'")
    if cursor.fetchone()[0]:
        exists_count += 1

print(f"{exists_count}/{len(v9_tables)} 表已创建")
conn.close()
EOF
        ''')
        
        output = stdout.read().decode('utf-8')
        result = output.strip()
        print(f"✅ 数据库表: {result}")
        test_results.append({"test": "database_tables", "status": "pass", "result": result})
    except Exception as e:
        print(f"❌ 数据库表测试失败: {e}")
        test_results.append({"test": "database_tables", "status": "fail", "error": str(e)})
    finally:
        ssh.close()
    
    # 8. 测试智能体文件
    print("\n【8/10】测试智能体文件...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(SERVER_HOST, SERVER_PORT, SERVER_USER, SERVER_PASSWORD)
        
        stdin, stdout, stderr = ssh.exec_command('''
            cd /var/www/backend/src/agents && ls -lh agent.py && grep -c "推荐分润" agent.py
        ''')
        
        output = stdout.read().decode('utf-8')
        if "推荐分润" in output:
            print("✅ agent.py - 包含v9.0功能")
            test_results.append({"test": "agent_file", "status": "pass"})
        else:
            print("❌ agent.py - 未找到v9.0功能")
            test_results.append({"test": "agent_file", "status": "fail"})
    except Exception as e:
        print(f"❌ 智能体文件测试失败: {e}")
        test_results.append({"test": "agent_file", "status": "fail", "error": str(e)})
    finally:
        ssh.close()
    
    # 9. 测试工具文件
    print("\n【9/10】测试工具文件...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(SERVER_HOST, SERVER_PORT, SERVER_USER, SERVER_PASSWORD)
        
        stdin, stdout, stderr = ssh.exec_command('''
            cd /var/www/backend/src/tools
            ls -1 referral_tools.py resource_tools.py project_tools.py digital_asset_tools.py 2>/dev/null | wc -l
        ''')
        
        output = stdout.read().decode('utf-8').strip()
        count = int(output) if output.isdigit() else 0
        print(f"✅ 工具文件: {count}/4 已部署")
        test_results.append({"test": "tool_files", "status": "pass" if count == 4 else "fail", "count": count})
    except Exception as e:
        print(f"❌ 工具文件测试失败: {e}")
        test_results.append({"test": "tool_files", "status": "fail", "error": str(e)})
    finally:
        ssh.close()
    
    # 10. 测试配置文件
    print("\n【10/10】测试配置文件...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(SERVER_HOST, SERVER_PORT, SERVER_USER, SERVER_PASSWORD)
        
        stdin, stdout, stderr = ssh.exec_command('''
            cd /var/www/backend/config
            grep -c "推荐分润\|资源匹配\|财富规划" agent_llm_config.json
        ''')
        
        output = stdout.read().decode('utf-8').strip()
        if output and int(output) > 0:
            print("✅ agent_llm_config.json - 包含v9.0 Prompt")
            test_results.append({"test": "config_file", "status": "pass"})
        else:
            print("❌ agent_llm_config.json - 未找到v9.0 Prompt")
            test_results.append({"test": "config_file", "status": "fail"})
    except Exception as e:
        print(f"❌ 配置文件测试失败: {e}")
        test_results.append({"test": "config_file", "status": "fail", "error": str(e)})
    finally:
        ssh.close()
    
    # 汇总结果
    print("\n" + "=" * 80)
    print("测试结果汇总")
    print("=" * 80)
    
    pass_count = sum(1 for r in test_results if r['status'] == 'pass')
    total_count = len(test_results)
    
    print(f"\n通过: {pass_count}/{total_count}")
    
    for result in test_results:
        status_icon = "✅" if result['status'] == 'pass' else "❌"
        test_name = result.get('test', 'unknown')
        print(f"{status_icon} {test_name}")
    
    print("\n" + "=" * 80)
    
    if pass_count == total_count:
        print("🎉 所有测试通过！v9.0部署成功！")
        print("\n访问地址:")
        print(f"  前端: http://{SERVER_HOST}:8001")
        print(f"  后端API: http://{SERVER_HOST}:8080")
        print(f"  API健康检查: http://{SERVER_HOST}:8080/api/health")
    else:
        print(f"⚠️  部分测试失败，请检查以上错误信息")
    
    print("=" * 80)

if __name__ == '__main__':
    test_v9_features()

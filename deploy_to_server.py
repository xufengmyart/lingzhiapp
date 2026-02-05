#!/usr/bin/env python3
"""
云服务器部署脚本 - 灵值智能体v9.0升级
将本地文件同步到云服务器
"""

import paramiko
import os
import tarfile
import io

# 云服务器配置
SERVER_HOST = '123.56.142.143'
SERVER_PORT = 22
SERVER_USER = 'root'
SERVER_PASSWORD = 'Meiyue@root123'
SERVER_WORKSPACE = '/var/www/backend'

# 需要同步的文件列表
FILES_TO_SYNC = {
    'admin-backend/app.py': 'app.py',
    'src/tools/referral_tools.py': 'referral_tools.py',
    'src/tools/resource_tools.py': 'resource_tools.py',
    'src/tools/project_tools.py': 'project_tools.py',
    'src/tools/digital_asset_tools.py': 'digital_asset_tools.py',
    'src/agents/agent.py': 'agent.py',
    'config/agent_llm_config.json': 'agent_llm_config.json',
}

def create_tar():
    """创建tar压缩包"""
    print("创建压缩包...")
    tar_buffer = io.BytesIO()
    
    with tarfile.open(fileobj=tar_buffer, mode='w:gz') as tar:
        for local_path, remote_path in FILES_TO_SYNC.items():
            if os.path.exists(local_path):
                print(f"  添加文件: {local_path} -> {remote_path}")
                tar.add(local_path, arcname=remote_path)
            else:
                print(f"  警告: 文件不存在 - {local_path}")
    
    tar_buffer.seek(0)
    return tar_buffer

def deploy_to_server():
    """部署到云服务器"""
    print("=" * 80)
    print("灵值智能体v9.0 - 云服务器部署")
    print("=" * 80)
    
    # 创建压缩包
    tar_buffer = create_tar()
    print(f"压缩包大小: {len(tar_buffer.getvalue()) / 1024:.2f} KB")
    
    # 连接服务器
    print("\n连接云服务器...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SERVER_HOST, SERVER_PORT, SERVER_USER, SERVER_PASSWORD)
        print("✅ 连接成功")
        
        # 创建SFTP客户端
        sftp = ssh.open_sftp()
        
        # 上传压缩包
        print("\n上传压缩包...")
        remote_tar_path = f"{SERVER_WORKSPACE}/v9.0_upgrade.tar.gz"
        
        with sftp.file(remote_tar_path, 'wb') as remote_file:
            remote_file.write(tar_buffer.getvalue())
        
        print(f"✅ 上传完成: {remote_tar_path}")
        
        # 关闭SFTP
        sftp.close()
        
        # 解压文件
        print("\n解压文件...")
        stdin, stdout, stderr = ssh.exec_command(f'''
            cd {SERVER_WORKSPACE}
            tar -xzf v9.0_upgrade.tar.gz
            ls -lh app.py referral_tools.py resource_tools.py project_tools.py digital_asset_tools.py agent.py agent_llm_config.json 2>/dev/null | wc -l
        ''')
        
        output = stdout.read().decode('utf-8')
        print(f"✅ 解压完成，共 {output.strip()} 个文件")
        
        # 移动文件到正确位置
        print("\n移动文件到正确位置...")
        stdin, stdout, stderr = ssh.exec_command(f'''
            cd {SERVER_WORKSPACE}
            
            # 移动agent.py到src/agents/
            mkdir -p src/agents src/tools config
            mv agent.py src/agents/
            
            # 移动工具文件到src/tools/
            mv referral_tools.py src/tools/
            mv resource_tools.py src/tools/
            mv project_tools.py src/tools/
            mv digital_asset_tools.py src/tools/
            
            # 移动配置文件到config/
            mv agent_llm_config.json config/
            
            # app.py留在当前位置
            ls -lh app.py src/agents/agent.py src/tools/*.py config/agent_llm_config.json 2>/dev/null
        ''')
        
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        print("文件分布:")
        print(output)
        if error:
            print(f"警告: {error}")
        
        # 重启后端服务
        print("\n重启后端服务...")
        stdin, stdout, stderr = ssh.exec_command('''
            cd /var/www/backend
            
            # 停止当前服务
            pkill -f "python3 app.py" || true
            sleep 2
            
            # 启动新服务
            nohup python3 app.py > /var/www/backend/backend.log 2>&1 &
            
            sleep 3
            
            # 检查服务状态
            ps aux | grep "python3 app.py" | grep -v grep
        ''')
        
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        print("服务状态:")
        print(output)
        if error:
            print(f"警告: {error}")
        
        # 检查日志
        print("\n检查服务日志...")
        stdin, stdout, stderr = ssh.exec_command('''
            tail -n 30 /var/www/backend/backend.log
        ''')
        
        output = stdout.read().decode('utf-8')
        print(output)
        
        # 清理压缩包
        print("\n清理压缩包...")
        stdin, stdout, stderr = ssh.exec_command(f'rm -f {SERVER_WORKSPACE}/v9.0_upgrade.tar.gz')
        
        print("=" * 80)
        print("✅ 部署完成！")
        print("=" * 80)
        print(f"服务器地址: http://{SERVER_HOST}:8001")
        print("后端API: http://123.56.142.143:8080")
        
    except Exception as e:
        print(f"❌ 部署失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == '__main__':
    deploy_to_server()

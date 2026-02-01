#!/usr/bin/env python3
"""
迁移旧用户数据到新数据库
"""

import paramiko

hostname = '123.56.142.143'
port = 22
username = 'root'
password = 'Meiyue@root123'

print("=" * 80)
print("迁移旧用户数据到新数据库")
print("=" * 80)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(hostname, port, username, password)

    # 创建迁移脚本
    migration_script = '''#!/usr/bin/env python3
import sqlite3
import bcrypt

old_db_path = '/var/www/lingzhiapp/灵值生态园智能体移植包/src/auth/auth.db'
new_db_path = '/var/www/backend/lingzhi_ecosystem.db'

print("连接旧数据库...")
conn_old = sqlite3.connect(old_db_path)
cursor_old = conn_old.cursor()

print("连接新数据库...")
conn_new = sqlite3.connect(new_db_path)
cursor_new = conn_new.cursor()

# 查询新数据库中的用户数量
cursor_new.execute("SELECT COUNT(*) FROM users")
new_user_count = cursor_new.fetchone()[0]

if new_user_count > 0:
    print(f"新数据库已有 {new_user_count} 个用户，跳过迁移")
    conn_old.close()
    conn_new.close()
    exit(0)

print("开始迁移用户...")

# 查询旧用户
cursor_old.execute("SELECT id, name, email, phone, password_hash, created_at FROM users")
old_users = cursor_old.fetchall()

print(f"找到 {len(old_users)} 个旧用户")

migrated_count = 0
for old_user in old_users:
    old_id, name, email, phone, password_hash, created_at = old_user
    
    # 处理重复邮箱
    username = name
    if email:
        cursor_new.execute("SELECT COUNT(*) FROM users WHERE email = ?", (email,))
        email_count = cursor_new.fetchone()[0]
        if email_count > 0:
            username = f"{name}_{old_id}"
            email = f"{username}_migrated@example.com"
    
    # 检查是否是 SHA256 密码
    is_sha256 = len(password_hash) == 64 and all(c in '0123456789abcdef' for c in password_hash.lower())
    
    # 插入用户
    try:
        cursor_new.execute(
            """INSERT INTO users 
               (username, email, phone, password_hash, total_lingzhi, status, created_at, is_verified) 
               VALUES (?, ?, ?, ?, 0, 'active', ?, 1)""",
            (username, email, phone, password_hash, created_at)
        )
        migrated_count += 1
        print(f"  迁移用户: {username} (SHA256: {is_sha256})")
    except Exception as e:
        print(f"  迁移失败 {username}: {e}")

conn_new.commit()
conn_old.close()
conn_new.close()

print(f"\\n迁移完成！共迁移 {migrated_count} 个用户")
'''

    # 上传脚本
    sftp = ssh.open_sftp()
    with sftp.file('/tmp/migrate_users.py', 'w') as f:
        f.write(migration_script)
    sftp.close()
    print("✅ 迁移脚本已上传")

    # 执行脚本
    print("\n执行迁移...")
    stdin, stdout, stderr = ssh.exec_command('python3 /tmp/migrate_users.py')
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')

    print(output)
    if error:
        print(f"错误: {error}")

    # 验证迁移
    print("\n验证迁移结果...")
    verify_script = '''#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('/var/www/backend/lingzhi_ecosystem.db')
cursor = conn.cursor()

cursor.execute("SELECT id, username, email, phone, total_lingzhi FROM users")
users = cursor.fetchall()

print(f"新数据库中的用户: {len(users)} 个")
print("-" * 80)
for user in users:
    print(f"ID: {user[0]}, 用户名: {user[1]}, 邮箱: {user[2]}, 手机: {user[3]}, 灵值: {user[4]}")

conn.close()
'''

    stdin, stdout, stderr = ssh.exec_command(f'python3 -c "{verify_script}"')
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')

    print(output)
    if error:
        print(f"错误: {error}")

    print("\n==========================================")
    print("✅ 迁移完成！")
    print("==========================================")

except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()

finally:
    ssh.close()

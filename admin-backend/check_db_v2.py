#!/usr/bin/env python3
import paramiko

hostname = '123.56.142.143'
port = 22
username = 'root'
password = 'Meiyue@root123'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

ssh.connect(hostname, port, username, password)

# 创建并上传Python脚本
script = '''#!/usr/bin/env python3
import sqlite3
import os

db_path = '/var/www/backend/lingzhi_ecosystem.db'

print("DB file size:", os.path.getsize(db_path), "bytes")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Tables:", len(tables))
    for table in tables:
        print(f"Table: {table[0]}")

    if len(tables) > 0:
        first_table = tables[0][0]
        cursor.execute(f"SELECT * FROM {first_table} LIMIT 5")
        rows = cursor.fetchall()
        print(f"First 5 rows from {first_table}:")
        for row in rows:
            print(row)

    conn.close()
except Exception as e:
    print("Error:", e)
    import traceback
    traceback.print_exc()
'''

sftp = ssh.open_sftp()
with sftp.file('/tmp/check_db.py', 'w') as f:
    f.write(script)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('python3 /tmp/check_db.py')
output = stdout.read().decode('utf-8')
error = stderr.read().decode('utf-8')

print(output)
if error:
    print(f"Error: {error}")

ssh.close()

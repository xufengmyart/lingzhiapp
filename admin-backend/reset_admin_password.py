#!/usr/bin/env python3
"""
重置admin用户密码
"""
import sqlite3
from werkzeug.security import generate_password_hash

DATABASE = 'data/lingzhi_ecosystem.db'

def reset_admin_password():
    """重置admin用户密码为123456"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # 生成新的密码哈希
    password = '123456'
    password_hash = generate_password_hash(password, method='scrypt')

    print(f"生成的密码哈希: {password_hash[:50]}...")

    # 更新admin用户的密码
    cursor.execute(
        "UPDATE users SET password_hash = ? WHERE username = ?",
        (password_hash, 'admin')
    )

    conn.commit()

    # 验证更新结果
    cursor.execute("SELECT username, password_hash FROM users WHERE username = ?", ('admin',))
    user = cursor.fetchone()

    if user:
        print(f"✅ Admin密码已重置")
        print(f"   用户名: {user[0]}")
        print(f"   密码哈希: {user[1][:50]}...")
    else:
        print("❌ Admin用户不存在")

    conn.close()

if __name__ == '__main__':
    reset_admin_password()

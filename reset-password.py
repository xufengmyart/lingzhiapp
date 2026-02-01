#!/usr/bin/env python3
# 重置用户密码脚本

import sqlite3
import hashlib

DB_PATH = './admin-backend/lingzhi_ecosystem.db'

def reset_password(username, new_password):
    """重置用户密码"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 生成新的密码哈希（SHA256）
    password_hash = hashlib.sha256(new_password.encode()).hexdigest()

    # 更新密码
    cursor.execute(
        "UPDATE users SET password_hash = ? WHERE username = ?",
        (password_hash, username)
    )

    if cursor.rowcount > 0:
        conn.commit()
        print(f"✓ 用户 '{username}' 的密码已重置为 '{new_password}'")
    else:
        print(f"✗ 用户 '{username}' 不存在")

    conn.close()

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 3:
        print("用法: python3 reset-password.py <用户名> <新密码>")
        print("示例: python3 reset-password.py 许锋 123456")
        sys.exit(1)

    username = sys.argv[1]
    new_password = sys.argv[2]

    reset_password(username, new_password)

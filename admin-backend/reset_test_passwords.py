#!/usr/bin/env python3
"""
为测试用户重置密码
"""

import sqlite3
import bcrypt

DATABASE = 'lingzhi_ecosystem.db'

def reset_test_passwords():
    """重置测试用户的密码"""
    print("=" * 80)
    print("为测试用户重置密码...")
    print("=" * 80)
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # 查询所有用户
    cursor.execute("SELECT id, username, password_hash FROM users")
    users = cursor.fetchall()
    
    reset_count = 0
    for user in users:
        user_id, username, password_hash = user
        
        # 如果密码是测试用的假密码，则重置
        if password_hash.startswith('hashed_password'):
            # 生成新的 bcrypt 密码
            new_password = '123456'  # 默认密码
            salt = bcrypt.gensalt()
            new_hash = bcrypt.hashpw(new_password.encode('utf-8'), salt).decode('utf-8')
            
            # 更新数据库
            cursor.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (new_hash, user_id)
            )
            reset_count += 1
            print(f"  ✅ 重置密码: {username} (新密码: {new_password})")
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 80)
    print(f"重置完成！共重置 {reset_count} 个用户的密码")
    print("测试用户可以使用密码 '123456' 登录")
    print("=" * 80)

if __name__ == '__main__':
    reset_test_passwords()

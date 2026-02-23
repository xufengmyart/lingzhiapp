#!/usr/bin/env python
"""
创建测试用户
"""
import sys
sys.path.append('admin-backend')

import bcrypt
from database import get_db

def create_test_user():
    """创建测试用户"""
    print("创建测试用户...")
    
    # 测试用户数据
    test_users = [
        {
            'username': 'testuser',
            'email': 'test@meiyueart.com',
            'phone': '13800138001',
            'password': 'test123',
            'status': 'active'
        },
        {
            'username': 'partner',
            'email': 'partner@meiyueart.com',
            'phone': '13800138002',
            'password': 'partner123',
            'status': 'active'
        }
    ]
    
    conn = get_db()
    
    for user_data in test_users:
        # 检查用户是否已存在
        existing_user = conn.execute(
            "SELECT id FROM users WHERE username = ?",
            (user_data['username'],)
        ).fetchone()
        
        if existing_user:
            print(f"用户 {user_data['username']} 已存在，跳过")
            continue
        
        # 加密密码
        password_bytes = user_data['password'].encode('utf-8')
        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')
        
        # 插入用户
        conn.execute(
            """INSERT INTO users 
               (username, email, phone, password_hash, status, total_lingzhi)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                user_data['username'],
                user_data['email'],
                user_data['phone'],
                hashed,
                user_data['status'],
                500
            )
        )
        
        print(f"✓ 创建用户: {user_data['username']} (密码: {user_data['password']})")
    
    conn.commit()
    conn.close()
    
    print("\n测试用户创建完成！")
    print("\n用户列表:")
    print("-" * 80)
    print(f"{'用户名':<15} {'邮箱':<30} {'密码':<15} {'状态':<10}")
    print("-" * 80)
    for user_data in test_users:
        print(f"{user_data['username']:<15} {user_data['email']:<30} {user_data['password']:<15} {user_data['status']:<10}")
    print("-" * 80)
    print("\n注意: admin用户已存在，密码为 '123'")

if __name__ == '__main__':
    create_test_user()

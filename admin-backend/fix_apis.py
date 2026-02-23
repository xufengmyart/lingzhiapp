#!/usr/bin/env python3
"""
修复缺失的API接口
"""

import sqlite3
import os
from datetime import datetime

# 配置
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'lingzhi_ecosystem.db')

def create_missing_tables():
    """创建缺失的表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 创建商家表（如果不存在）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS merchants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                merchant_code TEXT UNIQUE NOT NULL,
                merchant_name TEXT NOT NULL,
                description TEXT,
                category TEXT NOT NULL,
                logo_url TEXT,
                contact_person TEXT,
                contact_phone TEXT,
                contact_email TEXT,
                address TEXT,
                business_license TEXT,
                status TEXT DEFAULT 'active',
                commission_rate REAL DEFAULT 0.05,
                total_orders INTEGER DEFAULT 0,
                total_revenue REAL DEFAULT 0.00,
                rating REAL DEFAULT 0.0,
                rating_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                verified_at TIMESTAMP,
                verified_by INTEGER,
                FOREIGN KEY (verified_by) REFERENCES users(id)
            )
        ''')

        # 检查是否有测试数据
        cursor.execute('SELECT COUNT(*) FROM merchants')
        count = cursor.fetchone()[0]

        if count == 0:
            # 插入测试数据
            cursor.executemany('''
                INSERT INTO merchants (merchant_code, merchant_name, description, category, contact_person, contact_phone, contact_email, status, rating, rating_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', [
                ('MERCHANT_001', '西安文创馆', '专注于西安本土文化创意产品的开发与销售', '文化', '王经理', '13800000001', 'contact@xianculture.com', 'active', 4.5, 120),
                ('MERCHANT_002', '古韵非遗', '致力于非物质文化遗产的保护与传承', '非遗', '李师傅', '13800000002', 'contact@heritage.com', 'active', 4.8, 89),
                ('MERCHANT_003', '秦风汉韵', '专业制作秦汉时期风格的复制品', '历史', '张总', '13800000003', 'contact@qinhan.com', 'active', 4.2, 67),
                ('MERCHANT_004', '长安美食记', '提供西安特色美食和地方小吃', '美食', '刘大厨', '13800000004', 'contact@xianfood.com', 'active', 4.7, 156),
                ('MERCHANT_005', '关中民俗', '收集和展示关中地区的民俗文化产品', '民俗', '赵老师', '13800000005', 'contact@guanzhong.com', 'active', 4.3, 98),
            ])
            print("✅ 商家测试数据已创建")
        else:
            print(f"✅ 商家表已存在 {count} 条数据")

        conn.commit()
        print("✅ 数据库表创建成功")

    except Exception as e:
        print(f"❌ 创建表失败: {e}")
        conn.rollback()
    finally:
        conn.close()

def verify_api_routes():
    """验证API路由是否正确"""
    print("\n=== 验证API路由 ===")

    # 检查关键文件
    files_to_check = [
        'routes/user_system.py',
        'routes/culture_translation.py',
        'routes/complete_apis.py',
    ]

    for file_path in files_to_check:
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path} 存在")
            # 检查语法
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                compile(code, full_path, 'exec')
                print(f"   ✓ 语法正确")
            except SyntaxError as e:
                print(f"   ❌ 语法错误: {e}")
        else:
            print(f"❌ {file_path} 不存在")

if __name__ == '__main__':
    print("=== 开始修复API ===\n")
    create_missing_tables()
    verify_api_routes()
    print("\n=== 修复完成 ===")

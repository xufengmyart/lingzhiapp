#!/usr/bin/env python3
import sqlite3
from datetime import datetime, date, timedelta

conn = sqlite3.connect('lingzhi_ecosystem.db')
cursor = conn.cursor()

print("创建用户统计表...")
print("=" * 50)

# 创建用户统计表
cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_statistics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stat_date DATE NOT NULL UNIQUE,
        total_users INTEGER DEFAULT 0,
        new_users INTEGER DEFAULT 0,
        active_users INTEGER DEFAULT 0,
        total_lingzhi INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
print("✓ 用户统计表创建成功")

# 插入过去7天的统计数据（示例数据）
cursor.execute("SELECT MAX(stat_date) FROM user_statistics")
last_date = cursor.fetchone()[0]

if last_date:
    last_date = datetime.strptime(last_date, '%Y-%m-%d').date()
else:
    last_date = date.today() - timedelta(days=7)

cursor.execute("SELECT COUNT(*) FROM users")
total_users = cursor.fetchone()[0]

# 生成从last_date到今天的统计数据
current_date = last_date + timedelta(days=1)
while current_date <= date.today():
    # 计算新增用户数（示例：随机生成）
    import random
    new_users = random.randint(0, 5) if current_date != date.today() else max(0, total_users - 7)  # 今天使用实际数据

    # 更新总用户数
    total_users += new_users

    cursor.execute('''
        INSERT OR REPLACE INTO user_statistics
        (stat_date, total_users, new_users, active_users, total_lingzhi)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        current_date,
        total_users,
        new_users,
        total_users,  # 简化处理，假设所有用户都是活跃用户
        1000  # 示例数据
    ))

    current_date += timedelta(days=1)

print("✓ 已生成历史统计数据")

conn.commit()
conn.close()

print()
print("用户统计表初始化完成！")

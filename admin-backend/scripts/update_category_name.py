#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新新闻分类名称
将"系统公告"改为"平台信息"
"""

import sqlite3
import os

# 数据库路径
DATABASE_PATH = os.getenv('DATABASE_PATH', '/app/meiyueart-backend/data/lingzhi_ecosystem.db')

def main():
    print("开始更新新闻分类名称...")
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # 检查是否有"系统公告"分类
    cursor.execute("SELECT id, name FROM news_categories WHERE slug = 'announcements'")
    category = cursor.fetchone()
    
    if category and category[1] == '系统公告':
        print(f"找到分类: {category[0]} - {category[1]}")
        
        # 更新分类名称
        cursor.execute("""
            UPDATE news_categories
            SET name = '平台信息',
                description = '平台公告、系统更新和重要通知',
                updated_at = CURRENT_TIMESTAMP
            WHERE slug = 'announcements'
        """)
        
        affected_rows = cursor.rowcount
        conn.commit()
        
        print(f"✅ 已更新 {affected_rows} 条记录")
        print("✅ 分类名称已从'系统公告'改为'平台信息'")
    else:
        if category:
            print(f"✅ 分类名称已经是: {category[1]}")
        else:
            print("⚠️  未找到 slug 为 'announcements' 的分类")
    
    conn.close()
    print("完成！")

if __name__ == '__main__':
    main()

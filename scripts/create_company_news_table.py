#!/usr/bin/env python3
import sqlite3
from datetime import datetime

conn = sqlite3.connect('lingzhi_ecosystem.db')
cursor = conn.cursor()

print("创建公司动态表...")
print("=" * 50)

# 创建公司动态表
cursor.execute('''
    CREATE TABLE IF NOT EXISTS company_news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        news_type TEXT DEFAULT 'news',
        status TEXT DEFAULT 'published',
        author TEXT DEFAULT '系统管理员',
        views INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        published_at TIMESTAMP
    )
''')
print("✓ 公司动态表创建成功")

# 插入示例数据
sample_news = [
    {
        "title": "灵值生态园正式上线运营",
        "content": "陕西媄月商业艺术有限责任公司旗下灵值生态园平台正式上线，标志着我们在文化数字化与数字资产创新领域迈出了重要一步。平台致力于通过技术赋能让文化价值更高效地流转和传递。",
        "news_type": "announcement",
        "author": "总经理办公室"
    },
    {
        "title": "用户突破1000人里程碑",
        "content": "感谢所有用户的支持与信任，灵值生态园注册用户数已突破1000人。我们将继续优化用户体验，提供更优质的服务。",
        "news_type": "milestone",
        "author": "运营团队"
    },
    {
        "title": "新增西安文化关键词转译功能",
        "content": "平台全新推出西安文化关键词转译功能，用户可以通过AI智能体快速将文化关键词转化为商业价值。目前已收录110个文化关键词及转译提示。",
        "news_type": "feature",
        "author": "产品团队"
    }
]

for news in sample_news:
    cursor.execute('''
        INSERT INTO company_news (title, content, news_type, author, published_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        news["title"],
        news["content"],
        news["news_type"],
        news["author"],
        datetime.now()
    ))

print(f"✓ 已插入 {len(sample_news)} 条示例公司动态")

conn.commit()
conn.close()

print()
print("公司动态表初始化完成！")

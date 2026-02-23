"""
数据库表结构优化脚本
为灵值生态园系统添加知识库分类、系统配置等新功能
"""

import sqlite3
import os
import json
from datetime import datetime

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lingzhi_ecosystem.db')

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def execute_sql(conn, sql, description=""):
    """执行SQL语句"""
    try:
        conn.execute(sql)
        print(f"✅ {description}")
        return True
    except sqlite3.Error as e:
        if "duplicate column name" in str(e).lower():
            print(f"⚠️  {description} - 列已存在，跳过")
            return True
        else:
            print(f"❌ {description} - 错误: {e}")
            return False

def create_tables():
    """创建新表"""
    print("\n=== 创建新表 ===\n")
    
    conn = get_db_connection()
    
    # 1. 知识库分类表
    execute_sql(conn, """
        CREATE TABLE IF NOT EXISTS knowledge_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL,
            description TEXT,
            icon TEXT,
            color TEXT,
            parent_id INTEGER,
            sort_order INTEGER DEFAULT 0,
            is_system BOOLEAN DEFAULT 0,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES knowledge_categories(id)
        )
    """, "创建知识库分类表 (knowledge_categories)")
    
    # 2. 知识标签表
    execute_sql(conn, """
        CREATE TABLE IF NOT EXISTS knowledge_tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL,
            description TEXT,
            color TEXT,
            usage_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """, "创建知识标签表 (knowledge_tags)")
    
    # 3. 知识库-分类关联表
    execute_sql(conn, """
        CREATE TABLE IF NOT EXISTS knowledge_base_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            knowledge_base_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_bases(id),
            FOREIGN KEY (category_id) REFERENCES knowledge_categories(id),
            UNIQUE(knowledge_base_id, category_id)
        )
    """, "创建知识库-分类关联表 (knowledge_base_categories)")
    
    # 4. 知识文档-标签关联表
    execute_sql(conn, """
        CREATE TABLE IF NOT EXISTS knowledge_document_tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES knowledge_documents(id),
            FOREIGN KEY (tag_id) REFERENCES knowledge_tags(id),
            UNIQUE(document_id, tag_id)
        )
    """, "创建知识文档-标签关联表 (knowledge_document_tags)")
    
    # 5. 知识访问统计表
    execute_sql(conn, """
        CREATE TABLE IF NOT EXISTS knowledge_access_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            knowledge_base_id INTEGER,
            document_id INTEGER,
            user_id INTEGER,
            action TEXT NOT NULL,
            search_query TEXT,
            result_count INTEGER,
            ip_address TEXT,
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_bases(id),
            FOREIGN KEY (document_id) REFERENCES knowledge_documents(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """, "创建知识访问统计表 (knowledge_access_logs)")
    
    # 6. 系统配置表
    execute_sql(conn, """
        CREATE TABLE IF NOT EXISTS system_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            config_key TEXT UNIQUE NOT NULL,
            config_value TEXT NOT NULL,
            config_type TEXT DEFAULT 'string',
            description TEXT,
            category TEXT,
            is_public BOOLEAN DEFAULT 0,
            is_editable BOOLEAN DEFAULT 1,
            updated_by INTEGER,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """, "创建系统配置表 (system_configs)")
    
    # 7. 系统统计表
    execute_sql(conn, """
        CREATE TABLE IF NOT EXISTS system_statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stat_date DATE NOT NULL,
            stat_type TEXT NOT NULL,
            stat_key TEXT NOT NULL,
            stat_value INTEGER DEFAULT 0,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(stat_date, stat_type, stat_key)
        )
    """, "创建系统统计表 (system_statistics)")
    
    conn.commit()
    conn.close()

def alter_tables():
    """修改现有表结构"""
    print("\n=== 修改现有表结构 ===\n")
    
    conn = get_db_connection()
    
    # 修改 knowledge_bases 表
    execute_sql(conn, """
        ALTER TABLE knowledge_bases ADD COLUMN category_id INTEGER
    """, "knowledge_bases 添加 category_id 列")
    
    execute_sql(conn, """
        ALTER TABLE knowledge_bases ADD COLUMN tags TEXT
    """, "knowledge_bases 添加 tags 列")
    
    execute_sql(conn, """
        ALTER TABLE knowledge_bases ADD COLUMN view_count INTEGER DEFAULT 0
    """, "knowledge_bases 添加 view_count 列")
    
    execute_sql(conn, """
        ALTER TABLE knowledge_bases ADD COLUMN search_count INTEGER DEFAULT 0
    """, "knowledge_bases 添加 search_count 列")
    
    execute_sql(conn, """
        ALTER TABLE knowledge_bases ADD COLUMN download_count INTEGER DEFAULT 0
    """, "knowledge_bases 添加 download_count 列")
    
    execute_sql(conn, """
        ALTER TABLE knowledge_bases ADD COLUMN is_public BOOLEAN DEFAULT 1
    """, "knowledge_bases 添加 is_public 列")
    
    # 修改 knowledge_documents 表
    execute_sql(conn, """
        ALTER TABLE knowledge_documents ADD COLUMN summary TEXT
    """, "knowledge_documents 添加 summary 列")
    
    execute_sql(conn, """
        ALTER TABLE knowledge_documents ADD COLUMN author TEXT
    """, "knowledge_documents 添加 author 列")
    
    execute_sql(conn, """
        ALTER TABLE knowledge_documents ADD COLUMN view_count INTEGER DEFAULT 0
    """, "knowledge_documents 添加 view_count 列")
    
    execute_sql(conn, """
        ALTER TABLE knowledge_documents ADD COLUMN download_count INTEGER DEFAULT 0
    """, "knowledge_documents 添加 download_count 列")
    
    # 修改 audit_logs 表
    execute_sql(conn, """
        ALTER TABLE audit_logs ADD COLUMN request_method TEXT
    """, "audit_logs 添加 request_method 列")
    
    execute_sql(conn, """
        ALTER TABLE audit_logs ADD COLUMN request_path TEXT
    """, "audit_logs 添加 request_path 列")
    
    execute_sql(conn, """
        ALTER TABLE audit_logs ADD COLUMN response_status INTEGER
    """, "audit_logs 添加 response_status 列")
    
    execute_sql(conn, """
        ALTER TABLE audit_logs ADD COLUMN response_time INTEGER
    """, "audit_logs 添加 response_time 列")
    
    execute_sql(conn, """
        ALTER TABLE audit_logs ADD COLUMN session_id TEXT
    """, "audit_logs 添加 session_id 列")
    
    conn.commit()
    conn.close()

def create_indexes():
    """创建索引"""
    print("\n=== 创建索引 ===\n")
    
    conn = get_db_connection()
    
    # knowledge_categories 索引
    execute_sql(conn, """
        CREATE INDEX IF NOT EXISTS idx_kb_categories_code ON knowledge_categories(code)
    """, "创建 knowledge_categories.code 索引")
    
    execute_sql(conn, """
        CREATE INDEX IF NOT EXISTS idx_kb_categories_parent ON knowledge_categories(parent_id)
    """, "创建 knowledge_categories.parent_id 索引")
    
    # knowledge_tags 索引
    execute_sql(conn, """
        CREATE INDEX IF NOT EXISTS idx_kb_tags_code ON knowledge_tags(code)
    """, "创建 knowledge_tags.code 索引")
    
    # knowledge_access_logs 索引
    execute_sql(conn, """
        CREATE INDEX IF NOT EXISTS idx_kb_access_user ON knowledge_access_logs(user_id)
    """, "创建 knowledge_access_logs.user_id 索引")
    
    execute_sql(conn, """
        CREATE INDEX IF NOT EXISTS idx_kb_access_kb ON knowledge_access_logs(knowledge_base_id)
    """, "创建 knowledge_access_logs.knowledge_base_id 索引")
    
    execute_sql(conn, """
        CREATE INDEX IF NOT EXISTS idx_kb_access_created ON knowledge_access_logs(created_at)
    """, "创建 knowledge_access_logs.created_at 索引")
    
    # system_configs 索引
    execute_sql(conn, """
        CREATE INDEX IF NOT EXISTS idx_sys_configs_category ON system_configs(category)
    """, "创建 system_configs.category 索引")
    
    # system_statistics 索引
    execute_sql(conn, """
        CREATE INDEX IF NOT EXISTS idx_sys_stats_date ON system_statistics(stat_date)
    """, "创建 system_statistics.stat_date 索引")
    
    execute_sql(conn, """
        CREATE INDEX IF NOT EXISTS idx_sys_stats_type ON system_statistics(stat_type)
    """, "创建 system_statistics.stat_type 索引")
    
    conn.commit()
    conn.close()

def init_default_categories():
    """初始化默认知识库分类"""
    print("\n=== 初始化知识库分类 ===\n")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 西安文化知识库分类
    categories = [
        # 一级分类
        (1, None, '历史文化', 'history', '西安深厚的历史文化底蕴，包含周秦汉唐等朝代文化', '📚', '#8B4513', 1),
        (2, None, '建筑文化', 'architecture', '西安独特的建筑文化，从古城墙到唐风建筑', '🏛️', '#DAA520', 2),
        (3, None, '艺术文化', 'art', '丰富的艺术文化，包括秦俑、皮影、戏曲等', '🎭', '#FF6347', 3),
        (4, None, '饮食文化', 'food', '著名的西安饮食文化，陕菜和特色小吃', '🍜', '#FFA500', 4),
        (5, None, '民俗文化', 'folk', '独特的民俗文化和传统习俗', '🎪', '#9370DB', 5),
        (6, None, '现代文化', 'modern', '现代文化创新和文化产业发展', '🚀', '#4682B4', 6),
        
        # 历史文化子分类
        (7, 1, '周秦汉唐文化', 'zhou_qin_han_tang', '周、秦、汉、唐四大朝代文化', '👑', '#8B4513', 1),
        (8, 1, '古都文化', 'ancient_capital', '十三朝古都文化', '🏰', '#8B4513', 2),
        (9, 1, '历史人物', 'historical_figures', '西安历史上的重要人物', '👤', '#8B4513', 3),
        
        # 建筑文化子分类
        (10, 2, '城墙文化', 'city_wall', '西安城墙文化', '🧱', '#DAA520', 1),
        (11, 2, '唐风建筑', 'tang_style', '唐代风格建筑', '🏯', '#DAA520', 2),
        (12, 2, '寺庙古建', 'temples', '寺庙和古建筑', '⛩️', '#DAA520', 3),
        
        # 艺术文化子分类
        (13, 3, '秦俑文化', 'terracotta', '秦始皇兵马俑文化', '⚔️', '#FF6347', 1),
        (14, 3, '皮影艺术', 'shadow_puppetry', '皮影戏艺术', '🎪', '#FF6347', 2),
        (15, 3, '戏曲文化', 'opera', '秦腔等戏曲文化', '🎭', '#FF6347', 3),
        (16, 3, '民间工艺', 'folk_crafts', '民间传统工艺', '✂️', '#FF6347', 4),
        
        # 饮食文化子分类
        (17, 4, '陕菜体系', 'shaanxi_cuisine', '陕西菜系', '🥘', '#FFA500', 1),
        (18, 4, '面食文化', 'noodle_culture', '陕西面食文化', '🍜', '#FFA500', 2),
        (19, 4, '特色小吃', 'snacks', '西安特色小吃', '🥟', '#FFA500', 3),
        
        # 民俗文化子分类
        (20, 5, '节庆习俗', 'festivals', '节庆习俗文化', '🎉', '#9370DB', 1),
        (21, 5, '民间信仰', 'beliefs', '民间信仰文化', '🙏', '#9370DB', 2),
        (22, 5, '婚丧嫁娶', 'life_events', '婚丧嫁娶习俗', '💒', '#9370DB', 3),
        
        # 现代文化子分类
        (23, 6, '文化创新', 'cultural_innovation', '文化创新项目', '💡', '#4682B4', 1),
        (24, 6, '文旅融合', 'cultural_tourism', '文化旅游融合', '🗺️', '#4682B4', 2),
        (25, 6, '数字文化', 'digital_culture', '数字文化发展', '💻', '#4682B4', 3),
    ]
    
    for id, parent_id, name, code, description, icon, color, sort_order in categories:
        try:
            cursor.execute("""
                INSERT INTO knowledge_categories 
                (id, name, code, description, icon, color, parent_id, sort_order, is_system, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
            """, (id, name, code, description, icon, color, parent_id, sort_order, 
                  datetime.now().isoformat(), datetime.now().isoformat()))
            print(f"✅ 创建分类: {name} ({code})")
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint" in str(e):
                print(f"⚠️  分类已存在: {name}")
            else:
                print(f"❌ 创建分类失败: {name} - {e}")
    
    conn.commit()
    conn.close()

def init_system_configs():
    """初始化系统配置"""
    print("\n=== 初始化系统配置 ===\n")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    configs = {
        # 网站配置
        'site_name': {'value': '灵值生态园', 'type': 'string', 'category': 'site', 'description': '网站名称'},
        'site_description': {'value': '文化商业生态平台', 'type': 'string', 'category': 'site', 'description': '网站描述'},
        'site_keywords': {'value': '西安文化,文化商业,灵值', 'type': 'string', 'category': 'site', 'description': '网站关键词'},
        'contact_email': {'value': 'contact@meiyueart.com', 'type': 'string', 'category': 'site', 'description': '联系邮箱'},
        'contact_phone': {'value': '400-XXX-XXXX', 'type': 'string', 'category': 'site', 'description': '联系电话'},
        
        # 灵值配置
        'checkin_reward': {'value': '10', 'type': 'number', 'category': 'lingzhi', 'description': '签到奖励'},
        'checkin_consecutive_reward': {'value': '50', 'type': 'number', 'category': 'lingzhi', 'description': '连续签到奖励'},
        'daily_limit': {'value': '500', 'type': 'number', 'category': 'lingzhi', 'description': '每日灵值上限'},
        'conversation_reward_min': {'value': '2', 'type': 'number', 'category': 'lingzhi', 'description': '对话奖励最小值'},
        'conversation_reward_max': {'value': '5', 'type': 'number', 'category': 'lingzhi', 'description': '对话奖励最大值'},
        
        # 推荐配置
        'direct_reward': {'value': '50', 'type': 'number', 'category': 'referral', 'description': '直推奖励'},
        'indirect_rate': {'value': '0.2', 'type': 'number', 'category': 'referral', 'description': '间接奖励比例'},
        'max_level': {'value': '5', 'type': 'number', 'category': 'referral', 'description': '最大推荐层级'},
    }
    
    for key, config in configs.items():
        try:
            cursor.execute("""
                INSERT INTO system_configs 
                (config_key, config_value, config_type, description, category, updated_at, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (key, config['value'], config['type'], config['description'], config['category'],
                  datetime.now().isoformat(), datetime.now().isoformat()))
            print(f"✅ 创建配置: {key} = {config['value']}")
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint" in str(e):
                print(f"⚠️  配置已存在: {key}")
            else:
                print(f"❌ 创建配置失败: {key} - {e}")
    
    conn.commit()
    conn.close()

def verify_tables():
    """验证表创建"""
    print("\n=== 验证表创建 ===\n")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查新表
    new_tables = [
        'knowledge_categories',
        'knowledge_tags',
        'knowledge_base_categories',
        'knowledge_document_tags',
        'knowledge_access_logs',
        'system_configs',
        'system_statistics'
    ]
    
    for table in new_tables:
        cursor.execute(f"""
            SELECT COUNT(*) as count FROM sqlite_master 
            WHERE type='table' AND name='{table}'
        """)
        result = cursor.fetchone()
        if result['count'] > 0:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            count = cursor.fetchone()['count']
            print(f"✅ 表 {table} 已创建，记录数: {count}")
        else:
            print(f"❌ 表 {table} 未创建")
    
    conn.close()

def main():
    """主函数"""
    print("=" * 60)
    print("数据库表结构优化脚本")
    print("=" * 60)
    print(f"数据库路径: {DB_PATH}")
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # 创建新表
        create_tables()
        
        # 修改现有表
        alter_tables()
        
        # 创建索引
        create_indexes()
        
        # 初始化数据
        init_default_categories()
        init_system_configs()
        
        # 验证结果
        verify_tables()
        
        print("\n" + "=" * 60)
        print("✅ 数据库表结构优化完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

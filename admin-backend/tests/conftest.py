"""
测试配置
Test Configuration
"""

import os
import sys
import tempfile
import sqlite3

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 测试环境变量
os.environ['FLASK_ENV'] = 'testing'
os.environ['FLASK_DEBUG'] = 'False'

# 创建临时测试数据库
TEST_DB_PATH = os.path.join(tempfile.gettempdir(), 'test_lingzhi_ecosystem.db')

# 设置环境变量，让应用使用测试数据库
os.environ['TEST_DATABASE_PATH'] = TEST_DB_PATH


class TestConfig:
    """测试配置"""

    # 数据库配置
    DATABASE_PATH = TEST_DB_PATH
    OLD_DATABASE = TEST_DB_PATH

    # JWT 配置
    JWT_SECRET_KEY = 'test_secret_key_123456'
    JWT_EXPIRATION = 3600

    # Flask 配置
    TESTING = True
    DEBUG = False
    SECRET_KEY = 'test_secret_key'


def init_test_database():
    """初始化测试数据库"""
    # 删除旧的测试数据库
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    # 创建新的测试数据库
    conn = sqlite3.connect(TEST_DB_PATH)
    cursor = conn.cursor()

    # 创建用户表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT,
        phone TEXT,
        password_hash TEXT NOT NULL,
        total_lingzhi INTEGER DEFAULT 0,
        status TEXT DEFAULT 'active',
        last_login_at TIMESTAMP,
        avatar_url TEXT,
        real_name TEXT,
        is_verified BOOLEAN DEFAULT 0,
        login_type TEXT DEFAULT 'phone',
        wechat_openid TEXT,
        wechat_unionid TEXT,
        wechat_nickname TEXT,
        wechat_avatar TEXT,
        referrer_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 创建管理员表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'admin',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 创建签到记录表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS checkin_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        checkin_date DATE NOT NULL,
        lingzhi_earned INTEGER DEFAULT 10,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        UNIQUE(user_id, checkin_date)
    )
    ''')

    # 创建推荐关系表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS referral_relationships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        referrer_id INTEGER NOT NULL,
        referred_user_id INTEGER NOT NULL,
        level INTEGER DEFAULT 1,
        lingzhi_reward INTEGER DEFAULT 0,
        reward_status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (referrer_id) REFERENCES users(id),
        FOREIGN KEY (referred_user_id) REFERENCES users(id),
        UNIQUE(referrer_id, referred_user_id)
    )
    ''')

    # 创建推荐码表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS referral_codes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        referrer_id INTEGER NOT NULL,
        code TEXT UNIQUE NOT NULL,
        status TEXT DEFAULT 'active',
        expires_at TIMESTAMP,
        used_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (referrer_id) REFERENCES users(id)
    )
    ''')

    # 创建充值档位表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS recharge_tiers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price DECIMAL(10,2) NOT NULL,
        base_lingzhi INTEGER NOT NULL,
        bonus_lingzhi INTEGER NOT NULL,
        bonus_percentage INTEGER NOT NULL,
        partner_level INTEGER DEFAULT 0,
        benefits TEXT,
        status TEXT DEFAULT 'active',
        sort_order INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 创建充值记录表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS recharge_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        tier_id INTEGER NOT NULL,
        order_no TEXT UNIQUE NOT NULL,
        amount DECIMAL(10,2) NOT NULL,
        base_lingzhi INTEGER NOT NULL,
        bonus_lingzhi INTEGER NOT NULL,
        total_lingzhi INTEGER NOT NULL,
        payment_method VARCHAR(20) DEFAULT 'online',
        payment_status VARCHAR(20) DEFAULT 'pending',
        payment_time TIMESTAMP,
        transaction_id TEXT,
        voucher_id INTEGER,
        audit_status VARCHAR(20),
        bank_info TEXT,
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (tier_id) REFERENCES recharge_tiers(id)
    )
    ''')

    # 插入测试数据
    import bcrypt
    password_hash = bcrypt.hashpw('123456'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # 创建测试用户
    cursor.execute(
        """
        INSERT INTO users (username, password_hash, email, phone, total_lingzhi)
        VALUES (?, ?, ?, ?, 100)
        """,
        ('testuser', password_hash, 'test@example.com', '13800138000')
    )

    # 创建测试管理员
    cursor.execute(
        """
        INSERT INTO admins (username, password_hash, role)
        VALUES (?, ?, 'admin')
        """,
        ('admin', password_hash)
    )

    # 创建测试充值档位
    cursor.execute(
        """
        INSERT INTO recharge_tiers
        (name, description, price, base_lingzhi, bonus_lingzhi, bonus_percentage, sort_order)
        VALUES
        ('体验档', '新手体验套餐', 1.00, 100, 0, 0, 1),
        ('标准档', '标准套餐', 10.00, 1000, 100, 10, 2),
        ('尊享档', '尊享套餐', 100.00, 10000, 2000, 20, 3)
        """
    )

    conn.commit()
    conn.close()

    print(f"✅ 测试数据库已初始化: {TEST_DB_PATH}")


def cleanup_test_database():
    """清理测试数据库"""
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
        print(f"✅ 测试数据库已清理: {TEST_DB_PATH}")


if __name__ == '__main__':
    init_test_database()

-- 充值档位表
CREATE TABLE IF NOT EXISTS recharge_tiers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    base_lingzhi INTEGER NOT NULL,
    bonus_lingzhi INTEGER DEFAULT 0,
    bonus_percentage INTEGER DEFAULT 0,
    partner_level VARCHAR(50) DEFAULT 'bronze',
    benefits TEXT,
    status VARCHAR(20) DEFAULT 'active',
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 充值记录表
CREATE TABLE IF NOT EXISTS recharge_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    tier_id INTEGER NOT NULL,
    order_no VARCHAR(50) NOT NULL UNIQUE,
    amount DECIMAL(10,2) NOT NULL,
    base_lingzhi INTEGER NOT NULL,
    bonus_lingzhi INTEGER DEFAULT 0,
    total_lingzhi INTEGER NOT NULL,
    payment_method VARCHAR(50) DEFAULT 'online',
    payment_status VARCHAR(50) DEFAULT 'pending',
    payment_time TIMESTAMP,
    transaction_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (tier_id) REFERENCES recharge_tiers(id)
);

-- 公司收款账户表
CREATE TABLE IF NOT EXISTS company_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_name VARCHAR(100) NOT NULL,
    account_number VARCHAR(100) NOT NULL,
    bank_name VARCHAR(100),
    bank_branch VARCHAR(200),
    company_name VARCHAR(200),
    company_credit_code VARCHAR(50),
    account_type VARCHAR(50) DEFAULT 'bank',
    is_active INTEGER DEFAULT 1,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 灵值消费记录表
CREATE TABLE IF NOT EXISTS lingzhi_consumption_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    consumption_type VARCHAR(50) NOT NULL,
    consumption_item VARCHAR(100),
    lingzhi_amount INTEGER NOT NULL,
    description TEXT,
    related_order_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_recharge_records_user_id ON recharge_records(user_id);
CREATE INDEX IF NOT EXISTS idx_recharge_records_order_no ON recharge_records(order_no);
CREATE INDEX IF NOT EXISTS idx_recharge_records_status ON recharge_records(payment_status);
CREATE INDEX IF NOT EXISTS idx_lingzhi_consumption_user_id ON lingzhi_consumption_records(user_id);
CREATE INDEX IF NOT EXISTS idx_lingzhi_consumption_type ON lingzhi_consumption_records(consumption_type);

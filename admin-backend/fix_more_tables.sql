-- 修复更多缺失的表和字段
-- 创建时间: 2026-02-18

-- 1. 修复 resource_matches 表，添加 earned_at 字段
-- 先检查表结构
PRAGMA table_info(resource_matches);

-- 如果没有 earned_at 字段，则添加
ALTER TABLE resource_matches ADD COLUMN earned_at DATETIME DEFAULT CURRENT_TIMESTAMP;

-- 2. 创建 merchant_reviews 表
CREATE TABLE IF NOT EXISTS merchant_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    merchant_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (merchant_id) REFERENCES merchants(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_merchant_reviews_merchant ON merchant_reviews(merchant_id);
CREATE INDEX IF NOT EXISTS idx_merchant_reviews_user ON merchant_reviews(user_id);

-- 3. 创建 merchant_analytics 表（用于商家统计）
CREATE TABLE IF NOT EXISTS merchant_analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    merchant_id INTEGER NOT NULL,
    view_count INTEGER DEFAULT 0,
    order_count INTEGER DEFAULT 0,
    total_revenue DECIMAL(10,2) DEFAULT 0.00,
    avg_rating DECIMAL(3,2) DEFAULT 5.00,
    date DATE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (merchant_id) REFERENCES merchants(id),
    UNIQUE(merchant_id, date)
);

-- 4. 插入一些示例商家评价
INSERT INTO merchant_reviews (merchant_id, user_id, rating, comment)
VALUES
    (1, 1, 5, '书店很棒，书籍种类丰富'),
    (2, 1, 4, '古玩市场有很多宝贝');

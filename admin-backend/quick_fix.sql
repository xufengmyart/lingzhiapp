-- 快速修复脚本 - 创建缺失的表

-- 创建 merchant_reviews 表
CREATE TABLE IF NOT EXISTS merchant_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    merchant_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    status TEXT DEFAULT 'approved',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (merchant_id) REFERENCES merchants(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_merchant_reviews_merchant ON merchant_reviews(merchant_id);
CREATE INDEX IF NOT EXISTS idx_merchant_reviews_user ON merchant_reviews(user_id);

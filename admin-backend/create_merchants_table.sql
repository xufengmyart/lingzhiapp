-- 商家表创建脚本
-- 创建时间: 2026-02-20

-- 创建商家表
CREATE TABLE IF NOT EXISTS merchants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    merchant_code TEXT UNIQUE NOT NULL,           -- 商家代码
    merchant_name TEXT NOT NULL,                  -- 商家名称
    description TEXT,                             -- 商家描述
    category TEXT NOT NULL,                       -- 类别
    logo_url TEXT,                                -- 商家Logo
    contact_person TEXT,                          -- 联系人
    contact_phone TEXT,                           -- 联系电话
    contact_email TEXT,                           -- 联系邮箱
    address TEXT,                                 -- 地址
    business_license TEXT,                        -- 营业执照
    status TEXT DEFAULT 'active',                 -- 状态：active, suspended, closed
    commission_rate REAL DEFAULT 0.05,            -- 佣金比例
    total_orders INTEGER DEFAULT 0,               -- 总订单数
    total_revenue REAL DEFAULT 0.00,              -- 总收入
    rating REAL DEFAULT 0.0,                      -- 评分
    rating_count INTEGER DEFAULT 0,               -- 评分次数
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verified_at TIMESTAMP,                        -- 认证时间
    verified_by INTEGER,                          -- 认证人ID
    FOREIGN KEY (verified_by) REFERENCES users(id)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_merchants_code ON merchants(merchant_code);
CREATE INDEX IF NOT EXISTS idx_merchants_category ON merchants(category);
CREATE INDEX IF NOT EXISTS idx_merchants_status ON merchants(status);
CREATE INDEX IF NOT EXISTS idx_merchants_rating ON merchants(rating);

-- 插入测试数据
INSERT INTO merchants (merchant_code, merchant_name, description, category, contact_person, contact_phone, contact_email, status, rating, rating_count) VALUES
('MERCHANT_001', '西安文创馆', '专注于西安本土文化创意产品的开发与销售，展示古城西安的文化魅力', '文化', '王经理', '13800000001', 'contact@xianculture.com', 'active', 4.5, 120),
('MERCHANT_002', '古韵非遗', '致力于非物质文化遗产的保护与传承，提供传统手工艺品', '非遗', '李师傅', '13800000002', 'contact@heritage.com', 'active', 4.8, 89),
('MERCHANT_003', '秦风汉韵', '专业制作秦汉时期风格的复制品和文创产品', '历史', '张总', '13800000003', 'contact@qinhan.com', 'active', 4.2, 67),
('MERCHANT_004', '长安美食记', '提供西安特色美食和地方小吃，传承千年饮食文化', '美食', '刘大厨', '13800000004', 'contact@xianfood.com', 'active', 4.7, 156),
('MERCHANT_005', '关中民俗', '收集和展示关中地区的民俗文化产品', '民俗', '赵老师', '13800000005', 'contact@guanzhong.com', 'active', 4.3, 98);

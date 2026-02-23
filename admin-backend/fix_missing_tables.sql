-- 创建缺失的数据库表
-- 创建时间: 2026-02-18

-- 1. 创建 user_knowledge_bases 表
CREATE TABLE IF NOT EXISTS user_knowledge_bases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    knowledge_base_id INTEGER NOT NULL,
    name VARCHAR(255),
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_bases(id)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_user_knowledge ON user_knowledge_bases(user_id, knowledge_base_id);

-- 2. 创建 resources 表
CREATE TABLE IF NOT EXISTS resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(50) DEFAULT 'article',
    category VARCHAR(100),
    tags TEXT, -- JSON 格式存储标签数组
    file_url VARCHAR(500),
    thumbnail_url VARCHAR(500),
    content TEXT,
    author_id INTEGER,
    view_count INTEGER DEFAULT 0,
    download_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_resources_type ON resources(type);
CREATE INDEX IF NOT EXISTS idx_resources_category ON resources(category);
CREATE INDEX IF NOT EXISTS idx_resources_author ON resources(author_id);

-- 3. 创建 merchants 表
CREATE TABLE IF NOT EXISTS merchants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    logo_url VARCHAR(500),
    banner_url VARCHAR(500),
    category VARCHAR(100),
    contact_phone VARCHAR(20),
    contact_email VARCHAR(255),
    address TEXT,
    business_hours VARCHAR(100),
    rating DECIMAL(3,2) DEFAULT 5.00,
    review_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',
    owner_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_merchants_category ON merchants(category);
CREATE INDEX IF NOT EXISTS idx_merchants_owner ON merchants(owner_id);

-- 插入一些示例数据
INSERT INTO resources (title, description, type, category, tags, content, author_id, status)
VALUES
    ('灵值生态园介绍', '灵值生态园是一个智能体生态系统...', 'article', '系统介绍', '["生态", "介绍", "指南"]', '灵值生态园是一个智能体生态系统...', 1, 'active'),
    ('中华文化知识', '中华文化的深度解读...', 'article', '文化', '["文化", "历史", "传统"]', '中华文化的深度解读...', 1, 'active');

INSERT INTO merchants (name, description, category, contact_phone, contact_email, status, owner_id)
VALUES
    ('文化书店', '专营传统文化书籍和文创产品', '书店', '13800000001', 'bookstore@example.com', 'active', 1),
    ('古玩市场', '收藏品交易和鉴赏', '古玩', '13800000002', 'antique@example.com', 'active', 1);

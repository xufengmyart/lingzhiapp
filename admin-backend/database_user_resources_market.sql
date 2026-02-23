-- 用户资源变现系统数据库设计

-- 1. 用户资源表（重构）
CREATE TABLE IF NOT EXISTS user_resources_market (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,  -- 资源所有者ID
    title VARCHAR(200) NOT NULL,  -- 资源标题
    resource_type VARCHAR(50) NOT NULL,  -- 资源类型：文化资源、内容资源、语言资源、设计资源、技术资源、商业资源、其他
    resource_level VARCHAR(20) NOT NULL DEFAULT 'normal',  -- 资源级别：normal（普通）、key（关键）
    brief_description TEXT NOT NULL,  -- 简介内容（所有用户可见）
    detailed_description TEXT,  -- 详细内容（需要付费或权限才能查看）
    implementation_guide TEXT,  -- 落地实施指南
    required_resources TEXT,  -- 所需资源
    expected_benefits TEXT,  -- 预期收益
    risk_assessment TEXT,  -- 风险评估
    price_lingzhi INTEGER NOT NULL,  -- 查看价格（灵值）
    view_count INTEGER DEFAULT 0,  -- 浏览次数
    purchase_count INTEGER DEFAULT 0,  -- 购买次数
    status VARCHAR(20) NOT NULL DEFAULT 'active',  -- 状态：active（上线）、inactive（下线）、pending（审核中）
    visibility VARCHAR(20) NOT NULL DEFAULT 'private',  -- 可见性：private（私有，仅自己和超级管理员可见）、public（公开，所有用户可见简介）
    requires_approval BOOLEAN DEFAULT TRUE,  -- 是否需要对方同意才能查看
    approval_required_by INTEGER,  -- 需要哪些用户ID的同意（JSON数组）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 2. 资源访问记录表
CREATE TABLE IF NOT EXISTS resource_access_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,  -- 访问者ID
    access_type VARCHAR(20) NOT NULL,  -- 访问类型：brief（简介）、detailed（详细）
    lingshi_spent INTEGER DEFAULT 0,  -- 消耗的灵值
    approval_granted BOOLEAN DEFAULT FALSE,  -- 是否获得批准
    access_granted BOOLEAN DEFAULT FALSE,  -- 是否获得访问权限
    reason TEXT,  -- 拒绝原因
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resource_id) REFERENCES user_resources_market(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 3. 资源申请表（需要批准的访问请求）
CREATE TABLE IF NOT EXISTS resource_access_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_id INTEGER NOT NULL,
    requester_id INTEGER NOT NULL,  -- 申请人ID
    approver_id INTEGER NOT NULL,  -- 审批人ID（资源所有者）
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- 状态：pending（待审批）、approved（已批准）、rejected（已拒绝）
    request_message TEXT,  -- 申请说明
    response_message TEXT,  -- 审批回复
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resource_id) REFERENCES user_resources_market(id),
    FOREIGN KEY (requester_id) REFERENCES users(id),
    FOREIGN KEY (approver_id) REFERENCES users(id)
);

-- 4. 资源分类表
CREATE TABLE IF NOT EXISTS resource_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,  -- 分类名称
    description TEXT,  -- 分类描述
    icon VARCHAR(100),  -- 图标
    sort_order INTEGER DEFAULT 0,  -- 排序
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. 资源标签表
CREATE TABLE IF NOT EXISTS resource_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_id INTEGER NOT NULL,
    tag_name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resource_id) REFERENCES user_resources_market(id),
    UNIQUE(resource_id, tag_name)
);

-- 6. 灵值交易记录表（用于资源购买）
CREATE TABLE IF NOT EXISTS lingshi_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,  -- 交易类型：purchase（购买）、earn（获得）、refund（退款）
    amount INTEGER NOT NULL,  -- 金额（正数表示获得，负数表示消费）
    related_type VARCHAR(20),  -- 关联类型：resource_access（资源访问）
    related_id INTEGER,  -- 关联ID
    description TEXT,  -- 描述
    balance_after INTEGER,  -- 交易后余额
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 插入默认资源分类
INSERT OR IGNORE INTO resource_categories (name, description, icon, sort_order) VALUES
('文化资源', '包括文物、艺术品、文化遗产等', '🏛️', 1),
('内容资源', '包括文章、视频、音频等内容', '📚', 2),
('语言资源', '包括翻译、本地化等', '🌐', 3),
('设计资源', '包括UI/UX、平面设计等', '🎨', 4),
('技术资源', '包括代码、技术方案等', '💻', 5),
('商业资源', '包括商业模式、营销方案等', '💼', 6),
('其他', '其他类型的资源', '📦', 7);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_resources_user ON user_resources_market(user_id);
CREATE INDEX IF NOT EXISTS idx_resources_type ON user_resources_market(resource_type);
CREATE INDEX IF NOT EXISTS idx_resources_status ON user_resources_market(status);
CREATE INDEX IF NOT EXISTS idx_resources_visibility ON user_resources_market(visibility);
CREATE INDEX IF NOT EXISTS idx_access_resource ON resource_access_records(resource_id);
CREATE INDEX IF NOT EXISTS idx_access_user ON resource_access_records(user_id);
CREATE INDEX IF NOT EXISTS idx_request_resource ON resource_access_requests(resource_id);
CREATE INDEX IF NOT EXISTS idx_request_requester ON resource_access_requests(requester_id);
CREATE INDEX IF NOT EXISTS idx_transaction_user ON lingshi_transactions(user_id);

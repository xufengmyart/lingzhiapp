-- 用户反馈系统、数据分析、导航优化、引导文档相关的数据库表
-- 创建时间: 2026-02-11

-- 1. 用户反馈表
CREATE TABLE IF NOT EXISTS user_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    username TEXT,
    feedback_type TEXT NOT NULL,  -- 'navigation', 'feature', 'bug', 'suggestion'
    category TEXT,                -- 分类（针对导航优化：'navigation', 'ui', 'ux'等）
    rating INTEGER,               -- 评分（1-5星）
    content TEXT NOT NULL,        -- 反馈内容
    page TEXT,                    -- 反馈时的页面
    screenshot_url TEXT,          -- 截图URL
    status TEXT DEFAULT 'pending', -- 'pending', 'reviewed', 'resolved', 'rejected'
    priority TEXT DEFAULT 'medium', -- 'low', 'medium', 'high', 'urgent'
    admin_notes TEXT,             -- 管理员备注
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 2. 页面访问统计表
CREATE TABLE IF NOT EXISTS page_visit_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    page_path TEXT NOT NULL,      -- 页面路径
    page_title TEXT,              -- 页面标题
    visit_duration INTEGER,       -- 访问时长（秒）
    referer TEXT,                 -- 来源页面
    device_type TEXT,             -- 设备类型：'desktop', 'mobile', 'tablet'
    browser TEXT,                 -- 浏览器
    os TEXT,                      -- 操作系统
    ip_address TEXT,              -- IP地址
    session_id TEXT,              -- 会话ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 3. 功能使用统计表（用于数据分析）
CREATE TABLE IF NOT EXISTS feature_usage_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    feature_name TEXT NOT NULL,   -- 功能名称（如 'ai_assistant', 'digital_assets'）
    feature_category TEXT,        -- 功能分类
    action TEXT NOT NULL,         -- 动作类型：'view', 'click', 'submit', 'complete'
    metadata TEXT,                -- 额外元数据（JSON格式）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 4. 导航配置表（用于微调优化）
CREATE TABLE IF NOT EXISTS navigation_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nav_group_id TEXT NOT NULL,   -- 导航组ID（如 'ai_assistant', 'resource_hub'）
    nav_item_id TEXT NOT NULL,    -- 导航项ID
    label TEXT NOT NULL,          -- 显示标签
    path TEXT NOT NULL,           -- 路径
    icon_name TEXT,               -- 图标名称
    order_index INTEGER DEFAULT 0, -- 排序索引
    is_visible INTEGER DEFAULT 1, -- 是否可见：1=可见，0=隐藏
    is_highlighted INTEGER DEFAULT 0, -- 是否高亮：1=高亮，0=普通
    description TEXT,             -- 描述文字
    requires_role TEXT,           -- 需要的角色（为空表示所有用户可见）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. 用户引导文档表
CREATE TABLE IF NOT EXISTS user_guide_articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,          -- 标题
    slug TEXT UNIQUE NOT NULL,    -- URL slug
    category TEXT,                -- 分类：'getting_started', 'features', 'tips'
    content TEXT NOT NULL,        -- 内容（Markdown格式）
    order_index INTEGER DEFAULT 0, -- 排序索引
    view_count INTEGER DEFAULT 0, -- 查看次数
    is_published INTEGER DEFAULT 1, -- 是否发布：1=发布，0=草稿
    created_by INTEGER,
    updated_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (updated_by) REFERENCES users(id)
);

-- 6. 用户引导阅读记录表
CREATE TABLE IF NOT EXISTS user_guide_reads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    article_id INTEGER NOT NULL,
    read_time INTEGER DEFAULT 0,  -- 阅读时长（秒）
    completed INTEGER DEFAULT 0,  -- 是否完成：1=完成，0=未完成
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (article_id) REFERENCES user_guide_articles(id)
);

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_user_feedback_user_id ON user_feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_user_feedback_type ON user_feedback(feedback_type);
CREATE INDEX IF NOT EXISTS idx_user_feedback_status ON user_feedback(status);
CREATE INDEX IF NOT EXISTS idx_user_feedback_created_at ON user_feedback(created_at);

CREATE INDEX IF NOT EXISTS idx_page_visit_stats_user_id ON page_visit_stats(user_id);
CREATE INDEX IF NOT EXISTS idx_page_visit_stats_page_path ON page_visit_stats(page_path);
CREATE INDEX IF NOT EXISTS idx_page_visit_stats_created_at ON page_visit_stats(created_at);

CREATE INDEX IF NOT EXISTS idx_feature_usage_stats_user_id ON feature_usage_stats(user_id);
CREATE INDEX IF NOT EXISTS idx_feature_usage_stats_feature_name ON feature_usage_stats(feature_name);
CREATE INDEX IF NOT EXISTS idx_feature_usage_stats_created_at ON feature_usage_stats(created_at);

CREATE INDEX IF NOT EXISTS idx_navigation_config_group_id ON navigation_config(nav_group_id);
CREATE INDEX IF NOT EXISTS idx_navigation_config_is_visible ON navigation_config(is_visible);

CREATE INDEX IF NOT EXISTS idx_user_guide_articles_category ON user_guide_articles(category);
CREATE INDEX IF NOT EXISTS idx_user_guide_articles_is_published ON user_guide_articles(is_published);

CREATE INDEX IF NOT EXISTS idx_user_guide_reads_user_id ON user_guide_reads(user_id);
CREATE INDEX IF NOT EXISTS idx_user_guide_reads_article_id ON user_guide_reads(article_id);

-- 插入默认导航配置（基于当前导航结构）
INSERT INTO navigation_config (nav_group_id, nav_item_id, label, path, icon_name, order_index, is_highlighted, description) VALUES
-- 智能助手
('ai_assistant', 'chat', '智能对话', '/chat', 'MessageSquare', 1, 1, 'AI驱动的智能对话助手'),
('ai_assistant', 'knowledge', '知识库', '/knowledge', 'BookOpen', 2, 0, '系统知识库'),
('ai_assistant', 'culture_knowledge', '文化知识库', '/culture/knowledge', 'Brain', 3, 0, '文化相关的知识内容'),
('ai_assistant', 'culture_translation', '文化转译', '/culture/translation', 'Wand2', 4, 0, 'AI文化内容转译'),
('ai_assistant', 'culture_projects', '文化项目', '/culture/projects', 'Layers', 5, 0, '文化项目管理'),

-- 资源广场
('resource_hub', 'user_resources', '用户资源', '/user-resources', 'Users', 1, 0, '用户资源池'),
('resource_hub', 'project_pool', '项目资源', '/project-pool', 'Box', 2, 0, '项目资源池'),
('resource_hub', 'merchant_pool', '商家资源', '/merchant-pool', 'Building2', 3, 0, '商家资源池'),
('resource_hub', 'bounty_hunter', '赏金任务', '/bounty-hunter', 'Trophy', 4, 0, '赏金任务中心'),
('resource_hub', 'dividend_pool', '分红池', '/dividend-pool', 'DollarSign', 5, 0, '分红池'),

-- 资产价值
('asset_value', 'assets', '数字资产', '/assets', 'Gem', 1, 1, '数字资产管理'),
('asset_value', 'asset_management', '资产管理', '/asset-management', 'Coins', 2, 0, '资产管理工具'),
('asset_value', 'sacred_sites', '文化圣地', '/sacred-sites', 'Map', 3, 0, '文化圣地管理'),
('asset_value', 'aesthetic_tasks', '美学侦探', '/aesthetic-tasks', 'Flower2', 4, 0, '美学侦探任务'),
('asset_value', 'partner', '合伙人计划', '/partner', 'Award', 5, 0, '合伙人计划'),

-- 文化创作
('cultural_creation', 'journey', '用户旅程', '/journey', 'Route', 1, 0, '用户旅程管理'),
('cultural_creation', 'user_learning', '修行记录', '/user-learning', 'GraduationCap', 2, 0, '修行记录'),
('cultural_creation', 'economy', '经济模型', '/economy', 'TrendUp', 3, 0, '经济模型查看'),
('cultural_creation', 'recharge', '购买灵值', '/recharge', 'Wallet', 4, 0, '灵值充值'),

-- 动态资讯
('news_updates', 'company_news', '公司动态', '/company/news', 'FileText', 1, 0, '公司最新动态'),
('news_updates', 'company_projects', '项目动态', '/company/projects', 'Box', 2, 0, '项目最新动态'),
('news_updates', 'company_info', '平台信息', '/company/info', 'Info', 3, 0, '平台信息介绍'),
('news_updates', 'company_users', '数据统计', '/company/users', 'Target', 4, 0, '数据统计分析');

-- 插入默认引导文档
INSERT INTO user_guide_articles (title, slug, category, content, order_index) VALUES
('快速入门', 'getting-started', 'getting_started', '# 快速入门指南\n\n欢迎使用灵值元宇宙！本指南将帮助您快速上手。\n\n## 第一步：注册账号\n\n访问 https://meiyueart.com，点击"注册"按钮创建账号。\n\n## 第二步：完善资料\n\n登录后，前往个人中心完善您的个人资料。\n\n## 第三步：探索功能\n\n- **智能助手**：与AI对话，获取知识\n- **资源广场**：发现和匹配资源\n- **资产价值**：管理您的数字资产\n- **文化创作**：参与文化创作活动\n\n## 第四步：开始使用\n\n选择您感兴趣的功能，开始探索吧！', 1),

('导航使用指南', 'navigation-guide', 'getting_started', '# 导航使用指南\n\n了解如何使用系统的导航功能。\n\n## 五大核心分类\n\n### 1. 智能助手 🤖\nAI驱动的核心功能，包括智能对话、知识库等。\n\n### 2. 资源广场 🌐\n资源匹配与交易平台。\n\n### 3. 资产价值 💎\n资产管理和价值实现。\n\n### 4. 文化创作 🎨\n文化内容创作与管理。\n\n### 5. 动态资讯 📢\n平台最新动态和资讯。\n\n## 快捷功能\n\n右侧功能区包含：帮助、指南、个人中心、反馈等功能。', 2),

('功能功能说明', 'feature-guide', 'features', '# 功能功能说明\n\n## 核心功能详解\n\n### 智能对话\n与AI助手进行智能对话，获取帮助和建议。\n\n### 数字资产\n管理您的数字资产，包括通证和SBT。\n\n### 文化圣地\n探索和管理文化圣地资源。\n\n### 美学侦探\n参与美学侦探任务，赚取奖励。\n\n## 商家功能\n\n### 商家工作台\n登记客户群、推荐商家、核销优惠券。\n\n## 专家功能\n\n### 专家工作台\n承接任务、提交AIGC作品。', 1),

('常见问题', 'faq', 'tips', '# 常见问题\n\n## 账号相关\n\n### 如何修改密码？\n前往个人中心 → 安全设置 → 修改密码。\n\n### 如何绑定手机？\n前往个人中心 → 安全设置 → 绑定手机。\n\n## 功能相关\n\n### 如何提交反馈？\n点击右上角的"反馈"按钮，填写反馈表单。\n\n### 如何查看我的资产？\n导航到"资产价值" → "数字资产"。', 3);

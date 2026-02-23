-- ==========================================
-- 通知系统数据库设计
-- ==========================================

-- 通知表
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,                       -- 接收通知的用户ID
    notification_type TEXT NOT NULL,                -- 通知类型：resource_match, project_application, project_approval, profit_distribution, etc.
    title TEXT NOT NULL,                            -- 通知标题
    content TEXT,                                   -- 通知内容
    related_type TEXT,                              -- 关联类型：resource, project, participation, profit
    related_id INTEGER,                             -- 关联ID
    priority TEXT DEFAULT 'normal',                 -- 优先级：low, normal, high, urgent
    is_read BOOLEAN DEFAULT 0,                      -- 是否已读
    read_at TIMESTAMP,                              -- 阅读时间
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT,                                  -- 元数据（JSON）
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);
CREATE INDEX idx_notifications_type ON notifications(notification_type);
CREATE INDEX idx_notifications_created_at ON notifications(created_at DESC);

-- 通知偏好设置表
CREATE TABLE IF NOT EXISTS notification_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,                -- 用户ID
    email_notifications BOOLEAN DEFAULT 1,          -- 邮件通知
    push_notifications BOOLEAN DEFAULT 1,           -- 推送通知
    sms_notifications BOOLEAN DEFAULT 0,            -- 短信通知
    resource_match_notifications BOOLEAN DEFAULT 1, -- 资源匹配通知
    project_updates BOOLEAN DEFAULT 1,              -- 项目更新通知
    profit_notifications BOOLEAN DEFAULT 1,         -- 分润通知
    system_notifications BOOLEAN DEFAULT 1,         -- 系统通知
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_notification_preferences_user_id ON notification_preferences(user_id);

-- 通知模板表
CREATE TABLE IF NOT EXISTS notification_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_code TEXT NOT NULL UNIQUE,             -- 模板代码
    template_name TEXT NOT NULL,                    -- 模板名称
    notification_type TEXT NOT NULL,                -- 通知类型
    title_template TEXT NOT NULL,                   -- 标题模板
    content_template TEXT NOT NULL,                 -- 内容模板
    is_active BOOLEAN DEFAULT 1,                    -- 是否启用
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入默认通知模板
INSERT OR IGNORE INTO notification_templates (template_code, template_name, notification_type, title_template, content_template) VALUES
('resource_matched', '资源匹配通知', 'resource_match', '您的资源 {{resource_name}} 匹配到新项目 {{project_name}}', '系统自动为您匹配到项目 {{project_name}}，匹配分数：{{match_score}}分。点击查看详情。'),
('project_applied', '项目申请通知', 'project_application', '用户 {{username}} 申请参与项目 {{project_name}}', '用户 {{username}} 申请以{{participation_type}}身份参与项目 {{project_name}}。贡献描述：{{contribution_description}}'),
('project_approved', '项目申请通过', 'project_approval', '您参与项目 {{project_name}} 的申请已通过', '恭喜！您参与项目 {{project_name}} 的申请已通过。请尽快完成项目参与手续。'),
('profit_distributed', '分润到账通知', 'profit_distribution', '您获得项目 {{project_name}} 分润 ¥{{amount}}', '您的项目 {{project_name}} 分润已到账，金额：¥{{amount}}。请查收。');

-- 触发器：自动更新 updated_at
CREATE TRIGGER IF NOT EXISTS update_notification_preferences_timestamp
AFTER UPDATE ON notification_preferences
BEGIN
    UPDATE notification_preferences SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

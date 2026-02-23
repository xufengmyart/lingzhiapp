-- ==========================================
-- 私有资源库及项目管理系统数据库设计
-- ==========================================

-- 1. 私有资源库表
CREATE TABLE IF NOT EXISTS private_resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,                       -- 拥有者用户ID
    resource_name TEXT NOT NULL,                    -- 资源名称
    resource_type TEXT NOT NULL,                    -- 资源类型：government(政府), enterprise(企业), personal(人脉), other(其他)
    department TEXT,                                -- 部门
    contact_name TEXT NOT NULL,                     -- 联系人姓名
    contact_phone TEXT NOT NULL,                    -- 联系电话
    contact_email TEXT,                             -- 联系邮箱
    position TEXT,                                  -- 职位（选填）
    description TEXT,                               -- 资源描述
    authorization_status TEXT DEFAULT 'unauthorized', -- 授权状态：unauthorized(未授权), authorized(已授权), pending(待授权)
    authorization_note TEXT,                        -- 授权说明
    valid_from DATE,                                -- 有效期开始
    valid_until DATE,                               -- 有效期结束
    can_solve TEXT,                                 -- 能解决的问题描述
    risk_level TEXT DEFAULT 'low',                  -- 风险等级：low, medium, high
    verification_status TEXT DEFAULT 'pending',     -- 验证状态：pending(待验证), verified(已验证), rejected(已拒绝)
    visibility TEXT DEFAULT 'private',              -- 可见性：private(私有), matchable(可匹配)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,                           -- 软删除
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_private_resources_user_id ON private_resources(user_id);
CREATE INDEX idx_private_resources_status ON private_resources(authorization_status);
CREATE INDEX idx_private_resources_type ON private_resources(resource_type);
CREATE INDEX idx_private_resources_visibility ON private_resources(visibility);

-- 2. 资源需求表
CREATE TABLE IF NOT EXISTS resource_requirements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,                    -- 关联项目
    requirement_name TEXT NOT NULL,                 -- 需求名称
    requirement_type TEXT NOT NULL,                 -- 需求类型
    description TEXT,                               -- 需求描述
    priority TEXT DEFAULT 'medium',                 -- 优先级：low, medium, high, urgent
    status TEXT DEFAULT 'open',                     -- 状态：open(开放中), filled(已满足), closed(已关闭)
    quantity_needed INTEGER DEFAULT 1,              -- 需要数量
    quantity_matched INTEGER DEFAULT 0,             -- 已匹配数量
    urgency_level TEXT DEFAULT 'normal',            -- 紧急程度：low, normal, high
    budget_range TEXT,                              -- 预算范围
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES company_projects(id) ON DELETE CASCADE
);

CREATE INDEX idx_resource_requirements_project_id ON resource_requirements(project_id);
CREATE INDEX idx_resource_requirements_status ON resource_requirements(status);

-- 3. 资源匹配表
CREATE TABLE IF NOT EXISTS resource_matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_id INTEGER NOT NULL,                   -- 私有资源ID
    project_id INTEGER NOT NULL,                    -- 项目ID
    requirement_id INTEGER,                         -- 需求ID（可选）
    match_score REAL DEFAULT 0,                     -- 匹配分数 (0-100)
    match_reason TEXT,                              -- 匹配原因
    status TEXT DEFAULT 'pending',                  -- 状态：pending(待确认), approved(已接受), rejected(已拒绝)
    initiated_by TEXT DEFAULT 'system',             -- 发起方：system(系统), user(用户), admin(管理员)
    resource_owner_confirmed BOOLEAN DEFAULT 0,    -- 资源拥有者确认
    project_manager_confirmed BOOLEAN DEFAULT 0,   -- 项目经理确认
    match_confirmed_at TIMESTAMP,                   -- 匹配确认时间
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resource_id) REFERENCES private_resources(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES company_projects(id) ON DELETE CASCADE,
    FOREIGN KEY (requirement_id) REFERENCES resource_requirements(id) ON DELETE SET NULL
);

CREATE INDEX idx_resource_matches_resource_id ON resource_matches(resource_id);
CREATE INDEX idx_resource_matches_project_id ON resource_matches(project_id);
CREATE INDEX idx_resource_matches_status ON resource_matches(status);
CREATE INDEX idx_resource_matches_score ON resource_matches(match_score DESC);

-- 4. 项目参与表
CREATE TABLE IF NOT EXISTS project_participations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,                    -- 项目ID
    user_id INTEGER NOT NULL,                       -- 用户ID
    participation_type TEXT NOT NULL,               -- 参与类型：resource_provider(资源提供者), executor(执行者), investor(投资方)
    role_name TEXT,                                 -- 角色名称
    status TEXT DEFAULT 'applied',                  -- 状态：applied(已申请), approved(已批准), active(进行中), completed(已完成), terminated(已终止), rejected(已拒绝)
    contribution_description TEXT,                  -- 贡献描述
    contribution_share REAL DEFAULT 0,              -- 贡献占比 (0-100)
    resource_ids TEXT,                              -- 关联的资源ID列表（JSON数组）
    payment_status TEXT DEFAULT 'unpaid',           -- 支付状态：unpaid(未支付), paid(已支付), refunded(已退款), waived(已免除)
    payment_amount REAL DEFAULT 0,                  -- 支付金额
    payment_method TEXT,                            -- 支付方式
    payment_time TIMESTAMP,                         -- 支付时间
    payment_transaction_id TEXT,                    -- 支付交易ID
    approved_by INTEGER,                            -- 审批人ID
    approved_at TIMESTAMP,                          -- 审批时间
    start_date DATE,                                -- 参与开始日期
    end_date DATE,                                  -- 参与结束日期
    notes TEXT,                                     -- 备注
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES company_projects(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (approved_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_project_participations_project_id ON project_participations(project_id);
CREATE INDEX idx_project_participations_user_id ON project_participations(user_id);
CREATE INDEX idx_project_participations_status ON project_participations(status);
CREATE INDEX idx_project_participations_payment ON project_participations(payment_status);

-- 5. 分润记录表
CREATE TABLE IF NOT EXISTS profit_sharing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,                    -- 项目ID
    user_id INTEGER NOT NULL,                       -- 用户ID
    participation_id INTEGER NOT NULL,              -- 参与记录ID
    total_profit REAL,                              -- 项目总收益
    user_share REAL,                                -- 用户应得分润
    share_percentage REAL DEFAULT 0,                -- 分润比例 (0-100)
    sharing_rule TEXT,                              -- 分润规则描述
    status TEXT DEFAULT 'pending',                  -- 状态：pending(待结算), calculated(已计算), distributed(已发放), cancelled(已取消)
    settlement_period TEXT,                         -- 结算周期：monthly(月结), quarterly(季结), upon_delivery(交付后)
    distribution_method TEXT,                       -- 发放方式
    distribution_time TIMESTAMP,                    -- 发放时间
    distribution_transaction_id TEXT,               -- 发放交易ID
    verified_by INTEGER,                            -- 验证人ID
    verified_at TIMESTAMP,                          -- 验证时间
    notes TEXT,                                     -- 备注
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES company_projects(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (participation_id) REFERENCES project_participations(id) ON DELETE CASCADE,
    FOREIGN KEY (verified_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_profit_sharing_project_id ON profit_sharing(project_id);
CREATE INDEX idx_profit_sharing_user_id ON profit_sharing(user_id);
CREATE INDEX idx_profit_sharing_status ON profit_sharing(status);

-- 6. 项目里程碑表
CREATE TABLE IF NOT EXISTS project_milestones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,                    -- 项目ID
    milestone_name TEXT NOT NULL,                   -- 里程碑名称
    description TEXT,                               -- 描述
    planned_date DATE NOT NULL,                     -- 计划日期
    actual_date DATE,                               -- 实际完成日期
    status TEXT DEFAULT 'pending',                  -- 状态：pending(待开始), in_progress(进行中), completed(已完成), delayed(延期), cancelled(已取消)
    progress_percentage REAL DEFAULT 0,             -- 进度百分比
    deliverables TEXT,                              -- 交付物描述（JSON）
    dependencies TEXT,                              -- 依赖的里程碑ID列表（JSON）
    responsible_person_id INTEGER,                  -- 负责人ID
    budget_allocated REAL DEFAULT 0,                -- 分配预算
    actual_cost REAL DEFAULT 0,                     -- 实际成本
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,                         -- 完成时间
    FOREIGN KEY (project_id) REFERENCES company_projects(id) ON DELETE CASCADE,
    FOREIGN KEY (responsible_person_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_project_milestones_project_id ON project_milestones(project_id);
CREATE INDEX idx_project_milestones_status ON project_milestones(status);
CREATE INDEX idx_project_milestones_planned_date ON project_milestones(planned_date);

-- 7. 项目任务表
CREATE TABLE IF NOT EXISTS project_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,                    -- 项目ID
    milestone_id INTEGER,                           -- 里程碑ID（可选）
    task_name TEXT NOT NULL,                        -- 任务名称
    description TEXT,                               -- 任务描述
    assignee_id INTEGER,                            -- 负责人ID
    status TEXT DEFAULT 'pending',                  -- 状态：pending(待开始), in_progress(进行中), completed(已完成), blocked(被阻塞), cancelled(已取消)
    priority TEXT DEFAULT 'medium',                 -- 优先级：low, medium, high, urgent
    estimated_hours REAL DEFAULT 0,                 -- 预估工时
    actual_hours REAL DEFAULT 0,                    -- 实际工时
    start_date DATE,                                -- 开始日期
    due_date DATE,                                  -- 截止日期
    completed_at TIMESTAMP,                         -- 完成时间
    tags TEXT,                                      -- 标签（JSON数组）
    dependencies TEXT,                              -- 依赖的任务ID列表（JSON）
    attachments TEXT,                               -- 附件列表（JSON）
    comments TEXT,                                  -- 评论（JSON数组）
    created_by INTEGER,                             -- 创建人ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES company_projects(id) ON DELETE CASCADE,
    FOREIGN KEY (milestone_id) REFERENCES project_milestones(id) ON DELETE SET NULL,
    FOREIGN KEY (assignee_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_project_tasks_project_id ON project_tasks(project_id);
CREATE INDEX idx_project_tasks_milestone_id ON project_tasks(milestone_id);
CREATE INDEX idx_project_tasks_assignee_id ON project_tasks(assignee_id);
CREATE INDEX idx_project_tasks_status ON project_tasks(status);
CREATE INDEX idx_project_tasks_due_date ON project_tasks(due_date);

-- 8. 项目工作流记录表
CREATE TABLE IF NOT EXISTS project_workflow_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,                    -- 项目ID
    action_type TEXT NOT NULL,                      -- 动作类型：created, updated, milestone_completed, task_assigned, user_joined, status_changed
    action_description TEXT,                        -- 动作描述
    actor_id INTEGER,                               -- 操作人ID
    actor_type TEXT DEFAULT 'user',                 -- 操作人类型：user, system
    metadata TEXT,                                  -- 元数据（JSON）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES company_projects(id) ON DELETE CASCADE,
    FOREIGN KEY (actor_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_project_workflow_logs_project_id ON project_workflow_logs(project_id);
CREATE INDEX idx_project_workflow_logs_created_at ON project_workflow_logs(created_at DESC);

-- 9. 资源访问授权记录表
CREATE TABLE IF NOT EXISTS resource_access_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_id INTEGER NOT NULL,                   -- 资源ID
    requester_id INTEGER,                           -- 请求者ID
    request_type TEXT NOT NULL,                     -- 请求类型：view, contact, use
    request_reason TEXT,                            -- 请求原因
    project_id INTEGER,                             -- 关联项目ID
    access_granted BOOLEAN DEFAULT 0,               -- 是否授权
    granted_by INTEGER,                             -- 授权人ID
    granted_at TIMESTAMP,                           -- 授权时间
    access_duration TEXT,                           -- 授权时长
    expiry_time TIMESTAMP,                          -- 授权过期时间
    notes TEXT,                                     -- 备注
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resource_id) REFERENCES private_resources(id) ON DELETE CASCADE,
    FOREIGN KEY (requester_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (project_id) REFERENCES company_projects(id) ON DELETE SET NULL,
    FOREIGN KEY (granted_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_resource_access_logs_resource_id ON resource_access_logs(resource_id);
CREATE INDEX idx_resource_access_logs_requester_id ON resource_access_logs(requester_id);

-- 10. 项目资金流水表
CREATE TABLE IF NOT EXISTS project_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,                    -- 项目ID
    transaction_type TEXT NOT NULL,                 -- 交易类型：participation_fee(参与费), investment(投资), profit_distribution(分润), refund(退款)
    amount REAL NOT NULL,                           -- 金额
    currency TEXT DEFAULT 'CNY',                    -- 货币
    user_id INTEGER NOT NULL,                       -- 关联用户ID
    transaction_status TEXT DEFAULT 'pending',      -- 交易状态：pending(待处理), completed(已完成), failed(失败), cancelled(已取消)
    payment_method TEXT,                            -- 支付方式
    payment_channel TEXT,                           -- 支付渠道
    transaction_id TEXT,                            -- 交易ID（第三方）
    reference_id TEXT,                              -- 关联ID（如参与记录ID）
    description TEXT,                               -- 描述
    processed_by INTEGER,                           -- 处理人ID
    processed_at TIMESTAMP,                         -- 处理时间
    metadata TEXT,                                  -- 元数据（JSON）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES company_projects(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (processed_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_project_transactions_project_id ON project_transactions(project_id);
CREATE INDEX idx_project_transactions_user_id ON project_transactions(user_id);
CREATE INDEX idx_project_transactions_status ON project_transactions(transaction_status);

-- 添加一些视图以方便查询
-- 1. 项目统计视图
CREATE VIEW IF NOT EXISTS project_stats_view AS
SELECT 
    p.id as project_id,
    p.project_name,
    p.status,
    COUNT(DISTINCT pp.id) as participant_count,
    COUNT(DISTINCT pt.id) as task_count,
    COUNT(DISTINCT pm.id) as milestone_count,
    COALESCE(SUM(pt.actual_hours), 0) as total_hours,
    COALESCE(SUM(CASE WHEN pt.status = 'completed' THEN 1 ELSE 0 END), 0) as completed_tasks
FROM company_projects p
LEFT JOIN project_participations pp ON p.id = pp.project_id AND pp.status IN ('active', 'completed')
LEFT JOIN project_tasks pt ON p.id = pt.project_id
LEFT JOIN project_milestones pm ON p.id = pm.project_id
GROUP BY p.id;

-- 2. 用户资源统计视图
CREATE VIEW IF NOT EXISTS user_resource_stats_view AS
SELECT 
    u.id as user_id,
    u.username,
    COUNT(DISTINCT pr.id) as total_resources,
    COUNT(DISTINCT CASE WHEN pr.authorization_status = 'authorized' THEN pr.id END) as authorized_resources,
    COUNT(DISTINCT rm.id) as total_matches,
    COUNT(DISTINCT CASE WHEN rm.status = 'approved' THEN rm.id END) as approved_matches,
    COALESCE(SUM(ps.user_share), 0) as total_profits
FROM users u
LEFT JOIN private_resources pr ON u.id = pr.user_id AND pr.deleted_at IS NULL
LEFT JOIN resource_matches rm ON pr.id = rm.resource_id
LEFT JOIN project_participations pp ON u.id = pp.user_id
LEFT JOIN profit_sharing ps ON pp.id = ps.participation_id
GROUP BY u.id;

-- 触发器：自动更新 updated_at 字段
CREATE TRIGGER IF NOT EXISTS update_private_resources_timestamp
AFTER UPDATE ON private_resources
BEGIN
    UPDATE private_resources SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_resource_requirements_timestamp
AFTER UPDATE ON resource_requirements
BEGIN
    UPDATE resource_requirements SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_resource_matches_timestamp
AFTER UPDATE ON resource_matches
BEGIN
    UPDATE resource_matches SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_project_participations_timestamp
AFTER UPDATE ON project_participations
BEGIN
    UPDATE project_participations SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_profit_sharing_timestamp
AFTER UPDATE ON profit_sharing
BEGIN
    UPDATE profit_sharing SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_project_milestones_timestamp
AFTER UPDATE ON project_milestones
BEGIN
    UPDATE project_milestones SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_project_tasks_timestamp
AFTER UPDATE ON project_tasks
BEGIN
    UPDATE project_tasks SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_project_transactions_timestamp
AFTER UPDATE ON project_transactions
BEGIN
    UPDATE project_transactions SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

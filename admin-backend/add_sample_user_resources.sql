-- 为用户添加示例资源数据
-- 创建时间: 2026-02-18

-- 为许韩玲 (ID: 1028) 添加资源
INSERT INTO user_resources (user_id, resource_type, resource_name, description, availability, estimated_value, status, tags, created_at, updated_at)
VALUES
(1028, '灵值', '每日签到奖励', '通过每日签到获得的灵值', 'active', 10.00, 'active', '["签到", "奖励", "灵值"]', datetime('now'), datetime('now')),
(1028, '知识', '文化知识包', '中华传统文化知识合集', 'active', 50.00, 'active', '["知识", "文化", "学习"]', datetime('now'), datetime('now')),
(1028, '资源', '数字资产', '灵值生态园数字资产', 'active', 100.00, 'active', '["资产", "数字", "生态"]', datetime('now'), datetime('now'));

-- 为许明芳 (ID: 1035) 添加资源
INSERT INTO user_resources (user_id, resource_type, resource_name, description, availability, estimated_value, status, tags, created_at, updated_at)
VALUES
(1035, '灵值', '每日签到奖励', '通过每日签到获得的灵值', 'active', 10.00, 'active', '["签到", "奖励", "灵值"]', datetime('now'), datetime('now')),
(1035, '知识', '新手礼包', '新手入门知识包', 'active', 20.00, 'active', '["新手", "礼包", "知识"]', datetime('now'), datetime('now'));

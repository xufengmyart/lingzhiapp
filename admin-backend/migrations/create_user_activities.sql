-- 创建用户活动统计视图
CREATE VIEW IF NOT EXISTS user_activities_view AS
SELECT
    1 as id,
    SUBSTR(username, 1, 1) || '用户' || ROW_NUMBER() OVER (PARTITION BY 1 ORDER BY created_at) as username,
    '注册加入' as action,
    '新用户注册，获得新人奖励100灵值' as description,
    'register' as type,
    datetime(created_at) as created_at,
    total_lingzhi as lingzhi
FROM users
WHERE id NOT IN (1, 10)
ORDER BY created_at DESC
LIMIT 50;

-- 查看用户活动数据
SELECT * FROM user_activities_view LIMIT 20;

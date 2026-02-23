-- 修复 admin 用户密码的 SQL 脚本
-- 在生产服务器上执行: sqlite3 /root/lingzhi_ecosystem.db < fix_admin_password.sql

-- 方法 1: 如果使用 werkzeug 生成哈希（推荐）
-- 需要先在 Python 中生成密码哈希
-- from werkzeug.security import generate_password_hash
-- hash = generate_password_hash('admin123')
-- 然后将生成的哈希替换下面的 $2b$12$... 部分

UPDATE users
SET password_hash = '$2b$12$RWy1TQmJqOqX8yOqYqYqY.qYqYqYqYqYqYqYqYqYqYqYqYqYqYqYq'
WHERE username = 'admin';

-- 方法 2: 重新创建 admin 用户（更简单）
DELETE FROM users WHERE username = 'admin';

INSERT INTO users (username, password_hash, email, phone, status, is_verified)
VALUES (
    'admin',
    '$2b$12$RWy1TQmJqOqX8yOqYqYqY.qYqYqYqYqYqYqYqYqYqYqYqYqYqYqYq',
    'admin@meiyueart.com',
    '',
    'active',
    1
);

-- 验证修改
SELECT id, username, substr(password_hash, 1, 30) as password_hash_preview
FROM users
WHERE username = 'admin';

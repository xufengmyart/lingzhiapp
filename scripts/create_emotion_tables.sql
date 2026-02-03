-- =====================================================
-- 灵值智能体 v8.1 - 情绪系统数据库表结构
-- 版本: v8.1 (PostgreSQL)
-- 创建日期: 2025年1月15日
-- 主体公司: 陕西媄月商业艺术有限责任公司
-- =====================================================

-- 创建情绪记录表
CREATE TABLE IF NOT EXISTS emotion_records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    emotion VARCHAR(20) NOT NULL,
    emotion_name VARCHAR(20) NOT NULL,
    intensity FLOAT NOT NULL,
    context TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

-- 创建情绪记录表索引
CREATE INDEX IF NOT EXISTS ix_emotion_records_user_id ON emotion_records(user_id);
CREATE INDEX IF NOT EXISTS ix_emotion_records_created_at ON emotion_records(created_at);
CREATE INDEX IF NOT EXISTS ix_emotion_records_emotion ON emotion_records(emotion);

-- 添加情绪记录表注释
COMMENT ON TABLE emotion_records IS '情绪记录表';
COMMENT ON COLUMN emotion_records.id IS '主键ID';
COMMENT ON COLUMN emotion_records.user_id IS '用户ID（外键）';
COMMENT ON COLUMN emotion_records.emotion IS '情绪类型（joy, sadness, anger, fear, surprise, disgust, neutral）';
COMMENT ON COLUMN emotion_records.emotion_name IS '情绪名称（中文）';
COMMENT ON COLUMN emotion_records.intensity IS '情绪强度（0.0-1.0）';
COMMENT ON COLUMN emotion_records.context IS '情绪上下文描述';
COMMENT ON COLUMN emotion_records.created_at IS '记录创建时间';

-- =====================================================

-- 创建情绪日记表
CREATE TABLE IF NOT EXISTS emotion_diaries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    content TEXT NOT NULL,
    emotion VARCHAR(20) NOT NULL,
    emotion_name VARCHAR(20) NOT NULL,
    intensity FLOAT NOT NULL,
    tags JSON,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

-- 创建情绪日记表索引
CREATE INDEX IF NOT EXISTS ix_emotion_diaries_user_id ON emotion_diaries(user_id);
CREATE INDEX IF NOT EXISTS ix_emotion_diaries_created_at ON emotion_diaries(created_at);

-- 添加情绪日记表注释
COMMENT ON TABLE emotion_diaries IS '情绪日记表';
COMMENT ON COLUMN emotion_diaries.id IS '主键ID';
COMMENT ON COLUMN emotion_diaries.user_id IS '用户ID（外键）';
COMMENT ON COLUMN emotion_diaries.content IS '日记内容';
COMMENT ON COLUMN emotion_diaries.emotion IS '情绪类型（joy, sadness, anger, fear, surprise, disgust, neutral）';
COMMENT ON COLUMN emotion_diaries.emotion_name IS '情绪名称（中文）';
COMMENT ON COLUMN emotion_diaries.intensity IS '情绪强度（0.0-1.0）';
COMMENT ON COLUMN emotion_diaries.tags IS '标签（JSON格式）';
COMMENT ON COLUMN emotion_diaries.created_at IS '日记创建时间';

-- =====================================================

-- 验证表创建成功
SELECT
    table_name,
    table_comment AS comment
FROM (
    SELECT
        schemaname,
        tablename AS table_name,
        obj_description((schemaname || '.' || tablename)::regclass, 'pg_class') AS table_comment
    FROM pg_tables
    WHERE tablename IN ('emotion_records', 'emotion_diaries')
    AND schemaname = 'public'
) AS t;

-- 验证索引创建成功
SELECT
    tablename,
    indexname,
    idx_scan AS index_scans,
    idx_tup_read AS tuples_read
FROM pg_stat_user_indexes
WHERE tablename IN ('emotion_records', 'emotion_diaries')
ORDER BY tablename, indexname;

-- =====================================================

-- 创建测试数据（可选）
-- INSERT INTO emotion_records (user_id, emotion, emotion_name, intensity, context)
-- VALUES
--     (1, 'joy', '快乐', 0.9, '今天完成了重要的工作任务'),
--     (1, 'calm', '平静', 0.7, '享受午后的宁静时光'),
--     (2, 'sadness', '悲伤', 0.6, '想起了过去的一些事情');

-- =====================================================

-- 部署完成提示
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE '情绪系统数据库表创建完成！';
    RAISE NOTICE '========================================';
    RAISE NOTICE '已创建的表:';
    RAISE NOTICE '  - emotion_records (情绪记录表)';
    RAISE NOTICE '  - emotion_diaries (情绪日记表)';
    RAISE NOTICE '========================================';
END $$;

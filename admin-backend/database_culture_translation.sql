-- 文化转译系统数据库表
-- 创建时间: 2026-02-20

-- 1. 转译项目表（存储可参与的转译项目类型）
CREATE TABLE IF NOT EXISTS translation_projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_code TEXT UNIQUE NOT NULL,       -- 项目代码，如 'aesthetic_detective', 'culture_creation'
    title TEXT NOT NULL,                     -- 项目标题
    description TEXT,                        -- 项目描述
    project_type TEXT NOT NULL,              -- 项目类型：'text', 'image', 'audio', 'video', 'comprehensive'
    category TEXT NOT NULL,                  -- 分类：'heritage', 'folklore', 'art', 'architecture', 'cuisine'
    difficulty_level TEXT DEFAULT 'medium',  -- 难度等级：'easy', 'medium', 'hard'
    status TEXT DEFAULT 'active',            -- 状态：'active', 'paused', 'ended'
    requirements TEXT,                       -- 转译要求（JSON格式）
    example_template TEXT,                   -- 示例模板
    base_reward INTEGER DEFAULT 0,           -- 基础奖励灵值
    max_participants INTEGER,                -- 最大参与人数
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 转译任务表（存储具体的转译任务）
CREATE TABLE IF NOT EXISTS translation_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,             -- 关联项目ID
    task_code TEXT UNIQUE NOT NULL,          -- 任务代码
    title TEXT NOT NULL,                     -- 任务标题
    description TEXT,                        -- 任务描述
    source_content TEXT,                     -- 原始内容（需要转译的内容）
    source_type TEXT NOT NULL,               -- 原始内容类型：'text', 'image_url', 'audio_url', 'video_url'
    target_type TEXT NOT NULL,               -- 目标类型：'text', 'image', 'audio', 'video'
    translation_prompt TEXT,                 -- 转译提示词
    status TEXT DEFAULT 'available',         -- 状态：'available', 'in_progress', 'completed', 'cancelled'
    reward INTEGER DEFAULT 0,                -- 任务奖励灵值
    max_attempts INTEGER DEFAULT 1,          -- 最大尝试次数
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES translation_projects(id)
);

-- 3. 转译作品表（存储用户提交的转译作品）
CREATE TABLE IF NOT EXISTS translation_works (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,                -- 关联任务ID
    user_id INTEGER NOT NULL,               -- 提交用户ID
    username TEXT,                           -- 用户名
    original_content TEXT,                   -- 原始内容
    translated_content TEXT,                 -- 转译后内容
    content_type TEXT NOT NULL,              -- 内容类型：'text', 'image_url', 'audio_url', 'video_url'
    ai_assisted INTEGER DEFAULT 0,           -- 是否使用AI辅助：0=否，1=是
    ai_model TEXT,                           -- 使用的AI模型
    submission_notes TEXT,                   -- 提交备注
    status TEXT DEFAULT 'pending',           -- 状态：'pending', 'under_review', 'approved', 'rejected'
    review_score INTEGER,                    -- 审核评分（0-100）
    reviewer_id INTEGER,                     -- 审核人ID
    review_notes TEXT,                       -- 审核备注
    reward_issued INTEGER DEFAULT 0,         -- 是否发放奖励：0=否，1=是
    lingzhi_reward INTEGER DEFAULT 0,        -- 实际奖励灵值
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES translation_tasks(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (reviewer_id) REFERENCES users(id)
);

-- 4. 转译流程表（记录转译的流程状态和步骤）
CREATE TABLE IF NOT EXISTS translation_processes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_id INTEGER NOT NULL,                -- 关联作品ID
    process_type TEXT NOT NULL,              -- 流程类型：'create', 'translate', 'optimize', 'submit'
    current_step TEXT NOT NULL,              -- 当前步骤
    steps_completed TEXT,                    -- 已完成步骤（JSON数组）
    steps_pending TEXT,                      -- 待完成步骤（JSON数组）
    step_data TEXT,                          -- 每个步骤的数据（JSON格式）
    status TEXT DEFAULT 'in_progress',       -- 状态：'pending', 'in_progress', 'completed', 'failed'
    progress INTEGER DEFAULT 0,              -- 进度（0-100）
    error_message TEXT,                      -- 错误信息
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (work_id) REFERENCES translation_works(id)
);

-- 5. 转译步骤详情表（存储每个步骤的详细信息）
CREATE TABLE IF NOT EXISTS translation_process_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    process_id INTEGER NOT NULL,             -- 关联流程ID
    step_name TEXT NOT NULL,                 -- 步骤名称
    step_type TEXT NOT NULL,                 -- 步骤类型：'input', 'ai_process', 'review', 'output'
    step_order INTEGER NOT NULL,             -- 步骤顺序
    step_status TEXT DEFAULT 'pending',      -- 步骤状态：'pending', 'in_progress', 'completed', 'failed'
    input_data TEXT,                         -- 输入数据（JSON格式）
    output_data TEXT,                        -- 输出数据（JSON格式）
    ai_model TEXT,                           -- 使用的AI模型
    processing_time INTEGER,                 -- 处理时间（毫秒）
    error_message TEXT,                      -- 错误信息
    started_at TIMESTAMP,                    -- 开始时间
    completed_at TIMESTAMP,                  -- 完成时间
    FOREIGN KEY (process_id) REFERENCES translation_processes(id)
);

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_translation_projects_status ON translation_projects(status);
CREATE INDEX IF NOT EXISTS idx_translation_projects_type ON translation_projects(project_type);
CREATE INDEX IF NOT EXISTS idx_translation_projects_category ON translation_projects(category);

CREATE INDEX IF NOT EXISTS idx_translation_tasks_project_id ON translation_tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_translation_tasks_status ON translation_tasks(status);
CREATE INDEX IF NOT EXISTS idx_translation_tasks_code ON translation_tasks(task_code);

CREATE INDEX IF NOT EXISTS idx_translation_works_task_id ON translation_works(task_id);
CREATE INDEX IF NOT EXISTS idx_translation_works_user_id ON translation_works(user_id);
CREATE INDEX IF NOT EXISTS idx_translation_works_status ON translation_works(status);
CREATE INDEX IF NOT EXISTS idx_translation_works_created_at ON translation_works(created_at);

CREATE INDEX IF NOT EXISTS idx_translation_processes_work_id ON translation_processes(work_id);
CREATE INDEX IF NOT EXISTS idx_translation_processes_status ON translation_processes(status);
CREATE INDEX IF NOT EXISTS idx_translation_processes_type ON translation_processes(process_type);

CREATE INDEX IF NOT EXISTS idx_translation_process_steps_process_id ON translation_process_steps(process_id);
CREATE INDEX IF NOT EXISTS idx_translation_process_steps_order ON translation_process_steps(step_order);

-- 插入默认转译项目
INSERT INTO translation_projects (project_code, title, description, project_type, category, difficulty_level, requirements, base_reward) VALUES
(
    'aesthetic_detective',
    '西安美学侦探',
    '通过摄影任务探索西安城市美学，将西安文化转译为视觉艺术',
    'image',
    'heritage',
    'easy',
    '{"description":"拍摄西安城市文化相关的照片，展现西安的美学价值","content_type":"image","max_size":"10MB","formats":["jpg","jpeg","png","webp"],"requirements":["照片需拍摄于西安地区","内容需体现西安文化元素","构图美观，画质清晰","附带50-200字的文化解读"]}',
    50
),
(
    'culture_creation',
    '文化创作',
    '创作文化作品，将传统文化转译为现代艺术形式',
    'comprehensive',
    'art',
    'medium',
    '{"description":"基于传统文化元素创作现代艺术作品","content_types":["text","image","video"],"requirements":["主题需基于传统文化","展现形式需符合现代审美","具有创新性和艺术性","附带创作说明"]}',
    100
),
(
    'text_translation',
    '古文翻译',
    '将古文典籍翻译为现代文，让传统文化更易理解',
    'text',
    'heritage',
    'hard',
    '{"description":"将古文典籍翻译为现代中文","content_type":"text","requirements":["准确理解古文原意","保持原文韵味","语言流畅易懂","可适当添加注释"]}',
    150
),
(
    'folklore_adaptation',
    '民俗改编',
    '将传统民俗故事改编为现代形式',
    'text',
    'folklore',
    'medium',
    '{"description":"改编传统民俗故事为现代小说、剧本等形式","content_type":"text","requirements":["保留民俗文化核心","符合现代表达习惯","故事结构完整","具有传播价值"]}',
    120
);

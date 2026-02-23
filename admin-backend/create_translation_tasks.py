#!/usr/bin/env python3
"""
创建测试转译任务
"""

import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'lingzhi_ecosystem.db')

def create_test_tasks():
    """创建测试转译任务"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 获取项目ID
    projects = cursor.execute('SELECT id, project_code, base_reward FROM translation_projects').fetchall()

    tasks_created = 0

    for project_id, project_code, base_reward in projects:
        # 为每个项目创建3个测试任务
        for i in range(1, 4):
            task_code = f"{project_code}_task_{i}"

            if project_code == 'aesthetic_detective':
                title = f"西安美学侦探任务 {i}"
                description = f"拍摄西安古城墙的文化元素照片，展现历史美感"
                source_content = "西安古城墙是中国现存规模最大、保存最完整的古代城垣建筑，始建于明洪武年间。"
                source_type = 'text'
                target_type = 'text'
                translation_prompt = "请将这段关于西安古城墙的介绍转译为富有美感的现代文案，适合在社交媒体传播。"
            elif project_code == 'culture_creation':
                title = f"文化创作任务 {i}"
                description = f"基于传统文化元素创作现代艺术作品"
                source_content = "唐代长安是当时世界上最大的城市，人口超过100万，来自各国的商贾云集。"
                source_type = 'text'
                target_type = 'text'
                translation_prompt = "请将这段关于唐代长安的历史转译为一段生动的现代叙事，适合短视频脚本。"
            elif project_code == 'text_translation':
                title = f"古文翻译任务 {i}"
                description = f"翻译古文典籍为现代文"
                source_content = "学而时习之，不亦说乎？有朋自远方来，不亦乐乎？"
                source_type = 'text'
                target_type = 'text'
                translation_prompt = "请将这段《论语》中的经典语句翻译为现代汉语，并解释其深层含义。"
            else:  # folklore_adaptation
                title = f"民俗改编任务 {i}"
                description = f"改编传统民俗故事为现代形式"
                source_content = "相传牛郎织女被银河隔开，每年七月七日才能相会一次。"
                source_type = 'text'
                target_type = 'text'
                translation_prompt = "请将这个牛郎织女的传说改编为现代都市爱情故事的开篇。"

            # 检查任务是否已存在
            existing = cursor.execute(
                'SELECT id FROM translation_tasks WHERE task_code = ?',
                (task_code,)
            ).fetchone()

            if not existing:
                cursor.execute(
                    '''INSERT INTO translation_tasks
                       (project_id, task_code, title, description, source_content,
                        source_type, target_type, translation_prompt, status, reward)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (project_id, task_code, title, description, source_content,
                     source_type, target_type, translation_prompt, 'available', base_reward)
                )
                tasks_created += 1
                print(f"✅ 创建任务: {task_code}")
            else:
                print(f"⏭️  任务已存在: {task_code}")

    conn.commit()
    conn.close()

    print(f"\n🎉 共创建 {tasks_created} 个测试任务")

if __name__ == '__main__':
    create_test_tasks()

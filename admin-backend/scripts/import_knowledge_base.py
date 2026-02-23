#!/usr/bin/env python3
"""
批量导入知识库文档脚本
将原始资料批量导入到知识库系统中
"""

import sqlite3
import os
import sys
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect('./lingzhi_ecosystem.db')
    conn.row_factory = sqlite3.Row
    return conn

def read_file_content(file_path):
    """读取文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"读取文件 {file_path} 失败: {e}")
        return None

def get_file_title(file_path):
    """从文件路径提取标题"""
    filename = Path(file_path).stem
    # 转换文件名为友好的标题
    title_map = {
        '公司简介': '陕西媄月商业艺术有限责任公司简介',
        '西安文化关键词库': '西安文化关键词库（110个）',
        '西安文化基因库': '西安文化基因库',
        '灵值生态一体化服务总纲': '灵值生态一体化服务总纲',
        '灵值智能体v9.0-全面升级设计方案': '灵值智能体v9.0全面升级设计方案',
    }
    return title_map.get(filename, filename.replace('-', ' ').title())

def categorize_document(file_path):
    """根据文件路径分类文档"""
    if '公司' in file_path:
        return '公司信息'
    elif '西安' in file_path:
        return '西安文化'
    elif '灵值' in file_path or '生态' in file_path:
        return '灵值生态'
    elif '智能体' in file_path:
        return '智能体系统'
    else:
        return '通用'

def import_documents():
    """批量导入文档"""
    print("="*80)
    print("开始批量导入知识库文档")
    print("="*80)

    # 要导入的文档列表
    documents_to_import = [
        {
            'file_path': '../../assets/公司简介.md',
            'title': '陕西媄月商业艺术有限责任公司简介',
            'category': '公司信息',
            'description': '媄月公司的使命、愿景、核心架构与行动方向'
        },
        {
            'file_path': '../../assets/西安文化关键词库.md',
            'title': '西安文化关键词库（110个）',
            'category': '西安文化',
            'description': '110个西安文化关键词及转译提示，涵盖都城气象、盛唐意象、历史地标等'
        },
        {
            'file_path': '../../assets/西安文化基因库.md',
            'title': '西安文化基因库',
            'category': '西安文化',
            'description': '西安文化基因分类和解码方法'
        },
        {
            'file_path': '../../assets/灵值生态一体化服务总纲.md',
            'title': '灵值生态一体化服务总纲',
            'category': '灵值生态',
            'description': '生态全景、规则体系、贡献值体系的完整说明'
        },
        {
            'file_path': '../../assets/灵值智能体v9.0-全面升级设计方案.md',
            'title': '灵值智能体v9.0全面升级设计方案',
            'category': '智能体系统',
            'description': '智能体v9.0的升级内容、技术架构和功能特性'
        },
        {
            'file_path': '../../docs/灵值生态园完整体系梳理（最终版）.md',
            'title': '灵值生态园完整体系梳理',
            'category': '灵值生态',
            'description': '灵值生态园的完整功能模块和业务流程梳理'
        },
        {
            'file_path': '../../docs/灵值生态园-生态闭环完整战略规划.md',
            'title': '灵值生态园生态闭环完整战略规划',
            'category': '战略规划',
            'description': '生态闭环的战略规划和实施路径'
        },
        {
            'file_path': '../../docs/灵值生态园-完整生态闭环战略规划（最终融合版）.md',
            'title': '灵值生态园完整生态闭环战略规划（最终融合版）',
            'category': '战略规划',
            'description': '最终融合版的生态闭环战略规划'
        },
    ]

    conn = get_db_connection()
    cursor = conn.cursor()

    # 获取或创建知识库
    cursor.execute('SELECT id, name FROM knowledge_bases WHERE name = ?', ('灵值生态核心知识库',))
    kb = cursor.fetchone()

    if kb:
        kb_id = kb['id']
        print(f"\n找到现有知识库: {kb['name']} (ID: {kb_id})")
    else:
        # 创建新的知识库
        cursor.execute('''
            INSERT INTO knowledge_bases (name, description, created_at, updated_at)
            VALUES (?, ?, ?, ?)
        ''', ('灵值生态核心知识库', '灵值生态园的核心知识库，包含公司信息、文化资料、系统文档等', datetime.now().isoformat(), datetime.now().isoformat()))
        kb_id = cursor.lastrowid
        print(f"\n创建新知识库: 灵值生态核心知识库 (ID: {kb_id})")

    # 获取或创建分类
    categories = {}
    for doc in documents_to_import:
        category_name = doc['category']
        if category_name not in categories:
            cursor.execute('SELECT id FROM knowledge_categories WHERE name = ?', (category_name,))
            cat = cursor.fetchone()
            if cat:
                categories[category_name] = cat['id']
            else:
                # 生成分类code（使用拼音首字母）
                code_map = {
                    '公司信息': 'company',
                    '西安文化': 'xian_culture',
                    '灵值生态': 'lingzhi_ecosystem',
                    '智能体系统': 'agent_system',
                    '战略规划': 'strategy'
                }
                code = code_map.get(category_name, category_name.lower().replace(' ', '_'))

                cursor.execute('''
                    INSERT INTO knowledge_categories (name, code, description, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (category_name, code, f'{category_name}相关文档', datetime.now().isoformat()))
                categories[category_name] = cursor.lastrowid
                print(f"创建新分类: {category_name} (code: {code})")

    # 导入文档
    imported_count = 0
    skipped_count = 0
    error_count = 0

    for doc_info in documents_to_import:
        file_path = os.path.join(os.path.dirname(__file__), doc_info['file_path'])
        content = read_file_content(file_path)

        if not content:
            print(f"⚠️  跳过: {doc_info['title']} (无法读取文件)")
            skipped_count += 1
            continue

        # 检查文档是否已存在
        cursor.execute('SELECT id FROM knowledge_documents WHERE title = ? AND knowledge_base_id = ?',
                      (doc_info['title'], kb_id))
        existing = cursor.fetchone()

        if existing:
            print(f"⏭️  跳过: {doc_info['title']} (已存在)")
            skipped_count += 1
            continue

        # 插入新文档
        try:
            cursor.execute('''
                INSERT INTO knowledge_documents (
                    knowledge_base_id,
                    title,
                    content,
                    summary,
                    file_path,
                    file_type,
                    file_size,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                kb_id,
                doc_info['title'],
                content,
                doc_info['description'],
                file_path,
                'text/markdown',
                len(content),
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            imported_count += 1
            print(f"✓ 导入: {doc_info['title']} ({len(content)} 字符)")
        except Exception as e:
            print(f"✗ 错误: {doc_info['title']} - {e}")
            error_count += 1

    # 提交更改
    conn.commit()
    conn.close()

    print("\n" + "="*80)
    print("导入完成")
    print("="*80)
    print(f"✓ 成功导入: {imported_count} 个文档")
    print(f"⏭️  跳过: {skipped_count} 个文档")
    print(f"✗ 错误: {error_count} 个文档")
    print(f"\n知识库ID: {kb_id}")
    print("="*80)

if __name__ == '__main__':
    import_documents()

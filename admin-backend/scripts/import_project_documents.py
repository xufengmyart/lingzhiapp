#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目文档导入脚本
将项目文档导入到知识库中
"""

import sqlite3
import os
from datetime import datetime

# 数据库路径
DB_PATH = 'lingzhi_ecosystem.db'

# 知识库ID
KNOWLEDGE_BASE_ID = 7

# 项目文档列表
PROJECT_DOCUMENTS = [
    {
        'id': 23,
        'title': '西安美学侦探项目',
        'file_path': '../assets/项目文档-西安美学侦探.md',
        'file_type': 'text/markdown',
        'category': '项目管理'
    },
    {
        'id': 24,
        'title': '中视频项目',
        'file_path': '../assets/项目文档-中视频项目.md',
        'file_type': 'text/markdown',
        'category': '项目管理'
    },
    {
        'id': 25,
        'title': '赏金猎人项目',
        'file_path': '../assets/项目文档-赏金猎人项目.md',
        'file_type': 'text/markdown',
        'category': '项目管理'
    },
    {
        'id': 26,
        'title': '分红池项目',
        'file_path': '../assets/项目文档-分红池项目.md',
        'file_type': 'text/markdown',
        'category': '项目管理'
    },
    {
        'id': 27,
        'title': '商家资源池项目',
        'file_path': '../assets/项目文档-商家资源池.md',
        'file_type': 'text/markdown',
        'category': '项目管理'
    },
    {
        'id': 28,
        'title': '数字资产系统',
        'file_path': '../assets/项目文档-数字资产系统.md',
        'file_type': 'text/markdown',
        'category': '项目管理'
    },
    {
        'id': 29,
        'title': '圣地管理系统',
        'file_path': '../assets/项目文档-圣地管理系统.md',
        'file_type': 'text/markdown',
        'category': '项目管理'
    },
    {
        'id': 30,
        'title': '文化转译项目',
        'file_path': '../assets/项目文档-文化转译项目.md',
        'file_type': 'text/markdown',
        'category': '项目管理'
    },
    {
        'id': 31,
        'title': '用户旅程系统',
        'file_path': '../assets/项目文档-用户旅程系统.md',
        'file_type': 'text/markdown',
        'category': '项目管理'
    },
    {
        'id': 32,
        'title': '项目管理系统',
        'file_path': '../assets/项目文档-项目管理系统.md',
        'file_type': 'text/markdown',
        'category': '项目管理'
    }
]


def read_document_content(file_path):
    """读取文档内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        print(f"❌ 读取文档失败: {file_path}, 错误: {e}")
        return None


def generate_summary(content, max_length=200):
    """生成文档摘要"""
    if not content:
        return ""
    
    # 移除标题和空行
    lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
    
    if not lines:
        return ""
    
    # 取第一段作为摘要
    summary = lines[0]
    if len(summary) > max_length:
        summary = summary[:max_length] + "..."
    
    return summary


def import_documents():
    """导入文档到知识库"""
    
    print("="*60)
    print("项目文档导入脚本")
    print("="*60)
    
    # 连接数据库
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        print("✓ 数据库连接成功")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False
    
    # 检查知识库是否存在
    cursor.execute('SELECT id, name FROM knowledge_bases WHERE id = ?', (KNOWLEDGE_BASE_ID,))
    kb = cursor.fetchone()
    
    if not kb:
        print(f"❌ 知识库不存在: ID {KNOWLEDGE_BASE_ID}")
        conn.close()
        return False
    
    print(f"✓ 知识库: {kb[1]} (ID: {kb[0]})")
    
    # 导入文档
    imported_count = 0
    skipped_count = 0
    
    print("\n开始导入文档...")
    print("-"*60)
    
    for doc_info in PROJECT_DOCUMENTS:
        doc_id = doc_info['id']
        title = doc_info['title']
        file_path = doc_info['file_path']
        file_type = doc_info['file_type']
        
        # 检查文档是否已存在
        cursor.execute('SELECT id FROM knowledge_documents WHERE id = ?', (doc_id,))
        existing = cursor.fetchone()
        
        if existing:
            print(f"⏭️  跳过: {title} (已存在)")
            skipped_count += 1
            continue
        
        # 读取文档内容
        content = read_document_content(file_path)
        if not content:
            continue
        
        # 生成摘要
        summary = generate_summary(content)
        file_size = len(content)
        
        # 插入文档
        try:
            cursor.execute('''
                INSERT INTO knowledge_documents (
                    id, knowledge_base_id, title, content, summary, 
                    file_path, file_type, file_size, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                doc_id,
                KNOWLEDGE_BASE_ID,
                title,
                content,
                summary,
                file_path,
                file_type,
                file_size,
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            conn.commit()
            imported_count += 1
            print(f"✓ 导入: {title} ({file_size:,} 字符)")
        except Exception as e:
            print(f"❌ 导入失败: {title}, 错误: {e}")
    
    # 统计信息
    print("-"*60)
    print(f"\n导入完成:")
    print(f"  成功导入: {imported_count} 个文档")
    print(f"  跳过: {skipped_count} 个文档")
    
    # 查询知识库统计
    cursor.execute('''
        SELECT COUNT(*) FROM knowledge_documents WHERE knowledge_base_id = ?
    ''', (KNOWLEDGE_BASE_ID,))
    total_docs = cursor.fetchone()[0]
    
    print(f"\n知识库统计:")
    print(f"  文档总数: {total_docs}")
    
    conn.close()
    print("\n✓ 数据库连接已关闭")
    
    return True


if __name__ == '__main__':
    success = import_documents()
    
    if success:
        print("\n" + "="*60)
        print("✓ 项目文档导入成功！")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ 项目文档导入失败！")
        print("="*60)

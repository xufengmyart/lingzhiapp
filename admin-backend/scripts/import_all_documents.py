#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量导入所有核心文档到知识库
包括灵值生态核心档案、项目文档等
"""

import sqlite3
import os
import sys
from datetime import datetime
from pathlib import Path
import hashlib

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

def calculate_content_hash(content):
    """计算内容哈希"""
    if not content:
        return None
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def ensure_knowledge_base_exists(conn, name, description):
    """确保知识库存在，不存在则创建"""
    cursor = conn.cursor()
    
    # 检查是否已存在
    cursor.execute('SELECT id FROM knowledge_bases WHERE name = ?', (name,))
    existing = cursor.fetchone()
    
    if existing:
        print(f"  ✓ 知识库已存在: {name}")
        return existing[0]
    
    # 创建新知识库
    cursor.execute('''
        INSERT INTO knowledge_bases (name, description, created_at, updated_at)
        VALUES (?, ?, ?, ?)
    ''', (name, description, datetime.now().isoformat(), datetime.now().isoformat()))
    
    kb_id = cursor.lastrowid
    print(f"  ✓ 创建知识库: {name}")
    return kb_id

def import_document(conn, doc_data):
    """导入单个文档"""
    cursor = conn.cursor()
    
    file_path = doc_data['file_path']
    title = doc_data['title']
    category = doc_data['category']
    description = doc_data['description']
    kb_id = doc_data['kb_id']
    
    # 读取文件内容
    content = read_file_content(file_path)
    if not content:
        print(f"  ✗ 跳过（无法读取）: {title}")
        return False
    
    # 计算内容哈希
    content_hash = calculate_content_hash(content)
    
    # 检查是否已存在（通过内容哈希或标题）
    cursor.execute('''
        SELECT id FROM knowledge_documents 
        WHERE title = ? OR summary = ?
    ''', (title, content_hash))
    
    existing = cursor.fetchone()
    
    if existing:
        print(f"  ✓ 文档已存在: {title}")
        return True
    
    # 插入新文档（注意：使用实际表结构字段）
    cursor.execute('''
        INSERT INTO knowledge_documents (
            knowledge_base_id, title, content, summary, author,
            embedding_status, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        kb_id, title, content, content_hash, '系统导入',
        'pending', datetime.now().isoformat(), datetime.now().isoformat()
    ))
    
    print(f"  ✓ 导入文档: {title} ({len(content)} 字符)")
    return True

def main():
    """主函数"""
    print("=" * 80)
    print("开始批量导入所有核心文档到知识库")
    print("=" * 80)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 创建灵值生态核心知识库
        print("\n1. 创建知识库...")
        kb_id = ensure_knowledge_base_exists(
            conn,
            "灵值生态核心知识库",
            "包含灵值生态的核心价值体系、架构设计、运营规则与文化基因"
        )
        
        # 要导入的文档列表
        documents = [
            # 灵值生态核心档案
            {
                'file_path': '/workspace/projects/docs/灵值生态核心档案.md',
                'title': '灵值生态核心档案',
                'category': '灵值生态',
                'description': '灵值生态系统的核心知识库，整合了核心价值体系、架构设计、运营规则与文化基因',
                'kb_id': kb_id
            },
            # 体系梳理
            {
                'file_path': '/workspace/projects/docs/灵值生态园完整体系梳理（最终版）.md',
                'title': '灵值生态园完整体系梳理',
                'category': '灵值生态',
                'description': '灵值生态园的完整功能模块和业务流程梳理',
                'kb_id': kb_id
            },
            # 战略规划
            {
                'file_path': '/workspace/projects/docs/灵值生态园-生态闭环完整战略规划.md',
                'title': '灵值生态园生态闭环完整战略规划',
                'category': '战略规划',
                'description': '灵值生态园的生态闭环战略规划',
                'kb_id': kb_id
            },
            # 生态闭环战略规划（最终融合版）
            {
                'file_path': '/workspace/projects/docs/灵值生态园-完整生态闭环战略规划（最终融合版）.md',
                'title': '灵值生态园完整生态闭环战略规划（最终融合版）',
                'category': '战略规划',
                'description': '灵值生态园完整生态闭环战略规划最终融合版',
                'kb_id': kb_id
            },
            # 公司信息
            {
                'file_path': '/workspace/projects/assets/公司简介.md',
                'title': '陕西媄月商业艺术有限责任公司简介',
                'category': '公司信息',
                'description': '媄月公司的使命、愿景、核心架构与行动方向',
                'kb_id': kb_id
            },
            # 西安文化
            {
                'file_path': '/workspace/projects/assets/西安文化关键词库.md',
                'title': '西安文化关键词库（110个）',
                'category': '西安文化',
                'description': '110个西安文化关键词及转译提示，涵盖都城气象、盛唐意象、历史地标等',
                'kb_id': kb_id
            },
            {
                'file_path': '/workspace/projects/assets/西安文化基因库.md',
                'title': '西安文化基因库',
                'category': '西安文化',
                'description': '西安文化基因分类和解码方法',
                'kb_id': kb_id
            },
            # 服务总纲
            {
                'file_path': '/workspace/projects/assets/灵值生态一体化服务总纲.md',
                'title': '灵值生态一体化服务总纲',
                'category': '灵值生态',
                'description': '生态全景、规则体系、贡献值体系的完整说明',
                'kb_id': kb_id
            },
            # 智能体系统
            {
                'file_path': '/workspace/projects/docs/灵值智能体v9.0-全面升级完成报告.md',
                'title': '灵值智能体v9.0全面升级完成报告',
                'category': '智能体系统',
                'description': '智能体v9.0的升级内容、技术架构和功能特性',
                'kb_id': kb_id
            },
            {
                'file_path': '/workspace/projects/assets/灵值智能体v9.0-全面升级设计方案.md',
                'title': '灵值智能体v9.0全面升级设计方案',
                'category': '智能体系统',
                'description': '智能体v9.0的升级设计方案',
                'kb_id': kb_id
            },
            # 项目文档
            {
                'file_path': '/workspace/projects/assets/项目文档-西安美学侦探.md',
                'title': '项目文档：西安美学侦探',
                'category': '项目文档',
                'description': '西安美学侦探项目概述、参与方式、奖励机制',
                'kb_id': kb_id
            },
            {
                'file_path': '/workspace/projects/assets/项目文档-中视频项目.md',
                'title': '项目文档：中视频项目',
                'category': '项目文档',
                'description': '中视频项目概述、参与方式、奖励机制',
                'kb_id': kb_id
            },
            {
                'file_path': '/workspace/projects/assets/项目文档-赏金猎人项目.md',
                'title': '项目文档：赏金猎人项目',
                'category': '项目文档',
                'description': '赏金猎人项目概述、参与方式、奖励机制',
                'kb_id': kb_id
            },
            {
                'file_path': '/workspace/projects/assets/项目文档-分红池项目.md',
                'title': '项目文档：分红池项目',
                'category': '项目文档',
                'description': '分红池项目概述、参与方式、奖励机制',
                'kb_id': kb_id
            },
            {
                'file_path': '/workspace/projects/assets/项目文档-商家资源池.md',
                'title': '项目文档：商家资源池',
                'category': '项目文档',
                'description': '商家资源池项目概述、参与方式、奖励机制',
                'kb_id': kb_id
            },
            {
                'file_path': '/workspace/projects/assets/项目文档-数字资产系统.md',
                'title': '项目文档：数字资产系统',
                'category': '项目文档',
                'description': '数字资产系统项目概述、参与方式、奖励机制',
                'kb_id': kb_id
            },
            {
                'file_path': '/workspace/projects/assets/项目文档-圣地管理系统.md',
                'title': '项目文档：圣地管理系统',
                'category': '项目文档',
                'description': '圣地管理系统项目概述、参与方式、奖励机制',
                'kb_id': kb_id
            },
            {
                'file_path': '/workspace/projects/assets/项目文档-文化转译项目.md',
                'title': '项目文档：文化转译项目',
                'category': '项目文档',
                'description': '文化转译项目概述、参与方式、奖励机制',
                'kb_id': kb_id
            },
            {
                'file_path': '/workspace/projects/assets/项目文档-用户旅程系统.md',
                'title': '项目文档：用户旅程系统',
                'category': '项目文档',
                'description': '用户旅程系统项目概述、参与方式、奖励机制',
                'kb_id': kb_id
            },
            {
                'file_path': '/workspace/projects/assets/项目文档-项目管理系统.md',
                'title': '项目文档：项目管理系统',
                'category': '项目文档',
                'description': '项目管理系统项目概述、参与方式、奖励机制',
                'kb_id': kb_id
            },
        ]
        
        # 导入文档
        print("\n2. 导入文档...")
        success_count = 0
        skip_count = 0
        total_chars = 0
        
        for doc in documents:
            if import_document(conn, doc):
                file_path = doc['file_path']
                content = read_file_content(file_path)
                if content:
                    total_chars += len(content)
                success_count += 1
            else:
                skip_count += 1
        
        # 关联智能体
        print("\n3. 关联智能体...")
        
        # 查找智能体
        cursor.execute('SELECT id, name FROM agents')
        agents = cursor.fetchall()
        
        for agent in agents:
            agent_id, agent_name = agent
            
            # 检查是否已关联（注意表结构是 knowledge_base_id 而不是 kb_id）
            cursor.execute('''
                SELECT agent_id FROM agent_knowledge_bases 
                WHERE agent_id = ? AND knowledge_base_id = ?
            ''', (agent_id, kb_id))
            
            existing = cursor.fetchone()
            
            if not existing:
                cursor.execute('''
                    INSERT INTO agent_knowledge_bases (agent_id, knowledge_base_id, created_at)
                    VALUES (?, ?, ?)
                ''', (agent_id, kb_id, datetime.now().isoformat()))
                
                print(f"  ✓ 关联智能体: {agent_name}")
            else:
                print(f"  ✓ 智能体已关联: {agent_name}")
        
        # 提交事务
        conn.commit()
        
        # 显示统计
        print("\n" + "=" * 80)
        print("导入完成")
        print("=" * 80)
        print(f"成功导入: {success_count} 个文档")
        print(f"跳过: {skip_count} 个文档（已存在）")
        print(f"总字符数: {total_chars:,}")
        print(f"知识库ID: {kb_id}")
        
        # 查询知识库统计
        cursor.execute('''
            SELECT COUNT(*) as total, 
                   SUM(LENGTH(content)) as total_chars
            FROM knowledge_documents
            WHERE knowledge_base_id = ?
        ''', (kb_id,))
        
        stats = cursor.fetchone()
        print(f"知识库文档总数: {stats['total']}")
        print(f"知识库总字符数: {stats['total_chars']:,}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ 导入失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    success = main()
    
    print("\n" + "=" * 80)
    if success:
        print("✓ 所有文档导入成功！")
    else:
        print("✗ 导入失败")
    print("=" * 80)

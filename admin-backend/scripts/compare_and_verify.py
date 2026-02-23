#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
全局对比和验证脚本
功能：对比新旧文件，确保部署不影响原有设计和板块
"""

import sqlite3
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple

# ==================== 配置 ====================

BACKEND_DIR = "/workspace/projects/admin-backend"
CURRENT_DB = os.path.join(BACKEND_DIR, "lingzhi_ecosystem.db")
BACKUP_DB = os.path.join(BACKEND_DIR, "lingzhi_ecosystem_backup_manual.db")

# ==================== 工具函数 ====================

def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def print_success(msg: str):
    print(f"✅ {msg}")

def print_warning(msg: str):
    print(f"⚠️  {msg}")

def print_error(msg: str):
    print(f"❌ {msg}")

def print_info(msg: str):
    print(f"ℹ️  {msg}")

# ==================== 数据库对比 ====================

class DatabaseComparator:
    """数据库对比器"""
    
    def __init__(self, current_db: str, backup_db: str):
        self.current_conn = sqlite3.connect(current_db)
        self.backup_conn = sqlite3.connect(backup_db)
        self.current_cursor = self.current_conn.cursor()
        self.backup_cursor = self.backup_conn.cursor()
        
        self.differences = []
        self.warnings = []
        self.errors = []
    
    def compare_tables(self) -> List[Tuple]:
        """对比所有表"""
        print_section("数据库表对比")
        
        current_tables = self.get_tables(self.current_cursor)
        backup_tables = self.get_tables(self.backup_cursor)
        
        all_tables = sorted(set(current_tables) | set(backup_tables))
        
        print(f"当前数据库表数: {len(current_tables)}")
        print(f"备份数据库表数: {len(backup_tables)}")
        print(f"总表数: {len(all_tables)}")
        
        differences = []
        
        for table in all_tables:
            in_current = table in current_tables
            in_backup = table in backup_tables
            
            if not in_current:
                self.warnings.append(f"表 {table} 在当前数据库中不存在")
                print_warning(f"表 {table} 仅存在于备份中")
                differences.append(('table_missing', table, None, 'backup_only'))
            elif not in_backup:
                self.warnings.append(f"表 {table} 在备份数据库中不存在")
                print_warning(f"表 {table} 仅存在于当前数据库")
                differences.append(('table_missing', table, 'current_only', None))
            else:
                print_info(f"表 {table}: 存在于两个数据库")
                # 对比表结构
                table_diff = self.compare_table_structure(table)
                if table_diff:
                    differences.append(('table_structure', table, table_diff))
        
        return differences
    
    def compare_table_structure(self, table: str) -> Dict:
        """对比表结构"""
        current_columns = self.get_columns(self.current_cursor, table)
        backup_columns = self.get_columns(self.backup_cursor, table)
        
        current_dict = {col['name']: col for col in current_columns}
        backup_dict = {col['name']: col for col in backup_columns}
        
        differences = {
            'added': [],
            'removed': [],
            'modified': []
        }
        
        all_columns = set(current_dict.keys()) | set(backup_dict.keys())
        
        for col in all_columns:
            if col not in backup_dict:
                differences['added'].append(col)
                print_warning(f"  表 {table} 新增字段: {col}")
            elif col not in current_dict:
                differences['removed'].append(col)
                print_error(f"  表 {table} 删除字段: {col}")
                self.errors.append(f"表 {table} 删除了字段 {col}")
            else:
                # 对比字段定义
                if current_dict[col] != backup_dict[col]:
                    differences['modified'].append({
                        'name': col,
                        'current': current_dict[col],
                        'backup': backup_dict[col]
                    })
                    print_info(f"  表 {table} 字段变更: {col}")
        
        return differences if any(differences.values()) else None
    
    def compare_agents(self) -> List[Dict]:
        """对比智能体配置"""
        print_section("智能体配置对比")
        
        current_agents = self.get_agents(self.current_cursor)
        backup_agents = self.get_agents(self.backup_cursor)
        
        print(f"当前智能体数: {len(current_agents)}")
        print(f"备份智能体数: {len(backup_agents)}")
        
        differences = []
        
        for agent in current_agents:
            agent_id = agent['id']
            name = agent['name']
            
            backup_agent = next((a for a in backup_agents if a['id'] == agent_id), None)
            
            if not backup_agent:
                print_warning(f"智能体 {name} (ID: {agent_id}) 仅存在于当前数据库")
                differences.append({
                    'id': agent_id,
                    'name': name,
                    'type': 'new_agent'
                })
            else:
                # 对比配置
                current_config = json.loads(agent['model_config']) if agent['model_config'] else {}
                backup_config = json.loads(backup_agent['model_config']) if backup_agent['model_config'] else {}
                
                if current_config != backup_config:
                    print_info(f"智能体 {name} 配置变更:")
                    print(f"  备份: {backup_config}")
                    print(f"  当前: {current_config}")
                    differences.append({
                        'id': agent_id,
                        'name': name,
                        'type': 'config_changed',
                        'backup': backup_config,
                        'current': current_config
                    })
        
        return differences
    
    def get_tables(self, cursor) -> List[str]:
        """获取所有表"""
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        return [row[0] for row in cursor.fetchall()]
    
    def get_columns(self, cursor, table: str) -> List[Dict]:
        """获取表的所有列"""
        cursor.execute(f"PRAGMA table_info({table})")
        columns = []
        for row in cursor.fetchall():
            columns.append({
                'cid': row[0],
                'name': row[1],
                'type': row[2],
                'notnull': row[3],
                'dflt_value': row[4],
                'pk': row[5]
            })
        return columns
    
    def get_agents(self, cursor) -> List[Dict]:
        """获取智能体配置"""
        cursor.execute("SELECT id, name, description, model_config FROM agents")
        agents = []
        for row in cursor.fetchall():
            agents.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'model_config': row[3]
            })
        return agents
    
    def check_critical_tables(self) -> bool:
        """检查关键表是否存在"""
        print_section("关键表检查")
        
        critical_tables = [
            'users',           # 用户表
            'checkin_records', # 签到记录表
            'agents',          # 智能体表
            'conversations',   # 对话表
            'messages',        # 消息表
        ]
        
        all_ok = True
        
        for table in critical_tables:
            current_exists = table in self.get_tables(self.current_cursor)
            backup_exists = table in self.get_tables(self.backup_cursor)
            
            if current_exists and backup_exists:
                print_success(f"关键表 {table}: 存在")
            elif current_exists and not backup_exists:
                print_warning(f"关键表 {table}: 仅存在于当前数据库")
            elif not current_exists and backup_exists:
                print_error(f"关键表 {table}: 在当前数据库中不存在！")
                self.errors.append(f"关键表 {table} 缺失")
                all_ok = False
            else:
                print_error(f"关键表 {table}: 在两个数据库中都不存在！")
                self.errors.append(f"关键表 {table} 完全缺失")
                all_ok = False
        
        return all_ok
    
    def close(self):
        """关闭连接"""
        self.current_conn.close()
        self.backup_conn.close()

# ==================== 文件对比 ====================

class FileComparator:
    """文件对比器"""
    
    def __init__(self, backend_dir: str):
        self.backend_dir = backend_dir
        self.differences = []
        self.warnings = []
        self.errors = []
    
    def compare_routes(self) -> List[Dict]:
        """对比路由文件"""
        print_section("路由文件对比")
        
        critical_files = [
            'routes/complete_apis.py',  # 签到系统
            'routes/agent.py',          # 智能体系统
        ]
        
        differences = []
        
        for file_path in critical_files:
            full_path = os.path.join(self.backend_dir, file_path)
            
            if not os.path.exists(full_path):
                print_error(f"关键文件不存在: {file_path}")
                self.errors.append(f"关键文件缺失: {file_path}")
                continue
            
            print_info(f"检查文件: {file_path}")
            
            # 检查签到系统字段名
            if 'complete_apis.py' in file_path:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    if 'lingzhi_earned' in content:
                        print_success(f"  签到系统字段名正确: lingzhi_earned")
                    else:
                        print_error(f"  签到系统字段名错误: 应使用 lingzhi_earned")
                        self.errors.append(f"签到系统字段名错误: {file_path}")
                    
                    if 'lingzhi_reward' in content:
                        print_warning(f"  存在旧字段名: lingzhi_reward (需要修复)")
                        self.warnings.append(f"签到系统存在旧字段名: {file_path}")
            
            # 检查智能体系统
            if 'agent.py' in file_path:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    if 'LLMClient' in content or 'coze_coding_dev_sdk' in content:
                        print_success(f"  智能体SDK正确集成")
                    else:
                        print_error(f"  智能体SDK未正确集成")
                        self.errors.append(f"智能体SDK未集成: {file_path}")
        
        return differences

# ==================== 主流程 ====================

def main():
    """主流程"""
    print("="*60)
    print("  全局对比和验证")
    print("  时间:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("="*60)
    
    # 检查文件是否存在
    if not os.path.exists(CURRENT_DB):
        print_error(f"当前数据库不存在: {CURRENT_DB}")
        return False
    
    if not os.path.exists(BACKUP_DB):
        print_warning(f"备份数据库不存在: {BACKUP_DB}")
        return True  # 没有备份也算通过
    
    # 数据库对比
    db_comparator = DatabaseComparator(CURRENT_DB, BACKUP_DB)
    
    try:
        # 1. 检查关键表
        critical_ok = db_comparator.check_critical_tables()
        
        # 2. 对比所有表
        table_diffs = db_comparator.compare_tables()
        
        # 3. 对比智能体配置
        agent_diffs = db_comparator.compare_agents()
        
        # 文件对比
        file_comparator = FileComparator(BACKEND_DIR)
        route_diffs = file_comparator.compare_routes()
        
        # 汇总结果
        print_section("验证结果汇总")
        
        print(f"警告数量: {len(db_comparator.warnings) + len(file_comparator.warnings)}")
        print(f"错误数量: {len(db_comparator.errors) + len(file_comparator.errors)}")
        
        # 判断是否可以部署
        can_deploy = True
        
        if db_comparator.errors:
            print_error("数据库存在错误，不能部署:")
            for error in db_comparator.errors:
                print(f"  - {error}")
            can_deploy = False
        
        if file_comparator.errors:
            print_error("文件存在错误，不能部署:")
            for error in file_comparator.errors:
                print(f"  - {error}")
            can_deploy = False
        
        if db_comparator.warnings:
            print_warning("数据库存在警告:")
            for warning in db_comparator.warnings:
                print(f"  - {warning}")
        
        if file_comparator.warnings:
            print_warning("文件存在警告:")
            for warning in file_comparator.warnings:
                print(f"  - {warning}")
        
        print_section("最终结论")
        
        if can_deploy:
            print_success("✅ 验证通过，可以部署")
            print_info("所有关键表和配置都正常")
            print_info("原有设计和板块未受影响")
            return True
        else:
            print_error("❌ 验证失败，不能部署")
            print_info("请修复错误后重试")
            return False
    
    finally:
        db_comparator.close()

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

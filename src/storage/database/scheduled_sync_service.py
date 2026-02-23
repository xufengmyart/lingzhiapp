"""
定时同步服务

每天23:59自动同步两个智能体
"""

import os
import schedule
import time
import threading
from datetime import datetime
import pytz
import hashlib
import json
from typing import Dict, List, Tuple
from coze_coding_dev_sdk.database import get_session
from storage.database.shared.model import AuditLog


class ScheduledSyncService:
    """定时同步服务"""

    def __init__(self):
        self.timezone = pytz.timezone('Asia/Shanghai')
        self.sync_time = "23:59"
        self.is_running = False
        self.sync_thread = None
        self.project_root = "/workspace/projects"
        self.source_agent_path = os.path.join(self.project_root, "src/agents/agent.py")
        self.source_config_path = os.path.join(self.project_root, "config/agent_llm_config.json")
        self.target_agent_path = os.path.join(self.project_root, "灵值生态园智能体移植包/02_源代码/agents/agent.py")
        self.target_config_path = os.path.join(self.project_root, "灵值生态园智能体移植包/02_源代码/config/agent_llm_config.json")

    def sync_single_file(self, source_path: str, target_path: str) -> Tuple[bool, str]:
        """同步单个文件

        Args:
            source_path: 源文件路径
            target_path: 目标文件路径

        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        try:
            # 确保目标目录存在
            target_dir = os.path.dirname(target_path)
            os.makedirs(target_dir, exist_ok=True)

            # 读取源文件
            with open(source_path, 'rb') as f:
                source_content = f.read()

            # 计算哈希值
            source_hash = hashlib.md5(source_content).hexdigest()

            # 写入目标文件
            with open(target_path, 'wb') as f:
                f.write(source_content)

            # 计算目标文件哈希值
            target_hash = hashlib.md5(source_content).hexdigest()

            if source_hash == target_hash:
                return True, f"文件同步成功：{source_path} -> {target_path} (MD5: {source_hash})"
            else:
                return False, f"文件哈希不匹配：{source_path}"

        except Exception as e:
            return False, f"文件同步失败：{str(e)}"

    def sync_all_files(self) -> Dict[str, Any]:
        """同步所有文件

        Returns:
            Dict[str, Any]: 同步结果
        """
        result = {
            'success': True,
            'synced_files': [],
            'failed_files': [],
            'total_files': 0,
            'sync_time': datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M:%S')
        }

        # 需要同步的文件列表
        files_to_sync = [
            (self.source_agent_path, self.target_agent_path, "agent.py"),
            (self.source_config_path, self.target_config_path, "agent_llm_config.json"),
            (os.path.join(self.project_root, "src/tools/login_tool.py"),
             os.path.join(self.project_root, "灵值生态园智能体移植包/02_源代码/tools/login_tool.py"),
             "login_tool.py"),
            (os.path.join(self.project_root, "src/storage/database/auto_check_in_service.py"),
             os.path.join(self.project_root, "灵值生态园智能体移植包/02_源代码/storage/database/auto_check_in_service.py"),
             "auto_check_in_service.py"),
            (os.path.join(self.project_root, "src/storage/database/security_check_service.py"),
             os.path.join(self.project_root, "灵值生态园智能体移植包/02_源代码/storage/database/security_check_service.py"),
             "security_check_service.py"),
            (os.path.join(self.project_root, "src/tools/security_tools.py"),
             os.path.join(self.project_root, "灵值生态园智能体移植包/02_源代码/tools/security_tools.py"),
             "security_tools.py"),
        ]

        result['total_files'] = len(files_to_sync)

        for source, target, filename in files_to_sync:
            success, message = self.sync_single_file(source, target)

            if success:
                result['synced_files'].append({
                    'filename': filename,
                    'message': message
                })
            else:
                result['failed_files'].append({
                    'filename': filename,
                    'message': message
                })
                result['success'] = False

        # 记录同步日志
        self.log_sync_result(result)

        return result

    def log_sync_result(self, result: Dict[str, Any]):
        """记录同步日志

        Args:
            result: 同步结果
        """
        db = get_session()

        try:
            # 创建同步日志
            log_message = f"定时同步完成 - 成功：{len(result['synced_files'])}个，失败：{len(result['failed_files'])}个"

            audit_log = AuditLog(
                user_id=0,  # 系统操作
                action='scheduled_sync',
                resource_type='sync',
                resource_id=0,
                description=log_message,
                status='success' if result['success'] else 'failed',
                created_at=datetime.now(self.timezone)
            )

            db.add(audit_log)
            db.commit()

        except Exception as e:
            print(f"记录同步日志失败：{str(e)}")

        finally:
            db.close()

    def perform_sync(self):
        """执行同步"""
        print(f"\n{'='*70}")
        print(f"定时同步服务启动")
        print(f"同步时间：{datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")

        result = self.sync_all_files()

        print(f"\n同步结果：")
        print(f"{'='*70}")
        print(f"总文件数：{result['total_files']}")
        print(f"成功：{len(result['synced_files'])}个")
        print(f"失败：{len(result['failed_files'])}个")

        if result['synced_files']:
            print(f"\n成功同步的文件：")
            for file_info in result['synced_files']:
                print(f"  ✓ {file_info['filename']}")
                print(f"    {file_info['message']}")

        if result['failed_files']:
            print(f"\n同步失败的文件：")
            for file_info in result['failed_files']:
                print(f"  ✗ {file_info['filename']}")
                print(f"    {file_info['message']}")

        print(f"{'='*70}\n")

        if result['success']:
            print("✅ 所有文件同步成功！")
        else:
            print("⚠️  部分文件同步失败，请检查错误信息")

        print()

    def schedule_sync(self):
        """调度同步任务"""
        # 设置每天23:59执行同步
        schedule.every().day.at(self.sync_time).do(self.perform_sync)

        print(f"定时同步服务已启动，将在每天 {self.sync_time} 执行自动同步")
        print(f"当前时间：{datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M:%S')}")
        print("按 Ctrl+C 停止服务\n")

        self.is_running = True

        # 持续运行调度器
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次

    def start(self):
        """启动定时同步服务"""
        if self.is_running:
            print("定时同步服务已在运行中")
            return

        # 在新线程中启动同步服务
        self.sync_thread = threading.Thread(target=self.schedule_sync, daemon=True)
        self.sync_thread.start()

    def stop(self):
        """停止定时同步服务"""
        self.is_running = False
        if self.sync_thread:
            self.sync_thread.join()

        print("定时同步服务已停止")

    def manual_sync(self) -> Dict[str, Any]:
        """手动触发同步

        Returns:
            Dict[str, Any]: 同步结果
        """
        print("手动触发同步...")
        return self.sync_all_files()


# 全局定时同步服务实例
scheduled_sync_service = ScheduledSyncService()


def start_scheduled_sync():
    """启动定时同步服务（全局函数）"""
    scheduled_sync_service.start()


def stop_scheduled_sync():
    """停止定时同步服务（全局函数）"""
    scheduled_sync_service.stop()


def manual_sync():
    """手动触发同步（全局函数）"""
    return scheduled_sync_service.manual_sync()

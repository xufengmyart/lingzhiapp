#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
统一管理所有配置，通过环境变量动态配置，支持开发和生产环境
"""

import os
from dotenv import load_dotenv
from typing import Optional


class Config:
    """配置管理类"""

    def __init__(self, env_file: Optional[str] = None):
        """初始化配置

        Args:
            env_file: .env 文件路径，默认为 admin-backend/.env
        """
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()

        # 数据库配置
        self.DATABASE_PATH = os.getenv('DATABASE_PATH', './data/lingzhi_ecosystem.db')
        self.OLD_DATABASE = os.getenv('OLD_DATABASE', '../../灵值生态园智能体移植包/src/auth/auth.db')

        # 服务器配置
        self.HOST = os.getenv('HOST', '0.0.0.0')
        self.PORT = int(os.getenv('PORT', 8080))
        self.DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

        # JWT 配置
        self.JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'meiyueart-default-secret-key')
        self.JWT_EXPIRATION = int(os.getenv('JWT_EXPIRATION', 86400))  # 24小时

        # 微信配置
        self.WECHAT_APP_ID = os.getenv('WECHAT_APP_ID', '')
        self.WECHAT_APP_SECRET = os.getenv('WECHAT_APP_SECRET', '')
        self.WECHAT_REDIRECT_URI = os.getenv('WECHAT_REDIRECT_URI', '')
        # 微信开放平台配置（用于网页扫码登录）
        self.WECHAT_OPEN_PLATFORM_APPID = os.getenv('WECHAT_OPEN_PLATFORM_APPID', '')
        self.WECHAT_OPEN_PLATFORM_APPSECRET = os.getenv('WECHAT_OPEN_PLATFORM_APPSECRET', '')

        # LLM 配置
        self.LLM_API_KEY = os.getenv('COZE_WORKLOAD_IDENTITY_API_KEY', '')
        self.LLM_BASE_URL = os.getenv('COZE_INTEGRATION_MODEL_BASE_URL', '')
        self.LLM_MODEL = os.getenv('LLM_MODEL', 'doubao-seed-1-6-251015')

        # 日志配置
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_FILE = os.getenv('LOG_FILE', '/var/log/meiyueart-backend/app.log')

        # API 配置
        self.API_PREFIX = '/api'
        self.API_VERSION = os.getenv('API_VERSION', 'v1')

        # 安全配置
        self.BCRYPT_ROUNDS = int(os.getenv('BCRYPT_ROUNDS', 12))
        self.MAX_LOGIN_ATTEMPTS = int(os.getenv('MAX_LOGIN_ATTEMPTS', 5))
        self.LOGIN_LOCKOUT_TIME = int(os.getenv('LOGIN_LOCKOUT_TIME', 300))  # 5分钟

        # 文件上传配置
        self.MAX_UPLOAD_SIZE = int(os.getenv('MAX_UPLOAD_SIZE', 16 * 1024 * 1024))  # 16MB
        self.UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', './uploads')

        # 备份配置
        self.BACKUP_FOLDER = os.path.join(os.path.dirname(self.DATABASE_PATH), 'backups')
        self.MAX_BACKUP_COUNT = int(os.getenv('MAX_BACKUP_COUNT', 7))

        # 验证配置
        self._validate_config()

    def _validate_config(self):
        """验证配置的有效性"""
        # 验证数据库路径
        db_dir = os.path.dirname(self.DATABASE_PATH)
        if not os.path.exists(db_dir):
            print(f"⚠️  警告: 数据库目录不存在，将自动创建: {db_dir}")
            os.makedirs(db_dir, exist_ok=True)

        # 验证日志目录
        log_dir = os.path.dirname(self.LOG_FILE)
        if log_dir and not os.path.exists(log_dir):
            print(f"⚠️  警告: 日志目录不存在，将自动创建: {log_dir}")
            os.makedirs(log_dir, exist_ok=True)

        # 验证上传目录
        if not os.path.exists(self.UPLOAD_FOLDER):
            print(f"⚠️  警告: 上传目录不存在，将自动创建: {self.UPLOAD_FOLDER}")
            os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)

        # 验证备份目录
        if not os.path.exists(self.BACKUP_FOLDER):
            print(f"⚠️  警告: 备份目录不存在，将自动创建: {self.BACKUP_FOLDER}")
            os.makedirs(self.BACKUP_FOLDER, exist_ok=True)

    def get_database_url(self) -> str:
        """获取数据库连接 URL"""
        return f"sqlite:///{self.DATABASE_PATH}"

    def is_production(self) -> bool:
        """判断是否为生产环境"""
        return not self.DEBUG

    def is_development(self) -> bool:
        """判断是否为开发环境"""
        return self.DEBUG

    def print_config(self):
        """打印配置信息（隐藏敏感信息）"""
        print("=" * 60)
        print("系统配置信息")
        print("=" * 60)
        print(f"数据库路径: {self.DATABASE_PATH}")
        print(f"服务器地址: {self.HOST}:{self.PORT}")
        print(f"调试模式: {self.DEBUG}")
        print(f"JWT 过期时间: {self.JWT_EXPIPTION} 秒")
        print(f"日志级别: {self.LOG_LEVEL}")
        print(f"日志文件: {self.LOG_FILE}")
        print(f"最大上传大小: {self.MAX_UPLOAD_SIZE / 1024 / 1024} MB")
        print(f"最大备份数: {self.MAX_BACKUP_COUNT}")
        print(f"LLM 模型: {self.LLM_MODEL}")
        print("=" * 60)


# 全局配置实例
config = Config()

# 在模块导入时打印配置
if __name__ != '__main__':
    print(f"✅ 配置加载成功: {config.DATABASE_PATH}")

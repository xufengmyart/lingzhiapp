#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵值生态园 - 日志工具
Logging Utilities

Author: Coze Coding
Version: 1.0.0
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


def setup_logger(name='app', log_dir='logs', level=logging.INFO):
    """
    设置日志记录器

    Args:
        name: 记录器名称
        log_dir: 日志目录
        level: 日志级别

    Returns:
        logging.Logger: 配置好的记录器
    """
    # 创建日志目录
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # 创建记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 避免重复添加处理器
    if logger.handlers:
        return logger

    # 日志格式
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] '
        '[%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 文件处理器 - 按天轮转
    date_file_handler = TimedRotatingFileHandler(
        log_path / f'{name}_daily.log',
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    date_file_handler.suffix = '%Y-%m-%d'
    date_file_handler.setFormatter(formatter)
    date_file_handler.setLevel(level)

    # 文件处理器 - 按大小轮转
    rotating_file_handler = RotatingFileHandler(
        log_path / f'{name}.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    rotating_file_handler.setFormatter(formatter)
    rotating_file_handler.setLevel(level)

    # 错误日志处理器
    error_handler = RotatingFileHandler(
        log_path / f'{name}_error.log',
        maxBytes=10 * 1024 * 1024,
        backupCount=10,
        encoding='utf-8'
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)

    # 添加处理器
    logger.addHandler(date_file_handler)
    logger.addHandler(rotating_file_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)

    return logger


def get_logger(name):
    """
    获取日志记录器

    Args:
        name: 记录器名称

    Returns:
        logging.Logger: 记录器实例
    """
    return logging.getLogger(name)


class LoggerMixin:
    """日志记录器混入类"""

    @property
    def logger(self):
        """获取类日志记录器"""
        if not hasattr(self, '_logger'):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger


def log_function_call(func):
    """
    函数调用日志装饰器

    Args:
        func: 被装饰的函数

    Returns:
        包装后的函数
    """
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f'Calling {func.__name__} with args={args}, kwargs={kwargs}')

        try:
            result = func(*args, **kwargs)
            logger.debug(f'{func.__name__} returned {result}')
            return result
        except Exception as e:
            logger.error(f'{func.__name__} raised {type(e).__name__}: {e}')
            raise

    return wrapper


def log_execution_time(func):
    """
    执行时间日志装饰器

    Args:
        func: 被装饰的函数

    Returns:
        包装后的函数
    """
    import time

    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f'{func.__name__} executed in {execution_time:.2f}s')
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f'{func.__name__} failed after {execution_time:.2f}s: {e}')
            raise

    return wrapper

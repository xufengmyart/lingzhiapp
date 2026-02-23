"""
请求日志中间件
Request Logger Middleware

记录所有 API 请求和响应
"""

import time
import logging
from flask import request, g
from functools import wraps

logger = logging.getLogger(__name__)


class RequestLogger:
    """请求日志记录器"""

    @staticmethod
    def before_request():
        """请求前处理"""
        g.start_time = time.time()

        # 记录请求信息
        logger.info(
            f"📥 {request.method} {request.path} | "
            f"Remote: {request.remote_addr} | "
            f"User-Agent: {request.headers.get('User-Agent', 'Unknown')[:100]}"
        )

    @staticmethod
    def after_request(response):
        """请求后处理"""
        # 计算处理时间
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
        else:
            duration = 0

        # 记录响应信息
        status_emoji = "✅" if 200 <= response.status_code < 300 else \
                      "⚠️" if 300 <= response.status_code < 400 else \
                      "❌" if 400 <= response.status_code < 500 else \
                      "🔥"

        # 安全地获取响应大小（避免direct passthrough模式出错）
        try:
            size = len(response.get_data())
        except (RuntimeError, TypeError):
            size = 0

        logger.info(
            f"{status_emoji} {request.method} {request.path} | "
            f"Status: {response.status_code} | "
            f"Duration: {duration:.3f}s | "
            f"Size: {size} bytes"
        )

        # 添加响应头
        response.headers['X-Response-Time'] = f"{duration:.3f}s"
        response.headers['X-Request-ID'] = getattr(g, 'request_id', 'unknown')

        return response

    @staticmethod
    def teardown_request(exception):
        """请求清理"""
        if exception:
            logger.error(
                f"Request failed: {request.path} | "
                f"Error: {str(exception)}"
            )


def setup_request_logging(app):
    """设置请求日志"""

    # 注册请求处理函数
    app.before_request(RequestLogger.before_request)
    app.after_request(RequestLogger.after_request)
    app.teardown_request(RequestLogger.teardown_request)

    logger.info("✅ 请求日志中间件已注册")


def log_function_call(func):
    """函数调用日志装饰器"""

    @wraps(func)
    def decorated_function(*args, **kwargs):
        func_name = func.__name__
        logger.debug(f"🔧 Calling {func_name}")

        try:
            result = func(*args, **kwargs)
            logger.debug(f"✅ {func_name} completed successfully")
            return result
        except Exception as e:
            logger.error(f"❌ {func_name} failed: {str(e)}")
            raise

    return decorated_function

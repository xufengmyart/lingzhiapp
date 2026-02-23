"""
错误处理中间件
Error Handler Middleware

统一处理应用中的异常，返回标准化的错误响应
"""

from flask import jsonify, request
from functools import wraps
import traceback
import logging

logger = logging.getLogger(__name__)


class APIError(Exception):
    """API 异常基类"""

    def __init__(self, message, status_code=400, error_code=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or 'API_ERROR'


class ValidationError(APIError):
    """验证错误"""

    def __init__(self, message, errors=None):
        super().__init__(message, 400, 'VALIDATION_ERROR')
        self.errors = errors


class NotFoundError(APIError):
    """资源未找到错误"""

    def __init__(self, message='资源未找到'):
        super().__init__(message, 404, 'NOT_FOUND')


class UnauthorizedError(APIError):
    """未授权错误"""

    def __init__(self, message='未授权访问'):
        super().__init__(message, 401, 'UNAUTHORIZED')


class ForbiddenError(APIError):
    """禁止访问错误"""

    def __init__(self, message='禁止访问'):
        super().__init__(message, 403, 'FORBIDDEN')


class ConflictError(APIError):
    """冲突错误"""

    def __init__(self, message='资源冲突'):
        super().__init__(message, 409, 'CONFLICT')


class TooManyRequestsError(APIError):
    """请求过多错误"""

    def __init__(self, message='请求过于频繁，请稍后再试'):
        super().__init__(message, 429, 'TOO_MANY_REQUESTS')


class InternalServerError(APIError):
    """服务器内部错误"""

    def __init__(self, message='服务器内部错误'):
        super().__init__(message, 500, 'INTERNAL_SERVER_ERROR')


def register_error_handlers(app):
    """注册错误处理器"""

    @app.errorhandler(APIError)
    def handle_api_error(error):
        """处理 API 异常"""
        logger.warning(
            f"API Error: {error.error_code} - {error.message} | "
            f"Path: {request.path} | Method: {request.method}"
        )

        response = {
            'success': False,
            'message': error.message,
            'error_code': error.error_code
        }

        if hasattr(error, 'errors') and error.errors:
            response['errors'] = error.errors

        return jsonify(response), error.status_code

    @app.errorhandler(400)
    def handle_bad_request(error):
        """处理 400 错误"""
        logger.warning(
            f"Bad Request: {request.path} | Method: {request.method} | "
            f"Error: {str(error)}"
        )
        return jsonify({
            'success': False,
            'message': '请求参数错误',
            'error_code': 'BAD_REQUEST'
        }), 400

    @app.errorhandler(401)
    def handle_unauthorized(error):
        """处理 401 错误"""
        logger.warning(
            f"Unauthorized: {request.path} | Method: {request.method}"
        )
        return jsonify({
            'success': False,
            'message': '未授权访问',
            'error_code': 'UNAUTHORIZED'
        }), 401

    @app.errorhandler(403)
    def handle_forbidden(error):
        """处理 403 错误"""
        logger.warning(
            f"Forbidden: {request.path} | Method: {request.method}"
        )
        return jsonify({
            'success': False,
            'message': '禁止访问',
            'error_code': 'FORBIDDEN'
        }), 403

    @app.errorhandler(404)
    def handle_not_found(error):
        """处理 404 错误"""
        logger.info(
            f"Not Found: {request.path} | Method: {request.method}"
        )
        return jsonify({
            'success': False,
            'message': '接口不存在',
            'error_code': 'NOT_FOUND'
        }), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        """处理 405 错误"""
        logger.warning(
            f"Method Not Allowed: {request.path} | Method: {request.method}"
        )
        return jsonify({
            'success': False,
            'message': '请求方法不允许',
            'error_code': 'METHOD_NOT_ALLOWED',
            'allowed_methods': error.valid_methods
        }), 405

    @app.errorhandler(429)
    def handle_too_many_requests(error):
        """处理 429 错误"""
        logger.warning(
            f"Too Many Requests: {request.path} | Method: {request.method}"
        )
        return jsonify({
            'success': False,
            'message': '请求过于频繁，请稍后再试',
            'error_code': 'TOO_MANY_REQUESTS'
        }), 429

    @app.errorhandler(500)
    def handle_internal_server_error(error):
        """处理 500 错误"""
        logger.error(
            f"Internal Server Error: {request.path} | Method: {request.method} | "
            f"Error: {str(error)}\n{traceback.format_exc()}"
        )
        return jsonify({
            'success': False,
            'message': '服务器内部错误',
            'error_code': 'INTERNAL_SERVER_ERROR'
        }), 500

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """处理未预期的异常"""
        logger.error(
            f"Unexpected Error: {request.path} | Method: {request.method} | "
            f"Error: {str(error)}\n{traceback.format_exc()}"
        )
        return jsonify({
            'success': False,
            'message': '服务器内部错误',
            'error_code': 'INTERNAL_SERVER_ERROR'
        }), 500

    logger.info("✅ 错误处理器已注册")


def handle_errors(f):
    """错误处理装饰器"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except APIError:
            raise  # API 异常由错误处理器处理
        except ValueError as e:
            raise ValidationError(f'参数验证失败: {str(e)}')
        except KeyError as e:
            raise ValidationError(f'缺少必要参数: {str(e)}')
        except Exception as e:
            logger.error(
                f"Unexpected error in {f.__name__}: {str(e)}\n"
                f"{traceback.format_exc()}"
            )
            raise InternalServerError()

    return decorated_function

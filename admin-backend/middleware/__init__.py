"""
中间件包
Middleware Package

包含所有中间件模块
"""

from .error_handler import (
    register_error_handlers,
    handle_errors,
    APIError,
    ValidationError,
    NotFoundError,
    UnauthorizedError,
    ForbiddenError,
    ConflictError,
    TooManyRequestsError,
    InternalServerError
)

from .request_logger import (
    setup_request_logging,
    log_function_call
)

from .jwt_auth import (
    init_jwt_auth,
    get_jwt_auth,
    require_auth,
    optional_auth,
    require_admin
)

__all__ = [
    # Error Handler
    'register_error_handlers',
    'handle_errors',
    'APIError',
    'ValidationError',
    'NotFoundError',
    'UnauthorizedError',
    'ForbiddenError',
    'ConflictError',
    'TooManyRequestsError',
    'InternalServerError',

    # Request Logger
    'setup_request_logging',
    'log_function_call',

    # JWT Auth
    'init_jwt_auth',
    'get_jwt_auth',
    'require_auth',
    'optional_auth',
    'require_admin'
]

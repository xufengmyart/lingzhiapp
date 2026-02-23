"""
API路径兼容性处理
解决前端API路径重复问题（/api/api/* -> /api/*）
"""

from flask import Blueprint, request, jsonify, Response
import logging

logger = logging.getLogger(__name__)

api_path_compat_bp = Blueprint('api_path_compat', __name__)

# ============ 修复重复路径 ============

@api_path_compat_bp.route('/api/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'])
def fix_duplicate_api_path(path):
    """将 /api/api/* 重定向到 /api/*"""
    from flask import current_app

    logger.info(f"API路径重定向: /api/api/{path} -> /api/{path}, Method: {request.method}, Content-Type: {request.content_type}")

    try:
        # 处理 OPTIONS 预检请求
        if request.method == 'OPTIONS':
            response = Response('', status=204)
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
            response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type, Accept, Origin'
            return response

        # 使用 werkzeug Client 来转发请求（支持文件上传）
        from werkzeug.test import Client
        import io

        # 准备请求数据
        environ = {
            'REQUEST_METHOD': request.method,
            'PATH_INFO': f'/api/{path}',
            'QUERY_STRING': request.query_string.decode('utf-8') if request.query_string else '',
            'CONTENT_TYPE': request.content_type or '',
            'CONTENT_LENGTH': str(request.content_length) if request.content_length else '',
            'REMOTE_ADDR': request.remote_addr,
            'HTTP_AUTHORIZATION': request.headers.get('Authorization', ''),
        }

        # 添加其他HTTP头
        for key, value in request.headers:
            if key.upper() not in ['CONTENT-TYPE', 'CONTENT-LENGTH', 'HOST', 'CONNECTION']:
                environ[f'HTTP_{key.upper().replace("-", "_")}'] = value

        # 处理不同类型的请求体
        if request.method in ['POST', 'PUT', 'PATCH']:
            if request.content_type and 'multipart/form-data' in request.content_type:
                # 文件上传：保持原始的输入流
                environ['wsgi.input'] = request.stream
            elif request.content_type and 'application/json' in request.content_type:
                # JSON 请求
                data = request.get_data(as_text=False)
                environ['wsgi.input'] = io.BytesIO(data)
            elif request.content_type and 'application/x-www-form-urlencoded' in request.content_type:
                # 表单请求
                data = request.get_data(as_text=False)
                environ['wsgi.input'] = io.BytesIO(data)
            else:
                # 其他类型
                data = request.get_data(as_text=False)
                environ['wsgi.input'] = io.BytesIO(data)
        else:
            # GET/DELETE 请求
            environ['wsgi.input'] = io.BytesIO(b'')

        # 添加其他 WSGI 环境变量
        environ['wsgi.url_scheme'] = 'https'
        environ['wsgi.version'] = (1, 0)
        environ['wsgi.errors'] = io.StringIO()
        environ['wsgi.multithread'] = False
        environ['wsgi.multiprocess'] = True
        environ['wsgi.run_once'] = False

        # 调用 WSGI 应用
        response_start = {}

        def start_response(status, headers):
            response_start['status'] = status
            response_start['headers'] = headers

        response_iter = current_app.wsgi_app(environ, start_response)

        # 构造 Flask 响应
        response_body = b''.join(response_iter)
        response = Response(response_body)

        # 设置响应头
        if 'headers' in response_start:
            for key, value in response_start['headers']:
                response.headers[key] = value

        # 设置状态码
        if 'status' in response_start:
            status_code = int(response_start['status'].split()[0])
            response.status_code = status_code

        return response

    except Exception as e:
        logger.error(f"API路径重定向异常: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'API路径重定向异常: {str(e)}'
        }), 500

"""
JSON响应转换中间件
JSON Response Converter Middleware

自动将所有API响应中的snake_case字段名转换为camelCase
"""

from flask import jsonify, Response, request
import json
import logging

try:
    from utils.response_utils import transform_dict_keys
    RESPONSE_UTILS_AVAILABLE = True
except ImportError:
    RESPONSE_UTILS_AVAILABLE = False

logger = logging.getLogger(__name__)


def register_response_converter(app):
    """注册响应转换中间件"""

    @app.after_request
    def convert_response_to_camel_case(response: Response):
        """
        将响应中的snake_case字段名转换为camelCase

        仅处理：
        1. Content-Type为application/json的响应
        2. 成功状态码（2xx）
        3. 响应体为有效JSON
        """
        # 跳过非JSON响应
        content_type = response.content_type or ''
        if 'application/json' not in content_type:
            return response

        # 跳过错误响应（非2xx状态码）
        if response.status_code >= 400:
            return response

        # 跳过空响应
        if not response.data or len(response.data) == 0:
            return response

        try:
            # 解析响应JSON
            data = json.loads(response.data.decode('utf-8'))

            # 如果response_utils可用，转换字段名
            if RESPONSE_UTILS_AVAILABLE:
                # 递归转换所有嵌套的字典
                converted_data = transform_dict_keys(data, to_camel=True)

                # 重新序列化
                response.data = json.dumps(
                    converted_data,
                    ensure_ascii=False,
                    separators=(',', ':')
                ).encode('utf-8')

                # 更新Content-Length
                response.headers['Content-Length'] = len(response.data)

                # 安全地获取字段名用于日志
                def get_fields(obj):
                    if isinstance(obj, dict) and 'data' in obj:
                        data_field = obj['data']
                        if isinstance(data_field, dict):
                            return list(data_field.keys())
                        elif isinstance(data_field, list) and len(data_field) > 0:
                            return list(data_field[0].keys()) if isinstance(data_field[0], dict) else []
                    return 'N/A'

                logger.debug(
                    f"响应字段名已转换: {request.path} | "
                    f"原始字段: {get_fields(data)} | "
                    f"转换后字段: {get_fields(converted_data)}"
                )

        except json.JSONDecodeError as e:
            logger.warning(f"JSON解析失败: {request.path} | Error: {str(e)}")
        except Exception as e:
            logger.error(f"响应转换失败: {request.path} | Error: {str(e)}", exc_info=True)

        return response

    logger.info("✅ 响应转换中间件已注册")

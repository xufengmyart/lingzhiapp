"""
测试环境变量加载
"""
from flask import Blueprint
from config import config
import os

test_env_bp = Blueprint('test_env', __name__)

@test_env_bp.route('/test/env', methods=['GET'])
def test_env():
    """测试环境变量"""
    # 检查.env文件是否存在
    env_file = os.path.join(os.path.dirname(__file__), '../.env')
    env_exists = os.path.exists(env_file)
    env_size = os.path.getsize(env_file) if env_exists else 0

    # 检查环境变量
    env_appid = os.getenv('WECHAT_OPEN_PLATFORM_APPID', '')
    env_secret = os.getenv('WECHAT_OPEN_PLATFORM_APPSECRET', '')

    return {
        'success': True,
        'data': {
            'env_file_exists': env_exists,
            'env_file_size': env_size,
            'env_file_path': env_file,
            'os_env_appid': env_appid,
            'os_env_secret': (env_secret[:8] + '***') if env_secret else None,
            'config_has_appid': hasattr(config, 'WECHAT_OPEN_PLATFORM_APPID'),
            'config_has_secret': hasattr(config, 'WECHAT_OPEN_PLATFORM_APPSECRET'),
            'config_appid': config.WECHAT_OPEN_PLATFORM_APPID if hasattr(config, 'WECHAT_OPEN_PLATFORM_APPID') else None,
            'config_secret': (config.WECHAT_OPEN_PLATFORM_APPSECRET[:8] + '***') if hasattr(config, 'WECHAT_OPEN_PLATFORM_APPSECRET') and config.WECHAT_OPEN_PLATFORM_APPSECRET else None
        }
    }

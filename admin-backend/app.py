"""
灵值生态园智能体系统 - 主应用入口
简化版本，所有业务逻辑已迁移到 routes/ 模块
"""

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os
import sqlite3

# 导入配置管理模块
from config import config

# 加载环境变量配置文件
try:
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"✅ 环境变量已加载: {env_path}")
    else:
        print(f"⚠️  .env文件不存在: {env_path}")
except ImportError:
    print("⚠️  python-dotenv未安装，使用默认环境变量")

# 导入WebSocket服务
try:
    from websocket_service import socketio, get_online_count
    HAS_WEBSOCKET = True
    print("✅ WebSocket服务已加载")
except ImportError:
    HAS_WEBSOCKET = False
    print("⚠️  WebSocket服务未加载")

# 使用配置管理模块获取所有配置
SECRET_KEY = config.JWT_SECRET_KEY
# 如果是测试环境，使用测试数据库
DATABASE = os.getenv('TEST_DATABASE_PATH', config.DATABASE_PATH)
OLD_DATABASE = config.OLD_DATABASE
JWT_SECRET = config.JWT_SECRET_KEY
JWT_EXPIRATION = config.JWT_EXPIRATION

print(f"[配置] 数据库路径: {DATABASE}")
print(f"[配置] JWT过期时间: {JWT_EXPIRATION}秒")

# 导入日志模块
from logger import setup_logger
logger = setup_logger('app', log_dir='logs')

# 设置 Coze 环境变量（如果未设置）
os.environ.setdefault('COZE_WORKLOAD_IDENTITY_API_KEY', 'WU9RNGFQTmZTc3VnbnRCMmsyWUtDcDZHOWJMa0g5ZVk6NVN5cHNRbkNidjFzWHNEVnJ4UTZKQlN1SUxYMlU3ZEtidVRXbDYwWDFyZW9sdmhQbTU1QVdQaVJHcVo4b1BoWA==')
os.environ.setdefault('COZE_INTEGRATION_MODEL_BASE_URL', 'https://integration.coze.cn/api/v3')
os.environ.setdefault('COZE_INTEGRATION_BASE_URL', 'https://integration.coze.cn')
os.environ.setdefault('COZE_PROJECT_ID', '7597768668038643746')

# 创建 Flask 应用
app = Flask(__name__)
app.secret_key = SECRET_KEY

# 使用socketio包装app（如果WebSocket可用）
# 注意：socketio.init_app()会包装app，但返回socketio对象
# 我们需要保存原始的app用于装饰器
if HAS_WEBSOCKET:
    socketio_app = socketio.init_app(app, cors_allowed_origins="*", async_mode='threading')
    print("✅ Flask app 已使用 SocketIO 包装")
else:
    socketio_app = None
    print("⚠️  未使用 SocketIO 包装")

# ============ 注册中间件 ============

print("\n🔧 初始化中间件...")

# 1. 初始化 JWT 认证
try:
    from middleware.jwt_auth import init_jwt_auth
    init_jwt_auth(JWT_SECRET, JWT_EXPIRATION)
    print("✅ JWT 认证中间件已初始化")
except ImportError as e:
    print(f"⚠️  JWT 认证中间件初始化失败: {e}")

# 2. 注册错误处理器
try:
    from middleware.error_handler import register_error_handlers
    register_error_handlers(app)
    print("✅ 错误处理器已注册")
except ImportError as e:
    print(f"⚠️  错误处理器注册失败: {e}")

# 3. 注册请求日志
try:
    from middleware.request_logger import setup_request_logging
    setup_request_logging(app)
    print("✅ 请求日志中间件已注册")
except ImportError as e:
    print(f"⚠️  请求日志中间件注册失败: {e}")

# 4. 注册响应转换中间件（自动转换为camelCase）
try:
    from middleware.response_converter import register_response_converter
    register_response_converter(app)
    print("✅ 响应转换中间件已注册")
except ImportError as e:
    print(f"⚠️  响应转换中间件注册失败: {e}")

# 配置 CORS 允许跨域请求
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://meiyueart.com", "http://meiyueart.com", "*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    },
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# 配置静态文件路径
ENV = os.getenv('ENV', 'development')
if ENV == 'production':
    public_dir = os.getenv('STATIC_DIR', '/var/www/meiyueart.com')
    # uploads目录始终放在后端应用目录下
    uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads')
else:
    public_dir = os.path.join(os.path.dirname(__file__), '../public')
    uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads')

if os.path.exists(public_dir):
    app.static_folder = public_dir
    app.static_url_path = '/'
    print(f"静态文件目录: {public_dir}")

# 确保uploads目录存在
os.makedirs(uploads_dir, exist_ok=True)
os.makedirs(os.path.join(uploads_dir, 'avatars'), exist_ok=True)
print(f"上传文件目录: {uploads_dir}")

# 添加 uploads 静态文件服务
@app.route('/uploads/<path:filename>')
def serve_uploads(filename):
    return send_from_directory(uploads_dir, filename)

# ============ 注册蓝图（按功能模块） ============

print("\n📦 开始注册路由模块...")

# 0. API路径兼容（必须最先注册）
try:
    from routes.api_path_compat import api_path_compat_bp
    app.register_blueprint(api_path_compat_bp, url_prefix='/api')
    print("✅ API路径兼容 已注册")
except Exception as e:
    print(f"⚠️  API路径兼容模块加载失败: {e}")

# 1. 认证系统
try:
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    print("✅ 认证系统 API 已注册")
except ImportError as e:
    print(f"⚠️  认证系统模块加载失败: {e}")

# 2. 管理员功能
try:
    from routes.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/api')
    print("✅ 管理员功能 API 已注册")
except ImportError as e:
    print(f"⚠️  管理员功能模块加载失败: {e}")

# 3. 推荐系统
try:
    from routes.referral import referral_bp
    app.register_blueprint(referral_bp, url_prefix='/api')
    print("✅ 推荐系统 API 已注册")
except ImportError as e:
    print(f"⚠️  推荐系统模块加载失败: {e}")

# 4. 签到系统
try:
    from routes.checkin import checkin_bp
    app.register_blueprint(checkin_bp, url_prefix='/api')
    print("✅ 签到系统 API 已注册")
except ImportError as e:
    print(f"⚠️  签到系统模块加载失败: {e}")

# 5. 充值系统
try:
    from routes.recharge import recharge_bp
    app.register_blueprint(recharge_bp, url_prefix='/api')
    print("✅ 充值系统 API 已注册")
except ImportError as e:
    print(f"⚠️  充值系统模块加载失败: {e}")

# 5.1 支付系统
try:
    from routes.payment import payment_bp
    app.register_blueprint(payment_bp, url_prefix='/api')
    print("✅ 支付系统 API 已注册")
except ImportError as e:
    print(f"⚠️  支付系统模块加载失败: {e}")

# 6. 对话记忆系统
try:
    from conversation_memory import memory_bp, ensure_memory_tables
    app.register_blueprint(memory_bp, url_prefix='/api/memory')
    ensure_memory_tables()
    print("✅ 对话记忆系统 API 已注册")
except ImportError as e:
    print(f"⚠️  对话记忆系统模块加载失败: {e}")

# 7. 用户旅程系统
try:
    from user_journey import journey_bp, init_journey_tables
    app.register_blueprint(journey_bp, url_prefix='/api')
    init_journey_tables()
    print("✅ 用户旅程系统 API 已注册")
except ImportError as e:
    print(f"⚠️  用户旅程系统模块加载失败: {e}")

# 8. 统一认证系统
try:
    from unified_auth import auth_bp as unified_auth_bp
    app.register_blueprint(unified_auth_bp, url_prefix='/api')
    print("✅ 统一认证系统 API 已注册")
except ImportError as e:
    print(f"⚠️  统一认证系统模块加载失败: {e}")

# 9. 商家服务系统
try:
    from merchant_service import (
        init_merchant_tables,
        seed_merchant_data
    )
    init_merchant_tables()
    seed_merchant_data()
    print("✅ 商家服务系统 API 已注册")
except ImportError as e:
    print(f"⚠️  商家服务系统模块加载失败: {e}")

# 10. 用户资料编辑
try:
    from routes.user_profile import user_profile_bp
    app.register_blueprint(user_profile_bp, url_prefix='/api')
    print("✅ 用户资料编辑 API 已注册")
except ImportError as e:
    print(f"⚠️  用户资料编辑模块加载失败: {e}")

# 10.5. 用户个人中心
try:
    from routes.user_center import user_center_bp
    app.register_blueprint(user_center_bp, url_prefix='/api')
    print("✅ 用户个人中心 API 已注册")
except ImportError as e:
    print(f"⚠️  用户个人中心模块加载失败: {e}")

# 10.6. 密码修改功能
try:
    from routes.change_password import password_bp
    app.register_blueprint(password_bp, url_prefix='/api')
    print("✅ 密码修改功能 API 已注册")
except ImportError as e:
    print(f"⚠️  密码修改功能模块加载失败: {e}")

# 11. 贡献值系统
try:
    from routes.contribution import contribution_bp
    app.register_blueprint(contribution_bp, url_prefix='/api')
    print("✅ 贡献值系统 API 已注册")
except ImportError as e:
    print(f"⚠️  贡献值系统模块加载失败: {e}")

# 12. 商家功能
try:
    from routes.merchant import merchant_bp
    app.register_blueprint(merchant_bp, url_prefix='/api')
    print("✅ 商家功能 API 已注册")
except ImportError as e:
    print(f"⚠️  商家功能模块加载失败: {e}")

# 13. 专家功能
try:
    from routes.expert import expert_bp
    app.register_blueprint(expert_bp, url_prefix='/api')
    print("✅ 专家功能 API 已注册")
except ImportError as e:
    print(f"⚠️  专家功能模块加载失败: {e}")

# 14. 文化圣地
try:
    from routes.sacred_sites import sacred_bp
    app.register_blueprint(sacred_bp, url_prefix='/api')
    print("✅ 文化圣地 API 已注册")
except Exception as e:
    print(f"⚠️  文化圣地模块加载失败: {e}")

# 15. 美学侦探任务
try:
    from routes.aesthetic_tasks import aesthetic_bp
    app.register_blueprint(aesthetic_bp, url_prefix='/api')
    print("✅ 美学侦探任务 API 已注册")
except Exception as e:
    print(f"⚠️  美学侦探任务模块加载失败: {e}")

# 16. 数字资产
try:
    from routes.digital_assets import assets_bp
    app.register_blueprint(assets_bp, url_prefix='/api')
    print("✅ 数字资产 API 已注册")
except Exception as e:
    print(f"⚠️  数字资产模块加载失败: {e}")

# 17. 用户反馈
try:
    from routes.feedback import feedback_bp
    app.register_blueprint(feedback_bp, url_prefix='/api')
    print("✅ 用户反馈 API 已注册")
except ImportError as e:
    print(f"⚠️  用户反馈模块加载失败: {e}")

# 18. 批量导入
try:
    from routes.batch_import import batch_import_bp
    app.register_blueprint(batch_import_bp, url_prefix='/api')
    print("✅ 批量导入 API 已注册")
except ImportError as e:
    print(f"⚠️  批量导入模块加载失败: {e}")

# 19. 资产交易市场
try:
    from routes.market import market_bp
    app.register_blueprint(market_bp, url_prefix='/api/v9')
    print("✅ 资产交易市场 API 已注册")
except ImportError as e:
    print(f"⚠️  资产交易市场模块加载失败: {e}")

# 20. API监控和错误日志
try:
    from routes.monitor import monitor_bp
    app.register_blueprint(monitor_bp, url_prefix='/api')
    print("✅ API监控和错误日志 API 已注册")
except ImportError as e:
    print(f"⚠️  API监控和错误日志模块加载失败: {e}")

# 18. 灵值修复
try:
    from routes.lingzhi_fix import lingzhi_fix_bp
    app.register_blueprint(lingzhi_fix_bp, url_prefix='/api')
    print("✅ 灵值修复 API 已注册")
except ImportError as e:
    print(f"⚠️  灵值修复模块加载失败: {e}")

# 18. 数据分析
try:
    from routes.analytics import analytics_bp
    app.register_blueprint(analytics_bp, url_prefix='/api')
    print("✅ 数据分析 API 已注册")
except ImportError as e:
    print(f"⚠️  数据分析模块加载失败: {e}")

# 19. 导航配置
try:
    from routes.navigation_config import navigation_config_bp
    app.register_blueprint(navigation_config_bp, url_prefix='/api')
    print("✅ 导航配置 API 已注册")
except ImportError as e:
    print(f"⚠️  导航配置模块加载失败: {e}")

# 20. 用户引导文档
try:
    from routes.user_guide import user_guide_bp
    app.register_blueprint(user_guide_bp, url_prefix='/api')
    print("✅ 用户引导文档 API 已注册")
except ImportError as e:
    print(f"⚠️  用户引导文档模块加载失败: {e}")

# 22. 头像上传
try:
    from routes.avatar_upload import avatar_upload_bp
    app.register_blueprint(avatar_upload_bp, url_prefix='/api')
    print("✅ 头像上传 API 已注册")
except ImportError as e:
    print(f"⚠️  头像上传模块加载失败: {e}")

# 23. 智能体聊天
try:
    from routes.agent import agent_bp
    app.register_blueprint(agent_bp, url_prefix='/api')
    print("✅ 智能体聊天 API 已注册")
except ImportError as e:
    print(f"⚠️  智能体聊天模块加载失败: {e}")

# 22. 知识库
try:
    from routes.knowledge import knowledge_bp
    app.register_blueprint(knowledge_bp, url_prefix='/api')
    print("✅ 知识库 API 已注册")
except ImportError as e:
    print(f"⚠️  知识库模块加载失败: {e}")

# 23. 用户系统
try:
    from routes.user_system import user_bp
    app.register_blueprint(user_bp)
    print("✅ 用户系统 API 已注册")
except ImportError as e:
    print(f"⚠️  用户系统模块加载失败: {e}")

# 24. 综合功能
try:
    from routes.complete_apis import complete_bp
    app.register_blueprint(complete_bp)
    print("✅ 综合功能 API 已注册")
except ImportError as e:
    print(f"⚠️  综合功能模块加载失败: {e}")

# 25. 微信小程序登录
try:
    from routes.wechat_login import wechat_bp
    app.register_blueprint(wechat_bp)
    print("✅ 微信小程序登录 API 已注册")
except Exception as e:
    print(f"⚠️  微信小程序登录模块加载失败: {e}")

# 26. 微信开放平台登录
try:
    from routes.wechat_oauth import wechat_oauth_bp
    app.register_blueprint(wechat_oauth_bp, url_prefix='/api')
    print("✅ 微信开放平台登录 API 已注册")
except Exception as e:
    import traceback
    print(f"⚠️  微信开放平台登录模块加载失败: {e}")
    traceback.print_exc()

# 27. 测试环境变量（仅开发环境）
try:
    from routes.test_env import test_env_bp
    app.register_blueprint(test_env_bp, url_prefix='/api')
    print("✅ 测试环境变量 API 已注册")
except Exception as e:
    print(f"⚠️  测试环境变量模块加载失败: {e}")

# 28. 对话计费
try:
    from routes.conversation_billing import conversation_billing_bp
    app.register_blueprint(conversation_billing_bp, url_prefix='/api')
    print("✅ 对话计费 API 已注册")
except Exception as e:
    print(f"⚠️  对话计费模块加载失败: {e}")

# 27. 动态资讯
try:
    from routes.news_articles import news_bp
    app.register_blueprint(news_bp, url_prefix='/api')
    print("✅ 动态资讯 API 已注册")
except Exception as e:
    print(f"⚠️  动态资讯模块加载失败: {e}")

# 27.1. 文章评论
try:
    from routes.news_comments import comments_bp
    app.register_blueprint(comments_bp, url_prefix='/api')
    print("✅ 文章评论 API 已注册")
except Exception as e:
    print(f"⚠️  文章评论模块加载失败: {e}")

# 27.2. 平台信息（系统新闻和平台公告合并）
try:
    from routes.platform_info import platform_info_bp
    app.register_blueprint(platform_info_bp, url_prefix='/api')
    print('✅ 平台信息 API 已注册')
except Exception as e:
    print(f'⚠️  平台信息模块加载失败: {e}')

# 27.3. 平台信息增强功能（推送、阅读、订阅、评论、分享）
try:
    from routes.platform_info_enhanced import platform_info_enhanced_bp
    app.register_blueprint(platform_info_enhanced_bp, url_prefix='/api')
    print('✅ 平台信息增强功能 API 已注册')
except Exception as e:
    print(f'⚠️  平台信息增强功能模块加载失败: {e}')

# 28. 二维码生成
try:
    from routes.qrcode import qrcode_bp
    app.register_blueprint(qrcode_bp, url_prefix='/api')
    print("✅ 二维码生成 API 已注册")
except Exception as e:
    print(f"⚠️  二维码生成模块加载失败: {e}")

# 28.1. 文章分享
try:
    from routes.share import share_bp
    app.register_blueprint(share_bp, url_prefix='/api')
    print("✅ 文章分享 API 已注册")
except Exception as e:
    print(f"⚠️  文章分享模块加载失败: {e}")

# 28.2. 推荐关系管理（仅超级管理员）
try:
    from routes.referral_management import referral_management_bp
    app.register_blueprint(referral_management_bp, url_prefix='/api/admin')
    print("✅ 推荐关系管理 API 已注册")
except Exception as e:
    print(f"⚠️  推荐关系管理模块加载失败: {e}")

# 28.3. 分享分析系统（点击统计、转化率、排行榜、奖励机制）
try:
    from routes.share_analytics import share_analytics_bp
    app.register_blueprint(share_analytics_bp, url_prefix='/api/analytics')
    print("✅ 分享分析系统 API 已注册")
except Exception as e:
    print(f"⚠️  分享分析系统模块加载失败: {e}")

# 29. 中视频项目
try:
    from medium_video_api import medium_video_bp
    app.register_blueprint(medium_video_bp, url_prefix='/api')
    print("✅ 中视频项目 API 已注册")
except Exception as e:
    print(f"⚠️  中视频项目模块加载失败: {e}")

# 29. 推荐关系网络
try:
    from referral_network_api import referral_network_bp
    app.register_blueprint(referral_network_bp, url_prefix='/api')
    print("✅ 推荐关系网络 API 已注册")
except Exception as e:
    print(f"⚠️  推荐关系网络模块加载失败: {e}")

# 30. 合伙人招募
try:
    from partner_api import partner_bp
    app.register_blueprint(partner_bp, url_prefix='/api')
    print("✅ 合伙人招募 API 已注册")
except Exception as e:
    print(f"⚠️  合伙人招募模块加载失败: {e}")

# 31. API路径兼容（修复前端路径错误）
try:
    from routes.api_compat import compat_bp
    app.register_blueprint(compat_bp, url_prefix='/api')
    print("✅ API路径兼容 API 已注册")
except Exception as e:
    print(f"⚠️  API路径兼容模块加载失败: {e}")

# 32. 综合功能（修复500错误）
try:
    from routes.comprehensive_fix import comprehensive_bp
    app.register_blueprint(comprehensive_bp, url_prefix='/api')
    print("✅ 综合功能 API 已注册")
except Exception as e:
    print(f"⚠️  综合功能模块加载失败: {e}")

# 33. 头像上传
try:
    from routes.avatar_upload import avatar_upload_bp
    app.register_blueprint(avatar_upload_bp, url_prefix='/api')
    print("✅ 头像上传 API 已注册")
except Exception as e:
    print(f"⚠️  头像上传模块加载失败: {e}")

# 34. 二维码生成
try:
    from routes.qrcode import qrcode_bp
    app.register_blueprint(qrcode_bp, url_prefix='/api')
    print("✅ 二维码生成 API 已注册")
except Exception as e:
    print(f"⚠️  二维码生成模块加载失败: {e}")

# 35. 公司信息管理
try:
    from routes.company_info import company_info_bp
    app.register_blueprint(company_info_bp, url_prefix='/api')
    print("✅ 公司信息管理 API 已注册")
except Exception as e:
    print(f"⚠️  公司信息管理模块加载失败: {e}")

# 35. 公司项目管理
try:
    from routes.company_projects import company_projects_bp
    app.register_blueprint(company_projects_bp, url_prefix='/api')
    print("✅ 公司项目管理 API 已注册")
except Exception as e:
    print(f"⚠️  公司项目管理模块加载失败: {e}")

# 36. 角色管理
try:
    from routes.role_management import role_management_bp
    app.register_blueprint(role_management_bp, url_prefix='/api')
    print("✅ 角色管理 API 已注册")
except Exception as e:
    print(f"⚠️  角色管理模块加载失败: {e}")

# 37. 用户资源管理
try:
    from routes.user_resources import user_resources_bp
    app.register_blueprint(user_resources_bp, url_prefix='/api')
    print("✅ 用户资源管理 API 已注册")
except Exception as e:
    print(f"⚠️  用户资源管理模块加载失败: {e}")

# 38. 分红池管理
try:
    from routes.dividend_pool import dividend_pool_bp
    app.register_blueprint(dividend_pool_bp, url_prefix='/api')
    print("✅ 分红池管理 API 已注册")
except Exception as e:
    print(f"⚠️  分红池管理模块加载失败: {e}")

# 39. 经济系统
try:
    from routes.economy import economy_bp
    app.register_blueprint(economy_bp, url_prefix='/api')
    print("✅ 经济系统 API 已注册")
except Exception as e:
    print(f"⚠️  经济系统模块加载失败: {e}")
    import traceback
    traceback.print_exc()

# 40. 区块链集成
try:
    from routes.blockchain import blockchain_bp
    app.register_blueprint(blockchain_bp, url_prefix='/api')
    print("✅ 区块链集成 API 已注册")
except Exception as e:
    print(f"⚠️  区块链集成模块加载失败: {e}")
    import traceback
    traceback.print_exc()

# 41. 管理员统计API
try:
    from routes.admin_stats import admin_stats_bp
    app.register_blueprint(admin_stats_bp, url_prefix='/api')
    print("✅ 管理员统计 API 已注册")
except Exception as e:
    print(f"⚠️  管理员统计模块加载失败: {e}")

# 40. 文化转译系统
try:
    from routes.culture_translation import culture_translation_bp
    app.register_blueprint(culture_translation_bp, url_prefix='/api')
    print("✅ 文化转译系统 API 已注册")
except Exception as e:
    print(f"⚠️  文化转译系统模块加载失败: {e}")
    import traceback
    traceback.print_exc()

# 41. 私有资源库系统
try:
    from routes.private_resources import private_resources_bp
    app.register_blueprint(private_resources_bp)
    print("✅ 私有资源库系统 API 已注册")
except Exception as e:
    print(f"⚠️  私有资源库系统模块加载失败: {e}")
    import traceback
    traceback.print_exc()

# 42. 通知系统
try:
    from routes.notifications import notifications_bp
    app.register_blueprint(notifications_bp, url_prefix='/api')
    print("✅ 通知系统 API 已注册")
except Exception as e:
    print(f"⚠️  通知系统模块加载失败: {e}")
    import traceback
    traceback.print_exc()

# 43. 报表系统
try:
    from routes.reports import reports_bp
    app.register_blueprint(reports_bp)
    print("✅ 报表系统 API 已注册")
except Exception as e:
    print(f"⚠️  报表系统模块加载失败: {e}")
    import traceback
    traceback.print_exc()

# 44. 修改密码
try:
    from routes.change_password import password_bp
    app.register_blueprint(password_bp, url_prefix='/api', name='change_password')
    print("✅ 修改密码 API 已注册")
except Exception as e:
    print(f"⚠️  修改密码模块加载失败: {e}")
    import traceback
    traceback.print_exc()

# 45. 用户活动
try:
    from routes.user_activities import user_activities_bp
    app.register_blueprint(user_activities_bp, url_prefix='/api')
    print("✅ 用户活动 API 已注册")
except Exception as e:
    print(f"⚠️  用户活动模块加载失败: {e}")
    import traceback
    traceback.print_exc()

# 46. 项目详情（数据资产工作流）
try:
    from routes.project_details import project_details_bp
    app.register_blueprint(project_details_bp, url_prefix='/api')
    print("✅ 项目详情 API 已注册")
except Exception as e:
    print(f"⚠️  项目详情模块加载失败: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ 所有路由模块注册完成！\n")

# ============ 核心路由（留在 app.py 中） ============

@app.route('/')
def index():
    """首页 - 返回前端应用"""
    try:
        # 获取静态文件目录
        ENV = os.getenv('ENV', 'development')
        if ENV == 'production':
            public_dir = os.getenv('STATIC_DIR', '/var/www/meiyueart.com')
        else:
            public_dir = os.path.join(os.path.dirname(__file__), '../public')
        
        index_file = os.path.join(public_dir, 'index.html')
        if os.path.exists(index_file):
            with open(index_file, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return jsonify({
                'success': False,
                'message': f'前端文件未找到: {index_file}',
                'version': '9.24.0',
                'status': 'error'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'加载前端失败: {str(e)}',
            'version': '9.24.0',
            'status': 'error'
        }), 500

@app.route('/api/status')
def status():
    """系统状态"""
    return jsonify({
        'success': True,
        'message': '系统正常运行',
        'version': '9.24.0',
        'modules': '已重构为模块化架构'
    })

@app.route('/api/health')
def health():
    """健康检查"""
    try:
        conn = sqlite3.connect(DATABASE)
        conn.execute("SELECT 1")
        conn.close()
        return jsonify({
            'success': True,
            'status': 'healthy',
            'database': 'connected'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }), 500

# ============ 数据库初始化 ============

def init_db():
    """初始化数据库表结构"""
    print("📦 开始初始化数据库...")

    conn = None
    cursor = None

    try:
        # 先清理数据库锁定文件
        import os
        db_dir = os.path.dirname(DATABASE)
        if db_dir and os.path.exists(db_dir):
            for pattern in ['-wal', '-shm', '-journal', '.lock']:
                lock_file = DATABASE + pattern
                if os.path.exists(lock_file):
                    try:
                        os.remove(lock_file)
                        print(f"✅ 已删除锁定文件: {lock_file}")
                    except:
                        pass

        conn = sqlite3.connect(DATABASE, timeout=30)
        cursor = conn.cursor()

        # 禁用WAL模式以避免锁定问题
        cursor.execute('PRAGMA journal_mode=DELETE')
        cursor.execute('PRAGMA synchronous=FULL')
        cursor.execute('PRAGMA busy_timeout=30000')  # 30秒超时
        cursor.execute('PRAGMA locking_mode=NORMAL')
        print("✅ SQLite 配置完成（禁用WAL模式）")

        # 用户表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            phone TEXT,
            password_hash TEXT NOT NULL,
            total_lingzhi INTEGER DEFAULT 100,
            status TEXT DEFAULT 'active',
            last_login_at TIMESTAMP,
            avatar_url TEXT,
            real_name TEXT,
            is_verified BOOLEAN DEFAULT 0,
            login_type TEXT DEFAULT 'phone',
            wechat_openid TEXT,
            wechat_unionid TEXT,
            wechat_nickname TEXT,
            wechat_avatar TEXT,
            referrer_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # 添加字段（如果表已存在）
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'active'")
        except:
            pass
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN last_login_at TIMESTAMP")
        except:
            pass
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN avatar_url TEXT")
        except:
            pass
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN real_name TEXT")
        except:
            pass
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT 0")
        except:
            pass
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN login_type TEXT DEFAULT 'phone'")
        except:
            pass
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN wechat_openid TEXT UNIQUE")
        except:
            pass
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN wechat_unionid TEXT")
        except:
            pass
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN wechat_nickname TEXT")
        except:
            pass
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN wechat_avatar TEXT")
        except:
            pass
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN referrer_id INTEGER")
        except:
            pass

        # 管理员表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # 签到记录表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS checkin_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            checkin_date DATE NOT NULL,
            lingzhi_earned INTEGER DEFAULT 10,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, checkin_date)
        )
        ''')

        # 推荐关系表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS referral_relationships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referrer_id INTEGER NOT NULL,
            referred_user_id INTEGER NOT NULL,
            level INTEGER DEFAULT 1,
            lingzhi_reward INTEGER DEFAULT 0,
            reward_status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (referrer_id) REFERENCES users(id),
            FOREIGN KEY (referred_user_id) REFERENCES users(id),
            UNIQUE(referrer_id, referred_user_id)
        )
        ''')

        # 推荐码表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS referral_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referrer_id INTEGER NOT NULL,
            code TEXT UNIQUE NOT NULL,
            status TEXT DEFAULT 'active',
            expires_at TIMESTAMP,
            used_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (referrer_id) REFERENCES users(id)
        )
        ''')

        # 充值档位表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS recharge_tiers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price DECIMAL(10,2) NOT NULL,
            base_lingzhi INTEGER NOT NULL,
            bonus_lingzhi INTEGER NOT NULL,
            bonus_percentage INTEGER NOT NULL,
            partner_level INTEGER DEFAULT 0,
            benefits TEXT,
            status TEXT DEFAULT 'active',
            sort_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # 充值记录表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS recharge_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            tier_id INTEGER NOT NULL,
            order_no TEXT UNIQUE NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            base_lingzhi INTEGER NOT NULL,
            bonus_lingzhi INTEGER NOT NULL,
            total_lingzhi INTEGER NOT NULL,
            payment_method VARCHAR(20) DEFAULT 'online',
            payment_status VARCHAR(20) DEFAULT 'pending',
            payment_time TIMESTAMP,
            transaction_id TEXT,
            voucher_id INTEGER,
            audit_status VARCHAR(20),
            bank_info TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (tier_id) REFERENCES recharge_tiers(id)
        )
        ''')

        # 公司收款账户表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS company_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_name VARCHAR(200) NOT NULL,
            account_number VARCHAR(50) NOT NULL,
            bank_name VARCHAR(200) NOT NULL,
            bank_branch VARCHAR(200),
            company_name VARCHAR(200) NOT NULL,
            company_credit_code VARCHAR(50),
            account_type VARCHAR(20) NOT NULL DEFAULT 'primary',
            is_active BOOLEAN DEFAULT 1,
            sort_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # 转账凭证表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transfer_vouchers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recharge_record_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            image_url VARCHAR(500) NOT NULL,
            transfer_amount DECIMAL(10, 2) NOT NULL,
            transfer_time TIMESTAMP,
            transfer_account VARCHAR(200),
            remark TEXT,
            audit_status VARCHAR(20) DEFAULT 'pending',
            audit_user_id INTEGER,
            audit_time TIMESTAMP,
            audit_remark TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (recharge_record_id) REFERENCES recharge_records(id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (audit_user_id) REFERENCES admins(id)
        )
        ''')

        # 灵值消费记录表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS lingzhi_consumption_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            consumption_type TEXT NOT NULL,
            consumption_item TEXT,
            lingzhi_amount INTEGER NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')

        # 公司信息表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS company_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(200) NOT NULL,
            logo_url VARCHAR(500),
            description TEXT,
            address VARCHAR(500),
            phone VARCHAR(50),
            email VARCHAR(100),
            website VARCHAR(200),
            business_license VARCHAR(200),
            legal_representative VARCHAR(100),
            established_date DATE,
            registered_capital VARCHAR(100),
            business_scope TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # 公司项目表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS company_projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(200) NOT NULL,
            description TEXT,
            category VARCHAR(100),
            cover_image VARCHAR(500),
            budget DECIMAL(10, 2),
            start_date DATE,
            end_date DATE,
            status VARCHAR(20) DEFAULT 'planning',
            priority VARCHAR(20) DEFAULT 'medium',
            progress INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # 角色表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) UNIQUE NOT NULL,
            description TEXT,
            permissions TEXT,
            status VARCHAR(20) DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # 用户资源表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title VARCHAR(200) NOT NULL,
            content TEXT,
            category VARCHAR(100),
            cover_image VARCHAR(500),
            file_url VARCHAR(500),
            file_type VARCHAR(50),
            file_size INTEGER,
            tags TEXT,
            price DECIMAL(10, 2) DEFAULT 0,
            status VARCHAR(20) DEFAULT 'draft',
            is_public BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')

        # 分红池表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS dividend_pool (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(200) NOT NULL,
            description TEXT,
            amount DECIMAL(10, 2) DEFAULT 0,
            status VARCHAR(20) DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # 分红记录表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS dividend_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            pool_id INTEGER NOT NULL,
            amount DECIMAL(10, 2) NOT NULL,
            reason TEXT,
            status VARCHAR(20) DEFAULT 'pending',
            distributed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (pool_id) REFERENCES dividend_pool(id)
        )
        ''')

        # 智能体表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(200) NOT NULL,
            description TEXT,
            avatar_url VARCHAR(500),
            status VARCHAR(20) DEFAULT 'active',
            config TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # 知识库表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS knowledge_bases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(200) NOT NULL,
            description TEXT,
            status VARCHAR(20) DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # 修复新用户注册赠送灵值：将 total_lingzhi 为 0 的用户设置为 100
        # 修复所有灵值为0的用户（排除管理员创建的）
        cursor.execute('''
            UPDATE users
            SET total_lingzhi = 100
            WHERE total_lingzhi = 0
            AND id NOT IN (
                SELECT user_id FROM lingzhi_consumption_records
                WHERE consumption_type = 'admin_create'
            )
        ''')
        updated_count = cursor.rowcount
        
        print(f"[灵值修复] 检测到 {updated_count} 个灵值为0的用户")
        
        # 为修复的用户添加灵值消费记录（如果没有的话）
        if updated_count > 0:
            print(f"✅ 已修复 {updated_count} 个新用户的灵值（设置为100）")
            # 找出刚刚更新的用户ID
            cursor.execute('''
                SELECT id, username FROM users
                WHERE total_lingzhi = 100
                AND id NOT IN (
                    SELECT user_id FROM lingzhi_consumption_records
                    WHERE consumption_type = 'new_user_bonus'
                )
                AND id NOT IN (
                    SELECT user_id FROM lingzhi_consumption_records
                    WHERE consumption_type = 'admin_create'
                )
            ''')
            users_to_add_record = cursor.fetchall()
            
            print(f"[灵值修复] 需要添加消费记录的用户数: {len(users_to_add_record)}")
            
            for user_row in users_to_add_record:
                cursor.execute('''
                    INSERT INTO lingzhi_consumption_records (user_id, consumption_type, consumption_item, lingzhi_amount, description)
                    VALUES (?, 'new_user_bonus', 'new_user_bonus', 100, '新用户注册赠送（系统修复）')
                ''', (user_row['id'],))
                print(f"[灵值修复] 已为用户 {user_row['username']} (ID: {user_row['id']}) 添加灵值消费记录")
            
            print(f"✅ 已为 {len(users_to_add_record)} 个用户添加灵值消费记录")

        conn.commit()
        print("✅ 数据库初始化完成！")
        return True

    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 确保连接被关闭
        if cursor:
            cursor.close()
        if conn:
            try:
                conn.close()
                print("✅ 数据库连接已关闭")
            except Exception as e:
                print(f"⚠️  关闭数据库连接时出错: {e}")

# ============ 应用启动 ============

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 灵值生态园智能体系统 - V9.24.0")
    print("="*60 + "\n")

    # 清理数据库锁定文件
    print("🔧 清理数据库锁定文件...")
    try:
        from db_manager import cleanup_db_locks
        cleanup_db_locks()
    except Exception as e:
        print(f"⚠️  数据库锁定清理失败: {e}")

    # 初始化数据库
    init_db()

    # 初始化管理员账号
    try:
        from init_admin import init_admin
        init_admin()
    except Exception as e:
        print(f"⚠️  管理员账号初始化失败: {e}")

    # 启动应用
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    # 支持多种环境变量名（向后兼容）
    port_env = os.getenv('FLASK_PORT') or os.getenv('PORT') or '8080'
    port = int(port_env)
    debug = os.getenv('FLASK_DEBUG', 'False') == 'True'

    print(f"\n🌐 服务器启动: http://{host}:{port}")
    print(f"📝 调试模式: {debug}")
    print(f"🔧 工作目录: {os.getcwd()}\n")

    app.run(host=host, port=port, debug=debug)

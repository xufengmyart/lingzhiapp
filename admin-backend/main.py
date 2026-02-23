#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵值生态园 - 主入口文件
Main Entry Point for Lingzhi Ecosystem

Author: Coze Coding
Version: 1.0.0
Created: 2026-02-17
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到 Python 路径
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from app import app

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='灵值生态园后端服务')
    parser.add_argument('--host', default='0.0.0.0', help='服务器地址')
    parser.add_argument('--port', type=int, default=8080, help='服务器端口')
    parser.add_argument('--debug', action='store_true', help='调试模式')
    parser.add_argument('--workers', type=int, default=1, help='工作进程数')

    args = parser.parse_args()

    print('=' * 50)
    print('灵值生态园 - 后端服务启动中')
    print('=' * 50)
    print(f'环境: {os.getenv("FLASK_ENV", "production")}')
    print(f'地址: http://{args.host}:{args.port}')
    print(f'调试: {args.debug}')
    print('=' * 50)

    if args.debug:
        app.run(host=args.host, port=args.port, debug=True)
    else:
        # 生产环境使用多进程
        from werkzeug.serving import run_simple

        def application(environ, start_response):
            return app(environ, start_response)

        run_simple(
            args.host,
            args.port,
            application,
            use_reloader=False,
            use_debugger=False,
            use_evalex=False,
            threaded=True
        )

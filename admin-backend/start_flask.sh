#!/bin/bash
# 启动Flask服务脚本

cd /workspace/projects/admin-backend

# 设置环境变量
export PYTHONUNBUFFERED=1

# 启动Flask服务
python3 -c "
import sys
import os
sys.path.insert(0, os.getcwd())

# 导入Flask应用
from app import app, backup_database, init_default_data

# 备份数据库
print('正在备份数据库...')
backup_database()

# 初始化默认数据
init_default_data()

# 添加自定义响应头
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Max-Age', '86400')
    return response

# 启动服务
print('启动Flask服务，监听8080端口...')
app.run(host='0.0.0.0', port=8080, debug=False)
" > /tmp/flask.log 2>&1 &

sleep 5

# 检查服务状态
if netstat -tlnp 2>/dev/null | grep 8080 > /dev/null; then
    echo 'Flask服务已启动，监听8080端口'
    netstat -tlnp 2>/dev/null | grep 8080
else
    echo 'Flask服务启动失败'
    cat /tmp/flask.log | tail -n 20
fi

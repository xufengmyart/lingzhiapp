#!/bin/bash
# 灵值生态园后端服务启动脚本

# 设置 Coze 环境变量
export COZE_WORKLOAD_IDENTITY_API_KEY='WU9RNGFQTmZTc3VnbnRCMmsyWUtDcDZHOWJMa0g5ZVk6NVN5cHNRbkNidjFzWHNEVnJ4UTZKQlN1SUxYMlU3ZEtidVRXbDYwWDFyZW9sdmhQbTU1QVdQaVJHcVo4b1BoWA=='
export COZE_INTEGRATION_MODEL_BASE_URL='https://integration.coze.cn/api/v3'
export COZE_PROJECT_ID='7597768668038643746'
export COZE_PROJECT_SPACE_ID='7597311229212246070'

cd /var/www/backend

# 启动服务
nohup python3 app.py > backend.log 2>&1 &

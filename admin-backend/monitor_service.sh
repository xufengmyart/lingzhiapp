#!/bin/bash
# 服务监控脚本

while true; do
    # 检查服务是否运行
    if ! ps aux | grep -q "[p]ython3 app.py"; then
        echo "⚠️  服务未运行，正在重启..."
        cd /workspace/projects/admin-backend
        nohup python3 app.py > /tmp/production.log 2>&1 &
        sleep 10
        echo "✅ 服务已重启"
    fi

    # 每60秒检查一次
    sleep 60
done

#!/bin/bash
# 强制清理数据库锁定并重启服务

cd /app/meiyueart-backend

echo "=== 强制数据库锁定清理脚本 ==="
echo ""

# 1. 停止所有Python进程
echo "1. 停止所有Python进程..."
killall -9 python python3 2>/dev/null || true
killall -9 gunicorn uwsgi 2>/dev/null || true
sleep 3

# 2. 检查并清理数据库锁定
echo "2. 检查数据库锁定..."
if [ -f "data/lingzhi_ecosystem.db" ]; then
    # 检查是否有进程锁定数据库
    if lsof +D data > /dev/null 2>&1; then
        echo "发现数据库被锁定，正在清理..."
        lsof +D data 2>/dev/null
        PIDS=$(lsof +D data 2>/dev/null | awk 'NR>1 {print $2}' | sort -u)
        for PID in $PIDS; do
            echo "终止进程: $PID"
            kill -9 $PID 2>/dev/null || true
        done
        sleep 2
    fi

    # 删除所有SQLite锁定文件
    echo "删除锁定文件..."
    rm -f data/*.db-wal data/*.db-shm data/*-journal data/*.lock
    echo "✅ 锁定文件已删除"
fi

# 3. 检查数据库文件权限
echo "3. 检查数据库文件权限..."
if [ -f "data/lingzhi_ecosystem.db" ]; then
    ls -l data/lingzhi_ecosystem.db
    chmod 664 data/lingzhi_ecosystem.db
    chown root:root data/lingzhi_ecosystem.db
fi

# 4. 启动服务
echo "4. 启动服务..."
nohup python app.py > /var/log/meiyueart-backend/app.log 2>&1 &
sleep 5

# 5. 检查服务状态
echo "5. 检查服务状态..."
if ps aux | grep -v grep | grep "python.*app.py" > /dev/null; then
    echo "✅ 服务启动成功"
else
    echo "❌ 服务启动失败"
    echo "查看日志:"
    tail -n 30 /var/log/meiyueart-backend/app.log
fi

echo ""
echo "=== 清理完成 ==="

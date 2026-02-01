#!/bin/bash

echo "=========================================="
echo "  灵值生态园 - 服务状态自检工具"
echo "=========================================="
echo ""

# 检查端口
echo "[1] 端口监听状态:"
echo "----------------------------------------"
if netstat -tuln 2>/dev/null | grep -E ':80 ' > /dev/null; then
    echo "  ✓ 端口 80 (Nginx) - 正在监听"
else
    echo "  ✗ 端口 80 (Nginx) - 未监听"
fi

if netstat -tuln 2>/dev/null | grep -E ':8001 ' > /dev/null; then
    echo "  ✓ 端口 8001 (Flask) - 正在监听"
else
    echo "  ✗ 端口 8001 (Flask) - 未监听"
fi

if netstat -tuln 2>/dev/null | grep -E ':8080 ' > /dev/null; then
    echo "  ✓ 端口 8080 (HTTP) - 正在监听"
else
    echo "  ✗ 端口 8080 (HTTP) - 未监听"
fi

if netstat -tuln 2>/dev/null | grep -E ':9000 ' > /dev/null; then
    echo "  ✓ 端口 9000 (FaaS) - 正在监听"
else
    echo "  ✗ 端口 9000 (FaaS) - 未监听"
fi

# 检查Nginx
echo ""
echo "[2] Nginx服务状态:"
echo "----------------------------------------"
if command -v systemctl &> /dev/null; then
    if systemctl is-active --quiet nginx; then
        echo "  ✓ Nginx服务运行中"
        # 测试Nginx响应
        if curl -s -I http://127.0.0.1/ | grep "HTTP/1.1 200" > /dev/null; then
            echo "  ✓ Nginx响应正常 (HTTP 200)"
        else
            echo "  ✗ Nginx响应异常"
        fi
    else
        echo "  ✗ Nginx服务未运行"
    fi
else
    echo "  ! systemctl命令不可用，跳过检测"
fi

# 检查Flask后端
echo ""
echo "[3] Flask后端状态:"
echo "----------------------------------------"
if curl -s http://127.0.0.1:8001/api/health > /dev/null 2>&1; then
    echo "  ✓ Flask后端运行正常"
    RESPONSE=$(curl -s http://127.0.0.1:8001/api/health)
    echo "  响应: $RESPONSE"
else
    echo "  ✗ Flask后端未响应"
fi

# 检查FaaS服务
echo ""
echo "[4] FaaS服务状态:"
echo "----------------------------------------"
if curl -s http://127.0.0.1:9000/health > /dev/null 2>&1; then
    echo "  ✓ FaaS服务运行正常"
    RESPONSE=$(curl -s http://127.0.0.1:9000/health)
    echo "  响应: $RESPONSE"
else
    echo "  ✗ FaaS服务未响应"
fi

# 检查HTTP服务器
echo ""
echo "[5] HTTP服务器状态:"
echo "----------------------------------------"
if curl -s -I http://127.0.0.1:8080/test.html | grep "HTTP/1.0 200" > /dev/null; then
    echo "  ✓ HTTP服务器运行正常"
    echo "  测试页面: http://127.0.0.1:8080/test.html"
else
    echo "  ✗ HTTP服务器未响应"
fi

# 检查静态文件
echo ""
echo "[6] 静态文件检查:"
echo "----------------------------------------"
if [ -f "/workspace/projects/public/index.html" ]; then
    echo "  ✓ 前端页面存在"
else
    echo "  ✗ 前端页面缺失"
fi

if [ -d "/workspace/projects/public/assets" ]; then
    ASSET_COUNT=$(find /workspace/projects/public/assets -type f | wc -l)
    echo "  ✓ 资源目录存在 ($ASSET_COUNT 个文件)"
else
    echo "  ✗ 资源目录缺失"
fi

# 检查进程
echo ""
echo "[7] 进程状态:"
echo "----------------------------------------"
PYTHON_COUNT=$(ps aux | grep -E "python.*main.py|flask|uvicorn" | grep -v grep | wc -l)
if [ $PYTHON_COUNT -gt 0 ]; then
    echo "  ✓ 发现 $PYTHON_COUNT 个Python进程"
    ps aux | grep -E "python.*main.py|flask|uvicorn" | grep -v grep | head -3 | while read line; do
        echo "    - $line"
    done
else
    echo "  ✗ 未发现Python进程"
fi

NGINX_COUNT=$(ps aux | grep nginx | grep -v grep | wc -l)
if [ $NGINX_COUNT -gt 0 ]; then
    echo "  ✓ 发现 $NGINX_COUNT 个Nginx进程"
else
    echo "  ✗ 未发现Nginx进程"
fi

# 网络连通性测试
echo ""
echo "[8] 网络连通性:"
echo "----------------------------------------"
if command -v ping &> /dev/null; then
    if ping -c 1 -W 2 8.8.8.8 > /dev/null 2>&1; then
        echo "  ✓ 外网连通正常"
    else
        echo "  ✗ 外网连通异常"
    fi
else
    echo "  ! ping命令不可用，跳过检测"
fi

# 防火墙状态
echo ""
echo "[9] 防火墙状态:"
echo "----------------------------------------"
if command -v ufw &> /dev/null; then
    UFW_STATUS=$(ufw status 2>/dev/null | head -1)
    echo "  UFW状态: $UFW_STATUS"
else
    echo "  ! UFW未安装或不可用"
fi

# 总结
echo ""
echo "=========================================="
echo "  自检完成"
echo "=========================================="
echo ""
echo "访问地址："
echo "  - 本地访问: http://127.0.0.1"
echo "  - Flask后端: http://127.0.0.1:8001"
echo "  - FaaS服务: http://127.0.0.1:9000"
echo "  - 测试页面: http://127.0.0.1:8080/test.html"
echo ""
echo "公网访问："
echo "  - IP访问: http://123.56.142.143 (需要开放80端口)"
echo "  - 域名访问: https://f8ab8c28-f515-4fa3-9fb4-0ca0c3a0d34f.dev.coze.site/"
echo ""

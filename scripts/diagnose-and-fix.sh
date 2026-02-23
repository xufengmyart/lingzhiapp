#!/bin/bash

# 灵值生态园 - 快速诊断和修复脚本
# 用途：快速诊断和修复服务器问题

set -e

echo "========================================="
echo "灵值生态园 - 快速诊断和修复"
echo "========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 配置变量
FLASK_PORT=8080
NGINX_PORT_HTTP=80
NGINX_PORT_HTTPS=443

# 诊断函数
check_service() {
    local service_name=$1
    local service_port=$2

    echo -n "检查 $service_name (端口 $service_port)... "

    if lsof -Pi :$service_port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${GREEN}[运行中]${NC}"
        return 0
    else
        echo -e "${RED}[未运行]${NC}"
        return 1
    fi
}

# 1. 检查 Nginx
echo "========================================="
echo "[1] 检查 Nginx 服务"
echo "========================================="

check_service "Nginx HTTP" $NGINX_PORT_HTTP
nginx_http_status=$?

check_service "Nginx HTTPS" $NGINX_PORT_HTTPS
nginx_https_status=$?

if [ $nginx_http_status -eq 0 ] && [ $nginx_https_status -eq 0 ]; then
    echo -e "${GREEN}[OK]${NC} Nginx 服务正常"
else
    echo -e "${RED}[ERROR]${NC} Nginx 服务异常"
    echo ""
    echo "尝试启动 Nginx..."
    systemctl start nginx
    sleep 2
    check_service "Nginx HTTP" $NGINX_PORT_HTTP
fi

echo ""

# 2. 检查 Flask
echo "========================================="
echo "[2] 检查 Flask 服务"
echo "========================================="

check_service "Flask" $FLASK_PORT
flask_status=$?

if [ $flask_status -eq 0 ]; then
    echo -e "${GREEN}[OK]${NC} Flask 服务正常"

    # 测试健康检查
    echo -n "测试健康检查接口... "
    if curl -f http://localhost:$FLASK_PORT/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}[正常]${NC}"
    else
        echo -e "${YELLOW}[异常]${NC} 健康检查接口返回错误"
    fi
else
    echo -e "${RED}[ERROR]${NC} Flask 服务未运行"
    echo ""
    echo "尝试启动 Flask 服务..."
    systemctl start flask-app || pm2 restart flask-app || python3 backend/app.py &
    sleep 3
    check_service "Flask" $FLASK_PORT
fi

echo ""

# 3. 检查端口占用
echo "========================================="
echo "[3] 检查端口占用情况"
echo "========================================="

echo "端口 80 (Nginx HTTP):"
lsof -i :80 2>/dev/null | grep LISTEN || echo -e "${YELLOW}[空闲]${NC}"

echo ""
echo "端口 443 (Nginx HTTPS):"
lsof -i :443 2>/dev/null | grep LISTEN || echo -e "${YELLOW}[空闲]${NC}"

echo ""
echo "端口 8080 (Flask):"
lsof -i :8080 2>/dev/null | grep LISTEN || echo -e "${YELLOW}[空闲]${NC}"

echo ""

# 4. 检查 SSL 证书
echo "========================================="
echo "[4] 检查 SSL 证书"
echo "========================================="

SSL_CERT_DIR="/etc/nginx/ssl"
if [ -f "$SSL_CERT_DIR/meiyueart.com.crt" ] && [ -f "$SSL_CERT_DIR/meiyueart.com.key" ]; then
    echo -e "${GREEN}[OK]${NC} SSL 证书存在"

    # 检查证书有效期
    echo "证书信息："
    openssl x509 -in "$SSL_CERT_DIR/meiyueart.com.crt" -noout -dates 2>/dev/null || echo -e "${YELLOW}[无法读取证书信息]${NC}"
else
    echo -e "${RED}[ERROR]${NC} SSL 证书不存在"
    echo ""
    echo "生成自签名证书..."
    mkdir -p $SSL_CERT_DIR
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$SSL_CERT_DIR/meiyueart.com.key" \
        -out "$SSL_CERT_DIR/meiyueart.com.crt" \
        -subj "/C=CN/ST=Beijing/L=Beijing/O=MeiyueArt/CN=meiyueart.com"
    echo -e "${GREEN}[OK]${NC} SSL 证书生成完成"
fi

echo ""

# 5. 测试外网访问
echo "========================================="
echo "[5] 测试外网访问"
echo "========================================="

PUBLIC_IP=$(curl -s ifconfig.me)
echo "公网 IP: $PUBLIC_IP"

echo ""
echo -n "测试 HTTP 访问... "
if curl -f http://localhost/ > /dev/null 2>&1; then
    echo -e "${GREEN}[正常]${NC}"
else
    echo -e "${RED}[失败]${NC}"
fi

echo -n "测试 HTTPS 访问... "
if curl -kf https://localhost/ > /dev/null 2>&1; then
    echo -e "${GREEN}[正常]${NC}"
else
    echo -e "${RED}[失败]${NC}"
fi

echo -n "测试 API 访问... "
if curl -kf https://localhost/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}[正常]${NC}"
else
    echo -e "${RED}[失败]${NC}"
fi

echo ""

# 6. 查看服务状态
echo "========================================="
echo "[6] 服务状态汇总"
echo "========================================="

echo "Nginx 状态："
systemctl status nginx --no-pager -l | head -5

echo ""
echo "Flask 状态："
systemctl status flask-app --no-pager -l 2>/dev/null | head -5 || echo "Flask 服务未配置为 systemd 服务"

echo ""

# 7. 建议
echo "========================================="
echo "[7] 诊断完成 - 建议"
echo "========================================="

if [ $nginx_http_status -eq 0 ] && [ $nginx_https_status -eq 0 ] && [ $flask_status -eq 0 ]; then
    echo -e "${GREEN}[状态良好]${NC} 所有服务运行正常"
    echo ""
    echo "访问地址："
    echo "  HTTP:  http://$PUBLIC_IP"
    echo "  HTTPS: https://$PUBLIC_IP"
else
    echo -e "${YELLOW}[发现问题]${NC} 部分服务异常，请检查上述日志"
    echo ""
    echo "修复建议："
    if [ $flask_status -ne 0 ]; then
        echo "  1. 重启 Flask: systemctl restart flask-app"
    fi
    if [ $nginx_http_status -ne 0 ] || [ $nginx_https_status -ne 0 ]; then
        echo "  2. 重启 Nginx: systemctl restart nginx"
    fi
fi

echo ""
echo "========================================="
echo "查看日志："
echo "  Nginx:  tail -f /var/log/nginx/error.log"
echo "  Flask:  journalctl -u flask-app -f"
echo "========================================="

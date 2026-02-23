#!/bin/bash
# 在服务器上执行此脚本

echo "1. 检查Nginx配置"
cat /etc/nginx/sites-available/meiyueart.com

echo -e "\n2. 检查前端文件"
ls -lh /var/www/html/

echo -e "\n3. 检查index.html"
cat /var/www/html/index.html | grep -i api

echo -e "\n4. 检查前端JS文件"
ls -lh /var/www/html/assets/

echo -e "\n5. 检查Nginx日志"
tail -20 /var/log/nginx/error.log

#!/usr/bin/env python3
import os
import sys

sys.path.insert(0, '/workspace/projects/src')

from coze_coding_dev_sdk.s3 import S3SyncStorage

storage = S3SyncStorage(
    endpoint_url=os.getenv("COZE_BUCKET_ENDPOINT_URL"),
    access_key="",
    secret_key="",
    bucket_name=os.getenv("COZE_BUCKET_NAME"),
    region="cn-beijing",
)

# 最终部署脚本
script_content = """#!/bin/bash

echo "🌿 生态之梦风格 - 最终部署..."

cd /root
wget -q https://coze-coding-project.tos.coze.site/public_final.tar_522f5841.gz -O public.tar.gz

if [ $? -ne 0 ]; then
    echo "❌ 下载失败"
    exit 1
fi

echo "✅ 下载完成"

rm -rf /var/www/frontend/*
tar -xzf public.tar.gz -C /var/www/frontend/

if [ $? -ne 0 ]; then
    echo "❌ 解压失败"
    exit 1
fi

chown -R root:root /var/www/frontend
chmod -R 755 /var/www/frontend

systemctl reload nginx

if [ $? -ne 0 ]; then
    echo "❌ Nginx 重启失败"
    exit 1
fi

rm -f public.tar.gz

echo ""
echo "✅ 部署完成！"
echo "📱 访问地址: https://meiyueart.com"
echo "💡 请清除浏览器缓存后访问"
echo ""
echo "🎯 功能清单："
echo "  ✅ 生态之梦风格（绿色→琥珀金渐变）"
echo "  ✅ 无风格选择器"
echo "  ✅ 无顶部动画"
echo "  ✅ 不换行原则"
echo "  ✅ 登录与微信登录分离（双按钮）"
echo "  ✅ 忘记密码功能"
echo "  ✅ 100价值确定性/T+1快速到账/0手续费（光扫动画）"
echo "  ✅ 用户登录已修复"
echo "  ✅ 注册页推荐人必填（关系锁定）"
"""

key = storage.upload_file(
    file_content=script_content.encode('utf-8'),
    file_name='deploy_final_ecosystem.sh',
    content_type='text/x-shellscript',
)

print(f"✅ 上传成功！Key: {key}")
print(f"URL: https://coze-coding-project.tos.coze.site/{key}")

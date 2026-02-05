#!/usr/bin/env python3
import sys
sys.path.insert(0, '/workspace/projects/src')
from coze_coding_dev_sdk.s3 import S3SyncStorage
import os

storage = S3SyncStorage(
    endpoint_url=os.getenv('COZE_BUCKET_ENDPOINT_URL'),
    access_key='',
    secret_key='',
    bucket_name=os.getenv('COZE_BUCKET_NAME'),
    region='cn-beijing',
)

# 生成24小时有效的签名URL
signed_url = storage.generate_presigned_url(
    key='public_v3.tar_3e884757.gz',
    expire_time=86400  # 24小时
)

print("✅ 长期有效URL（24小时）：")
print(signed_url)

# 生成部署命令
deploy_cmd = f'''cd /root && wget -O public.tar.gz "{signed_url}" && rm -rf /var/www/frontend/* && tar -xzf public.tar.gz -C /var/www/frontend/ && chown -R root:root /var/www/frontend && chmod -R 755 /var/www/frontend && systemctl reload nginx && rm -f public.tar.gz && echo "✅ 部署完成！清除缓存后访问 https://meiyueart.com"'''

print("\n" + "="*80)
print("🚀 部署命令（复制到服务器执行）：")
print("="*80)
print(deploy_cmd)
print("="*80)

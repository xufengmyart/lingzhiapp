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

# 读取部署脚本
with open('/workspace/projects/full_deploy.sh', 'r') as f:
    script_content = f.read()

# 上传脚本
key = storage.upload_file(
    file_content=script_content.encode('utf-8'),
    file_name='full_deploy_ecosystem.sh',
    content_type='text/x-shellscript',
)

print(f"✅ 部署脚本已上传")
print(f"Key: {key}")

# 生成签名URL（24小时有效）
signed_url = storage.generate_presigned_url(
    key=key,
    expire_time=86400
)

print(f"\n🚀 服务器执行命令：")
print("="*80)
print(f"curl -fsSL '{signed_url}' | bash")
print("="*80)

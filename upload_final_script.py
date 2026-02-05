#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, '/workspace/projects/src')
from coze_coding_dev_sdk.s3 import S3SyncStorage

storage = S3SyncStorage(
    endpoint_url=os.getenv('COZE_BUCKET_ENDPOINT_URL'),
    access_key='',
    secret_key='',
    bucket_name=os.getenv('COZE_BUCKET_NAME'),
    region='cn-beijing',
)

# 上传部署脚本
with open('/workspace/projects/final_pwa_deploy.sh', 'r') as f:
    script_key = storage.upload_file(
        file_content=f.read().encode('utf-8'),
        file_name='final_pwa_deploy.sh',
        content_type='text/x-shellscript',
    )
    print(f'✅ 部署脚本: {script_key}')

# 生成部署命令
script_signed_url = storage.generate_presigned_url(
    key=script_key,
    expire_time=86400
)
print(f'\n🚀 最终部署命令:')
print(f'curl -fsSL \"{script_signed_url}\" | bash')

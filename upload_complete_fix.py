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

# 上传深度诊断脚本
with open('/workspace/projects/deep_diagnose.sh', 'r') as f:
    diag_key = storage.upload_file(
        file_content=f.read().encode('utf-8'),
        file_name='deep_diagnose.sh',
        content_type='text/x-shellscript',
    )
    print(f'✅ 深度诊断脚本: {diag_key}')

# 上传完整修复脚本
with open('/workspace/projects/complete_fix.sh', 'r') as f:
    fix_key = storage.upload_file(
        file_content=f.read().encode('utf-8'),
        file_name='complete_fix.sh',
        content_type='text/x-shellscript',
    )
    print(f'✅ 完整修复脚本: {fix_key}')

# 生成命令
diag_url = storage.generate_presigned_url(key=diag_key, expire_time=86400)
fix_url = storage.generate_presigned_url(key=fix_key, expire_time=86400)

print(f'\n🔍 深度诊断命令（如果需要）:')
print(f'curl -fsSL \"{diag_url}\" | bash')

print(f'\n🚀 完整修复命令（推荐）:')
print(f'curl -fsSL \"{fix_url}\" | bash')

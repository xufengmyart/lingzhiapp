#!/usr/bin/env python3
import os
import sys

sys.path.insert(0, '/workspace/projects/src')
from coze_coding_dev_sdk.s3 import S3SyncStorage

storage = S3SyncStorage(
    endpoint_url=os.getenv('COZE_BUCKET_ENDPOINT_URL'),
    access_key='',
    secret_key='',
    bucket_name=os.getenv('COZE_BUCKET_NAME'),
    region='cn-beijing',
)

# 上传诊断脚本
with open('/workspace/projects/diagnose_500_error.sh', 'r') as f:
    diag_key = storage.upload_file(
        file_content=f.read().encode('utf-8'),
        file_name='diagnose_500_error.sh',
        content_type='text/x-shellscript',
    )
    print(f'✅ 诊断脚本: {diag_key}')

# 上传修复脚本
with open('/workspace/projects/fix_500_error.sh', 'r') as f:
    fix_key = storage.upload_file(
        file_content=f.read().encode('utf-8'),
        file_name='fix_500_error.sh',
        content_type='text/x-shellscript',
    )
    print(f'✅ 修复脚本: {fix_key}')

# 生成诊断命令
diag_url = storage.generate_presigned_url(key=diag_key, expire_time=86400)
print(f'\n🔍 诊断命令（服务器执行）：')
print(f'curl -fsSL "{diag_url}" | bash')

# 生成修复命令
fix_url = storage.generate_presigned_url(key=fix_key, expire_time=86400)
print(f'\n🔧 修复命令（服务器执行）：')
print(f'curl -fsSL "{fix_url}" | bash')

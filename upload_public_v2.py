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

file_path = '/tmp/public_v2.tar.gz'
file_name = 'public_v2.tar.gz'

with open(file_path, 'rb') as f:
    key = storage.stream_upload_file(
        fileobj=f,
        file_name=file_name,
        content_type='application/gzip',
    )

print(f"✅ 上传成功！Key: {key}")
print(f"URL: https://coze-coding-project.tos.coze.site/{key}")

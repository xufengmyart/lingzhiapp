#!/usr/bin/env python3
"""
上传部署脚本到对象存储
"""
import os
from pathlib import Path
from coze_coding_dev_sdk.s3 import S3SyncStorage

# 初始化对象存储
storage = S3SyncStorage(
    endpoint_url=os.getenv("COZE_BUCKET_ENDPOINT_URL"),
    access_key="",
    secret_key="",
    bucket_name=os.getenv("COZE_BUCKET_NAME"),
    region="cn-beijing",
)

# 读取部署脚本
script_path = Path("deploy_frontend_from_storage.sh")
with open(script_path, 'r', encoding='utf-8') as f:
    script_content = f.read()

# 上传脚本
key = storage.upload_file(
    file_content=script_content.encode('utf-8'),
    file_name="deploy_frontend_from_storage.sh",
    content_type="text/plain; charset=utf-8",
)

print(f"✅ 部署脚本已上传")
print(f"\n🚀 在服务器上执行以下命令：\n")

# 构建公开URL
public_url = f"https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/{key}?sign=1770417491-0-0-0"

print(f"curl -fsSL \"{public_url}\" | bash")
print(f"\n或者手动下载后执行：")
print(f"wget -O deploy.sh \"{public_url}\" && chmod +x deploy.sh && ./deploy.sh")

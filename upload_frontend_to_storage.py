#!/usr/bin/env python3
"""
上传前端构建产物到对象存储
"""
import os
import sys
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

# 前端构建产物目录
BUILD_DIR = Path("/workspace/projects/public")

# 对象存储前缀
STORAGE_PREFIX = "frontend/"

def upload_file(file_path: Path, storage_path: str):
    """上传单个文件"""
    print(f"📤 上传: {file_path.name} -> {storage_path}")

    # 确定Content-Type
    content_type = None
    if file_path.suffix == '.html':
        content_type = 'text/html; charset=utf-8'
    elif file_path.suffix == '.css':
        content_type = 'text/css; charset=utf-8'
    elif file_path.suffix == '.js':
        content_type = 'application/javascript; charset=utf-8'
    elif file_path.suffix == '.svg':
        content_type = 'image/svg+xml'
    elif file_path.suffix == '.json':
        content_type = 'application/json'
    elif file_path.suffix == '.webmanifest':
        content_type = 'application/manifest+json'

    # 读取文件内容
    with open(file_path, 'rb') as f:
        file_content = f.read()

    # 上传
    key = storage.upload_file(
        file_content=file_content,
        file_name=storage_path,
        content_type=content_type,
    )

    return key

def upload_directory(directory: Path, prefix: str = ""):
    """递归上传目录"""
    if not directory.exists():
        print(f"❌ 目录不存在: {directory}")
        return

    print(f"📂 扫描目录: {directory}")

    uploaded_files = []
    for item in sorted(directory.rglob("*")):
        if item.is_file():
            # 计算相对路径
            relative_path = item.relative_to(directory)
            storage_path = f"{prefix}{relative_path}"

            # 上传文件
            key = upload_file(item, storage_path)
            uploaded_files.append(key)

    return uploaded_files

def main():
    print("=" * 60)
    print("🚀 开始上传前端构建产物到对象存储")
    print("=" * 60)

    # 上传整个public目录
    uploaded_files = upload_directory(BUILD_DIR, STORAGE_PREFIX)

    print("\n" + "=" * 60)
    print(f"✅ 上传完成！共上传 {len(uploaded_files)} 个文件")
    print("=" * 60)

    # 生成下载URL列表
    print("\n📋 文件列表：")
    for key in sorted(uploaded_files):
        print(f"  - {key}")

    return uploaded_files

if __name__ == "__main__":
    main()

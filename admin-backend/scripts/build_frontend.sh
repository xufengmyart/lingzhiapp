#!/bin/bash

cd /workspace/projects/web-app

echo "开始构建前端..."
npm run build

if [ $? -eq 0 ]; then
    echo "✅ 前端构建成功"
    ls -lh dist/
else
    echo "❌ 前端构建失败"
    exit 1
fi

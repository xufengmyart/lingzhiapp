#!/bin/bash

# 媄月商业艺术 - 权限管理系统启动脚本

echo "========================================="
echo "  媄月商业艺术 - 权限管理系统"
echo "  版本：v1.0"
echo "========================================="
echo ""

# 检查Python版本
echo "检查Python版本..."
python3 --version
if [ $? -ne 0 ]; then
    echo "错误：未安装Python3"
    exit 1
fi
echo ""

# 检查pip
echo "检查pip..."
pip3 --version
if [ $? -ne 0 ]; then
    echo "错误：未安装pip3"
    exit 1
fi
echo ""

# 安装依赖
echo "安装依赖..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "错误：依赖安装失败"
    exit 1
fi
echo "依赖安装完成！"
echo ""

# 初始化数据库
echo "初始化数据库..."
python3 init_data.py
if [ $? -ne 0 ]; then
    echo "错误：数据库初始化失败"
    exit 1
fi
echo "数据库初始化完成！"
echo ""

# 启动后端服务
echo "启动后端服务..."
echo "后端服务将在 http://localhost:8000 启动"
echo "API文档：http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

python3 api.py

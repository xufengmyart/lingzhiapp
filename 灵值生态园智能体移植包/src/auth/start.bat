@echo off
chcp 65001 > nul
title 媄月商业艺术 - 权限管理系统

echo =========================================
echo   媄月商业艺术 - 权限管理系统
echo   版本：v1.0
echo =========================================
echo.

REM 检查Python版本
echo 检查Python版本...
python --version
if errorlevel 1 (
    echo 错误：未安装Python
    pause
    exit /b 1
)
echo.

REM 检查pip
echo 检查pip...
pip --version
if errorlevel 1 (
    echo 错误：未安装pip
    pause
    exit /b 1
)
echo.

REM 安装依赖
echo 安装依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo 错误：依赖安装失败
    pause
    exit /b 1
)
echo 依赖安装完成！
echo.

REM 初始化数据库
echo 初始化数据库...
python init_data.py
if errorlevel 1 (
    echo 错误：数据库初始化失败
    pause
    exit /b 1
)
echo 数据库初始化完成！
echo.

REM 启动后端服务
echo 启动后端服务...
echo 后端服务将在 http://localhost:8000 启动
echo API文档：http://localhost:8000/docs
echo 前端界面：请用浏览器打开 index.html 文件
echo.
echo 按 Ctrl+C 停止服务
echo.

python api.py

pause

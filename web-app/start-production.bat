@echo off
REM 灵值生态智能体 Web APP 生产部署脚本 (Windows)

echo ========================================
echo 灵值生态智能体 Web APP 生产部署
echo ========================================
echo.

REM 配置
set PORT=3000
set LOG_DIR=logs
set LOG_FILE=%LOG_DIR%\web-app-production.log

REM 颜色设置（Windows CMD 不支持颜色，使用文本标识）
echo 配置信息:
echo   端口: %PORT%
echo   日志文件: %LOG_FILE%
echo.

REM 创建日志目录
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM 检查构建产物
if not exist "dist" (
    echo 错误: dist 目录不存在！
    echo 请先运行: npm run build
    pause
    exit /b 1
)

REM 停止现有服务器
echo 停止现有服务器...
taskkill /F /IM node.exe /FI "WINDOWTITLE eq production-server*" 2>nul
timeout /t 2 /nobreak >nul

REM 启动生产服务器
echo 启动生产服务器...
start "production-server" /MIN node production-server.js > "%LOG_FILE%" 2>&1

REM 等待服务器启动
echo 等待服务器启动...
timeout /t 3 /nobreak >nul

REM 检查服务器是否运行
tasklist /FI "IMAGENAME eq node.exe" | find /I "node.exe" >nul
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo 服务器已成功启动！
    echo ========================================
    echo   地址: http://localhost:%PORT%
    echo   日志文件: %LOG_FILE%
    echo.
    echo 查看日志:
    echo   type %LOG_FILE%
    echo.
    echo 停止服务器:
    echo   taskkill /F /IM node.exe
    echo.
    echo 或打开另一个命令窗口，输入:
    echo   type %LOG_FILE%
    echo.
) else (
    echo.
    echo ========================================
    echo 服务器启动失败！
    echo ========================================
    echo 请检查日志: %LOG_FILE%
    echo.
    pause
    exit /b 1
)

pause

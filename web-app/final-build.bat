@echo off
chcp 65001 >nul
echo ========================================
echo 灵值生态园完整构建和部署
echo ========================================
echo.

REM 停止所有Node.js进程
echo [1/6] 停止现有服务器...
taskkill /F /IM node.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo [完成]
echo.

REM 清理所有构建产物和缓存
echo [2/6] 清理构建产物和缓存...
if exist "dist" (
    rmdir /s /q dist
    echo 已删除 dist 目录
)
if exist "node_modules\.vite" (
    rmdir /s /q node_modules\.vite
    echo 已清理 Vite 缓存
)
echo [完成]
echo.

REM 重新安装依赖
echo [3/6] 重新安装依赖（确保完整）...
echo 这可能需要2-3分钟，请耐心等待...
echo.
npm install
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [错误] 依赖安装失败！
    echo 请检查网络连接或使用国内镜像：
    echo npm config set registry https://registry.npmmirror.com
    pause
    exit /b 1
)
echo [完成]
echo.

REM 构建项目（包含PWA和Mock API）
echo [4/6] 构建项目（包含PWA配置和Mock API支持）...
echo 正在编译TypeScript和构建生产版本...
echo.
npm run build
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [错误] 项目构建失败！
    pause
    exit /b 1
)
echo [完成]
echo.

REM 验证构建产物
echo [5/6] 验证构建产物...
echo 检查关键文件...
if exist "dist\index.html" (
    echo [√] index.html
) else (
    echo [×] index.html 缺失
)

if exist "dist\manifest.json" (
    echo [√] manifest.json (PWA)
) else (
    echo [×] manifest.json 缺失
)

if exist "dist\sw.js" (
    echo [√] sw.js (Service Worker)
) else (
    echo [×] sw.js 缺失
)

if exist "dist\assets\index-*.js" (
    echo [√] JavaScript 文件
) else (
    echo [×] JavaScript 文件缺失
)

if exist "dist\assets\index-*.css" (
    echo [√] CSS 样式文件
) else (
    echo [×] CSS 样式文件缺失
)
echo [完成]
echo.

REM 启动服务器
echo [6/6] 启动生产服务器...
echo.
echo ========================================
echo 服务器启动成功！
echo ========================================
echo.
echo 📱 访问地址：
echo    http://localhost:3000
echo.
echo 📱 PWA安装（电脑）：
echo    1. 访问 http://localhost:3000
echo    2. 点击地址栏右侧的安装图标
echo    3. 点击"安装"
echo.
echo 📱 PWA安装（手机）：
echo    1. 用手机访问应用地址
echo    2. 添加到主屏幕
echo.
echo ✨ 功能特点：
echo    - 完整的用户界面
echo    - 智能对话功能
echo    - 经济模型计算
echo    - 用户旅程管理
echo    - 合伙人申请
echo    - PWA可安装
echo    - Mock数据支持（无需后端）
echo.
echo 📊 测试账号：
echo    用户名：任意
echo    密码：任意
echo    （使用Mock API，任意账号都可登录）
echo.
echo 查看日志：tail -f logs\web-app-production.log
echo 停止服务器：taskkill /F /IM node.exe
echo.
node production-server.js

echo.
echo ========================================
echo 构建和部署完成！
echo ========================================
echo.
pause

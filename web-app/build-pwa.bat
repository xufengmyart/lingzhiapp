@echo off
chcp 65001 >nul
echo ========================================
echo 灵值生态园 PWA 构建和启动
echo ========================================
echo.

REM 停止服务器
echo [1/4] 停止现有服务器...
taskkill /F /IM node.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo.

REM 清理旧的构建产物
echo [2/4] 清理旧的构建产物...
if exist "dist" (
    rmdir /s /q dist
    echo 已删除 dist 目录
)
echo.

REM 重新构建项目
echo [3/4] 重新构建项目（包含PWA配置）...
echo 这可能需要1-2分钟，请耐心等待...
echo.
npm run build
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [错误] 构建失败！
    pause
    exit /b 1
)
echo.

REM 验证PWA文件
echo [4/4] 验证PWA配置...
if exist "dist\manifest.json" (
    echo [成功] manifest.json 已生成
) else (
    echo [警告] manifest.json 未找到
)

if exist "dist\sw.js" (
    echo [成功] Service Worker 已生成
) else (
    echo [警告] Service Worker 未找到
)
echo.

REM 启动服务器
echo ========================================
echo 启动PWA服务器...
echo ========================================
node production-server.js

echo.
echo ========================================
echo PWA构建完成！
echo ========================================
echo.
echo 📱 安装应用（电脑Chrome/Edge）：
echo 1. 访问 http://localhost:3000
echo 2. 点击地址栏右侧的安装图标（📱）
echo 3. 点击"安装"按钮
echo.
echo 📱 安装应用（Android手机）：
echo 1. 用手机访问应用地址
echo 2. 点击浏览器菜单
echo 3. 选择"添加到主屏幕"
echo.
echo 📱 安装应用（iPhone/iPad）：
echo 1. 用Safari访问应用地址
echo 2. 点击分享按钮（⬆️）
echo 3. 选择"添加到主屏幕"
echo.
echo 📖 详细说明请查看：PWA-GUIDE.md
echo.
pause

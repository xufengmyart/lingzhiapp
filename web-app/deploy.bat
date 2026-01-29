@echo off
REM###############################################################################
REM 灵值生态园APP - 一键部署脚本 (Windows版本)
REM 支持多种部署方案
REM###############################################################################

setlocal enabledelayedexpansion

REM 配置
set APP_NAME=lingzhi-ecosystem
set PROJECT_DIR=%USERPROFILE%\Documents\lingzhi-ecosystem

REM 打印Logo
cls
echo.
echo ================================================================
echo.
echo           灵值生态园APP - 一键部署脚本
echo           Lingzhi Ecosystem - One-Click Deployment
echo.
echo ================================================================
echo.

REM 检查Node.js
echo [INFO] 检查系统环境...
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js未安装！请先安装Node.js
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
)

where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] npm未安装！请先安装npm
    pause
    exit /b 1
)

echo [SUCCESS] 系统环境检查通过
node -v
npm -v
echo.

REM 检查项目目录
if not exist "package.json" (
    echo [ERROR] 请在项目根目录运行此脚本！
    pause
    exit /b 1
)

:menu
echo.
echo 请选择部署方案：
echo.
echo 1) 本地开发服务器 (localhost:3000)
echo 2) Docker容器部署
echo 3) 仅构建项目
echo 4) 移动应用打包 (Android/iOS)
echo 5) 安装依赖
echo 0) 退出
echo.
set /p choice="请选择 (0-5): "

if "%choice%"=="1" goto deploy_local
if "%choice%"=="2" goto deploy_docker
if "%choice%"=="3" goto deploy_build
if "%choice%"=="4" goto deploy_mobile
if "%choice%"=="5" goto install_deps
if "%choice%"=="0" goto exit
echo [ERROR] 无效的选择！
goto menu

:install_deps
echo.
echo [INFO] 安装项目依赖...
if exist "node_modules" (
    echo [WARNING] node_modules已存在，跳过安装
) else (
    npm install
    if %errorlevel% neq 0 (
        echo [ERROR] 依赖安装失败！
        pause
        exit /b 1
    )
    echo [SUCCESS] 依赖安装完成
)
goto menu

:deploy_local
echo.
echo [INFO] 启动本地开发服务器...
echo [WARNING] 服务器将运行在 http://localhost:3000
echo [WARNING] 按 Ctrl+C 停止服务器
echo.

npm run dev
goto menu

:deploy_docker
echo.
echo [INFO] Docker容器部署...

where docker >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker未安装！请先安装Docker Desktop
    pause
    exit /b 1
)

echo [INFO] 构建Docker镜像...
docker build -t %APP_NAME%:latest .
if %errorlevel% neq 0 (
    echo [ERROR] Docker镜像构建失败！
    pause
    exit /b 1
)

echo [INFO] 停止旧容器...
docker stop %APP_NAME% 2>nul
docker rm %APP_NAME% 2>nul

echo [INFO] 启动新容器...
docker run -d -p 80:80 --name %APP_NAME% --restart unless-stopped %APP_NAME%:latest
if %errorlevel% neq 0 (
    echo [ERROR] 容器启动失败！
    pause
    exit /b 1
)

echo [SUCCESS] Docker容器部署完成
echo [INFO] 应用已启动，访问地址: http://localhost
echo [INFO] 查看日志: docker logs -f %APP_NAME%
pause
goto menu

:deploy_build
echo.
echo [INFO] 构建项目...
npm run build
if %errorlevel% neq 0 (
    echo [ERROR] 项目构建失败！
    pause
    exit /b 1
)
echo [SUCCESS] 项目构建完成
echo [INFO] 输出目录: dist\
pause
goto menu

:deploy_mobile
echo.
echo [INFO] 移动应用打包...

REM 检查Capacitor
npm list @capacitor/cli >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Capacitor未安装！
    echo 安装命令: npm install @capacitor/core @capacitor/cli
    pause
    exit /b 1
)

REM 构建项目
call :deploy_build

echo.
echo [INFO] 选择移动平台:
echo 1) Android
echo 2) iOS
set /p PLATFORM="请选择 (1/2): "

if "%PLATFORM%"=="1" (
    echo [INFO] 构建Android应用...
    npx cap add android
    npx cap sync android
    echo [SUCCESS] Android应用准备完成
    echo [INFO] 下一步: 使用Android Studio打开 android\ 目录并构建APK
) else if "%PLATFORM%"=="2" (
    echo [INFO] 构建iOS应用...
    npx cap add ios
    npx cap sync ios
    echo [SUCCESS] iOS应用准备完成
    echo [INFO] 下一步: 使用Xcode打开 ios\ 目录并构建IPA
) else (
    echo [ERROR] 无效的选择！
    pause
    exit /b 1
)

pause
goto menu

:exit
echo.
echo [INFO] 退出脚本
exit /b 0

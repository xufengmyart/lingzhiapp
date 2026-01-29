@echo off
chcp 65001 >nul
echo ========================================
echo 灵值生态园 - 移动应用打包
echo ========================================
echo.

REM 检查是否已安装Capacitor
if not exist "node_modules\@capacitor" (
    echo [1/5] 安装Capacitor依赖...
    npm install -D @capacitor/cli @capacitor/core @capacitor/android @capacitor/ios
    npm install @capacitor/app @capacitor/keyboard @capacitor/splash-screen @capacitor/status-bar
)

REM 构建项目
echo [2/5] 构建项目...
call npm run build

REM 初始化Capacitor
if not exist "capacitor.config.ts" (
    echo [3/5] 初始化Capacitor...
    npx cap init "灵值生态园" "com.lingzhi.ecosystem"
)

REM 同步项目
echo [4/5] 同步项目到移动平台...
echo 选择平台:
echo   1. Android
echo   2. iOS
echo   3. 全部
echo.
set /p platform="请选择 (1/2/3): "

if "%platform%"=="1" (
    echo 同步到Android...
    npx cap sync android
    echo.
    echo ========================================
    echo Android项目已同步！
    echo ========================================
    echo.
    echo 下一步:
    echo   1. 打开Android Studio: npx cap open android
    echo   2. 在Android Studio中构建APK
    echo   3. 或者使用命令行构建
    echo.
) else if "%platform%"=="2" (
    echo 同步到iOS...
    npx cap sync ios
    echo.
    echo ========================================
    echo iOS项目已同步！
    echo ========================================
    echo.
    echo 下一步:
    echo   1. 打开Xcode: npx cap open ios
    echo   2. 在Xcode中构建IPA
    echo.
) else if "%platform%"=="3" (
    echo 同步到Android和iOS...
    npx cap sync android
    npx cap sync ios
    echo.
    echo ========================================
    echo 移动项目已同步！
    echo ========================================
    echo.
    echo Android: npx cap open android
    echo iOS: npx cap open ios
    echo.
)

echo [5/5] 准备完成！
echo.
pause

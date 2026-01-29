@echo off
REM 灵值生态园APP - 部署辅助脚本（Windows版本）
REM 此脚本帮助用户快速完成一些可以自动化的操作

setlocal enabledelayedexpansion

REM 颜色设置
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

REM 打印信息
:print_info
echo %BLUE%[INFO]%NC% %~1
goto :eof

:print_success
echo %GREEN%[SUCCESS]%NC% %~1
goto :eof

:print_warning
echo %YELLOW%[WARNING]%NC% %~1
goto :eof

:print_error
echo %RED%[ERROR]%NC% %~1
goto :eof

REM 打印横幅
:print_banner
echo.
echo ==========================================
echo   灵值生态园APP - 部署辅助脚本
echo ==========================================
echo.
goto :eof

REM 检查Git
:check_git
call :print_info 检查Git...

where git >nul 2>&1
if %errorlevel% neq 0 (
    call :print_error Git未安装，请先安装Git
    exit /b 1
)

if not exist ".git" (
    call :print_warning Git仓库未初始化
    call :print_info 正在初始化Git仓库...
    git init
    call :print_success Git仓库已初始化
) else (
    call :print_success Git仓库已存在
)
goto :eof

REM 检查远程仓库
:check_remote
call :print_info 检查Git远程仓库...

git remote get-url origin >nul 2>&1
if %errorlevel% equ 0 (
    for /f "delims=" %%i in ('git remote get-url origin') do set REMOTE_URL=%%i
    call :print_success 远程仓库已配置: !REMOTE_URL!
    exit /b 0
) else (
    call :print_warning 远程仓库未配置
    exit /b 1
)

REM 添加远程仓库
:add_remote
call :print_info 请输入GitHub仓库URL（格式：https://github.com/用户名/仓库名.git）
set /p REPO_URL="> "

if "!REPO_URL!"=="" (
    call :print_error 仓库URL不能为空
    exit /b 1
)

call :print_info 正在添加远程仓库...
git remote add origin !REPO_URL!
call :print_success 远程仓库已添加: !REPO_URL!
goto :eof

REM 推送到GitHub
:push_to_github
call :print_info 正在推送到GitHub...

REM 检查当前分支
for /f "delims=" %%i in ('git branch --show-current') do set CURRENT_BRANCH=%%i
if not "!CURRENT_BRANCH!"=="main" (
    call :print_info 切换到main分支...
    git checkout -b main 2>nul || git branch -M main
)

REM 尝试推送
git push -u origin main 2>&1
if %errorlevel% equ 0 (
    call :print_success 代码已成功推送到GitHub
    exit /b 0
) else (
    call :print_error 推送失败
    call :print_info 可能的原因：
    call :print_info   1. 仓库URL不正确
    call :print_info   2. 需要GitHub认证（用户名和Personal Access Token）
    call :print_info   3. 仓库不存在或没有权限
    call :print_info
    call :print_info 请检查以上问题后重试
    exit /b 1
)

REM 构建项目
:build_project
call :print_info 正在构建项目...

if not exist "package.json" (
    call :print_error package.json不存在，无法构建
    exit /b 1
)

where npm >nul 2>&1
if %errorlevel% neq 0 (
    call :print_error npm未安装，请先安装Node.js和npm
    exit /b 1
)

REM 检查node_modules
if not exist "node_modules" (
    call :print_info 正在安装依赖...
    call npm install
)

REM 构建
call npm run build

if exist "dist" (
    call :print_success 项目构建成功
    exit /b 0
) else (
    call :print_error 项目构建失败
    exit /b 1
)

REM 显示Git状态
:show_git_status
call :print_info Git状态：
git status
goto :eof

REM 显示最近的提交
:show_recent_commits
call :print_info 最近的提交：
git log --oneline -5
goto :eof

REM 显示帮助信息
:show_help
echo 使用方法: deploy-helper.bat [选项]
echo.
echo 选项:
echo     status      显示当前状态
echo     remote      检查/配置远程仓库
echo     push        推送代码到GitHub
echo     build       构建项目
echo     all         执行完整部署流程（检查-远程-推送）
echo     help        显示帮助信息
echo.
echo 示例:
echo     deploy-helper.bat status     # 查看状态
echo     deploy-helper.bat remote     # 配置远程仓库
echo     deploy-helper.bat push       # 推送代码
echo     deploy-helper.bat all        # 完整流程
echo.
goto :eof

REM 显示当前状态
:show_status
call :print_banner
call :check_git

echo.
call :print_info 远程仓库状态：
call :check_remote
if %errorlevel% equ 0 (
    echo   鈻遠程仓库已配置
) else (
    echo   鈫遠程仓库未配置
)

echo.
call :print_info 文件状态：
call :show_git_status

echo.
call :print_info 最近提交：
call :show_recent_commits

echo.
call :print_info 构建状态：
if exist "dist" (
    echo   鈻项目已构建
) else (
    echo   鈫项目未构建
)

echo.
call :print_info 下一步操作：
call :check_remote
if %errorlevel% neq 0 (
    echo   1. 运行: deploy-helper.bat remote
)
echo   2. 运行: deploy-helper.bat push
echo   3. 访问Vercel并导入仓库

goto :eof

REM 完整流程
:full_process
call :print_banner
call :print_info 开始完整部署流程...
echo.

REM 步骤1：检查Git
call :check_git

REM 步骤2：配置远程仓库
call :check_remote
if %errorlevel% neq 0 (
    echo.
    call :print_info ===== 步骤1/3: 配置远程仓库 =====
    call :add_remote
)

REM 步骤3：推送代码
echo.
call :print_info ===== 步骤2/3: 推送代码到GitHub =====
call :push_to_github
if %errorlevel% neq 0 (
    exit /b 1
)

REM 步骤4：构建项目（可选）
echo.
call :print_info ===== 步骤3/3: 构建项目（可选）=====
set /p BUILD_CHOICE="是否构建项目？(y/n) [n]: "
if "!BUILD_CHOICE!"=="y" (
    call :build_project
    if %errorlevel% neq 0 (
        exit /b 1
    )
)

REM 完成
echo.
call :print_banner
call :print_success 准备工作已完成！
echo.
call :print_info 下一步操作：
echo   1. 访问 https://vercel.com
echo   2. 登录并创建新项目
echo   3. 导入GitHub仓库
call :check_remote
if %errorlevel% equ 0 (
    for /f "delims=" %%i in ('git remote get-url origin') do echo   4. !REMOTE_URL已配置
) else (
    echo   4. 配置远程仓库并推送代码
)
echo   5. 点击Deploy按钮
echo   6. 等待部署完成（约2-3分钟）
echo.
call :print_info 详细步骤请参考: USER_ACTION_GUIDE.md

goto :eof

REM 主函数
:main
if "%1"=="" (
    goto :show_status
) else if "%1"=="status" (
    call :show_status
) else if "%1"=="remote" (
    call :print_banner
    call :check_git
    call :add_remote
) else if "%1"=="push" (
    call :print_banner
    call :check_git
    call :check_remote
    if %errorlevel% neq 0 (
        call :print_warning 远程仓库未配置，请先运行: deploy-helper.bat remote
        exit /b 1
    )
    call :push_to_github
) else if "%1"=="build" (
    call :print_banner
    call :build_project
) else if "%1"=="all" (
    call :full_process
) else if "%1"=="help" (
    call :show_help
) else if "%1"=="--help" (
    call :show_help
) else if "%1"=="-h" (
    call :show_help
) else (
    call :print_error 未知选项: %1
    echo.
    call :show_help
    exit /b 1
)

goto :eof

REM 执行主函数
call :main %*

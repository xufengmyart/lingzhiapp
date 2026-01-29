#############################################
# 灵值生态园智能体 - 一键部署脚本（Windows）
# 版本：v5.0
# 日期：2025-01-24
#############################################

$ErrorActionPreference = "Stop"

# 项目配置
$PROJECT_NAME = "灵值生态园智能体"
$VERSION = "v5.0"
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$AUTH_DIR = Join-Path $SCRIPT_DIR "src\auth"
$LOG_FILE = "C:\temp\deploy_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

# 创建日志目录
if (-not (Test-Path "C:\temp")) {
    New-Item -ItemType Directory -Path "C:\temp" | Out-Null
}

# 函数：打印信息
function Print-Info {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
    Add-Content -Path $LOG_FILE -Value "[$timestamp] [INFO] $Message"
}

# 函数：打印成功
function Print-Success {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
    Add-Content -Path $LOG_FILE -Value "[$timestamp] [SUCCESS] $Message"
}

# 函数：打印警告
function Print-Warning {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
    Add-Content -Path $LOG_FILE -Value "[$timestamp] [WARNING] $Message"
}

# 函数：打印错误
function Print-Error {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[ERROR] $Message" -ForegroundColor Red
    Add-Content -Path $LOG_FILE -Value "[$timestamp] [ERROR] $Message"
}

# 函数：打印标题
function Print-Title {
    param([string]$Message)
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host $Message -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Add-Content -Path $LOG_FILE -Value ""
    Add-Content -Path $LOG_FILE -Value "========================================"
    Add-Content -Path $LOG_FILE -Value $Message
    Add-Content -Path $LOG_FILE -Value "========================================"
}

# 函数：检查 Python 版本
function Check-PythonVersion {
    Print-Title "检查 Python 版本"
    
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python (\d+)\.(\d+)") {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            $versionString = "$major.$minor"
            
            Print-Info "Python 版本：$versionString"
            
            if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 10)) {
                Print-Error "Python 版本过低，需要 Python 3.10 或更高版本"
                return $false
            }
            
            Print-Success "Python 版本检查通过"
            return $true
        } else {
            Print-Error "无法解析 Python 版本"
            return $false
        }
    } catch {
        Print-Error "Python 未安装或未添加到 PATH"
        return $false
    }
}

# 函数：安装依赖
function Install-Dependencies {
    Print-Title "安装 Python 依赖"
    
    $requirementsFile = Join-Path $AUTH_DIR "requirements.txt"
    if (-not (Test-Path $requirementsFile)) {
        Print-Error "requirements.txt 文件不存在"
        return $false
    }
    
    Print-Info "正在安装依赖..."
    
    try {
        Set-Location $AUTH_DIR
        python -m pip install -r requirements.txt >> $LOG_FILE 2>&1
        Print-Success "依赖安装成功"
        return $true
    } catch {
        Print-Error "依赖安装失败，请查看日志：$LOG_FILE"
        return $false
    }
}

# 函数：初始化数据库
function Initialize-Database {
    Print-Title "初始化数据库"
    
    Set-Location $AUTH_DIR
    
    Print-Info "正在初始化权限管理数据..."
    try {
        python init_data.py >> $LOG_FILE 2>&1
        Print-Success "权限管理数据初始化成功"
    } catch {
        Print-Error "权限管理数据初始化失败"
        return $false
    }
    
    Print-Info "正在初始化生态机制数据..."
    try {
        python init_ecosystem.py >> $LOG_FILE 2>&1
        Print-Success "生态机制数据初始化成功"
    } catch {
        Print-Error "生态机制数据初始化失败"
        return $false
    }
    
    Print-Info "正在初始化项目参与和团队组建数据..."
    try {
        python init_project.py >> $LOG_FILE 2>&1
        Print-Success "项目参与和团队组建数据初始化成功"
    } catch {
        Print-Error "项目参与和团队组建数据初始化失败"
        return $false
    }
    
    Print-Success "数据库初始化完成"
    return $true
}

# 函数：停止旧服务
function Stop-Service {
    Print-Title "停止旧服务"
    
    try {
        $processes = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*uvicorn api:app*" }
        
        if ($processes) {
            foreach ($proc in $processes) {
                Print-Info "正在停止旧服务 (PID: $($proc.Id))..."
                Stop-Process -Id $proc.Id -Force
            }
            Start-Sleep -Seconds 2
            Print-Success "旧服务已停止"
        } else {
            Print-Info "未发现运行中的服务"
        }
    } catch {
        Print-Warning "停止服务时出现警告：$($_.Exception.Message)"
    }
}

# 函数：启动服务
function Start-Service {
    Print-Title "启动服务"
    
    try {
        Set-Location $AUTH_DIR
        
        Print-Info "正在启动 FastAPI 服务..."
        $null = Start-Process -FilePath python -ArgumentList "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000" -RedirectStandardOutput "C:\temp\api.log" -RedirectStandardError "C:\temp\api_error.log"
        
        Start-Sleep -Seconds 5
        
        $processes = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*uvicorn api:app*" }
        
        if ($processes) {
            Print-Success "服务启动成功 (PID: $($processes[0].Id))"
            return $true
        } else {
            Print-Error "服务启动失败，请查看日志：C:\temp\api_error.log"
            return $false
        }
    } catch {
        Print-Error "服务启动失败：$($_.Exception.Message)"
        return $false
    }
}

# 函数：验证服务
function Verify-Service {
    Print-Title "验证服务"
    
    Print-Info "正在检查服务状态..."
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/" -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Print-Success "服务响应正常"
        } else {
            Print-Warning "服务响应异常（状态码：$($response.StatusCode））"
        }
    } catch {
        Print-Error "服务无响应"
        return $false
    }
    
    Print-Info "正在测试登录功能..."
    try {
        $body = "username=xufeng@meiyueart.cn&password=Xf@071214"
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/auth/login" -Method POST -Body $body -ContentType "application/x-www-form-urlencoded" -UseBasicParsing -TimeoutSec 10
        $content = $response.Content
        
        if ($content -match "access_token") {
            Print-Success "登录功能正常"
        } else {
            Print-Warning "登录功能可能存在问题，请手动测试"
        }
    } catch {
        Print-Warning "登录功能测试失败：$($_.Exception.Message)"
    }
    
    Print-Info "正在检查 API 文档..."
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Print-Success "API 文档可访问"
        } else {
            Print-Warning "API 文档访问可能存在问题"
        }
    } catch {
        Print-Warning "API 文档访问测试失败：$($_.Exception.Message)"
    }
    
    return $true
}

# 函数：显示部署信息
function Show-DeployInfo {
    Print-Title "部署信息"
    
    Write-Host "项目名称：$PROJECT_NAME" -ForegroundColor Green
    Write-Host "版本：$VERSION" -ForegroundColor Green
    Write-Host "部署时间：$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Green
    Write-Host "日志文件：$LOG_FILE" -ForegroundColor Green
    Write-Host ""
    Write-Host "服务地址：http://localhost:8000" -ForegroundColor Green
    Write-Host "API 文档：http://localhost:8000/docs" -ForegroundColor Green
    Write-Host "健康检查：http://localhost:8000/" -ForegroundColor Green
    Write-Host ""
    Write-Host "管理员账号：xufeng@meiyueart.cn" -ForegroundColor Green
    Write-Host "管理员密码：Xf@071214" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  请妥善保管管理员账号密码！" -ForegroundColor Yellow
}

# 函数：主函数
function Main {
    Print-Title "$PROJECT_NAME 一键部署脚本（Windows）"
    Write-Host "版本：$VERSION" | Tee-Object -FilePath $LOG_FILE
    Write-Host "日期：$(Get-Date -Format 'yyyy-MM-dd')" | Tee-Object -FilePath $LOG_FILE
    Write-Host "" | Tee-Object -FilePath $LOG_FILE
    
    # 检查环境
    if (-not (Check-PythonVersion)) {
        exit 1
    }
    
    # 安装依赖
    if (-not (Install-Dependencies)) {
        exit 1
    }
    
    # 初始化数据库
    if (-not (Initialize-Database)) {
        exit 1
    }
    
    # 停止旧服务
    Stop-Service
    
    # 启动服务
    if (-not (Start-Service)) {
        exit 1
    }
    
    # 验证服务
    if (-not (Verify-Service)) {
        Print-Warning "服务验证失败，但服务可能仍在运行"
    }
    
    # 显示部署信息
    Show-DeployInfo
    
    Print-Success "部署完成！"
}

# 执行主函数
Main

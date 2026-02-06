#!/usr/bin/env python3
"""
灵值生态园 - 配置验证脚本
检查所有配置是否符合生产环境要求
"""
import os
import sys
from pathlib import Path

# 颜色输出
class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def print_header(title):
    print(f"\n{'='*60}")
    print(f"{title:^60}")
    print(f"{'='*60}\n")

def print_status(message, status):
    if status == 'OK':
        print(f"{Colors.GREEN}✅ {message}{Colors.NC}")
    elif status == 'WARNING':
        print(f"{Colors.YELLOW}⚠️  {message}{Colors.NC}")
    elif status == 'ERROR':
        print(f"{Colors.RED}❌ {message}{Colors.NC}")
    else:
        print(f"{Colors.BLUE}ℹ️  {message}{Colors.NC}")

def check_file_exists(path, required=True):
    """检查文件是否存在"""
    if Path(path).exists():
        return 'OK', f"文件存在: {path}"
    else:
        if required:
            return 'ERROR', f"文件缺失: {path}"
        else:
            return 'WARNING', f"文件可选: {path}"

def check_env_file(path, required_vars):
    """检查环境变量文件"""
    if not Path(path).exists():
        return 'ERROR', f"配置文件不存在: {path}"

    missing_vars = []
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        for var in required_vars:
            if var not in content:
                missing_vars.append(var)

    if missing_vars:
        return 'ERROR', f"缺少环境变量: {', '.join(missing_vars)}"

    # 检查默认值
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        default_values = ['your-jwt-secret-key-change-this', 'your-secret-key-here']
        for default in default_values:
            if default in content:
                return 'WARNING', f"使用了默认值: {default}"

    return 'OK', "配置文件完整"

def check_database():
    """检查数据库"""
    db_path = Path('admin-backend/lingzhi_ecosystem.db')
    if not db_path.exists():
        return 'WARNING', "数据库不存在，将在首次运行时创建"

    size = db_path.stat().st_size
    if size < 1024:
        return 'ERROR', f"数据库太小 ({size} bytes)"

    return 'OK', f"数据库大小: {size / 1024:.2f} KB"

def check_jwt_config():
    """检查JWT配置"""
    env_path = Path('admin-backend/.env')
    if not env_path.exists():
        return 'ERROR', "缺少.env配置文件"

    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'JWT_SECRET=lingzhi-jwt-secret-key' in content:
        return 'ERROR', "JWT_SECRET使用了默认值，存在安全风险"

    if 'SECRET_KEY=lingzhi-ecosystem-secret-key-2026' in content and 'prod' not in content:
        return 'WARNING', "SECRET_KEY使用了默认值，建议更新"

    return 'OK', "JWT配置安全"

def main():
    print_header("灵值生态园 - 配置验证")
    print(f"检查时间: {os.popen('date').read().strip()}")

    issues = []
    warnings = []

    # 1. 检查项目根目录
    print("【1】项目结构检查")
    status, msg = check_file_exists('.env', required=True)
    print_status(msg, status)
    if status == 'ERROR': issues.append(msg)

    status, msg = check_file_exists('.gitignore', required=True)
    print_status(msg, status)
    if status == 'ERROR': issues.append(msg)

    # 2. 检查后端配置
    print("\n【2】后端配置检查")
    status, msg = check_file_exists('admin-backend/app.py', required=True)
    print_status(msg, status)
    if status == 'ERROR': issues.append(msg)

    status, msg = check_file_exists('admin-backend/.env', required=True)
    print_status(msg, status)
    if status == 'ERROR': issues.append(msg)

    status, msg = check_env_file('admin-backend/.env', ['SECRET_KEY', 'JWT_SECRET'])
    print_status(msg, status)
    if status == 'ERROR': issues.append(msg)
    if status == 'WARNING': warnings.append(msg)

    status, msg = check_jwt_config()
    print_status(msg, status)
    if status == 'ERROR': issues.append(msg)
    if status == 'WARNING': warnings.append(msg)

    # 3. 检查前端配置
    print("\n【3】前端配置检查")
    status, msg = check_file_exists('web-app/package.json', required=True)
    print_status(msg, status)
    if status == 'ERROR': issues.append(msg)

    status, msg = check_file_exists('web-app/vite.config.ts', required=True)
    print_status(msg, status)
    if status == 'ERROR': issues.append(msg)

    # 4. 检查数据库
    print("\n【4】数据库检查")
    status, msg = check_database()
    print_status(msg, status)
    if status == 'ERROR': issues.append(msg)

    # 5. 检查部署脚本
    print("\n【5】部署脚本检查")
    status, msg = check_file_exists('sftp_deploy.py', required=False)
    print_status(msg, status)
    if status == 'ERROR': issues.append(msg)

    # 6. 安全检查
    print("\n【6】安全检查")
    if Path('.gitignore').exists():
        with open('.gitignore', 'r', encoding='utf-8') as f:
            content = f.read()
            if '.env' in content:
                print_status(".env文件已在.gitignore中", 'OK')
            else:
                print_status(".env文件未在.gitignore中", 'ERROR')
                issues.append(".env文件未添加到.gitignore")

    # 总结
    print_header("验证总结")

    if not issues and not warnings:
        print(f"{Colors.GREEN}✅ 所有配置检查通过！{Colors.NC}")
        return 0

    if warnings:
        print(f"{Colors.YELLOW}⚠️  发现 {len(warnings)} 个警告:{Colors.NC}")
        for i, warning in enumerate(warnings, 1):
            print(f"   {i}. {warning}")
        print()

    if issues:
        print(f"{Colors.RED}❌ 发现 {len(issues)} 个错误:{Colors.NC}")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        print()
        print(f"{Colors.YELLOW}请修复以上错误后再次验证{Colors.NC}")
        return 1

    return 0

if __name__ == '__main__':
    sys.exit(main())

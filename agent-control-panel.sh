#!/bin/bash

# ============================================
# 智能体控制面板
# 功能：管理自动化系统，查看状态，手动操作
# ============================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m'

# 配置
LOG_FILE="/workspace/projects/auto-deploy.log"
SERVER_HOST="123.56.142.143"

# ============================================
# 界面函数
# ============================================

print_header() {
    clear
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════╗"
    echo "║  灵值生态园 - 智能体控制面板            ║"
    echo "╚════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_menu() {
    echo -e "${BOLD}主菜单：${NC}"
    echo ""
    echo "  ${BLUE}1.${NC} 查看自动化系统状态"
    echo "  ${BLUE}2.${NC} 启动自动化系统"
    echo "  ${BLUE}3.${NC} 停止自动化系统"
    echo "  ${BLUE}4.${NC} 查看部署日志"
    echo "  ${BLUE}5.${NC} 手动触发部署"
    echo "  ${BLUE}6.${NC} 查看服务器状态"
    echo "  ${BLUE}7.${NC} 查看项目统计"
    echo "  ${BLUE}8.${NC} 快速部署（不备份）"
    echo "  ${BLUE}9.${NC} 完整部署（含备份）"
    echo "  ${RED}0.${NC} 退出"
    echo ""
}

# ============================================
# 功能函数
# ============================================

# 查看系统状态
show_system_status() {
    print_header
    echo -e "${BOLD}自动化系统状态${NC}"
    echo ""

    if [ -f "/workspace/projects/auto-deploy.pid" ]; then
        local pid=$(cat /workspace/projects/auto-deploy.pid)
        if ps -p "$pid" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ 状态：运行中${NC}"
            echo "  PID: $pid"
            echo "  启动时间: $(ps -p $pid -o lstart=)"
        else
            echo -e "${RED}✗ 状态：已停止${NC}"
            echo "  PID 文件存在但进程未运行"
        fi
    else
        echo -e "${YELLOW}✗ 状态：未运行${NC}"
        echo "  PID 文件不存在"
    fi

    echo ""
    echo -e "${BOLD}最近日志：${NC}"
    if [ -f "$LOG_FILE" ]; then
        tail -n 10 "$LOG_FILE"
    else
        echo "  日志文件不存在"
    fi

    echo ""
    read -p "按回车键返回主菜单..."
}

# 启动系统
start_automation() {
    print_header
    echo -e "${BOLD}启动自动化系统${NC}"
    echo ""

    ./auto-deploy.sh start

    echo ""
    read -p "按回车键返回主菜单..."
}

# 停止系统
stop_automation() {
    print_header
    echo -e "${BOLD}停止自动化系统${NC}"
    echo ""

    read -p "确认停止？(y/N): " confirm
    if [[ "$confirm" =~ ^[Yy]$ ]]; then
        ./auto-deploy.sh stop
    else
        echo "已取消"
    fi

    echo ""
    read -p "按回车键返回主菜单..."
}

# 查看日志
show_logs() {
    print_header
    echo -e "${BOLD}部署日志${NC}"
    echo ""
    echo "  按 Ctrl+C 退出日志查看"
    echo ""

    if [ -f "$LOG_FILE" ]; then
        tail -n 50 -f "$LOG_FILE"
    else
        echo "日志文件不存在"
        sleep 2
    fi
}

# 手动部署
manual_deploy() {
    print_header
    echo -e "${BOLD}手动触发部署${NC}"
    echo ""

    ./auto-deploy.sh deploy

    echo ""
    read -p "按回车键返回主菜单..."
}

# 查看服务器状态
show_server_status() {
    print_header
    echo -e "${BOLD}服务器状态${NC}"
    echo ""

    echo "正在连接服务器 $SERVER_HOST..."
    echo ""

    ssh root@"$SERVER_HOST" "
        echo '╔════════════════════════════════════════╗'
        echo '║  服务器系统信息                          ║'
        echo '╚════════════════════════════════════════╝'
        echo ''
        echo '系统信息：'
        uname -a
        echo ''
        echo '内存使用：'
        free -h
        echo ''
        echo '磁盘使用：'
        df -h | head -5
        echo ''
        echo 'Nginx 状态：'
        systemctl status nginx --no-pager | head -10
        echo ''
        echo '最近的 Nginx 错误日志：'
        tail -n 5 /var/log/nginx/error.log 2>/dev/null || echo '无错误日志'
    "

    echo ""
    read -p "按回车键返回主菜单..."
}

# 查看项目统计
show_project_stats() {
    print_header
    echo -e "${BOLD}项目统计${NC}"
    echo ""

    echo "代码统计："
    echo ""

    echo "  文件总数："
    find /workspace/projects -type f \( -name "*.tsx" -o -name "*.ts" -o -name "*.jsx" -o -name "*.js" \) -not -path "*/node_modules/*" -not -path "*/.git/*" | wc -l

    echo ""
    echo "  代码行数："
    find /workspace/projects -type f \( -name "*.tsx" -o -name "*.ts" -o -name "*.jsx" -o -name "*.js" \) -not -path "*/node_modules/*" -not -path "*/.git/*" -exec wc -l {} + | tail -1

    echo ""
    echo "  Git 状态："
    cd /workspace/projects
    git status --short | head -10

    echo ""
    echo "  最近提交："
    git log --oneline -5

    echo ""
    echo "  备份文件："
    ls -lh /workspace/projects/backups/*.tar.gz 2>/dev/null | tail -5 || echo "  无备份文件"

    echo ""
    read -p "按回车键返回主菜单..."
}

# 快速部署
quick_deploy() {
    print_header
    echo -e "${BOLD}快速部署${NC}"
    echo ""
    echo "  - 备份 public 目录"
    echo "  - 推送到 GitHub"
    echo "  - 同步到服务器"
    echo "  - 重启 Nginx"
    echo ""

    read -p "确认执行快速部署？(y/N): " confirm
    if [[ "$confirm" =~ ^[Yy]$ ]]; then
        ./quick-deploy.sh
    else
        echo "已取消"
    fi

    echo ""
    read -p "按回车键返回主菜单..."
}

# 完整部署
full_deploy() {
    print_header
    echo -e "${BOLD}完整部署${NC}"
    echo ""
    echo "  - 本地备份"
    echo "  - 服务器备份"
    echo "  - 推送到 GitHub"
    echo "  - 同步到服务器"
    echo "  - 重启 Nginx"
    echo "  - 验证部署"
    echo ""

    read -p "确认执行完整部署？(y/N): " confirm
    if [[ "$confirm" =~ ^[Yy]$ ]]; then
        ./deploy.sh
    else
        echo "已取消"
    fi

    echo ""
    read -p "按回车键返回主菜单..."
}

# ============================================
# 主流程
# ============================================

main() {
    while true; do
        print_menu
        read -p "请选择操作 (0-9): " choice

        case $choice in
            1)
                show_system_status
                ;;
            2)
                start_automation
                ;;
            3)
                stop_automation
                ;;
            4)
                show_logs
                ;;
            5)
                manual_deploy
                ;;
            6)
                show_server_status
                ;;
            7)
                show_project_stats
                ;;
            8)
                quick_deploy
                ;;
            9)
                full_deploy
                ;;
            0)
                echo ""
                echo -e "${GREEN}再见！${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}✗ 无效选项，请重新选择${NC}"
                sleep 2
                ;;
        esac
    done
}

# 启动主程序
main

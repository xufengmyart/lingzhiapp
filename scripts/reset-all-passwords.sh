#!/bin/bash

################################################################################
# 灵值生态园 - 一键重置所有用户密码（Shell 版本）
# 用途：将所有用户的密码统一重置为 123456
# 作者：Coze Coding
# 版本：v1.0
# 日期：2026-02-11
################################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 配置变量
DATABASE="/workspace/projects/lingzhi_ecosystem.db"
DEFAULT_PASSWORD="123456"
PASSWORD_HASH=$(echo -n "$DEFAULT_PASSWORD" | sha256sum | awk '{print $1}')

# 打印横幅
print_banner() {
    echo ""
    echo "================================================================================"
    echo "  灵值生态园 - 一键重置所有用户密码"
    echo "  默认密码: $DEFAULT_PASSWORD"
    echo "================================================================================"
    echo ""
}

# 检查数据库文件
check_database() {
    if [ ! -f "$DATABASE" ]; then
        echo -e "${RED}[ERROR]${NC} 数据库文件不存在: $DATABASE"
        exit 1
    fi
    echo -e "${GREEN}[INFO]${NC} 数据库文件: $DATABASE"
}

# 查询用户数量
get_user_count() {
    sqlite3 "$DATABASE" "SELECT COUNT(*) FROM users;" 2>/dev/null || echo "0"
}

# 显示用户列表
show_users() {
    echo ""
    echo "用户列表（前 20 个）："
    echo "--------------------------------------------------------------------------------"
    printf "%-6s %-20s %-15s %-25s\n" "ID" "用户名" "手机号" "邮箱"
    echo "--------------------------------------------------------------------------------"
    sqlite3 "$DATABASE" <<EOF
.mode column
.headers off
SELECT 
    printf('%-6d', id),
    printf('%-20s', SUBSTR(username, 1, 20)),
    printf('%-15s', COALESCE(phone, 'N/A')),
    printf('%-25s', COALESCE(email, 'N/A'))
FROM users
ORDER BY id
LIMIT 20;
EOF
    echo "--------------------------------------------------------------------------------"
}

# 重置所有用户密码
reset_all_passwords() {
    echo ""
    echo -e "${YELLOW}[WARNING]${NC} 即将重置所有用户密码"
    echo "默认密码: $DEFAULT_PASSWORD"
    echo "密码哈希: $PASSWORD_HASH"
    echo ""
    
    # 确认操作
    if [ "$FORCE" != "yes" ]; then
        read -p "确认要继续吗？(yes/no): " confirm
        if [ "$confirm" != "yes" ] && [ "$confirm" != "y" ]; then
            echo "操作已取消"
            exit 0
        fi
    fi
    
    echo ""
    echo "正在重置所有用户密码..."
    
    # 备份数据库
    BACKUP_FILE="${DATABASE}.backup.$(date +%Y%m%d_%H%M%S)"
    cp "$DATABASE" "$BACKUP_FILE"
    echo -e "${GREEN}[INFO]${NC} 数据库已备份到: $BACKUP_FILE"
    
    # 更新密码
    sqlite3 "$DATABASE" <<EOF
UPDATE users
SET password_hash = '$PASSWORD_HASH', updated_at = CURRENT_TIMESTAMP;
EOF
    
    if [ $? -eq 0 ]; then
        AFFECTED=$(sqlite3 "$DATABASE" "SELECT changes();")
        echo -e "${GREEN}[SUCCESS]${NC} 已重置 $AFFECTED 个用户的密码"
        echo "新密码: $DEFAULT_PASSWORD"
    else
        echo -e "${RED}[ERROR]${NC} 密码重置失败"
        exit 1
    fi
}

# 验证重置结果
verify_reset() {
    echo ""
    echo "验证重置结果..."
    
    HASH_COUNT=$(sqlite3 "$DATABASE" "SELECT COUNT(*) FROM users WHERE password_hash = '$PASSWORD_HASH';")
    TOTAL_COUNT=$(sqlite3 "$DATABASE" "SELECT COUNT(*) FROM users;")
    
    if [ "$HASH_COUNT" -eq "$TOTAL_COUNT" ]; then
        echo -e "${GREEN}[SUCCESS]${NC} 验证通过：所有用户的密码哈希正确"
    else
        echo -e "${YELLOW}[WARNING]${NC} 验证警告：部分用户的密码哈希可能不正确"
        echo "正确哈希数量: $HASH_COUNT / $TOTAL_COUNT"
    fi
}

# 显示总结
show_summary() {
    echo ""
    echo "================================================================================"
    echo "操作完成！"
    echo "================================================================================"
    echo ""
    echo "📝 提示："
    echo "  - 所有用户的新密码为: $DEFAULT_PASSWORD"
    echo "  - 建议用户首次登录后立即修改密码"
    echo "  - 数据库已备份到: $BACKUP_FILE"
    echo ""
}

# 主函数
main() {
    print_banner
    
    check_database
    
    # 获取用户数量
    USER_COUNT=$(get_user_count)
    echo "当前用户数量: $USER_COUNT"
    
    if [ "$USER_COUNT" -eq 0 ]; then
        echo -e "${YELLOW}[WARNING]${NC} 数据库中没有用户，无需重置密码"
        exit 0
    fi
    
    # 显示用户列表
    show_users
    
    # 检查是否是强制模式
    FORCE="no"
    if [ "$1" == "--force" ]; then
        FORCE="yes"
        echo -e "${YELLOW}[INFO]${NC} 强制模式，跳过确认"
    fi
    
    # 重置密码
    reset_all_passwords
    
    # 验证结果
    verify_reset
    
    # 显示总结
    show_summary
}

# 执行主函数
main "$@"

"""
数据库统计信息展示
简洁展示各表的记录数和关键信息
"""
import sqlite3

DATABASE_PATH = "auth.db"


def get_table_stats(conn, table_name):
    """获取表统计信息"""
    try:
        cursor = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        return count
    except:
        return 0


def show_sample_data(conn, table_name, limit=3):
    """显示样本数据"""
    try:
        cursor = conn.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]

        cursor = conn.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
        rows = cursor.fetchall()

        if rows:
            print(f"  样本数据（前{limit}条）：")
            for row in rows:
                values = []
                for col, val in zip(columns, row):
                    if val is None:
                        val = "NULL"
                    elif isinstance(val, str) and len(val) > 30:
                        val = val[:30] + "..."
                    elif isinstance(val, bytes):
                        val = f"<{len(val)} bytes>"
                    values.append(f"{val}")
                print(f"    {', '.join(values[:5])}...")  # 只显示前5列
        else:
            print(f"  （无数据）")
    except Exception as e:
        print(f"  错误：{e}")


def main():
    """主函数"""
    print("="*80)
    print("媄月商业艺术 - 数据库统计信息")
    print("="*80)

    conn = sqlite3.connect(DATABASE_PATH)

    try:
        # 获取所有表名
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]

        print(f"\n数据库中共有 {len(tables)} 个表\n")

        # 按类别分组
        categories = {
            "【核心系统表】": ['users', 'roles', 'permissions', 'user_roles', 'role_permissions', 'audit_logs'],
            "【会话管理】": ['sessions'],
            "【访客管理】": ['visitors', 'team_members'],
            "【生态机制】": ['member_levels', 'partners', 'projects', 'project_participations',
                          'referrals', 'commissions', 'dividend_pools', 'dividends'],
            "【项目参与】": ['opportunities', 'opportunity_participations'],
            "【团队组建】": ['teams', 'team_members_v2', 'team_milestones'],
            "【专家管理】": ['experts', 'team_experts', 'expert_engagements']
        }

        total_records = 0

        for category, expected_tables in categories.items():
            print(f"\n{category}")
            print("-" * 80)

            found_tables = [t for t in expected_tables if t in tables]
            if found_tables:
                for table in found_tables:
                    count = get_table_stats(conn, table)
                    total_records += count
                    print(f"  {table:30s} : {count:>6} 条记录")

                    # 如果有数据，显示样本
                    if count > 0:
                        show_sample_data(conn, table)
            else:
                print("  （无相关表）")

        # 显示其他未分类的表
        all_categorized = []
        for category_tables in categories.values():
            all_categorized.extend(category_tables)

        uncategorized = [t for t in tables if t not in all_categorized]
        if uncategorized:
            print(f"\n【其他表】")
            print("-" * 80)
            for table in uncategorized:
                count = get_table_stats(conn, table)
                total_records += count
                print(f"  {table:30s} : {count:>6} 条记录")

        print("\n" + "="*80)
        print(f"数据库总记录数：{total_records} 条")
        print("="*80)

    finally:
        conn.close()


if __name__ == "__main__":
    main()

"""
数据库内容展示脚本
展示所有表的数据
"""
import sqlite3
from datetime import datetime

DATABASE_PATH = "auth.db"


def display_table_data(conn, table_name, limit=10):
    """显示表数据"""
    print(f"\n{'='*80}")
    print(f"表名：{table_name}")
    print(f"{'='*80}")

    try:
        # 获取列信息
        cursor = conn.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"列：{', '.join(columns)}")

        # 获取记录数
        cursor = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
        total_count = cursor.fetchone()[0]
        print(f"总记录数：{total_count}")

        # 获取数据
        cursor = conn.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
        rows = cursor.fetchall()

        if rows:
            print(f"\n前{min(limit, total_count)}条记录：")
            for i, row in enumerate(rows, 1):
                print(f"\n--- 记录 {i} ---")
                for j, (col, value) in enumerate(zip(columns, row)):
                    # 处理长文本
                    if isinstance(value, str) and len(value) > 50:
                        value = value[:50] + "..."
                    # 处理datetime
                    if value and isinstance(value, str) and value.startswith('202'):
                        pass
                    print(f"  {col}: {value}")
        else:
            print("（无数据）")

    except Exception as e:
        print(f"错误：{str(e)}")


def main():
    """主函数"""
    print("="*80)
    print("媄月商业艺术 - 数据库内容展示")
    print(f"数据库路径：{DATABASE_PATH}")
    print(f"查询时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row

    try:
        # 获取所有表名
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]

        print(f"\n数据库中共有 {len(tables)} 个表：")
        print(", ".join(tables))

        # 按类别展示表
        print("\n\n" + "="*80)
        print("【核心系统表】")
        print("="*80)

        core_tables = ['users', 'roles', 'permissions', 'user_roles', 'role_permissions', 'audit_logs']
        for table in core_tables:
            if table in tables:
                display_table_data(conn, table)

        print("\n\n" + "="*80)
        print("【访客管理表】")
        print("="*80)

        visitor_tables = ['visitors', 'team_members', 'memberships']
        for table in visitor_tables:
            if table in tables:
                display_table_data(conn, table)

        print("\n\n" + "="*80)
        print("【生态机制表】")
        print("="*80)

        ecosystem_tables = ['member_levels', 'partners', 'projects', 'project_participations',
                          'referrals', 'commissions', 'dividend_pools', 'dividends']
        for table in ecosystem_tables:
            if table in tables:
                display_table_data(conn, table)

        print("\n\n" + "="*80)
        print("【项目参与和团队组建表】")
        print("="*80)

        project_tables = ['opportunities', 'opportunity_participations', 'teams',
                         'team_members', 'team_milestones', 'experts', 'team_experts',
                         'expert_engagements']
        for table in project_tables:
            if table in tables:
                display_table_data(conn, table)

        print("\n\n" + "="*80)
        print("展示完成")
        print("="*80)

    finally:
        conn.close()


if __name__ == "__main__":
    main()

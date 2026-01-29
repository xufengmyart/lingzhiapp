"""
媄月商业艺术 - 数据库连接测试脚本
以许锋身份连接数据库并查询信息
"""

import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000"

# 许锋账号信息
XUFENG_CREDENTIALS = {
    "username": "xufeng@meiyue.com",
    "password": "Xu@2026"
}


class DatabaseConnector:
    """数据库连接器"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.token = None
        self.user_info = None
    
    def login(self, username: str, password: str) -> bool:
        """登录系统"""
        print(f"正在登录: {username}")
        
        response = requests.post(
            f"{self.base_url}/api/auth/login",
            data={"username": username, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.user_info = data.get("user")
            print(f"✓ 登录成功！用户: {self.user_info.get('name')}")
            return True
        else:
            print(f"✗ 登录失败: {response.text}")
            return False
    
    def get_headers(self) -> dict:
        """获取请求头（包含token）"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def get_database_stats(self):
        """获取数据库统计信息"""
        print("\n" + "="*60)
        print("📊 数据库统计信息")
        print("="*60)
        
        response = requests.get(
            f"{self.base_url}/api/database/stats",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            stats = response.json()
            print(f"用户数量: {stats['users_count']}")
            print(f"角色数量: {stats['roles_count']}")
            print(f"权限数量: {stats['permissions_count']}")
            print(f"用户角色关系数: {stats['user_roles_count']}")
            print(f"角色权限关系数: {stats['role_permissions_count']}")
            print(f"数据库大小: {stats['database_size']}")
            return stats
        else:
            print(f"✗ 获取统计信息失败: {response.text}")
            return None
    
    def get_users(self, limit: int = 20):
        """获取用户列表"""
        print("\n" + "="*60)
        print("👥 用户列表")
        print("="*60)
        
        response = requests.get(
            f"{self.base_url}/api/database/users?limit={limit}",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            users = response.json()
            print(f"ID\t姓名\t\t邮箱\t\t\t\t职位\tCEO\t角色")
            print("-" * 100)
            for user in users:
                ceo_mark = "✓" if user['is_ceo'] else " "
                roles_str = ", ".join(user['roles'][:2]) + ("..." if len(user['roles']) > 2 else "")
                print(f"{user['id']}\t{user['name']}\t\t{user['email']}\t{user['position']}\t{ceo_mark}\t{roles_str}")
            return users
        else:
            print(f"✗ 获取用户列表失败: {response.text}")
            return None
    
    def get_current_user(self):
        """获取当前登录用户信息"""
        print("\n" + "="*60)
        print("👤 当前用户信息")
        print("="*60)
        
        response = requests.get(
            f"{self.base_url}/api/database/current-user",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"ID: {user_info['id']}")
            print(f"姓名: {user_info['name']}")
            print(f"邮箱: {user_info['email']}")
            print(f"职位: {user_info['position']}")
            print(f"CEO: {'是' if user_info['is_ceo'] else '否'}")
            print(f"微信: {user_info.get('wechat', '未设置')}")
            print(f"\n角色:")
            for role in user_info['roles']:
                print(f"  - {role['name']} ({role['english_name']}, 级别{role['level']})")
            print(f"\n权限数量: {len(user_info['permissions'])}")
            print(f"权限列表: {', '.join(user_info['permissions'][:10])}")
            if len(user_info['permissions']) > 10:
                print(f"  ... (共{len(user_info['permissions'])}个权限)")
            return user_info
        else:
            print(f"✗ 获取当前用户信息失败: {response.text}")
            return None
    
    def get_roles(self):
        """获取角色列表"""
        print("\n" + "="*60)
        print("🎭 角色列表")
        print("="*60)
        
        response = requests.get(
            f"{self.base_url}/api/database/roles",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            roles = response.json()
            print(f"ID\t级别\t角色名称\t\t英文名\t\t\t权限数\t用户数")
            print("-" * 90)
            for role in roles:
                print(f"{role['id']}\t{role['level']}\t{role['name']}\t\t{role['english_name']}\t{role['permissions_count']}\t{role['users_count']}")
            return roles
        else:
            print(f"✗ 获取角色列表失败: {response.text}")
            return None
    
    def get_permissions(self):
        """获取权限列表"""
        print("\n" + "="*60)
        print("🔑 权限列表")
        print("="*60)
        
        response = requests.get(
            f"{self.base_url}/api/database/permissions?limit=50",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            permissions = response.json()
            print(f"ID\t权限代码\t\t\t权限名称\t\t\t拥有角色")
            print("-" * 100)
            for perm in permissions:
                roles_str = ", ".join(perm['roles'][:2]) + ("..." if len(perm['roles']) > 2 else "")
                print(f"{perm['id']}\t{perm['code'][:20]}\t\t{perm['name'][:15]}\t\t{roles_str}")
            return permissions
        else:
            print(f"✗ 获取权限列表失败: {response.text}")
            return None


def main():
    """主函数"""
    print("="*60)
    print("媄月商业艺术 - 数据库连接测试")
    print("以许锋身份连接数据库")
    print("="*60)
    
    # 创建连接器
    connector = DatabaseConnector(BASE_URL)
    
    # 登录
    if not connector.login(
        username=XUFENG_CREDENTIALS["username"],
        password=XUFENG_CREDENTIALS["password"]
    ):
        print("无法登录，请检查API服务是否启动")
        return
    
    # 获取当前用户信息
    connector.get_current_user()
    
    # 获取数据库统计信息
    connector.get_database_stats()
    
    # 获取用户列表
    connector.get_users()
    
    # 获取角色列表
    connector.get_roles()
    
    # 获取权限列表
    connector.get_permissions()
    
    print("\n" + "="*60)
    print("✓ 数据库连接测试完成")
    print("="*60)


if __name__ == "__main__":
    main()

"""
测试登录自动签到功能
"""

import sys
import os

# 添加项目路径到 sys.path
workspace_path = os.getenv('COZE_WORKSPACE_PATH', '/workspace/projects')
src_path = os.path.join(workspace_path, 'src')
if workspace_path not in sys.path:
    sys.path.insert(0, workspace_path)
if src_path not in sys.path:
    sys.path.insert(0, src_path)


def test_auto_check_in_on_login():
    """测试登录自动签到"""
    
    print("="*70)
    print("登录自动签到测试")
    print("="*70)
    print()
    
    # 测试用户ID（许锋）
    user_id = 1
    
    from storage.database.auto_check_in_service import trigger_auto_check_in_on_login, AutoCheckInService
    
    print(f"📋 测试用户ID: {user_id}")
    print()
    
    # 创建自动签到服务
    auto_check_in_service = AutoCheckInService()
    
    # 模拟登录触发自动签到
    print("🔐 模拟用户登录...")
    result = auto_check_in_service.auto_check_in_on_login(user_id)
    
    print()
    print("="*70)
    print("自动签到结果")
    print("="*70)
    print()
    
    print(f"成功: {result['success']}")
    print(f"消息: {result['message']}")
    print(f"已签到: {result['already_checked']}")
    
    if result['check_in']:
        print(f"签到记录: {result['check_in']}")
        print(f"获得灵值: {result['check_in'].lingzhi_reward}")
    
    print()
    
    # 格式化消息
    formatted_message = auto_check_in_service.format_auto_check_in_message(user_id, result)
    print(formatted_message)
    
    print()
    print("="*70)
    print("✅ 测试完成")
    print("="*70)


def test_user_login():
    """测试用户登录"""
    
    print()
    print("="*70)
    print("用户登录测试")
    print("="*70)
    print()
    
    from tools.login_tool import user_login
    
    # 测试用户登录
    email = "xufeng@meiyueart.cn"
    password = "xf.071214"
    
    print(f"📋 登录信息:")
    print(f"   邮箱: {email}")
    print(f"   密码: {'*' * len(password)}")
    print()
    
    print("🔐 执行登录...")
    result = user_login(email, password)
    
    print(result)
    
    print()
    print("="*70)
    print("✅ 测试完成")
    print("="*70)


if __name__ == "__main__":
    test_auto_check_in_on_login()
    print()
    test_user_login()

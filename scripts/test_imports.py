"""
测试签到导入修复
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


def test_imports():
    """测试导入是否正常"""
    
    print("="*70)
    print("导入修复验证")
    print("="*70)
    print()
    
    try:
        # 测试导入签到管理器
        print("1️⃣ 测试导入 CheckInManager...")
        from storage.database.check_in_manager import CheckInManager
        print("   ✅ CheckInManager 导入成功")
        print()
        
        # 测试导入签到工具
        print("2️⃣ 测试导入签到工具...")
        from tools.check_in_tool import check_in, get_check_in_history
        print("   ✅ 签到工具导入成功")
        print()
        
        # 测试创建管理器实例
        print("3️⃣ 测试创建 CheckInManager 实例...")
        manager = CheckInManager()
        print("   ✅ CheckInManager 实例创建成功")
        print()
        
        print("4️⃣ 测试管理器方法...")
        print(f"   每日奖励: {manager.daily_reward}灵值")
        print(f"   时区: {manager.timezone}")
        print("   ✅ 管理器方法正常")
        print()
        
        print("="*70)
        print("✅ 所有导入测试通过！")
        print("="*70)
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print()
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        print()
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_imports()
    exit(0 if success else 1)

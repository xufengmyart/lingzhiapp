"""
测试签到功能
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

from coze_coding_dev_sdk.database import get_session
from storage.database.check_in_manager import CheckInManager


def test_check_in():
    """测试签到功能"""
    
    print("="*70)
    print("签到功能测试")
    print("="*70)
    print()
    
    # 获取数据库会话
    db = get_session()
    
    try:
        # 创建签到管理器
        manager = CheckInManager()
        
        # 测试用户ID（许锋）
        user_id = 1
        
        print(f"📋 测试用户ID: {user_id}")
        print()
        
        # 检查今天是否已签到
        has_checked_in = manager.has_checked_in_today(db, user_id)
        
        print(f"🔍 签到状态检查:")
        print(f"   今天是否已签到: {'是' if has_checked_in else '否'}")
        print()
        
        if has_checked_in:
            print("⚠️  今天已经签到过了，无法重复签到")
            
            # 获取签到历史
            history = manager.format_check_in_history(db, user_id, days=7)
            print()
            print(history)
        else:
            # 执行签到
            print("📝 执行签到...")
            success, message, check_in = manager.check_in(db, user_id)
            
            if success:
                print()
                print("="*70)
                print("✅ 签到成功!")
                print("="*70)
                print()
                print(f"奖励: {check_in.lingzhi_reward}灵值")
                print(f"时间: {check_in.created_at}")
                print()
                print(message)
                
                # 获取签到历史
                history = manager.format_check_in_history(db, user_id, days=7)
                print()
                print(history)
            else:
                print()
                print("❌ 签到失败!")
                print(f"原因: {message}")
        
        # 获取签到统计
        print()
        print("="*70)
        print("签到统计")
        print("="*70)
        
        total_count = manager.get_user_check_in_count(db, user_id, days=30)
        total_lingzhi = manager.get_user_total_lingzhi_from_check_in(db, user_id)
        today_count = manager.get_today_check_in_count(db)
        
        print(f"您的签到统计:")
        print(f"   最近30天签到次数: {total_count}")
        print(f"   累计获得灵值: {total_lingzhi}")
        print()
        print(f"平台统计:")
        print(f"   今日签到人数: {today_count}")
        print(f"   今日发放灵值: {today_count * manager.daily_reward}")
        
        print()
        print("="*70)
        print("✅ 测试完成")
        print("="*70)
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'db' in locals():
            db.close()


if __name__ == "__main__":
    test_check_in()

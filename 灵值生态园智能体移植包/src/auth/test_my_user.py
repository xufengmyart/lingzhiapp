"""
灵值生态园用户管理系统 - 功能测试脚本
测试所有核心功能模块

版本: v1.0
更新日期: 2026年1月25日
"""

import os
import sys
from decimal import Decimal
from datetime import datetime

# 添加父目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# 导入管理模块
from src.auth.my_user import MyUser, TransactionType
from src.auth.referral_manager import ReferralManager
from src.auth.project_manager import ProjectManager
from src.auth.dividend_manager import DividendManager


def test_user_management():
    """测试用户管理功能"""
    print("\n" + "="*80)
    print("测试 1: 用户管理功能")
    print("="*80)
    
    user1_id = None
    user2_id = None
    
    with MyUser() as user_mgr:
        # 创建测试用户
        print("\n[1.1] 创建测试用户...")
        # 使用时间戳生成唯一邮箱
        import time
        timestamp = int(time.time())
        
        user1 = user_mgr.create_user(
            name="测试用户A",
            email=f"test_a_{timestamp}@example.com",
            password_hash="hashed_password_a",
            phone="13800138001",
            wechat="wechat_a"
        )
        
        if user1:
            print(f"✅ 用户创建成功: {user1.name} (ID: {user1.id})")
            user1_id = user1.id
        else:
            print("❌ 用户创建失败")
            return False
        
        # 获取用户信息
        print("\n[1.2] 获取用户信息...")
        retrieved_user = user_mgr.get_user(user1.id)
        if retrieved_user:
            print(f"✅ 用户信息获取成功: {retrieved_user.name}")
        else:
            print("❌ 用户信息获取失败")
            return False
        
        # 获取贡献值
        print("\n[1.3] 获取贡献值...")
        contribution = user_mgr.get_contribution_value(user1.id)
        print(f"✅ 当前贡献值: {contribution}")
        
        # 增加贡献值
        print("\n[1.4] 增加贡献值...")
        success = user_mgr.add_contribution(
            user1.id,
            100.0,
            TransactionType.TASK_REWARD,
            "新手任务奖励"
        )
        
        if success:
            new_contribution = user_mgr.get_contribution_value(user1.id)
            print(f"✅ 贡献值增加成功: {contribution} -> {new_contribution}")
        else:
            print("❌ 贡献值增加失败")
            return False
        
        # 创建第二个测试用户
        print("\n[1.5] 创建第二个测试用户...")
        user2 = user_mgr.create_user(
            name="测试用户B",
            email=f"test_b_{timestamp}@example.com",
            password_hash="hashed_password_b",
            phone="13800138002"
        )
        
        if user2:
            print(f"✅ 用户创建成功: {user2.name} (ID: {user2.id})")
            user2_id = user2.id
        else:
            print("❌ 用户创建失败")
            return False
    
    return True, user1_id, user2_id


def test_referral_management(user1_id, user2_id):
    """测试推荐管理功能"""
    print("\n" + "="*80)
    print("测试 2: 推荐管理功能")
    print("="*80)
    
    with ReferralManager() as ref_mgr:
        # 创建推荐关系
        print("\n[2.1] 创建推荐关系...")
        success = ref_mgr.create_referral_relationship(
            referrer_id=user1_id,
            referee_id=user2_id
        )
        
        if success:
            print(f"✅ 推荐关系创建成功: 用户{user1_id} -> 用户{user2_id}")
        else:
            print("❌ 推荐关系创建失败")
            return False
        
        # 获取推荐统计
        print("\n[2.2] 获取推荐统计...")
        stats = ref_mgr.get_referral_stats(user1_id)
        print(f"✅ 推荐统计: {stats}")
        
        # 获取推荐记录
        print("\n[2.3] 获取推荐记录...")
        referrals = ref_mgr.get_referrals_by_user(user1_id)
        print(f"✅ 推荐记录数量: {len(referrals)}")
    
    return True


def test_project_management(user1_id):
    """测试项目管理功能"""
    print("\n" + "="*80)
    print("测试 3: 项目管理功能")
    print("="*80)
    
    with ProjectManager() as proj_mgr:
        # 创建项目
        print("\n[3.1] 创建测试项目...")
        project = proj_mgr.create_project(
            project_name="唐风茶馆品牌IP项目",
            project_code="TFCT_TEST_001",
            description="将唐代茶文化转化为现代茶馆品牌IP",
            project_type="cultural",
            total_investment=Decimal("100000"),  # 10万元
            profit_distribution_rate=0.8,
            min_participation_amount=Decimal("1000"),
            max_participants=100
        )
        
        if project:
            print(f"✅ 项目创建成功: {project.project_name} (ID: {project.id})")
        else:
            print("❌ 项目创建失败")
            return False
        
        # 参与项目（需要先给用户足够的贡献值）
        print("\n[3.2] 准备参与项目...")
        with MyUser() as user_mgr:
            # 增加足够贡献值
            user_mgr.add_contribution(
                user1_id,
                20000.0,  # 2万元贡献值
                TransactionType.TASK_REWARD,
                "测试奖励"
            )
            
            contribution = user_mgr.get_contribution_value(user1_id)
            print(f"✅ 当前贡献值: {contribution}")
        
        # 参与项目
        print("\n[3.3] 参与项目...")
        success = proj_mgr.participate_project(
            user_id=user1_id,
            project_id=project.id,
            participation_amount=Decimal("5000")  # 参与5000元
        )
        
        if success:
            print(f"✅ 项目参与成功: 项目ID={project.id}, 金额=5000元")
        else:
            print("❌ 项目参与失败")
            return False
        
        # 获取项目统计
        print("\n[3.4] 获取项目统计...")
        stats = proj_mgr.get_project_stats(project.id)
        print(f"✅ 项目统计: {stats}")
    
    return True, project.id


def test_dividend_management(user1_id):
    """测试分红管理功能"""
    print("\n" + "="*80)
    print("测试 4: 分红管理功能")
    print("="*80)
    
    with DividendManager() as div_mgr:
        # 创建分红池
        print("\n[4.1] 创建分红池...")
        pool = div_mgr.create_dividend_pool(
            pool_name="专家分红池测试",
            pool_type="expert",
            initial_amount=Decimal("10000")  # 1万元
        )
        
        if pool:
            print(f"✅ 分红池创建成功: {pool.pool_name} (ID: {pool.id})")
        else:
            print("❌ 分红池创建失败")
            return False
        
        # 向分红池注资
        print("\n[4.2] 向分红池注资...")
        success = div_mgr.add_to_dividend_pool(
            pool_id=pool.id,
            amount=Decimal("5000"),
            description="测试注资"
        )
        
        if success:
            print(f"✅ 分红池注资成功")
        else:
            print("❌ 分红池注资失败")
            return False
        
        # 获取分红池统计
        print("\n[4.3] 获取分红池统计...")
        stats = div_mgr.get_dividend_stats(pool.id)
        print(f"✅ 分红池统计: {stats}")
    
    return True, pool.id


def test_integration(user1_id, project_id, pool_id):
    """测试系统集成"""
    print("\n" + "="*80)
    print("测试 5: 系统集成")
    print("="*80)
    
    with MyUser() as user_mgr:
        # 获取当前贡献值
        print("\n[5.1] 获取当前贡献值...")
        contribution = user_mgr.get_contribution_value(user1_id)
        print(f"✅ 当前贡献值: {contribution}")
        
        # 获取会员级别
        print("\n[5.2] 获取会员级别...")
        user_level = user_mgr.get_member_level(user1_id)
        if user_level:
            print(f"✅ 会员级别信息:")
            print(f"   - 贡献值: {user_level.contribution_value}")
            print(f"   - 累计收益: {user_level.total_earned}")
            print(f"   - 分红收益: {user_level.total_dividend_earned}")
            print(f"   - 股权比例: {user_level.equity_percentage}%")
        else:
            print("⚠️  会员级别不存在")
    
    return True


def run_all_tests():
    """运行所有测试"""
    print("="*80)
    print("灵值生态园用户管理系统 - 功能测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    results = []
    
    try:
        # 测试用户管理
        result = test_user_management()
        if isinstance(result, tuple):
            success, user1_id, user2_id = result
        else:
            success = False
        
        results.append(("用户管理功能", success))
        
        if not success:
            print("\n❌ 用户管理功能测试失败，终止后续测试")
            return False
        
        # 测试推荐管理
        success = test_referral_management(user1_id, user2_id)
        results.append(("推荐管理功能", success))
        
        if not success:
            print("\n❌ 推荐管理功能测试失败，终止后续测试")
            return False
        
        # 测试项目管理
        result = test_project_management(user1_id)
        if isinstance(result, tuple):
            success, project_id = result
        else:
            success = False
        
        results.append(("项目管理功能", success))
        
        if not success:
            print("\n❌ 项目管理功能测试失败，终止后续测试")
            return False
        
        # 测试分红管理
        result = test_dividend_management(user1_id)
        if isinstance(result, tuple):
            success, pool_id = result
        else:
            success = False
        
        results.append(("分红管理功能", success))
        
        if not success:
            print("\n❌ 分红管理功能测试失败，终止后续测试")
            return False
        
        # 测试系统集成
        success = test_integration(user1_id, project_id, pool_id)
        results.append(("系统集成", success))
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # 汇总测试结果
    print("\n" + "="*80)
    print("测试结果汇总")
    print("="*80)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{name:<20} {status}")
    
    print("\n" + "="*80)
    print(f"总测试项: {total}")
    print(f"通过: {passed}")
    print(f"失败: {total - passed}")
    print("="*80)
    
    if passed == total:
        print("\n🎉 所有测试通过！")
        print("="*80)
        return True
    else:
        print("\n⚠️  部分测试失败")
        print("="*80)
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

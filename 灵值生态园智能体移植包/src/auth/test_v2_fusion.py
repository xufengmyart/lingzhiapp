"""
V2.0 融合版 - 综合测试脚本

测试内容：
1. 会员级别体系（4级合伙人）
2. 三级推荐佣金系统
3. 三维贡献值模型
4. 系统自动运营规则
5. 整体集成测试
"""

import sys
import os
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from contribution_manager_v2 import ContributionManagerV2, ContributionType
from referral_commission_manager_v2 import ReferralCommissionManagerV2
from auto_operation_manager import AutoOperationManager
from enums.partner_level import PartnerLevelType, get_partner_level_config


class V2FusionTestSuite:
    """V2.0融合版测试套件"""
    
    def __init__(self, db_url: str = "sqlite:///auth.db"):
        self.db_url = db_url
        self.engine = create_engine(db_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)
        self.session = None
        
        self.results = {
            "passed": 0,
            "failed": 0,
            "total": 0
        }
    
    def setup(self):
        """设置测试环境"""
        self.session = self.Session()
        print("="*70)
        print("V2.0 融合版 - 综合测试")
        print("="*70)
        print(f"\n测试开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"数据库：{self.db_url}\n")
    
    def teardown(self):
        """清理测试环境"""
        if self.session:
            self.session.close()
        
        print("\n" + "="*70)
        print("测试总结")
        print("="*70)
        print(f"总测试数：{self.results['total']}")
        print(f"通过：{self.results['passed']} ✓")
        print(f"失败：{self.results['failed']} ✗")
        print(f"通过率：{self.results['passed']/self.results['total']*100:.1f}%")
        print(f"\n测试结束时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
    
    def test(self, name: str, func):
        """执行测试"""
        self.results['total'] += 1
        print(f"\n测试 {self.results['total']}：{name}")
        print("-" * 70)
        
        try:
            func()
            self.results['passed'] += 1
            print(f"✓ 通过")
        except Exception as e:
            self.results['failed'] += 1
            print(f"✗ 失败：{str(e)}")
            import traceback
            traceback.print_exc()
    
    def test_member_levels(self):
        """测试1：会员级别体系（4级合伙人）"""
        # 查询合伙人级别
        levels = self.session.execute(
            text("""
                SELECT level, name, min_contribution_value, benefits
                FROM member_levels
                ORDER BY level
            """)
        ).fetchall()
        
        print(f"\n合伙人级别数量：{len(levels)}")
        
        expected_levels = [
            (1, "普通用户", 0.0),
            (2, "普通合伙人", 50000.0),
            (3, "高级合伙人", 100000.0),
            (4, "创始合伙人", 200000.0)
        ]
        
        for i, (level, name, min_contribution, benefits) in enumerate(levels):
            expected = expected_levels[i]
            print(f"\n  [{level}] {name}")
            print(f"     最小贡献值：{min_contribution}")
            print(f"     权益：{benefits[:50]}...")
            
            assert int(level) == expected[0], f"级别序号不匹配：{level} vs {expected[0]}"
            assert name == expected[1], f"级别名称不匹配：{name} vs {expected[1]}"
            assert min_contribution == expected[2], f"最小贡献值不匹配"
        
        assert len(levels) == 4, f"合伙人级别数量不正确：{len(levels)} vs 4"
    
    def test_three_level_commission(self):
        """测试2：三级推荐佣金系统"""
        manager = ReferralCommissionManagerV2(self.session)
        
        # 测试推荐佣金计算
        # 假设用户2获得了1000贡献值，用户1是推荐人
        contribution_earned = 1000.0
        commissions = manager.calculate_three_level_commission(
            referrer_id=1,
            referee_id=2,
            contribution_earned=contribution_earned
        )
        
        print(f"\n被推荐人获得贡献值：{contribution_earned}")
        print(f"推荐层级数量：{len(commissions)}")
        
        total_commission = 0.0
        for commission in commissions:
            print(f"\n  第{commission['level']}级推荐：")
            print(f"     推荐人ID：{commission['referrer_id']}")
            print(f"     佣金比例：{commission['rate']*100}%")
            print(f"     佣金金额：{commission['amount']:.2f}")
            total_commission += commission['amount']
        
        print(f"\n  总佣金：{total_commission:.2f}")
        
        # 验证佣金计算
        if len(commissions) > 0:
            assert commissions[0]['rate'] == 0.10, "一级推荐佣金比例应为10%"
        if len(commissions) > 1:
            assert commissions[1]['rate'] == 0.05, "二级推荐佣金比例应为5%"
        if len(commissions) > 2:
            assert commissions[2]['rate'] == 0.03, "三级推荐佣金比例应为3%"
    
    def test_contribution_model(self):
        """测试3：三维贡献值模型"""
        manager = ContributionManagerV2(self.session)
        
        # 获取用户贡献值
        user_id = 1
        contribution = manager.get_user_contribution(user_id)
        
        print(f"\n用户{user_id}的贡献值：")
        print(f"  累计贡献值：{contribution['cumulative_contribution']}")
        print(f"  项目贡献值：{contribution['project_contribution']}")
        print(f"  剩余贡献值：{contribution['remaining_contribution']}")
        print(f"  消费贡献值：{contribution['consumed_contribution']}")
        
        # 验证贡献值类型
        assert 'cumulative_contribution' in contribution
        assert 'project_contribution' in contribution
        assert 'remaining_contribution' in contribution
        
        # 测试项目贡献值计算
        difficulty = 1.5
        quality = 9.0
        participation = 0.8
        project_contribution = manager.calculate_project_contribution(
            difficulty_coefficient=difficulty,
            quality_score=quality,
            participation_rate=participation
        )
        
        expected = difficulty * quality * participation * 10
        print(f"\n项目贡献值计算：")
        print(f"  难度系数：{difficulty}")
        print(f"  质量评分：{quality}")
        print(f"  参与度：{participation}")
        print(f"  计算结果：{project_contribution:.2f}")
        print(f"  预期结果：{expected:.2f}")
        
        assert abs(project_contribution - expected) < 0.01, "项目贡献值计算不正确"
    
    def test_auto_operations(self):
        """测试4：系统自动运营规则"""
        manager = AutoOperationManager(self.session)
        
        # 测试新用户注册
        print("\n1. 新用户注册奖励：")
        test_user_id = 999  # 使用一个不存在的用户ID进行测试
        
        # 先检查用户是否存在
        user_exists = self.session.execute(
            text("SELECT id FROM users WHERE id = :user_id"),
            {"user_id": test_user_id}
        ).fetchone()
        
        if user_exists:
            result = manager.handle_user_login(test_user_id)
            print(f"  连续登录天数：{result['consecutive_login_days']}")
        else:
            print(f"  测试用户不存在，跳过登录测试")
        
        # 测试活跃用户勋章
        print("\n2. 活跃用户勋章检查：")
        result = manager.check_active_user_badges()
        print(f"  活跃用户数：{result['active_users_count']}")
        print(f"  颁发勋章数：{result['badges_granted']}")
        
        # 测试沉睡用户
        print("\n3. 沉睡用户检查：")
        result = manager.check_dormant_users()
        print(f"  沉睡用户数：{result['dormant_users_count']}")
        print(f"  创建奖励数：{result['rewards_created']}")
        
        # 测试项目超时
        print("\n4. 项目超时检查：")
        result = manager.check_project_timeout()
        print(f"  超时项目数：{result['timeout_participations']}")
        print(f"  惩罚用户数：{result['penalized_count']}")
        
        # 验证所有结果都是字典
        assert isinstance(result, dict)
    
    def test_integration(self):
        """测试5：整体集成测试"""
        print("\nV2.0融合版功能验证：")
        
        # 1. 验证数据库表
        print("\n1. 数据库表验证：")
        tables = self.session.execute(
            text("SELECT name FROM sqlite_master WHERE type='table'")
        ).fetchall()
        
        required_tables = [
            'users',
            'member_levels',
            'user_contributions_v2',
            'user_active_badges',
            'project_assignments',
            'pending_rewards',
            'referral_commissions'
        ]
        
        for table_name in required_tables:
            table_exists = any(t[0] == table_name for t in tables)
            status = "✓" if table_exists else "✗"
            print(f"  {status} {table_name}")
            assert table_exists, f"表 {table_name} 不存在"
        
        # 2. 验证用户表字段
        print("\n2. 用户表新字段验证：")
        required_fields = [
            'partner_level',
            'registration_date',
            'last_login_date',
            'consecutive_login_days',
            'direct_investment',
            'bonus_multiplier'
        ]
        
        columns = self.session.execute(
            text("PRAGMA table_info(users)")
        ).fetchall()
        
        existing_fields = [col[1] for col in columns]
        
        for field_name in required_fields:
            field_exists = field_name in existing_fields
            status = "✓" if field_exists else "✗"
            print(f"  {status} {field_name}")
            assert field_exists, f"字段 {field_name} 不存在"
        
        # 3. 验证推荐佣金表字段
        print("\n3. 推荐佣金表新字段验证：")
        required_fields = ['referral_level', 'is_upgrade_reward', 'calculation_basis']
        
        columns = self.session.execute(
            text("PRAGMA table_info(referral_commissions)")
        ).fetchall()
        
        existing_fields = [col[1] for col in columns]
        
        for field_name in required_fields:
            field_exists = field_name in existing_fields
            status = "✓" if field_exists else "✗"
            print(f"  {status} {field_name}")
            assert field_exists, f"字段 {field_name} 不存在"
        
        # 4. 验证合伙人级别数据
        print("\n4. 合伙人级别数据验证：")
        levels = self.session.execute(
            text("SELECT level_code FROM member_levels ORDER BY level")
        ).fetchall()
        
        expected_levels = ['normal_user', 'regular_partner', 'senior_partner', 'founding_partner']
        
        for i, (level_code,) in enumerate(levels):
            expected = expected_levels[i]
            status = "✓" if level_code == expected else "✗"
            print(f"  {status} {level_code}")
            assert level_code == expected, f"级别代码不匹配：{level_code} vs {expected}"
        
        print("\n✓ 所有集成测试通过！")
    
    def run_all_tests(self):
        """运行所有测试"""
        self.setup()
        
        # 执行测试
        self.test("会员级别体系（4级合伙人）", self.test_member_levels)
        self.test("三级推荐佣金系统", self.test_three_level_commission)
        self.test("三维贡献值模型", self.test_contribution_model)
        self.test("系统自动运营规则", self.test_auto_operations)
        self.test("整体集成测试", self.test_integration)
        
        self.teardown()
        
        return self.results['failed'] == 0


def main():
    """主函数"""
    test_suite = V2FusionTestSuite()
    success = test_suite.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

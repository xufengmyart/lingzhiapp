"""
V2.0 融合版 - 系统自动运营管理器

功能：
1. 新用户注册奖励（1000初始灵值）
2. 活跃用户勋章（30天连续登录+5%收益）
3. 沉睡用户唤醒（60天未登录+200唤醒奖励）
4. 项目自动分配
5. 项目超时惩罚（7天-100灵值）
"""

from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from contribution_manager_v2 import ContributionManagerV2, ContributionType


class AutoOperationManager:
    """系统自动运营管理器"""
    
    def __init__(self, session: Session):
        self.session = session
        self.contribution_manager = ContributionManagerV2(session)
    
    def handle_new_user_registration(self, user_id: int) -> Dict:
        """
        处理新用户注册（V2.0）
        
        规则：
        - 自动赠送1000初始灵值
        - 记录注册时间
        - 7天后提醒首项目
        """
        # 1. 自动赠送1000初始灵值
        self.contribution_manager.add_contribution(
            user_id=user_id,
            amount=1000.0,
            contribution_type=ContributionType.INITIAL,
            description="新用户注册奖励（V2.0）"
        )
        
        # 2. 记录注册时间
        self.session.execute(
            text("""
                UPDATE users
                SET registration_date = datetime('now'),
                    partner_level = 'normal_user'
                WHERE id = :user_id
            """),
            {"user_id": user_id}
        )
        
        # 3. 记录待发放的首项目奖励（7天内完成首项目额外奖励500）
        self._add_pending_reward(
            user_id=user_id,
            reward_type="first_project",
            amount=500.0,
            description="首项目完成奖励（7天内完成）",
            expires_days=7
        )
        
        self.session.commit()
        
        return {
            "success": True,
            "initial_contribution": 1000.0,
            "pending_first_project_reward": 500.0,
            "expires_days": 7
        }
    
    def check_active_user_badges(self) -> Dict:
        """
        检查活跃用户勋章（每天定时执行）
        
        规则：
        - 连续30天登录，获得"活跃勋章"
        - 灵值收益额外+5%
        """
        # 查找连续30天登录的用户
        active_users = self.session.execute(
            text("""
                SELECT id, name, consecutive_login_days, bonus_multiplier
                FROM users
                WHERE consecutive_login_days >= 30
            """)
        ).fetchall()
        
        granted_count = 0
        
        for user_id, name, consecutive_days, current_multiplier in active_users:
            # 检查是否已有活跃勋章
            has_badge = self.session.execute(
                text("""
                    SELECT id FROM user_active_badges
                    WHERE user_id = :user_id AND badge_type = 'active'
                    AND is_active = 1
                """),
                {"user_id": user_id}
            ).fetchone()
            
            if not has_badge:
                # 颁发活跃勋章
                self.session.execute(
                    text("""
                        INSERT INTO user_active_badges (
                            user_id, badge_type, badge_name, consecutive_days,
                            bonus_multiplier, granted_at, is_active
                        ) VALUES (
                            :user_id, 'active', '活跃用户', :consecutive_days,
                            1.05, datetime('now'), 1
                        )
                    """),
                    {
                        "user_id": user_id,
                        "consecutive_days": consecutive_days
                    }
                )
                
                # 更新用户收益倍数
                self.session.execute(
                    text("""
                        UPDATE users
                        SET bonus_multiplier = 1.05
                        WHERE id = :user_id
                    """),
                    {"user_id": user_id}
                )
                
                granted_count += 1
        
        self.session.commit()
        
        return {
            "active_users_count": len(active_users),
            "badges_granted": granted_count
        }
    
    def check_dormant_users(self) -> Dict:
        """
        检查沉睡用户（每天定时执行）
        
        规则：
        - 连续60天未登录，发送唤醒短信
        - 登录即送200灵值
        """
        # 查找连续60天未登录的用户
        dormant_users = self.session.execute(
            text("""
                SELECT id, name, phone, last_login_date
                FROM users
                WHERE (
                    last_login_date IS NULL 
                    OR last_login_date < datetime('now', '-60 days')
                )
                AND status = 'active'
            """)
        ).fetchall()
        
        processed_count = 0
        
        for user_id, name, phone, last_login in dormant_users:
            # 检查是否已有待发放的唤醒奖励
            existing_reward = self.session.execute(
                text("""
                    SELECT id FROM pending_rewards
                    WHERE user_id = :user_id AND reward_type = 'wakeup'
                    AND is_granted = 0
                """),
                {"user_id": user_id}
            ).fetchone()
            
            if not existing_reward:
                # 记录待发放的唤醒奖励
                self._add_pending_reward(
                    user_id=user_id,
                    reward_type="wakeup",
                    amount=200.0,
                    description="沉睡用户唤醒奖励（登录即发）",
                    expires_days=30
                )
                
                # 这里应该发送唤醒短信（需要集成短信服务）
                # self._send_wakeup_sms(phone, name)
                
                processed_count += 1
        
        self.session.commit()
        
        return {
            "dormant_users_count": len(dormant_users),
            "rewards_created": processed_count
        }
    
    def handle_user_login(self, user_id: int) -> Dict:
        """
        处理用户登录
        
        规则：
        - 更新最后登录时间
        - 更新连续登录天数
        - 检查并发放待发放奖励
        """
        user_info = self.session.execute(
            text("""
                SELECT last_login_date, consecutive_login_days
                FROM users
                WHERE id = :user_id
            """),
            {"user_id": user_id}
        ).fetchone()
        
        if not user_info:
            return {"success": False, "message": "用户不存在"}
        
        last_login, consecutive_days = user_info
        
        # 计算连续登录天数
        today = datetime.now().date()
        last_login_date = datetime.strptime(last_login, "%Y-%m-%d %H:%M:%S").date() if last_login else None
        
        if last_login_date:
            delta = (today - last_login_date).days
            if delta == 1:
                consecutive_days += 1
            elif delta > 1:
                consecutive_days = 1
        else:
            consecutive_days = 1
        
        # 更新登录信息
        self.session.execute(
            text("""
                UPDATE users
                SET last_login_date = datetime('now'),
                    consecutive_login_days = :consecutive_days
                WHERE id = :user_id
            """),
            {
                "consecutive_days": consecutive_days,
                "user_id": user_id
            }
        )
        
        # 检查并发放待发放奖励
        rewards_granted = []
        
        pending_rewards = self.session.execute(
            text("""
                SELECT id, reward_type, amount, description
                FROM pending_rewards
                WHERE user_id = :user_id AND is_granted = 0
            """),
            {"user_id": user_id}
        ).fetchall()
        
        for reward_id, reward_type, amount, description in pending_rewards:
            # 发放奖励
            self.contribution_manager.add_contribution(
                user_id=user_id,
                amount=amount,
                contribution_type=ContributionType.INITIAL,
                description=description
            )
            
            # 标记为已发放
            self.session.execute(
                text("""
                    UPDATE pending_rewards
                    SET is_granted = 1,
                        granted_at = datetime('now')
                    WHERE id = :reward_id
                """),
                {"reward_id": reward_id}
            )
            
            rewards_granted.append({
                "type": reward_type,
                "amount": amount,
                "description": description
            })
        
        self.session.commit()
        
        return {
            "success": True,
            "consecutive_login_days": consecutive_days,
            "rewards_granted": rewards_granted
        }
    
    def auto_assign_projects(self, user_id: int) -> List[Dict]:
        """
        自动分配项目给用户
        
        匹配因子：
        - 用户职称
        - 历史项目经验
        - 灵值等级
        
        Returns:
            推荐项目列表（最多5个）
        """
        # 获取用户画像
        user_profile = self.session.execute(
            text("""
                SELECT 
                    u.id,
                    u.name,
                    u.position,
                    u.partner_level,
                    uc.cumulative_contribution,
                    uc.project_contribution,
                    COUNT(pp.id) as project_count
                FROM users u
                LEFT JOIN user_contributions_v2 uc ON u.id = uc.user_id
                LEFT JOIN project_participations pp ON u.id = pp.partner_id
                WHERE u.id = :user_id
                GROUP BY u.id
            """),
            {"user_id": user_id}
        ).fetchone()
        
        if not user_profile:
            return []
        
        user_id, name, position, partner_level, cumulative_contribution, project_contribution, project_count = user_profile
        
        # 获取适合的项目
        suitable_projects = self.session.execute(
            text("""
                SELECT 
                    p.id,
                    p.name,
                    p.project_code,
                    p.description,
                    p.min_participation_amount,
                    p.current_participants,
                    p.max_participants,
                    p.status
                FROM projects p
                WHERE p.status = 'active'
                AND p.current_participants < p.max_participants
                AND (p.min_participation_amount IS NULL OR p.min_participation_amount <= :contribution)
                ORDER BY RANDOM()
                LIMIT 10
            """),
            {"contribution": cumulative_contribution or 0}
        ).fetchall()
        
        # 计算匹配分数并排序
        ranked_projects = []
        for project in suitable_projects:
            match_score = self._calculate_project_match_score(
                position=position,
                contribution_level=partner_level,
                project_experience=project_count
            )
            
            ranked_projects.append({
                "project_id": project[0],
                "project_name": project[1],
                "project_code": project[2],
                "description": project[3],
                "min_amount": project[4],
                "current_participants": project[5],
                "max_participants": project[6],
                "match_score": match_score
            })
        
        # 按匹配分数排序
        ranked_projects.sort(key=lambda x: x["match_score"], reverse=True)
        
        # 返回前5个
        recommended_projects = ranked_projects[:5]
        
        # 记录分配记录
        for project in recommended_projects:
            self.session.execute(
                text("""
                    INSERT INTO project_assignments (
                        user_id, project_id, assignment_type, match_score,
                        assigned_at, status
                    ) VALUES (
                        :user_id, :project_id, 'auto', :match_score,
                        datetime('now'), 'pending'
                    )
                """),
                {
                    "user_id": user_id,
                    "project_id": project["project_id"],
                    "match_score": project["match_score"]
                }
            )
        
        self.session.commit()
        
        return recommended_projects
    
    def _calculate_project_match_score(
        self,
        position: str,
        contribution_level: str,
        project_experience: int
    ) -> float:
        """
        计算项目匹配分数
        """
        score = 0.0
        
        # 职称匹配
        if position:
            if "总监" in position or "经理" in position:
                score += 0.4
            elif "专家" in position:
                score += 0.5
            else:
                score += 0.3
        
        # 贡献值等级匹配
        if contribution_level:
            if "founding" in contribution_level:
                score += 0.4
            elif "senior" in contribution_level:
                score += 0.3
            elif "regular" in contribution_level:
                score += 0.2
            else:
                score += 0.1
        
        # 项目经验匹配
        if project_experience > 10:
            score += 0.2
        elif project_experience > 5:
            score += 0.15
        elif project_experience > 2:
            score += 0.1
        else:
            score += 0.05
        
        return score
    
    def check_project_timeout(self) -> Dict:
        """
        检查项目超时（每天定时执行）
        
        规则：
        - 未完成项目超过7天，自动扣除100灵值惩罚
        """
        # 查找超过7天未完成的项目参与记录
        timeout_participations = self.session.execute(
            text("""
                SELECT 
                    pp.id,
                    pp.partner_id,
                    p.name as project_name,
                    pp.created_at
                FROM project_participations pp
                JOIN projects p ON pp.project_id = p.id
                WHERE pp.status = 'in_progress'
                AND pp.created_at < datetime('now', '-7 days')
            """)
        ).fetchall()
        
        penalized_count = 0
        
        for participation_id, user_id, project_name, created_at in timeout_participations:
            # 扣除100灵值惩罚
            try:
                self.contribution_manager.consume_contribution(
                    user_id=user_id,
                    amount=100.0,
                    description=f"项目超时惩罚：{project_name}"
                )
                
                penalized_count += 1
                
                # 这里应该发送超时通知
                # self._send_timeout_notification(user_id, project_name)
                
            except ValueError as e:
                # 余额不足，记录日志
                print(f"用户{user_id}余额不足，无法扣除超时惩罚：{str(e)}")
        
        self.session.commit()
        
        return {
            "timeout_participations": len(timeout_participations),
            "penalized_count": penalized_count
        }
    
    def _add_pending_reward(
        self,
        user_id: int,
        reward_type: str,
        amount: float,
        description: str,
        expires_days: int = 30
    ):
        """
        添加待发放奖励
        """
        self.session.execute(
            text("""
                INSERT INTO pending_rewards (
                    user_id, reward_type, amount, description,
                    created_at, expires_at, is_granted
                ) VALUES (
                    :user_id, :reward_type, :amount, :description,
                    datetime('now'), datetime('now', '+'||:expires_days||' days'), 0
                )
            """),
            {
                "user_id": user_id,
                "reward_type": reward_type,
                "amount": amount,
                "description": description,
                "expires_days": expires_days
            }
        )


# 便捷函数
def create_auto_operation_manager(session: Session) -> AutoOperationManager:
    """创建自动运营管理器实例"""
    return AutoOperationManager(session)


if __name__ == "__main__":
    # 测试代码
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    DATABASE_URL = "sqlite:///auth.db"
    engine = create_engine(DATABASE_URL, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        manager = create_auto_operation_manager(session)
        
        print("="*60)
        print("V2.0 系统自动运营规则测试")
        print("="*60)
        
        # 测试1：处理新用户注册
        print("\n测试1：处理新用户注册")
        result = manager.handle_new_user_registration(user_id=1)
        print(f"  初始贡献值：{result['initial_contribution']}")
        print(f"  待发放首项目奖励：{result['pending_first_project_reward']}")
        
        # 测试2：检查活跃用户勋章
        print("\n\n测试2：检查活跃用户勋章")
        result = manager.check_active_user_badges()
        print(f"  活跃用户数：{result['active_users_count']}")
        print(f"  颁发勋章数：{result['badges_granted']}")
        
        # 测试3：检查沉睡用户
        print("\n\n测试3：检查沉睡用户")
        result = manager.check_dormant_users()
        print(f"  沉睡用户数：{result['dormant_users_count']}")
        print(f"  创建奖励数：{result['rewards_created']}")
        
        # 测试4：处理用户登录
        print("\n\n测试4：处理用户登录")
        result = manager.handle_user_login(user_id=1)
        print(f"  连续登录天数：{result['consecutive_login_days']}")
        print(f"  发放奖励数：{len(result['rewards_granted'])}")
        
        # 测试5：自动分配项目
        print("\n\n测试5：自动分配项目")
        projects = manager.auto_assign_projects(user_id=1)
        print(f"  推荐项目数：{len(projects)}")
        for i, project in enumerate(projects, 1):
            print(f"  {i}. {project['project_name']} (匹配分数: {project['match_score']:.2f})")
        
        # 测试6：检查项目超时
        print("\n\n测试6：检查项目超时")
        result = manager.check_project_timeout()
        print(f"  超时项目数：{result['timeout_participations']}")
        print(f"  惩罚用户数：{result['penalized_count']}")
        
        print("\n✅ 测试完成！")
        
    finally:
        session.close()

#!/usr/bin/env python3
"""
高级数据分析系统
数据收集与处理、用户画像、趋势预测、数据可视化
"""

from flask import request, jsonify
from functools import wraps
import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
import statistics

# 配置
DATABASE = 'lingzhi_ecosystem.db'

def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ==================== 数据收集器 ====================

class DataCollector:
    """数据收集器"""

    def __init__(self):
        pass

    def collect_user_behavior(self, user_id: int, action: str, page: str, metadata: dict = None):
        """收集用户行为数据"""
        try:
            conn = get_db()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO user_behavior_logs
                (user_id, action, page, metadata, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, action, page, json.dumps(metadata or {}), datetime.now()))

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"收集用户行为失败: {e}")

    def collect_system_metrics(self, metrics: dict):
        """收集系统指标"""
        try:
            conn = get_db()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO system_metrics
                (metrics, created_at)
                VALUES (?, ?)
            ''', (json.dumps(metrics), datetime.now()))

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"收集系统指标失败: {e}")

# ==================== 用户画像构建器 ====================

class UserProfiler:
    """用户画像构建器"""

    def __init__(self):
        pass

    def build_profile(self, user_id: int) -> Dict:
        """构建用户画像"""
        try:
            conn = get_db()
            cursor = conn.cursor()

            # 获取基本信息
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()

            if not user:
                return {}

            # 获取行为统计
            cursor.execute('''
                SELECT action, COUNT(*) as count
                FROM user_behavior_logs
                WHERE user_id = ?
                GROUP BY action
            ''', (user_id,))

            actions = {row['action']: row['count'] for row in cursor.fetchall()}

            # 获取资产统计
            cursor.execute('''
                SELECT tt.name, tt.symbol, utb.balance
                FROM user_token_balances utb
                JOIN token_types tt ON utb.token_type_id = tt.id
                WHERE utb.user_id = ?
            ''', (user_id,))

            assets = [{
                'name': row['name'],
                'symbol': row['symbol'],
                'balance': row['balance']
            } for row in cursor.fetchall()]

            # 获取学习记录
            cursor.execute('''
                SELECT COUNT(*) as count, SUM(duration) as total_duration, SUM(reward) as total_reward
                FROM user_learning_records
                WHERE user_id = ?
            ''', (user_id,))

            learning = cursor.fetchone()

            # 获取贡献记录
            cursor.execute('''
                SELECT COUNT(*) as count, SUM(reward) as total_reward
                FROM user_contributions
                WHERE user_id = ?
            ''', (user_id,))

            contributions = cursor.fetchone()

            # 获取SBT
            cursor.execute('''
                SELECT st.name, st.rarity
                FROM user_sbts usb
                JOIN sbt_types st ON usb.sbt_type_id = st.id
                WHERE usb.user_id = ?
            ''', (user_id,))

            sbts = [{'name': row['name'], 'rarity': row['rarity']} for row in cursor.fetchall()]

            conn.close()

            # 构建画像
            profile = {
                'user_id': user_id,
                'username': user['username'],
                'created_at': user['created_at'],
                'activity_level': self._calculate_activity_level(actions),
                'interests': self._extract_interests(actions),
                'assets': assets,
                'learning': {
                    'count': learning['count'] if learning else 0,
                    'total_duration': learning['total_duration'] if learning else 0,
                    'total_reward': learning['total_reward'] if learning else 0
                },
                'contributions': {
                    'count': contributions['count'] if contributions else 0,
                    'total_reward': contributions['total_reward'] if contributions else 0
                },
                'sbts': sbts,
                'engagement_score': self._calculate_engagement_score(actions, learning, contributions)
            }

            # 保存画像
            self._save_profile(user_id, profile)

            return profile

        except Exception as e:
            print(f"构建用户画像失败: {e}")
            return {}

    def _calculate_activity_level(self, actions: Dict) -> str:
        """计算活跃度"""
        total_actions = sum(actions.values())
        if total_actions > 100:
            return 'high'
        elif total_actions > 50:
            return 'medium'
        else:
            return 'low'

    def _extract_interests(self, actions: Dict) -> List[str]:
        """提取兴趣"""
        # 简单示例：根据行为提取兴趣
        interests = []
        if 'sacred_sites' in actions:
            interests.append('culture')
        if 'projects' in actions:
            interests.append('projects')
        if 'learning' in actions:
            interests.append('education')
        if 'assets' in actions:
            interests.append('finance')
        return interests

    def _calculate_engagement_score(self, actions: Dict, learning, contributions) -> float:
        """计算参与度分数"""
        score = 0.0

        # 行为频率
        score += min(sum(actions.values()) / 10, 50)

        # 学习
        if learning:
            score += min(learning['count'] * 2, 30)

        # 贡献
        if contributions:
            score += min(contributions['count'] * 3, 20)

        return round(min(score, 100), 2)

    def _save_profile(self, user_id: int, profile: Dict):
        """保存画像"""
        try:
            conn = get_db()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO user_profiles
                (user_id, profile, updated_at)
                VALUES (?, ?, ?)
            ''', (user_id, json.dumps(profile), datetime.now()))

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"保存用户画像失败: {e}")

# ==================== 趋势预测器 ====================

class TrendPredictor:
    """趋势预测器"""

    def __init__(self):
        pass

    def predict_token_price(self, token_type_id: int, days: int = 7) -> Dict:
        """预测通证价格"""
        try:
            conn = get_db()
            cursor = conn.cursor()

            # 获取历史价格数据
            cursor.execute('''
                SELECT price, created_at
                FROM token_price_history
                WHERE token_type_id = ?
                ORDER BY created_at DESC
                LIMIT 30
            ''', (token_type_id,))

            prices = [row['price'] for row in cursor.fetchall()]
            conn.close()

            if len(prices) < 2:
                return {
                    'current_price': prices[0] if prices else 0,
                    'prediction': [],
                    'confidence': 0
                }

            # 简单的移动平均预测
            window = min(7, len(prices))
            moving_avg = statistics.mean(prices[:window])

            # 简单的趋势预测
            trend = (prices[0] - moving_avg) / moving_avg

            prediction = []
            for i in range(days):
                predicted_price = prices[0] * (1 + trend * 0.1 * (i + 1))
                prediction.append({
                    'day': i + 1,
                    'price': round(predicted_price, 2)
                })

            confidence = min(len(prices) / 30, 1.0)

            return {
                'current_price': prices[0],
                'prediction': prediction,
                'confidence': round(confidence, 2)
            }

        except Exception as e:
            print(f"预测通证价格失败: {e}")
            return {
                'current_price': 0,
                'prediction': [],
                'confidence': 0
            }

    def predict_user_growth(self, days: int = 30) -> Dict:
        """预测用户增长"""
        try:
            conn = get_db()
            cursor = conn.cursor()

            # 获取历史用户数据
            cursor.execute('''
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM users
                WHERE created_at >= DATE('now', '-30 days')
                GROUP BY DATE(created_at)
                ORDER BY date ASC
            ''')

            growth_data = [(row['date'], row['count']) for row in cursor.fetchall()]
            conn.close()

            if not growth_data:
                return {
                    'current_users': 0,
                    'prediction': [],
                    'confidence': 0
                }

            # 获取当前用户数
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) as count FROM users')
            current_users = cursor.fetchone()['count']
            conn.close()

            # 简单的线性回归预测
            if len(growth_data) >= 3:
                avg_daily_growth = statistics.mean([count for date, count in growth_data[-7:]])
            else:
                avg_daily_growth = 0

            prediction = []
            for i in range(days):
                predicted_users = current_users + avg_daily_growth * (i + 1)
                prediction.append({
                    'day': i + 1,
                    'users': int(predicted_users)
                })

            return {
                'current_users': current_users,
                'prediction': prediction,
                'confidence': 0.7
            }

        except Exception as e:
            print(f"预测用户增长失败: {e}")
            return {
                'current_users': 0,
                'prediction': [],
                'confidence': 0
            }

# ==================== 数据可视化器 ====================

class DataVisualizer:
    """数据可视化器"""

    def __init__(self):
        pass

    def get_dashboard_data(self) -> Dict:
        """获取仪表盘数据"""
        try:
            conn = get_db()
            cursor = conn.cursor()

            # 用户统计
            cursor.execute('SELECT COUNT(*) as total_users FROM users')
            total_users = cursor.fetchone()['total_users']

            cursor.execute('SELECT COUNT(*) as new_users FROM users WHERE created_at >= DATE("now", "-7 days")')
            new_users = cursor.fetchone()['new_users']

            # 资产统计
            cursor.execute('SELECT SUM(balance) as total_balance FROM user_token_balances')
            total_balance = cursor.fetchone()['total_balance'] or 0

            # 项目统计
            cursor.execute('SELECT COUNT(*) as total_projects FROM cultural_projects')
            total_projects = cursor.fetchone()['total_projects']

            cursor.execute('SELECT COUNT(*) as active_projects FROM cultural_projects WHERE status = "ongoing"')
            active_projects = cursor.fetchone()['active_projects']

            # 交易统计
            cursor.execute('SELECT COUNT(*) as total_transactions FROM token_transactions WHERE created_at >= DATE("now", "-7 days")')
            weekly_transactions = cursor.fetchone()['total_transactions']

            # 学习统计
            cursor.execute('SELECT SUM(duration) as total_duration FROM user_learning_records WHERE created_at >= DATE("now", "-7 days")')
            weekly_learning = cursor.fetchone()['total_duration'] or 0

            # 活动统计
            cursor.execute('SELECT COUNT(*) as total_activities FROM community_activities')
            total_activities = cursor.fetchone()['total_activities']

            conn.close()

            return {
                'users': {
                    'total': total_users,
                    'new': new_users
                },
                'assets': {
                    'total_balance': total_balance
                },
                'projects': {
                    'total': total_projects,
                    'active': active_projects
                },
                'transactions': {
                    'weekly': weekly_transactions
                },
                'learning': {
                    'weekly_duration': weekly_learning
                },
                'activities': {
                    'total': total_activities
                }
            }

        except Exception as e:
            print(f"获取仪表盘数据失败: {e}")
            return {}

# ==================== 初始化 ====================

data_collector = DataCollector()
user_profiler = UserProfiler()
trend_predictor = TrendPredictor()
data_visualizer = DataVisualizer()

# ==================== 注册 API ====================

def register_analytics_apis(app):
    """注册数据分析系统 API"""

    # 获取仪表盘数据
    @app.route('/api/analytics/dashboard', methods=['GET'])
    def get_dashboard():
        """获取仪表盘数据"""
        try:
            dashboard_data = data_visualizer.get_dashboard_data()

            return jsonify({
                'success': True,
                'data': dashboard_data
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'获取仪表盘数据失败: {str(e)}',
                'error_code': 'GET_DASHBOARD_ERROR'
            }), 500

    # 获取用户画像
    @app.route('/api/analytics/user-profile/<int:user_id>', methods=['GET'])
    def get_user_profile(user_id):
        """获取用户画像"""
        try:
            profile = user_profiler.build_profile(user_id)

            if profile:
                return jsonify({
                    'success': True,
                    'data': profile
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '用户不存在',
                    'error_code': 'USER_NOT_FOUND'
                }), 404

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'获取用户画像失败: {str(e)}',
                'error_code': 'GET_USER_PROFILE_ERROR'
            }), 500

    # 预测通证价格
    @app.route('/api/analytics/predict/price', methods=['POST'])
    def predict_price():
        """预测通证价格"""
        try:
            data = request.get_json()
            token_type_id = data.get('token_type_id')
            days = data.get('days', 7)

            if not token_type_id:
                return jsonify({
                    'success': False,
                    'message': '缺少通证类型ID',
                    'error_code': 'MISSING_TOKEN_TYPE_ID'
                }), 400

            prediction = trend_predictor.predict_token_price(token_type_id, days)

            return jsonify({
                'success': True,
                'data': prediction
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'预测通证价格失败: {str(e)}',
                'error_code': 'PREDICT_PRICE_ERROR'
            }), 500

    # 预测用户增长
    @app.route('/api/analytics/predict/user-growth', methods=['POST'])
    def predict_user_growth():
        """预测用户增长"""
        try:
            data = request.get_json()
            days = data.get('days', 30)

            prediction = trend_predictor.predict_user_growth(days)

            return jsonify({
                'success': True,
                'data': prediction
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'预测用户增长失败: {str(e)}',
                'error_code': 'PREDICT_USER_GROWTH_ERROR'
            }), 500

    # 收集用户行为
    @app.route('/api/analytics/behavior', methods=['POST'])
    def collect_behavior():
        """收集用户行为"""
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            action = data.get('action')
            page = data.get('page')
            metadata = data.get('metadata')

            if not user_id or not action:
                return jsonify({
                    'success': False,
                    'message': '缺少必要参数',
                    'error_code': 'MISSING_PARAMS'
                }), 400

            data_collector.collect_user_behavior(user_id, action, page, metadata)

            return jsonify({
                'success': True,
                'message': '行为数据已收集'
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'收集用户行为失败: {str(e)}',
                'error_code': 'COLLECT_BEHAVIOR_ERROR'
            }), 500

    print("✅ 数据分析系统 API 已注册")

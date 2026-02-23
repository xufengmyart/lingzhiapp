#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商家功能路由
支持客户群管理、推荐奖励、优惠券核销
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from database import get_db
from datetime import datetime, timedelta
import json
import logging

# 创建蓝图
merchant_bp = Blueprint('merchant', __name__)

# 日志配置
logger = logging.getLogger(__name__)


def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': '未授权'}), 401
        # TODO: 实现token验证逻辑
        return f(*args, **kwargs)
    return decorated_function


def merchant_required(f):
    """商家权限验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': '未授权'}), 401
        # TODO: 实现商家权限验证逻辑
        return f(*args, **kwargs)
    return decorated_function


# ==================== 商家客户群管理 ====================

@merchant_bp.route('/merchant/customer-groups', methods=['POST'])
@merchant_required
def create_customer_group():
    """
    商家登记客户群
    """
    try:
        db = get_db()
        data = request.get_json()

        # 验证必填字段
        required_fields = ['merchant_id', 'group_name', 'group_size', 'verification_evidence']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必填字段: {field}'}), 400

        # 查找赚取规则
        rule = db.execute(
            "SELECT id, contribution_value FROM contribution_rules WHERE rule_code = 'merchant_register_group' AND status = 'active'"
        ).fetchone()

        if not rule:
            return jsonify({'error': '相关规则不存在'}), 400

        # 检查每日限制
        if rule['contribution_value'] > 0:
            today_count = db.execute(
                """SELECT COUNT(*) FROM merchant_customer_groups
                   WHERE merchant_id = ? AND date(created_at) = date('now')""",
                (data['merchant_id'],)
            ).fetchone()[0]

            max_daily = db.execute(
                "SELECT max_daily_times FROM contribution_rules WHERE rule_code = 'merchant_register_group'"
            ).fetchone()[0]

            if max_daily and today_count >= max_daily:
                return jsonify({'error': f'今日登记次数已达上限（{max_daily}次）'}), 400

        # 插入客户群记录
        db.execute(
            """INSERT INTO merchant_customer_groups
               (merchant_id, group_name, group_type, group_size, group_source,
                contact_person, contact_phone, description, verification_evidence,
                contribution_reward)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                data['merchant_id'],
                data['group_name'],
                data.get('group_type', 'wechat'),
                data['group_size'],
                data.get('group_source', ''),
                data.get('contact_person', ''),
                data.get('contact_phone', ''),
                data.get('description', ''),
                json.dumps(data['verification_evidence']),
                rule['contribution_value']
            )
        )

        group_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

        # 创建贡献值交易记录
        merchant = db.execute(
            "SELECT id, total_contribution, total_lingzhi FROM users WHERE id = ?",
            (data['merchant_id'],)
        ).fetchone()

        if merchant:
            old_contribution = merchant['total_contribution']
            old_lingzhi = merchant['total_lingzhi']
            new_contribution = old_contribution + rule['contribution_value']

            db.execute(
                """INSERT INTO contribution_transactions
                   (user_id, rule_id, rule_code, rule_name, transaction_type,
                    contribution_change, balance_before, balance_after,
                    lingzhi_change, lingzhi_balance_before, lingzhi_balance_after,
                    description, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    data['merchant_id'],
                    rule['id'],
                    'merchant_register_group',
                    '商家登记客户群',
                    'earn',
                    rule['contribution_value'],
                    old_contribution,
                    new_contribution,
                    0,
                    old_lingzhi,
                    old_lingzhi,
                    f'登记客户群: {data["group_name"]}',
                    'completed'
                )
            )

            # 更新用户贡献值
            db.execute(
                """UPDATE users
                   SET total_contribution = ?,
                       cumulative_contribution = cumulative_contribution + ?,
                       updated_at = ?
                   WHERE id = ?""",
                (new_contribution, max(0, rule['contribution_value']), datetime.now().isoformat(), data['merchant_id'])
            )

        db.commit()

        logger.info(f"商家 {data['merchant_id']} 登记客户群: {data['group_name']}")

        return jsonify({
            'success': True,
            'message': f'客户群登记成功，获得 {rule["contribution_value"]} 贡献值',
            'group_id': group_id,
            'reward': rule['contribution_value']
        }), 201

    except Exception as e:
        logger.error(f"登记客户群失败: {str(e)}")
        db.rollback()
        return jsonify({'error': f'登记客户群失败: {str(e)}'}), 500


@merchant_bp.route('/merchant/customer-groups', methods=['GET'])
@login_required
def get_customer_groups():
    """
    获取客户群列表
    """
    try:
        db = get_db()

        # 获取查询参数
        merchant_id = request.args.get('merchant_id', '')
        status = request.args.get('status', '')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))

        # 构建查询条件
        where_clauses = []
        params = []

        if merchant_id:
            where_clauses.append('merchant_id = ?')
            params.append(merchant_id)

        if status:
            where_clauses.append('verification_status = ?')
            params.append(status)

        where_sql = ' AND '.join(where_clauses) if where_clauses else '1=1'

        # 查询总数
        count_query = f"SELECT COUNT(*) FROM merchant_customer_groups WHERE {where_sql}"
        total = db.execute(count_query, params).fetchone()[0]

        # 查询数据
        offset = (page - 1) * page_size
        query = f"""
            SELECT g.*, u.username, u.real_name
            FROM merchant_customer_groups g
            LEFT JOIN users u ON g.merchant_id = u.id
            WHERE {where_sql}
            ORDER BY g.created_at DESC
            LIMIT ? OFFSET ?
        """
        params.extend([page_size, offset])

        groups = db.execute(query, params).fetchall()

        return jsonify({
            'success': True,
            'groups': [dict(g) for g in groups],
            'total': total,
            'page': page,
            'page_size': page_size
        }), 200

    except Exception as e:
        logger.error(f"获取客户群列表失败: {str(e)}")
        return jsonify({'error': f'获取客户群列表失败: {str(e)}'}), 500


@merchant_bp.route('/merchant/customer-groups/<int:group_id>', methods=['PUT'])
@login_required
def update_customer_group(group_id):
    """
    更新客户群信息
    """
    try:
        db = get_db()
        data = request.get_json()

        # 检查客户群是否存在
        group = db.execute(
            'SELECT id, verification_status FROM merchant_customer_groups WHERE id = ?',
            (group_id,)
        ).fetchone()

        if not group:
            return jsonify({'error': '客户群不存在'}), 404

        if group['verification_status'] == 'verified':
            return jsonify({'error': '已验证的客户群不能修改'}), 400

        # 构建更新SQL
        update_fields = []
        update_values = []

        editable_fields = ['group_name', 'group_size', 'contact_person', 'contact_phone', 'description']

        for field in editable_fields:
            if field in data:
                update_fields.append(f"{field} = ?")
                update_values.append(data[field])

        if not update_fields:
            return jsonify({'error': '没有要更新的字段'}), 400

        update_fields.append("updated_at = ?")
        update_values.append(datetime.now().isoformat())
        update_values.append(group_id)

        sql = f"UPDATE merchant_customer_groups SET {', '.join(update_fields)} WHERE id = ?"
        db.execute(sql, update_values)
        db.commit()

        return jsonify({
            'success': True,
            'message': '客户群信息更新成功'
        }), 200

    except Exception as e:
        logger.error(f"更新客户群失败: {str(e)}")
        db.rollback()
        return jsonify({'error': f'更新客户群失败: {str(e)}'}), 500


# ==================== 商家推荐系统 ====================

@merchant_bp.route('/merchant/referrals', methods=['POST'])
@merchant_required
def create_referral():
    """
    商家推荐其他商家
    """
    try:
        db = get_db()
        data = request.get_json()

        # 验证必填字段
        required_fields = ['referrer_merchant_id', 'referee_merchant_id', 'relationship_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必填字段: {field}'}), 400

        if data['referrer_merchant_id'] == data['referee_merchant_id']:
            return jsonify({'error': '不能推荐自己'}), 400

        # 检查是否已存在推荐关系
        existing = db.execute(
            """SELECT id FROM merchant_referrals
               WHERE referrer_merchant_id = ? AND referee_merchant_id = ?""",
            (data['referrer_merchant_id'], data['referee_merchant_id'])
        ).fetchone()

        if existing:
            return jsonify({'error': '推荐关系已存在'}), 400

        # 检查被推荐商家是否存在
        referee = db.execute(
            "SELECT id FROM users WHERE id = ?",
            (data['referee_merchant_id'],)
        ).fetchone()

        if not referee:
            return jsonify({'error': '被推荐商家不存在'}), 404

        # 查找赚取规则
        rule = db.execute(
            "SELECT id, contribution_value, lingzhi_value FROM contribution_rules WHERE rule_code = 'merchant_recommend' AND status = 'active'"
        ).fetchone()

        if not rule:
            return jsonify({'error': '相关规则不存在'}), 400

        # 生成推荐码
        import random
        import string
        referral_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

        # 插入推荐记录
        db.execute(
            """INSERT INTO merchant_referrals
               (referrer_merchant_id, referee_merchant_id, referral_code,
                relationship_type, relationship_description,
                contribution_reward, referral_status)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                data['referrer_merchant_id'],
                data['referee_merchant_id'],
                referral_code,
                data['relationship_type'],
                data.get('relationship_description', ''),
                rule['contribution_value'],
                'confirmed'
            )
        )

        # 创建贡献值交易记录
        merchant = db.execute(
            "SELECT id, total_contribution, total_lingzhi FROM users WHERE id = ?",
            (data['referrer_merchant_id'],)
        ).fetchone()

        if merchant:
            old_contribution = merchant['total_contribution']
            old_lingzhi = merchant['total_lingzhi']
            new_contribution = old_contribution + rule['contribution_value']
            new_lingzhi = old_lingzhi + rule['lingzhi_value']

            db.execute(
                """INSERT INTO contribution_transactions
                   (user_id, rule_id, rule_code, rule_name, transaction_type,
                    contribution_change, balance_before, balance_after,
                    lingzhi_change, lingzhi_balance_before, lingzhi_balance_after,
                    description, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    data['referrer_merchant_id'],
                    rule['id'],
                    'merchant_recommend',
                    '商家推荐商家',
                    'earn',
                    rule['contribution_value'],
                    old_contribution,
                    new_contribution,
                    rule['lingzhi_value'],
                    old_lingzhi,
                    new_lingzhi,
                    f'推荐商家 ID:{data["referee_merchant_id"]}',
                    'completed'
                )
            )

            # 更新用户贡献值和灵值
            db.execute(
                """UPDATE users
                   SET total_contribution = ?,
                       cumulative_contribution = cumulative_contribution + ?,
                       total_lingzhi = ?,
                       updated_at = ?
                   WHERE id = ?""",
                (new_contribution, max(0, rule['contribution_value']), new_lingzhi,
                 datetime.now().isoformat(), data['referrer_merchant_id'])
            )

        db.commit()

        logger.info(f"商家 {data['referrer_merchant_id']} 推荐商家 {data['referee_merchant_id']}")

        return jsonify({
            'success': True,
            'message': f'推荐成功，获得 {rule["contribution_value"]} 贡献值和 {rule["lingzhi_value"]} 灵值',
            'referral_code': referral_code,
            'reward': {
                'contribution': rule['contribution_value'],
                'lingzhi': rule['lingzhi_value']
            }
        }), 201

    except Exception as e:
        logger.error(f"创建推荐失败: {str(e)}")
        db.rollback()
        return jsonify({'error': f'创建推荐失败: {str(e)}'}), 500


@merchant_bp.route('/merchant/referrals', methods=['GET'])
@login_required
def get_referrals():
    """
    获取推荐记录列表
    """
    try:
        db = get_db()

        merchant_id = request.args.get('merchant_id', '')
        status = request.args.get('status', '')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))

        where_clauses = []
        params = []

        if merchant_id:
            where_clauses.append('referrer_merchant_id = ?')
            params.append(merchant_id)

        if status:
            where_clauses.append('referral_status = ?')
            params.append(status)

        where_sql = ' AND '.join(where_clauses) if where_clauses else '1=1'

        count_query = f"SELECT COUNT(*) FROM merchant_referrals WHERE {where_sql}"
        total = db.execute(count_query, params).fetchone()[0]

        offset = (page - 1) * page_size
        query = f"""
            SELECT r.*,
                   u1.username as referrer_name,
                   u1.real_name as referrer_real_name,
                   u2.username as referee_name,
                   u2.real_name as referee_real_name
            FROM merchant_referrals r
            LEFT JOIN users u1 ON r.referrer_merchant_id = u1.id
            LEFT JOIN users u2 ON r.referee_merchant_id = u2.id
            WHERE {where_sql}
            ORDER BY r.created_at DESC
            LIMIT ? OFFSET ?
        """
        params.extend([page_size, offset])

        referrals = db.execute(query, params).fetchall()

        return jsonify({
            'success': True,
            'referrals': [dict(r) for r in referrals],
            'total': total,
            'page': page,
            'page_size': page_size
        }), 200

    except Exception as e:
        logger.error(f"获取推荐记录失败: {str(e)}")
        return jsonify({'error': f'获取推荐记录失败: {str(e)}'}), 500


# ==================== 优惠券核销 ====================

@merchant_bp.route('/merchant/coupons/verify', methods=['POST'])
@merchant_required
def verify_coupon():
    """
    商家核销优惠券
    """
    try:
        db = get_db()
        data = request.get_json()

        # 验证必填字段
        required_fields = ['merchant_id', 'coupon_code', 'user_id', 'used_amount']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必填字段: {field}'}), 400

        # 查找用户优惠券
        user_coupon = db.execute(
            """SELECT uc.*, c.coupon_type, c.discount_value, c.min_purchase_amount
               FROM user_coupons uc
               LEFT JOIN coupons c ON uc.coupon_id = c.id
               WHERE uc.coupon_code = ? AND uc.user_id = ? AND uc.status = 'unused'""",
            (data['coupon_code'], data['user_id'])
        ).fetchone()

        if not user_coupon:
            return jsonify({'error': '优惠券不存在或已使用'}), 404

        # 检查是否过期
        if user_coupon['expires_at'] and datetime.now() > datetime.fromisoformat(user_coupon['expires_at']):
            return jsonify({'error': '优惠券已过期'}), 400

        # 查找赚取规则
        rule = db.execute(
            "SELECT id, contribution_value, lingzhi_value FROM contribution_rules WHERE rule_code = 'merchant_coupon_verify' AND status = 'active'"
        ).fetchone()

        if not rule:
            return jsonify({'error': '相关规则不存在'}), 400

        # 检查今日核销限制
        today_count = db.execute(
            """SELECT COUNT(*) FROM contribution_transactions
               WHERE user_id = ? AND rule_code = 'merchant_coupon_verify'
               AND date(created_at) = date('now')""",
            (data['merchant_id'],)
        ).fetchone()[0]

        max_daily = db.execute(
            "SELECT max_daily_times FROM contribution_rules WHERE rule_code = 'merchant_coupon_verify'"
        ).fetchone()[0]

        if max_daily and today_count >= max_daily:
            return jsonify({'error': f'今日核销次数已达上限（{max_daily}次）'}), 400

        # 更新用户优惠券状态
        db.execute(
            """UPDATE user_coupons
               SET status = 'used', used_at = ?, used_amount = ?
               WHERE id = ?""",
            (datetime.now().isoformat(), data['used_amount'], user_coupon['id'])
        )

        # 更新优惠券使用次数
        db.execute(
            "UPDATE coupons SET usage_count = usage_count + 1 WHERE id = ?",
            (user_coupon['coupon_id'],)
        )

        # 创建贡献值交易记录
        merchant = db.execute(
            "SELECT id, total_contribution, total_lingzhi FROM users WHERE id = ?",
            (data['merchant_id'],)
        ).fetchone()

        if merchant:
            old_contribution = merchant['total_contribution']
            old_lingzhi = merchant['total_lingzhi']
            new_contribution = old_contribution + rule['contribution_value']
            new_lingzhi = old_lingzhi + rule['lingzhi_value']

            db.execute(
                """INSERT INTO contribution_transactions
                   (user_id, rule_id, rule_code, rule_name, transaction_type,
                    contribution_change, balance_before, balance_after,
                    lingzhi_change, lingzhi_balance_before, lingzhi_balance_after,
                    related_user_id, description, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    data['merchant_id'],
                    rule['id'],
                    'merchant_coupon_verify',
                    '优惠券核销',
                    'earn',
                    rule['contribution_value'],
                    old_contribution,
                    new_contribution,
                    rule['lingzhi_value'],
                    old_lingzhi,
                    new_lingzhi,
                    data['user_id'],
                    f'核销用户 {data["user_id"]} 的优惠券 {data["coupon_code"]}',
                    'completed'
                )
            )

            # 更新商家贡献值和灵值
            db.execute(
                """UPDATE users
                   SET total_contribution = ?,
                       cumulative_contribution = cumulative_contribution + ?,
                       total_lingzhi = ?,
                       updated_at = ?
                   WHERE id = ?""",
                (new_contribution, max(0, rule['contribution_value']), new_lingzhi,
                 datetime.now().isoformat(), data['merchant_id'])
            )

        db.commit()

        logger.info(f"商家 {data['merchant_id']} 核销优惠券 {data['coupon_code']}")

        return jsonify({
            'success': True,
            'message': f'核销成功，获得 {rule["contribution_value"]} 贡献值和 {rule["lingzhi_value"]} 灵值',
            'reward': {
                'contribution': rule['contribution_value'],
                'lingzhi': rule['lingzhi_value']
            },
            'discount': {
                'type': user_coupon['coupon_type'],
                'value': user_coupon['discount_value']
            }
        }), 200

    except Exception as e:
        logger.error(f"核销优惠券失败: {str(e)}")
        db.rollback()
        return jsonify({'error': f'核销优惠券失败: {str(e)}'}), 500


@merchant_bp.route('/merchant/coupons/verified', methods=['GET'])
@login_required
def get_verified_coupons():
    """
    获取核销记录
    """
    try:
        db = get_db()

        merchant_id = request.args.get('merchant_id', '')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))

        where_clauses = []
        params = []

        if merchant_id:
            where_clauses.append('user_id = ?')
            params.append(merchant_id)

        if start_date:
            where_clauses.append("date(created_at) >= ?")
            params.append(start_date)

        if end_date:
            where_clauses.append("date(created_at) <= ?")
            params.append(end_date)

        where_sql = ' AND '.join(where_clauses) if where_clauses else '1=1'

        count_query = f"SELECT COUNT(*) FROM contribution_transactions WHERE {where_sql} AND rule_code = 'merchant_coupon_verify'"
        total = db.execute(count_query, params).fetchone()[0]

        offset = (page - 1) * page_size
        query = f"""
            SELECT t.*, u.username, u.real_name
            FROM contribution_transactions t
            LEFT JOIN users u ON t.related_user_id = u.id
            WHERE {where_sql} AND rule_code = 'merchant_coupon_verify'
            ORDER BY t.created_at DESC
            LIMIT ? OFFSET ?
        """
        params.extend([page_size, offset])

        transactions = db.execute(query, params).fetchall()

        return jsonify({
            'success': True,
            'transactions': [dict(t) for t in transactions],
            'total': total,
            'page': page,
            'page_size': page_size
        }), 200

    except Exception as e:
        logger.error(f"获取核销记录失败: {str(e)}")
        return jsonify({'error': f'获取核销记录失败: {str(e)}'}), 500

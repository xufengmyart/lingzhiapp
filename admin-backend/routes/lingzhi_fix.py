"""
灵值修复接口
用于修复新用户注册时没有正确赠送100灵值的问题
"""

from flask import Blueprint, jsonify
import sqlite3
import os

# 导入配置
from config import config
DATABASE = os.getenv('TEST_DATABASE_PATH', config.DATABASE_PATH)

lingzhi_fix_bp = Blueprint('lingzhi_fix', __name__)

def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@lingzhi_fix_bp.route('/lingzhi/fix/user/<int:user_id>', methods=['POST'])
def fix_user_lingzhi(user_id):
    """修复指定用户的灵值"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        # 检查用户是否存在
        cursor.execute("SELECT id, username, total_lingzhi FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404

        print(f"[灵值修复] 用户 {user['username']} (ID: {user_id}) 当前灵值: {user['total_lingzhi']}")

        # 如果灵值已经是100，不需要修复
        if user['total_lingzhi'] >= 100:
            conn.close()
            return jsonify({
                'success': True,
                'message': '用户灵值正常，无需修复',
                'data': {
                    'user_id': user_id,
                    'total_lingzhi': user['total_lingzhi']
                }
            })

        # 修复灵值
        cursor.execute(
            "UPDATE users SET total_lingzhi = 100 WHERE id = ?",
            (user_id,)
        )
        
        # 检查是否有灵值消费记录
        cursor.execute(
            """
            SELECT COUNT(*) as count 
            FROM lingzhi_consumption_records 
            WHERE user_id = ? AND consumption_type = 'new_user_bonus'
            """,
            (user_id,)
        )
        record_count = cursor.fetchone()['count']
        
        # 如果没有消费记录，添加一条
        if record_count == 0:
            cursor.execute(
                """
                INSERT INTO lingzhi_consumption_records (user_id, consumption_type, consumption_item, lingzhi_amount, description)
                VALUES (?, 'new_user_bonus', 'new_user_bonus', 100, '新用户注册赠送（手动修复）')
                """,
                (user_id,)
            )
            print(f"[灵值修复] 已为用户 {user['username']} 添加灵值消费记录")
        
        conn.commit()
        conn.close()

        print(f"[灵值修复] 成功修复用户 {user['username']} 的灵值，从 {user['total_lingzhi']} 修复为 100")

        return jsonify({
            'success': True,
            'message': f'已成功修复用户灵值，从 {user["total_lingzhi"]} 修复为 100',
            'data': {
                'user_id': user_id,
                'username': user['username'],
                'old_lingzhi': user['total_lingzhi'],
                'new_lingzhi': 100
            }
        })

    except Exception as e:
        print(f"[灵值修复] 修复失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'修复失败: {str(e)}'
        }), 500

@lingzhi_fix_bp.route('/lingzhi/fix/all', methods=['POST'])
def fix_all_users_lingzhi():
    """修复所有灵值为0的用户"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        # 查找所有灵值为0的用户
        cursor.execute("""
            SELECT id, username, total_lingzhi 
            FROM users 
            WHERE total_lingzhi = 0
            AND id NOT IN (
                SELECT user_id FROM lingzhi_consumption_records
                WHERE consumption_type = 'admin_create'
            )
        """)
        users_to_fix = cursor.fetchall()
        
        if not users_to_fix:
            conn.close()
            return jsonify({
                'success': True,
                'message': '没有需要修复的用户',
                'data': {
                    'fixed_count': 0
                }
            })

        print(f"[灵值修复] 找到 {len(users_to_fix)} 个需要修复的用户")

        fixed_count = 0
        for user in users_to_fix:
            # 更新灵值
            cursor.execute(
                "UPDATE users SET total_lingzhi = 100 WHERE id = ?",
                (user['id'],)
            )
            
            # 添加消费记录
            cursor.execute(
                """
                INSERT INTO lingzhi_consumption_records (user_id, consumption_type, consumption_item, lingzhi_amount, description)
                VALUES (?, 'new_user_bonus', 'new_user_bonus', 100, '新用户注册赠送（批量修复）')
                """,
                (user['id'],)
            )
            
            print(f"[灵值修复] 修复用户 {user['username']} (ID: {user['id']})")
            fixed_count += 1
        
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': f'已成功修复 {fixed_count} 个用户的灵值',
            'data': {
                'fixed_count': fixed_count,
                'users': [{'id': u['id'], 'username': u['username']} for u in users_to_fix]
            }
        })

    except Exception as e:
        print(f"[灵值修复] 批量修复失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'批量修复失败: {str(e)}'
        }), 500

@lingzhi_fix_bp.route('/lingzhi/check/<int:user_id>', methods=['GET'])
def check_user_lingzhi(user_id):
    """检查用户的灵值状态"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        # 查询用户信息
        cursor.execute("SELECT id, username, total_lingzhi, created_at FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404

        # 查询灵值消费记录
        cursor.execute(
            """
            SELECT consumption_type, consumption_item, lingzhi_amount, description, created_at
            FROM lingzhi_consumption_records
            WHERE user_id = ? AND consumption_type = 'new_user_bonus'
            """,
            (user_id,)
        )
        records = cursor.fetchall()
        
        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'user_id': user['id'],
                'username': user['username'],
                'total_lingzhi': user['total_lingzhi'],
                'created_at': user['created_at'],
                'has_bonus_record': len(records) > 0,
                'bonus_records': [
                    {
                        'type': r['consumption_type'],
                        'item': r['consumption_item'],
                        'amount': r['lingzhi_amount'],
                        'description': r['description'],
                        'created_at': r['created_at']
                    }
                    for r in records
                ]
            }
        })

    except Exception as e:
        print(f"[灵值修复] 检查失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'检查失败: {str(e)}'
        }), 500

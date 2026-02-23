"""
公司信息管理路由蓝图
包含公司信息的增删改查功能
"""

from flask import Blueprint, request, jsonify
import sqlite3
import json
from datetime import datetime

company_info_bp = Blueprint('company_info', __name__)

# 导入配置
from config import config
DATABASE = config.DATABASE_PATH

def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ============ 获取公司信息 ============

@company_info_bp.route('/admin/company/info', methods=['GET'])
def get_company_info():
    """获取公司信息"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        # 查询公司信息
        cursor.execute("SELECT * FROM company_info WHERE id = 1")
        company = cursor.fetchone()

        if company:
            result = dict(company)
        else:
            result = {
                'name': '',
                'logo_url': '',
                'description': '',
                'address': '',
                'phone': '',
                'email': '',
                'website': '',
                'business_license': '',
                'legal_representative': '',
                'established_date': '',
                'registered_capital': '',
                'business_scope': '',
                'created_at': '',
                'updated_at': ''
            }

        conn.close()

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取公司信息失败: {str(e)}'
        }), 500

# ============ 更新公司信息 ============

@company_info_bp.route('/admin/company/info', methods=['PUT'])
def update_company_info():
    """更新公司信息"""
    try:
        data = request.json

        conn = get_db()
        cursor = conn.cursor()

        # 检查是否已存在公司信息
        cursor.execute("SELECT id FROM company_info WHERE id = 1")
        existing = cursor.fetchone()

        if existing:
            # 更新
            cursor.execute("""
                UPDATE company_info SET
                    name = ?,
                    logo_url = ?,
                    description = ?,
                    address = ?,
                    phone = ?,
                    email = ?,
                    website = ?,
                    business_license = ?,
                    legal_representative = ?,
                    established_date = ?,
                    registered_capital = ?,
                    business_scope = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = 1
            """, (
                data.get('name', ''),
                data.get('logo_url', ''),
                data.get('description', ''),
                data.get('address', ''),
                data.get('phone', ''),
                data.get('email', ''),
                data.get('website', ''),
                data.get('business_license', ''),
                data.get('legal_representative', ''),
                data.get('established_date', ''),
                data.get('registered_capital', ''),
                data.get('business_scope', '')
            ))
        else:
            # 插入
            cursor.execute("""
                INSERT INTO company_info (
                    id, name, logo_url, description, address, phone, email, website,
                    business_license, legal_representative, established_date,
                    registered_capital, business_scope, created_at, updated_at
                ) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (
                data.get('name', ''),
                data.get('logo_url', ''),
                data.get('description', ''),
                data.get('address', ''),
                data.get('phone', ''),
                data.get('email', ''),
                data.get('website', ''),
                data.get('business_license', ''),
                data.get('legal_representative', ''),
                data.get('established_date', ''),
                data.get('registered_capital', ''),
                data.get('business_scope', '')
            ))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '公司信息更新成功'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新公司信息失败: {str(e)}'
        }), 500

#!/usr/bin/env python3
"""
功能扩展模块 - 中视频、西安美学侦探、合伙人项目
"""
import sqlite3
from flask import jsonify, request
from datetime import datetime

# ============ 数据库表创建 ============

def create_extension_tables(conn):
    """创建扩展功能表"""
    cursor = conn.cursor()
    
    # 中视频项目表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS video_projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'draft',
            video_url TEXT,
            cover_image TEXT,
            lingzhi_cost INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # 西安美学侦探项目表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aesthetic_projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            project_name TEXT NOT NULL,
            location TEXT,
            theme TEXT,
            status TEXT DEFAULT 'planning',
            discovery_data TEXT,
            images TEXT,
            lingzhi_cost INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # 扩展合伙人功能 - 项目申请表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS partner_projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partner_id INTEGER NOT NULL,
            project_name TEXT NOT NULL,
            project_type TEXT NOT NULL,
            investment_amount INTEGER DEFAULT 0,
            expected_return REAL DEFAULT 0,
            status TEXT DEFAULT 'pending',
            description TEXT,
            approval_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (partner_id) REFERENCES users(id)
        )
    ''')
    
    # 合伙人收益记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS partner_earnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partner_id INTEGER NOT NULL,
            project_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            earning_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            description TEXT,
            FOREIGN KEY (partner_id) REFERENCES users(id),
            FOREIGN KEY (project_id) REFERENCES partner_projects(id)
        )
    ''')
    
    conn.commit()
    print("扩展功能表创建成功")

# ============ API路由定义 ============

def register_video_routes(app, get_db, verify_token):
    """注册中视频项目路由"""
    
    @app.route('/api/video/projects', methods=['GET'])
    def get_video_projects():
        """获取用户的中视频项目列表"""
        try:
            user_id = verify_token(request.headers.get('Authorization'))
            if not user_id:
                return jsonify({'success': False, 'message': '未授权'}), 401
            
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM video_projects 
                WHERE user_id = ? 
                ORDER BY created_at DESC
            ''', (user_id,))
            
            projects = []
            for row in cursor.fetchall():
                projects.append({
                    'id': row[0],
                    'user_id': row[1],
                    'title': row[2],
                    'description': row[3],
                    'status': row[4],
                    'video_url': row[5],
                    'cover_image': row[6],
                    'lingzhi_cost': row[7],
                    'created_at': row[8],
                    'updated_at': row[9]
                })
            
            conn.close()
            return jsonify({'success': True, 'data': projects})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    @app.route('/api/video/projects', methods=['POST'])
    def create_video_project():
        """创建中视频项目"""
        try:
            user_id = verify_token(request.headers.get('Authorization'))
            if not user_id:
                return jsonify({'success': False, 'message': '未授权'}), 401
            
            data = request.json
            title = data.get('title')
            description = data.get('description', '')
            video_url = data.get('video_url', '')
            cover_image = data.get('cover_image', '')
            lingzhi_cost = data.get('lingzhi_cost', 0)
            
            if not title:
                return jsonify({'success': False, 'message': '项目标题不能为空'}), 400
            
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO video_projects (user_id, title, description, video_url, cover_image, lingzhi_cost)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, title, description, video_url, cover_image, lingzhi_cost))
            
            project_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': '项目创建成功',
                'data': {'id': project_id}
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    @app.route('/api/video/projects/<int:project_id>', methods=['PUT'])
    def update_video_project(project_id):
        """更新中视频项目"""
        try:
            user_id = verify_token(request.headers.get('Authorization'))
            if not user_id:
                return jsonify({'success': False, 'message': '未授权'}), 401
            
            data = request.json
            conn = get_db()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE video_projects 
                SET title = ?, description = ?, video_url = ?, cover_image = ?, 
                    lingzhi_cost = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_id = ?
            ''', (
                data.get('title'),
                data.get('description'),
                data.get('video_url'),
                data.get('cover_image'),
                data.get('lingzhi_cost'),
                data.get('status', 'draft'),
                project_id,
                user_id
            ))
            
            conn.commit()
            conn.close()
            
            return jsonify({'success': True, 'message': '项目更新成功'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

def register_aesthetic_routes(app, get_db, verify_token):
    """注册西安美学侦探项目路由"""
    
    @app.route('/api/aesthetic/projects', methods=['GET'])
    def get_aesthetic_projects():
        """获取用户的西安美学侦探项目列表"""
        try:
            user_id = verify_token(request.headers.get('Authorization'))
            if not user_id:
                return jsonify({'success': False, 'message': '未授权'}), 401
            
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM aesthetic_projects 
                WHERE user_id = ? 
                ORDER BY created_at DESC
            ''', (user_id,))
            
            projects = []
            for row in cursor.fetchall():
                projects.append({
                    'id': row[0],
                    'user_id': row[1],
                    'project_name': row[2],
                    'location': row[3],
                    'theme': row[4],
                    'status': row[5],
                    'discovery_data': row[6],
                    'images': row[7],
                    'lingzhi_cost': row[8],
                    'created_at': row[9],
                    'updated_at': row[10]
                })
            
            conn.close()
            return jsonify({'success': True, 'data': projects})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    @app.route('/api/aesthetic/projects', methods=['POST'])
    def create_aesthetic_project():
        """创建西安美学侦探项目"""
        try:
            user_id = verify_token(request.headers.get('Authorization'))
            if not user_id:
                return jsonify({'success': False, 'message': '未授权'}), 401
            
            data = request.json
            project_name = data.get('project_name')
            location = data.get('location', '')
            theme = data.get('theme', '')
            discovery_data = data.get('discovery_data', '')
            images = data.get('images', '')
            lingzhi_cost = data.get('lingzhi_cost', 0)
            
            if not project_name:
                return jsonify({'success': False, 'message': '项目名称不能为空'}), 400
            
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO aesthetic_projects (user_id, project_name, location, theme, discovery_data, images, lingzhi_cost)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, project_name, location, theme, discovery_data, images, lingzhi_cost))
            
            project_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': '项目创建成功',
                'data': {'id': project_id}
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

def register_enhanced_partner_routes(app, get_db, verify_token):
    """注册增强的合伙人功能路由"""
    
    @app.route('/api/partner/projects', methods=['GET'])
    def get_partner_projects():
        """获取合伙人项目列表"""
        try:
            user_id = verify_token(request.headers.get('Authorization'))
            if not user_id:
                return jsonify({'success': False, 'message': '未授权'}), 401
            
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM partner_projects 
                WHERE partner_id = ? 
                ORDER BY created_at DESC
            ''', (user_id,))
            
            projects = []
            for row in cursor.fetchall():
                projects.append({
                    'id': row[0],
                    'partner_id': row[1],
                    'project_name': row[2],
                    'project_type': row[3],
                    'investment_amount': row[4],
                    'expected_return': row[5],
                    'status': row[6],
                    'description': row[7],
                    'approval_date': str(row[8]) if row[8] else None,
                    'created_at': row[9]
                })
            
            conn.close()
            return jsonify({'success': True, 'data': projects})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    @app.route('/api/partner/projects', methods=['POST'])
    def create_partner_project():
        """创建合伙人项目申请"""
        try:
            user_id = verify_token(request.headers.get('Authorization'))
            if not user_id:
                return jsonify({'success': False, 'message': '未授权'}), 401
            
            data = request.json
            project_name = data.get('project_name')
            project_type = data.get('project_type')
            investment_amount = data.get('investment_amount', 0)
            expected_return = data.get('expected_return', 0)
            description = data.get('description', '')
            
            if not project_name or not project_type:
                return jsonify({'success': False, 'message': '项目名称和类型不能为空'}), 400
            
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO partner_projects (partner_id, project_name, project_type, investment_amount, expected_return, description)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, project_name, project_type, investment_amount, expected_return, description))
            
            project_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': '项目申请已提交',
                'data': {'id': project_id}
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    @app.route('/api/partner/earnings', methods=['GET'])
    def get_partner_earnings():
        """获取合伙人收益记录"""
        try:
            user_id = verify_token(request.headers.get('Authorization'))
            if not user_id:
                return jsonify({'success': False, 'message': '未授权'}), 401
            
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT pe.*, pp.project_name 
                FROM partner_earnings pe
                LEFT JOIN partner_projects pp ON pe.project_id = pp.id
                WHERE pe.partner_id = ? 
                ORDER BY pe.earning_date DESC
            ''', (user_id,))
            
            earnings = []
            for row in cursor.fetchall():
                earnings.append({
                    'id': row[0],
                    'partner_id': row[1],
                    'project_id': row[2],
                    'amount': row[3],
                    'earning_date': row[4],
                    'description': row[5],
                    'project_name': row[6]
                })
            
            conn.close()
            return jsonify({'success': True, 'data': earnings})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

# ============ 初始化函数 ============

def init_extension_features(app, get_db, verify_token):
    """初始化所有扩展功能"""
    # 创建数据库表
    conn = get_db()
    create_extension_tables(conn)
    conn.close()
    
    # 注册路由
    register_video_routes(app, get_db, verify_token)
    register_aesthetic_routes(app, get_db, verify_token)
    register_enhanced_partner_routes(app, get_db, verify_token)
    
    print("扩展功能初始化完成")

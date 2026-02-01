from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, date
import sqlite3
import hashlib
import jwt
import os

app = Flask(__name__)
CORS(app)

# 配置
SECRET_KEY = os.getenv('SECRET_KEY', 'lingzhi-ecosystem-secret-key-2026')
DATABASE = 'lingzhi_ecosystem.db'

# JWT 配置
JWT_SECRET = os.getenv('JWT_SECRET', 'lingzhi-jwt-secret-key')
JWT_EXPIRATION = 7 * 24 * 60 * 60  # 7天

def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # 用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            phone TEXT,
            password_hash TEXT NOT NULL,
            total_lingzhi INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 签到记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS checkin_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            checkin_date DATE NOT NULL,
            lingzhi_earned INTEGER DEFAULT 10,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, checkin_date)
        )
    ''')

    # 会话表（用于用户旅程）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            conversation_id TEXT,
            stage TEXT DEFAULT 'new',
            progress INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # 合伙人申请表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS partner_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            user_name TEXT,
            phone TEXT,
            current_lingzhi INTEGER,
            reason TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # 后台管理员表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token(user_id):
    """生成JWT token"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow().timestamp() + JWT_EXPIRATION
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def verify_token(token):
    """验证JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload['user_id']
    except:
        return None

# 初始化数据库
init_db()

# 创建默认管理员账号（如果不存在）
def create_default_admin():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admins WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO admins (username, password_hash, role) VALUES (?, ?, ?)",
            ('admin', hash_password('admin123'), 'admin')
        )
        conn.commit()
        print("默认管理员账号已创建: admin / admin123")
    conn.close()

create_default_admin()

# ============ 路由定义 ============

@app.route('/')
def index():
    """健康检查"""
    return jsonify({
        'status': 'success',
        'message': '灵值生态园 API 服务正常运行',
        'version': '1.0.0'
    })

@app.route('/api/health')
def health():
    """健康检查"""
    return jsonify({'status': 'ok'})

# ============ 用户认证 ============

@app.route('/api/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email', '')
        phone = data.get('phone', '')
        password = data.get('password')

        if not username or not password:
            return jsonify({
                'success': False,
                'message': '用户名和密码不能为空'
            }), 400

        conn = get_db()
        cursor = conn.cursor()

        # 检查用户名是否已存在
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'message': '用户名已存在'
            }), 400

        # 创建用户
        password_hash = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, email, phone, password_hash) VALUES (?, ?, ?, ?)",
            (username, email, phone, password_hash)
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # 生成token
        token = generate_token(user_id)

        return jsonify({
            'success': True,
            'message': '注册成功',
            'data': {
                'token': token,
                'user': {
                    'id': user_id,
                    'username': username,
                    'email': email,
                    'phone': phone,
                    'totalLingzhi': 0
                }
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'注册失败: {str(e)}'
        }), 500

@app.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({
                'success': False,
                'message': '用户名和密码不能为空'
            }), 400

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )
        user = cursor.fetchone()
        conn.close()

        if not user:
            return jsonify({
                'success': False,
                'message': '用户名或密码错误'
            }), 401

        if user['password_hash'] != hash_password(password):
            return jsonify({
                'success': False,
                'message': '用户名或密码错误'
            }), 401

        # 生成token
        token = generate_token(user['id'])

        return jsonify({
            'success': True,
            'message': '登录成功',
            'data': {
                'token': token,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'phone': user['phone'],
                    'totalLingzhi': user['total_lingzhi']
                }
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'登录失败: {str(e)}'
        }), 500

@app.route('/api/user/info', methods=['GET'])
def get_user_info():
    """获取用户信息"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': '未授权'
            }), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)

        if not user_id:
            return jsonify({
                'success': False,
                'message': 'token无效'
            }), 401

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'phone': user['phone'],
                'totalLingzhi': user['total_lingzhi']
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取用户信息失败: {str(e)}'
        }), 500

# ============ 签到功能 ============

@app.route('/api/checkin', methods=['POST'])
def checkin():
    """签到"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': '未授权'
            }), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)

        if not user_id:
            return jsonify({
                'success': False,
                'message': 'token无效'
            }), 401

        today = date.today()
        lingzhi_earned = 10

        conn = get_db()
        cursor = conn.cursor()

        # 检查今天是否已签到
        cursor.execute(
            "SELECT * FROM checkin_records WHERE user_id = ? AND checkin_date = ?",
            (user_id, today)
        )
        if cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'message': '今天已经签到过了'
            }), 400

        # 插入签到记录
        cursor.execute(
            "INSERT INTO checkin_records (user_id, checkin_date, lingzhi_earned) VALUES (?, ?, ?)",
            (user_id, today, lingzhi_earned)
        )

        # 更新用户总灵值
        cursor.execute(
            "UPDATE users SET total_lingzhi = total_lingzhi + ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (lingzhi_earned, user_id)
        )

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '签到成功',
            'data': {
                'lingzhi': lingzhi_earned
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'签到失败: {str(e)}'
        }), 500

@app.route('/api/checkin/status', methods=['GET'])
def checkin_status():
    """获取今日签到状态"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': '未授权'
            }), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)

        if not user_id:
            return jsonify({
                'success': False,
                'message': 'token无效'
            }), 401

        today = date.today()

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM checkin_records WHERE user_id = ? AND checkin_date = ?",
            (user_id, today)
        )
        record = cursor.fetchone()
        conn.close()

        if record:
            return jsonify({
                'success': True,
                'data': {
                    'checkedIn': True,
                    'lingzhi': record['lingzhi_earned']
                }
            })
        else:
            return jsonify({
                'success': True,
                'data': {
                    'checkedIn': False,
                    'lingzhi': 0
                }
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取签到状态失败: {str(e)}'
        }), 500

# ============ 后台管理 ============

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """管理员登录"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({
                'success': False,
                'message': '用户名和密码不能为空'
            }), 400

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM admins WHERE username = ?",
            (username,)
        )
        admin = cursor.fetchone()
        conn.close()

        if not admin:
            return jsonify({
                'success': False,
                'message': '用户名或密码错误'
            }), 401

        if admin['password_hash'] != hash_password(password):
            return jsonify({
                'success': False,
                'message': '用户名或密码错误'
            }), 401

        # 生成token
        token = generate_token(admin['id'])

        return jsonify({
            'success': True,
            'message': '登录成功',
            'data': {
                'token': token,
                'admin': {
                    'id': admin['id'],
                    'username': admin['username'],
                    'role': admin['role']
                }
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'登录失败: {str(e)}'
        }), 500

@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    """获取系统统计"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': '未授权'
            }), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)

        if not user_id:
            return jsonify({
                'success': False,
                'message': 'token无效'
            }), 401

        conn = get_db()
        cursor = conn.cursor()

        # 用户总数
        cursor.execute("SELECT COUNT(*) as count FROM users")
        total_users = cursor.fetchone()['count']

        # 今日签到数
        today = date.today()
        cursor.execute("SELECT COUNT(*) as count FROM checkin_records WHERE checkin_date = ?", (today,))
        today_checkins = cursor.fetchone()['count']

        # 总灵值
        cursor.execute("SELECT SUM(total_lingzhi) as total FROM users")
        total_lingzhi = cursor.fetchone()['total'] or 0

        # 合伙人申请数
        cursor.execute("SELECT COUNT(*) as count FROM partner_applications WHERE status = 'pending'")
        pending_applications = cursor.fetchone()['count']

        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'totalUsers': total_users,
                'todayCheckIns': today_checkins,
                'totalLingzhi': total_lingzhi,
                'pendingApplications': pending_applications
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取统计数据失败: {str(e)}'
        }), 500

# ============ 启动服务 ============

if __name__ == '__main__':
    print("=" * 50)
    print("灵值生态园 API 服务启动中...")
    print("=" * 50)
    print("服务地址: http://0.0.0.0:8001")
    print("默认管理员账号: admin / admin123")
    print("=" * 50)

    app.run(host='0.0.0.0', port=8001, debug=True)

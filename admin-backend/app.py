from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, date
import sqlite3
import hashlib
import jwt
import os
import bcrypt
import random
import string

app = Flask(__name__)
CORS(app)

# 配置
SECRET_KEY = os.getenv('SECRET_KEY', 'lingzhi-ecosystem-secret-key-2026')
DATABASE = 'lingzhi_ecosystem.db'
OLD_DATABASE = '../../灵值生态园智能体移植包/src/auth/auth.db'  # 旧数据库路径

# JWT 配置
JWT_SECRET = os.getenv('JWT_SECRET', 'lingzhi-jwt-secret-key')
JWT_EXPIRATION = 7 * 24 * 60 * 60  # 7天

# 验证码存储（模拟短信验证码）
verification_codes = {}  # {phone: {'code': '123456', 'expire_at': timestamp}}

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

    # 智能体表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            system_prompt TEXT,
            model_config TEXT,
            tools TEXT,
            status TEXT DEFAULT 'active',
            avatar_url TEXT,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES admins(id)
        )
    ''')

    # 知识库表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS knowledge_bases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            vector_db_id TEXT,
            document_count INTEGER DEFAULT 0,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES admins(id)
        )
    ''')

    # 知识库文档表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS knowledge_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            knowledge_base_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            file_path TEXT,
            file_type TEXT,
            file_size INTEGER,
            embedding_status TEXT DEFAULT 'pending',
            embedding_error TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_bases(id)
        )
    ''')

    # 智能体-知识库关联表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agent_knowledge_bases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id INTEGER NOT NULL,
            knowledge_base_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (agent_id) REFERENCES agents(id),
            FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_bases(id),
            UNIQUE(agent_id, knowledge_base_id)
        )
    ''')

    # 对话记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id INTEGER NOT NULL,
            user_id INTEGER,
            conversation_id TEXT,
            messages TEXT,
            title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (agent_id) REFERENCES agents(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # 反馈表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER,
            agent_id INTEGER NOT NULL,
            user_id INTEGER,
            rating INTEGER,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id),
            FOREIGN KEY (agent_id) REFERENCES agents(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
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
    """密码哈希（SHA256）"""
    return hashlib.sha256(password.encode()).hexdigest()

def hash_password_bcrypt(password):
    """密码哈希（bcrypt）"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password, password_hash):
    """验证密码（支持 SHA256 和 bcrypt）"""
    # 先尝试 SHA256
    if password_hash == hashlib.sha256(password.encode()).hexdigest():
        return True
    
    # 再尝试 bcrypt
    try:
        if password_hash.startswith('$2b$'):
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except:
        pass
    
    return False

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

# 迁移旧用户数据
def migrate_old_users():
    """从旧数据库迁移用户数据"""
    old_db_path = os.path.join(os.path.dirname(__file__), OLD_DATABASE)
    if not os.path.exists(old_db_path):
        print("旧数据库不存在，跳过迁移")
        return
    
    conn_old = sqlite3.connect(old_db_path)
    cursor_old = conn_old.cursor()
    
    # 查询旧用户
    cursor_old.execute("SELECT id, name, email, phone, password_hash, created_at FROM users")
    old_users = cursor_old.fetchall()
    
    if not old_users:
        print("旧数据库中没有用户数据")
        conn_old.close()
        return
    
    conn_new = get_db()
    cursor_new = conn_new.cursor()
    
    migrated_count = 0
    for old_user in old_users:
        old_id, name, email, phone, password_hash, created_at = old_user
        
        # 检查是否已存在（按邮箱）
        cursor_new.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor_new.fetchone():
            continue
        
        # 插入新用户（使用 name 作为 username）
        try:
            cursor_new.execute(
                "INSERT INTO users (username, email, phone, password_hash, total_lingzhi, created_at) VALUES (?, ?, ?, ?, 0, ?)",
                (name, email, phone or '', password_hash, created_at)
            )
            migrated_count += 1
            print(f"迁移用户: {name} ({email})")
        except Exception as e:
            print(f"迁移用户失败 {name}: {e}")
    
    conn_new.commit()
    conn_new.close()
    conn_old.close()
    
    if migrated_count > 0:
        print(f"成功迁移 {migrated_count} 个用户")
    else:
        print("没有新用户需要迁移")

# 执行迁移
migrate_old_users()

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

        if not verify_password(password, user['password_hash']):
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

        if not verify_password(password, admin['password_hash']):
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

# ============ 忘记密码 ============

@app.route('/api/send-code', methods=['POST'])
def send_code():
    """发送验证码"""
    try:
        data = request.json
        phone = data.get('phone')

        if not phone:
            return jsonify({
                'success': False,
                'message': '手机号不能为空'
            }), 400

        if not phone.isdigit() or len(phone) != 11:
            return jsonify({
                'success': False,
                'message': '手机号格式不正确'
            }), 400

        # 查询用户是否存在
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE phone = ?", (phone,))
        user = cursor.fetchone()
        conn.close()

        if not user:
            return jsonify({
                'success': False,
                'message': '该手机号未注册'
            }), 400

        # 生成6位验证码
        code = ''.join(random.choices(string.digits, k=6))
        expire_at = datetime.utcnow().timestamp() + 300  # 5分钟有效期

        # 存储验证码
        verification_codes[phone] = {
            'code': code,
            'expire_at': expire_at
        }

        # 打印验证码到控制台（模拟短信发送）
        print(f"短信验证码已发送到 {phone}: {code}")

        return jsonify({
            'success': True,
            'message': '验证码已发送'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'发送验证码失败: {str(e)}'
        }), 500

@app.route('/api/verify-code', methods=['POST'])
def verify_code():
    """验证验证码"""
    try:
        data = request.json
        phone = data.get('phone')
        code = data.get('code')

        if not phone or not code:
            return jsonify({
                'success': False,
                'message': '手机号和验证码不能为空'
            }), 400

        # 检查验证码
        if phone not in verification_codes:
            return jsonify({
                'success': False,
                'message': '验证码不存在或已过期'
            }), 400

        stored_code = verification_codes[phone]

        # 检查是否过期
        if datetime.utcnow().timestamp() > stored_code['expire_at']:
            del verification_codes[phone]
            return jsonify({
                'success': False,
                'message': '验证码已过期'
            }), 400

        # 验证码是否正确
        if stored_code['code'] != code:
            return jsonify({
                'success': False,
                'message': '验证码错误'
            }), 400

        return jsonify({
            'success': True,
            'message': '验证码正确'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'验证失败: {str(e)}'
        }), 500

@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    """重置密码"""
    try:
        data = request.json
        phone = data.get('phone')
        code = data.get('code')
        new_password = data.get('newPassword')

        if not phone or not code or not new_password:
            return jsonify({
                'success': False,
                'message': '参数不完整'
            }), 400

        if len(new_password) < 6:
            return jsonify({
                'success': False,
                'message': '密码长度至少6位'
            }), 400

        # 再次验证验证码
        if phone not in verification_codes:
            return jsonify({
                'success': False,
                'message': '验证码不存在或已过期'
            }), 400

        stored_code = verification_codes[phone]

        if datetime.utcnow().timestamp() > stored_code['expire_at']:
            del verification_codes[phone]
            return jsonify({
                'success': False,
                'message': '验证码已过期'
            }), 400

        if stored_code['code'] != code:
            return jsonify({
                'success': False,
                'message': '验证码错误'
            }), 400

        # 更新密码
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET password_hash = ? WHERE phone = ?",
            (hash_password(new_password), phone)
        )
        conn.commit()
        conn.close()

        # 清除验证码
        del verification_codes[phone]

        return jsonify({
            'success': True,
            'message': '密码重置成功'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'重置密码失败: {str(e)}'
        }), 500

# ============ 智能体管理 ============

@app.route('/api/admin/agents', methods=['GET'])
def get_agents():
    """获取智能体列表"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, name, description, status, avatar_url, created_at, updated_at
            FROM agents
            ORDER BY created_at DESC
        ''')
        agents = cursor.fetchall()
        conn.close()

        return jsonify({
            'success': True,
            'data': [dict(agent) for agent in agents]
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取智能体列表失败: {str(e)}'
        }), 500

@app.route('/api/admin/agents', methods=['POST'])
def create_agent():
    """创建智能体"""
    try:
        data = request.json
        name = data.get('name')
        description = data.get('description', '')
        system_prompt = data.get('system_prompt', '')
        model_config = data.get('model_config', {})
        tools = data.get('tools', [])
        avatar_url = data.get('avatar_url', '')

        if not name:
            return jsonify({
                'success': False,
                'message': '智能体名称不能为空'
            }), 400

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO agents (name, description, system_prompt, model_config, tools, avatar_url)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            name,
            description,
            system_prompt,
            json.dumps(model_config),
            json.dumps(tools),
            avatar_url
        ))
        agent_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '智能体创建成功',
            'data': {'id': agent_id}
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'创建智能体失败: {str(e)}'
        }), 500

@app.route('/api/admin/agents/<int:agent_id>', methods=['GET'])
def get_agent_detail(agent_id):
    """获取智能体详情"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM agents WHERE id = ?
        ''', (agent_id,))
        agent = cursor.fetchone()
        conn.close()

        if not agent:
            return jsonify({
                'success': False,
                'message': '智能体不存在'
            }), 404

        return jsonify({
            'success': True,
            'data': dict(agent)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取智能体详情失败: {str(e)}'
        }), 500

@app.route('/api/admin/agents/<int:agent_id>', methods=['PUT'])
def update_agent(agent_id):
    """更新智能体"""
    try:
        data = request.json
        name = data.get('name')
        description = data.get('description')
        system_prompt = data.get('system_prompt')
        model_config = data.get('model_config')
        tools = data.get('tools')
        avatar_url = data.get('avatar_url')
        status = data.get('status')

        conn = get_db()
        cursor = conn.cursor()

        # 检查智能体是否存在
        cursor.execute('SELECT id FROM agents WHERE id = ?', (agent_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'message': '智能体不存在'
            }), 404

        # 构建更新语句
        update_fields = []
        update_values = []
        
        if name is not None:
            update_fields.append('name = ?')
            update_values.append(name)
        if description is not None:
            update_fields.append('description = ?')
            update_values.append(description)
        if system_prompt is not None:
            update_fields.append('system_prompt = ?')
            update_values.append(system_prompt)
        if model_config is not None:
            update_fields.append('model_config = ?')
            update_values.append(json.dumps(model_config))
        if tools is not None:
            update_fields.append('tools = ?')
            update_values.append(json.dumps(tools))
        if avatar_url is not None:
            update_fields.append('avatar_url = ?')
            update_values.append(avatar_url)
        if status is not None:
            update_fields.append('status = ?')
            update_values.append(status)

        if update_fields:
            update_fields.append('updated_at = CURRENT_TIMESTAMP')
            update_values.append(agent_id)

            cursor.execute(f'''
                UPDATE agents
                SET {', '.join(update_fields)}
                WHERE id = ?
            ''', update_values)

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '智能体更新成功'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新智能体失败: {str(e)}'
        }), 500

@app.route('/api/admin/agents/<int:agent_id>', methods=['DELETE'])
def delete_agent(agent_id):
    """删除智能体"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        # 检查智能体是否存在
        cursor.execute('SELECT id FROM agents WHERE id = ?', (agent_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'message': '智能体不存在'
            }), 404

        cursor.execute('DELETE FROM agents WHERE id = ?', (agent_id,))
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '智能体删除成功'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'删除智能体失败: {str(e)}'
        }), 500

# ============ 知识库管理 ============

@app.route('/api/admin/knowledge-bases', methods=['GET'])
def get_knowledge_bases():
    """获取知识库列表"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, name, description, vector_db_id, document_count, created_at, updated_at
            FROM knowledge_bases
            ORDER BY created_at DESC
        ''')
        kbs = cursor.fetchall()
        conn.close()

        return jsonify({
            'success': True,
            'data': [dict(kb) for kb in kbs]
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取知识库列表失败: {str(e)}'
        }), 500

@app.route('/api/admin/knowledge-bases', methods=['POST'])
def create_knowledge_base():
    """创建知识库"""
    try:
        data = request.json
        name = data.get('name')
        description = data.get('description', '')

        if not name:
            return jsonify({
                'success': False,
                'message': '知识库名称不能为空'
            }), 400

        conn = get_db()
        cursor = conn.cursor()

        # 生成 vector_db_id
        vector_db_id = f"kb_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        cursor.execute('''
            INSERT INTO knowledge_bases (name, description, vector_db_id)
            VALUES (?, ?, ?)
        ''', (name, description, vector_db_id))
        kb_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '知识库创建成功',
            'data': {'id': kb_id, 'vector_db_id': vector_db_id}
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'创建知识库失败: {str(e)}'
        }), 500

@app.route('/api/admin/knowledge-bases/<int:kb_id>', methods=['GET'])
def get_knowledge_base_detail(kb_id):
    """获取知识库详情"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM knowledge_bases WHERE id = ?
        ''', (kb_id,))
        kb = cursor.fetchone()

        if not kb:
            conn.close()
            return jsonify({
                'success': False,
                'message': '知识库不存在'
            }), 404

        # 获取文档列表
        cursor.execute('''
            SELECT id, title, content, file_type, file_size, embedding_status, created_at
            FROM knowledge_documents
            WHERE knowledge_base_id = ?
            ORDER BY created_at DESC
        ''', (kb_id,))
        documents = cursor.fetchall()

        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'knowledge_base': dict(kb),
                'documents': [dict(doc) for doc in documents]
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取知识库详情失败: {str(e)}'
        }), 500

@app.route('/api/admin/knowledge-bases/<int:kb_id>', methods=['PUT'])
def update_knowledge_base(kb_id):
    """更新知识库"""
    try:
        data = request.json
        name = data.get('name')
        description = data.get('description')

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM knowledge_bases WHERE id = ?', (kb_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'message': '知识库不存在'
            }), 404

        update_fields = []
        update_values = []

        if name is not None:
            update_fields.append('name = ?')
            update_values.append(name)
        if description is not None:
            update_fields.append('description = ?')
            update_values.append(description)

        if update_fields:
            update_fields.append('updated_at = CURRENT_TIMESTAMP')
            update_values.append(kb_id)

            cursor.execute(f'''
                UPDATE knowledge_bases
                SET {', '.join(update_fields)}
                WHERE id = ?
            ''', update_values)

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '知识库更新成功'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新知识库失败: {str(e)}'
        }), 500

@app.route('/api/admin/knowledge-bases/<int:kb_id>', methods=['DELETE'])
def delete_knowledge_base(kb_id):
    """删除知识库"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM knowledge_bases WHERE id = ?', (kb_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'message': '知识库不存在'
            }), 404

        # 删除知识库的所有文档
        cursor.execute('DELETE FROM knowledge_documents WHERE knowledge_base_id = ?', (kb_id,))
        # 删除知识库
        cursor.execute('DELETE FROM knowledge_bases WHERE id = ?', (kb_id,))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '知识库删除成功'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'删除知识库失败: {str(e)}'
        }), 500

@app.route('/api/admin/knowledge-bases/<int:kb_id>/documents', methods=['POST'])
def upload_document(kb_id):
    """上传文档到知识库"""
    try:
        # 检查是否是 multipart/form-data
        if not request.files:
            return jsonify({
                'success': False,
                'message': '请上传文件'
            }), 400

        file = request.files.get('file')
        if not file:
            return jsonify({
                'success': False,
                'message': '请上传文件'
            }), 400

        if file.filename == '':
            return jsonify({
                'success': False,
                'message': '文件名为空'
            }), 400

        # 读取文件内容
        content = file.read().decode('utf-8', errors='ignore')
        file_type = file.filename.split('.')[-1] if '.' in file.filename else 'txt'
        file_size = len(content)

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM knowledge_bases WHERE id = ?', (kb_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'message': '知识库不存在'
            }), 404

        # 插入文档记录
        cursor.execute('''
            INSERT INTO knowledge_documents (knowledge_base_id, title, content, file_type, file_size)
            VALUES (?, ?, ?, ?, ?)
        ''', (kb_id, file.filename, content, file_type, file_size))

        doc_id = cursor.lastrowid

        # 更新文档计数
        cursor.execute('''
            UPDATE knowledge_bases
            SET document_count = document_count + 1
            WHERE id = ?
        ''', (kb_id,))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '文档上传成功',
            'data': {'id': doc_id}
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'上传文档失败: {str(e)}'
        }), 500

@app.route('/api/admin/knowledge-bases/<int:kb_id>/documents', methods=['POST'])
def add_document_text(kb_id):
    """添加文本内容到知识库"""
    try:
        data = request.json
        title = data.get('title', '')
        content = data.get('content', '')

        if not content:
            return jsonify({
                'success': False,
                'message': '内容不能为空'
            }), 400

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM knowledge_bases WHERE id = ?', (kb_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'message': '知识库不存在'
            }), 404

        cursor.execute('''
            INSERT INTO knowledge_documents (knowledge_base_id, title, content, file_type, file_size)
            VALUES (?, ?, ?, 'text', ?)
        ''', (kb_id, title, content, len(content)))

        doc_id = cursor.lastrowid

        cursor.execute('''
            UPDATE knowledge_bases
            SET document_count = document_count + 1
            WHERE id = ?
        ''', (kb_id,))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '内容添加成功',
            'data': {'id': doc_id}
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'添加内容失败: {str(e)}'
        }), 500

@app.route('/api/admin/knowledge-bases/<int:kb_id>/documents/<int:doc_id>', methods=['DELETE'])
def delete_document(kb_id, doc_id):
    """删除文档"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM knowledge_documents WHERE id = ? AND knowledge_base_id = ?', (doc_id, kb_id))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'message': '文档不存在'
            }), 404

        cursor.execute('DELETE FROM knowledge_documents WHERE id = ? AND knowledge_base_id = ?', (doc_id, kb_id))

        cursor.execute('''
            UPDATE knowledge_bases
            SET document_count = document_count - 1
            WHERE id = ?
        ''', (kb_id,))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '文档删除成功'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'删除文档失败: {str(e)}'
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

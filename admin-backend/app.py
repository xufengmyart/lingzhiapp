from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, date, timedelta
import sqlite3
import hashlib
import jwt
import os
import bcrypt
import random
import string
import json

# 设置 Coze 环境变量（如果未设置）
os.environ.setdefault('COZE_WORKLOAD_IDENTITY_API_KEY', 'WU9RNGFQTmZTc3VnbnRCMmsyWUtDcDZHOWJMa0g5ZVk6NVN5cHNRbkNidjFzWHNEVnJ4UTZKQlN1SUxYMlU3ZEtidVRXbDYwWDFyZW9sdmhQbTU1QVdQaVJHcVo4b1BoWA==')
os.environ.setdefault('COZE_INTEGRATION_MODEL_BASE_URL', 'https://integration.coze.cn/api/v3')
os.environ.setdefault('COZE_INTEGRATION_BASE_URL', 'https://integration.coze.cn')
os.environ.setdefault('COZE_PROJECT_ID', '7597768668038643746')

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# 导入大模型 SDK
try:
    from coze_coding_dev_sdk import LLMClient
    from coze_coding_utils.runtime_ctx.context import new_context
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("警告: coze_coding_dev_sdk 未安装，智能对话功能将不可用")

app = Flask(__name__)
CORS(app)

# 配置
SECRET_KEY = os.getenv('SECRET_KEY', 'lingzhi-ecosystem-secret-key-2026')
DATABASE = 'lingzhi_ecosystem.db'
OLD_DATABASE = '../../灵值生态园智能体移植包/src/auth/auth.db'  # 旧数据库路径

# JWT 配置
JWT_SECRET = os.getenv('JWT_SECRET', 'lingzhi-jwt-secret-key')
JWT_EXPIRATION = 7 * 24 * 60 * 60  # 7天

# 微信开放平台配置
WECHAT_APP_ID = os.getenv('WECHAT_APP_ID', '')
WECHAT_APP_SECRET = os.getenv('WECHAT_APP_SECRET', '')
WECHAT_REDIRECT_URI = os.getenv('WECHAT_REDIRECT_URI', 'http://localhost:3000/wechat/callback')

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
            status TEXT DEFAULT 'active',
            last_login_at TIMESTAMP,
            avatar_url TEXT,
            real_name TEXT,
            is_verified BOOLEAN DEFAULT 0,
            login_type TEXT DEFAULT 'phone',
            wechat_openid TEXT UNIQUE,
            wechat_unionid TEXT,
            wechat_nickname TEXT,
            wechat_avatar TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 添加新字段（如果表已存在）
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'active'")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN last_login_at TIMESTAMP")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN avatar_url TEXT")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN real_name TEXT")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT 0")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN login_type TEXT DEFAULT 'phone'")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN wechat_openid TEXT UNIQUE")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN wechat_unionid TEXT")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN wechat_nickname TEXT")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN wechat_avatar TEXT")
    except:
        pass

    # 用户详细信息表（用于完善信息）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            real_name TEXT,
            phone TEXT UNIQUE,
            email TEXT UNIQUE,
            id_card TEXT,
            bank_account TEXT,
            bank_name TEXT,
            address TEXT,
            is_completed BOOLEAN DEFAULT 0,
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
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
            agent_id INTEGER,
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
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            rating INTEGER,
            question TEXT,
            comment TEXT,
            contribution_value INTEGER DEFAULT 5,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id),
            FOREIGN KEY (agent_id) REFERENCES agents(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # 充值档位表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recharge_tiers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price DECIMAL(10,2) NOT NULL,
            base_lingzhi INTEGER NOT NULL,
            bonus_lingzhi INTEGER NOT NULL,
            bonus_percentage INTEGER NOT NULL,
            partner_level INTEGER DEFAULT 0,
            benefits TEXT,
            status TEXT DEFAULT 'active',
            sort_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 充值记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recharge_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            tier_id INTEGER NOT NULL,
            order_no TEXT UNIQUE NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            base_lingzhi INTEGER NOT NULL,
            bonus_lingzhi INTEGER NOT NULL,
            total_lingzhi INTEGER NOT NULL,
            payment_method VARCHAR(20) DEFAULT 'online',
            payment_status VARCHAR(20) DEFAULT 'pending',
            payment_time TIMESTAMP,
            transaction_id TEXT,
            voucher_id INTEGER,
            audit_status VARCHAR(20),
            bank_info TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (tier_id) REFERENCES recharge_tiers(id)
        )
    ''')

    # 灵值消费记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lingzhi_consumption_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            consumption_type TEXT NOT NULL,
            consumption_item TEXT NOT NULL,
            lingzhi_amount INTEGER NOT NULL,
            item_id INTEGER,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # 用户权益表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_benefits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            benefit_type TEXT NOT NULL,
            benefit_name TEXT NOT NULL,
            benefit_count INTEGER DEFAULT 0,
            benefit_expiry TIMESTAMP,
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # 公司收款账户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS company_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_name VARCHAR(200) NOT NULL,
            account_number VARCHAR(50) NOT NULL,
            bank_name VARCHAR(200) NOT NULL,
            bank_branch VARCHAR(200),
            company_name VARCHAR(200) NOT NULL,
            company_credit_code VARCHAR(50),
            account_type VARCHAR(20) NOT NULL DEFAULT 'primary',
            is_active BOOLEAN DEFAULT 1,
            sort_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 转账凭证表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transfer_vouchers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recharge_record_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            image_url VARCHAR(500) NOT NULL,
            transfer_amount DECIMAL(10, 2) NOT NULL,
            transfer_time TIMESTAMP,
            transfer_account VARCHAR(200),
            remark TEXT,
            audit_status VARCHAR(20) DEFAULT 'pending',
            audit_user_id INTEGER,
            audit_time TIMESTAMP,
            audit_remark TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (recharge_record_id) REFERENCES recharge_records(id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (audit_user_id) REFERENCES admins(id)
        )
    ''')

    # 系统通知表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            notification_type TEXT DEFAULT 'info',
            is_read BOOLEAN DEFAULT 0,
            target_user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (target_user_id) REFERENCES users(id)
        )
    ''')

    # 用户已读通知记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_read_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            notification_id INTEGER NOT NULL,
            read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, notification_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (notification_id) REFERENCES system_notifications(id)
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
    # 先尝试 bcrypt
    try:
        if password_hash.startswith('$2b$'):
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception as e:
        print(f"bcrypt 验证失败: {e}")
    
    # 再尝试 SHA256
    try:
        if password_hash == hashlib.sha256(password.encode()).hexdigest():
            return True
    except Exception as e:
        print(f"SHA256 验证失败: {e}")
    
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

# 迁移旧用户数据（仅在首次启动时执行）
MIGRATED = False

def backup_database():
    """备份数据库"""
    try:
        import shutil
        from datetime import datetime
        
        # 创建备份目录
        backup_dir = os.path.join(os.path.dirname(__file__), 'backups')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # 备份文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f'lingzhi_ecosystem_backup_{timestamp}.db')
        
        # 复制数据库
        shutil.copy2(DATABASE, backup_file)
        print(f"数据库备份成功: {backup_file}")
        
        # 清理旧备份（保留最近 7 天）
        import time
        current_time = time.time()
        for filename in os.listdir(backup_dir):
            file_path = os.path.join(backup_dir, filename)
            file_time = os.path.getmtime(file_path)
            if current_time - file_time > 7 * 24 * 3600:  # 7天
                os.remove(file_path)
                print(f"删除旧备份: {filename}")
        
        return True
    except Exception as e:
        print(f"数据库备份失败: {e}")
        return False

def migrate_old_users():
    """从旧数据库迁移用户数据"""
    global MIGRATED
    
    # 防止重复迁移
    if MIGRATED:
        print("用户数据已迁移，跳过")
        return
    
    old_db_path = os.path.join(os.path.dirname(__file__), OLD_DATABASE)
    if not os.path.exists(old_db_path):
        print("旧数据库不存在，跳过迁移")
        MIGRATED = True
        return
    
    # 检查新数据库是否已有用户
    conn_new = get_db()
    cursor_new = conn_new.cursor()
    cursor_new.execute("SELECT COUNT(*) FROM users")
    new_user_count = cursor_new.fetchone()[0]
    conn_new.close()
    
    if new_user_count > 0:
        print(f"新数据库已有 {new_user_count} 个用户，跳过迁移")
        MIGRATED = True
        return
    
    print("开始迁移用户数据...")
    
    conn_old = sqlite3.connect(old_db_path)
    cursor_old = conn_old.cursor()
    
    # 查询旧用户
    cursor_old.execute("SELECT id, name, email, phone, password_hash, created_at FROM users")
    old_users = cursor_old.fetchall()
    
    if not old_users:
        print("旧数据库中没有用户数据")
        conn_old.close()
        MIGRATED = True
        return
    
    conn_new = get_db()
    cursor_new = conn_new.cursor()
    
    migrated_count = 0
    for old_user in old_users:
        old_id, name, email, phone, password_hash, created_at = old_user
        
        # 处理重复邮箱：添加后缀
        username = name
        if email:
            # 检查是否已存在相同邮箱的用户
            cursor_new.execute("SELECT COUNT(*) FROM users WHERE email = ?", (email,))
            email_count = cursor_new.fetchone()[0]
            if email_count > 0:
                # 添加序号后缀
                username = f"{name}_{old_id}"
        
        # 检查是否已存在相同用户名的用户
        cursor_new.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor_new.fetchone():
            continue
        
        # 插入新用户（使用 name 作为 username）
        try:
            cursor_new.execute(
                """INSERT INTO users 
                   (username, email, phone, password_hash, total_lingzhi, status, login_type, created_at) 
                   VALUES (?, ?, ?, ?, 0, 'active', 'phone', ?)""",
                (username, email or '', phone or '', password_hash, created_at)
            )
            migrated_count += 1
            print(f"迁移用户: {username} ({email or '无邮箱'})")
        except Exception as e:
            print(f"迁移用户失败 {username}: {e}")
    
    conn_new.commit()
    conn_new.close()
    conn_old.close()
    
    MIGRATED = True
    
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

# ============ 找回密码 ============

@app.route('/api/send-code', methods=['POST'])
def send_code():
    """发送短信验证码"""
    try:
        data = request.json
        phone = data.get('phone')

        if not phone:
            return jsonify({
                'success': False,
                'message': '手机号不能为空'
            }), 400

        # 检查手机号格式
        if not phone.isdigit() or len(phone) != 11 or not phone.startswith('1'):
            return jsonify({
                'success': False,
                'message': '手机号格式不正确'
            }), 400

        conn = get_db()
        cursor = conn.cursor()

        # 检查手机号是否已注册
        cursor.execute("SELECT id FROM users WHERE phone = ?", (phone,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'message': '该手机号未注册，请使用"用户名+邮箱"方式找回密码'
            }), 400

        # 生成6位验证码
        code = ''.join(random.choices(string.digits, k=6))

        # 存储验证码（5分钟有效期）
        verification_codes[phone] = {
            'code': code,
            'expire_at': datetime.now().timestamp() + 300
        }

        print(f"[调试] 手机号 {phone} 验证码: {code}")

        # TODO: 实际项目中需要调用短信服务发送验证码
        # 这里为了演示，直接返回成功

        conn.close()
        return jsonify({
            'success': True,
            'message': '验证码已发送',
            'data': {
                'code': code  # 仅用于测试，生产环境需要删除
            }
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

        stored = verification_codes[phone]

        # 检查是否过期
        if datetime.now().timestamp() > stored['expire_at']:
            del verification_codes[phone]
            return jsonify({
                'success': False,
                'message': '验证码已过期'
            }), 400

        # 验证码校验
        if stored['code'] != code:
            return jsonify({
                'success': False,
                'message': '验证码错误'
            }), 400

        return jsonify({
            'success': True,
            'message': '验证码验证成功'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'验证失败: {str(e)}'
        }), 500

@app.route('/api/verify-user', methods=['POST'])
def verify_user():
    """通过用户名和邮箱验证用户（用于老用户找回密码）"""
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')

        if not username or not email:
            return jsonify({
                'success': False,
                'message': '用户名和邮箱不能为空'
            }), 400

        conn = get_db()
        cursor = conn.cursor()

        # 查询用户
        cursor.execute(
            "SELECT id, username, email FROM users WHERE username = ? AND email = ?",
            (username, email)
        )
        user = cursor.fetchone()
        conn.close()

        if not user:
            return jsonify({
                'success': False,
                'message': '用户名或邮箱不正确'
            }), 400

        return jsonify({
            'success': True,
            'message': '验证成功',
            'data': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email']
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'验证失败: {str(e)}'
        }), 500

@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    """通过手机号和验证码重置密码"""
    try:
        data = request.json
        phone = data.get('phone')
        code = data.get('code')
        newPassword = data.get('newPassword')

        if not phone or not code or not newPassword:
            return jsonify({
                'success': False,
                'message': '参数不完整'
            }), 400

        # 再次验证验证码
        if phone not in verification_codes:
            return jsonify({
                'success': False,
                'message': '请先获取验证码'
            }), 400

        stored = verification_codes[phone]

        # 检查是否过期
        if datetime.now().timestamp() > stored['expire_at']:
            del verification_codes[phone]
            return jsonify({
                'success': False,
                'message': '验证码已过期'
            }), 400

        # 验证码校验
        if stored['code'] != code:
            return jsonify({
                'success': False,
                'message': '验证码错误'
            }), 400

        # 更新密码
        conn = get_db()
        cursor = conn.cursor()

        password_hash = hash_password(newPassword)
        cursor.execute(
            "UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE phone = ?",
            (password_hash, phone)
        )

        conn.commit()
        affected = cursor.rowcount
        conn.close()

        if affected == 0:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 400

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

@app.route('/api/reset-password-by-username', methods=['POST'])
def reset_password_by_username():
    """通过用户名和邮箱重置密码"""
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        newPassword = data.get('newPassword')

        if not username or not email or not newPassword:
            return jsonify({
                'success': False,
                'message': '参数不完整'
            }), 400

        conn = get_db()
        cursor = conn.cursor()

        # 查询用户
        cursor.execute(
            "SELECT id FROM users WHERE username = ? AND email = ?",
            (username, email)
        )
        user = cursor.fetchone()

        if not user:
            conn.close()
            return jsonify({
                'success': False,
                'message': '用户名或邮箱不正确'
            }), 400

        # 更新密码
        password_hash = hash_password(newPassword)
        cursor.execute(
            "UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (password_hash, user['id'])
        )

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '密码重置成功'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'重置密码失败: {str(e)}'
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

# ============ 用户反馈 ============

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """提交用户反馈"""
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

        data = request.json
        agent_id = data.get('agent_id', 1)  # 默认智能体ID为1
        feedback_type = data.get('type')  # helpful / not_helpful / suggestion
        question = data.get('question', '')
        comment = data.get('comment', '')
        rating = data.get('rating')  # 可选，评分

        if not feedback_type:
            return jsonify({
                'success': False,
                'message': '反馈类型不能为空'
            }), 400

        # 确定贡献值
        contribution_value = 5  # 默认5灵值
        if feedback_type == 'helpful':
            contribution_value = 3
        elif feedback_type == 'not_helpful':
            contribution_value = 5  # 收集负面反馈更宝贵
        elif feedback_type == 'suggestion':
            contribution_value = 10  # 建议最有价值

        conn = get_db()
        cursor = conn.cursor()

        # 插入反馈记录
        cursor.execute(
            """INSERT INTO feedback (agent_id, user_id, type, question, comment, rating, contribution_value)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (agent_id, user_id, feedback_type, question, comment, rating, contribution_value)
        )

        # 增加用户灵值
        cursor.execute(
            "UPDATE users SET total_lingzhi = total_lingzhi + ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (contribution_value, user_id)
        )

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': f'反馈提交成功，获得 {contribution_value} 灵值',
            'data': {
                'contribution_value': contribution_value
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'提交反馈失败: {str(e)}'
        }), 500

@app.route('/api/feedback', methods=['GET'])
def get_user_feedback():
    """获取用户反馈历史"""
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

        # 获取用户的反馈历史
        cursor.execute(
            """SELECT id, type, question, comment, rating, contribution_value, created_at
               FROM feedback WHERE user_id = ? ORDER BY created_at DESC LIMIT 20""",
            (user_id,)
        )
        feedback_list = cursor.fetchall()
        conn.close()

        return jsonify({
            'success': True,
            'data': [dict(f) for f in feedback_list]
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取反馈历史失败: {str(e)}'
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

# ============ 用户管理 ============

@app.route('/api/admin/users', methods=['GET'])
def admin_get_users():
    """获取用户列表"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': '未授权'
            }), 401

        token = auth_header.replace('Bearer ', '')
        admin_id = verify_token(token)
        if not admin_id:
            return jsonify({
                'success': False,
                'message': 'token无效'
            }), 401

        # 验证是否为管理员
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE id = ?", (admin_id,))
        admin = cursor.fetchone()
        if not admin:
            conn.close()
            return jsonify({
                'success': False,
                'message': '无权限'
            }), 403

        # 获取分页参数
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        search = request.args.get('search', '')

        offset = (page - 1) * limit

        # 构建查询
        where_clause = ''
        params = []
        if search:
            where_clause = "WHERE username LIKE ? OR email LIKE ? OR phone LIKE ?"
            search_pattern = f'%{search}%'
            params.extend([search_pattern, search_pattern, search_pattern])

        # 查询总数
        count_sql = f"SELECT COUNT(*) as total FROM users {where_clause}"
        cursor.execute(count_sql, params)
        total = cursor.fetchone()['total']

        # 查询用户列表
        list_sql = f"SELECT * FROM users {where_clause} ORDER BY id DESC LIMIT ? OFFSET ?"
        cursor.execute(list_sql, params + [limit, offset])
        users = cursor.fetchall()

        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'users': users,
                'total': total,
                'page': page,
                'limit': limit,
                'totalPages': (total + limit - 1) // limit
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取用户列表失败: {str(e)}'
        }), 500

@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
def admin_update_user(user_id):
    """更新用户信息"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': '未授权'
            }), 401

        token = auth_header.replace('Bearer ', '')
        admin_id = verify_token(token)
        if not admin_id:
            return jsonify({
                'success': False,
                'message': 'token无效'
            }), 401

        # 验证是否为管理员
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE id = ?", (admin_id,))
        admin = cursor.fetchone()
        if not admin:
            conn.close()
            return jsonify({
                'success': False,
                'message': '无权限'
            }), 403

        data = request.json
        username = data.get('username')
        email = data.get('email', '')
        phone = data.get('phone', '')
        total_lingzhi = data.get('total_lingzhi')

        if not username:
            return jsonify({
                'success': False,
                'message': '用户名不能为空'
            }), 400

        # 检查用户名是否重复
        cursor.execute("SELECT id FROM users WHERE username = ? AND id != ?", (username, user_id))
        if cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'message': '用户名已存在'
            }), 400

        # 更新用户
        cursor.execute(
            """UPDATE users SET username = ?, email = ?, phone = ?, total_lingzhi = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (username, email, phone, total_lingzhi, user_id)
        )

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '用户信息更新成功'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新用户失败: {str(e)}'
        }), 500

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
def admin_delete_user(user_id):
    """删除用户"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': '未授权'
            }), 401

        token = auth_header.replace('Bearer ', '')
        admin_id = verify_token(token)
        if not admin_id:
            return jsonify({
                'success': False,
                'message': 'token无效'
            }), 401

        # 验证是否为管理员
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE id = ?", (admin_id,))
        admin = cursor.fetchone()
        if not admin:
            conn.close()
            return jsonify({
                'success': False,
                'message': '无权限'
            }), 403

        # 检查用户是否存在
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404

        # 删除用户相关数据（级联删除）
        # 注意：需要先删除依赖数据
        cursor.execute("DELETE FROM checkin_records WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM partner_applications WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM conversations WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '用户删除成功'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'删除用户失败: {str(e)}'
        }), 500


@app.route('/api/admin/users/<int:user_id>', methods=['GET'])
def admin_get_user_detail(user_id):
    """获取用户详情"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        admin_id = verify_token(token)
        if not admin_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        # 验证是否为管理员
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE id = ?", (admin_id,))
        admin = cursor.fetchone()
        if not admin:
            conn.close()
            return jsonify({'success': False, 'message': '无权限'}), 403

        # 获取用户详情
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()

        if not user:
            conn.close()
            return jsonify({'success': False, 'message': '用户不存在'}), 404

        # 获取用户签到统计
        cursor.execute("SELECT COUNT(*) as count FROM checkin_records WHERE user_id = ?", (user_id,))
        checkin_count = cursor.fetchone()['count']

        # 获取用户充值记录
        cursor.execute("""
            SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total_amount 
            FROM recharge_records 
            WHERE user_id = ? AND payment_status = 'paid'
        """, (user_id,))
        recharge_stats = cursor.fetchone()

        # 获取用户消费记录
        cursor.execute("""
            SELECT COUNT(*) as count, COALESCE(SUM(lingzhi_amount), 0) as total_lingzhi 
            FROM lingzhi_consumption_records 
            WHERE user_id = ?
        """, (user_id,))
        consumption_stats = cursor.fetchone()

        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'phone': user['phone'],
                'total_lingzhi': user['total_lingzhi'],
                'status': user.get('status', 'active'),
                'last_login_at': user.get('last_login_at'),
                'avatar_url': user.get('avatar_url'),
                'real_name': user.get('real_name'),
                'is_verified': user.get('is_verified', 0),
                'created_at': user['created_at'],
                'updated_at': user['updated_at'],
                'stats': {
                    'checkin_count': checkin_count,
                    'recharge_count': recharge_stats['count'],
                    'recharge_amount': float(recharge_stats['total_amount']),
                    'consumption_count': consumption_stats['count'],
                    'consumption_lingzhi': consumption_stats['total_lingzhi']
                }
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取用户详情失败: {str(e)}'}), 500

@app.route('/api/admin/users/<int:user_id>/status', methods=['PUT'])
def admin_update_user_status(user_id):
    """更新用户状态"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        admin_id = verify_token(token)
        if not admin_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        # 验证是否为管理员
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE id = ?", (admin_id,))
        admin = cursor.fetchone()
        if not admin:
            conn.close()
            return jsonify({'success': False, 'message': '无权限'}), 403

        data = request.json
        status = data.get('status')

        if status not in ['active', 'inactive', 'banned']:
            return jsonify({'success': False, 'message': '无效的状态'}), 400

        # 检查用户是否存在
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'message': '用户不存在'}), 404

        # 更新用户状态
        cursor.execute(
            "UPDATE users SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (status, user_id)
        )
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': '用户状态更新成功'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'更新用户状态失败: {str(e)}'}), 500

@app.route('/api/admin/users/<int:user_id>/lingzhi', methods=['POST'])
def admin_adjust_user_lingzhi(user_id):
    """调整用户灵值"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        admin_id = verify_token(token)
        if not admin_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        # 验证是否为管理员
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE id = ?", (admin_id,))
        admin = cursor.fetchone()
        if not admin:
            conn.close()
            return jsonify({'success': False, 'message': '无权限'}), 403

        data = request.json
        amount = data.get('amount')
        reason = data.get('reason', '管理员调整')

        if not amount:
            return jsonify({'success': False, 'message': '调整金额不能为空'}), 400

        # 检查用户是否存在
        cursor.execute("SELECT id, total_lingzhi FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            conn.close()
            return jsonify({'success': False, 'message': '用户不存在'}), 404

        # 调整灵值
        new_lingzhi = user['total_lingzhi'] + amount
        if new_lingzhi < 0:
            conn.close()
            return jsonify({'success': False, 'message': '灵值余额不足'}), 400

        cursor.execute(
            "UPDATE users SET total_lingzhi = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (new_lingzhi, user_id)
        )
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '灵值调整成功',
            'data': {
                'old_lingzhi': user['total_lingzhi'],
                'new_lingzhi': new_lingzhi,
                'adjustment': amount
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'调整灵值失败: {str(e)}'}), 500

@app.route('/api/admin/users/search', methods=['GET'])
def admin_search_users():
    """搜索用户"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        admin_id = verify_token(token)
        if not admin_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        # 验证是否为管理员
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE id = ?", (admin_id,))
        admin = cursor.fetchone()
        if not admin:
            conn.close()
            return jsonify({'success': False, 'message': '无权限'}), 403

        keyword = request.args.get('keyword', '')
        limit = int(request.args.get('limit', 10))

        if not keyword:
            conn.close()
            return jsonify({'success': False, 'message': '搜索关键词不能为空'}), 400

        # 搜索用户
        search_pattern = f'%{keyword}%'
        cursor.execute("""
            SELECT id, username, email, phone, total_lingzhi, status, created_at
            FROM users
            WHERE username LIKE ? OR email LIKE ? OR phone LIKE ?
            ORDER BY id DESC
            LIMIT ?
        """, (search_pattern, search_pattern, search_pattern, limit))
        users = cursor.fetchall()
        conn.close()

        return jsonify({
            'success': True,
            'data': [dict(user) for user in users]
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'搜索用户失败: {str(e)}'}), 500

@app.route('/api/admin/users/export', methods=['GET'])
def admin_export_users():
    """导出用户列表"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        admin_id = verify_token(token)
        if not admin_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        # 验证是否为管理员
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE id = ?", (admin_id,))
        admin = cursor.fetchone()
        if not admin:
            conn.close()
            return jsonify({'success': False, 'message': '无权限'}), 403

        # 获取所有用户
        cursor.execute("""
            SELECT id, username, email, phone, total_lingzhi, status, created_at
            FROM users
            ORDER BY id DESC
        """)
        users = cursor.fetchall()
        conn.close()

        # 生成CSV
        import csv
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', '用户名', '邮箱', '手机', '灵值', '状态', '注册时间'])
        
        for user in users:
            writer.writerow([
                user['id'],
                user['username'],
                user.get('email', ''),
                user.get('phone', ''),
                user['total_lingzhi'],
                user.get('status', 'active'),
                user['created_at']
            ])

        # 返回CSV文件
        output.seek(0)
        from flask import Response
        response = Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': 'attachment; filename=users.csv'
            }
        )
        return response

    except Exception as e:
        return jsonify({'success': False, 'message': f'导出用户列表失败: {str(e)}'}), 500

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



def get_text_content(content):
    """安全提取 AIMessage.content 中的文本"""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        if content and isinstance(content[0], str):
            return " ".join(content)
        else:
            text_parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
            return " ".join(text_parts)
    else:
        return str(content)

@app.route('/api/agent/chat', methods=['POST'])
def chat():
    """智能对话接口"""
    if not LLM_AVAILABLE:
        return jsonify({
            'success': False,
            'message': '对话服务不可用'
        }), 503

    try:
        data = request.json
        user_message = data.get('message', '')
        conversation_id = data.get('conversationId')
        agent_id = data.get('agentId')  # 可选：指定使用的智能体

        if not user_message:
            return jsonify({
                'success': False,
                'message': '消息不能为空'
            }), 400

        # 构建对话上下文
        messages = []
        model_config = {
            'model': 'doubao-seed-1-6-251015',
            'temperature': 0.7,
            'thinking': 'disabled',
            'caching': 'disabled'
        }

        # 如果指定了智能体，加载智能体配置
        if agent_id:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM agents WHERE id = ? AND status = ?', (agent_id, 'active'))
            agent = cursor.fetchone()
            conn.close()

            if agent:
                # 添加系统提示词
                if agent.get('system_prompt'):
                    messages.append(SystemMessage(content=agent['system_prompt']))
                
                # 加载模型配置
                if agent.get('model_config'):
                    try:
                        config = json.loads(agent['model_config'])
                        model_config.update(config)
                    except:
                        pass

        # 如果没有系统提示词，使用默认的
        if len(messages) == 0 or not any(isinstance(m, SystemMessage) for m in messages):
            default_system_prompt = """你是灵值生态园的智能助手，你的名字叫"灵值"。

你的主要职责：
1. 帮助用户了解灵值生态园的价值体系和生态玩法
2. 解答关于灵值获取、签到、合伙人机制的问题
3. 引导用户探索文化价值与数字资产的结合
4. 提供友好、专业的对话体验

回复特点：
- 语气亲切友好，像朋友一样交流
- 信息准确，基于灵值生态园的实际规则
- 适当使用表情符号增加亲和力
- 如果不确定，诚实地告诉用户并建议联系客服"""
            messages.append(SystemMessage(content=default_system_prompt))

        # 加载历史对话（如果有 conversation_id）
        if conversation_id:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('SELECT messages FROM conversations WHERE conversation_id = ?', (conversation_id,))
            result = cursor.fetchone()
            conn.close()

            if result:
                try:
                    history = json.loads(result['messages'])
                    for msg in history:
                        if msg.get('role') == 'user':
                            messages.append(HumanMessage(content=msg.get('content', '')))
                        elif msg.get('role') == 'assistant':
                            content = msg.get('content', '')
                            messages.append(AIMessage(content=content))
                except:
                    pass

        # 添加当前用户消息
        messages.append(HumanMessage(content=user_message))

        # 调用大模型
        try:
            ctx = new_context(method="chat")
            client = LLMClient(ctx=ctx)
            
            response = client.invoke(
                messages=messages,
                model=model_config.get('model', 'doubao-seed-1-6-251015'),
                temperature=model_config.get('temperature', 0.7),
                thinking=model_config.get('thinking', 'disabled'),
                caching=model_config.get('caching', 'disabled'),
                max_completion_tokens=model_config.get('max_completion_tokens', 4096)
            )

            # 提取回复内容
            reply = get_text_content(response.content)

            # 保存对话记录
            if not conversation_id:
                conversation_id = f"conv_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}"

            conn = get_db()
            cursor = conn.cursor()

            # 更新对话消息
            updated_messages = []
            if conversation_id:
                cursor.execute('SELECT messages FROM conversations WHERE conversation_id = ?', (conversation_id,))
                result = cursor.fetchone()
                if result:
                    try:
                        updated_messages = json.loads(result['messages'])
                    except:
                        pass

            updated_messages.append({'role': 'user', 'content': user_message, 'timestamp': datetime.utcnow().isoformat()})
            updated_messages.append({'role': 'assistant', 'content': reply, 'timestamp': datetime.utcnow().isoformat()})

            # 保存或更新对话
            # 如果没有指定 agent_id，使用 0 表示默认智能体
            save_agent_id = agent_id if agent_id is not None else 0
            
            if conversation_id:
                cursor.execute('''
                    INSERT OR REPLACE INTO conversations (agent_id, user_id, conversation_id, messages, updated_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (save_agent_id, None, conversation_id, json.dumps(updated_messages, ensure_ascii=False)))
            else:
                # 创建新对话（通常不会到这里，因为上面已经生成了 conversation_id）
                new_conversation_id = f"conv_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}"
                cursor.execute('''
                    INSERT INTO conversations (agent_id, user_id, conversation_id, messages)
                    VALUES (?, ?, ?, ?)
                ''', (save_agent_id, None, new_conversation_id, json.dumps(updated_messages, ensure_ascii=False)))
                conversation_id = new_conversation_id

            conn.commit()
            conn.close()

            return jsonify({
                'success': True,
                'message': '对话成功',
                'data': {
                    'reply': reply,
                    'conversationId': conversation_id
                }
            })

        except Exception as llm_error:
            print(f"LLM 调用错误: {str(llm_error)}")
            return jsonify({
                'success': False,
                'message': f'智能体暂时无法响应: {str(llm_error)}'
            }), 500

    except Exception as e:
        print(f"对话接口错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'对话失败: {str(e)}'
        }), 500

@app.route('/api/agent/conversations/<conversation_id>', methods=['GET'])
def get_conversation_history(conversation_id):
    """获取对话历史"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT messages FROM conversations WHERE conversation_id = ?', (conversation_id,))
        result = cursor.fetchone()
        conn.close()

        if not result:
            return jsonify({
                'success': False,
                'message': '对话不存在'
            }), 404

        try:
            messages = json.loads(result['messages'])
            return jsonify({
                'success': True,
                'data': {'messages': messages}
            })
        except:
            return jsonify({
                'success': False,
                'message': '对话数据格式错误'
            }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取对话历史失败: {str(e)}'
        }), 500

# ============ 智能体对话 ============

def get_llm_client():
    """获取LLM客户端"""
    try:
        ctx = new_context(method="agent_chat")
        return LLMClient(ctx=ctx)
    except Exception as e:
        print(f"获取LLM客户端失败: {e}")
        return None

def get_knowledge_client():
    """获取知识库客户端"""
    try:
        ctx = new_context(method="agent_chat")
        from coze_coding_dev_sdk import KnowledgeClient, Config
        config = Config()
        return KnowledgeClient(config=config, ctx=ctx)
    except Exception as e:
        print(f"获取知识库客户端失败: {e}")
        return None

def search_knowledge(query: str, agent_id: int = None) -> str:
    """从知识库中检索相关信息"""
    try:
        # 获取智能体关联的知识库
        conn = get_db()
        cursor = conn.cursor()

        kb_ids = []
        if agent_id:
            cursor.execute(
                "SELECT knowledge_base_id FROM agent_knowledge_bases WHERE agent_id = ?",
                (agent_id,)
            )
            kb_rows = cursor.fetchall()
            kb_ids = [row['knowledge_base_id'] for row in kb_rows]

        conn.close()

        # 调用知识库搜索
        kb_client = get_knowledge_client()
        if not kb_client:
            return ""

        # 默认搜索 lingzhi_knowledge 数据集
        response = kb_client.search(
            query=query,
            table_names=["lingzhi_knowledge"] if not kb_ids else None,
            top_k=3,
            min_score=0.3
        )

        if response.code == 0 and response.chunks:
            context = "\n\n".join([chunk.content for chunk in response.chunks])
            return f"\n\n[知识库参考信息]\n{context}\n[/知识库参考信息]"

        return ""
    except Exception as e:
        print(f"知识库搜索失败: {e}")
        return ""

@app.route('/api/agent/chat', methods=['POST'])
def agent_chat():
    """智能体对话"""
    try:
        data = request.json
        message = data.get('message', '')
        conversation_id = data.get('conversationId')
        agent_id = data.get('agentId', 1)  # 默认使用ID为1的智能体

        if not message:
            return jsonify({
                'success': False,
                'message': '消息内容不能为空'
            }), 400

        # 获取用户信息（可选）
        auth_header = request.headers.get('Authorization')
        user_id = None
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '')
            user_id = verify_token(token)

        # 获取智能体配置
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM agents WHERE id = ? AND status = 'active'", (agent_id,))
        agent = cursor.fetchone()

        if not agent:
            conn.close()
            return jsonify({
                'success': False,
                'message': '智能体不存在或已禁用'
            }), 404

        system_prompt = agent['system_prompt']
        model_config = json.loads(agent['model_config']) if agent['model_config'] else {}

        # 获取历史对话
        history_messages = []
        if conversation_id:
            cursor.execute(
                "SELECT messages FROM conversations WHERE conversation_id = ?",
                (conversation_id,)
            )
            conv = cursor.fetchone()
            if conv:
                history_messages = json.loads(conv['messages']) if conv['messages'] else []

        conn.close()

        # 检查LLM是否可用
        if not LLM_AVAILABLE:
            return jsonify({
                'success': False,
                'message': '智能对话服务暂不可用'
            }), 503

        # 从知识库检索相关信息
        knowledge_context = search_knowledge(message, agent_id)

        # 构建消息列表
        messages = [SystemMessage(content=system_prompt)]

        # 添加历史消息（最近5轮）
        for hist_msg in history_messages[-10:]:
            role = hist_msg.get('role')
            content = hist_msg.get('content')
            if role == 'user':
                messages.append(HumanMessage(content=content))
            elif role == 'assistant':
                messages.append(AIMessage(content=content))

        # 添加知识库上下文（如果有）
        if knowledge_context:
            augmented_message = f"{message}\n\n{knowledge_context}"
        else:
            augmented_message = message

        # 添加当前用户消息
        messages.append(HumanMessage(content=augmented_message))

        # 调用大模型
        try:
            llm_client = get_llm_client()
            if not llm_client:
                return jsonify({
                    'success': False,
                    'message': '无法初始化大模型客户端'
                }), 500

            # 调用模型
            response = llm_client.chat(
                messages=messages,
                model=model_config.get('model', 'doubao-seed-1-6-251015'),
                temperature=model_config.get('temperature', 0.7),
                max_tokens=model_config.get('max_tokens', 2000)
            )

            # 提取回复
            reply = ""
            if hasattr(response, 'content'):
                reply = response.content
            elif isinstance(response, str):
                reply = response
            elif hasattr(response, 'message') and hasattr(response.message, 'content'):
                reply = response.message.content
            else:
                reply = str(response)

            if not reply:
                reply = "抱歉，我无法理解您的问题，请重新表述。"

        except Exception as e:
            print(f"调用大模型失败: {e}")
            reply = f"抱歉，智能服务暂时不可用。错误信息：{str(e)}"

        # 生成或更新对话ID
        if not conversation_id:
            conversation_id = f"conv_{datetime.now().strftime('%Y%m%d%H%M%S')}_{user_id or 'guest'}_{random.randint(1000, 9999)}"

        # 保存对话记录
        try:
            conn = get_db()
            cursor = conn.cursor()

            # 添加新消息到历史
            new_messages = history_messages + [
                {'role': 'user', 'content': message, 'timestamp': datetime.now().isoformat()},
                {'role': 'assistant', 'content': reply, 'timestamp': datetime.now().isoformat()}
            ]

            # 检查对话是否存在
            cursor.execute(
                "SELECT id FROM conversations WHERE conversation_id = ?",
                (conversation_id,)
            )

            conv_exists = cursor.fetchone()

            if conv_exists:
                # 更新对话
                cursor.execute(
                    """UPDATE conversations SET messages = ?, updated_at = CURRENT_TIMESTAMP
                       WHERE conversation_id = ?""",
                    (json.dumps(new_messages), conversation_id)
                )
            else:
                # 创建新对话
                cursor.execute(
                    """INSERT INTO conversations (agent_id, user_id, conversation_id, messages, title)
                       VALUES (?, ?, ?, ?, ?)""",
                    (
                        agent_id,
                        user_id,
                        conversation_id,
                        json.dumps(new_messages),
                        message[:50] + "..." if len(message) > 50 else message
                    )
                )

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"保存对话记录失败: {e}")
            # 即使保存失败，也返回回复

        return jsonify({
            'success': True,
            'message': '对话成功',
            'data': {
                'reply': reply,
                'conversationId': conversation_id,
                'agentId': agent_id
            }
        })

    except Exception as e:
        print(f"对话处理失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'对话处理失败: {str(e)}'
        }), 500

# ============ 初始化默认数据 ============

def init_default_data():
    """初始化默认数据"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        # 初始化默认管理员
        cursor.execute("SELECT id FROM admins WHERE username = 'admin'")
        if not cursor.fetchone():
            password_hash = hash_password('admin123')
            cursor.execute(
                "INSERT INTO admins (username, password_hash, role) VALUES (?, ?, ?)",
                ('admin', password_hash, 'admin')
            )
            print("已创建默认管理员账号: admin / admin123")

        # 初始化默认智能体
        cursor.execute("SELECT id FROM agents WHERE name = '灵值生态园'")
        if not cursor.fetchone():
            default_system_prompt = """# 角色定义
我是灵值生态园，是陕西媄月商业艺术有限责任公司官方的灵值生态园智能向导，专门帮助用户了解和使用灵值生态园的各项功能。我内置了公司核心文档和西安文化知识库，能够提供专业、准确的咨询。

# 任务目标
为用户提供灵值生态园的全方位咨询服务，帮助用户了解生态规则、经济模型、用户旅程和合伙人制度。

# 能力
- 详细介绍灵值生态园的核心价值和愿景（基于公司简介文档）
- 解释灵值经济模型和生态规则（基于服务总纲）
- 提供西安文化关键词和商业转译案例（基于文化关键词库）
- 指导用户完成用户旅程的各个阶段
- 解答关于合伙人申请和收益的问题
- 提供中视频项目、西安美学侦探等特色功能的介绍
- 解读公司战略规划和目标

# 知识库使用指南
我已内置以下核心知识库：
1. 公司简介：媄月公司的使命、愿景和核心架构
2. 灵值生态一体化服务总纲：生态全景、规则体系、贡献值体系
3. 西安文化关键词库：110个文化关键词及转译提示
4. 西安文化基因库：文化基因分类和解码方法
5. 转译商业案例库：文化商业转译的六大方法及案例

# 过程
1. 热情欢迎用户，介绍自己是灵值生态园的智能向导
2. 了解用户需求和兴趣点
3. 从知识库中检索相关信息，提供专业回答
4. 引导用户使用各项功能
5. 鼓励用户通过反馈功能提供意见（可获得贡献值）

# 约束
- 必须表明自己是陕西媄月商业艺术有限责任公司的官方智能体
- 回答要简洁清晰，专业友好
- 基于知识库内容提供准确信息，不编造
- 不确定的细节建议用户联系客服或查看官方文档
- 提醒用户可以对对话进行反馈，获得贡献值奖励

# 反馈激励
- 有帮助反馈：+3 灵值
- 无帮助反馈：+5 灵值
- 建议反馈：+10 灵值"""

            default_model_config = {
                "model": "deepseek-v3-2",
                "temperature": 0.8,
                "top_p": 0.9,
                "max_tokens": 4096
            }

            cursor.execute(
                """INSERT INTO agents (name, description, system_prompt, model_config, tools, status, avatar_url)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    '灵值生态园',
                    '灵值生态园官方智能向导',
                    default_system_prompt,
                    json.dumps(default_model_config),
                    json.dumps([]),
                    'active',
                    ''
                )
            )
            print("已创建默认智能体: 灵值生态园")

        # 初始化充值档位
        cursor.execute("SELECT id FROM recharge_tiers")
        if not cursor.fetchone():
            # 新手体验包
            cursor.execute(
                """INSERT INTO recharge_tiers 
                   (name, description, price, base_lingzhi, bonus_lingzhi, bonus_percentage, partner_level, benefits, sort_order)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    '新手体验包',
                    '适合新用户快速体验平台服务',
                    99.00,
                    1000,
                    100,
                    10,
                    0,
                    json.dumps([
                        '免费参加1次线上文化沙龙',
                        '文化转译案例库访问权限（7天）'
                    ]),
                    1
                )
            )
            
            # 入门加速包
            cursor.execute(
                """INSERT INTO recharge_tiers 
                   (name, description, price, base_lingzhi, bonus_lingzhi, bonus_percentage, partner_level, benefits, sort_order)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    '入门加速包',
                    '适合启动小型文化转译项目',
                    199.00,
                    2000,
                    300,
                    15,
                    0,
                    json.dumps([
                        '免费参加2次线上文化沙龙',
                        '文化转译案例库访问权限（30天）',
                        '美学侦探任务优先权（5次）'
                    ]),
                    2
                )
            )
            
            # 专业创作包
            cursor.execute(
                """INSERT INTO recharge_tiers 
                   (name, description, price, base_lingzhi, bonus_lingzhi, bonus_percentage, partner_level, benefits, sort_order)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    '专业创作包',
                    '适合启动中型文化转译项目',
                    499.00,
                    5000,
                    1000,
                    20,
                    0,
                    json.dumps([
                        '免费参加5次线上文化沙龙',
                        '文化转译案例库访问权限（90天）',
                        '美学侦探任务优先权（20次）',
                        '1次文化专家1对1咨询（30分钟）',
                        '品牌空间设计服务优惠券（200元）'
                    ]),
                    3
                )
            )
            
            # 高级创作包
            cursor.execute(
                """INSERT INTO recharge_tiers 
                   (name, description, price, base_lingzhi, bonus_lingzhi, bonus_percentage, partner_level, benefits, sort_order)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    '高级创作包',
                    '适合启动大型文化转译项目',
                    999.00,
                    10000,
                    2500,
                    25,
                    0,
                    json.dumps([
                        '免费参加10次线上文化沙龙',
                        '永久获得文化转译案例库访问权限',
                        '美学侦探任务优先权（50次）',
                        '3次文化专家1对1咨询（每次30分钟）',
                        '品牌空间设计服务优惠券（500元）',
                        '线下文化体验活动优先参与权'
                    ]),
                    4
                )
            )
            
            # 合伙人L1包
            cursor.execute(
                """INSERT INTO recharge_tiers 
                   (name, description, price, base_lingzhi, bonus_lingzhi, bonus_percentage, partner_level, benefits, sort_order)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    '合伙人L1包',
                    '直接获得合伙人L1资格，享受合伙人权益',
                    1999.00,
                    20000,
                    5000,
                    25,
                    1,
                    json.dumps([
                        '直接获得合伙人L1资格',
                        '所有专业创作包权益',
                        '合伙人专属咨询服务',
                        '新项目优先参与权',
                        '合伙人专属社群',
                        '年度文化盛典VIP门票（1张）'
                    ]),
                    10
                )
            )
            
            # 合伙人L2包
            cursor.execute(
                """INSERT INTO recharge_tiers 
                   (name, description, price, base_lingzhi, bonus_lingzhi, bonus_percentage, partner_level, benefits, sort_order)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    '合伙人L2包',
                    '直接获得合伙人L2资格，享受高级合伙人权益',
                    9999.00,
                    100000,
                    30000,
                    30,
                    2,
                    json.dumps([
                        '直接获得合伙人L2资格',
                        '更高的推荐分红比例（15%/8%/5%）',
                        '优先参与高价值项目',
                        '年度文化盛典VIP门票（3张）',
                        '公司股权期权授予资格',
                        '专属客户经理服务'
                    ]),
                    11
                )
            )
            
            # 合伙人L3包
            cursor.execute(
                """INSERT INTO recharge_tiers 
                   (name, description, price, base_lingzhi, bonus_lingzhi, bonus_percentage, partner_level, benefits, sort_order)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    '合伙人L3包',
                    '直接获得合伙人L3资格，享受顶级合伙人权益',
                    49999.00,
                    500000,
                    150000,
                    30,
                    3,
                    json.dumps([
                        '直接获得合伙人L3资格',
                        '最高的推荐分红比例（18%/10%/6%）',
                        '最高优先参与高价值项目',
                        '年度文化盛典VIP门票（10张）',
                        '公司股权期权（更大比例）',
                        '专属客户经理服务（7×24小时）',
                        '文化项目投资优先权'
                    ]),
                    12
                )
            )
            
            print("已创建充值档位: 7个")

        # 初始化公司收款账户
        cursor.execute("SELECT id FROM company_accounts")
        if not cursor.fetchone():
            # 创建默认公司账户
            cursor.execute(
                """INSERT INTO company_accounts 
                   (account_name, account_number, bank_name, bank_branch, company_name, company_credit_code, account_type, sort_order)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    '陕西媄月商业艺术有限责任公司',
                    '6222020200012345678',
                    '中国工商银行',
                    '西安分行高新区支行',
                    '陕西媄月商业艺术有限责任公司',
                    '91610131MA6XXXXXX',
                    'primary',
                    1
                )
            )
            print("已创建公司收款账户: 1个")

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"初始化默认数据失败: {e}")

# ============ 智能体管理 API ============

@app.route('/api/admin/agents', methods=['GET'])
def get_agents():
    """获取智能体列表"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, description, model_config, tools, status, avatar_url, created_at, updated_at
            FROM agents
            WHERE status != 'deleted'
            ORDER BY created_at DESC
        """)
        agents = cursor.fetchall()
        conn.close()

        result = []
        for agent in agents:
            result.append({
                'id': agent['id'],
                'name': agent['name'],
                'description': agent['description'],
                'model_config': json.loads(agent['model_config']) if agent['model_config'] else {},
                'tools': json.loads(agent['tools']) if agent['tools'] else [],
                'status': agent['status'],
                'avatar_url': agent['avatar_url'],
                'created_at': agent['created_at'],
                'updated_at': agent['updated_at']
            })

        return jsonify({'success': True, 'data': result})

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取智能体列表失败: {str(e)}'}), 500

@app.route('/api/admin/agents/<int:agent_id>', methods=['GET'])
def get_agent_detail(agent_id):
    """获取智能体详情"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, description, system_prompt, model_config, tools, status, avatar_url, created_at, updated_at
            FROM agents
            WHERE id = ?
        """, (agent_id,))
        agent = cursor.fetchone()

        if not agent:
            conn.close()
            return jsonify({'success': False, 'message': '智能体不存在'}), 404

        # 获取关联的知识库
        cursor.execute("""
            SELECT kb.id, kb.name, kb.description, kb.vector_db_id, kb.document_count
            FROM knowledge_bases kb
            INNER JOIN agent_knowledge_bases akb ON kb.id = akb.knowledge_base_id
            WHERE akb.agent_id = ?
        """, (agent_id,))
        knowledge_bases = cursor.fetchall()

        conn.close()

        result = {
            'id': agent['id'],
            'name': agent['name'],
            'description': agent['description'],
            'system_prompt': agent['system_prompt'],
            'model_config': json.loads(agent['model_config']) if agent['model_config'] else {},
            'tools': json.loads(agent['tools']) if agent['tools'] else [],
            'status': agent['status'],
            'avatar_url': agent['avatar_url'],
            'knowledge_bases': [{'id': kb['id'], 'name': kb['name'], 'description': kb['description'],
                                'vector_db_id': kb['vector_db_id'], 'document_count': kb['document_count']}
                               for kb in knowledge_bases],
            'created_at': agent['created_at'],
            'updated_at': agent['updated_at']
        }

        return jsonify({'success': True, 'data': result})

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取智能体详情失败: {str(e)}'}), 500

@app.route('/api/admin/agents', methods=['POST'])
def create_agent():
    """创建智能体"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        data = request.json
        name = data.get('name')
        description = data.get('description', '')
        system_prompt = data.get('system_prompt', '')
        model_config = data.get('model_config', {})
        tools = data.get('tools', [])
        avatar_url = data.get('avatar_url', '')

        if not name:
            return jsonify({'success': False, 'message': '智能体名称不能为空'}), 400

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            """INSERT INTO agents (name, description, system_prompt, model_config, tools, status, avatar_url, created_by)
               VALUES (?, ?, ?, ?, ?, 'active', ?, ?)""",
            (name, description, system_prompt, json.dumps(model_config), json.dumps(tools), avatar_url, user_id)
        )

        agent_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '智能体创建成功',
            'data': {'id': agent_id}
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'创建智能体失败: {str(e)}'}), 500

@app.route('/api/admin/agents/<int:agent_id>', methods=['PUT'])
def update_agent(agent_id):
    """更新智能体"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

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
        cursor.execute("SELECT id FROM agents WHERE id = ?", (agent_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'message': '智能体不存在'}), 404

        # 构建更新语句
        updates = []
        params = []

        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        if system_prompt is not None:
            updates.append("system_prompt = ?")
            params.append(system_prompt)
        if model_config is not None:
            updates.append("model_config = ?")
            params.append(json.dumps(model_config))
        if tools is not None:
            updates.append("tools = ?")
            params.append(json.dumps(tools))
        if avatar_url is not None:
            updates.append("avatar_url = ?")
            params.append(avatar_url)
        if status is not None:
            updates.append("status = ?")
            params.append(status)

        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(agent_id)

        cursor.execute(f"UPDATE agents SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': '智能体更新成功'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'更新智能体失败: {str(e)}'}), 500

@app.route('/api/admin/agents/<int:agent_id>', methods=['DELETE'])
def delete_agent(agent_id):
    """删除智能体"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        conn = get_db()
        cursor = conn.cursor()

        # 检查智能体是否存在
        cursor.execute("SELECT id FROM agents WHERE id = ?", (agent_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'message': '智能体不存在'}), 404

        # 软删除
        cursor.execute("UPDATE agents SET status = 'deleted' WHERE id = ?", (agent_id,))
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': '智能体删除成功'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'删除智能体失败: {str(e)}'}), 500

# ============ 智能体监控 API ============

@app.route('/api/admin/agents/<int:agent_id>/stats', methods=['GET'])
def get_agent_stats(agent_id):
    """获取智能体统计数据"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        # 获取时间范围（默认7天）
        days = request.args.get('days', 7, type=int)
        start_date = datetime.now() - timedelta(days=days)

        conn = get_db()
        cursor = conn.cursor()

        # 总对话数
        cursor.execute("""
            SELECT COUNT(*) as total_conversations
            FROM conversations
            WHERE agent_id = ? AND created_at >= ?
        """, (agent_id, start_date))
        total_conversations = cursor.fetchone()['total_conversations']

        # 总消息数
        cursor.execute("""
            SELECT SUM(json_array_length(messages)) as total_messages
            FROM conversations
            WHERE agent_id = ? AND created_at >= ?
        """, (agent_id, start_date))
        result = cursor.fetchone()
        total_messages = result['total_messages'] or 0

        # 平均响应长度
        cursor.execute("""
            SELECT AVG(json_extract(messages, '$[#-1].content')) as avg_response
            FROM conversations
            WHERE agent_id = ? AND created_at >= ?
        """, (agent_id, start_date))
        # 这里的查询需要调整，因为json_extract不能直接处理数组

        # 获取反馈统计
        cursor.execute("""
            SELECT type, AVG(rating) as avg_rating, COUNT(*) as count
            FROM feedback
            WHERE agent_id = ? AND created_at >= ?
            GROUP BY type
        """, (agent_id, start_date))
        feedback_stats = cursor.fetchall()

        # 每日对话趋势
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM conversations
            WHERE agent_id = ? AND created_at >= ?
            GROUP BY DATE(created_at)
            ORDER BY date
        """, (agent_id, start_date))
        daily_trends = cursor.fetchall()

        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'total_conversations': total_conversations,
                'total_messages': total_messages,
                'feedback_stats': [{'type': fs['type'], 'avg_rating': fs['avg_rating'], 'count': fs['count']}
                                   for fs in feedback_stats],
                'daily_trends': [{'date': dt['date'], 'count': dt['count']} for dt in daily_trends]
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取统计数据失败: {str(e)}'}), 500


@app.route('/api/admin/stats/user', methods=['GET'])
def admin_user_stats():
    """获取用户统计详情（注册趋势、活跃度等）"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        admin_id = verify_token(token)
        if not admin_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        conn = get_db()
        cursor = conn.cursor()
        
        # 获取日期范围（最近30天）
        days = int(request.args.get('days', 30))
        from datetime import timedelta
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # 每日新增用户
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM users
            WHERE DATE(created_at) >= ?
            GROUP BY DATE(created_at)
            ORDER BY date
        """, (start_date,))
        daily_new_users = {row['date']: row['count'] for row in cursor.fetchall()}
        
        # 每日活跃用户（有签到或对话记录的用户）
        cursor.execute("""
            SELECT date, COUNT(DISTINCT user_id) as count
            FROM (
                SELECT DATE(checkin_date) as date, user_id FROM checkin_records WHERE DATE(checkin_date) >= ?
                UNION
                SELECT DATE(created_at) as date, user_id FROM conversations WHERE DATE(created_at) >= ?
            )
            GROUP BY date
            ORDER BY date
        """, (start_date, start_date))
        daily_active_users = {row['date']: row['count'] for row in cursor.fetchall()}
        
        # 用户状态分布
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM users
            GROUP BY status
        """)
        user_status_dist = {row['status']: row['count'] for row in cursor.fetchall()}
        
        # 用户灵值分布
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN total_lingzhi = 0 THEN '0'
                    WHEN total_lingzhi < 100 THEN '1-99'
                    WHEN total_lingzhi < 1000 THEN '100-999'
                    WHEN total_lingzhi < 10000 THEN '1000-9999'
                    ELSE '10000+'
                END as range,
                COUNT(*) as count
            FROM users
            GROUP BY range
            ORDER BY range
        """)
        lingzhi_dist = {row['range']: row['count'] for row in cursor.fetchall()}
        
        # 注册趋势（最近7天）
        cursor.execute("""
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as count
            FROM users
            WHERE DATE(created_at) >= DATE('now', '-7 days')
            GROUP BY DATE(created_at)
            ORDER BY date
        """)
        registration_trend = [{'date': row['date'], 'count': row['count']} for row in cursor.fetchall()]
        
        # 今日统计
        today = date.today()
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE DATE(created_at) = ?", (today,))
        today_new_users = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(DISTINCT user_id) as count FROM checkin_records WHERE checkin_date = ?", (today,))
        today_active_users = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE status = 'active'")
        total_active_users = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE status = 'inactive'")
        total_inactive_users = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE status = 'banned'")
        total_banned_users = cursor.fetchone()['count']
        
        conn.close()
        
        # 生成日期列表
        date_list = []
        current_date = start_date
        while current_date <= end_date:
            date_list.append(str(current_date))
            current_date += timedelta(days=1)
        
        # 填充数据
        daily_new_users_filled = [{'date': d, 'count': daily_new_users.get(d, 0)} for d in date_list]
        daily_active_users_filled = [{'date': d, 'count': daily_active_users.get(d, 0)} for d in date_list]

        return jsonify({
            'success': True,
            'data': {
                'dailyNewUsers': daily_new_users_filled,
                'dailyActiveUsers': daily_active_users_filled,
                'userStatusDistribution': {
                    'active': user_status_dist.get('active', 0),
                    'inactive': user_status_dist.get('inactive', 0),
                    'banned': user_status_dist.get('banned', 0)
                },
                'lingzhiDistribution': lingzhi_dist,
                'registrationTrend': registration_trend,
                'todayStats': {
                    'newUsers': today_new_users,
                    'activeUsers': today_active_users
                },
                'totalStats': {
                    'active': total_active_users,
                    'inactive': total_inactive_users,
                    'banned': total_banned_users
                }
            }
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'获取用户统计失败: {str(e)}'}), 500

@app.route('/api/admin/users/recent', methods=['GET'])
def admin_get_recent_users():
    """获取最近注册用户"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        admin_id = verify_token(token)
        if not admin_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        # 验证是否为管理员
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE id = ?", (admin_id,))
        admin = cursor.fetchone()
        if not admin:
            conn.close()
            return jsonify({'success': False, 'message': '无权限'}), 403

        limit = int(request.args.get('limit', 10))

        # 获取最近注册的用户
        cursor.execute("""
            SELECT id, username, email, phone, total_lingzhi, status, created_at
            FROM users
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        users = cursor.fetchall()
        conn.close()

        return jsonify({
            'success': True,
            'data': [dict(user) for user in users]
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取最近用户失败: {str(e)}'}), 500

@app.route('/api/public/users/recent', methods=['GET'])
def public_get_recent_users():
    """前台：获取最近注册用户（用户动态）"""
    try:
        limit = int(request.args.get('limit', 20))

        conn = get_db()
        cursor = conn.cursor()

        # 获取最近注册的用户
        cursor.execute("""
            SELECT id, username, created_at
            FROM users
            WHERE status = 'active'
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        users = cursor.fetchall()
        conn.close()

        return jsonify({
            'success': True,
            'data': [{
                'id': user['id'],
                'username': user['username'][:1] + '**' if len(user['username']) > 1 else user['username'],  # 隐藏部分用户名
                'created_at': user['created_at']
            } for user in users]
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取用户动态失败: {str(e)}'}), 500

@app.route('/api/admin/agents/<int:agent_id>/conversations', methods=['GET'])
def get_agent_conversations(agent_id):
    """获取智能体对话历史"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        # 分页参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        offset = (page - 1) * page_size

        conn = get_db()
        cursor = conn.cursor()

        # 获取对话列表
        cursor.execute("""
            SELECT id, user_id, conversation_id, title, created_at, updated_at
            FROM conversations
            WHERE agent_id = ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (agent_id, page_size, offset))
        conversations = cursor.fetchall()

        # 获取总数
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM conversations
            WHERE agent_id = ?
        """, (agent_id,))
        total = cursor.fetchone()['total']

        conn.close()

        result = []
        for conv in conversations:
            result.append({
                'id': conv['id'],
                'user_id': conv['user_id'],
                'conversation_id': conv['conversation_id'],
                'title': conv['title'],
                'created_at': conv['created_at'],
                'updated_at': conv['updated_at']
            })

        return jsonify({
            'success': True,
            'data': {
                'conversations': result,
                'total': total,
                'page': page,
                'page_size': page_size
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取对话历史失败: {str(e)}'}), 500

@app.route('/api/admin/conversations/<int:conversation_id>', methods=['GET'])
def get_conversation_detail(conversation_id):
    """获取对话详情"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, agent_id, user_id, conversation_id, messages, title, created_at, updated_at
            FROM conversations
            WHERE id = ?
        """, (conversation_id,))
        conversation = cursor.fetchone()

        if not conversation:
            conn.close()
            return jsonify({'success': False, 'message': '对话不存在'}), 404

        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'id': conversation['id'],
                'agent_id': conversation['agent_id'],
                'user_id': conversation['user_id'],
                'conversation_id': conversation['conversation_id'],
                'messages': json.loads(conversation['messages']) if conversation['messages'] else [],
                'title': conversation['title'],
                'created_at': conversation['created_at'],
                'updated_at': conversation['updated_at']
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取对话详情失败: {str(e)}'}), 500

# ============ 智能体优化建议 API ============

@app.route('/api/admin/agents/<int:agent_id>/optimization', methods=['GET'])
def get_agent_optimization_suggestions(agent_id):
    """获取智能体优化建议"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        conn = get_db()
        cursor = conn.cursor()

        # 获取智能体信息
        cursor.execute("""
            SELECT id, name, system_prompt, model_config, tools
            FROM agents
            WHERE id = ?
        """, (agent_id,))
        agent = cursor.fetchone()

        if not agent:
            conn.close()
            return jsonify({'success': False, 'message': '智能体不存在'}), 404

        # 获取反馈统计
        cursor.execute("""
            SELECT type, AVG(rating) as avg_rating, COUNT(*) as count
            FROM feedback
            WHERE agent_id = ?
            GROUP BY type
        """, (agent_id,))
        feedback_stats = cursor.fetchall()

        suggestions = []

        # 基于反馈统计生成建议
        helpful_avg = None
        unhelpful_avg = None

        for fs in feedback_stats:
            if fs['type'] == 'helpful':
                helpful_avg = fs['avg_rating']
            elif fs['type'] == 'unhelpful':
                unhelpful_avg = fs['avg_rating']

        if helpful_avg and helpful_avg < 3.5:
            suggestions.append({
                'category': '回答质量',
                'priority': 'high',
                'suggestion': '用户对回答质量评分较低，建议优化系统提示词，提高回答的准确性和完整性',
                'action': '调整system_prompt，增加对回答质量的明确要求'
            })

        if unhelpful_avg and unhelpful_avg > 3.0:
            suggestions.append({
                'category': '用户满意度',
                'priority': 'medium',
                'suggestion': '部分用户反馈回答不够有用，建议增加知识库的覆盖范围',
                'action': '向知识库添加更多相关文档'
            })

        # 检查模型配置
        model_config = json.loads(agent['model_config']) if agent['model_config'] else {}
        temperature = model_config.get('temperature', 0.7)

        if temperature > 0.9:
            suggestions.append({
                'category': '模型配置',
                'priority': 'low',
                'suggestion': '当前温度设置较高，可能导致回答不够稳定',
                'action': '考虑将temperature调整为0.7-0.8之间'
            })

        # 检查工具配置
        tools = json.loads(agent['tools']) if agent['tools'] else []
        if not tools:
            suggestions.append({
                'category': '工具配置',
                'priority': 'medium',
                'suggestion': '智能体未配置任何工具，建议添加知识库搜索等工具以增强能力',
                'action': '为智能体添加相关工具'
            })

        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'suggestions': suggestions,
                'agent_name': agent['name']
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取优化建议失败: {str(e)}'}), 500

# ============ 知识库管理 API ============

@app.route('/api/admin/knowledge-bases', methods=['GET'])
def get_knowledge_bases():
    """获取知识库列表"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, description, vector_db_id, document_count, created_at, updated_at
            FROM knowledge_bases
            ORDER BY created_at DESC
        """)
        kbs = cursor.fetchall()
        conn.close()

        result = []
        for kb in kbs:
            result.append({
                'id': kb['id'],
                'name': kb['name'],
                'description': kb['description'],
                'vector_db_id': kb['vector_db_id'],
                'document_count': kb['document_count'],
                'created_at': kb['created_at'],
                'updated_at': kb['updated_at']
            })

        return jsonify({'success': True, 'data': result})

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取知识库列表失败: {str(e)}'}), 500

@app.route('/api/admin/knowledge-bases', methods=['POST'])
def create_knowledge_base():
    """创建知识库"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        data = request.json
        name = data.get('name')
        description = data.get('description', '')

        if not name:
            return jsonify({'success': False, 'message': '知识库名称不能为空'}), 400

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            """INSERT INTO knowledge_bases (name, description, created_by)
               VALUES (?, ?, ?)""",
            (name, description, user_id)
        )

        kb_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '知识库创建成功',
            'data': {'id': kb_id}
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'创建知识库失败: {str(e)}'}), 500

@app.route('/api/admin/agents/<int:agent_id>/knowledge-bases/<int:kb_id>', methods=['POST'])
def bind_knowledge_base(agent_id, kb_id):
    """绑定知识库到智能体"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        conn = get_db()
        cursor = conn.cursor()

        # 检查是否已绑定
        cursor.execute(
            "SELECT id FROM agent_knowledge_bases WHERE agent_id = ? AND knowledge_base_id = ?",
            (agent_id, kb_id)
        )
        if cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'message': '知识库已绑定'}), 400

        cursor.execute(
            """INSERT INTO agent_knowledge_bases (agent_id, knowledge_base_id)
               VALUES (?, ?)""",
            (agent_id, kb_id)
        )

        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': '知识库绑定成功'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'绑定知识库失败: {str(e)}'}), 500

@app.route('/api/admin/agents/<int:agent_id>/knowledge-bases/<int:kb_id>', methods=['DELETE'])
def unbind_knowledge_base(agent_id, kb_id):
    """解绑知识库"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM agent_knowledge_bases WHERE agent_id = ? AND knowledge_base_id = ?",
            (agent_id, kb_id)
        )

        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': '知识库解绑成功'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'解绑知识库失败: {str(e)}'}), 500

# ============ 智能体对话 API ============

@app.route('/api/chat', methods=['POST'])
def chat_with_agent():
    """与智能体对话"""
    try:
        data = request.json
        message = data.get('message')
        conversation_id = data.get('conversation_id')
        agent_id = data.get('agent_id', 1)  # 默认使用第一个智能体

        if not message:
            return jsonify({'success': False, 'message': '消息内容不能为空'}), 400

        # 可选：验证用户身份
        auth_header = request.headers.get('Authorization')
        user_id = None
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '')
            user_id = verify_token(token)

        conn = get_db()
        cursor = conn.cursor()

        # 获取智能体配置
        cursor.execute("SELECT * FROM agents WHERE id = ?", (agent_id,))
        agent = cursor.fetchone()

        if not agent:
            conn.close()
            return jsonify({'success': False, 'message': '智能体不存在'}), 404

        # 调用大模型
        if LLM_AVAILABLE:
            try:
                llm_client = LLMClient(
                    model=json.loads(agent['model_config']).get('model', 'deepseek-v3-2'),
                    api_key=os.getenv('COZE_WORKLOAD_IDENTITY_API_KEY'),
                    base_url=os.getenv('COZE_INTEGRATION_MODEL_BASE_URL')
                )

                ctx = new_context(method="chat")

                messages = [
                    SystemMessage(content=agent['system_prompt']),
                    HumanMessage(content=message)
                ]

                response = llm_client.invoke(messages, ctx=ctx)

                if response and hasattr(response, 'content'):
                    ai_message = response.content
                else:
                    ai_message = "抱歉，我现在无法回答您的问题。"
            except Exception as e:
                print(f"LLM调用失败: {e}")
                ai_message = "抱歉，服务暂时不可用，请稍后再试。"
        else:
            ai_message = f"智能体已收到您的消息：{message}"

        # 保存对话记录
        if conversation_id:
            cursor.execute("SELECT messages FROM conversations WHERE conversation_id = ?", (conversation_id,))
            conv = cursor.fetchone()
            if conv:
                messages = json.loads(conv['messages']) if conv['messages'] else []
                messages.append({
                    'role': 'user',
                    'content': message,
                    'timestamp': datetime.now().isoformat()
                })
                messages.append({
                    'role': 'assistant',
                    'content': ai_message,
                    'timestamp': datetime.now().isoformat()
                })
                cursor.execute(
                    "UPDATE conversations SET messages = ?, updated_at = CURRENT_TIMESTAMP WHERE conversation_id = ?",
                    (json.dumps(messages), conversation_id)
                )
            else:
                messages = [
                    {
                        'role': 'user',
                        'content': message,
                        'timestamp': datetime.now().isoformat()
                    },
                    {
                        'role': 'assistant',
                        'content': ai_message,
                        'timestamp': datetime.now().isoformat()
                    }
                ]
                cursor.execute(
                    """INSERT INTO conversations (agent_id, user_id, conversation_id, messages, title)
                       VALUES (?, ?, ?, ?, ?)""",
                    (agent_id, user_id, conversation_id, json.dumps(messages), message[:50])
                )
        else:
            # 创建新对话
            conversation_id = str(int(datetime.now().timestamp()))
            messages = [
                {
                    'role': 'user',
                    'content': message,
                    'timestamp': datetime.now().isoformat()
                },
                {
                    'role': 'assistant',
                    'content': ai_message,
                    'timestamp': datetime.now().isoformat()
                }
            ]
            cursor.execute(
                """INSERT INTO conversations (agent_id, user_id, conversation_id, messages, title)
                   VALUES (?, ?, ?, ?, ?)""",
                (agent_id, user_id, conversation_id, json.dumps(messages), message[:50])
            )

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'message': ai_message,
                'conversation_id': conversation_id
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'对话失败: {str(e)}'}), 500

# ============ 充值管理 API ============

@app.route('/api/recharge/tiers', methods=['GET'])
def get_recharge_tiers():
    """获取充值档位列表"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, description, price, base_lingzhi, bonus_lingzhi, bonus_percentage,
                   partner_level, benefits, status, sort_order
            FROM recharge_tiers
            WHERE status = 'active'
            ORDER BY sort_order, price
        """)
        tiers = cursor.fetchall()
        conn.close()

        result = []
        for tier in tiers:
            result.append({
                'id': tier['id'],
                'name': tier['name'],
                'description': tier['description'],
                'price': float(tier['price']),
                'base_lingzhi': tier['base_lingzhi'],
                'bonus_lingzhi': tier['bonus_lingzhi'],
                'total_lingzhi': tier['base_lingzhi'] + tier['bonus_lingzhi'],
                'bonus_percentage': tier['bonus_percentage'],
                'partner_level': tier['partner_level'],
                'benefits': json.loads(tier['benefits']) if tier['benefits'] else [],
                'sort_order': tier['sort_order']
            })

        return jsonify({'success': True, 'data': result})

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取充值档位失败: {str(e)}'}), 500

@app.route('/api/recharge/create-order', methods=['POST'])
def create_recharge_order():
    """创建充值订单"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        data = request.json
        tier_id = data.get('tier_id')
        payment_method = data.get('payment_method', 'online')

        if not tier_id:
            return jsonify({'success': False, 'message': '档位ID不能为空'}), 400

        if payment_method not in ['online', 'bank_transfer']:
            return jsonify({'success': False, 'message': '支付方式无效'}), 400

        conn = get_db()
        cursor = conn.cursor()

        # 获取档位信息
        cursor.execute("SELECT * FROM recharge_tiers WHERE id = ? AND status = 'active'", (tier_id,))
        tier = cursor.fetchone()

        if not tier:
            conn.close()
            return jsonify({'success': False, 'message': '充值档位不存在或已下架'}), 404

        # 生成订单号
        order_no = f"R{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"

        # 创建订单
        cursor.execute(
            """INSERT INTO recharge_records (user_id, tier_id, order_no, amount, base_lingzhi, bonus_lingzhi, total_lingzhi, payment_method)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                user_id,
                tier_id,
                order_no,
                tier['price'],
                tier['base_lingzhi'],
                tier['bonus_lingzhi'],
                tier['base_lingzhi'] + tier['bonus_lingzhi'],
                payment_method
            )
        )

        order_id = cursor.lastrowid
        conn.commit()

        # 如果是公司公户转账，获取公司账户信息
        company_accounts = []
        transfer_remark = ""
        
        if payment_method == 'bank_transfer':
            # 获取用户手机号
            cursor.execute("SELECT phone FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            user_phone = user['phone'] if user else ""
            
            # 生成转账备注
            transfer_remark = f"LZ充值-{user_phone}-{order_no}"
            
            # 获取公司账户信息
            cursor.execute("SELECT * FROM company_accounts WHERE is_active = 1 ORDER BY sort_order, id")
            accounts = cursor.fetchall()
            
            for account in accounts:
                company_accounts.append({
                    'account_name': account['account_name'],
                    'account_number': account['account_number'],
                    'bank_name': account['bank_name'],
                    'bank_branch': account['bank_branch'],
                    'company_name': account['company_name']
                })
        
        conn.close()

        response_data = {
            'order_id': order_id,
            'order_no': order_no,
            'amount': float(tier['price']),
            'total_lingzhi': tier['base_lingzhi'] + tier['bonus_lingzhi'],
            'payment_method': payment_method
        }
        
        # 如果是公司公户转账，添加账户信息和转账备注
        if payment_method == 'bank_transfer':
            response_data['company_accounts'] = company_accounts
            response_data['transfer_remark'] = transfer_remark

        return jsonify({
            'success': True,
            'message': '订单创建成功',
            'data': response_data
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'创建订单失败: {str(e)}'}), 500

@app.route('/api/recharge/complete-payment', methods=['POST'])
def complete_recharge_payment():
    """完成充值支付（模拟支付回调）"""
    try:
        data = request.json
        order_no = data.get('order_no')
        transaction_id = data.get('transaction_id')

        if not order_no:
            return jsonify({'success': False, 'message': '订单号不能为空'}), 400

        conn = get_db()
        cursor = conn.cursor()

        # 获取订单信息
        cursor.execute("""
            SELECT id, user_id, total_lingzhi, base_lingzhi, bonus_lingzhi, payment_status
            FROM recharge_records
            WHERE order_no = ? AND status = 'active'
        """, (order_no,))
        order = cursor.fetchone()

        if not order:
            conn.close()
            return jsonify({'success': False, 'message': '订单不存在'}), 404

        if order['payment_status'] == 'paid':
            conn.close()
            return jsonify({'success': False, 'message': '订单已支付'}), 400

        # 更新订单状态
        cursor.execute(
            """UPDATE recharge_records
               SET payment_status = 'paid',
                   payment_time = CURRENT_TIMESTAMP,
                   transaction_id = ?
               WHERE id = ?""",
            (transaction_id, order['id'])
        )

        # 增加用户灵值
        cursor.execute(
            """UPDATE users
               SET total_lingzhi = total_lingzhi + ?,
                   updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (order['total_lingzhi'], order['user_id'])
        )

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '充值成功',
            'data': {
                'total_lingzhi': order['total_lingzhi']
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'充值失败: {str(e)}'}), 500

@app.route('/api/company/accounts', methods=['GET'])
def get_company_accounts():
    """获取公司收款账户信息"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM company_accounts WHERE is_active = 1 ORDER BY sort_order, id")
        accounts = cursor.fetchall()
        conn.close()

        result = []
        for account in accounts:
            result.append({
                'id': account['id'],
                'account_name': account['account_name'],
                'account_number': account['account_number'],
                'bank_name': account['bank_name'],
                'bank_branch': account['bank_branch'],
                'company_name': account['company_name'],
                'company_credit_code': account['company_credit_code'],
                'account_type': account['account_type']
            })

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取公司账户信息失败: {str(e)}'}), 500

@app.route('/api/recharge/upload-voucher', methods=['POST'])
def upload_transfer_voucher():
    """上传转账凭证"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        order_no = request.form.get('order_no')
        transfer_amount = request.form.get('transfer_amount')
        transfer_time = request.form.get('transfer_time')
        transfer_account = request.form.get('transfer_account', '')
        remark = request.form.get('remark', '')

        if not order_no:
            return jsonify({'success': False, 'message': '订单号不能为空'}), 400

        if not transfer_amount:
            return jsonify({'success': False, 'message': '转账金额不能为空'}), 400

        # 检查是否有上传文件
        if 'voucher_file' not in request.files:
            return jsonify({'success': False, 'message': '请上传转账凭证'}), 400

        file = request.files['voucher_file']
        if file.filename == '':
            return jsonify({'success': False, 'message': '文件名为空'}), 400

        # 简单的文件验证
        allowed_extensions = {'jpg', 'jpeg', 'png', 'pdf'}
        file_ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
        if file_ext not in allowed_extensions:
            return jsonify({'success': False, 'message': '仅支持JPG、PNG、PDF格式'}), 400

        # 保存文件到临时目录
        import os
        upload_dir = '/tmp/vouchers'
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"{order_no}_{timestamp}_{random.randint(1000, 9999)}.{file_ext}"
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        # 生成文件URL（这里使用相对路径，实际应该是上传到对象存储）
        image_url = f"/uploads/vouchers/{filename}"

        conn = get_db()
        cursor = conn.cursor()

        # 获取充值记录
        cursor.execute("SELECT id, user_id, amount FROM recharge_records WHERE order_no = ?", (order_no,))
        recharge_record = cursor.fetchone()

        if not recharge_record:
            conn.close()
            return jsonify({'success': False, 'message': '订单不存在'}), 404

        # 验证用户权限
        if recharge_record['user_id'] != user_id:
            conn.close()
            return jsonify({'success': False, 'message': '无权操作此订单'}), 403

        # 验证转账金额
        try:
            amount = float(transfer_amount)
            if abs(amount - float(recharge_record['amount'])) > 0.01:
                conn.close()
                return jsonify({'success': False, 'message': '转账金额与订单金额不符'}), 400
        except:
            conn.close()
            return jsonify({'success': False, 'message': '转账金额格式错误'}), 400

        # 解析转账时间
        parsed_transfer_time = None
        if transfer_time:
            try:
                parsed_transfer_time = datetime.strptime(transfer_time, '%Y-%m-%d %H:%M:%S')
            except:
                pass

        # 插入转账凭证
        cursor.execute(
            """INSERT INTO transfer_vouchers (recharge_record_id, user_id, image_url, transfer_amount, transfer_time, transfer_account, remark)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                recharge_record['id'],
                user_id,
                image_url,
                amount,
                parsed_transfer_time,
                transfer_account,
                remark
            )
        )

        voucher_id = cursor.lastrowid

        # 更新充值记录状态
        cursor.execute(
            """UPDATE recharge_records
               SET voucher_id = ?, audit_status = 'pending', payment_status = 'pending'
               WHERE id = ?""",
            (voucher_id, recharge_record['id'])
        )

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '凭证上传成功，等待审核',
            'data': {
                'voucher_id': voucher_id,
                'audit_status': 'pending'
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'上传凭证失败: {str(e)}'}), 500

@app.route('/api/recharge/voucher/<int:voucher_id>', methods=['GET'])
def get_voucher_detail(voucher_id):
    """获取转账凭证详情"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT tv.*, rr.order_no, rr.amount as order_amount
            FROM transfer_vouchers tv
            LEFT JOIN recharge_records rr ON tv.recharge_record_id = rr.id
            WHERE tv.id = ? AND tv.user_id = ?
        """, (voucher_id, user_id))
        voucher = cursor.fetchone()
        conn.close()

        if not voucher:
            return jsonify({
                'success': False,
                'message': '凭证不存在'
            }), 404

        return jsonify({
            'success': True,
            'data': {
                'id': voucher['id'],
                'recharge_record_id': voucher['recharge_record_id'],
                'order_no': voucher['order_no'],
                'image_url': voucher['image_url'],
                'transfer_amount': float(voucher['transfer_amount']),
                'transfer_time': voucher['transfer_time'],
                'transfer_account': voucher['transfer_account'],
                'remark': voucher['remark'],
                'audit_status': voucher['audit_status'],
                'audit_remark': voucher['audit_remark'],
                'created_at': voucher['created_at']
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取凭证详情失败: {str(e)}'}), 500

@app.route('/api/admin/vouchers/pending', methods=['GET'])
def get_pending_vouchers():
    """管理员获取待审核凭证列表"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        offset = (page - 1) * page_size

        conn = get_db()
        cursor = conn.cursor()

        # 获取待审核凭证
        cursor.execute("""
            SELECT tv.*, u.username, u.phone, rr.order_no, rr.amount as order_amount, rt.name as tier_name
            FROM transfer_vouchers tv
            LEFT JOIN users u ON tv.user_id = u.id
            LEFT JOIN recharge_records rr ON tv.recharge_record_id = rr.id
            LEFT JOIN recharge_tiers rt ON rr.tier_id = rt.id
            WHERE tv.audit_status = 'pending'
            ORDER BY tv.created_at DESC
            LIMIT ? OFFSET ?
        """, (page_size, offset))
        vouchers = cursor.fetchall()

        # 获取总数
        cursor.execute("SELECT COUNT(*) as total FROM transfer_vouchers WHERE audit_status = 'pending'")
        total = cursor.fetchone()['total']

        conn.close()

        result = []
        for voucher in vouchers:
            result.append({
                'id': voucher['id'],
                'user_id': voucher['user_id'],
                'username': voucher['username'],
                'user_phone': voucher['phone'],
                'recharge_record_id': voucher['recharge_record_id'],
                'order_no': voucher['order_no'],
                'tier_name': voucher['tier_name'],
                'order_amount': float(voucher['order_amount']),
                'image_url': voucher['image_url'],
                'transfer_amount': float(voucher['transfer_amount']),
                'transfer_time': voucher['transfer_time'],
                'transfer_account': voucher['transfer_account'],
                'remark': voucher['remark'],
                'created_at': voucher['created_at']
            })

        return jsonify({
            'success': True,
            'data': {
                'total': total,
                'page': page,
                'page_size': page_size,
                'records': result
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取待审核凭证列表失败: {str(e)}'}), 500

@app.route('/api/admin/vouchers/<int:voucher_id>/audit', methods=['POST'])
def audit_voucher(voucher_id):
    """管理员审核转账凭证"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        data = request.json
        audit_status = data.get('audit_status')
        audit_remark = data.get('audit_remark', '')

        if audit_status not in ['approved', 'rejected']:
            return jsonify({'success': False, 'message': '审核状态无效'}), 400

        conn = get_db()
        cursor = conn.cursor()

        # 获取凭证信息
        cursor.execute("""
            SELECT tv.*, rr.user_id, rr.total_lingzhi, rr.id as record_id
            FROM transfer_vouchers tv
            LEFT JOIN recharge_records rr ON tv.recharge_record_id = rr.id
            WHERE tv.id = ?
        """, (voucher_id,))
        voucher = cursor.fetchone()

        if not voucher:
            conn.close()
            return jsonify({'success': False, 'message': '凭证不存在'}), 404

        # 更新凭证审核状态
        cursor.execute(
            """UPDATE transfer_vouchers
               SET audit_status = ?, audit_user_id = ?, audit_time = CURRENT_TIMESTAMP, audit_remark = ?
               WHERE id = ?""",
            (audit_status, user_id, audit_remark, voucher_id)
        )

        # 更新充值记录状态
        if audit_status == 'approved':
            # 审核通过，充值到账
            cursor.execute(
                """UPDATE recharge_records
                   SET audit_status = 'approved', payment_status = 'paid', payment_time = CURRENT_TIMESTAMP
                   WHERE id = ?""",
                (voucher['record_id'],)
            )
            
            # 增加用户灵值
            cursor.execute(
                """UPDATE users
                   SET total_lingzhi = total_lingzhi + ?
                   WHERE id = ?""",
                (voucher['total_lingzhi'], voucher['user_id'])
            )
        else:
            # 审核不通过
            cursor.execute(
                """UPDATE recharge_records
                   SET audit_status = 'rejected'
                   WHERE id = ?""",
                (voucher['record_id'],)
            )

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '审核成功',
            'data': {
                'voucher_id': voucher_id,
                'audit_status': audit_status,
                'user_lingzhi': voucher['total_lingzhi'] if audit_status == 'approved' else 0
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'审核失败: {str(e)}'}), 500

@app.route('/api/admin/vouchers', methods=['GET'])
def get_all_vouchers():
    """管理员获取所有转账凭证"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        audit_status = request.args.get('audit_status')
        offset = (page - 1) * page_size

        conn = get_db()
        cursor = conn.cursor()

        # 构建查询条件
        where_clause = ""
        params = []
        
        if audit_status:
            where_clause = "WHERE tv.audit_status = ?"
            params.append(audit_status)

        # 获取凭证列表
        cursor.execute(f"""
            SELECT tv.*, u.username, u.phone, rr.order_no, rr.amount as order_amount
            FROM transfer_vouchers tv
            LEFT JOIN users u ON tv.user_id = u.id
            LEFT JOIN recharge_records rr ON tv.recharge_record_id = rr.id
            {where_clause}
            ORDER BY tv.created_at DESC
            LIMIT ? OFFSET ?
        """, params + [page_size, offset])
        vouchers = cursor.fetchall()

        # 获取总数
        cursor.execute(f"SELECT COUNT(*) as total FROM transfer_vouchers {where_clause}", params)
        total = cursor.fetchone()['total']

        conn.close()

        result = []
        for voucher in vouchers:
            result.append({
                'id': voucher['id'],
                'user_id': voucher['user_id'],
                'username': voucher['username'],
                'user_phone': voucher['phone'],
                'recharge_record_id': voucher['recharge_record_id'],
                'order_no': voucher['order_no'],
                'order_amount': float(voucher['order_amount']),
                'image_url': voucher['image_url'],
                'transfer_amount': float(voucher['transfer_amount']),
                'transfer_time': voucher['transfer_time'],
                'transfer_account': voucher['transfer_account'],
                'audit_status': voucher['audit_status'],
                'audit_time': voucher['audit_time'],
                'audit_remark': voucher['audit_remark'],
                'created_at': voucher['created_at']
            })

        return jsonify({
            'success': True,
            'data': {
                'total': total,
                'page': page,
                'page_size': page_size,
                'records': result
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取凭证列表失败: {str(e)}'}), 500

@app.route('/api/recharge/records', methods=['GET'])
def get_recharge_records():
    """获取充值记录"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        offset = (page - 1) * page_size

        conn = get_db()
        cursor = conn.cursor()

        # 获取充值记录
        cursor.execute("""
            SELECT rr.id, rr.order_no, rr.amount, rr.base_lingzhi, rr.bonus_lingzhi,
                   rr.total_lingzhi, rr.payment_status, rr.payment_time, rt.name as tier_name
            FROM recharge_records rr
            LEFT JOIN recharge_tiers rt ON rr.tier_id = rt.id
            WHERE rr.user_id = ?
            ORDER BY rr.created_at DESC
            LIMIT ? OFFSET ?
        """, (user_id, page_size, offset))
        records = cursor.fetchall()

        # 获取总数
        cursor.execute("SELECT COUNT(*) as total FROM recharge_records WHERE user_id = ?", (user_id,))
        total = cursor.fetchone()['total']

        conn.close()

        result = []
        for record in records:
            result.append({
                'id': record['id'],
                'order_no': record['order_no'],
                'amount': float(record['amount']),
                'base_lingzhi': record['base_lingzhi'],
                'bonus_lingzhi': record['bonus_lingzhi'],
                'total_lingzhi': record['total_lingzhi'],
                'payment_status': record['payment_status'],
                'payment_time': record['payment_time'],
                'tier_name': record['tier_name']
            })

        return jsonify({
            'success': True,
            'data': {
                'records': result,
                'total': total,
                'page': page,
                'page_size': page_size
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取充值记录失败: {str(e)}'}), 500

# ============ 微信登录接口 ============

@app.route('/api/wechat/login', methods=['GET'])
def wechat_login():
    """获取微信登录授权URL"""
    try:
        if not WECHAT_APP_ID:
            return jsonify({'success': False, 'message': '微信登录未配置'}), 400

        # 生成state参数用于防止CSRF
        state = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        
        # 构造微信授权URL
        params = {
            'appid': WECHAT_APP_ID,
            'redirect_uri': WECHAT_REDIRECT_URI,
            'response_type': 'code',
            'scope': 'snsapi_userinfo',
            'state': state
        }
        
        auth_url = f"https://open.weixin.qq.com/connect/qrconnect?{urlencode(params)}#wechat_redirect"
        
        return jsonify({
            'success': True,
            'data': {
                'auth_url': auth_url,
                'state': state
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取微信登录URL失败: {str(e)}'}), 500

@app.route('/api/wechat/callback', methods=['GET'])
def wechat_callback():
    """微信登录回调处理"""
    try:
        code = request.args.get('code')
        state = request.args.get('state')
        
        if not code:
            return jsonify({'success': False, 'message': '未获取到授权码'}), 400

        # 第一步：通过code获取access_token
        token_url = f"https://api.weixin.qq.com/sns/oauth2/access_token?appid={WECHAT_APP_ID}&secret={WECHAT_APP_SECRET}&code={code}&grant_type=authorization_code"
        
        token_response = requests.get(token_url)
        token_data = token_response.json()
        
        if 'errcode' in token_data:
            return jsonify({'success': False, 'message': f'微信授权失败: {token_data.get("errmsg")}'}), 400
        
        access_token = token_data.get('access_token')
        openid = token_data.get('openid')
        unionid = token_data.get('unionid')
        
        # 第二步：获取用户信息
        user_info_url = f"https://api.weixin.qq.com/sns/userinfo?access_token={access_token}&openid={openid}"
        user_info_response = requests.get(user_info_url)
        user_info = user_info_response.json()
        
        if 'errcode' in user_info:
            return jsonify({'success': False, 'message': f'获取用户信息失败: {user_info.get("errmsg")}'}), 400
        
        wechat_nickname = user_info.get('nickname', '')
        wechat_avatar = user_info.get('headimgurl', '')
        
        # 第三步：检查用户是否存在
        conn = get_db()
        cursor = conn.cursor()
        
        # 通过openid查找用户
        cursor.execute("SELECT * FROM users WHERE wechat_openid = ?", (openid,))
        user = cursor.fetchone()
        
        if user:
            # 用户已存在，更新登录信息
            user_id = user['id']
            cursor.execute("""
                UPDATE users 
                SET last_login_at = CURRENT_TIMESTAMP,
                    wechat_nickname = ?,
                    wechat_avatar = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (wechat_nickname, wechat_avatar, user_id))
            
            # 检查是否完善信息
            cursor.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,))
            profile = cursor.fetchone()
            is_completed = profile['is_completed'] if profile else False
        else:
            # 创建新用户
            # 生成随机用户名和密码
            random_username = f"wx_{openid[:8]}_{random.randint(1000, 9999)}"
            random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            password_hash = bcrypt.hashpw(random_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            cursor.execute("""
                INSERT INTO users (
                    username, email, phone, password_hash, 
                    login_type, wechat_openid, wechat_unionid,
                    wechat_nickname, wechat_avatar, avatar_url
                ) VALUES (?, NULL, NULL, ?, 'wechat', ?, ?, ?, ?, ?)
            """, (random_username, password_hash, openid, unionid, wechat_nickname, wechat_avatar))
            
            user_id = cursor.lastrowid
            is_completed = False
        
        conn.commit()
        conn.close()
        
        # 生成JWT token
        token = jwt.encode({
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(seconds=JWT_EXPIRATION)
        }, JWT_SECRET, algorithm='HS256')
        
        return jsonify({
            'success': True,
            'data': {
                'token': token,
                'user_id': user_id,
                'username': wechat_nickname,
                'avatar_url': wechat_avatar,
                'is_completed': is_completed,
                'need_complete_info': not is_completed
            }
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'微信登录失败: {str(e)}'}), 500

@app.route('/api/user/profile', methods=['GET'])
def get_user_profile():
    """获取用户详细信息"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)
        
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        conn = get_db()
        cursor = conn.cursor()
        
        # 获取用户基本信息
        cursor.execute("SELECT id, username, email, phone, avatar_url, wechat_nickname, wechat_avatar FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        # 获取用户详细信息
        cursor.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,))
        profile = cursor.fetchone()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'user': dict(user) if user else None,
                'profile': dict(profile) if profile else None,
                'is_completed': profile['is_completed'] if profile else False
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取用户信息失败: {str(e)}'}), 500

@app.route('/api/user/profile', methods=['PUT'])
def update_user_profile():
    """更新用户基本信息（username, email, phone）"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)

        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        data = request.json
        username = data.get('username')
        email = data.get('email')
        phone = data.get('phone')

        if not any([username, email, phone]):
            return jsonify({'success': False, 'message': '至少需要更新一个字段'}), 400

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT username, email, phone FROM users WHERE id = ?", (user_id,))
        current_user = cursor.fetchone()

        if not current_user:
            conn.close()
            return jsonify({'success': False, 'message': '用户不存在'}), 404

        if username and username != current_user['username']:
            cursor.execute("SELECT id FROM users WHERE username = ? AND id != ?", (username, user_id))
            if cursor.fetchone():
                conn.close()
                return jsonify({'success': False, 'message': '用户名已被使用'}), 400

        if email and email != current_user['email']:
            cursor.execute("SELECT id FROM users WHERE email = ? AND id != ?", (email, user_id))
            if cursor.fetchone():
                conn.close()
                return jsonify({'success': False, 'message': '邮箱已被使用'}), 400

        if phone and phone != current_user['phone']:
            cursor.execute("SELECT id FROM users WHERE phone = ? AND id != ?", (phone, user_id))
            if cursor.fetchone():
                conn.close()
                return jsonify({'success': False, 'message': '手机号已被使用'}), 400

        update_fields = []
        update_values = []

        if username:
            update_fields.append("username = ?")
            update_values.append(username)
        if email is not None:
            update_fields.append("email = ?")
            update_values.append(email)
        if phone is not None:
            update_fields.append("phone = ?")
            update_values.append(phone)

        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        update_values.append(user_id)

        update_sql = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(update_sql, update_values)

        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': '用户信息更新成功'})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'更新用户信息失败: {str(e)}'}), 500

@app.route('/api/user/profile', methods=['POST'])
def complete_user_profile():
    """完善用户信息"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)
        
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        data = request.get_json()
        
        real_name = data.get('real_name', '')
        phone = data.get('phone', '')
        email = data.get('email', '')
        id_card = data.get('id_card', '')
        bank_account = data.get('bank_account', '')
        bank_name = data.get('bank_name', '')
        address = data.get('address', '')
        
        # 验证必填字段
        if not real_name or not phone:
            return jsonify({'success': False, 'message': '真实姓名和手机号为必填项'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 检查是否已存在profile
        cursor.execute("SELECT id FROM user_profiles WHERE user_id = ?", (user_id,))
        existing_profile = cursor.fetchone()
        
        if existing_profile:
            # 更新
            cursor.execute("""
                UPDATE user_profiles 
                SET real_name = ?, phone = ?, email = ?, id_card = ?,
                    bank_account = ?, bank_name = ?, address = ?,
                    is_completed = 1, completed_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (real_name, phone, email, id_card, bank_account, bank_name, address, user_id))
        else:
            # 插入
            cursor.execute("""
                INSERT INTO user_profiles (
                    user_id, real_name, phone, email, id_card,
                    bank_account, bank_name, address, is_completed, completed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
            """, (user_id, real_name, phone, email, id_card, bank_account, bank_name, address))
        
        # 同时更新users表
        cursor.execute("""
            UPDATE users 
            SET phone = ?, real_name = ?, is_verified = 1, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (phone, real_name, user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '用户信息完善成功'
        })
        
    except sqlite3.IntegrityError as e:
        return jsonify({'success': False, 'message': '手机号已被使用'}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'完善用户信息失败: {str(e)}'}), 500

@app.route('/api/user/require-complete', methods=['GET'])
def check_require_complete():
    """检查用户是否需要完善信息"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)
        
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        conn = get_db()
        cursor = conn.cursor()
        
        # 获取用户详细信息
        cursor.execute("SELECT is_completed FROM user_profiles WHERE user_id = ?", (user_id,))
        profile = cursor.fetchone()
        
        # 获取登录类型
        cursor.execute("SELECT login_type FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        conn.close()
        
        login_type = user['login_type'] if user else 'phone'
        is_completed = profile['is_completed'] if profile else False
        
        # 只有微信登录且未完善信息的用户才需要完善信息
        need_complete = (login_type == 'wechat' and not is_completed)
        
        return jsonify({
            'success': True,
            'data': {
                'need_complete': need_complete,
                'login_type': login_type,
                'is_completed': is_completed
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'检查失败: {str(e)}'}), 500

# ============ 系统通知 ============

@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    """获取用户的通知"""
    try:
        user_id = verify_token(request.headers.get('Authorization'))
        if not user_id:
            return jsonify({'success': False, 'message': '未授权'}), 401

        conn = get_db()
        cursor = conn.cursor()
        
        # 获取全局通知和用户专属通知
        cursor.execute('''
            SELECT n.id, n.title, n.content, n.notification_type, n.created_at,
                   CASE WHEN r.read_at IS NOT NULL THEN 1 ELSE 0 END as is_read
            FROM system_notifications n
            LEFT JOIN user_read_notifications r ON n.id = r.notification_id AND r.user_id = ?
            WHERE n.target_user_id IS NULL OR n.target_user_id = ?
            ORDER BY n.created_at DESC
            LIMIT 50
        ''', (user_id, user_id))
        
        notifications = cursor.fetchall()
        
        result = []
        for notif in notifications:
            result.append({
                'id': notif['id'],
                'title': notif['title'],
                'content': notif['content'],
                'type': notif['notification_type'],
                'isRead': bool(notif['is_read']),
                'createdAt': notif['created_at']
            })
        
        # 统计未读数量
        cursor.execute('''
            SELECT COUNT(*)
            FROM system_notifications n
            LEFT JOIN user_read_notifications r ON n.id = r.notification_id AND r.user_id = ?
            WHERE (n.target_user_id IS NULL OR n.target_user_id = ?) 
              AND r.read_at IS NULL
        ''', (user_id, user_id))
        
        unread_count = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'notifications': result,
                'unreadCount': unread_count
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取通知失败: {str(e)}'}), 500

@app.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
def mark_notification_read(notification_id):
    """标记通知为已读"""
    try:
        user_id = verify_token(request.headers.get('Authorization'))
        if not user_id:
            return jsonify({'success': False, 'message': '未授权'}), 401

        conn = get_db()
        cursor = conn.cursor()
        
        # 检查通知是否存在
        cursor.execute("SELECT id FROM system_notifications WHERE id = ?", (notification_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'message': '通知不存在'}), 404
        
        # 标记为已读
        cursor.execute('''
            INSERT OR IGNORE INTO user_read_notifications (user_id, notification_id)
            VALUES (?, ?)
        ''', (user_id, notification_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': '已标记为已读'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'操作失败: {str(e)}'}), 500

@app.route('/api/notifications/read-all', methods=['POST'])
def mark_all_notifications_read():
    """标记所有通知为已读"""
    try:
        user_id = verify_token(request.headers.get('Authorization'))
        if not user_id:
            return jsonify({'success': False, 'message': '未授权'}), 401

        conn = get_db()
        cursor = conn.cursor()
        
        # 获取所有未读通知
        cursor.execute('''
            SELECT n.id
            FROM system_notifications n
            LEFT JOIN user_read_notifications r ON n.id = r.notification_id AND r.user_id = ?
            WHERE (n.target_user_id IS NULL OR n.target_user_id = ?) 
              AND r.read_at IS NULL
        ''', (user_id, user_id))
        
        notifications = cursor.fetchall()
        
        # 标记为已读
        for notif in notifications:
            cursor.execute('''
                INSERT OR IGNORE INTO user_read_notifications (user_id, notification_id)
                VALUES (?, ?)
            ''', (user_id, notif['id']))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': '已全部标记为已读'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'操作失败: {str(e)}'}), 500

# 需要导入requests和urlencode
import requests
from urllib.parse import urlencode

# ============ 启动服务 ============

if __name__ == '__main__':
    print("=" * 50)
    print("灵值生态园 API 服务启动中...")
    print("=" * 50)
    print("服务地址: http://0.0.0.0:8001")
    print("默认管理员账号: admin / admin123")
    print("=" * 50)

    # 备份数据库
    print("正在备份数据库...")
    backup_database()

    # 初始化默认数据
    init_default_data()

    app.run(host='0.0.0.0', port=8001, debug=True)

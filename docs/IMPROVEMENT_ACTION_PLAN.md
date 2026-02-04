# 灵值生态园智能体 - 改进行动计划

## 📅 计划概览
- **制定时间**: 2026年2月4日
- **执行周期**: 分3个阶段
- **负责人**: AI Agent + 人工审核
- **验收标准**: 每个阶段完成后进行测试验证

---

## 🎯 阶段一：紧急安全加固 (本周内)

### 目标
修复所有高优先级安全问题，确保系统安全运行

### 任务清单

#### 1. 更换默认密钥 (P0)
**状态**: 🔴 未完成
**优先级**: P0 - 最高
**预计时间**: 1小时

**步骤**:
```bash
# 1. 生成强随机密钥
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
python3 -c "import secrets; print('JWT_SECRET=' + secrets.token_hex(32))"

# 2. 更新 .env 文件
# 将生成的密钥添加到 .env

# 3. 更新服务器环境变量
export SSHPASS="Meiyue@root123"
sshpass -e ssh root@123.56.142.143 "echo 'export SECRET_KEY=<生成的密钥>' >> ~/.bashrc"
sshpass -e ssh root@123.56.142.143 "echo 'export JWT_SECRET=<生成的密钥>' >> ~/.bashrc"

# 4. 重启后端服务
sshpass -e ssh root@123.56.142.143 "pkill -f 'python.*app.py' && cd /var/www/backend && nohup python3 app.py > app.log 2>&1 &"
```

**验收标准**:
- [ ] SECRET_KEY 不是默认值
- [ ] JWT_SECRET 不是默认值
- [ ] 服务重启后正常工作
- [ ] 用户登录功能正常

---

#### 2. 添加API速率限制 (P0)
**状态**: 🔴 未完成
**优先级**: P0 - 最高
**预计时间**: 2小时

**步骤**:

**后端修改**:
```python
# 在 admin-backend/app.py 顶部添加
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# 初始化限流器
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# 为关键API添加限流
@app.route('/api/login', methods=['POST'])
@limiter.limit("5 per minute")  # 登录限制：每分钟5次
def login():
    # ... 现有代码

@app.route('/api/send-code', methods=['POST'])
@limiter.limit("3 per minute")  # 验证码限制：每分钟3次
def send_code():
    # ... 现有代码
```

**修改 requirements.txt**:
```
Flask-Limiter==3.5.0
```

**部署**:
```bash
# 安装新依赖
cd admin-backend
pip install Flask-Limiter==3.5.0

# 测试
python3 app.py

# 部署到服务器
./quick-deploy.sh
```

**验收标准**:
- [ ] 安装 Flask-Limiter 成功
- [ ] 登录API超过5次/分钟返回429
- [ ] 验证码API超过3次/分钟返回429
- [ ] 其他功能正常

---

#### 3. 配置HTTPS (P0)
**状态**: 🔴 未完成
**优先级**: P0 - 最高
**预计时间**: 3小时

**步骤**:

**方案A: 使用Let's Encrypt (免费)**
```bash
# 在服务器上执行
sshpass -e ssh root@123.56.142.143

# 1. 安装Certbot
apt-get update
apt-get install -y certbot python3-certbot-nginx

# 2. 获取SSL证书
certbot --nginx -d lingzhiapp.com -d www.lingzhiapp.com

# 3. 自动续期
certbot renew --dry-run

# 4. 配置Nginx强制HTTPS
# 编辑 /etc/nginx/sites-available/default
# 添加以下配置:
server {
    listen 80;
    server_name lingzhiapp.com www.lingzhiapp.com;
    return 301 https://$server_name$request_uri;
}
```

**方案B: 使用云服务商SSL证书**
1. 在阿里云购买SSL证书
2. 下载证书文件
3. 上传到服务器
4. 配置Nginx

**验收标准**:
- [ ] SSL证书安装成功
- [ ] HTTP自动跳转HTTPS
- [ ] 浏览器显示安全锁图标
- [ ] 所有API调用正常

---

### 阶段一验收清单
- [ ] 默认密钥已更换
- [ ] API速率限制已添加
- [ ] HTTPS已配置
- [ ] 所有功能测试通过
- [ ] 安全扫描无高危漏洞

---

## 🔧 阶段二：功能完善与测试 (本月内)

### 目标
完善未测试功能，确保所有功能稳定可靠

### 任务清单

#### 1. 测试充值流程 (P1)
**状态**: 🟡 未完成
**优先级**: P1 - 高
**预计时间**: 4小时

**测试用例**:
```
1. 创建充值订单
   - 输入: 用户ID, 充值档位
   - 预期: 返回订单号和支付信息

2. 上传充值凭证
   - 输入: 订单号, 凭证图片
   - 预期: 凭证上传成功

3. 管理员审核
   - 输入: 订单号, 审核结果
   - 预期: 用户灵值增加

4. 充值记录查询
   - 输入: 用户ID
   - 预期: 返回充值历史
```

**执行步骤**:
```bash
# 1. 测试创建订单
curl -X POST http://123.56.142.143:8001/api/recharge/create-order \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "tier_id": 1}'

# 2. 测试上传凭证
curl -X POST http://123.56.142.143:8001/api/recharge/upload-voucher \
  -F "order_id=xxx" \
  -F "voucher_image=@/path/to/image.jpg"

# 3. 测试管理员审核
curl -X PUT http://123.56.142.143:8001/api/admin/vouchers/1/audit \
  -H "Content-Type: application/json" \
  -d '{"status": "approved", "remark": "审核通过"}'

# 4. 测试查询记录
curl http://123.56.142.143:8001/api/recharge/records?user_id=1
```

**验收标准**:
- [ ] 创建订单成功
- [ ] 凭证上传成功
- [ ] 管理员审核成功
- [ ] 用户灵值正确增加
- [ ] 充值记录查询正常

---

#### 2. 测试知识库功能 (P1)
**状态**: 🟡 未完成
**优先级**: P1 - 高
**预计时间**: 3小时

**测试用例**:
```
1. 创建知识库
   - 输入: 名称, 描述, 分类
   - 预期: 知识库创建成功

2. 添加知识条目
   - 输入: 标题, 内容, 标签
   - 预期: 条目添加成功

3. 关联智能体
   - 输入: 智能体ID, 知识库ID
   - 预期: 关联成功

4. 智能体对话测试
   - 输入: 问题
   - 预期: 回答包含知识库内容
```

**执行步骤**:
```bash
# 1. 初始化知识库
cd admin-backend
python3 << 'EOF'
import sqlite3

conn = sqlite3.connect('lingzhi_ecosystem.db')
cursor = conn.cursor()

# 创建示例知识库
cursor.execute('''
    INSERT INTO knowledge_base (name, description, category, content, tags, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
''', ('灵值生态园规则', '系统使用规则', '系统', '用户每日签到可获得30灵值...', '签到,规则', datetime.now()))

conn.commit()
conn.close()
print('✅ 知识库初始化成功')
EOF

# 2. 测试查询
curl http://123.56.142.143:8001/api/knowledge-bases

# 3. 测试智能体对话
curl -X POST http://123.56.142.143:8001/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "签到可以获得多少灵值？"}'
```

**验收标准**:
- [ ] 知识库创建成功
- [ ] 知识库查询正常
- [ ] 智能体能够检索知识库
- [ ] 对话回答准确

---

#### 3. 实现用户反馈前端 (P1)
**状态**: 🟡 未完成
**优先级**: P1 - 高
**预计时间**: 4小时

**步骤**:

**创建前端页面**:
```typescript
// web-app/src/pages/Feedback.tsx
import React, { useState } from 'react'
import { Send } from 'lucide-react'

export default function Feedback() {
  const [content, setContent] = useState('')
  const [rating, setRating] = useState(5)
  const [submitted, setSubmitted] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    // 调用API提交反馈
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">用户反馈</h1>
      {/* 反馈表单 */}
    </div>
  )
}
```

**更新路由**:
```typescript
// web-app/src/App.tsx
import Feedback from './pages/Feedback'

<Route path="/feedback" element={<Feedback />} />
```

**添加导航入口**:
```typescript
// 在Dashboard中添加反馈入口
<Link to="/feedback">
  <MessageSquare />
  <span>用户反馈</span>
</Link>
```

**验收标准**:
- [ ] 反馈页面创建成功
- [ ] 表单验证正常
- [ ] 反馈提交成功
- [ ] 路由导航正常

---

#### 4. 添加操作日志 (P1)
**状态**: 🟡 未完成
**优先级**: P1 - 高
**预计时间**: 3小时

**步骤**:

**创建日志表**:
```sql
CREATE TABLE IF NOT EXISTS operation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    user_type TEXT,  -- 'user' or 'admin'
    action TEXT,     -- 'login', 'checkin', 'recharge', etc.
    details TEXT,
    ip_address TEXT,
    user_agent TEXT,
    status TEXT,     -- 'success', 'failed'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_logs_user ON operation_logs(user_id);
CREATE INDEX idx_logs_action ON operation_logs(action);
CREATE INDEX idx_logs_created ON operation_logs(created_at);
```

**实现日志装饰器**:
```python
# admin-backend/utils/logger.py
from functools import wraps
import logging
import sqlite3

def log_operation(action: str):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # 记录操作前
            result = f(*args, **kwargs)
            # 记录操作后
            # 保存到数据库
            return result
        return wrapped
    return decorator
```

**应用到关键API**:
```python
@app.route('/api/login', methods=['POST'])
@log_operation('login')
def login():
    # ...
```

**验收标准**:
- [ ] 日志表创建成功
- [ ] 关键操作记录完整
- [ ] 日志查询功能正常
- [ ] 不影响原有功能

---

### 阶段二验收清单
- [ ] 充值流程测试通过
- [ ] 知识库功能测试通过
- [ ] 用户反馈前端完成
- [ ] 操作日志系统完成
- [ ] 所有功能回归测试通过

---

## 🚀 阶段三：性能优化与新功能 (下个季度)

### 目标
优化系统性能，实现新功能扩展

### 任务清单

#### 1. 实现Redis缓存 (P2)
**状态**: 🟢 未完成
**优先级**: P2 - 中
**预计时间**: 6小时

**步骤**:

**安装Redis**:
```bash
# 服务器上安装
sshpass -e ssh root@123.56.142.143 "apt-get install -y redis-server"

# 启动Redis
sshpass -e ssh root@123.56.142.143 "systemctl start redis-server"
sshpass -e ssh root@123.56.142.143 "systemctl enable redis-server"
```

**后端集成Redis**:
```python
# admin-backend/app.py
from redis import Redis
from functools import wraps

# Redis连接
redis_client = Redis(host='localhost', port=6379, db=0, decode_responses=True)

# 缓存装饰器
def cache_result(expire=3600):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{f.__name__}:{args}:{kwargs}"

            # 尝试从缓存获取
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            # 执行函数
            result = f(*args, **kwargs)

            # 保存到缓存
            redis_client.setex(cache_key, expire, json.dumps(result))

            return result
        return wrapped
    return decorator

# 应用到API
@app.route('/api/stats')
@cache_result(expire=300)  # 缓存5分钟
def get_stats():
    # ...
```

**验收标准**:
- [ ] Redis安装成功
- [ ] 缓存功能正常
- [ ] API响应速度提升
- [ ] 缓存过期机制正常

---

#### 2. 前端代码分割 (P2)
**状态**: 🟢 未完成
**优先级**: P2 - 中
**预计时间**: 4小时

**步骤**:

**配置Vite代码分割**:
```typescript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'ui-vendor': ['lucide-react', 'framer-motion'],
          'utils': ['lodash', 'date-fns'],
        }
      }
    }
  }
})
```

**路由懒加载**:
```typescript
// web-app/src/App.tsx
import { lazy } from 'react'

const Dashboard = lazy(() => import('./pages/Dashboard'))
const Chat = lazy(() => import('./pages/Chat'))
// ... 其他页面

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/chat" element={<Chat />} />
        {/* ... */}
      </Routes>
    </Suspense>
  )
}
```

**验收标准**:
- [ ] 代码分割成功
- [ ] 构建产物变小
- [ ] 首屏加载时间减少
- [ ] 路由切换流畅

---

#### 3. 添加系统监控 (P2)
**状态**: 🟢 未完成
**优先级**: P2 - 中
**预计时间**: 5小时

**监控指标**:
```
1. 系统指标
   - CPU使用率
   - 内存使用率
   - 磁盘使用率
   - 网络流量

2. 应用指标
   - 请求响应时间
   - 错误率
   - QPS (每秒查询数)
   - 数据库连接数

3. 业务指标
   - 活跃用户数
   - 签到人数
   - 充值金额
```

**实现方案**:

**方案A: 使用Prometheus + Grafana**
```bash
# 安装Prometheus
apt-get install -y prometheus

# 安装Grafana
apt-get install -y grafana

# 配置Prometheus采集指标
```

**方案B: 自建监控API**
```python
# admin-backend/app.py
@app.route('/api/admin/monitor/metrics')
def get_monitor_metrics():
    return jsonify({
        'system': {
            'cpu': get_cpu_usage(),
            'memory': get_memory_usage(),
            'disk': get_disk_usage(),
        },
        'application': {
            'response_time': get_avg_response_time(),
            'error_rate': get_error_rate(),
            'qps': get_qps(),
        },
        'business': {
            'active_users': get_active_users(),
            'checkin_count': get_checkin_count(),
            'recharge_amount': get_recharge_amount(),
        }
    })
```

**验收标准**:
- [ ] 监控指标采集正常
- [ ] 监控数据准确
- [ ] 告警机制正常
- [ ] 可视化面板完善

---

### 阶段三验收清单
- [ ] Redis缓存实现完成
- [ ] 前端代码分割完成
- [ ] 系统监控实现完成
- [ ] 性能指标达标
- [ ] 性能测试通过

---

## 📊 总体时间表

| 阶段 | 开始时间 | 结束时间 | 状态 |
|------|----------|----------|------|
| 阶段一: 安全加固 | 2026-02-04 | 2026-02-11 | 🟡 进行中 |
| 阶段二: 功能完善 | 2026-02-12 | 2026-02-29 | ⏳ 计划中 |
| 阶段三: 性能优化 | 2026-03-01 | 2026-03-31 | ⏳ 计划中 |

---

## 🎯 成功指标

### 阶段一成功指标
- [ ] 安全评分 > 90
- [ ] 无高危漏洞
- [ ] HTTPS正常工作

### 阶段二成功指标
- [ ] 功能完整性 > 95%
- [ ] 测试覆盖率 > 80%
- [ ] Bug数量 < 5

### 阶段三成功指标
- [ ] API响应时间 < 500ms
- [ ] 首屏加载时间 < 2s
- [ ] 系统可用性 > 99%

---

## 📝 备注说明

### 风险评估
1. **配置HTTPS可能影响旧用户访问** - 需要提前通知
2. **Redis部署需要额外资源** - 需评估服务器容量
3. **代码分割可能引入新问题** - 需要充分测试

### 资源需求
- 人力资源: 1名开发人员 + 1名测试人员
- 服务器资源: 额外2GB内存用于Redis
- 时间资源: 3个阶段共约3个月

### 依赖条件
- 云服务商SSL证书
- Redis服务支持
- 监控工具授权

---

**计划制定时间**: 2026年2月4日
**计划执行负责人**: AI Agent
**计划审核人**: 人工审核
**下次更新时间**: 每周五更新进度

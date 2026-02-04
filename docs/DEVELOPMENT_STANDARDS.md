# 灵值生态园智能体 - 开发规范

## 📋 文档说明
本文档定义了灵值生态园智能体项目的开发规范，所有开发人员必须严格遵守，以确保代码质量、系统稳定性和可维护性。

---

## 🎯 一、开发流程规范

### 1.1 开发环境要求

#### 环境配置
- **Node.js**: >= 18.0.0
- **Python**: >= 3.9
- **Git**: >= 2.30
- **数据库**: SQLite (开发), PostgreSQL (生产建议)

#### IDE推荐
- **前端**: VSCode + Volar插件
- **后端**: PyCharm / VSCode + Python插件

### 1.2 开发流程

#### 步骤1: 需求分析
```
1. 明确需求目标和范围
2. 评估技术可行性
3. 识别潜在风险
4. 制定实现方案
5. 编写设计文档（如需要）
```

#### 步骤2: 本地开发
```
1. 创建功能分支: git checkout -b feature/xxx
2. 按照代码规范编写代码
3. 本地测试验证
4. 编写单元测试（如需要）
5. 代码自审查
```

#### 步骤3: 扣子平台测试
```
1. 在扣子平台创建工作流/智能体
2. 配置必要的工具和知识库
3. 测试所有功能场景
4. 验证输出格式和准确性
5. 记录测试结果和问题
```

#### 步骤4: 代码合并
```
1. 提交代码: git commit -m "feat: xxx"
2. 推送到远程: git push origin feature/xxx
3. 创建Pull Request
4. 代码审查
5. 合并到主分支
```

#### 步骤5: 云服务器部署
```
1. 运行部署脚本: ./quick-deploy.sh
2. 验证部署成功
3. 在服务器上测试关键功能
4. 更新部署文档
5. 记录部署日志
```

### 1.3 开发笔记规范

#### 必须记录的内容
```markdown
## 功能开发笔记 - [功能名称]

### 开发时间
- 开始: YYYY-MM-DD HH:MM
- 结束: YYYY-MM-DD HH:MM
- 耗时: X小时

### 需求描述
[详细描述功能需求和目标]

### 实现方案
[说明技术方案和关键实现]

### 关键代码
[记录重要的代码片段和说明]

### 测试记录
[记录测试用例和结果]

### 遇到的问题
[记录开发过程中的问题和解决方案]

### 遗留问题
[记录未解决的问题和后续计划]

### 部署记录
[记录部署过程和验证结果]
```

---

## 💻 二、代码规范

### 2.1 前端代码规范 (TypeScript/React)

#### 命名规范
```typescript
// 组件命名: PascalCase
export default function UserProfile() {}

// 函数命名: camelCase
function getUserData() {}

// 变量命名: camelCase
const userName = 'xxx'

// 常量命名: UPPER_SNAKE_CASE
const MAX_RETRY_COUNT = 3

// 类型命名: PascalCase
interface UserData {}
type UserRole = 'admin' | 'user'

// 文件命名: PascalCase (组件), camelCase (工具)
// UserProfile.tsx
// userService.ts
```

#### 组件结构
```typescript
import React, { useState, useEffect } from 'react'
import { Icon } from 'lucide-react'

// 1. 类型定义
interface Props {
  title: string
  onSubmit: (data: any) => void
}

// 2. 组件定义
export default function MyComponent({ title, onSubmit }: Props) {
  // 3. 状态定义
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState(null)

  // 4. 副作用
  useEffect(() => {
    fetchData()
  }, [])

  // 5. 事件处理
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // ...
  }

  // 6. 渲染
  return (
    <div className="container">
      {/* JSX */}
    </div>
  )
}

// 7. 工具函数
async function fetchData() {
  // ...
}
```

#### Hooks规范
```typescript
// ✅ 正确: 使用自定义Hook提取逻辑
function useUserData(userId: string) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchUser(userId).then(setUser).finally(() => setLoading(false))
  }, [userId])

  return { user, loading }
}

// ❌ 错误: 在组件内直接调用API
export default function MyComponent() {
  useEffect(() => {
    fetch('/api/user').then(res => res.json()) // 不应该直接调用
  }, [])
}
```

#### 样式规范
```typescript
// ✅ 优先使用Tailwind CSS
<div className="flex items-center justify-between p-4 bg-white rounded-lg shadow">

// ✅ 复杂样式使用styled-components或CSS模块
<div className={styles.container}>

// ❌ 避免使用内联样式
<div style={{ display: 'flex', padding: '16px' }}>
```

### 2.2 后端代码规范 (Python/Flask)

#### 命名规范
```python
# 函数命名: snake_case
def get_user_data(user_id: int) -> dict:
    pass

# 类命名: PascalCase
class UserManager:
    pass

# 变量命名: snake_case
user_name = 'xxx'

# 常量命名: UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3

# 文件命名: snake_case
# user_service.py
```

#### API路由规范
```python
# ✅ 正确: 使用RESTful风格
@app.route('/api/users', methods=['GET'])           # 获取列表
@app.route('/api/users/<int:id>', methods=['GET'])  # 获取单个
@app.route('/api/users', methods=['POST'])          # 创建
@app.route('/api/users/<int:id>', methods=['PUT'])  # 更新
@app.route('/api/users/<int:id>', methods=['DELETE']) # 删除

# ❌ 错误: 不规范的路由
@app.route('/api/getUserById')  # 不符合RESTful规范
```

#### 错误处理规范
```python
# ✅ 正确: 统一的错误处理
@app.route('/api/users/<int:id>')
def get_user(id: int):
    try:
        user = db.query_user(id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify(user)
    except Exception as e:
        logger.error(f'Error getting user {id}: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

# ❌ 错误: 没有错误处理
@app.route('/api/users/<int:id>')
def get_user(id: int):
    user = db.query_user(id)
    return jsonify(user)
```

#### 数据库操作规范
```python
# ✅ 正确: 使用参数化查询
cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))

# ❌ 错误: SQL注入风险
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

### 2.3 Git提交规范

#### Commit Message格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Type类型
```
feat:     新功能
fix:      修复bug
docs:     文档更新
style:    代码格式调整
refactor: 重构
perf:     性能优化
test:     测试相关
chore:    构建/工具相关
```

#### 示例
```
feat(backend): 添加用户验证码登录功能

- 新增发送验证码API
- 新增验证验证码API
- 更新登录流程支持验证码

Closes #123
```

---

## 🔐 三、安全规范

### 3.1 敏感信息管理

#### 环境变量
```bash
# ✅ 正确: 使用环境变量
SECRET_KEY=os.getenv('SECRET_KEY', 'default')

# ❌ 错误: 硬编码密钥
SECRET_KEY='my-secret-key-123'
```

#### 密码处理
```python
# ✅ 正确: 使用bcrypt加密
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

# ❌ 错误: 明文存储
password = 'user123'
```

#### SQL注入防护
```python
# ✅ 正确: 参数化查询
cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))

# ❌ 错误: 字符串拼接
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

### 3.2 API安全

#### 认证授权
```python
# ✅ 正确: 使用JWT认证
from flask_jwt_extended import jwt_required, get_jwt_identity

@app.route('/api/protected')
@jwt_required()
def protected():
    user_id = get_jwt_identity()
    return jsonify({'user_id': user_id})

# ❌ 错误: 没有认证
@app.route('/api/protected')
def protected():
    return jsonify({'data': 'sensitive'})
```

#### 速率限制
```python
# ✅ 正确: 添加速率限制
@app.route('/api/login')
@limiter.limit("5 per minute")
def login():
    pass
```

#### 输入验证
```python
# ✅ 正确: 验证输入
@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()

    # 验证必填字段
    if not data.get('username'):
        return jsonify({'error': 'Username required'}), 400

    # 验证数据类型
    if not isinstance(data.get('age'), int):
        return jsonify({'error': 'Age must be integer'}), 400

    # ...
```

---

## 🧪 四、测试规范

### 4.1 前端测试

#### 单元测试
```typescript
// ✅ 使用Jest + React Testing Library
import { render, screen } from '@testing-library/react'
import UserCard from './UserCard'

describe('UserCard', () => {
  it('should display user name', () => {
    render(<UserCard name="John" />)
    expect(screen.getByText('John')).toBeInTheDocument()
  })
})
```

#### 集成测试
```typescript
// 测试API调用
import { getUserData } from './api'
import { rest } from 'msw'
import { setupServer } from 'msw/node'

const server = setupServer(
  rest.get('/api/users/1', (req, res, ctx) => {
    return res(ctx.json({ id: 1, name: 'John' }))
  })
)

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

test('getUserData fetches user data', async () => {
  const user = await getUserData(1)
  expect(user.name).toBe('John')
})
```

### 4.2 后端测试

#### 单元测试
```python
# ✅ 使用pytest
import pytest

def test_hash_password():
    password = 'test123'
    hashed = hash_password(password)
    assert verify_password(password, hashed)
    assert not verify_password('wrong', hashed)
```

#### API测试
```python
# ✅ 使用Flask测试客户端
def test_login(client):
    response = client.post('/api/login', json={
        'username': 'test',
        'password': 'test123'
    })
    assert response.status_code == 200
    assert 'token' in response.json
```

---

## 📚 五、文档规范

### 5.1 代码注释

#### 函数注释
```python
def get_user_with_activity(user_id: int, days: int = 7) -> dict:
    """
    获取用户及其最近N天的活动记录

    Args:
        user_id: 用户ID
        days: 查询天数，默认7天

    Returns:
        包含用户信息和活动记录的字典

    Raises:
        ValueError: 当user_id不存在时

    Example:
        >>> get_user_with_activity(1, 7)
        {'user': {'id': 1, 'name': 'John'}, 'activities': [...]}
    """
    # ...
```

#### TypeScript类型注释
```typescript
/**
 * 用户数据接口
 */
interface UserData {
  /** 用户ID */
  id: number;
  /** 用户名 */
  name: string;
  /** 用户角色 */
  role: 'admin' | 'user' | 'guest';
  /** 创建时间 */
  createdAt: Date;
}

/**
 * 获取用户数据
 * @param userId - 用户ID
 * @returns 用户数据
 */
async function getUserData(userId: number): Promise<UserData> {
  // ...
}
```

### 5.2 API文档

#### 使用OpenAPI规范
```yaml
paths:
  /api/users:
    get:
      summary: 获取用户列表
      parameters:
        - name: page
          in: query
          type: integer
          description: 页码
      responses:
        200:
          description: 成功
          schema:
            type: object
            properties:
              users:
                type: array
                items:
                  $ref: '#/definitions/User'
```

---

## 🚀 六、部署规范

### 6.1 部署前检查清单

```bash
# 代码质量检查
□ 代码格式化完成
□ 代码审查通过
□ 单元测试通过
□ 集成测试通过

# 功能检查
□ 所有功能验证完成
□ 边界情况测试
□ 错误处理验证

# 性能检查
□ 前端打包优化
□ API响应时间测试
□ 数据库查询优化

# 安全检查
□ 敏感信息检查
□ 依赖漏洞扫描
□ 权限配置验证

# 文档检查
□ API文档更新
□ 部署文档更新
□ 开发笔记完成
```

### 6.2 部署流程

```bash
# 1. 本地构建
cd web-app
npm run build

# 2. 提交代码
git add .
git commit -m "feat: xxx"
git push origin main

# 3. 部署到服务器
./quick-deploy.sh

# 4. 验证部署
curl http://123.56.142.143/api/health

# 5. 测试关键功能
# ...

# 6. 监控日志
ssh root@123.56.142.143 "tail -f /var/www/backend/app.log"
```

### 6.3 回滚流程

```bash
# 1. 停止服务
ssh root@123.56.142.143 "pkill -f 'python.*app.py'"

# 2. 恢复备份
ssh root@123.56.142.143 "cp /var/www/backend/app.py.backup /var/www/backend/app.py"

# 3. 重启服务
ssh root@123.56.142.143 "cd /var/www/backend && nohup python3 app.py > app.log 2>&1 &"

# 4. 验证恢复
curl http://123.56.142.143/api/health
```

---

## 📊 七、监控与维护

### 7.1 日志规范

#### 日志级别
```python
# DEBUG: 详细调试信息
logger.debug(f"Processing user {user_id}")

# INFO: 一般信息
logger.info(f"User {user_id} logged in successfully")

# WARNING: 警告信息
logger.warning(f"User {user_id} has reached rate limit")

# ERROR: 错误信息
logger.error(f"Failed to fetch user {user_id}: {str(e)}")

# CRITICAL: 严重错误
logger.critical("Database connection lost")
```

#### 日志格式
```python
# 统一日志格式
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/www/backend/app.log'),
        logging.StreamHandler()
    ]
)
```

### 7.2 监控指标

#### 系统指标
- CPU使用率
- 内存使用率
- 磁盘使用率
- 网络流量

#### 应用指标
- API响应时间
- 错误率
- QPS (每秒查询数)
- 数据库连接数

#### 业务指标
- 活跃用户数
- 签到率
- 充值金额
- 对话成功率

---

## 🎯 八、质量目标

### 8.1 代码质量指标

| 指标 | 目标值 | 测量方式 |
|------|--------|----------|
| 代码覆盖率 | > 80% | Jest / pytest |
| 圈复杂度 | < 10 | SonarQube |
| 代码重复率 | < 5% | SonarQube |
| TypeScript覆盖率 | 100% | tsconfig |
| ESLint错误数 | 0 | eslint |

### 8.2 性能指标

| 指标 | 目标值 | 测量方式 |
|------|--------|----------|
| API响应时间 | < 500ms | APM工具 |
| 首屏加载时间 | < 2s | Lighthouse |
| 数据库查询时间 | < 100ms | 慢查询日志 |
| 并发用户数 | > 1000 | 压力测试 |

### 8.3 安全指标

| 指标 | 目标值 | 测量方式 |
|------|--------|----------|
| 高危漏洞数 | 0 | 安全扫描 |
| 中危漏洞数 | < 5 | 安全扫描 |
| 密码强度 | 强 | 密码策略 |
| HTTPS覆盖率 | 100% | 检查清单 |

---

## 📝 九、违规处理

### 9.1 轻度违规
- **定义**: 不符合代码风格、缺少注释等
- **处理**: 代码审查时指出，要求修改

### 9.2 中度违规
- **定义**: 不符合安全规范、缺少测试等
- **处理**: 拒绝合并，要求补充

### 9.3 严重违规
- **定义**: 硬编码密钥、SQL注入漏洞等
- **处理**: 立即修复，进行培训

---

## 📖 十、参考资源

### 文档
- [React官方文档](https://react.dev)
- [Flask官方文档](https://flask.palletsprojects.com)
- [TypeScript官方文档](https://www.typescriptlang.org)
- [OWASP安全指南](https://owasp.org)

### 工具
- [ESLint](https://eslint.org)
- [Prettier](https://prettier.io)
- [SonarQube](https://www.sonarqube.org)
- [Snyk](https://snyk.io)

---

**文档版本**: v1.0
**生效日期**: 2026年2月4日
**维护人员**: AI Agent
**更新频率**: 每季度更新

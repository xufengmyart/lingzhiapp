# 微信小程序登录配置指南

## 概述

系统已支持微信小程序登录功能，采用类似三维商联的登录方式：
- 支持微信授权登录
- 支持手机号快速验证
- 自动创建或关联用户账号
- 完整的 token 认证机制

## 1. 后端配置

### 1.1 环境变量配置

在 `admin-backend/.env` 文件中添加以下配置：

```bash
# 微信小程序配置
WECHAT_APP_ID=your_app_id_here
WECHAT_APP_SECRET=your_app_secret_here
```

### 1.2 获取 AppID 和 AppSecret

1. 登录 [微信公众平台](https://mp.weixin.qq.com/)
2. 进入"开发" → "开发管理" → "开发设置"
3. 记录 AppID
4. 重置并记录 AppSecret（只显示一次）

### 1.3 数据库迁移

数据库已自动添加微信相关字段：

```sql
wechat_openid          VARCHAR(100) UNIQUE    -- 微信 OpenID
wechat_unionid         VARCHAR(100)           -- 微信 UnionID（跨应用唯一）
wechat_session_key     VARCHAR(100)           -- 会话密钥（加密存储）
nickname               VARCHAR(100)           -- 昵称
avatar_url             VARCHAR(500)           -- 头像
gender                 INTEGER DEFAULT 0      -- 性别（0-未知，1-男，2-女）
city                   VARCHAR(50)            -- 城市
province               VARCHAR(50)           -- 省份
country                VARCHAR(50)           -- 国家
phone                  VARCHAR(20)            -- 手机号
```

## 2. 前端配置（微信小程序）

### 2.1 创建小程序项目

1. 下载并安装 [微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)
2. 创建新项目，选择"小程序"
3. 填写 AppID（从微信公众平台获取）
4. 选择"JavaScript"或"TypeScript"基础模板

### 2.2 配置 app.js

```javascript
App({
  globalData: {
    apiUrl: 'https://meiyueart.com',  // 修改为你的域名
    token: '',
    user: null
  },

  onLaunch() {
    this.checkLogin()
  },

  checkLogin() {
    const token = wx.getStorageSync('token')
    const user = wx.getStorageSync('user')

    if (token && user) {
      this.globalData.token = token
      this.globalData.user = user
    }
  }
})
```

### 2.3 实现登录页面

参考 `docs/wechat_miniprogram_login_guide.md` 中的完整代码。

关键步骤：
1. 调用 `wx.login()` 获取 code
2. 将 code 发送到 `/api/wechat/login`
3. 后端返回 token 和用户信息
4. 存储到 `globalData` 和 `localStorage`
5. 后续请求携带 token

## 3. 后端 API

### 3.1 微信登录

**接口**: `POST /api/wechat/login`

**请求参数**:
```json
{
  "code": "wx_login_code",           // 微信登录 code
  "userInfo": {                      // 可选，用户信息
    "nickName": "用户昵称",
    "avatarUrl": "头像URL",
    "gender": 1,
    "city": "城市",
    "province": "省份",
    "country": "国家"
  }
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "token": "jwt_token_here",
    "user": {
      "id": 1,
      "username": "用户名",
      "nickname": "昵称",
      "avatar_url": "头像URL",
      "total_lingzhi": 100
    }
  }
}
```

### 3.2 绑定手机号

**接口**: `POST /api/wechat/phone-number`

**请求头**:
```
Authorization: Bearer {token}
```

**请求参数**:
```json
{
  "code": "phone_number_code"  // 手机号验证 code
}
```

**响应**:
```json
{
  "success": true,
  "message": "手机号绑定成功"
}
```

## 4. 登录流程

### 4.1 静默登录（推荐）

```
用户打开小程序
    ↓
wx.login() 获取 code
    ↓
发送 code 到后端
    ↓
后端调用微信 API 获取 openid
    ↓
查询用户是否存在
    ↓
存在 → 返回 token
不存在 → 创建新用户 → 返回 token
```

### 4.2 授权登录

```
用户点击"微信授权登录"
    ↓
wx.getUserProfile() 获取用户信息
    ↓
wx.login() 获取 code
    ↓
发送 code 和 userInfo 到后端
    ↓
后端创建或更新用户信息
    ↓
返回 token 和用户信息
```

### 4.3 手机号快速验证

```
用户点击"手机号快速验证"
    ↓
wx.login() 获取 code
    ↓
发送 code 到后端（登录）
    ↓
getPhoneNumber() 获取手机号 code
    ↓
发送手机号 code 到后端（绑定）
    ↓
后端解密并保存手机号
```

## 5. 安全注意事项

### 5.1 后端安全

1. **Access Token 缓存**
   - 后端已自动缓存 access_token，有效期 7200 秒
   - 避免频繁调用微信 API

2. **Session Key 加密**
   - session_key 需要加密存储（可选，使用 AES-256）
   - 建议使用 `Fernet` 或 `cryptography` 库

3. **HTTPS 通信**
   - 生产环境必须使用 HTTPS
   - 本地开发可以使用 HTTP

### 5.2 前端安全

1. **不存储敏感信息**
   - 不要在 `localStorage` 存储 openid 和 session_key
   - 只存储 token

2. **Token 管理**
   - token 有效期 24 小时
   - token 失败时自动跳转登录

3. **用户授权**
   - `wx.getUserProfile` 每次都需要用户授权
   - 可以先静默登录，再引导授权

## 6. 测试

### 6.1 本地测试

1. 启动后端服务：
```bash
cd admin-backend
python app.py
```

2. 在微信开发者工具中配置：
   - "开发" → "开发管理" → "开发设置" → "服务器域名"
   - 添加 `https://meiyueart.com` 到 request 合法域名

3. 临时关闭域名校验（仅开发）：
   - 微信开发者工具 → "详情" → "本地设置" → 勾选"不校验合法域名"

### 6.2 生产测试

1. 配置正确的域名
2. 使用真实的 AppID 和 AppSecret
3. 测试登录、token 认证、手机号绑定等流程

## 7. 常见问题

### Q1: 提示"invalid code"

**原因**: code 已过期或被使用过

**解决**: 每次 wx.login() 后立即使用 code，不要重复使用

### Q2: 提示"access_token 失效"

**原因**: access_token 已过期（7200 秒）

**解决**: 后端已自动处理，无需手动操作

### Q3: 手机号解密失败

**原因**: session_key 无效或已过期

**解决**:
- 重新登录获取新的 session_key
- 检查 session_key 加密/解密逻辑

### Q4: 用户信息不显示

**原因**: 未调用 `wx.getUserProfile` 获取授权

**解决**:
- 引导用户点击授权按钮
- 或使用默认昵称和头像

## 8. 后续优化建议

1. **UnionID 机制**
   - 如果有多个小程序/公众号，使用 UnionID 关联
   - 需要在微信开放平台绑定应用

2. **多种登录方式**
   - 手机号验证码登录
   - 邮箱登录
   - 第三方登录（支付宝、QQ等）

3. **用户绑定**
   - 支持微信账号绑定已有账号
   - 支持手机号绑定微信账号

4. **数据分析**
   - 统计微信登录用户占比
   - 分析用户来源和活跃度

## 9. 参考资料

- [微信小程序登录流程](https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/login.html)
- [获取用户信息](https://developers.weixin.qq.com/miniprogram/dev/api/open-api/user-info/wx.getUserProfile.html)
- [获取手机号](https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/getPhoneNumber.html)
- [服务器接口调试工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/httpdebugger.html)

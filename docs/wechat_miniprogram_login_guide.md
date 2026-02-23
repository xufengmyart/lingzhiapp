# 微信小程序登录系统 - 前端实现

## 1. 登录页面 (pages/login/login.js)

```javascript
// pages/login/login.js
const app = getApp()

Page({
  data: {
    loading: false,
    userInfo: null
  },

  onLoad() {
    // 检查是否已登录
    if (app.globalData.token) {
      wx.redirectTo({
        url: '/pages/dashboard/dashboard'
      })
    }
  },

  // 微信授权登录
  handleWeChatLogin() {
    this.setData({ loading: true })

    // 1. 获取用户授权
    wx.getUserProfile({
      desc: '用于完善用户资料',
      success: (res) => {
        this.data.userInfo = res.userInfo
        this.doLogin()
      },
      fail: (err) => {
        console.error('获取用户信息失败', err)
        // 用户拒绝授权，直接登录（不获取用户信息）
        this.doLogin()
      },
      complete: () => {
        this.setData({ loading: false })
      }
    })
  },

  // 执行登录
  doLogin() {
    wx.showLoading({
      title: '登录中...',
      mask: true
    })

    // 2. 获取登录 code
    wx.login({
      success: (loginRes) => {
        if (!loginRes.code) {
          wx.showToast({
            title: '获取登录凭证失败',
            icon: 'none'
          })
          return
        }

        // 3. 将 code 发送到后端
        wx.request({
          url: app.globalData.apiUrl + '/api/wechat/login',
          method: 'POST',
          data: {
            code: loginRes.code,
            userInfo: this.data.userInfo || null
          },
          success: (res) => {
            if (res.data.success) {
              const { token, user } = res.data.data

              // 4. 保存 token 和用户信息
              app.globalData.token = token
              app.globalData.user = user
              wx.setStorageSync('token', token)
              wx.setStorageSync('user', user)

              wx.showToast({
                title: '登录成功',
                icon: 'success'
              })

              // 5. 跳转到首页
              setTimeout(() => {
                wx.switchTab({
                  url: '/pages/dashboard/dashboard'
                })
              }, 1500)
            } else {
              wx.showToast({
                title: res.data.error || '登录失败',
                icon: 'none'
              })
            }
          },
          fail: (err) => {
            console.error('登录请求失败', err)
            wx.showToast({
              title: '网络错误，请重试',
              icon: 'none'
            })
          },
          complete: () => {
            wx.hideLoading()
          }
        })
      },
      fail: (err) => {
        console.error('wx.login 失败', err)
        wx.showToast({
          title: '登录失败',
          icon: 'none'
        })
        wx.hideLoading()
      }
    })
  },

  // 手机号快速验证登录
  handlePhoneLogin() {
    this.setData({ loading: true })

    // 获取手机号按钮（需要 button open-type="getPhoneNumber"）
    wx.showModal({
      title: '提示',
      content: '请使用手机号快速验证按钮进行登录',
      showCancel: false
    })

    this.setData({ loading: false })
  }
})
```

## 2. 登录页面 WXML (pages/login/login.wxml)

```xml
<!--pages/login/login.wxml-->
<view class="login-container">
  <view class="login-box">
    <!-- Logo -->
    <view class="logo-section">
      <image class="logo" src="/assets/logo.png" mode="aspectFit"></image>
      <text class="app-name">灵值生态园</text>
      <text class="app-slogan">连接价值，共创未来</text>
    </view>

    <!-- 登录按钮 -->
    <view class="login-buttons">
      <!-- 微信授权登录 -->
      <button
        class="wechat-login-btn"
        bindtap="handleWeChatLogin"
        loading="{{loading}}"
        disabled="{{loading}}"
      >
        <image class="btn-icon" src="/assets/wechat-icon.png" mode="aspectFit"></image>
        <text>微信授权登录</text>
      </button>

      <!-- 手机号快速验证 -->
      <button
        class="phone-login-btn"
        open-type="getPhoneNumber"
        bindgetphonenumber="handlePhoneLogin"
        loading="{{loading}}"
        disabled="{{loading}}"
      >
        <image class="btn-icon" src="/assets/phone-icon.png" mode="aspectFit"></image>
        <text>手机号快速验证</text>
      </button>
    </view>

    <!-- 用户协议 -->
    <view class="agreement">
      <checkbox checked="{{agreed}}" bindtap="toggleAgreement" />
      <text class="agreement-text">
        我已阅读并同意
        <text class="link" bindtap="showUserAgreement">《用户协议》</text>
        和
        <text class="link" bindtap="showPrivacyPolicy">《隐私政策》</text>
      </text>
    </view>
  </view>
</view>
```

## 3. 登录页面样式 (pages/login/login.wxss)

```css
/* pages/login/login.wxss */
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40rpx;
}

.login-box {
  width: 100%;
  max-width: 600rpx;
}

.logo-section {
  text-align: center;
  margin-bottom: 120rpx;
}

.logo {
  width: 160rpx;
  height: 160rpx;
  margin-bottom: 30rpx;
  border-radius: 32rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.15);
}

.app-name {
  display: block;
  font-size: 48rpx;
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 16rpx;
}

.app-slogan {
  display: block;
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.8);
}

.login-buttons {
  margin-bottom: 40rpx;
}

.wechat-login-btn {
  width: 100%;
  height: 96rpx;
  background: #ffffff;
  border-radius: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.1);
  font-size: 32rpx;
  color: #333333;
  border: none;
}

.wechat-login-btn::after {
  border: none;
}

.wechat-login-btn[disabled] {
  opacity: 0.6;
}

.phone-login-btn {
  width: 100%;
  height: 96rpx;
  background: rgba(255, 255, 255, 0.2);
  border: 2rpx solid rgba(255, 255, 255, 0.3);
  border-radius: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32rpx;
  color: #ffffff;
  margin-bottom: 24rpx;
}

.phone-login-btn::after {
  border: none;
}

.btn-icon {
  width: 40rpx;
  height: 40rpx;
  margin-right: 16rpx;
}

.agreement {
  display: flex;
  align-items: flex-start;
  padding: 0 20rpx;
}

.agreement checkbox {
  margin-right: 12rpx;
  margin-top: 4rpx;
}

.agreement-text {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.6;
}

.agreement-text .link {
  color: #ffffff;
  text-decoration: underline;
}
```

## 4. 请求封装 (utils/request.js)

```javascript
// utils/request.js
const app = getApp()

function request(url, options = {}) {
  const {
    method = 'GET',
    data = {},
    header = {},
    needAuth = true
  } = options

  // 添加 token
  if (needAuth && app.globalData.token) {
    header['Authorization'] = 'Bearer ' + app.globalData.token
  }

  return new Promise((resolve, reject) => {
    wx.request({
      url: app.globalData.apiUrl + url,
      method,
      data,
      header: {
        'Content-Type': 'application/json',
        ...header
      },
      success: (res) => {
        if (res.statusCode === 200) {
          if (res.data.success) {
            resolve(res.data)
          } else {
            // 业务错误
            if (res.data.error === '未授权') {
              // token 失效，跳转到登录页
              app.clearLoginData()
              wx.redirectTo({
                url: '/pages/login/login'
              })
            }
            reject(res.data)
          }
        } else {
          reject({
            success: false,
            error: '网络请求失败'
          })
        }
      },
      fail: (err) => {
        reject({
          success: false,
          error: err.errMsg || '网络请求失败'
        })
      }
    })
  })
}

module.exports = {
  get: (url, data, options) => request(url, { ...options, method: 'GET', data }),
  post: (url, data, options) => request(url, { ...options, method: 'POST', data }),
  put: (url, data, options) => request(url, { ...options, method: 'PUT', data }),
  delete: (url, data, options) => request(url, { ...options, method: 'DELETE', data })
}
```

## 5. app.js 全局配置

```javascript
// app.js
App({
  globalData: {
    apiUrl: 'https://meiyueart.com',
    token: '',
    user: null
  },

  onLaunch() {
    // 检查登录状态
    this.checkLogin()

    // 检查更新
    this.checkUpdate()
  },

  // 检查登录状态
  checkLogin() {
    const token = wx.getStorageSync('token')
    const user = wx.getStorageSync('user')

    if (token && user) {
      this.globalData.token = token
      this.globalData.user = user
    }
  },

  // 清除登录数据
  clearLoginData() {
    this.globalData.token = ''
    this.globalData.user = null
    wx.removeStorageSync('token')
    wx.removeStorageSync('user')
  },

  // 检查小程序更新
  checkUpdate() {
    if (wx.canIUse('getUpdateManager')) {
      const updateManager = wx.getUpdateManager()

      updateManager.onCheckForUpdate((res) => {
        if (res.hasUpdate) {
          console.log('发现新版本')
        }
      })

      updateManager.onUpdateReady(() => {
        wx.showModal({
          title: '更新提示',
          content: '新版本已准备好，是否重启应用？',
          success: (res) => {
            if (res.confirm) {
              updateManager.applyUpdate()
            }
          }
        })
      })

      updateManager.onUpdateFailed(() => {
        wx.showToast({
          title: '更新失败',
          icon: 'none'
        })
      })
    }
  }
})
```

## 6. 获取手机号处理

```javascript
// 在登录页面中添加
Page({
  data: {
    loading: false,
    userInfo: null
  },

  // 处理获取手机号
  handleGetPhoneNumber(e) {
    if (e.detail.errMsg !== 'getPhoneNumber:ok') {
      wx.showToast({
        title: '获取手机号失败',
        icon: 'none'
      })
      return
    }

    this.setData({ loading: true })

    // 先登录获取 token
    this.doLogin(e.detail.code)
  },

  // 执行登录（带手机号 code）
  doLogin(phoneCode = null) {
    wx.showLoading({
      title: '登录中...',
      mask: true
    })

    wx.login({
      success: (loginRes) => {
        if (!loginRes.code) {
          wx.showToast({
            title: '获取登录凭证失败',
            icon: 'none'
          })
          return
        }

        wx.request({
          url: app.globalData.apiUrl + '/api/wechat/login',
          method: 'POST',
          data: {
            code: loginRes.code,
            userInfo: this.data.userInfo || null
          },
          success: (res) => {
            if (res.data.success) {
              const { token, user } = res.data.data

              app.globalData.token = token
              app.globalData.user = user
              wx.setStorageSync('token', token)
              wx.setStorageSync('user', user)

              // 如果有手机号 code，绑定手机号
              if (phoneCode) {
                this.bindPhoneNumber(phoneCode)
              } else {
                this.jumpToDashboard()
              }
            } else {
              wx.showToast({
                title: res.data.error || '登录失败',
                icon: 'none'
              })
            }
          },
          fail: (err) => {
            console.error('登录请求失败', err)
            wx.showToast({
              title: '网络错误，请重试',
              icon: 'none'
            })
          },
          complete: () => {
            wx.hideLoading()
            this.setData({ loading: false })
          }
        })
      }
    })
  },

  // 绑定手机号
  bindPhoneNumber(code) {
    wx.request({
      url: app.globalData.apiUrl + '/api/wechat/phone-number',
      method: 'POST',
      header: {
        'Authorization': 'Bearer ' + app.globalData.token
      },
      data: { code },
      success: (res) => {
        if (res.data.success) {
          wx.showToast({
            title: '手机号绑定成功',
            icon: 'success'
          })
          this.jumpToDashboard()
        } else {
          wx.showToast({
            title: res.data.error || '绑定失败',
            icon: 'none'
          })
        }
      },
      fail: (err) => {
        console.error('绑定手机号失败', err)
        this.jumpToDashboard() // 即使失败也跳转
      }
    })
  },

  // 跳转到首页
  jumpToDashboard() {
    setTimeout(() => {
      wx.switchTab({
        url: '/pages/dashboard/dashboard'
      })
    }, 1500)
  }
})
```

## 7. 数据库表结构更新

```sql
-- 为 users 表添加微信相关字段
ALTER TABLE users ADD COLUMN wechat_openid VARCHAR(100) UNIQUE;
ALTER TABLE users ADD COLUMN wechat_unionid VARCHAR(100);
ALTER TABLE users ADD COLUMN wechat_session_key VARCHAR(100);
ALTER TABLE users ADD COLUMN nickname VARCHAR(100);
ALTER TABLE users ADD COLUMN avatar_url VARCHAR(500);
ALTER TABLE users ADD COLUMN gender INT DEFAULT 0;
ALTER TABLE users ADD COLUMN city VARCHAR(50);
ALTER TABLE users ADD COLUMN province VARCHAR(50);
ALTER TABLE users ADD COLUMN country VARCHAR(50);
ALTER TABLE users ADD COLUMN phone VARCHAR(20);
```

## 8. app.json 配置

```json
{
  "pages": [
    "pages/login/login",
    "pages/dashboard/dashboard",
    "pages/profile/profile"
  ],
  "tabBar": {
    "list": [
      {
        "pagePath": "pages/dashboard/dashboard",
        "text": "首页",
        "iconPath": "assets/home.png",
        "selectedIconPath": "assets/home-active.png"
      },
      {
        "pagePath": "pages/profile/profile",
        "text": "我的",
        "iconPath": "assets/profile.png",
        "selectedIconPath": "assets/profile-active.png"
      }
    ]
  },
  "permission": {
    "scope.userLocation": {
      "desc": "你的位置信息将用于小程序位置接口的效果展示"
    }
  }
}
```

## 关键点总结

1. **登录流程**：
   - 前端调用 `wx.login()` 获取 code
   - 将 code 发送到后端
   - 后端调用微信 API 换取 openid
   - 后端查询或创建用户
   - 后端生成 JWT token
   - 前端存储 token，后续请求携带 token

2. **安全性**：
   - 不在前端存储 openid 和 session_key
   - 使用 HTTPS 通信
   - Token 有过期时间
   - 手机号获取需要用户授权

3. **用户体验**：
   - 支持静默登录（只获取 code）
   - 支持授权登录（获取用户信息）
   - 支持手机号快速验证
   - 自动检查更新
   - Token 失效自动跳转登录

4. **注意事项**：
   - `wx.getUserProfile` 每次调用都需要用户授权
   - 手机号获取需要认证的小程序
   - access_token 需要缓存
   - session_key 需要加密存储

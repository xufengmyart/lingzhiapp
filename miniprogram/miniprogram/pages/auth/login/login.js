// pages/auth/login/login.js
const authApi = require('../../../api/auth.js')

Page({
  /**
   * 页面的初始数据
   */
  data: {
    formData: {
      username: '',
      password: ''
    },
    showPassword: false,
    loading: false
  },

  /**
   * 用户名输入
   */
  onUsernameInput(e) {
    this.setData({
      'formData.username': e.detail.value
    })
  },

  /**
   * 密码输入
   */
  onPasswordInput(e) {
    this.setData({
      'formData.password': e.detail.value
    })
  },

  /**
   * 切换密码显示/隐藏
   */
  togglePassword() {
    this.setData({
      showPassword: !this.data.showPassword
    })
  },

  /**
   * 处理登录
   */
  handleLogin() {
    const { username, password } = this.data.formData

    // 表单验证
    if (!username) {
      wx.showToast({
        title: '请输入用户名',
        icon: 'none'
      })
      return
    }

    if (!password) {
      wx.showToast({
        title: '请输入密码',
        icon: 'none'
      })
      return
    }

    // 设置加载状态
    this.setData({ loading: true })

    // 调用登录 API
    authApi.login(username, password)
      .then(res => {
        // 保存 Token 和用户信息
        wx.setStorageSync('lingzhi_token', res.data.token)
        wx.setStorageSync('lingzhi_user_info', res.data.user)

        wx.showToast({
          title: '登录成功',
          icon: 'success'
        })

        // 延迟跳转，让用户看到成功提示
        setTimeout(() => {
          wx.reLaunch({
            url: '/pages/index/index'
          })
        }, 1500)
      })
      .catch(err => {
        console.error('登录失败:', err)
      })
      .finally(() => {
        this.setData({ loading: false })
      })
  },

  /**
   * 导航到注册页面
   */
  navigateToRegister() {
    wx.navigateTo({
      url: '/pages/auth/register/register'
    })
  },

  /**
   * 导航到忘记密码页面
   */
  navigateToForgot() {
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    })
  }
})

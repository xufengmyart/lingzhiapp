// pages/user/profile/profile.js
const authApi = require('../../../api/auth.js')
const userApi = require('../../../api/user.js')

Page({
  /**
   * 页面的初始数据
   */
  data: {
    userInfo: {
      username: '',
      avatarUrl: '',
      realName: '',
      totalLingzhi: 0
    },
    isLogin: false
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
    this.checkLoginStatus()
  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {
    this.loadUserInfo()
  },

  /**
   * 检查登录状态
   */
  checkLoginStatus() {
    const token = wx.getStorageSync('lingzhi_token')
    this.setData({ isLogin: !!token })
  },

  /**
   * 加载用户信息
   */
  loadUserInfo() {
    const token = wx.getStorageSync('lingzhi_token')
    if (!token) {
      this.setData({
        userInfo: {
          username: '未登录',
          avatarUrl: '',
          realName: '',
          totalLingzhi: 0
        },
        isLogin: false
      })
      return
    }

    // 先从本地存储获取
    const localUserInfo = wx.getStorageSync('lingzhi_user_info')
    if (localUserInfo) {
      this.setData({
        userInfo: localUserInfo,
        isLogin: true
      })
    }

    // 从服务器获取最新数据
    userApi.getUserInfo()
      .then(res => {
        this.setData({
          userInfo: res.data,
          isLogin: true
        })
        // 更新本地存储
        wx.setStorageSync('lingzhi_user_info', res.data)
      })
      .catch(err => {
        console.error('获取用户信息失败:', err)
      })
  },

  /**
   * 头像上传
   */
  handleAvatarUpload() {
    const token = wx.getStorageSync('lingzhi_token')
    if (!token) {
      wx.navigateTo({
        url: '/pages/auth/login/login'
      })
      return
    }

    wx.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        const tempFilePath = res.tempFilePaths[0]

        wx.showLoading({
          title: '上传中...'
        })

        userApi.uploadAvatar(tempFilePath)
          .then(uploadRes => {
            wx.showToast({
              title: '上传成功',
              icon: 'success'
            })
            // 刷新用户信息
            this.loadUserInfo()
          })
          .catch(err => {
            console.error('上传头像失败:', err)
          })
          .finally(() => {
            wx.hideLoading()
          })
      }
    })
  },

  /**
   * 导航到编辑资料
   */
  navigateToEditProfile() {
    const token = wx.getStorageSync('lingzhi_token')
    if (!token) {
      wx.navigateTo({
        url: '/pages/auth/login/login'
      })
      return
    }
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    })
  },

  /**
   * 导航到修改密码
   */
  navigateToChangePassword() {
    const token = wx.getStorageSync('lingzhi_token')
    if (!token) {
      wx.navigateTo({
        url: '/pages/auth/login/login'
      })
      return
    }
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    })
  },

  /**
   * 导航到推荐人信息
   */
  navigateToReferral() {
    const token = wx.getStorageSync('lingzhi_token')
    if (!token) {
      wx.navigateTo({
        url: '/pages/auth/login/login'
      })
      return
    }
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    })
  },

  /**
   * 导航到消息通知
   */
  navigateToNotifications() {
    wx.navigateTo({
      url: '/pages/notifications/list/list'
    })
  },

  /**
   * 导航到关于我们
   */
  navigateToAbout() {
    wx.showModal({
      title: '关于我们',
      content: '灵值生态园智能体系统\n版本: v1.0.0\n\n致力于打造智能资源匹配与价值共享平台',
      showCancel: false
    })
  },

  /**
   * 退出登录
   */
  handleLogout() {
    wx.showModal({
      title: '提示',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          authApi.logout()
        }
      }
    })
  }
})

// pages/index/index.js
const authApi = require('../../api/auth.js')
const resourcesApi = require('../../api/resources.js')
const userApi = require('../../api/user.js')

Page({
  /**
   * 页面的初始数据
   */
  data: {
    userInfo: null,
    recentResources: [],
    notices: [
      {
        id: 1,
        title: '欢迎使用灵值生态园',
        time: '2024-02-23'
      }
    ]
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
    this.loadUserInfo()
    this.loadRecentResources()
  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {
    // 刷新用户信息
    this.loadUserInfo()
  },

  /**
   * 加载用户信息
   */
  loadUserInfo() {
    const userInfo = wx.getStorageSync('lingzhi_user_info')
    if (userInfo) {
      this.setData({ userInfo })
    }
  },

  /**
   * 加载最新资源
   */
  loadRecentResources() {
    resourcesApi.getResourceList({ page: 1, limit: 5 })
      .then(res => {
        this.setData({
          recentResources: res.data || []
        })
      })
      .catch(err => {
        console.error('加载资源失败:', err)
      })
  },

  /**
   * 导航到资源列表
   */
  navigateToResources() {
    wx.switchTab({
      url: '/pages/resources/list/list'
    })
  },

  /**
   * 导航到任务列表
   */
  navigateToTasks() {
    wx.switchTab({
      url: '/pages/tasks/list/list'
    })
  },

  /**
   * 导航到项目列表
   */
  navigateToProjects() {
    wx.navigateTo({
      url: '/pages/projects/list/list'
    })
  },

  /**
   * 导航到通知列表
   */
  navigateToNotifications() {
    wx.navigateTo({
      url: '/pages/notifications/list/list'
    })
  },

  /**
   * 导航到个人中心
   */
  navigateToProfile() {
    const token = wx.getStorageSync('lingzhi_token')
    if (token) {
      wx.switchTab({
        url: '/pages/user/profile/profile'
      })
    } else {
      wx.navigateTo({
        url: '/pages/auth/login/login'
      })
    }
  },

  /**
   * 导航到资源详情
   */
  navigateToResourceDetail(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/resources/detail/detail?id=${id}`
    })
  }
})

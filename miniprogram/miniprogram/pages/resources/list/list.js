// pages/resources/list/list.js
const resourcesApi = require('../../../api/resources.js')

Page({
  /**
   * 页面的初始数据
   */
  data: {
    resources: [],
    currentTab: 'all',
    searchText: '',
    page: 1,
    loading: false,
    hasMore: true
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
    this.loadResources()
  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {
    // 刷新列表
    this.setData({
      page: 1,
      resources: []
    })
    this.loadResources()
  },

  /**
   * 下拉刷新
   */
  onPullDownRefresh() {
    this.setData({
      page: 1,
      resources: []
    })
    this.loadResources().then(() => {
      wx.stopPullDownRefresh()
    })
  },

  /**
   * 上拉加载更多
   */
  onReachBottom() {
    if (this.data.hasMore && !this.data.loading) {
      this.setData({
        page: this.data.page + 1
      })
      this.loadResources()
    }
  },

  /**
   * 搜索输入
   */
  onSearchInput(e) {
    this.setData({
      searchText: e.detail.value
    })
  },

  /**
   * 搜索
   */
  onSearch() {
    this.setData({
      page: 1,
      resources: []
    })
    this.loadResources()
  },

  /**
   * 切换标签
   */
  switchTab(e) {
    const tab = e.currentTarget.dataset.tab
    this.setData({
      currentTab: tab,
      page: 1,
      resources: []
    })
    this.loadResources()
  },

  /**
   * 加载资源列表
   */
  loadResources() {
    if (this.data.loading) return

    this.setData({ loading: true })

    const params = {
      page: this.data.page,
      limit: 20
    }

    // 添加状态筛选
    if (this.data.currentTab !== 'all') {
      params.status = this.data.currentTab
    }

    resourcesApi.getResourceList(params)
      .then(res => {
        const newResources = this.data.page === 1 ? res.data : [...this.data.resources, ...res.data]
        this.setData({
          resources: newResources,
          hasMore: res.data && res.data.length >= 20
        })
      })
      .catch(err => {
        console.error('加载资源失败:', err)
      })
      .finally(() => {
        this.setData({ loading: false })
      })
  },

  /**
   * 获取状态文本
   */
  getStatusText(item) {
    if (item.authorizationStatus === 'authorized') {
      return '已授权'
    } else if (item.verificationStatus === 'pending') {
      return '待审核'
    } else {
      return '未授权'
    }
  },

  /**
   * 导航到详情页
   */
  navigateToDetail(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/resources/detail/detail?id=${id}`
    })
  },

  /**
   * 导航到创建页面
   */
  navigateToCreate() {
    wx.navigateTo({
      url: '/pages/resources/create/create'
    })
  }
})

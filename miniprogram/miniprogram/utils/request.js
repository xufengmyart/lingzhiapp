// 网络请求封装
const config = require('./config.js')

/**
 * 统一请求方法
 * @param {string} url 请求地址
 * @param {object} options 请求配置
 * @returns {Promise} 返回Promise对象
 */
function request(url, options = {}) {
  const {
    method = 'GET',
    data = {},
    header = {},
    needAuth = true
  } = options

  // 获取 Token
  const token = wx.getStorageSync(config.tokenKey)

  // 如果需要认证且没有 Token，跳转到登录页
  if (needAuth && !token) {
    wx.navigateTo({
      url: '/pages/auth/login/login'
    })
    return Promise.reject(new Error('未登录'))
  }

  // 构建请求头
  const requestHeader = {
    'content-type': 'application/json',
    ...header
  }

  // 添加认证头
  if (needAuth && token) {
    requestHeader['Authorization'] = `Bearer ${token}`
  }

  // 构建完整 URL
  const fullUrl = url.startsWith('http') ? url : `${config.apiBaseUrl}${url}`

  return new Promise((resolve, reject) => {
    wx.request({
      url: fullUrl,
      method: method.toUpperCase(),
      data: data,
      header: requestHeader,
      timeout: config.requestTimeout,
      success(res) {
        const { statusCode, data: responseData } = res

        // 处理 HTTP 状态码
        if (statusCode === 200) {
          // 处理业务状态码
          if (responseData.success) {
            resolve(responseData)
          } else {
            // 业务错误
            wx.showToast({
              title: responseData.message || '请求失败',
              icon: 'none',
              duration: 2000
            })
            reject(new Error(responseData.message || '请求失败'))
          }
        } else if (statusCode === 401) {
          // 未授权，清除 Token 并跳转到登录页
          wx.removeStorageSync(config.tokenKey)
          wx.removeStorageSync(config.userInfoKey)
          wx.navigateTo({
            url: '/pages/auth/login/login'
          })
          reject(new Error('登录已过期，请重新登录'))
        } else {
          // 其他 HTTP 错误
          wx.showToast({
            title: `请求失败(${statusCode})`,
            icon: 'none',
            duration: 2000
          })
          reject(new Error(`请求失败: ${statusCode}`))
        }
      },
      fail(err) {
        console.error('请求失败:', err)
        wx.showToast({
          title: '网络请求失败',
          icon: 'none',
          duration: 2000
        })
        reject(err)
      }
    })
  })
}

/**
 * GET 请求
 * @param {string} url 请求地址
 * @param {object} params 查询参数
 * @param {boolean} needAuth 是否需要认证
 */
function get(url, params = {}, needAuth = true) {
  return request(url, {
    method: 'GET',
    data: params,
    needAuth
  })
}

/**
 * POST 请求
 * @param {string} url 请求地址
 * @param {object} data 请求体数据
 * @param {boolean} needAuth 是否需要认证
 */
function post(url, data = {}, needAuth = true) {
  return request(url, {
    method: 'POST',
    data: data,
    needAuth
  })
}

/**
 * PUT 请求
 * @param {string} url 请求地址
 * @param {object} data 请求体数据
 * @param {boolean} needAuth 是否需要认证
 */
function put(url, data = {}, needAuth = true) {
  return request(url, {
    method: 'PUT',
    data: data,
    needAuth
  })
}

/**
 * DELETE 请求
 * @param {string} url 请求地址
 * @param {boolean} needAuth 是否需要认证
 */
function del(url, needAuth = true) {
  return request(url, {
    method: 'DELETE',
    needAuth
  })
}

/**
 * 上传文件
 * @param {string} url 上传地址
 * @param {string} filePath 文件路径
 * @param {string} name 文件字段名
 * @param {object} formData 额外表单数据
 */
function uploadFile(url, filePath, name = 'file', formData = {}) {
  const token = wx.getStorageSync(config.tokenKey)

  const header = {}
  if (token) {
    header['Authorization'] = `Bearer ${token}`
  }

  return new Promise((resolve, reject) => {
    wx.uploadFile({
      url: url.startsWith('http') ? url : `${config.apiBaseUrl}${url}`,
      filePath: filePath,
      name: name,
      formData: formData,
      header: header,
      success(res) {
        if (res.statusCode === 200) {
          try {
            const data = JSON.parse(res.data)
            if (data.success) {
              resolve(data)
            } else {
              wx.showToast({
                title: data.message || '上传失败',
                icon: 'none'
              })
              reject(new Error(data.message || '上传失败'))
            }
          } catch (e) {
            reject(new Error('上传失败'))
          }
        } else {
          wx.showToast({
            title: `上传失败(${res.statusCode})`,
            icon: 'none'
          })
          reject(new Error(`上传失败: ${res.statusCode}`))
        }
      },
      fail(err) {
        wx.showToast({
          title: '上传失败',
          icon: 'none'
        })
        reject(err)
      }
    })
  })
}

module.exports = {
  request,
  get,
  post,
  put,
  del,
  uploadFile
}

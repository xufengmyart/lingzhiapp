// 认证相关 API
const request = require('../utils/request.js')

/**
 * 用户登录
 * @param {string} username 用户名
 * @param {string} password 密码
 */
function login(username, password) {
  return request.post('/auth/login', {
    username,
    password
  }, false)
}

/**
 * 用户注册
 * @param {string} username 用户名
 * @param {string} password 密码
 * @param {string} phone 手机号
 * @param {string} verifyCode 验证码
 */
function register(username, password, phone, verifyCode) {
  return request.post('/auth/register', {
    username,
    password,
    phone,
    verifyCode
  }, false)
}

/**
 * 发送验证码
 * @param {string} phone 手机号
 */
function sendVerifyCode(phone) {
  return request.post('/auth/send-code', {
    phone
  }, false)
}

/**
 * 重置密码
 * @param {string} phone 手机号
 * @param {string} newPassword 新密码
 * @param {string} verifyCode 验证码
 */
function resetPassword(phone, newPassword, verifyCode) {
  return request.post('/auth/reset-password', {
    phone,
    newPassword,
    verifyCode
  }, false)
}

/**
 * 退出登录
 */
function logout() {
  wx.removeStorageSync('lingzhi_token')
  wx.removeStorageSync('lingzhi_user_info')
  wx.reLaunch({
    url: '/pages/index/index'
  })
}

module.exports = {
  login,
  register,
  sendVerifyCode,
  resetPassword,
  logout
}

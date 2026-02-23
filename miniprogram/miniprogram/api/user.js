// 用户相关 API
const request = require('../utils/request.js')

/**
 * 获取用户信息
 */
function getUserInfo() {
  return request.get('/user/info')
}

/**
 * 更新用户信息
 * @param {object} data 用户数据
 */
function updateUserInfo(data) {
  return request.put('/user/info', data)
}

/**
 * 上传头像
 * @param {string} filePath 文件路径
 */
function uploadAvatar(filePath) {
  return request.uploadFile('/user/avatar', filePath, 'file')
}

/**
 * 修改密码
 * @param {string} oldPassword 旧密码
 * @param {string} newPassword 新密码
 */
function changePassword(oldPassword, newPassword) {
  return request.post('/user/change-password', {
    oldPassword,
    newPassword
  })
}

/**
 * 获取用户灵值
 */
function getLingzhi() {
  return request.get('/user/lingzhi')
}

/**
 * 获取推荐人信息
 */
function getReferralInfo() {
  return request.get('/user/referral')
}

module.exports = {
  getUserInfo,
  updateUserInfo,
  uploadAvatar,
  changePassword,
  getLingzhi,
  getReferralInfo
}

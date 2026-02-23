// 资源相关 API
const request = require('../utils/request.js')

/**
 * 获取资源列表
 * @param {object} params 查询参数
 */
function getResourceList(params = {}) {
  const { page = 1, limit = 20, status } = params
  return request.get('/private-resources', {
    page,
    limit,
    status
  })
}

/**
 * 获取资源详情
 * @param {number} resourceId 资源ID
 */
function getResourceDetail(resourceId) {
  return request.get(`/private-resources/${resourceId}`)
}

/**
 * 创建资源
 * @param {object} data 资源数据
 */
function createResource(data) {
  return request.post('/private-resources', data)
}

/**
 * 更新资源
 * @param {number} resourceId 资源ID
 * @param {object} data 资源数据
 */
function updateResource(resourceId, data) {
  return request.put(`/private-resources/${resourceId}`, data)
}

/**
 * 删除资源
 * @param {number} resourceId 资源ID
 */
function deleteResource(resourceId) {
  return request.del(`/private-resources/${resourceId}`)
}

/**
 * 授权资源
 * @param {number} resourceId 资源ID
 * @param {object} data 授权数据
 */
function authorizeResource(resourceId, data) {
  return request.post(`/private-resources/${resourceId}/authorize`, data)
}

/**
 * 获取匹配列表
 */
function getMatchList() {
  return request.get('/resource-matches')
}

/**
 * 自动匹配资源
 */
function autoMatchResources() {
  return request.post('/resource-matches/auto-match')
}

module.exports = {
  getResourceList,
  getResourceDetail,
  createResource,
  updateResource,
  deleteResource,
  authorizeResource,
  getMatchList,
  autoMatchResources
}

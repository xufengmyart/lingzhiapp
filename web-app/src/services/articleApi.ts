import axios from 'axios';

// 创建 axios 实例
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 添加 token
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // 未授权，清除 token 并跳转到登录页
          localStorage.removeItem('token');
          window.location.href = '/login';
          break;
        case 403:
          // 权限不足
          console.error('权限不足');
          break;
        case 404:
          // 资源不存在
          console.error('资源不存在');
          break;
        case 500:
          // 服务器错误
          console.error('服务器错误');
          break;
        default:
          console.error('请求失败:', error.response.data);
      }
    } else {
      console.error('网络错误:', error.message);
    }
    return Promise.reject(error);
  }
);

// ==================== 文章相关 API ====================

/**
 * 获取文章列表
 */
export const getArticles = (params?: {
  page?: number;
  page_size?: number;
  category_id?: number;
  status?: string;
  keyword?: string;
  sort?: string;
}) => {
  return api.get('/admin/news/articles', { params });
};

/**
 * 获取文章详情（通过 slug）
 */
export const getArticleBySlug = (slug: string) => {
  return api.get(`/v9/news/articles/${slug}`);
};

/**
 * 创建文章
 */
export const createArticle = (data: {
  title: string;
  slug: string;
  content: string;
  summary?: string;
  category_id: number;
  author_id: number;
  author_name: string;
  cover_image?: string;
  is_pinned?: boolean;
  is_featured?: boolean;
  status?: string;
}) => {
  return api.post('/admin/news/articles', data);
};

/**
 * 更新文章
 */
export const updateArticle = (id: number, data: {
  title?: string;
  slug?: string;
  content?: string;
  summary?: string;
  category_id?: number;
  author_name?: string;
  cover_image?: string;
  is_pinned?: boolean;
  is_featured?: boolean;
  status?: string;
}) => {
  return api.put(`/admin/news/articles/${id}`, data);
};

/**
 * 删除文章
 */
export const deleteArticle = (id: number) => {
  return api.delete(`/admin/news/articles/${id}`);
};

/**
 * 审核通过文章
 */
export const approveArticle = (id: number) => {
  return api.put(`/admin/news/articles/${id}/approve`);
};

/**
 * 审核拒绝文章
 */
export const rejectArticle = (id: number, reason: string) => {
  return api.put(`/admin/news/articles/${id}/reject`, { reason });
};

/**
 * 点赞文章
 */
export const likeArticle = (id: number) => {
  return api.post(`/v9/news/articles/${id}/like`);
};

// ==================== 分享相关 API ====================

/**
 * 获取文章分享信息
 */
export const getShareInfo = (articleId: number, type: string) => {
  return api.get(`/articles/${articleId}/share`, { params: { type } });
};

// ==================== 分类相关 API ====================

/**
 * 获取分类列表
 */
export const getCategories = () => {
  return api.get('/v9/news/categories');
};

// ==================== 评论相关 API ====================

/**
 * 获取文章评论列表
 */
export const getComments = (articleId: number, params?: {
  page?: number;
  page_size?: number;
}) => {
  return api.get(`/v9/news/articles/${articleId}/comments`, { params });
};

/**
 * 创建评论
 */
export const createComment = (articleId: number, data: {
  content: string;
  parent_id?: number;
}) => {
  return api.post(`/v9/news/articles/${articleId}/comments`, data);
};

/**
 * 点赞评论
 */
export const likeComment = (articleId: number, commentId: number) => {
  return api.post(`/v9/news/articles/${articleId}/comments/${commentId}/like`);
};

// ==================== 通知相关 API ====================

/**
 * 获取通知列表
 */
export const getNotifications = (params?: {
  page?: number;
  page_size?: number;
  is_read?: boolean;
  type?: string;
}) => {
  return api.get('/v9/notifications', { params });
};

/**
 * 获取未读通知数量
 */
export const getUnreadNotificationCount = () => {
  return api.get('/v9/notifications/unread/count');
};

/**
 * 获取最新通知
 */
export const getLatestNotifications = (limit?: number) => {
  return api.get('/v9/notifications/latest', { params: { limit } });
};

/**
 * 标记通知为已读
 */
export const markNotificationAsRead = (notificationId: number) => {
  return api.put(`/v9/notifications/${notificationId}/read`);
};

/**
 * 标记所有通知为已读
 */
export const markAllNotificationsAsRead = () => {
  return api.put('/v9/notifications/read-all');
};

/**
 * 删除通知
 */
export const deleteNotification = (notificationId: number) => {
  return api.delete(`/v9/notifications/${notificationId}`);
};

// ==================== 推荐关系管理 API（仅超级管理员） ====================

/**
 * 获取所有推荐关系
 */
export const getReferralRelationships = (params?: {
  page?: number;
  limit?: number;
  referrer_id?: number;
  referee_id?: number;
}) => {
  return api.get('/admin/referral/relationships', { params });
};

/**
 * 修改推荐关系
 */
export const updateReferralRelationship = (relationshipId: number, data: {
  referrer_id?: number;
  status?: 'active' | 'inactive';
}) => {
  return api.put(`/admin/referral/relationships/${relationshipId}`, data);
};

/**
 * 删除推荐关系
 */
export const deleteReferralRelationship = (relationshipId: number) => {
  return api.delete(`/admin/referral/relationships/${relationshipId}`);
};

/**
 * 获取分享统计
 */
export const getShareStats = (params?: {
  page?: number;
  limit?: number;
  user_id?: number;
  article_id?: number;
  share_type?: string;
}) => {
  return api.get('/admin/share/stats', { params });
};

/**
 * 获取分享统计摘要
 */
export const getShareSummary = () => {
  return api.get('/admin/share/summary');
};

// ==================== 用户相关 API ====================

/**
 * 获取当前用户信息
 */
export const getCurrentUser = () => {
  return api.get('/auth/user');
};

export default api;

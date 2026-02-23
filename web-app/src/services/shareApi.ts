/**
 * 分享系统 API 服务
 */

import axios from 'axios';

const API_BASE_URL = 'https://meiyueart.com/api';

// 获取转化率统计
export const getConversionStats = async (token: string, days: number = 7) => {
  try {
    const response = await axios.get(
      `${API_BASE_URL}/share/conversion?days=${days}`,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      }
    );
    return response.data;
  } catch (error) {
    console.error('获取转化率统计失败:', error);
    throw error;
  }
};

// 获取分享排行榜
export const getShareLeaderboard = async (period: string = 'week', limit: number = 10) => {
  try {
    const response = await axios.get(
      `${API_BASE_URL}/share/leaderboard?period=${period}&limit=${limit}`,
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
    return response.data;
  } catch (error) {
    console.error('获取排行榜失败:', error);
    throw error;
  }
};

// 记录分享点击
export const trackShareClick = async (data: {
  referral_code: string;
  article_id: number;
  platform: string;
}) => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/share/click`,
      data,
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
    return response.data;
  } catch (error) {
    console.error('记录分享点击失败:', error);
    throw error;
  }
};

// 记录分享带来的注册
export const trackShareRegistration = async (data: {
  referral_code: string;
  new_user_id: number;
}) => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/share/registration`,
      data,
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
    return response.data;
  } catch (error) {
    console.error('记录分享注册失败:', error);
    throw error;
  }
};

// 获取推荐关系树（管理员）
export const getReferralTree = async (token: string) => {
  try {
    const response = await axios.get(
      `${API_BASE_URL}/referral/tree`,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      }
    );
    return response.data;
  } catch (error) {
    console.error('获取推荐关系树失败:', error);
    throw error;
  }
};

// 获取推荐奖励记录（管理员）
export const getReferralRewards = async (token: string, page: number = 1, perPage: number = 20) => {
  try {
    const response = await axios.get(
      `${API_BASE_URL}/referral/rewards?page=${page}&per_page=${perPage}`,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      }
    );
    return response.data;
  } catch (error) {
    console.error('获取推荐奖励记录失败:', error);
    throw error;
  }
};

// 手动发放奖励（管理员）
export const grantManualReward = async (token: string, data: {
  target_user_id: number;
  amount: number;
  reason: string;
}) => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/referral/rewards/manual`,
      data,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      }
    );
    return response.data;
  } catch (error) {
    console.error('手动发放奖励失败:', error);
    throw error;
  }
};

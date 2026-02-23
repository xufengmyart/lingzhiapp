import React, { useState, useEffect } from 'react';

interface CustomerGroup {
  id: number;
  merchant_id: number;
  group_name: string;
  group_type: string;
  platform: string;
  member_count: number;
  verification_proof: string;
  status: string;
  created_at: string;
}

interface Referral {
  id: number;
  referrer_id: number;
  referee_merchant_id: number;
  referral_code: string;
  status: string;
  reward_contribution: number;
  reward_lingzhi: number;
  confirmed_at: string;
}

interface CouponVerification {
  id: number;
  merchant_id: number;
  user_id: number;
  coupon_code: string;
  reward_contribution: number;
  reward_lingzhi: number;
  created_at: string;
}

const MerchantWorkbench: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'groups' | 'referrals' | 'coupons'>('groups');
  const [customerGroups, setCustomerGroups] = useState<CustomerGroup[]>([]);
  const [referrals, setReferrals] = useState<Referral[]>([]);
  const [couponVerifications, setCouponVerifications] = useState<CouponVerification[]>([]);
  const [loading, setLoading] = useState(false);
  const [showGroupModal, setShowGroupModal] = useState(false);
  const [showReferralModal, setShowReferralModal] = useState(false);
  const [showCouponModal, setShowCouponModal] = useState(false);
  const [userRole, setUserRole] = useState<string>('');
  const [userId, setUserId] = useState<string>('');
  const [groupFormData, setGroupFormData] = useState({
    group_name: '',
    group_type: '',
    platform: '',
    member_count: 0,
    verification_proof: ''
  });
  const [referralFormData, setReferralFormData] = useState({
    referee_merchant_id: 0,
    referral_code: ''
  });
  const [couponFormData, setCouponFormData] = useState({
    coupon_code: ''
  });

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

  useEffect(() => {
    const role = localStorage.getItem('userRole') || '';
    const uid = localStorage.getItem('userId') || '';
    setUserRole(role);
    setUserId(uid);
    
    if (role === 'merchant' || role === 'admin') {
      fetchCustomerGroups();
      fetchReferrals();
      fetchCouponVerifications();
    }
  }, []);

  const fetchCustomerGroups = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/merchant/customer-groups`, {
        headers: {
          'X-User-ID': userId
        }
      });
      const data = await response.json();
      setCustomerGroups(data.groups || []);
    } catch (error) {
      console.error('获取客户群失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchReferrals = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/merchant/referrals`, {
        headers: {
          'X-User-ID': userId
        }
      });
      const data = await response.json();
      setReferrals(data.referrals || []);
    } catch (error) {
      console.error('获取推荐记录失败:', error);
    }
  };

  const fetchCouponVerifications = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/merchant/coupons/verified`, {
        headers: {
          'X-User-ID': userId
        }
      });
      const data = await response.json();
      setCouponVerifications(data.verifications || []);
    } catch (error) {
      console.error('获取核销记录失败:', error);
    }
  };

  const handleCreateGroup = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/merchant/customer-groups`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': userId
        },
        body: JSON.stringify(groupFormData)
      });
      if (response.ok) {
        alert('客户群登记成功！已获得100贡献值奖励');
        setShowGroupModal(false);
        setGroupFormData({
          group_name: '',
          group_type: '',
          platform: '',
          member_count: 0,
          verification_proof: ''
        });
        fetchCustomerGroups();
      } else {
        const error = await response.json();
        alert(error.error || '登记失败');
      }
    } catch (error) {
      console.error('登记客户群失败:', error);
    }
  };

  const handleCreateReferral = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/merchant/referrals`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': userId
        },
        body: JSON.stringify(referralFormData)
      });
      if (response.ok) {
        alert('推荐成功！已获得200贡献值+50灵值奖励');
        setShowReferralModal(false);
        setReferralFormData({
          referee_merchant_id: 0,
          referral_code: ''
        });
        fetchReferrals();
      } else {
        const error = await response.json();
        alert(error.error || '推荐失败');
      }
    } catch (error) {
      console.error('推荐商家失败:', error);
    }
  };

  const handleVerifyCoupon = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/merchant/coupons/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': userId
        },
        body: JSON.stringify(couponFormData)
      });
      if (response.ok) {
        alert('优惠券核销成功！已获得30贡献值+10灵值奖励');
        setShowCouponModal(false);
        setCouponFormData({ coupon_code: '' });
        fetchCouponVerifications();
      } else {
        const error = await response.json();
        alert(error.error || '核销失败');
      }
    } catch (error) {
      console.error('核销优惠券失败:', error);
    }
  };

  if (userRole !== 'merchant' && userRole !== 'admin') {
    return (
      <div className="merchant-workbench">
        <div className="access-denied">
          <h2>权限不足</h2>
          <p>此页面仅限商家访问</p>
        </div>
      </div>
    );
  }

  return (
    <div className="merchant-workbench">
      <div className="header">
        <h1>商家工作台</h1>
        <div className="header-actions">
          <button
            className="btn-primary"
            onClick={() => setShowGroupModal(true)}
          >
            + 登记客户群
          </button>
          <button
            className="btn-primary"
            onClick={() => setShowReferralModal(true)}
          >
            + 推荐商家
          </button>
          <button
            className="btn-success"
            onClick={() => setShowCouponModal(true)}
          >
            核销优惠券
          </button>
        </div>
      </div>

      <div className="tabs">
        <button
          className={activeTab === 'groups' ? 'active' : ''}
          onClick={() => setActiveTab('groups')}
        >
          客户群管理
        </button>
        <button
          className={activeTab === 'referrals' ? 'active' : ''}
          onClick={() => setActiveTab('referrals')}
        >
          推荐记录
        </button>
        <button
          className={activeTab === 'coupons' ? 'active' : ''}
          onClick={() => setActiveTab('coupons')}
        >
          优惠券核销
        </button>
      </div>

      <div className="content">
        {activeTab === 'groups' && (
          <div className="customer-groups">
            <h3>客户群列表</h3>
            {loading ? (
              <div className="loading">加载中...</div>
            ) : customerGroups.length > 0 ? (
              <div className="groups-grid">
                {customerGroups.map((group) => (
                  <div key={group.id} className="group-card">
                    <div className="group-header">
                      <h4>{group.group_name}</h4>
                      <span className={`status-badge ${group.status}`}>
                        {group.status}
                      </span>
                    </div>
                    <div className="group-info">
                      <div className="info-item">
                        <span className="label">类型:</span>
                        <span>{group.group_type}</span>
                      </div>
                      <div className="info-item">
                        <span className="label">平台:</span>
                        <span>{group.platform}</span>
                      </div>
                      <div className="info-item">
                        <span className="label">成员数:</span>
                        <span>{group.member_count}</span>
                      </div>
                      <div className="info-item">
                        <span className="label">创建时间:</span>
                        <span>{new Date(group.created_at).toLocaleDateString('zh-CN')}</span>
                      </div>
                    </div>
                    {group.verification_proof && (
                      <div className="verification-proof">
                        <span className="label">验证凭证:</span>
                        <a href={group.verification_proof} target="_blank" rel="noopener noreferrer">
                          查看凭证
                        </a>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <p>暂无客户群记录</p>
                <button className="btn-primary" onClick={() => setShowGroupModal(true)}>
                  开始登记
                </button>
              </div>
            )}
          </div>
        )}

        {activeTab === 'referrals' && (
          <div className="referrals">
            <h3>推荐记录</h3>
            {referrals.length > 0 ? (
              <div className="referrals-list">
                {referrals.map((referral) => (
                  <div key={referral.id} className="referral-card">
                    <div className="referral-header">
                      <h4>推荐码: {referral.referral_code}</h4>
                      <span className={`status-badge ${referral.status}`}>
                        {referral.status}
                      </span>
                    </div>
                    <div className="referral-info">
                      <div className="info-item">
                        <span className="label">推荐商家ID:</span>
                        <span>{referral.referee_merchant_id}</span>
                      </div>
                      <div className="info-item">
                        <span className="label">奖励:</span>
                        <span className="reward">
                          {referral.reward_contribution} 贡献值 + {referral.reward_lingzhi} 灵值
                        </span>
                      </div>
                      {referral.confirmed_at && (
                        <div className="info-item">
                          <span className="label">确认时间:</span>
                          <span>{new Date(referral.confirmed_at).toLocaleString('zh-CN')}</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <p>暂无推荐记录</p>
                <button className="btn-primary" onClick={() => setShowReferralModal(true)}>
                  开始推荐
                </button>
              </div>
            )}
          </div>
        )}

        {activeTab === 'coupons' && (
          <div className="coupon-verifications">
            <h3>优惠券核销记录</h3>
            {couponVerifications.length > 0 ? (
              <div className="verifications-list">
                {couponVerifications.map((verification) => (
                  <div key={verification.id} className="verification-card">
                    <div className="verification-header">
                      <h4>优惠券: {verification.coupon_code}</h4>
                      <span className="reward">
                        +{verification.reward_contribution} 贡献值 +{verification.reward_lingzhi} 灵值
                      </span>
                    </div>
                    <div className="verification-info">
                      <div className="info-item">
                        <span className="label">用户ID:</span>
                        <span>{verification.user_id}</span>
                      </div>
                      <div className="info-item">
                        <span className="label">核销时间:</span>
                        <span>{new Date(verification.created_at).toLocaleString('zh-CN')}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <p>暂无核销记录</p>
                <button className="btn-success" onClick={() => setShowCouponModal(true)}>
                  核销优惠券
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* 客户群登记模态框 */}
      {showGroupModal && (
        <div className="modal">
          <div className="modal-content">
            <div className="modal-header">
              <h2>登记客户群</h2>
              <button className="close-btn" onClick={() => setShowGroupModal(false)}>×</button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>客户群名称 *</label>
                <input
                  type="text"
                  value={groupFormData.group_name}
                  onChange={(e) => setGroupFormData({ ...groupFormData, group_name: e.target.value })}
                  placeholder="输入客户群名称"
                />
              </div>
              <div className="form-group">
                <label>群类型 *</label>
                <select
                  value={groupFormData.group_type}
                  onChange={(e) => setGroupFormData({ ...groupFormData, group_type: e.target.value })}
                >
                  <option value="">选择类型</option>
                  <option value="wechat">微信群</option>
                  <option value="offline">线下群</option>
                  <option value="online">线上群</option>
                </select>
              </div>
              <div className="form-group">
                <label>平台 *</label>
                <input
                  type="text"
                  value={groupFormData.platform}
                  onChange={(e) => setGroupFormData({ ...groupFormData, platform: e.target.value })}
                  placeholder="例如: 微信、钉钉"
                />
              </div>
              <div className="form-group">
                <label>成员数量 *</label>
                <input
                  type="number"
                  value={groupFormData.member_count}
                  onChange={(e) => setGroupFormData({ ...groupFormData, member_count: Number(e.target.value) })}
                  placeholder="输入群成员数量"
                />
              </div>
              <div className="form-group">
                <label>验证凭证URL</label>
                <input
                  type="url"
                  value={groupFormData.verification_proof}
                  onChange={(e) => setGroupFormData({ ...groupFormData, verification_proof: e.target.value })}
                  placeholder="输入截图或证据的URL"
                />
              </div>
              <div className="info-text">
                💡 登记成功后将获得 100 贡献值 奖励（每日限5次）
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn-secondary" onClick={() => setShowGroupModal(false)}>取消</button>
              <button className="btn-primary" onClick={handleCreateGroup}>登记</button>
            </div>
          </div>
        </div>
      )}

      {/* 推荐商家模态框 */}
      {showReferralModal && (
        <div className="modal">
          <div className="modal-content">
            <div className="modal-header">
              <h2>推荐商家</h2>
              <button className="close-btn" onClick={() => setShowReferralModal(false)}>×</button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>被推荐商家ID *</label>
                <input
                  type="number"
                  value={referralFormData.referee_merchant_id}
                  onChange={(e) => setReferralFormData({ ...referralFormData, referee_merchant_id: Number(e.target.value) })}
                  placeholder="输入被推荐商家的ID"
                />
              </div>
              <div className="info-text">
                💡 推荐成功后将获得 200 贡献值 + 50 灵值 奖励
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn-secondary" onClick={() => setShowReferralModal(false)}>取消</button>
              <button className="btn-primary" onClick={handleCreateReferral}>推荐</button>
            </div>
          </div>
        </div>
      )}

      {/* 优惠券核销模态框 */}
      {showCouponModal && (
        <div className="modal">
          <div className="modal-content">
            <div className="modal-header">
              <h2>核销优惠券</h2>
              <button className="close-btn" onClick={() => setShowCouponModal(false)}>×</button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>优惠券码 *</label>
                <input
                  type="text"
                  value={couponFormData.coupon_code}
                  onChange={(e) => setCouponFormData({ ...couponFormData, coupon_code: e.target.value })}
                  placeholder="输入用户提供的优惠券码"
                />
              </div>
              <div className="info-text">
                💡 核销成功后将获得 30 贡献值 + 10 灵值 奖励（每日限50次）
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn-secondary" onClick={() => setShowCouponModal(false)}>取消</button>
              <button className="btn-success" onClick={handleVerifyCoupon}>核销</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MerchantWorkbench;

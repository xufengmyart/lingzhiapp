import React, { useState, useEffect } from 'react';

interface SacredSite {
  id: number;
  name: string;
  type: string;
  location: string;
  description: string;
  cultural_significance: string;
  images: string[];
  rating: number;
  total_reviews: number;
  visit_count: number;
  status: string;
  created_at: string;
}

interface Experience {
  id: number;
  title: string;
  type: string;
  description: string;
  duration: number;
  max_participants: number;
  price: number;
  highlights: string[];
  status: string;
}

const SacredSitesManagement: React.FC = () => {
  const [sites, setSites] = useState<SacredSite[]>([]);
  const [selectedSite, setSelectedSite] = useState<SacredSite | null>(null);
  const [experiences, setExperiences] = useState<Experience[]>([]);
  const [activeTab, setActiveTab] = useState<'sites' | 'experiences' | 'reviews'>('sites');
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    type: '',
    location: '',
    description: '',
    cultural_significance: '',
    images: [],
    opening_hours: '',
    admission_fee: 0,
    contact_info: '',
    website: ''
  });

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

  useEffect(() => {
    fetchSites();
  }, []);

  const fetchSites = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/sacred-sites`, {
        headers: {
          'X-User-ID': localStorage.getItem('userId') || ''
        }
      });
      const data = await response.json();
      setSites(data.sites || []);
    } catch (error) {
      console.error('获取圣地列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSite = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/sacred-sites`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': localStorage.getItem('userId') || ''
        },
        body: JSON.stringify(formData)
      });
      if (response.ok) {
        setShowModal(false);
        fetchSites();
      }
    } catch (error) {
      console.error('创建圣地失败:', error);
    }
  };

  const handleSelectSite = (site: SacredSite) => {
    setSelectedSite(site);
    fetchExperiences(site.id);
  };

  const fetchExperiences = async (siteId: number) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/sacred-sites/${siteId}/experiences`, {
        headers: {
          'X-User-ID': localStorage.getItem('userId') || ''
        }
      });
      const data = await response.json();
      setExperiences(data.experiences || []);
    } catch (error) {
      console.error('获取体验列表失败:', error);
    }
  };

  return (
    <div className="sacred-sites-management">
      <div className="header">
        <h1>文化圣地管理</h1>
        <button
          className="btn-primary"
          onClick={() => setShowModal(true)}
        >
          创建圣地
        </button>
      </div>

      <div className="content">
        {/* 圣地列表 */}
        <div className="sites-list">
          <div className="list-header">
            <h2>圣地列表</h2>
            <div className="filters">
              <select
                value={selectedSite?.status || ''}
                onChange={(e) => {
                  // 实现筛选逻辑
                }}
              >
                <option value="">所有状态</option>
                <option value="active">活跃</option>
                <option value="inactive">非活跃</option>
              </select>
            </div>
          </div>

          {loading ? (
            <div className="loading">加载中...</div>
          ) : (
            <div className="sites-grid">
              {sites.map((site) => (
                <div
                  key={site.id}
                  className={`site-card ${selectedSite?.id === site.id ? 'selected' : ''}`}
                  onClick={() => handleSelectSite(site)}
                >
                  {site.images.length > 0 && (
                    <img
                      src={site.images[0]}
                      alt={site.name}
                      className="site-image"
                    />
                  )}
                  <div className="site-info">
                    <h3>{site.name}</h3>
                    <p className="location">{site.location}</p>
                    <div className="stats">
                      <span className="rating">
                        ⭐ {site.rating.toFixed(1)}
                      </span>
                      <span className="reviews">
                        {site.total_reviews} 评论
                      </span>
                      <span className="visits">
                        {site.visit_count} 访问
                      </span>
                    </div>
                    <div className="status-badge">
                      {site.status}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 详情面板 */}
        {selectedSite && (
          <div className="detail-panel">
            <div className="tabs">
              <button
                className={activeTab === 'sites' ? 'active' : ''}
                onClick={() => setActiveTab('sites')}
              >
                基本信息
              </button>
              <button
                className={activeTab === 'experiences' ? 'active' : ''}
                onClick={() => setActiveTab('experiences')}
              >
                体验活动 ({experiences.length})
              </button>
              <button
                className={activeTab === 'reviews' ? 'active' : ''}
                onClick={() => setActiveTab('reviews')}
              >
                评论管理
              </button>
            </div>

            {activeTab === 'sites' && (
              <div className="site-details">
                <h2>{selectedSite.name}</h2>
                <p className="type">{selectedSite.type}</p>
                <p className="description">{selectedSite.description}</p>
                <div className="cultural-info">
                  <h3>文化意义</h3>
                  <p>{selectedSite.cultural_significance}</p>
                </div>
                {selectedSite.images.length > 0 && (
                  <div className="images-gallery">
                    <h3>图片</h3>
                    <div className="image-grid">
                      {selectedSite.images.map((img, index) => (
                        <img key={index} src={img} alt={`图片 ${index + 1}`} />
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'experiences' && (
              <div className="experiences-list">
                <div className="list-header">
                  <h3>体验活动</h3>
                  <button className="btn-primary btn-sm">添加体验</button>
                </div>
                {experiences.map((exp) => (
                  <div key={exp.id} className="experience-card">
                    <h4>{exp.title}</h4>
                    <p className="type">{exp.type}</p>
                    <p className="description">{exp.description}</p>
                    <div className="details">
                      <span>时长: {exp.duration}分钟</span>
                      <span>人数: {exp.max_participants}</span>
                      <span className="price">¥{exp.price}</span>
                    </div>
                    {exp.highlights.length > 0 && (
                      <div className="highlights">
                        <strong>亮点:</strong>
                        {exp.highlights.map((h, i) => (
                          <span key={i} className="tag">{h}</span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {activeTab === 'reviews' && (
              <div className="reviews-section">
                <h3>评论管理</h3>
                <p className="placeholder">评论功能开发中...</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* 创建圣地模态框 */}
      {showModal && (
        <div className="modal">
          <div className="modal-content">
            <div className="modal-header">
              <h2>创建文化圣地</h2>
              <button
                className="close-btn"
                onClick={() => setShowModal(false)}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>圣地名称 *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="输入圣地名称"
                />
              </div>
              <div className="form-group">
                <label>类型 *</label>
                <select
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                >
                  <option value="">选择类型</option>
                  <option value="temple">寺庙</option>
                  <option value="museum">博物馆</option>
                  <option value="park">公园</option>
                  <option value="historic_site">历史遗址</option>
                  <option value="cultural_center">文化中心</option>
                </select>
              </div>
              <div className="form-group">
                <label>地理位置 *</label>
                <input
                  type="text"
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  placeholder="输入详细地址"
                />
              </div>
              <div className="form-group">
                <label>描述 *</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="输入圣地描述"
                  rows={4}
                />
              </div>
              <div className="form-group">
                <label>文化意义</label>
                <textarea
                  value={formData.cultural_significance}
                  onChange={(e) => setFormData({ ...formData, cultural_significance: e.target.value })}
                  placeholder="输入文化意义和历史价值"
                  rows={3}
                />
              </div>
              <div className="form-group">
                <label>开放时间</label>
                <input
                  type="text"
                  value={formData.opening_hours}
                  onChange={(e) => setFormData({ ...formData, opening_hours: e.target.value })}
                  placeholder="例如: 9:00-17:00"
                />
              </div>
              <div className="form-group">
                <label>门票价格</label>
                <input
                  type="number"
                  value={formData.admission_fee}
                  onChange={(e) => setFormData({ ...formData, admission_fee: Number(e.target.value) })}
                  placeholder="0 表示免费"
                />
              </div>
              <div className="form-group">
                <label>联系方式</label>
                <input
                  type="text"
                  value={formData.contact_info}
                  onChange={(e) => setFormData({ ...formData, contact_info: e.target.value })}
                  placeholder="电话、邮箱等"
                />
              </div>
              <div className="form-group">
                <label>官方网站</label>
                <input
                  type="url"
                  value={formData.website}
                  onChange={(e) => setFormData({ ...formData, website: e.target.value })}
                  placeholder="https://..."
                />
              </div>
            </div>
            <div className="modal-footer">
              <button
                className="btn-secondary"
                onClick={() => setShowModal(false)}
              >
                取消
              </button>
              <button
                className="btn-primary"
                onClick={handleCreateSite}
              >
                创建
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SacredSitesManagement;

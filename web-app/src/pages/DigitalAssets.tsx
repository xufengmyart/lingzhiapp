import React, { useState, useEffect } from 'react';

interface Token {
  id: number;
  name: string;
  symbol: string;
  description: string;
  token_type: string;
  total_supply: number;
  circulating_supply: number;
  decimals: number;
  contract_address: string;
  status: string;
  created_at: string;
}

interface SBTTemplate {
  id: number;
  name: string;
  description: string;
  category: string;
  rarity: string;
  max_mint_count: number;
  minted_count: number;
  status: string;
}

interface UserSBT {
  id: number;
  template_id: number;
  token_id: string;
  attributes: any;
  minted_at: string;
  name: string;
  description: string;
  category: string;
  rarity: string;
}

interface AssetStats {
  token_balances: { symbol: string; balance: number }[];
  sbt_count: number;
  spirit_balance: number;
}

const DigitalAssets: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'tokens' | 'sbt' | 'my-sbt' | 'stats'>('tokens');
  const [tokens, setTokens] = useState<Token[]>([]);
  const [sbtTemplates, setSbtTemplates] = useState<SBTTemplate[]>([]);
  const [userSbt, setUserSbt] = useState<UserSBT[]>([]);
  const [stats, setStats] = useState<AssetStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [userRole, setUserRole] = useState<string>('');
  const [showTokenModal, setShowTokenModal] = useState(false);
  const [showSBTModal, setShowSBTModal] = useState(false);
  const [showMintModal, setShowMintModal] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<SBTTemplate | null>(null);

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

  useEffect(() => {
    const role = localStorage.getItem('userRole') || '';
    setUserRole(role);
    fetchTokens();
    fetchSBTTemplates();
    fetchUserSBT();
    fetchAssetStats();
  }, []);

  const fetchTokens = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/assets/tokens`);
      const data = await response.json();
      setTokens(data.tokens || []);
    } catch (error) {
      console.error('获取通证列表失败:', error);
    }
  };

  const fetchSBTTemplates = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/assets/sbt`);
      const data = await response.json();
      setSbtTemplates(data.templates || []);
    } catch (error) {
      console.error('获取SBT模板失败:', error);
    }
  };

  const fetchUserSBT = async () => {
    try {
      const userId = localStorage.getItem('userId');
      const response = await fetch(`${API_BASE_URL}/api/assets/sbt/my-sbt`, {
        headers: {
          'X-User-ID': userId || ''
        }
      });
      const data = await response.json();
      setUserSbt(data.sbts || []);
    } catch (error) {
      console.error('获取用户SBT失败:', error);
    }
  };

  const fetchAssetStats = async () => {
    try {
      const userId = localStorage.getItem('userId');
      const response = await fetch(`${API_BASE_URL}/api/assets/stats`, {
        headers: {
          'X-User-ID': userId || ''
        }
      });
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('获取资产统计失败:', error);
    }
  };

  const handleMintSBT = async (attributes: any) => {
    if (!selectedTemplate) return;
    
    try {
      const userId = localStorage.getItem('userId');
      const response = await fetch(`${API_BASE_URL}/api/assets/sbt/${selectedTemplate.id}/mint`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': userId || ''
        },
        body: JSON.stringify({ attributes })
      });
      
      if (response.ok) {
        alert('SBT铸造成功！');
        setShowMintModal(false);
        fetchUserSBT();
        fetchSBTTemplates();
        fetchAssetStats();
      } else {
        const error = await response.json();
        alert(error.error || '铸造失败');
      }
    } catch (error) {
      console.error('铸造SBT失败:', error);
    }
  };

  const getRarityColor = (rarity: string) => {
    switch (rarity) {
      case 'common': return '#9e9e9e';
      case 'rare': return '#2196f3';
      case 'epic': return '#9c27b0';
      case 'legendary': return '#ff9800';
      default: return '#9e9e9e';
    }
  };

  return (
    <div className="digital-assets">
      <div className="header">
        <h1>数字资产中心</h1>
        {userRole === 'admin' && (
          <div className="header-actions">
            <button
              className="btn-primary"
              onClick={() => setShowTokenModal(true)}
            >
              创建通证
            </button>
            <button
              className="btn-primary"
              onClick={() => setShowSBTModal(true)}
            >
              创建SBT模板
            </button>
          </div>
        )}
      </div>

      <div className="tabs">
        <button
          className={activeTab === 'tokens' ? 'active' : ''}
          onClick={() => setActiveTab('tokens')}
        >
          通证列表
        </button>
        <button
          className={activeTab === 'sbt' ? 'active' : ''}
          onClick={() => setActiveTab('sbt')}
        >
          SBT市场
        </button>
        <button
          className={activeTab === 'my-sbt' ? 'active' : ''}
          onClick={() => setActiveTab('my-sbt')}
        >
          我的SBT
        </button>
        <button
          className={activeTab === 'stats' ? 'active' : ''}
          onClick={() => setActiveTab('stats')}
        >
          资产统计
        </button>
      </div>

      <div className="content">
        {activeTab === 'tokens' && (
          <div className="tokens-list">
            {tokens.map((token) => (
              <div key={token.id} className="token-card">
                <div className="token-header">
                  <h3>{token.name}</h3>
                  <span className="symbol">{token.symbol}</span>
                </div>
                <p className="description">{token.description}</p>
                <div className="token-stats">
                  <div className="stat">
                    <span className="label">总供应量</span>
                    <span className="value">{token.total_supply.toLocaleString()}</span>
                  </div>
                  <div className="stat">
                    <span className="label">流通量</span>
                    <span className="value">{token.circulating_supply.toLocaleString()}</span>
                  </div>
                  <div className="stat">
                    <span className="label">类型</span>
                    <span className="value">{token.token_type.toUpperCase()}</span>
                  </div>
                </div>
                {token.contract_address && (
                  <div className="contract-address">
                    <span>合约地址:</span>
                    <code>{token.contract_address}</code>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {activeTab === 'sbt' && (
          <div className="sbt-templates">
            {sbtTemplates.map((template) => (
              <div key={template.id} className="sbt-card">
                <div className="sbt-header">
                  <h3>{template.name}</h3>
                  <span
                    className="rarity-badge"
                    style={{ backgroundColor: getRarityColor(template.rarity) }}
                  >
                    {template.rarity}
                  </span>
                </div>
                <p className="description">{template.description}</p>
                <div className="sbt-info">
                  <div className="info-item">
                    <span className="icon">📂</span>
                    <span>{template.category}</span>
                  </div>
                  <div className="info-item">
                    <span className="icon">🎯</span>
                    <span>{template.minted_count} / {template.max_mint_count || '∞'}</span>
                  </div>
                </div>
                <button
                  className="btn-primary"
                  onClick={() => {
                    setSelectedTemplate(template);
                    setShowMintModal(true);
                  }}
                >
                  铸造SBT
                </button>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'my-sbt' && (
          <div className="my-sbt-list">
            {userSbt.length > 0 ? (
              userSbt.map((sbt) => (
                <div key={sbt.id} className="sbt-card owned">
                  <div className="sbt-header">
                    <h3>{sbt.name}</h3>
                    <span
                      className="rarity-badge"
                      style={{ backgroundColor: getRarityColor(sbt.rarity) }}
                    >
                      {sbt.rarity}
                    </span>
                  </div>
                  <p className="description">{sbt.description}</p>
                  <div className="token-id">
                    <span>Token ID:</span>
                    <code>{sbt.token_id}</code>
                  </div>
                  {Object.keys(sbt.attributes).length > 0 && (
                    <div className="attributes">
                      <h4>属性</h4>
                      <div className="attributes-grid">
                        {Object.entries(sbt.attributes).map(([key, value]) => (
                          <div key={key} className="attribute">
                            <span className="key">{key}:</span>
                            <span className="value">{String(value)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  <div className="minted-at">
                    <span>铸造时间:</span>
                    <span>{new Date(sbt.minted_at).toLocaleString('zh-CN')}</span>
                  </div>
                </div>
              ))
            ) : (
              <div className="empty-state">
                <p>您还没有任何SBT</p>
                <button
                  className="btn-primary"
                  onClick={() => setActiveTab('sbt')}
                >
                  去铸造
                </button>
              </div>
            )}
          </div>
        )}

        {activeTab === 'stats' && stats && (
          <div className="stats-dashboard">
            <div className="stats-overview">
              <div className="stat-card large">
                <div className="stat-icon">✨</div>
                <div className="stat-info">
                  <div className="stat-value">{stats.spirit_balance.toLocaleString()}</div>
                  <div className="stat-label">灵值余额</div>
                </div>
              </div>
              <div className="stat-card large">
                <div className="stat-icon">🎴</div>
                <div className="stat-info">
                  <div className="stat-value">{stats.sbt_count}</div>
                  <div className="stat-label">SBT数量</div>
                </div>
              </div>
            </div>
            <h3>通证余额</h3>
            {stats.token_balances.length > 0 ? (
              <div className="token-balances">
                {stats.token_balances.map((balance, index) => (
                  <div key={index} className="token-balance-card">
                    <span className="symbol">{balance.symbol}</span>
                    <span className="balance">{balance.balance.toLocaleString()}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="no-data">暂无通证余额</p>
            )}
          </div>
        )}
      </div>

      {/* 铸造SBT模态框 */}
      {showMintModal && selectedTemplate && (
        <SBTMintModal
          template={selectedTemplate}
          onClose={() => {
            setShowMintModal(false);
            setSelectedTemplate(null);
          }}
          onMint={handleMintSBT}
        />
      )}
    </div>
  );
};

interface SBTMintModalProps {
  template: SBTTemplate;
  onClose: () => void;
  onMint: (attributes: any) => void;
}

const SBTMintModal: React.FC<SBTMintModalProps> = ({ template, onClose, onMint }) => {
  const [attributes, setAttributes] = useState<any>({});
  const [customAttributes, setCustomAttributes] = useState('');
  
  return (
    <div className="modal">
      <div className="modal-content">
        <div className="modal-header">
          <h2>铸造SBT - {template.name}</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        <div className="modal-body">
          <div className="template-info">
            <p className="description">{template.description}</p>
            <div className="template-meta">
              <span className="rarity">{template.rarity}</span>
              <span className="category">{template.category}</span>
            </div>
          </div>
          <div className="form-group">
            <label>自定义属性 (JSON格式)</label>
            <textarea
              value={customAttributes}
              onChange={(e) => {
                setCustomAttributes(e.target.value);
                try {
                  setAttributes(JSON.parse(e.target.value));
                } catch {}
              }}
              placeholder='{"name": "自定义名称", "level": 1}'
              rows={6}
            />
          </div>
        </div>
        <div className="modal-footer">
          <button className="btn-secondary" onClick={onClose}>取消</button>
          <button
            className="btn-primary"
            onClick={() => onMint(attributes)}
          >
            铸造
          </button>
        </div>
      </div>
    </div>
  );
};

export default DigitalAssets;

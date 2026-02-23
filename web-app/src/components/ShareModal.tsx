import React, { useState, useEffect } from 'react';
import { 
  Modal, Tabs, Button, Input, message, Row, Col, Space, Typography,
  Divider, Tag, QRCode, Tooltip
} from 'antd';
import { 
  WechatOutlined, WeiboOutlined, QqOutlined, LinkOutlined,
  CopyOutlined, ShareAltOutlined, CheckCircleOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { Title, Text, Paragraph } = Typography;
const { TabPane } = Tabs;

interface ShareModalProps {
  visible: boolean;
  onClose: () => void;
  articleId: number;
  articleTitle?: string;
  onShareSuccess?: (platform: string) => void;
}

interface ShareData {
  article_id: number;
  article_title: string;
  article_slug: string;
  referral_code: string;
  share_url: string;
  platform: string;
  share_text: string;
  qrcode?: string;
}

const ShareModal: React.FC<ShareModalProps> = ({
  visible,
  onClose,
  articleId,
  articleTitle,
  onShareSuccess,
}) => {
  const [loading, setLoading] = useState(false);
  const [shareData, setShareData] = useState<Record<string, ShareData>>({});
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState('link');

  const API_BASE = '/api';

  // 加载分享信息
  const loadShareInfo = async (type: string) => {
    if (shareData[type]) {
      return; // 已经加载过
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API_BASE}/articles/${articleId}/share`,
        {
          params: { type },
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.data.success) {
        setShareData(prev => ({
          ...prev,
          [type]: response.data.data,
        }));
      }
    } catch (error) {
      console.error('加载分享信息失败:', error);
      message.error('加载分享信息失败');
    } finally {
      setLoading(false);
    }
  };

  // 复制链接到剪贴板
  const copyLink = async (url: string) => {
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      message.success('链接已复制到剪贴板');
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      // 降级处理
      const textArea = document.createElement('textarea');
      textArea.value = url;
      document.body.appendChild(textArea);
      textArea.select();
      try {
        document.execCommand('copy');
        setCopied(true);
        message.success('链接已复制到剪贴板');
        setTimeout(() => setCopied(false), 2000);
      } catch (err) {
        message.error('复制失败，请手动复制');
      }
      document.body.removeChild(textArea);
    }
  };

  // 分享到外部平台
  const shareToPlatform = (platform: string, shareInfo: ShareData) => {
    const { share_text, share_url } = shareInfo;
    
    let shareUrl = '';
    const encodedUrl = encodeURIComponent(share_url);
    const encodedTitle = encodeURIComponent(share_text);

    switch (platform) {
      case 'wechat':
        // 微信分享使用二维码
        message.info('请使用微信扫描二维码分享');
        return;
      case 'weibo':
        shareUrl = `https://service.weibo.com/share/share.php?url=${encodedUrl}&title=${encodedTitle}`;
        break;
      case 'qq':
        shareUrl = `https://connect.qq.com/widget/shareqq/index.html?url=${encodedUrl}&title=${encodedTitle}`;
        break;
      default:
        return;
    }

    window.open(shareUrl, '_blank');
    
    if (onShareSuccess) {
      onShareSuccess(platform);
    }
    
    message.success(`已打开${platform === 'weibo' ? '微博' : platform === 'qq' ? 'QQ' : ''}分享页面`);
  };

  // 标签页变化时加载对应数据
  const handleTabChange = (key: string) => {
    setActiveTab(key);
    loadShareInfo(key);
  };

  // 初始化时加载数据
  useEffect(() => {
    if (visible && articleId) {
      loadShareInfo('link');
    }
  }, [visible, articleId]);

  const currentShareData = shareData[activeTab];

  return (
    <Modal
      title={
        <Space>
          <ShareAltOutlined />
          <span>分享文章</span>
          {articleTitle && <Text type="secondary"> - {articleTitle}</Text>}
        </Space>
      }
      open={visible}
      onCancel={onClose}
      footer={[
        <Button key="close" onClick={onClose}>
          关闭
        </Button>,
      ]}
      width={600}
    >
      {loading && !currentShareData ? (
        <div style={{ textAlign: 'center', padding: '40px 0' }}>
          加载中...
        </div>
      ) : currentShareData ? (
        <>
          <Tabs activeKey={activeTab} onChange={handleTabChange}>
            {/* 链接分享 */}
            <TabPane 
              tab={
                <Space>
                  <LinkOutlined />
                  <span>链接分享</span>
                </Space>
              } 
              key="link"
            >
              <Space direction="vertical" style={{ width: '100%' }} size="large">
                {/* 推荐关系锁定提示 */}
                <div style={{ 
                  background: '#f0f5ff', 
                  border: '1px solid #adc6ff',
                  borderRadius: '8px',
                  padding: '12px',
                }}>
                  <Space direction="vertical" size="small" style={{ width: '100%' }}>
                    <Space>
                      <CheckCircleOutlined style={{ color: '#52c41a' }} />
                      <Text strong>推荐关系已锁定</Text>
                    </Space>
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      其他用户通过此链接注册时，将自动绑定推荐关系，有效期 1 年
                    </Text>
                    <div>
                      <Tag color="blue">推荐码: {currentShareData.referral_code}</Tag>
                    </div>
                  </Space>
                </div>

                {/* 分享链接 */}
                <div>
                  <Text strong style={{ marginBottom: 8, display: 'block' }}>
                    分享链接
                  </Text>
                  <Input
                    value={currentShareData.share_url}
                    readOnly
                    suffix={
                      <Tooltip title={copied ? "已复制" : "复制链接"}>
                        <Button 
                          type="link" 
                          icon={copied ? <CheckCircleOutlined /> : <CopyOutlined />}
                          onClick={() => copyLink(currentShareData.share_url)}
                        >
                          {copied ? '已复制' : '复制'}
                        </Button>
                      </Tooltip>
                    }
                  />
                </div>

                {/* 二维码 */}
                {currentShareData.qrcode && (
                  <div style={{ textAlign: 'center' }}>
                    <Text strong style={{ marginBottom: 8, display: 'block' }}>
                      扫码分享
                    </Text>
                    <QRCode 
                      value={currentShareData.share_url}
                      size={200}
                      style={{ border: '1px solid #d9d9d9', padding: '8px', borderRadius: '8px' }}
                    />
                    <div style={{ marginTop: 8 }}>
                      <Text type="secondary" style={{ fontSize: '12px' }}>
                        扫描二维码直接访问
                      </Text>
                    </div>
                  </div>
                )}
              </Space>
            </TabPane>

            {/* 微信分享 */}
            <TabPane 
              tab={
                <Space>
                  <WechatOutlined style={{ color: '#07c160' }} />
                  <span>微信分享</span>
                </Space>
              } 
              key="wechat"
            >
              <Space direction="vertical" style={{ width: '100%' }} size="large" align="center">
                <div>
                  <Text strong style={{ marginBottom: 8, display: 'block' }}>
                    微信分享
                  </Text>
                  <Paragraph type="secondary">
                    请使用微信扫描以下二维码分享
                  </Paragraph>
                </div>
                {currentShareData.qrcode && (
                  <div style={{ textAlign: 'center' }}>
                    <QRCode 
                      value={currentShareData.share_url}
                      size={220}
                      style={{ border: '1px solid #d9d9d9', padding: '12px', borderRadius: '8px' }}
                    />
                  </div>
                )}
                <div style={{ background: '#f6ffed', border: '1px solid #b7eb8f', borderRadius: '8px', padding: '12px', width: '100%' }}>
                  <Space>
                    <CheckCircleOutlined style={{ color: '#52c41a' }} />
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      通过此链接注册的用户将自动绑定您的推荐关系
                    </Text>
                  </Space>
                </div>
              </Space>
            </TabPane>

            {/* 微博分享 */}
            <TabPane 
              tab={
                <Space>
                  <WeiboOutlined style={{ color: '#e6162d' }} />
                  <span>微博分享</span>
                </Space>
              } 
              key="weibo"
            >
              <Space direction="vertical" style={{ width: '100%' }} size="large">
                <div>
                  <Text strong style={{ marginBottom: 8, display: 'block' }}>
                    分享文案
                  </Text>
                  <Input.TextArea
                    value={currentShareData.share_text}
                    readOnly
                    rows={4}
                  />
                </div>
                <Button
                  type="primary"
                  icon={<WeiboOutlined />}
                  onClick={() => shareToPlatform('weibo', currentShareData)}
                  block
                  size="large"
                >
                  打开微博分享
                </Button>
                <div style={{ 
                  background: '#fff7e6', 
                  border: '1px solid #ffd591',
                  borderRadius: '8px',
                  padding: '12px',
                }}>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    分享后，其他用户通过链接注册将自动绑定您的推荐关系
                  </Text>
                </div>
              </Space>
            </TabPane>

            {/* QQ分享 */}
            <TabPane 
              tab={
                <Space>
                  <QqOutlined style={{ color: '#12b7f5' }} />
                  <span>QQ分享</span>
                </Space>
              } 
              key="qq"
            >
              <Space direction="vertical" style={{ width: '100%' }} size="large">
                <div>
                  <Text strong style={{ marginBottom: 8, display: 'block' }}>
                    分享文案
                  </Text>
                  <Input.TextArea
                    value={currentShareData.share_text}
                    readOnly
                    rows={4}
                  />
                </div>
                <Button
                  type="primary"
                  icon={<QqOutlined />}
                  onClick={() => shareToPlatform('qq', currentShareData)}
                  block
                  size="large"
                >
                  打开QQ分享
                </Button>
                <div style={{ 
                  background: '#e6f7ff', 
                  border: '1px solid #91d5ff',
                  borderRadius: '8px',
                  padding: '12px',
                }}>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    分享后，其他用户通过链接注册将自动绑定您的推荐关系
                  </Text>
                </div>
              </Space>
            </TabPane>
          </Tabs>
        </>
      ) : null}
    </Modal>
  );
};

export default ShareModal;

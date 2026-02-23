import React, { useState, useEffect } from 'react';
import { 
  Card, Typography, Tag, Space, Button, Divider, Row, Col, 
  Avatar, message, Spin, Empty, Tooltip, Affix
} from 'antd';
import { 
  EyeOutlined, LikeOutlined, CommentOutlined, ClockCircleOutlined,
  ShareAltOutlined, CalendarOutlined, UserOutlined, FireOutlined,
  ArrowLeftOutlined
} from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import ShareModal from '../components/ShareModal';

const { Title, Paragraph, Text } = Typography;

interface Article {
  id: number;
  title: string;
  slug: string;
  content: string;
  summary: string;
  category_id: number;
  category_name?: string;
  author_id: number;
  author_name: string;
  cover_image?: string;
  status: string;
  is_pinned: boolean;
  is_featured: boolean;
  view_count: number;
  like_count: number;
  comment_count: number;
  tags?: string;
  published_at: string;
  created_at: string;
  updated_at: string;
}

const ArticleDetail: React.FC = () => {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  
  const [article, setArticle] = useState<Article | null>(null);
  const [loading, setLoading] = useState(true);
  const [shareModalVisible, setShareModalVisible] = useState(false);
  const [liked, setLiked] = useState(false);
  const [likeLoading, setLikeLoading] = useState(false);

  const API_BASE = '/api/v9';

  // 加载文章详情
  const loadArticle = async () => {
    if (!slug) return;
    
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/news/articles/${slug}`);
      
      if (response.data.success && response.data.data) {
        setArticle(response.data.data);
      } else {
        message.error('文章不存在');
        navigate('/news');
      }
    } catch (error) {
      console.error('加载文章失败:', error);
      message.error('加载文章失败');
      navigate('/news');
    } finally {
      setLoading(false);
    }
  };

  // 点赞文章
  const handleLike = async () => {
    if (!article) return;
    
    setLikeLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API_BASE}/news/articles/${article.id}/like`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.data.success) {
        setLiked(!liked);
        setArticle(prev => prev ? {
          ...prev,
          like_count: prev.like_count + (liked ? -1 : 1)
        } : null);
        
        if (!liked) {
          message.success('点赞成功');
        }
      }
    } catch (error) {
      console.error('点赞失败:', error);
      message.error('点赞失败');
    } finally {
      setLikeLoading(false);
    }
  };

  // 打开分享弹窗
  const handleShare = () => {
    if (!article) return;
    setShareModalVisible(true);
  };

  // 分享成功回调
  const handleShareSuccess = (platform: string) => {
    message.success(`成功分享到${platform === 'weibo' ? '微博' : platform === 'qq' ? 'QQ' : '微信'}`);
  };

  useEffect(() => {
    loadArticle();
  }, [slug]);

  if (loading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }

  if (!article) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <Empty description="文章不存在" />
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f0f2f5', padding: '24px 0' }}>
      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 24px' }}>
        {/* 返回按钮 */}
        <Button 
          icon={<ArrowLeftOutlined />} 
          onClick={() => navigate(-1)}
          style={{ marginBottom: 16 }}
        >
          返回
        </Button>

        <Row gutter={24}>
          {/* 左侧文章内容 */}
          <Col xs={24} md={18}>
            <Card>
              {/* 文章头部 */}
              <div style={{ marginBottom: 24 }}>
                {/* 标题 */}
                <Title level={1} style={{ marginBottom: 16 }}>
                  {article.is_pinned && (
                    <Tag color="gold" style={{ marginRight: 8 }}>置顶</Tag>
                  )}
                  {article.is_featured && (
                    <Tag color="purple" style={{ marginRight: 8 }}>推荐</Tag>
                  )}
                  {article.title}
                </Title>

                {/* 文章信息 */}
                <Space size="large" wrap>
                  <Space>
                    <UserOutlined />
                    <Text type="secondary">{article.author_name}</Text>
                  </Space>
                  <Space>
                    <CalendarOutlined />
                    <Text type="secondary">
                      {article.published_at || article.created_at}
                    </Text>
                  </Space>
                  <Space>
                    <EyeOutlined />
                    <Text type="secondary">{article.view_count} 次浏览</Text>
                  </Space>
                  <Space>
                    <LikeOutlined />
                    <Text type="secondary">{article.like_count} 次点赞</Text>
                  </Space>
                  <Space>
                    <CommentOutlined />
                    <Text type="secondary">{article.comment_count} 条评论</Text>
                  </Space>
                </Space>

                {/* 分类标签 */}
                {article.category_name && (
                  <div style={{ marginTop: 12 }}>
                    <Tag color="blue">{article.category_name}</Tag>
                  </div>
                )}

                {/* 标签 */}
                {article.tags && (
                  <div style={{ marginTop: 12 }}>
                    {article.tags.split(',').map((tag, index) => (
                      <Tag key={index} style={{ cursor: 'pointer' }}>
                        #{tag.trim()}
                      </Tag>
                    ))}
                  </div>
                )}
              </div>

              <Divider />

              {/* 封面图片 */}
              {article.cover_image && (
                <div style={{ marginBottom: 24 }}>
                  <img
                    src={article.cover_image}
                    alt={article.title}
                    style={{
                      width: '100%',
                      maxHeight: 400,
                      objectFit: 'cover',
                      borderRadius: 8,
                    }}
                  />
                </div>
              )}

              {/* 摘要 */}
              {article.summary && (
                <div style={{ 
                  background: '#f5f5f5', 
                  padding: '16px', 
                  borderRadius: 8, 
                  marginBottom: 24 
                }}>
                  <Paragraph type="secondary" style={{ marginBottom: 0, fontSize: 16 }}>
                    {article.summary}
                  </Paragraph>
                </div>
              )}

              {/* 文章内容 */}
              <div 
                className="article-content"
                dangerouslySetInnerHTML={{ __html: article.content }}
                style={{ 
                  lineHeight: 1.8, 
                  fontSize: 16,
                  color: '#333'
                }}
              />

              <Divider />

              {/* 底部操作栏 */}
              <Affix offsetBottom={0}>
                <Card size="small" style={{ borderRadius: 0 }}>
                  <Row justify="space-between" align="middle">
                    <Col>
                      <Space size="middle">
                        <Tooltip title="点赞">
                          <Button
                            type={liked ? "primary" : "default"}
                            icon={<LikeOutlined />}
                            onClick={handleLike}
                            loading={likeLoading}
                          >
                            {article.like_count + (liked ? 1 : 0)}
                          </Button>
                        </Tooltip>
                        <Tooltip title="评论">
                          <Button icon={<CommentOutlined />}>
                            {article.comment_count}
                          </Button>
                        </Tooltip>
                      </Space>
                    </Col>
                    <Col>
                      <Space size="middle">
                        <Tooltip title="分享文章">
                          <Button
                            type="primary"
                            icon={<ShareAltOutlined />}
                            onClick={handleShare}
                          >
                            分享
                          </Button>
                        </Tooltip>
                      </Space>
                    </Col>
                  </Row>
                </Card>
              </Affix>
            </Card>
          </Col>

          {/* 右侧侧边栏 */}
          <Col xs={24} md={6}>
            <Affix offsetTop={80}>
              <Space direction="vertical" style={{ width: '100%' }} size="middle">
                {/* 快捷操作 */}
                <Card title="快捷操作" size="small">
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <Button
                      block
                      icon={<ShareAltOutlined />}
                      onClick={handleShare}
                    >
                      分享文章
                    </Button>
                  </Space>
                </Card>

                {/* 推荐关系提示 */}
                <Card 
                  size="small"
                  style={{
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    color: 'white',
                    border: 'none',
                  }}
                >
                  <div style={{ textAlign: 'center' }}>
                    <Title level={4} style={{ color: 'white', marginBottom: 8 }}>
                      <FireOutlined /> 热门文章
                    </Title>
                    <Paragraph style={{ color: 'rgba(255,255,255,0.9)', marginBottom: 0 }}>
                      分享文章，邀请好友注册即可获得推荐奖励
                    </Paragraph>
                  </div>
                </Card>
              </Space>
            </Affix>
          </Col>
        </Row>
      </div>

      {/* 分享弹窗 */}
      <ShareModal
        visible={shareModalVisible}
        onClose={() => setShareModalVisible(false)}
        articleId={article.id}
        articleTitle={article.title}
        onShareSuccess={handleShareSuccess}
      />
    </div>
  );
};

export default ArticleDetail;

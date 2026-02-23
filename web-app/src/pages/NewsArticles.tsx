import React, { useState, useEffect } from 'react';
import { 
  Card, List, Tag, Input, Select, Button, Modal, Typography, Space, 
  Divider, Empty, Pagination, Spin, Tooltip, message, Row, Col
} from 'antd';
import { 
  SearchOutlined, FilterOutlined, EyeOutlined, MessageOutlined, 
  LikeOutlined, ClockCircleOutlined, FireOutlined, StarOutlined,
  ArrowLeftOutlined, ReloadOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { Title, Paragraph, Text } = Typography;
const { Option } = Select;
const { TextArea } = Input;

interface Article {
  id: number;
  title: string;
  slug: string;
  summary: string;
  content: string;
  category?: string;
  categoryName?: string;
  categoryId?: number;
  publishedAt: string;
  isPinned: boolean;
  isFeatured: boolean;
  viewCount: number;
  likeCount: number;
  commentCount: number;
  coverImage?: string;
}

interface Comment {
  id: number;
  content: string;
  author: string;
  createdAt: string;
  likeCount: number;
}

const NewsArticles: React.FC = () => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchKeyword, setSearchKeyword] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<number | null>(null);
  const [sortOrder, setSortOrder] = useState<'latest' | 'popular' | 'pinned'>('latest');
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 });
  const [categories, setCategories] = useState<Array<{id: number, name: string}>>([]);
  
  // 文章详情相关
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  
  // 评论相关
  const [comments, setComments] = useState<Comment[]>([]);
  const [commentLoading, setCommentLoading] = useState(false);
  const [newComment, setNewComment] = useState('');
  const [submittingComment, setSubmittingComment] = useState(false);

  const API_BASE = '/api/v9';

  // 加载新闻文章
  const loadArticles = async () => {
    setLoading(true);
    try {
      const params: any = {
        page: pagination.current,
        page_size: pagination.pageSize,
      };
      
      if (searchKeyword) params.keyword = searchKeyword;
      if (categoryFilter) params.category_id = categoryFilter;
      if (sortOrder === 'popular') params.sort = 'popular';
      if (sortOrder === 'pinned') params.pinned_only = true;

      const response = await axios.get(`${API_BASE}/news/articles`, { params });
      
      if (response.data.success) {
        setArticles(response.data.data);
        setPagination(prev => ({
          ...prev,
          total: response.data.pagination?.total || response.data.data.length
        }));
      }
    } catch (error) {
      message.error('加载新闻失败');
      console.error('加载新闻失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 加载分类
  const loadCategories = async () => {
    try {
      const response = await axios.get(`${API_BASE}/news/categories`);
      if (response.data.success) {
        setCategories(response.data.data || []);
      }
    } catch (error) {
      console.error('加载分类失败:', error);
    }
  };

  // 打开文章详情
  const openArticleDetail = async (article: Article) => {
    setSelectedArticle(article);
    setDetailModalVisible(true);
    await loadComments(article.id);
  };

  // 加载评论
  const loadComments = async (articleId: number) => {
    setCommentLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/news/articles/${articleId}/comments`);
      if (response.data.success) {
        setComments(response.data.data || []);
      }
    } catch (error) {
      console.error('加载评论失败:', error);
    } finally {
      setCommentLoading(false);
    }
  };

  // 提交评论
  const submitComment = async () => {
    if (!newComment.trim()) {
      message.warning('请输入评论内容');
      return;
    }
    
    if (!selectedArticle) return;

    setSubmittingComment(true);
    try {
      const response = await axios.post(`${API_BASE}/news/articles/${selectedArticle.id}/comments`, {
        content: newComment,
      });
      
      if (response.data.success) {
        message.success('评论发布成功');
        setNewComment('');
        await loadComments(selectedArticle.id);
        await loadArticles(); // 刷新评论数
      } else {
        message.error(response.data.message || '评论发布失败');
      }
    } catch (error: any) {
      message.error(error.response?.data?.message || '评论发布失败');
    } finally {
      setSubmittingComment(false);
    }
  };

  // 点赞文章
  const likeArticle = async (articleId: number) => {
    try {
      await axios.post(`${API_BASE}/news/articles/${articleId}/like`);
      message.success('点赞成功');
      await loadArticles();
    } catch (error) {
      message.error('点赞失败');
    }
  };

  // 应用搜索和过滤
  const handleSearch = () => {
    setPagination(prev => ({ ...prev, current: 1 }));
    loadArticles();
  };

  // 重置筛选
  const resetFilters = () => {
    setSearchKeyword('');
    setCategoryFilter(null);
    setSortOrder('latest');
    setPagination(prev => ({ ...prev, current: 1 }));
    setTimeout(loadArticles, 100);
  };

  useEffect(() => {
    loadCategories();
    loadArticles();
  }, [pagination.current, pagination.pageSize, sortOrder]);

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ marginBottom: '24px' }}>
        <Title level={2}>
          <StarOutlined style={{ color: '#faad14' }} /> 系统新闻
        </Title>
      </div>

      {/* 搜索和过滤栏 */}
      <Card style={{ marginBottom: '24px' }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} md={8}>
            <Input
              placeholder="搜索新闻标题或内容"
              prefix={<SearchOutlined />}
              value={searchKeyword}
              onChange={(e) => setSearchKeyword(e.target.value)}
              onPressEnter={handleSearch}
              allowClear
            />
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Select
              placeholder="选择分类"
              value={categoryFilter}
              onChange={setCategoryFilter}
              allowClear
              style={{ width: '100%' }}
              suffixIcon={<FilterOutlined />}
            >
              {categories.map(cat => (
                <Option key={cat.id} value={cat.id}>{cat.name}</Option>
              ))}
            </Select>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Select
              placeholder="排序方式"
              value={sortOrder}
              onChange={setSortOrder}
              style={{ width: '100%' }}
            >
              <Option value="latest">最新发布</Option>
              <Option value="popular">热门排行</Option>
              <Option value="pinned">置顶优先</Option>
            </Select>
          </Col>
          <Col xs={24} sm={12} md={4}>
            <Space>
              <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
                搜索
              </Button>
              <Button icon={<ReloadOutlined />} onClick={resetFilters}>
                重置
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 新闻列表 */}
      <Spin spinning={loading}>
        {articles.length === 0 ? (
          <Empty description="暂无新闻" />
        ) : (
          <List
            dataSource={articles}
            renderItem={(article) => (
              <Card 
                key={article.id}
                style={{ marginBottom: '16px' }}
                hoverable
                onClick={() => openArticleDetail(article)}
              >
                <List.Item>
                  <List.Item.Meta
                    title={
                      <Space>
                        {article.isPinned && <Tag color="red">置顶</Tag>}
                        {article.isFeatured && <Tag color="gold">精选</Tag>}
                        {article.categoryName && <Tag color="blue">{article.categoryName}</Tag>}
                        <span style={{ fontSize: '16px', fontWeight: 500 }}>{article.title}</span>
                      </Space>
                    }
                    description={
                      <Space direction="vertical" size="small">
                        <Text type="secondary">{article.summary}</Text>
                        <Space split={<Divider type="vertical" />}>
                          <Text type="secondary">
                            <ClockCircleOutlined /> {new Date(article.publishedAt).toLocaleString('zh-CN')}
                          </Text>
                          <Text type="secondary">
                            <EyeOutlined /> {article.viewCount}
                          </Text>
                          <Text type="secondary">
                            <LikeOutlined /> {article.likeCount}
                          </Text>
                          <Text type="secondary">
                            <MessageOutlined /> {article.commentCount}
                          </Text>
                        </Space>
                      </Space>
                    }
                  />
                </List.Item>
              </Card>
            )}
          />
        )}
      </Spin>

      {/* 分页 */}
      {articles.length > 0 && (
        <div style={{ marginTop: '24px', textAlign: 'center' }}>
          <Pagination
            current={pagination.current}
            pageSize={pagination.pageSize}
            total={pagination.total}
            onChange={(page, pageSize) => {
              setPagination({ current: page, pageSize: pageSize || 10, total: pagination.total });
            }}
            showSizeChanger
            showTotal={(total) => `共 ${total} 条`}
          />
        </div>
      )}

      {/* 文章详情弹窗 */}
      <Modal
        title={
          <Space>
            {selectedArticle?.isPinned && <Tag color="red">置顶</Tag>}
            {selectedArticle?.isFeatured && <Tag color="gold">精选</Tag>}
            <span>{selectedArticle?.title}</span>
          </Space>
        }
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={[
          <Button key="back" onClick={() => setDetailModalVisible(false)}>
            关闭
          </Button>,
          <Button 
            key="like" 
            type="primary" 
            icon={<LikeOutlined />}
            onClick={() => selectedArticle && likeArticle(selectedArticle.id)}
          >
            点赞
          </Button>,
        ]}
        width={800}
      >
        {selectedArticle && (
          <div>
            <Divider />
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <div>
                <Text type="secondary">
                  <ClockCircleOutlined /> 发布时间：{new Date(selectedArticle.publishedAt).toLocaleString('zh-CN')}
                </Text>
                <br />
                <Text type="secondary">
                  <EyeOutlined /> 阅读：{selectedArticle.viewCount} | 
                  <LikeOutlined /> 点赞：{selectedArticle.likeCount} | 
                  <MessageOutlined /> 评论：{selectedArticle.commentCount}
                </Text>
              </div>
              
              <div>
                <Title level={4}>内容摘要</Title>
                <Paragraph>{selectedArticle.summary}</Paragraph>
              </div>

              {/* 评论区域 */}
              <div>
                <Title level={4}>
                  <MessageOutlined /> 评论 ({comments.length})
                </Title>
                
                {/* 发表评论 */}
                <div style={{ marginBottom: '16px' }}>
                  <TextArea
                    rows={3}
                    placeholder="发表你的评论..."
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    maxLength={500}
                    showCount
                  />
                  <div style={{ marginTop: '8px', textAlign: 'right' }}>
                    <Button 
                      type="primary" 
                      onClick={submitComment}
                      loading={submittingComment}
                    >
                      发表评论
                    </Button>
                  </div>
                </div>

                {/* 评论列表 */}
                <Spin spinning={commentLoading}>
                  {comments.length === 0 ? (
                    <Empty description="暂无评论，快来发表第一条评论吧！" />
                  ) : (
                    <List
                      dataSource={comments}
                      renderItem={(comment) => (
                        <List.Item key={comment.id}>
                          <List.Item.Meta
                            title={
                              <Space>
                                <Text strong>{comment.author}</Text>
                                <Text type="secondary" style={{ fontSize: '12px' }}>
                                  {new Date(comment.createdAt).toLocaleString('zh-CN')}
                                </Text>
                              </Space>
                            }
                            description={
                              <div>
                                <Paragraph>{comment.content}</Paragraph>
                                <Space>
                                  <Tooltip title="点赞">
                                    <Button 
                                      type="text" 
                                      icon={<LikeOutlined />} 
                                      size="small"
                                    >
                                      {comment.likeCount}
                                    </Button>
                                  </Tooltip>
                                </Space>
                              </div>
                            }
                          />
                        </List.Item>
                      )}
                    />
                  )}
                </Spin>
              </div>
            </Space>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default NewsArticles;

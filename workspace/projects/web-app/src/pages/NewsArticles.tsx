import React, { useState, useEffect } from 'react';
import { Card, List, Tag, Typography, Spin, Empty, Pagination, Space, Button, Modal } from 'antd';
import { EyeOutlined, LikeOutlined, CommentOutlined, CalendarOutlined, FireOutlined } from '@ant-design/icons';

const { Title, Paragraph, Text } = Typography;

interface Article {
  id: number;
  title: string;
  slug: string;
  summary: string;
  categoryId: number | null;
  categoryName: string | null;
  coverImage: string | null;
  isFeatured: boolean;
  isPinned: boolean;
  viewCount: number;
  likeCount: number;
  commentCount: number;
  publishedAt: string;
  createdAt: string;
}

interface NewsResponse {
  success: boolean;
  message: string;
  data: Article[];
  total: number;
  page: number;
  page_size: number;
}

const NewsArticles: React.FC = () => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [total, setTotal] = useState(0);
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null);
  const [modalVisible, setModalVisible] = useState(false);

  // 获取文章列表
  const fetchArticles = async (page: number = 1, page_size: number = 10) => {
    setLoading(true);
    try {
      const response = await fetch(
        `/api/v9/news/articles?page=${page}&page_size=${page_size}`
      );
      const data: NewsResponse = await response.json();
      if (data.success) {
        setArticles(data.data);
        setTotal(data.total);
        setCurrentPage(data.page);
        setPageSize(data.page_size);
      }
    } catch (error) {
      console.error('获取新闻失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 获取文章详情
  const fetchArticleDetail = async (slug: string) => {
    try {
      const response = await fetch(`/api/v9/news/articles/${slug}`);
      const data = await response.json();
      if (data.success) {
        setSelectedArticle(data.data);
        setModalVisible(true);
      }
    } catch (error) {
      console.error('获取文章详情失败:', error);
    }
  };

  useEffect(() => {
    fetchArticles();
  }, []);

  // 处理文章点击
  const handleArticleClick = (article: Article) => {
    fetchArticleDetail(article.slug);
  };

  // 处理分页变化
  const handlePageChange = (page: number, pageSize?: number) => {
    fetchArticles(page, pageSize);
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <Title level={2} style={{ textAlign: 'center', marginBottom: '32px' }}>
        📰 灵值生态园新闻动态
      </Title>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '48px' }}>
          <Spin size="large" />
        </div>
      ) : (
        <>
          {/* 置顶和精选文章 */}
          {(articles.filter(a => a.isPinned || a.isFeatured).length > 0) && (
            <div style={{ marginBottom: '24px' }}>
              <Title level={4}>🔥 重要公告</Title>
              <List
                grid={{ gutter: 16, xs: 1, sm: 1, md: 2, lg: 2, xl: 2 }}
                dataSource={articles.filter(a => a.isPinned || a.isFeatured)}
                renderItem={(article) => (
                  <List.Item>
                    <Card
                      hoverable
                      style={{ height: '100%', borderColor: '#1890ff' }}
                      bodyStyle={{ padding: '16px' }}
                      onClick={() => handleArticleClick(article)}
                    >
                      <Space direction="vertical" size="small" style={{ width: '100%' }}>
                        <Space>
                          {article.isPinned && <Tag color="red">置顶</Tag>}
                          {article.isFeatured && <Tag color="orange">精选</Tag>}
                          {article.categoryName && (
                            <Tag color="blue">{article.categoryName}</Tag>
                          )}
                        </Space>
                        <Text strong style={{ fontSize: '16px' }}>
                          {article.title}
                        </Text>
                        <Paragraph
                          ellipsis={{ rows: 2 }}
                          style={{ margin: 0, color: '#666' }}
                        >
                          {article.summary}
                        </Paragraph>
                        <Space>
                          <Text type="secondary">
                            <CalendarOutlined /> {article.publishedAt?.split(' ')[0]}
                          </Text>
                          <Text type="secondary">
                            <EyeOutlined /> {article.viewCount}
                          </Text>
                        </Space>
                      </Space>
                    </Card>
                  </List.Item>
                )}
              />
            </div>
          )}

          {/* 全部文章 */}
          <div>
            <Title level={4}>📝 全部文章</Title>
            {articles.length === 0 ? (
              <Empty description="暂无新闻" />
            ) : (
              <>
                <List
                  dataSource={articles}
                  renderItem={(article) => (
                    <List.Item
                      key={article.id}
                      onClick={() => handleArticleClick(article)}
                      style={{
                        cursor: 'pointer',
                        padding: '16px 0',
                        borderBottom: '1px solid #f0f0f0'
                      }}
                    >
                      <List.Item.Meta
                        title={
                          <Space>
                            <Text
                              strong
                              style={{ fontSize: '16px', color: '#1890ff' }}
                            >
                              {article.title}
                            </Text>
                            {article.isPinned && <Tag color="red">置顶</Tag>}
                            {article.isFeatured && <Tag color="orange">精选</Tag>}
                            {article.categoryName && (
                              <Tag color="blue">{article.categoryName}</Tag>
                            )}
                          </Space>
                        }
                        description={
                          <Space direction="vertical" size="small" style={{ width: '100%' }}>
                            <Paragraph
                              ellipsis={{ rows: 2 }}
                              style={{ margin: 0, color: '#666' }}
                            >
                              {article.summary}
                            </Paragraph>
                            <Space>
                              <Text type="secondary" style={{ fontSize: '12px' }}>
                                <CalendarOutlined /> {article.publishedAt?.split(' ')[0]}
                              </Text>
                              <Text type="secondary" style={{ fontSize: '12px' }}>
                                <EyeOutlined /> {article.viewCount} 阅读
                              </Text>
                              <Text type="secondary" style={{ fontSize: '12px' }}>
                                <LikeOutlined /> {article.likeCount} 点赞
                              </Text>
                              <Text type="secondary" style={{ fontSize: '12px' }}>
                                <CommentOutlined /> {article.commentCount} 评论
                              </Text>
                            </Space>
                          </Space>
                        }
                      />
                    </List.Item>
                  )}
                />
                {total > pageSize && (
                  <div style={{ textAlign: 'center', marginTop: '24px' }}>
                    <Pagination
                      current={currentPage}
                      pageSize={pageSize}
                      total={total}
                      onChange={handlePageChange}
                      showSizeChanger
                      showQuickJumper
                      showTotal={(total) => `共 ${total} 篇`}
                    />
                  </div>
                )}
              </>
            )}
          </div>
        </>
      )}

      {/* 文章详情弹窗 */}
      <Modal
        title={selectedArticle?.title}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={[
          <Button key="close" type="primary" onClick={() => setModalVisible(false)}>
            关闭
          </Button>
        ]}
        width={800}
      >
        {selectedArticle && (
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            <Space>
              {selectedArticle.isPinned && <Tag color="red">置顶</Tag>}
              {selectedArticle.isFeatured && <Tag color="orange">精选</Tag>}
              {selectedArticle.categoryName && (
                <Tag color="blue">{selectedArticle.categoryName}</Tag>
              )}
            </Space>
            <Paragraph style={{ fontSize: '14px', color: '#666' }}>
              发布时间: {selectedArticle.publishedAt}
            </Paragraph>
            <div
              style={{
                padding: '24px',
                background: '#f9f9f9',
                borderRadius: '8px',
                lineHeight: '1.8'
              }}
              dangerouslySetInnerHTML={{ __html: selectedArticle.summary }}
            />
            <Space style={{ marginTop: '16px' }}>
              <Text type="secondary">
                <EyeOutlined /> 阅读: {selectedArticle.viewCount}
              </Text>
              <Text type="secondary">
                <LikeOutlined /> 点赞: {selectedArticle.likeCount}
              </Text>
              <Text type="secondary">
                <CommentOutlined /> 评论: {selectedArticle.commentCount}
              </Text>
            </Space>
          </Space>
        )}
      </Modal>
    </div>
  );
};

export default NewsArticles;

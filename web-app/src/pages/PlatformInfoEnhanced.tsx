import React, { useState, useEffect } from 'react';
import { 
  Card, List, Tag, Input, Select, Button, Typography, Space, 
  Divider, Empty, Pagination, Spin, Alert, Badge, message, Drawer,
  Descriptions, Tooltip, Row, Col, Comment, Avatar, Modal,
  notification, Dropdown
} from 'antd';
import { 
  SearchOutlined, EyeOutlined, LikeOutlined, ClockCircleOutlined, 
  BellOutlined, InfoCircleOutlined, ExclamationCircleOutlined,
  ThunderboltOutlined, ReloadOutlined, MessageOutlined,
  ShareAltOutlined, CheckCircleOutlined, StarFilled, StarOutlined,
  SubscribeOutlined, SendOutlined, WechatOutlined, WeiboOutlined,
  QqOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { Title, Paragraph, Text } = Typography;
const { Option } = Select;
const { TextArea } = Input;

interface PlatformInfo {
  id: number;
  title: string;
  slug: string;
  summary: string;
  content?: string;
  coverImage?: string;
  infoType: string;
  importanceLevel: number;
  effectiveDate?: string;
  expiryDate?: string;
  isExpired?: boolean;
  isRead?: boolean;
  viewCount: number;
  likeCount: number;
  commentCount: number;
  publishedAt: string;
  isPinned: boolean;
  isLiked?: boolean;
  createdAt: string;
  updatedAt: string;
}

interface Comment {
  id: number;
  userId: number;
  username: string;
  nickname: string;
  content: string;
  likeCount: number;
  replyCount: number;
  replies: any[];
  createdAt: string;
}

const PlatformInfoEnhanced = () => {
  const [loading, setLoading] = useState(false);
  const [infoList, setInfoList] = useState<PlatformInfo[]>([]);
  const [selectedInfo, setSelectedInfo] = useState<PlatformInfo | null>(null);
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  
  const [pagination, setPagination] = useState({ current: 1, pageSize: 20, total: 0 });
  const [searchKeyword, setSearchKeyword] = useState('');
  const [infoTypeFilter, setInfoTypeFilter] = useState<string>('');
  const [importantNotices, setImportantNotices] = useState<PlatformInfo[]>([]);
  
  // 评论相关
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState('');
  const [commentLoading, setCommentLoading] = useState(false);
  
  // 订阅相关
  const [subscriptions, setSubscriptions] = useState<any[]>([]);

  const API_BASE = '/api/v9';
  const token = localStorage.getItem('token');

  // 加载平台信息列表
  const loadPlatformInfo = async () => {
    setLoading(true);
    try {
      const params: any = {
        page: pagination.current,
        page_size: pagination.pageSize,
      };
      if (searchKeyword) params.keyword = searchKeyword;
      if (infoTypeFilter) params.info_type = infoTypeFilter;

      const response = await axios.get(`${API_BASE}/platform-info`, { params });
      
      if (response.data.success) {
        setInfoList(response.data.data);
        setPagination(prev => ({
          ...prev,
          total: response.data.pagination?.total || response.data.data.length
        }));
      }
    } catch (error) {
      message.error('加载平台信息失败');
    } finally {
      setLoading(false);
    }
  };

  // 加载重要通知
  const loadImportantNotices = async () => {
    try {
      const response = await axios.get(`${API_BASE}/platform-info/important?limit=5`);
      if (response.data.success) {
        setImportantNotices(response.data.data);
      }
    } catch (error) {
      console.error('加载重要通知失败:', error);
    }
  };

  // 加载未读数量
  const loadUnreadCount = async () => {
    try {
      const response = await axios.get(`${API_BASE}/platform-info/unread-count`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.data.success) {
        setUnreadCount(response.data.data.unread_count);
      }
    } catch (error) {
      console.error('加载未读数量失败:', error);
    }
  };

  // 加载评论
  const loadComments = async (infoId: number) => {
    try {
      const response = await axios.get(`${API_BASE}/platform-info/${infoId}/comments`);
      if (response.data.success) {
        setComments(response.data.data);
      }
    } catch (error) {
      message.error('加载评论失败');
    }
  };

  // 加载订阅
  const loadSubscriptions = async () => {
    try {
      const response = await axios.get(`${API_BASE}/platform-info/subscriptions`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.data.success) {
        setSubscriptions(response.data.data);
      }
    } catch (error) {
      console.error('加载订阅失败:', error);
    }
  };

  // 标记已读
  const markAsRead = async (infoId: number) => {
    try {
      await axios.post(`${API_BASE}/platform-info/${infoId}/read`, {}, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('标记已读失败:', error);
    }
  };

  // 点赞
  const handleLike = async (infoId: number) => {
    try {
      await axios.post(`${API_BASE}/platform-info/${infoId}/like`, {}, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      message.success('点赞成功');
      loadPlatformInfo();
    } catch (error) {
      message.error('点赞失败');
    }
  };

  // 评论
  const handleComment = async () => {
    if (!newComment.trim()) {
      message.warning('请输入评论内容');
      return;
    }
    
    setCommentLoading(true);
    try {
      await axios.post(`${API_BASE}/platform-info/${selectedInfo!.id}/comments`, {
        content: newComment
      }, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      message.success('评论成功');
      setNewComment('');
      loadComments(selectedInfo!.id);
      loadPlatformInfo();
    } catch (error) {
      message.error('评论失败');
    } finally {
      setCommentLoading(false);
    }
  };

  // 分享
  const handleShare = async (platform: string) => {
    try {
      const response = await axios.post(`${API_BASE}/platform-info/${selectedInfo!.id}/share`, {
        platform
      }, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.data.success) {
        const shareUrl = response.data.data.shareUrl;
        
        if (navigator.clipboard) {
          await navigator.clipboard.writeText(shareUrl);
          message.success('分享链接已复制到剪贴板');
        } else {
          Modal.info({
            title: '分享链接',
            content: shareUrl,
          });
        }
      }
    } catch (error) {
      message.error('分享失败');
    }
  };

  // 订阅
  const handleSubscribe = async (infoType: string) => {
    try {
      await axios.post(`${API_BASE}/platform-info/subscribe`, {
        info_type: infoType
      }, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      message.success('订阅成功');
      loadSubscriptions();
    } catch (error) {
      message.error('订阅失败');
    }
  };

  // 加载详情
  const loadDetail = async (id: number) => {
    try {
      const response = await axios.get(`${API_BASE}/platform-info/${id}`);
      if (response.data.success) {
        setSelectedInfo(response.data.data);
        setDrawerVisible(true);
        markAsRead(id);
        loadComments(id);
      }
    } catch (error) {
      message.error('加载详情失败');
    }
  };

  useEffect(() => {
    loadPlatformInfo();
    loadImportantNotices();
    loadUnreadCount();
    loadSubscriptions();
  }, [pagination.current, pagination.pageSize, infoTypeFilter]);

  const getInfoTypeColor = (type: string) => {
    const colorMap = {
      'general': 'default',
      'update': 'blue',
      'notice': 'orange',
      'warning': 'red',
    };
    return colorMap[type] || 'default';
  };

  const getInfoTypeLabel = (type: string) => {
    const labelMap = {
      'general': '通用',
      'update': '更新',
      'notice': '通知',
      'warning': '警告',
    };
    return labelMap[type] || type;
  };

  const getImportanceIcon = (level: number) => {
    if (level >= 3) return <ThunderboltOutlined style={{ color: '#ff4d4f' }} />;
    if (level >= 2) return <ExclamationCircleOutlined style={{ color: '#faad14' }} />;
    return <InfoCircleOutlined style={{ color: '#52c41a' }} />;
  };

  // 分享菜单
  const shareMenu = (
    <Menu>
      <Menu.Item key="link" icon={<LinkOutlined />} onClick={() => handleShare('link')}>
        复制链接
      </Menu.Item>
      <Menu.Item key="wechat" icon={<WechatOutlined />} onClick={() => handleShare('wechat')}>
        微信
      </Menu.Item>
      <Menu.Item key="weibo" icon={<WeiboOutlined />} onClick={() => handleShare('weibo')}>
        微博
      </Menu.Item>
      <Menu.Item key="qq" icon={<QqOutlined />} onClick={() => handleShare('qq')}>
        QQ
      </Menu.Item>
    </Menu>
  );

  return (
    <div style={{ padding: 24, background: '#f0f2f5', minHeight: '100vh' }}>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Space>
          <Title level={2} style={{ margin: 0 }}>
            <Badge count={unreadCount} offset={[10, 0]}>
              <BellOutlined /> 平台信息
            </Badge>
          </Title>
        </Space>
        <Button 
          icon={<ReloadOutlined />} 
          onClick={() => {
            loadPlatformInfo();
            loadImportantNotices();
            loadUnreadCount();
          }}
        >
          刷新
        </Button>
      </div>

      {/* 重要通知 */}
      {importantNotices.length > 0 && (
        <Card 
          title={<span><ExclamationCircleOutlined /> 重要通知</span>}
          style={{ marginBottom: 16 }}
        >
          <List
            dataSource={importantNotices}
            renderItem={(item) => (
              <List.Item onClick={() => loadDetail(item.id)} style={{ cursor: 'pointer' }}>
                <List.Item.Meta
                  avatar={getImportanceIcon(item.importanceLevel)}
                  title={
                    <Space>
                      {item.isPinned && <Badge status="error" text="置顶" />}
                      <Tag color={getInfoTypeColor(item.infoType)}>
                        {getInfoTypeLabel(item.infoType)}
                      </Tag>
                      <span>{item.title}</span>
                    </Space>
                  }
                  description={item.summary || item.publishedAt}
                />
              </List.Item>
            )}
          />
        </Card>
      )}

      {/* 订阅快捷入口 */}
      <Card style={{ marginBottom: 16 }}>
        <Space wrap>
          <Text>快速订阅：</Text>
          {['general', 'update', 'notice', 'warning'].map(type => (
            <Button
              key={type}
              type={subscriptions.some(s => s.infoType === type) ? 'primary' : 'default'}
              icon={subscriptions.some(s => s.infoType === type) ? <CheckCircleOutlined /> : <SubscribeOutlined />}
              onClick={() => handleSubscribe(type)}
            >
              {getInfoTypeLabel(type)}
            </Button>
          ))}
        </Space>
      </Card>

      {/* 筛选和搜索 */}
      <Card style={{ marginBottom: 16 }}>
        <Space wrap>
          <Input
            placeholder="搜索关键词"
            prefix={<SearchOutlined />}
            value={searchKeyword}
            onChange={(e) => setSearchKeyword(e.target.value)}
            style={{ width: 200 }}
            allowClear
          />
          <Select
            placeholder="信息类型"
            value={infoTypeFilter}
            onChange={setInfoTypeFilter}
            style={{ width: 120 }}
            allowClear
          >
            <Option value="general">通用</Option>
            <Option value="update">更新</Option>
            <Option value="notice">通知</Option>
            <Option value="warning">警告</Option>
          </Select>
        </Space>
      </Card>

      {/* 平台信息列表 */}
      <Card>
        <Spin spinning={loading}>
          {infoList.length === 0 ? (
            <Empty description="暂无平台信息" />
          ) : (
            <List
              dataSource={infoList}
              renderItem={(item) => (
                <List.Item
                  onClick={() => loadDetail(item.id)}
                  style={{ cursor: 'pointer' }}
                  actions={[
                    <Tooltip title="点赞">
                      <Button
                        type="text"
                        icon={item.isLiked ? <StarFilled style={{ color: '#faad14' }} /> : <StarOutlined />}
                        onClick={(e) => { e.stopPropagation(); handleLike(item.id); }}
                      >
                        {item.likeCount}
                      </Button>
                    </Tooltip>,
                    <Tooltip title="评论">
                      <Button type="text" icon={<MessageOutlined />}>
                        {item.commentCount}
                      </Button>
                    </Tooltip>,
                    <Tooltip title="分享">
                      <Dropdown overlay={shareMenu} trigger={['click']}>
                        <Button type="text" icon={<ShareAltOutlined />} onClick={(e) => e.stopPropagation()} />
                      </Dropdown>
                    </Tooltip>,
                    <Text type="secondary"><EyeOutlined /> {item.viewCount}</Text>,
                  ]}
                >
                  <List.Item.Meta
                    avatar={getImportanceIcon(item.importanceLevel)}
                    title={
                      <Space>
                        {item.isPinned && <Badge status="error" text="置顶" />}
                        {item.isExpired && <Tag color="red">已过期</Tag>}
                        <Tag color={getInfoTypeColor(item.infoType)}>
                          {getInfoTypeLabel(item.infoType)}
                        </Tag>
                        {!item.isRead && <Badge dot>未读</Badge>}
                        <span>{item.title}</span>
                      </Space>
                    }
                    description={
                      <div>
                        <Paragraph ellipsis={{ rows: 2 }}>{item.summary}</Paragraph>
                        <Text type="secondary" style={{ fontSize: 12 }}>
                          <ClockCircleOutlined /> {item.publishedAt}
                        </Text>
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
          )}
        </Spin>
      </Card>

      {/* 分页 */}
      <div style={{ textAlign: 'right', marginTop: 16 }}>
        <Pagination
          current={pagination.current}
          pageSize={pagination.pageSize}
          total={pagination.total}
          onChange={(page, pageSize) => {
            setPagination({ current: page, pageSize: pageSize || 20, total: pagination.total });
          }}
          showSizeChanger
          showTotal={(total) => `共 ${total} 条`}
        />
      </div>

      {/* 详情抽屉 */}
      <Drawer
        title={selectedInfo?.title}
        placement="right"
        width={720}
        open={drawerVisible}
        onClose={() => setDrawerVisible(false)}
        extra={
          <Space>
            <Tag color={getInfoTypeColor(selectedInfo?.infoType || '')}>
              {getInfoTypeLabel(selectedInfo?.infoType || '')}
            </Tag>
            <Dropdown overlay={shareMenu} trigger={['click']}>
              <Button icon={<ShareAltOutlined />}>分享</Button>
            </Dropdown>
          </Space>
        }
      >
        {selectedInfo && (
          <div>
            <Descriptions column={2} bordered style={{ marginBottom: 16 }}>
              <Descriptions.Item label="发布时间">{selectedInfo.publishedAt}</Descriptions.Item>
              <Descriptions.Item label="浏览量">{selectedInfo.viewCount}</Descriptions.Item>
            </Descriptions>

            {selectedInfo.summary && (
              <Alert message="摘要" description={selectedInfo.summary} type="info" style={{ marginBottom: 16 }} />
            )}

            <div 
              className="article-content"
              dangerouslySetInnerHTML={{ __html: selectedInfo.content || '' }}
            />

            <Divider />

            {/* 操作按钮 */}
            <Space>
              <Button 
                icon={selectedInfo.isLiked ? <StarFilled /> : <StarOutlined />} 
                onClick={() => handleLike(selectedInfo.id)}
              >
                点赞 ({selectedInfo.likeCount})
              </Button>
              <Dropdown overlay={shareMenu} trigger={['click']}>
                <Button icon={<ShareAltOutlined />}>分享</Button>
              </Dropdown>
            </Space>

            <Divider orientation="left">评论 ({comments.length})</Divider>

            {/* 评论输入 */}
            <div style={{ marginBottom: 16 }}>
              <TextArea
                rows={3}
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                placeholder="发表评论..."
              />
              <div style={{ marginTop: 8, textAlign: 'right' }}>
                <Button 
                  type="primary" 
                  icon={<SendOutlined />}
                  onClick={handleComment}
                  loading={commentLoading}
                >
                  发表评论
                </Button>
              </div>
            </div>

            {/* 评论列表 */}
            <List
              dataSource={comments}
              renderItem={(comment) => (
                <Comment
                  author={comment.nickname || comment.username}
                  avatar={<Avatar>{comment.username?.[0]?.toUpperCase()}</Avatar>}
                  content={comment.content}
                  datetime={comment.createdAt}
                  actions={[
                    <span><LikeOutlined /> {comment.likeCount}</span>
                  ]}
                >
                  {comment.replies && comment.replies.map((reply) => (
                    <Comment
                      key={reply.id}
                      author={reply.nickname || reply.username}
                      avatar={<Avatar>{reply.username?.[0]?.toUpperCase()}</Avatar>}
                      content={reply.content}
                      datetime={reply.createdAt}
                    />
                  ))}
                </Comment>
              )}
            />
          </div>
        )}
      </Drawer>
    </div>
  );
};

const Menu = require('antd').Menu;
const LinkOutlined = require('@ant-design/icons').LinkOutlined;

export default PlatformInfoEnhanced;

import React, { useState, useEffect } from 'react';
import { 
  Card, List, Badge, Tag, Button, Typography, Space, 
  Divider, Empty, Pagination, Spin, Select, Row, Col
} from 'antd';
import { 
  MessageOutlined, BellOutlined, CheckCircleOutlined,
  ClockCircleOutlined, FireOutlined, ReloadOutlined, Tooltip
} from '@ant-design/icons';
import axios from 'axios';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;

interface Notification {
  id: number;
  userId: number;
  type: string;
  title: string;
  content: string;
  isRead: boolean;
  priority: 'low' | 'medium' | 'high';
  category: string;
  relatedId?: number;
  relatedType?: string;
  createdAt: string;
  readAt?: string;
  metadata?: any;
}

const UserNotifications: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 });
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [readStatusFilter, setReadStatusFilter] = useState<string>('all');
  const [sortOrder, setSortOrder] = useState<'latest' | 'oldest' | 'priority'>('latest');
  const [unreadCount, setUnreadCount] = useState(0);
  
  // 实时通知相关
  const [hasNewNotification, setHasNewNotification] = useState(false);
  const [lastNotificationTime, setLastNotificationTime] = useState<number>(Date.now());

  const API_BASE = '/api/v9';

  // 加载通知列表
  const loadNotifications = async () => {
    setLoading(true);
    try {
      const params: any = {
        page: pagination.current,
        page_size: pagination.pageSize,
      };
      
      if (categoryFilter !== 'all') params.category = categoryFilter;
      if (readStatusFilter === 'unread') params.is_read = false;
      if (readStatusFilter === 'read') params.is_read = true;
      
      if (sortOrder === 'latest') params.sort = '-created_at';
      if (sortOrder === 'oldest') params.sort = 'created_at';
      if (sortOrder === 'priority') params.sort = '-priority';

      const response = await axios.get(`${API_BASE}/notifications`, { params });
      
      if (response.data.success) {
        setNotifications(response.data.data || []);
        setPagination(prev => ({
          ...prev,
          total: response.data.pagination?.total || (response.data.data?.length || 0)
        }));
      }
    } catch (error) {
      console.error('加载通知失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 加载未读数量
  const loadUnreadCount = async () => {
    try {
      const response = await axios.get(`${API_BASE}/notifications/unread/count`);
      if (response.data.success) {
        setUnreadCount(response.data.data?.count || 0);
      }
    } catch (error) {
      console.error('加载未读数量失败:', error);
    }
  };

  // 标记单个通知为已读
  const markAsRead = async (notificationId: number) => {
    try {
      const response = await axios.put(`${API_BASE}/notifications/${notificationId}/read`);
      if (response.data.success) {
        await loadNotifications();
        await loadUnreadCount();
      }
    } catch (error) {
      console.error('标记已读失败:', error);
    }
  };

  // 批量标记已读
  const markAllAsRead = async () => {
    try {
      const response = await axios.put(`${API_BASE}/notifications/read-all`);
      if (response.data.success) {
        setHasNewNotification(false);
        await loadNotifications();
        await loadUnreadCount();
      }
    } catch (error) {
      console.error('批量标记已读失败:', error);
    }
  };

  // 删除通知
  const deleteNotification = async (notificationId: number) => {
    try {
      const response = await axios.delete(`${API_BASE}/notifications/${notificationId}`);
      if (response.data.success) {
        await loadNotifications();
        await loadUnreadCount();
      }
    } catch (error) {
      console.error('删除通知失败:', error);
    }
  };

  // 实时通知检查
  const checkNewNotifications = async () => {
    try {
      const response = await axios.get(`${API_BASE}/notifications/latest`, {
        params: { since: new Date(lastNotificationTime).toISOString() }
      });
      
      if (response.data.success && response.data.data?.length > 0) {
        setHasNewNotification(true);
        setLastNotificationTime(Date.now());
      }
    } catch (error) {
      console.error('检查新通知失败:', error);
    }
  };

  // 重置筛选
  const resetFilters = () => {
    setCategoryFilter('all');
    setReadStatusFilter('all');
    setSortOrder('latest');
    setPagination(prev => ({ ...prev, current: 1 }));
    setTimeout(loadNotifications, 100);
  };

  // 获取通知类型图标和颜色
  const getNotificationStyle = (type: string, priority: string) => {
    const typeConfig: Record<string, { icon: any, color: string }> = {
      news: { icon: <MessageOutlined />, color: 'blue' },
      activity: { icon: <FireOutlined />, color: 'orange' },
      system: { icon: <BellOutlined />, color: 'purple' },
      alert: { icon: <BellOutlined />, color: 'red' },
      success: { icon: <CheckCircleOutlined />, color: 'green' },
    };
    
    const config = typeConfig[type] || { icon: <BellOutlined />, color: 'default' };
    return config;
  };

  // 获取优先级标签
  const getPriorityTag = (priority: string) => {
    const priorityConfig: Record<string, { color: string, text: string }> = {
      low: { color: 'default', text: '低' },
      medium: { color: 'blue', text: '中' },
      high: { color: 'red', text: '高' },
    };
    return priorityConfig[priority] || priorityConfig.low;
  };

  // 获取分类标签
  const getCategoryTag = (category: string) => {
    const categoryConfig: Record<string, { color: string, text: string }> = {
      news: { color: 'blue', text: '新闻' },
      activity: { color: 'orange', text: '活动' },
      system: { color: 'purple', text: '系统' },
      reward: { color: 'gold', text: '奖励' },
      security: { color: 'red', text: '安全' },
      task: { color: 'green', text: '任务' },
    };
    return categoryConfig[category] || { color: 'default', text: category };
  };

  useEffect(() => {
    loadNotifications();
    loadUnreadCount();
    
    // 设置定时检查新通知（每30秒）
    const interval = setInterval(checkNewNotifications, 30000);
    
    return () => clearInterval(interval);
  }, [pagination.current, pagination.pageSize, categoryFilter, readStatusFilter, sortOrder]);

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ marginBottom: '24px' }}>
        <Space>
          <Title level={2} style={{ margin: 0 }}>
            <Badge count={unreadCount} offset={[10, 0]}>
              <BellOutlined style={{ color: '#1890ff' }} />
            </Badge>
            {' '}我的通知
          </Title>
          {hasNewNotification && (
            <Tag color="red">有新通知</Tag>
          )}
          <Button 
            icon={<CheckCircleOutlined />} 
            onClick={markAllAsRead}
            disabled={unreadCount === 0}
          >
            全部标为已读
          </Button>
        </Space>
      </div>

      {/* 筛选栏 */}
      <Card style={{ marginBottom: '24px' }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={8} md={6}>
            <Select
              placeholder="通知分类"
              value={categoryFilter}
              onChange={setCategoryFilter}
              style={{ width: '100%' }}
            >
              <Option value="all">全部分类</Option>
              <Option value="news">新闻</Option>
              <Option value="activity">活动</Option>
              <Option value="system">系统</Option>
              <Option value="reward">奖励</Option>
              <Option value="security">安全</Option>
              <Option value="task">任务</Option>
            </Select>
          </Col>
          <Col xs={24} sm={8} md={6}>
            <Select
              placeholder="阅读状态"
              value={readStatusFilter}
              onChange={setReadStatusFilter}
              style={{ width: '100%' }}
            >
              <Option value="all">全部状态</Option>
              <Option value="unread">未读</Option>
              <Option value="read">已读</Option>
            </Select>
          </Col>
          <Col xs={24} sm={8} md={6}>
            <Select
              placeholder="排序方式"
              value={sortOrder}
              onChange={setSortOrder}
              style={{ width: '100%' }}
            >
              <Option value="latest">最新优先</Option>
              <Option value="oldest">最早优先</Option>
              <Option value="priority">优先级排序</Option>
            </Select>
          </Col>
          <Col xs={24} sm={8} md={6}>
            <Space>
              <Button onClick={loadNotifications} icon={<ReloadOutlined />}>
                刷新
              </Button>
              <Button onClick={resetFilters}>
                重置筛选
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 通知统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} md={6}>
          <Card size="small">
            <Space direction="vertical" size="small">
              <Text type="secondary">全部通知</Text>
              <Text strong style={{ fontSize: '24px' }}>{pagination.total}</Text>
            </Space>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card size="small">
            <Space direction="vertical" size="small">
              <Text type="secondary">未读通知</Text>
              <Text strong style={{ fontSize: '24px', color: '#ff4d4f' }}>{unreadCount}</Text>
            </Space>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card size="small">
            <Space direction="vertical" size="small">
              <Text type="secondary">系统通知</Text>
              <Text strong style={{ fontSize: '24px', color: '#722ed1' }}>
                {notifications.filter(n => n.category === 'system').length}
              </Text>
            </Space>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card size="small">
            <Space direction="vertical" size="small">
              <Text type="secondary">高优先级</Text>
              <Text strong style={{ fontSize: '24px', color: '#ff4d4f' }}>
                {notifications.filter(n => n.priority === 'high').length}
              </Text>
            </Space>
          </Card>
        </Col>
      </Row>

      {/* 通知列表 */}
      <Spin spinning={loading}>
        {notifications.length === 0 ? (
          <Empty description="暂无通知" />
        ) : (
          <List
            dataSource={notifications}
            renderItem={(notification) => {
              const style = getNotificationStyle(notification.type, notification.priority);
              const priorityTag = getPriorityTag(notification.priority);
              const categoryTag = getCategoryTag(notification.category);
              
              return (
                <Card 
                  key={notification.id}
                  style={{ 
                    marginBottom: '12px',
                    borderLeft: notification.isRead ? 'none' : `4px solid #1890ff`
                  }}
                  hoverable
                >
                  <List.Item
                    actions={[
                      !notification.isRead && (
                        <Button 
                          type="link" 
                          size="small"
                          onClick={(e) => {
                            e.stopPropagation();
                            markAsRead(notification.id);
                          }}
                        >
                          标为已读
                        </Button>
                      ),
                      <Button 
                        type="link" 
                        danger 
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteNotification(notification.id);
                        }}
                      >
                        删除
                      </Button>
                    ]}
                  >
                    <List.Item.Meta
                      avatar={
                        <div style={{ 
                          width: '40px', 
                          height: '40px', 
                          borderRadius: '50%',
                          backgroundColor: style.color === 'red' ? '#fff1f0' : 
                                         style.color === 'orange' ? '#fff7e6' :
                                         style.color === 'blue' ? '#e6f7ff' :
                                         style.color === 'green' ? '#f6ffed' :
                                         style.color === 'purple' ? '#f9f0ff' : '#f5f5f5',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: style.color === 'red' ? '#ff4d4f' : 
                                 style.color === 'orange' ? '#fa8c16' :
                                 style.color === 'blue' ? '#1890ff' :
                                 style.color === 'green' ? '#52c41a' :
                                 style.color === 'purple' ? '#722ed1' : '#8c8c8c'
                        }}>
                          {style.icon}
                        </div>
                      }
                      title={
                        <Space>
                          {!notification.isRead && <Badge dot />}
                          <span style={{ 
                            fontWeight: notification.isRead ? 'normal' : 500,
                            fontSize: '16px'
                          }}>
                            {notification.title}
                          </span>
                          <Tag color={categoryTag.color}>{categoryTag.text}</Tag>
                          <Tag color={priorityTag.color}>优先级: {priorityTag.text}</Tag>
                        </Space>
                      }
                      description={
                        <Space direction="vertical" size="small" style={{ width: '100%' }}>
                          <Paragraph 
                            style={{ 
                              margin: 0,
                              opacity: notification.isRead ? 0.65 : 1
                            }}
                          >
                            {notification.content}
                          </Paragraph>
                          <Space split={<Divider type="vertical" />}>
                            <Text type="secondary" style={{ fontSize: '12px' }}>
                              <ClockCircleOutlined /> {new Date(notification.createdAt).toLocaleString('zh-CN')}
                            </Text>
                            {notification.readAt && (
                              <Text type="secondary" style={{ fontSize: '12px' }}>
                                已读时间: {new Date(notification.readAt).toLocaleString('zh-CN')}
                              </Text>
                            )}
                          </Space>
                        </Space>
                      }
                    />
                  </List.Item>
                </Card>
              );
            }}
          />
        )}
      </Spin>

      {/* 分页 */}
      {notifications.length > 0 && (
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
    </div>
  );
};

export default UserNotifications;

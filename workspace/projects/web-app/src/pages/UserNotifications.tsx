import React, { useState, useEffect } from 'react';
import { List, Badge, Tag, Typography, Spin, Empty, Pagination, Space, Button, Modal, message } from 'antd';
import { BellOutlined, CheckCircleOutlined, ClockCircleOutlined, LinkOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

interface Notification {
  id: number;
  title: string;
  content: string | null;
  type: string;
  isRead: boolean;
  link: string | null;
  createdAt: string;
  readAt: string | null;
}

interface NotificationResponse {
  success: boolean;
  message: string;
  data: Notification[];
  unreadCount: number;
  total: number;
  page: number;
  page_size: number;
  user_id: number;
}

const UserNotifications: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [unreadCount, setUnreadCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [total, setTotal] = useState(0);

  // 获取通知列表
  const fetchNotifications = async (page: number = 1, page_size: number = 20) => {
    setLoading(true);
    try {
      const response = await fetch(
        `/api/v9/news/notifications?page=${page}&page_size=${page_size}&user_id=1`
      );
      const data: NotificationResponse = await response.json();
      if (data.success) {
        setNotifications(data.data);
        setUnreadCount(data.unreadCount);
        setTotal(data.total);
        setCurrentPage(data.page);
        setPageSize(data.page_size);
      }
    } catch (error) {
      console.error('获取通知失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 标记为已读
  const markAsRead = async (notificationId: number) => {
    try {
      const response = await fetch(`/api/v9/news/notifications/${notificationId}/read`, {
        method: 'PUT'
      });
      const data = await response.json();
      if (data.success) {
        message.success('标记为已读');
        fetchNotifications(currentPage, pageSize);
      }
    } catch (error) {
      console.error('标记失败:', error);
      message.error('标记失败');
    }
  };

  // 全部标记为已读
  const markAllAsRead = async () => {
    try {
      const response = await fetch('/api/v9/news/notifications/read-all', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_id: 1 })
      });
      const data = await response.json();
      if (data.success) {
        message.success('全部标记为已读');
        fetchNotifications(currentPage, pageSize);
      }
    } catch (error) {
      console.error('批量标记失败:', error);
      message.error('批量标记失败');
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, []);

  // 处理分页变化
  const handlePageChange = (page: number, pageSize?: number) => {
    fetchNotifications(page, pageSize);
  };

  // 获取通知类型颜色
  const getNotificationTypeColor = (type: string) => {
    const colorMap: Record<string, string> = {
      system: 'blue',
      update: 'green',
      alert: 'red',
      info: 'cyan',
      promotion: 'orange'
    };
    return colorMap[type] || 'default';
  };

  // 获取通知类型名称
  const getNotificationTypeName = (type: string) => {
    const nameMap: Record<string, string> = {
      system: '系统通知',
      update: '版本更新',
      alert: '告警通知',
      info: '信息通知',
      promotion: '活动推广'
    };
    return nameMap[type] || type;
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1000px', margin: '0 auto' }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Title level={2} style={{ margin: 0 }}>
            <Badge count={unreadCount} offset={[10, 0]}>
              <BellOutlined /> 我的通知
            </Badge>
          </Title>
          {unreadCount > 0 && (
            <Button type="primary" onClick={markAllAsRead}>
              全部标记为已读
            </Button>
          )}
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '48px' }}>
            <Spin size="large" />
          </div>
        ) : (
          <>
            {notifications.length === 0 ? (
              <Empty description="暂无通知" />
            ) : (
              <>
                <List
                  dataSource={notifications}
                  renderItem={(notification) => (
                    <List.Item
                      style={{
                        background: notification.isRead ? '#fff' : '#e6f7ff',
                        padding: '16px',
                        borderRadius: '8px',
                        marginBottom: '12px',
                        border: '1px solid #f0f0f0',
                        cursor: 'pointer'
                      }}
                      onClick={() => !notification.isRead && markAsRead(notification.id)}
                    >
                      <List.Item.Meta
                        avatar={
                          notification.isRead ? (
                            <CheckCircleOutlined style={{ fontSize: '24px', color: '#52c41a' }} />
                          ) : (
                            <BellOutlined style={{ fontSize: '24px', color: '#1890ff' }} />
                          )
                        }
                        title={
                          <Space>
                            <Text strong={!notification.isRead}>
                              {notification.title}
                            </Text>
                            {!notification.isRead && (
                              <Tag color="red">未读</Tag>
                            )}
                            <Tag color={getNotificationTypeColor(notification.type)}>
                              {getNotificationTypeName(notification.type)}
                            </Tag>
                          </Space>
                        }
                        description={
                          <Space direction="vertical" size="small" style={{ width: '100%' }}>
                            <Text>{notification.content}</Text>
                            <Space>
                              <Text type="secondary" style={{ fontSize: '12px' }}>
                                <ClockCircleOutlined /> {notification.createdAt}
                              </Text>
                              {notification.link && (
                                <Button
                                  type="link"
                                  size="small"
                                  icon={<LinkOutlined />}
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    window.open(notification.link, '_blank');
                                  }}
                                >
                                  查看详情
                                </Button>
                              )}
                              {!notification.isRead && (
                                <Button
                                  type="link"
                                  size="small"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    markAsRead(notification.id);
                                  }}
                                >
                                  标记为已读
                                </Button>
                              )}
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
                      showTotal={(total) => `共 ${total} 条通知`}
                    />
                  </div>
                )}
              </>
            )}
          </>
        )}
      </Space>
    </div>
  );
};

export default UserNotifications;

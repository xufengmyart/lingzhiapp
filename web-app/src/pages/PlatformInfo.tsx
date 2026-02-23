import React, { useState, useEffect } from 'react';
import { 
  Card, List, Tag, Input, Select, Button, Typography, Space, 
  Divider, Empty, Pagination, Spin, Alert, Badge, message, Drawer,
  Descriptions, Tooltip, Row, Col
} from 'antd';
import { 
  SearchOutlined, EyeOutlined, LikeOutlined, 
  ClockCircleOutlined, BellOutlined, InfoCircleOutlined, 
  ExclamationCircleOutlined, ThunderboltOutlined, ReloadOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { Title, Paragraph, Text } = Typography;
const { Option } = Select;

const PlatformInfo = () => {
  const [loading, setLoading] = useState(false);
  const [infoList, setInfoList] = useState([]);
  const [selectedInfo, setSelectedInfo] = useState(null);
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 20, total: 0 });
  const [searchKeyword, setSearchKeyword] = useState('');
  const [infoTypeFilter, setInfoTypeFilter] = useState('');
  const [importantNotices, setImportantNotices] = useState([]);

  const API_BASE = '/api/v9';

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

  const loadDetail = async (id) => {
    try {
      const response = await axios.get(`${API_BASE}/platform-info/${id}`);
      if (response.data.success) {
        setSelectedInfo(response.data.data);
        setDrawerVisible(true);
      }
    } catch (error) {
      message.error('加载详情失败');
    }
  };

  useEffect(() => {
    loadPlatformInfo();
    loadImportantNotices();
  }, [pagination.current, pagination.pageSize, infoTypeFilter]);

  useEffect(() => {
    if (searchKeyword) {
      const timer = setTimeout(() => {
        setPagination(prev => ({ ...prev, current: 1 }));
        loadPlatformInfo();
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [searchKeyword]);

  const getInfoTypeColor = (type) => {
    const colorMap = {
      'general': 'default',
      'update': 'blue',
      'notice': 'orange',
      'warning': 'red',
    };
    return colorMap[type] || 'default';
  };

  const getInfoTypeLabel = (type) => {
    const labelMap = {
      'general': '通用',
      'update': '更新',
      'notice': '通知',
      'warning': '警告',
    };
    return labelMap[type] || type;
  };

  const getImportanceIcon = (level) => {
    if (level >= 3) return <ThunderboltOutlined style={{ color: '#ff4d4f' }} />;
    if (level >= 2) return <ExclamationCircleOutlined style={{ color: '#faad14' }} />;
    return <InfoCircleOutlined style={{ color: '#52c41a' }} />;
  };

  return (
    <div style={{ padding: 24, background: '#f0f2f5', minHeight: '100vh' }}>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Title level={2}>
          <BellOutlined /> 平台信息
        </Title>
        <Button 
          icon={<ReloadOutlined />} 
          onClick={() => {
            loadPlatformInfo();
            loadImportantNotices();
          }}
        >
          刷新
        </Button>
      </div>

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
                    <span>
                      {item.title}
                      {item.isPinned && <Tag color="red" style={{ marginLeft: 8 }}>置顶</Tag>}
                      <Tag color={getInfoTypeColor(item.infoType)} style={{ marginLeft: 8 }}>
                        {getInfoTypeLabel(item.infoType)}
                      </Tag>
                    </span>
                  }
                  description={item.summary || item.publishedAt}
                />
              </List.Item>
            )}
          />
        </Card>
      )}

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
          </Select>
        </Space>
      </Card>

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
                    <Text type="secondary"><EyeOutlined /> {item.viewCount}</Text>,
                    <Text type="secondary"><LikeOutlined /> {item.likeCount}</Text>,
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

      <Drawer
        title={selectedInfo?.title}
        placement="right"
        width={720}
        open={drawerVisible}
        onClose={() => setDrawerVisible(false)}
      >
        {selectedInfo && (
          <div>
            <Descriptions column={2} bordered>
              <Descriptions.Item label="发布时间">{selectedInfo.publishedAt}</Descriptions.Item>
              <Descriptions.Item label="浏览量">{selectedInfo.viewCount}</Descriptions.Item>
            </Descriptions>
            <Divider />
            {selectedInfo.summary && (
              <Alert message="摘要" description={selectedInfo.summary} type="info" style={{ marginBottom: 16 }} />
            )}
            <div dangerouslySetInnerHTML={{ __html: selectedInfo.content || '' }} />
          </div>
        )}
      </Drawer>
    </div>
  );
};

export default PlatformInfo;

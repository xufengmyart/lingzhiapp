import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Statistic, 
  Row, 
  Col, 
  Table, 
  Tabs, 
  Select, 
  DatePicker, 
  Button,
  Space,
  Tag,
  message,
  Spin,
  Empty,
  Progress
} from 'antd';
import {
  ShareAltOutlined,
  EyeOutlined,
  UserAddOutlined,
  TrophyOutlined,
  BarChartOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import { 
  getConversionStats, 
  getShareLeaderboard, 
  getReferralTree 
} from '../services/shareApi';
import './ShareAnalytics.css';

const { TabPane } = Tabs;
const { RangePicker } = DatePicker;
const { Option } = Select;

interface ConversionData {
  summary: {
    total_shares: number;
    total_clicks: number;
    total_registrations: number;
    click_rate: number;
    registration_rate: number;
  };
  daily: Array<{
    date: string;
    shares: number;
    clicks: number;
    registrations: number;
  }>;
}

interface LeaderboardItem {
  rank: number;
  user_id: number;
  username: string;
  nickname: string;
  total_shares: number;
  total_clicks: number;
  total_registrations: number;
}

const ShareAnalytics: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [conversionData, setConversionData] = useState<ConversionData | null>(null);
  const [leaderboard, setLeaderboard] = useState<LeaderboardItem[]>([]);
  const [period, setPeriod] = useState('week');
  const [days, setDays] = useState(7);

  // 获取转化率统计
  const fetchConversionStats = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await getConversionStats(token, days);
      if (response.success) {
        setConversionData(response.data);
      } else {
        message.error(response.message || '获取转化率统计失败');
      }
    } catch (error) {
      message.error('网络错误，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  // 获取排行榜
  const fetchLeaderboard = async () => {
    setLoading(true);
    try {
      const response = await getShareLeaderboard(period);
      if (response.success) {
        setLeaderboard(response.data);
      } else {
        message.error(response.message || '获取排行榜失败');
      }
    } catch (error) {
      message.error('网络错误，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConversionStats();
    fetchLeaderboard();
  }, [period, days]);

  const handleRefresh = () => {
    fetchConversionStats();
    fetchLeaderboard();
  };

  // 排行榜表格列
  const leaderboardColumns = [
    {
      title: '排名',
      dataIndex: 'rank',
      key: 'rank',
      width: 80,
      render: (rank: number) => (
        <div>
          {rank === 1 && <TrophyOutlined style={{ color: '#FFD700', fontSize: 24 }} />}
          {rank === 2 && <TrophyOutlined style={{ color: '#C0C0C0', fontSize: 24 }} />}
          {rank === 3 && <TrophyOutlined style={{ color: '#CD7F32', fontSize: 24 }} />}
          {rank > 3 && <span style={{ fontSize: 16, fontWeight: 'bold' }}>#{rank}</span>}
        </div>
      ),
    },
    {
      title: '用户',
      dataIndex: 'username',
      key: 'username',
      render: (username: string, record: LeaderboardItem) => (
        <div>
          <div style={{ fontWeight: 'bold' }}>{record.nickname || username}</div>
          <div style={{ fontSize: 12, color: '#999' }}>@{username}</div>
        </div>
      ),
    },
    {
      title: '分享次数',
      dataIndex: 'total_shares',
      key: 'total_shares',
      sorter: (a: LeaderboardItem, b: LeaderboardItem) => a.total_shares - b.total_shares,
      render: (count: number) => <Tag color="blue">{count}</Tag>,
    },
    {
      title: '点击次数',
      dataIndex: 'total_clicks',
      key: 'total_clicks',
      sorter: (a: LeaderboardItem, b: LeaderboardItem) => a.total_clicks - b.total_clicks,
      render: (count: number) => <Tag color="cyan">{count}</Tag>,
    },
    {
      title: '注册数',
      dataIndex: 'total_registrations',
      key: 'total_registrations',
      sorter: (a: LeaderboardItem, b: LeaderboardItem) => a.total_registrations - b.total_registrations,
      render: (count: number) => <Tag color="green">{count}</Tag>,
    },
    {
      title: '转化率',
      key: 'conversion_rate',
      render: (record: LeaderboardItem) => {
        const rate = record.total_clicks > 0 
          ? ((record.total_registrations / record.total_clicks) * 100).toFixed(2)
          : '0.00';
        return <Progress percent={parseFloat(rate)} size="small" />;
      },
    },
  ];

  return (
    <div className="share-analytics-container">
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>分享数据分析</h2>
        <Button 
          icon={<ReloadOutlined />} 
          onClick={handleRefresh}
          loading={loading}
        >
          刷新数据
        </Button>
      </div>

      <Tabs defaultActiveKey="overview">
        <TabPane tab="数据概览" key="overview">
          <Spin spinning={loading}>
            {conversionData ? (
              <>
                {/* 统计卡片 */}
                <Row gutter={16} style={{ marginBottom: 24 }}>
                  <Col span={6}>
                    <Card>
                      <Statistic
                        title="总分享次数"
                        value={conversionData.summary.total_shares}
                        prefix={<ShareAltOutlined />}
                        valueStyle={{ color: '#3f8600' }}
                      />
                    </Card>
                  </Col>
                  <Col span={6}>
                    <Card>
                      <Statistic
                        title="总点击次数"
                        value={conversionData.summary.total_clicks}
                        prefix={<EyeOutlined />}
                        valueStyle={{ color: '#1890ff' }}
                      />
                    </Card>
                  </Col>
                  <Col span={6}>
                    <Card>
                      <Statistic
                        title="总注册数"
                        value={conversionData.summary.total_registrations}
                        prefix={<UserAddOutlined />}
                        valueStyle={{ color: '#cf1322' }}
                      />
                    </Card>
                  </Col>
                  <Col span={6}>
                    <Card>
                      <Statistic
                        title="注册转化率"
                        value={conversionData.summary.registration_rate}
                        suffix="%"
                        prefix={<BarChartOutlined />}
                        valueStyle={{ color: '#722ed1' }}
                      />
                    </Card>
                  </Col>
                </Row>

                {/* 每日数据表格 */}
                <Card title="每日趋势" style={{ marginTop: 24 }}>
                  <Table
                    columns={[
                      {
                        title: '日期',
                        dataIndex: 'date',
                        key: 'date',
                      },
                      {
                        title: '分享数',
                        dataIndex: 'shares',
                        key: 'shares',
                        render: (value: number) => <Tag color="blue">{value}</Tag>,
                      },
                      {
                        title: '点击数',
                        dataIndex: 'clicks',
                        key: 'clicks',
                        render: (value: number) => <Tag color="cyan">{value}</Tag>,
                      },
                      {
                        title: '注册数',
                        dataIndex: 'registrations',
                        key: 'registrations',
                        render: (value: number) => <Tag color="green">{value}</Tag>,
                      },
                    ]}
                    dataSource={conversionData.daily}
                    rowKey="date"
                    pagination={{ pageSize: 10 }}
                  />
                </Card>
              </>
            ) : (
              <Empty description="暂无数据" />
            )}
          </Spin>
        </TabPane>

        <TabPane tab="分享排行榜" key="leaderboard">
          <div style={{ marginBottom: 16 }}>
            <Space>
              <span>统计周期：</span>
              <Select 
                value={period} 
                onChange={setPeriod}
                style={{ width: 120 }}
              >
                <Option value="week">本周</Option>
                <Option value="month">本月</Option>
                <Option value="all">全部</Option>
              </Select>
            </Space>
          </div>

          <Spin spinning={loading}>
            <Table
              columns={leaderboardColumns}
              dataSource={leaderboard}
              rowKey="rank"
              pagination={{ pageSize: 20 }}
            />
          </Spin>
        </TabPane>
      </Tabs>
    </div>
  );
};

export default ShareAnalytics;

import React, { useState, useEffect } from 'react';
import { 
  Card, Table, Tag, Space, Button, Typography, Select, DatePicker,
  message, Modal, QRCode, Spin, Empty, Row, Col, Statistic, Input,
  Divider
} from 'antd';
import { 
  ReloadOutlined, EyeOutlined, QrcodeOutlined, CopyOutlined,
  CheckCircleOutlined, ClockCircleOutlined, CloseCircleOutlined,
  DollarOutlined, ShoppingOutlined, SearchOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { RangePicker } = DatePicker;

interface RechargeRecord {
  id: number;
  user_id: number;
  tier_id: number;
  order_no: string;
  amount: number;
  base_lingzhi: number;
  bonus_lingzhi: number;
  total_lingzhi: number;
  payment_method: string;
  payment_status: string;
  payment_time?: string;
  transaction_id?: string;
  created_at: string;
  tier_name?: string;
}

const RechargeHistory: React.FC = () => {
  const [records, setRecords] = useState<RechargeRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 });
  const [filters, setFilters] = useState({
    status: 'all',
    method: 'all',
    dateRange: null as any,
    keyword: ''
  });
  
  const [selectedRecord, setSelectedRecord] = useState<RechargeRecord | null>(null);
  const [paymentModalVisible, setPaymentModalVisible] = useState(false);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [paymentQrCode, setPaymentQrCode] = useState('');
  const [paymentUrl, setPaymentUrl] = useState('');
  const [checkingPayment, setCheckingPayment] = useState(false);

  const API_BASE = '/api';

  // 加载充值记录
  const loadRecords = async () => {
    setLoading(true);
    try {
      const params: any = {
        page: pagination.current,
        page_size: pagination.pageSize,
      };
      
      if (filters.status !== 'all') params.status = filters.status;
      if (filters.method !== 'all') params.method = filters.method;
      if (filters.keyword) params.keyword = filters.keyword;
      
      const response = await axios.get(`${API_BASE}/recharge/records`, { params });
      
      if (response.data.success) {
        setRecords(response.data.data || []);
        setPagination(prev => ({
          ...prev,
          total: response.data.pagination?.total || response.data.data?.length || 0
        }));
      }
    } catch (error) {
      message.error('加载充值记录失败');
      console.error('加载充值记录失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 创建充值订单
  const createRechargeOrder = async (tierId: number) => {
    try {
      const response = await axios.post(`${API_BASE}/recharge/create-order`, {
        user_id: 10, // 测试用户ID
        tier_id: tierId,
        payment_method: 'alipay'
      });
      
      if (response.data.success) {
        const orderNo = response.data.data.order_no;
        // 创建支付订单
        const paymentResponse = await axios.post(`${API_BASE}/payment/alipay/create`, {
          order_no: orderNo
        });
        
        if (paymentResponse.data.success) {
          setPaymentQrCode(paymentResponse.data.data.qr_code);
          setPaymentUrl(paymentResponse.data.data.payment_url);
          setSelectedRecord({
            id: response.data.data.record_id,
            order_no: orderNo,
            amount: response.data.data.amount,
            total_lingzhi: response.data.data.total_lingzhi,
            payment_status: 'pending',
            created_at: new Date().toISOString()
          } as any);
          setPaymentModalVisible(true);
          
          // 开始轮询支付状态
          startPaymentPolling(orderNo);
        }
      }
    } catch (error) {
      message.error('创建订单失败');
      console.error('创建订单失败:', error);
    }
  };

  // 轮询支付状态
  const startPaymentPolling = (orderNo: string) => {
    const interval = setInterval(async () => {
      try {
        const response = await axios.get(`${API_BASE}/payment/status/${orderNo}`);
        if (response.data.success && response.data.data.payment_status === 'success') {
          clearInterval(interval);
          setPaymentModalVisible(false);
          message.success('支付成功！');
          loadRecords();
        }
      } catch (error) {
        console.error('查询支付状态失败:', error);
      }
    }, 3000); // 每3秒查询一次
    
    // 5分钟后停止轮询
    setTimeout(() => clearInterval(interval), 300000);
  };

  // 模拟支付（仅用于测试）
  const simulatePayment = async (orderNo: string) => {
    try {
      const response = await axios.post(`${API_BASE}/payment/simulate/${orderNo}`);
      if (response.data.success) {
        message.success(`模拟支付成功！获得 ${response.data.data.total_lingzhi} 灵值`);
        setPaymentModalVisible(false);
        loadRecords();
      }
    } catch (error) {
      message.error('模拟支付失败');
    }
  };

  // 查看详情
  const showDetail = (record: RechargeRecord) => {
    setSelectedRecord(record);
    setDetailModalVisible(true);
  };

  // 复制订单号
  const copyOrderNo = (orderNo: string) => {
    navigator.clipboard.writeText(orderNo);
    message.success('订单号已复制');
  };

  // 获取状态标签
  const getStatusTag = (status: string) => {
    const statusConfig: Record<string, { color: string; text: string }> = {
      'pending': { color: 'orange', text: '待支付' },
      'success': { color: 'green', text: '支付成功' },
      'failed': { color: 'red', text: '支付失败' },
      'cancelled': { color: 'default', text: '已取消' }
    };
    const config = statusConfig[status] || { color: 'default', text: status };
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  // 获取支付方法标签
  const getPaymentMethodTag = (method: string) => {
    const methodConfig: Record<string, { color: string; text: string }> = {
      'alipay': { color: 'blue', text: '支付宝' },
      'wechat': { color: 'green', text: '微信支付' },
      'bank': { color: 'purple', text: '银行转账' }
    };
    const config = methodConfig[method] || { color: 'default', text: method };
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  useEffect(() => {
    loadRecords();
  }, [pagination.current, pagination.pageSize, filters]);

  // 统计数据
  const statistics = {
    total: records.length,
    success: records.filter(r => r.payment_status === 'success').length,
    pending: records.filter(r => r.payment_status === 'pending').length,
    totalAmount: records.filter(r => r.payment_status === 'success').reduce((sum, r) => sum + r.amount, 0)
  };

  const columns = [
    {
      title: '订单号',
      dataIndex: 'order_no',
      key: 'order_no',
      render: (orderNo: string) => (
        <Space>
          <Text code>{orderNo}</Text>
          <Button type="link" size="small" icon={<CopyOutlined />} onClick={() => copyOrderNo(orderNo)} />
        </Space>
      )
    },
    {
      title: '充值档位',
      dataIndex: 'tier_name',
      key: 'tier_name',
      render: (tierName: string, record: RechargeRecord) => (
        <Space direction="vertical" size="small">
          <Text strong>{tierName || `充值 ${record.amount}元`}</Text>
          <Text type="secondary">¥{record.amount}</Text>
        </Space>
      )
    },
    {
      title: '获得灵值',
      dataIndex: 'total_lingzhi',
      key: 'total_lingzhi',
      render: (totalLingzhi: number, record: RechargeRecord) => (
        <Space>
          <Text strong style={{ color: '#52c41a' }}>{totalLingzhi}</Text>
          {record.bonus_lingzhi > 0 && <Text type="secondary">(+{record.bonus_lingzhi}赠送)</Text>}
        </Space>
      )
    },
    {
      title: '支付方式',
      dataIndex: 'payment_method',
      key: 'payment_method',
      render: getPaymentMethodTag
    },
    {
      title: '状态',
      dataIndex: 'payment_status',
      key: 'payment_status',
      render: getStatusTag
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (createdAt: string) => new Date(createdAt).toLocaleString('zh-CN')
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: RechargeRecord) => (
        <Space>
          <Button type="link" size="small" icon={<EyeOutlined />} onClick={() => showDetail(record)}>
            详情
          </Button>
          {record.payment_status === 'pending' && (
            <Button type="link" size="small" danger onClick={() => simulatePayment(record.order_no)}>
              模拟支付
            </Button>
          )}
        </Space>
      )
    }
  ];

  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto' }}>
      <div style={{ marginBottom: '24px' }}>
        <Title level={2}>
          <ShoppingOutlined /> 充值记录
        </Title>
      </div>

      {/* 统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="总订单数"
              value={statistics.total}
              prefix={<ShoppingOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="成功订单"
              value={statistics.success}
              valueStyle={{ color: '#3f8600' }}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="待支付"
              value={statistics.pending}
              valueStyle={{ color: '#faad14' }}
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="总充值金额"
              value={statistics.totalAmount}
              prefix={<DollarOutlined />}
              suffix="元"
            />
          </Card>
        </Col>
      </Row>

      {/* 筛选栏 */}
      <Card style={{ marginBottom: '24px' }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={8} md={6}>
            <Select
              placeholder="支付状态"
              value={filters.status}
              onChange={(value) => setFilters({ ...filters, status: value })}
              style={{ width: '100%' }}
            >
              <Option value="all">全部状态</Option>
              <Option value="pending">待支付</Option>
              <Option value="success">支付成功</Option>
              <Option value="failed">支付失败</Option>
            </Select>
          </Col>
          <Col xs={24} sm={8} md={6}>
            <Select
              placeholder="支付方式"
              value={filters.method}
              onChange={(value) => setFilters({ ...filters, method: value })}
              style={{ width: '100%' }}
            >
              <Option value="all">全部方式</Option>
              <Option value="alipay">支付宝</Option>
              <Option value="wechat">微信支付</Option>
              <Option value="bank">银行转账</Option>
            </Select>
          </Col>
          <Col xs={24} sm={8} md={6}>
            <Input
              placeholder="搜索订单号"
              value={filters.keyword}
              onChange={(e) => setFilters({ ...filters, keyword: e.target.value })}
              prefix={<SearchOutlined />}
              onPressEnter={() => loadRecords()}
            />
          </Col>
          <Col xs={24} sm={24} md={6}>
            <Space>
              <Button type="primary" icon={<SearchOutlined />} onClick={() => loadRecords()}>
                搜索
              </Button>
              <Button icon={<ReloadOutlined />} onClick={loadRecords}>
                刷新
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 充值记录表格 */}
      <Card>
        <Spin spinning={loading}>
          {records.length === 0 ? (
            <Empty description="暂无充值记录" />
          ) : (
            <Table
              columns={columns}
              dataSource={records}
              rowKey="id"
              pagination={{
                current: pagination.current,
                pageSize: pagination.pageSize,
                total: pagination.total,
                showSizeChanger: true,
                showTotal: (total) => `共 ${total} 条`
              }}
              scroll={{ x: 800 }}
            />
          )}
        </Spin>
      </Card>

      {/* 支付弹窗 */}
      <Modal
        title="扫码支付"
        open={paymentModalVisible}
        onCancel={() => setPaymentModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setPaymentModalVisible(false)}>
            关闭
          </Button>,
          <Button 
            key="simulate" 
            type="primary" 
            onClick={() => selectedRecord && simulatePayment(selectedRecord.order_no)}
          >
            模拟支付（测试用）
          </Button>
        ]}
        width={500}
      >
        {selectedRecord && (
          <div style={{ textAlign: 'center', padding: '20px 0' }}>
            <Title level={4}>订单金额</Title>
            <Title level={2} style={{ color: '#ff4d4f' }}>¥{selectedRecord.amount}</Title>
            <Divider />
            <div style={{ marginBottom: '20px' }}>
              <QRCode value={paymentQrCode} size={200} />
            </div>
            <Paragraph type="secondary">
              请使用支付宝扫描二维码完成支付
            </Paragraph>
            <Space direction="vertical" size="small" style={{ width: '100%' }}>
              <Text>订单号: <Text code>{selectedRecord.order_no}</Text></Text>
              <Text>获得灵值: <Text strong>{selectedRecord.total_lingzhi}</Text></Text>
            </Space>
          </div>
        )}
      </Modal>

      {/* 详情弹窗 */}
      <Modal
        title="充值详情"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setDetailModalVisible(false)}>
            关闭
          </Button>
        ]}
        width={600}
      >
        {selectedRecord && (
          <div>
            <Divider>订单信息</Divider>
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <Row>
                <Col span={8}><Text type="secondary">订单号:</Text></Col>
                <Col span={16}><Text code>{selectedRecord.order_no}</Text></Col>
              </Row>
              <Row>
                <Col span={8}><Text type="secondary">充值金额:</Text></Col>
                <Col span={16}><Text strong style={{ fontSize: '18px' }}>¥{selectedRecord.amount}</Text></Col>
              </Row>
              <Row>
                <Col span={8}><Text type="secondary">基础灵值:</Text></Col>
                <Col span={16}><Text>{selectedRecord.base_lingzhi}</Text></Col>
              </Row>
              <Row>
                <Col span={8}><Text type="secondary">赠送灵值:</Text></Col>
                <Col span={16}><Text style={{ color: '#52c41a' }}>+{selectedRecord.bonus_lingzhi}</Text></Col>
              </Row>
              <Row>
                <Col span={8}><Text type="secondary">总计灵值:</Text></Col>
                <Col span={16}><Text strong style={{ fontSize: '18px', color: '#52c41a' }}>{selectedRecord.total_lingzhi}</Text></Col>
              </Row>
              <Row>
                <Col span={8}><Text type="secondary">支付方式:</Text></Col>
                <Col span={16}>{getPaymentMethodTag(selectedRecord.payment_method)}</Col>
              </Row>
              <Row>
                <Col span={8}><Text type="secondary">支付状态:</Text></Col>
                <Col span={16}>{getStatusTag(selectedRecord.payment_status)}</Col>
              </Row>
              <Row>
                <Col span={8}><Text type="secondary">创建时间:</Text></Col>
                <Col span={16}>{new Date(selectedRecord.created_at).toLocaleString('zh-CN')}</Col>
              </Row>
              {selectedRecord.payment_time && (
                <Row>
                  <Col span={8}><Text type="secondary">支付时间:</Text></Col>
                  <Col span={16}>{new Date(selectedRecord.payment_time).toLocaleString('zh-CN')}</Col>
                </Row>
              )}
              {selectedRecord.transaction_id && (
                <Row>
                  <Col span={8}><Text type="secondary">交易流水号:</Text></Col>
                  <Col span={16}><Text code>{selectedRecord.transaction_id}</Text></Col>
                </Row>
              )}
            </Space>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default RechargeHistory;

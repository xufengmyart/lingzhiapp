import React, { useState, useEffect } from 'react';
import { 
  Card, Table, Button, Modal, Form, Input, Select, Space, Typography, 
  Tag, Image, message, Row, Col, Popconfirm, Tooltip, Switch, DatePicker,
  Upload, Divider
} from 'antd';
import { 
  PlusOutlined, EditOutlined, DeleteOutlined, EyeOutlined,
  CheckOutlined, CloseOutlined, UploadOutlined, ReloadOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { TextArea } = Input;
const { RangePicker } = DatePicker;

interface Article {
  id: number;
  title: string;
  slug: string;
  summary: string;
  content: string;
  category_id: number;
  category_name?: string;
  author_id?: number;
  author_name?: string;
  cover_image?: string;
  status: 'draft' | 'pending' | 'published' | 'rejected';
  is_pinned: boolean;
  is_featured: boolean;
  view_count: number;
  like_count: number;
  comment_count: number;
  published_at?: string;
  created_at: string;
  updated_at: string;
}

interface Category {
  id: number;
  name: string;
  slug: string;
}

const AdminArticleManagement: React.FC = () => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [statusFilter, setStatusFilter] = useState<string | undefined>();
  const [categoryFilter, setCategoryFilter] = useState<number | undefined>();

  // 文章编辑/创建模态框
  const [modalVisible, setModalVisible] = useState(false);
  const [modalMode, setModalMode] = useState<'create' | 'edit'>('create');
  const [currentArticle, setCurrentArticle] = useState<Partial<Article>>({});
  const [form] = Form.useForm();

  // 拒绝原因模态框
  const [rejectModalVisible, setRejectModalVisible] = useState(false);
  const [rejectingArticleId, setRejectingArticleId] = useState<number | null>(null);
  const [rejectReason, setRejectReason] = useState('');
  const [rejectForm] = Form.useForm();

  // 预览模态框
  const [previewVisible, setPreviewVisible] = useState(false);
  const [previewArticle, setPreviewArticle] = useState<Article | null>(null);

  const API_BASE = '/api';

  // 加载文章列表
  const loadArticles = async () => {
    setLoading(true);
    try {
      const params: any = {
        page,
        page_size: pageSize,
      };
      if (statusFilter) params.status = statusFilter;
      if (categoryFilter) params.category_id = categoryFilter;

      const response = await axios.get(`${API_BASE}/admin/news/articles`, { params });
      
      if (response.data.success) {
        setArticles(response.data.data || []);
        setTotal(response.data.pagination?.total || 0);
      }
    } catch (error) {
      message.error('加载文章列表失败');
      console.error('加载文章列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 加载分类列表
  const loadCategories = async () => {
    try {
      const response = await axios.get(`${API_BASE}/v9/news/categories`);
      if (response.data.success) {
        setCategories(response.data.data || []);
      }
    } catch (error) {
      console.error('加载分类失败:', error);
    }
  };

  // 创建文章
  const handleCreate = () => {
    setModalMode('create');
    setCurrentArticle({});
    form.resetFields();
    setModalVisible(true);
  };

  // 编辑文章
  const handleEdit = (article: Article) => {
    setModalMode('edit');
    setCurrentArticle(article);
    form.setFieldsValue({
      title: article.title,
      slug: article.slug,
      content: article.content,
      summary: article.summary,
      category_id: article.category_id,
      author_name: article.author_name,
      cover_image: article.cover_image,
      is_pinned: article.is_pinned,
      is_featured: article.is_featured,
      status: article.status,
    });
    setModalVisible(true);
  };

  // 保存文章
  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      const data = {
        ...values,
        author_id: 1, // TODO: 从当前用户获取
      };

      if (modalMode === 'create') {
        await axios.post(`${API_BASE}/admin/news/articles`, data);
        message.success('文章创建成功');
      } else {
        await axios.put(`${API_BASE}/admin/news/articles/${currentArticle.id}`, data);
        message.success('文章更新成功');
      }

      setModalVisible(false);
      loadArticles();
    } catch (error) {
      message.error(modalMode === 'create' ? '创建文章失败' : '更新文章失败');
      console.error('保存文章失败:', error);
    }
  };

  // 删除文章
  const handleDelete = async (id: number) => {
    try {
      await axios.delete(`${API_BASE}/admin/news/articles/${id}`);
      message.success('文章删除成功');
      loadArticles();
    } catch (error) {
      message.error('删除文章失败');
      console.error('删除文章失败:', error);
    }
  };

  // 审核通过
  const handleApprove = async (id: number) => {
    try {
      await axios.put(`${API_BASE}/admin/news/articles/${id}/approve`);
      message.success('文章审核通过');
      loadArticles();
    } catch (error) {
      message.error('审核失败');
      console.error('审核失败:', error);
    }
  };

  // 审核拒绝
  const handleReject = (id: number) => {
    setRejectingArticleId(id);
    setRejectReason('');
    rejectForm.resetFields();
    setRejectModalVisible(true);
  };

  // 确认拒绝
  const confirmReject = async () => {
    try {
      const values = await rejectForm.validateFields();
      await axios.put(`${API_BASE}/admin/news/articles/${rejectingArticleId}/reject`, {
        reason: values.reason,
      });
      message.success('文章已拒绝');
      setRejectModalVisible(false);
      loadArticles();
    } catch (error) {
      message.error('拒绝失败');
      console.error('拒绝失败:', error);
    }
  };

  // 预览文章
  const handlePreview = (article: Article) => {
    setPreviewArticle(article);
    setPreviewVisible(true);
  };

  // 刷新列表
  const handleRefresh = () => {
    loadArticles();
  };

  useEffect(() => {
    loadArticles();
    loadCategories();
  }, [page, pageSize, statusFilter, categoryFilter]);

  // 表格列定义
  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      width: 200,
      ellipsis: true,
    },
    {
      title: '分类',
      dataIndex: 'category_name',
      key: 'category_name',
      width: 120,
    },
    {
      title: '作者',
      dataIndex: 'author_name',
      key: 'author_name',
      width: 120,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        const statusMap: Record<string, { color: string; text: string }> = {
          draft: { color: 'default', text: '草稿' },
          pending: { color: 'warning', text: '待审核' },
          published: { color: 'success', text: '已发布' },
          rejected: { color: 'error', text: '已拒绝' },
        };
        const { color, text } = statusMap[status] || { color: 'default', text: status };
        return <Tag color={color}>{text}</Tag>;
      },
    },
    {
      title: '置顶/推荐',
      key: 'featured',
      width: 120,
      render: (_, record: Article) => (
        <Space>
          {record.is_pinned && <Tag color="gold">置顶</Tag>}
          {record.is_featured && <Tag color="purple">推荐</Tag>}
        </Space>
      ),
    },
    {
      title: '浏览/点赞',
      key: 'stats',
      width: 120,
      render: (_, record: Article) => (
        <Space>
          <Text type="secondary">{record.view_count} 👁️</Text>
          <Text type="secondary">{record.like_count} ❤️</Text>
        </Space>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
    },
    {
      title: '操作',
      key: 'actions',
      width: 280,
      fixed: 'right',
      render: (_, record: Article) => (
        <Space size="small">
          <Tooltip title="预览">
            <Button 
              type="link" 
              size="small" 
              icon={<EyeOutlined />} 
              onClick={() => handlePreview(record)}
            />
          </Tooltip>
          <Tooltip title="编辑">
            <Button 
              type="link" 
              size="small" 
              icon={<EditOutlined />} 
              onClick={() => handleEdit(record)}
            />
          </Tooltip>
          {record.status === 'pending' && (
            <>
              <Tooltip title="通过">
                <Button 
                  type="link" 
                  size="small" 
                  icon={<CheckOutlined />} 
                  onClick={() => handleApprove(record.id)}
                />
              </Tooltip>
              <Tooltip title="拒绝">
                <Button 
                  type="link" 
                  size="small" 
                  danger
                  icon={<CloseOutlined />} 
                  onClick={() => handleReject(record.id)}
                />
              </Tooltip>
            </>
          )}
          <Popconfirm
            title="确定删除这篇文章吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Tooltip title="删除">
              <Button 
                type="link" 
                size="small" 
                danger
                icon={<DeleteOutlined />} 
              />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>文章管理</Title>
      
      {/* 筛选栏 */}
      <Card style={{ marginBottom: 16 }}>
        <Row gutter={16} align="middle">
          <Col>
            <Select
              style={{ width: 150 }}
              placeholder="筛选状态"
              allowClear
              onChange={setStatusFilter}
              value={statusFilter}
            >
              <Option value="draft">草稿</Option>
              <Option value="pending">待审核</Option>
              <Option value="published">已发布</Option>
              <Option value="rejected">已拒绝</Option>
            </Select>
          </Col>
          <Col>
            <Select
              style={{ width: 200 }}
              placeholder="筛选分类"
              allowClear
              onChange={setCategoryFilter}
              value={categoryFilter}
            >
              {categories.map(cat => (
                <Option key={cat.id} value={cat.id}>{cat.name}</Option>
              ))}
            </Select>
          </Col>
          <Col flex={1} />
          <Col>
            <Space>
              <Button icon={<ReloadOutlined />} onClick={handleRefresh}>
                刷新
              </Button>
              <Button 
                type="primary" 
                icon={<PlusOutlined />} 
                onClick={handleCreate}
              >
                新建文章
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 文章列表 */}
      <Card>
        <Table
          columns={columns}
          dataSource={articles}
          rowKey="id"
          loading={loading}
          pagination={{
            current: page,
            pageSize,
            total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 篇`,
            onChange: (page, pageSize) => {
              setPage(page);
              setPageSize(pageSize);
            },
          }}
          scroll={{ x: 1500 }}
        />
      </Card>

      {/* 编辑/创建模态框 */}
      <Modal
        title={modalMode === 'create' ? '创建文章' : '编辑文章'}
        open={modalVisible}
        onOk={handleSave}
        onCancel={() => setModalVisible(false)}
        width={800}
        okText="保存"
        cancelText="取消"
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            is_pinned: false,
            is_featured: false,
            status: 'draft',
          }}
        >
          <Form.Item
            label="标题"
            name="title"
            rules={[{ required: true, message: '请输入文章标题' }]}
          >
            <Input placeholder="请输入文章标题" />
          </Form.Item>

          <Form.Item
            label="URL 别名 (slug)"
            name="slug"
            rules={[{ required: true, message: '请输入 URL 别名' }]}
          >
            <Input placeholder="请输入 URL 别名（英文，用于生成链接）" />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="分类"
                name="category_id"
                rules={[{ required: true, message: '请选择分类' }]}
              >
                <Select placeholder="请选择分类">
                  {categories.map(cat => (
                    <Option key={cat.id} value={cat.id}>{cat.name}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="作者"
                name="author_name"
                rules={[{ required: true, message: '请输入作者名称' }]}
              >
                <Input placeholder="请输入作者名称" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            label="摘要"
            name="summary"
          >
            <TextArea rows={3} placeholder="请输入文章摘要" />
          </Form.Item>

          <Form.Item
            label="内容"
            name="content"
            rules={[{ required: true, message: '请输入文章内容' }]}
          >
            <TextArea rows={10} placeholder="请输入文章内容（支持 HTML）" />
          </Form.Item>

          <Form.Item
            label="封面图片"
            name="cover_image"
          >
            <Input placeholder="请输入封面图片 URL" />
          </Form.Item>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                label="状态"
                name="status"
              >
                <Select>
                  <Option value="draft">草稿</Option>
                  <Option value="pending">待审核</Option>
                  <Option value="published">已发布</Option>
                  <Option value="rejected">已拒绝</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="置顶"
                name="is_pinned"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="推荐"
                name="is_featured"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>

      {/* 拒绝原因模态框 */}
      <Modal
        title="拒绝文章"
        open={rejectModalVisible}
        onOk={confirmReject}
        onCancel={() => setRejectModalVisible(false)}
        okText="确认拒绝"
        cancelText="取消"
      >
        <Form form={rejectForm}>
          <Form.Item
            label="拒绝原因"
            name="reason"
            rules={[{ required: true, message: '请输入拒绝原因' }]}
          >
            <TextArea 
              rows={4} 
              placeholder="请输入拒绝原因，将通知给作者"
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
            />
          </Form.Item>
        </Form>
      </Modal>

      {/* 预览模态框 */}
      <Modal
        title="文章预览"
        open={previewVisible}
        onCancel={() => setPreviewVisible(false)}
        footer={[
          <Button key="close" onClick={() => setPreviewVisible(false)}>
            关闭
          </Button>,
        ]}
        width={800}
      >
        {previewArticle && (
          <div>
            <Title level={2}>{previewArticle.title}</Title>
            <Divider />
            {previewArticle.cover_image && (
              <div style={{ marginBottom: 16 }}>
                <Image src={previewArticle.cover_image} alt={previewArticle.title} />
              </div>
            )}
            <div 
              dangerouslySetInnerHTML={{ __html: previewArticle.content }}
              style={{ minHeight: 200 }}
            />
          </div>
        )}
      </Modal>
    </div>
  );
};

export default AdminArticleManagement;

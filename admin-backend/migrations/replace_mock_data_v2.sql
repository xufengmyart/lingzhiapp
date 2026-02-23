-- 清除现有的模拟数据
DELETE FROM private_resources WHERE deleted_at IS NULL;

-- 插入真实的私有资源数据（匿名化处理）
INSERT INTO private_resources (user_id, resource_name, resource_type, department, contact_name, contact_phone, contact_email, position, description, authorization_status, can_solve, risk_level, verification_status, visibility, valid_from, valid_until) VALUES
(10, '政府招商引资资源', 'government', '经济发展局', '用户10', '13900000001', 'user10@gov.cn', '项目主任', '负责招商引资项目对接与审批流程', 'authorized', '企业注册、政策咨询、项目落地支持', 'low', 'verified', 'matchable', '2024-01-01', '2025-12-31'),
(11, '企业供应链资源', 'enterprise', '采购部', '用户11', '13900000002', 'user11@company.com', '采购总监', '拥有完整的供应链资源和优质供应商网络', 'authorized', '原材料采购、物流配送、供应商管理', 'medium', 'verified', 'matchable', '2024-02-01', '2025-12-31'),
(12, '人脉资源-投资圈', 'personal', '投资公司', '用户12', '13900000003', 'user12@investment.com', '投资经理', '广泛的投资人脉资源，熟悉投资流程', 'pending', '融资对接、项目评估、商业计划书优化', 'high', 'pending', 'private', '2024-03-01', '2025-12-31'),
(13, '技术研发资源', 'enterprise', '研发中心', '用户13', '13900000004', 'user13@tech.com', '技术总监', '拥有强大的技术研发团队和专利资源', 'authorized', '技术咨询、产品开发、专利申请', 'low', 'verified', 'matchable', '2024-04-01', '2025-12-31'),
(14, '市场推广资源', 'enterprise', '市场部', '用户14', '13900000005', 'user14@marketing.com', '市场总监', '丰富的市场推广经验和媒体资源', 'authorized', '品牌推广、营销策划、渠道拓展', 'medium', 'verified', 'matchable', '2024-05-01', '2025-12-31'),
(15, '法律咨询资源', 'other', '律师事务所', '用户15', '13900000006', 'user15@law.com', '律师', '专业的法律咨询服务，擅长企业合规', 'authorized', '合同审核、法律咨询、知识产权保护', 'low', 'verified', 'matchable', '2024-06-01', '2025-12-31'),
(16, '人才招聘资源', 'enterprise', '人力资源部', '用户16', '13900000007', 'user16@hr.com', '人力资源总监', '丰富的人才资源和招聘渠道', 'authorized', '人才招聘、猎头服务、团队建设', 'low', 'verified', 'matchable', '2024-07-01', '2025-12-31'),
(17, '政府补贴资源', 'government', '财政局', '用户17', '13900000008', 'user17@finance.gov.cn', '科长', '熟悉各类政府补贴政策和申请流程', 'pending', '补贴咨询、政策解读、申请代理', 'low', 'pending', 'private', '2024-08-01', '2025-12-31'),
(18, '银行融资资源', 'enterprise', '信贷部', '用户18', '13900000009', 'user18@bank.com', '信贷经理', '专业的企业融资服务，与多家银行有合作', 'authorized', '企业贷款、融资担保、财务规划', 'medium', 'verified', 'matchable', '2024-09-01', '2025-12-31'),
(19, '跨境电商资源', 'enterprise', '电商部', '用户19', '13900000010', 'user19@ecommerce.com', '运营总监', '丰富的跨境电商运营经验和海外资源', 'authorized', '海外市场拓展、跨境电商运营、物流配送', 'high', 'verified', 'matchable', '2024-10-01', '2025-12-31');

-- 更新商家资源数据
UPDATE merchants SET 
  contact_person = '商家1',
  contact_phone = '13800000001',
  merchant_type = '文创产品',
  business_scope = '文创产品设计、生产、销售'
WHERE id = 1;

UPDATE merchants SET 
  contact_person = '商家2',
  contact_phone = '13800000002',
  merchant_type = '非遗传承',
  business_scope = '非遗产品开发、展示、销售'
WHERE id = 2;

UPDATE merchants SET 
  contact_person = '商家3',
  contact_phone = '13800000003',
  merchant_type = '文化展览',
  business_scope = '文化活动策划、展览服务'
WHERE id = 3;

UPDATE merchants SET 
  contact_person = '商家4',
  contact_phone = '13800000004',
  merchant_type = '餐饮服务',
  business_scope = '特色餐饮、文化主题餐厅'
WHERE id = 4;

UPDATE merchants SET 
  contact_person = '商家5',
  contact_phone = '13800000005',
  merchant_type = '民俗体验',
  business_scope = '民俗文化体验、手工艺制作'
WHERE id = 5;

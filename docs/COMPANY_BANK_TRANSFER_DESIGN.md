# 公司公户收款功能设计文档

**版本**: v1.0
**创建日期**: 2026年
**开发团队**: 灵值生态园产品团队

---

## 功能概述

为支持企业用户和大额充值需求，灵值生态园新增公司公户收款功能。用户在选择充值时，可以选择通过公司公户转账的方式进行支付，上传转账凭证后，由管理员审核通过后完成充值。

## 流程设计

### 1. 充值流程

```
用户选择充值档位
    ↓
选择支付方式（在线支付 / 公司公户转账）
    ↓
[如果选择公司公户转账]
    ↓
创建充值订单（状态：待付款）
    ↓
系统显示公司收款账户信息
    ↓
用户通过银行转账到公司账户
    ↓
用户上传转账凭证（截图/照片）
    ↓
[订单状态：待审核]
    ↓
管理员审核转账凭证
    ↓
[如果审核通过]
    ↓
订单状态更新为：已完成
用户灵值余额增加
发送充值成功通知
    ↓
[如果审核不通过]
    ↓
订单状态更新为：审核失败
发送审核失败通知
用户可以重新上传凭证
```

### 2. 支付方式对比

| 支付方式 | 充值金额 | 到账时间 | 手续费 | 适用场景 |
|---------|---------|---------|--------|---------|
| 在线支付（微信/支付宝） | 小额（<10000元） | 即时 | 0.6% | 个人用户、小额充值 |
| 公司公户转账 | 不限 | 1-3个工作日 | 银行手续费 | 企业用户、大额充值 |

### 3. 公司收款账户信息

**公司信息**：
- 公司名称：陕西媄月商业艺术有限责任公司
- 统一社会信用代码：[待填写]

**银行账户信息**：
- 开户银行：[待填写]
- 银行账号：[待填写]
- 开户名：陕西媄月商业艺术有限责任公司

**转账备注**：
- 备注格式：LZ充值-{手机号}-{订单号}
- 示例：LZ充值-13800138000-ORD202602011200001

## 数据库设计

### 1. 公司收款账户表（company_accounts）

```sql
CREATE TABLE company_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_name VARCHAR(200) NOT NULL,          -- 账户名称
    account_number VARCHAR(50) NOT NULL,         -- 账号
    bank_name VARCHAR(200) NOT NULL,             -- 开户银行
    bank_branch VARCHAR(200),                    -- 开户支行
    company_name VARCHAR(200) NOT NULL,          -- 公司名称
    company_credit_code VARCHAR(50),             -- 统一社会信用代码
    account_type VARCHAR(20) NOT NULL,           -- 账户类型（basic/primary）
    is_active BOOLEAN DEFAULT TRUE,              -- 是否启用
    sort_order INTEGER DEFAULT 0,                -- 排序
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. 转账凭证表（transfer_vouchers）

```sql
CREATE TABLE transfer_vouchers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recharge_record_id INTEGER NOT NULL,         -- 充值记录ID
    user_id INTEGER NOT NULL,                    -- 用户ID
    image_url VARCHAR(500) NOT NULL,             -- 凭证图片URL
    transfer_amount DECIMAL(10, 2) NOT NULL,     -- 转账金额
    transfer_time TIMESTAMP,                     -- 转账时间
    transfer_account VARCHAR(200),               -- 转账账户
    remark TEXT,                                 -- 备注
    audit_status VARCHAR(20) DEFAULT 'pending',  -- 审核状态（pending/approved/rejected）
    audit_user_id INTEGER,                       -- 审核人ID
    audit_time TIMESTAMP,                        -- 审核时间
    audit_remark TEXT,                           -- 审核备注
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recharge_record_id) REFERENCES recharge_records(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (audit_user_id) REFERENCES admins(id)
);
```

### 3. 扩展充值记录表（recharge_records）

```sql
-- 新增字段
ALTER TABLE recharge_records ADD COLUMN payment_method VARCHAR(20) DEFAULT 'online';  -- 支付方式（online/bank_transfer）
ALTER TABLE recharge_records ADD COLUMN payment_status VARCHAR(20) DEFAULT 'pending'; -- 支付状态（pending/paid/failed/cancelled）
ALTER TABLE recharge_records ADD COLUMN voucher_id INTEGER;                          -- 转账凭证ID
ALTER TABLE recharge_records ADD COLUMN audit_status VARCHAR(20);                    -- 审核状态（pending/approved/rejected）
ALTER TABLE recharge_records ADD COLUMN bank_info TEXT;                               -- 银行信息
```

## API接口设计

### 1. 获取公司收款账户信息

**接口**：`GET /api/company/accounts`
**权限**：无需登录
**功能**：获取公司收款账户信息列表

**请求示例**：
```http
GET /api/company/accounts
```

**响应示例**：
```json
{
    "success": true,
    "data": [
        {
            "id": 1,
            "account_name": "陕西媄月商业艺术有限责任公司",
            "account_number": "6222 0200 0100 1234 567",
            "bank_name": "中国工商银行",
            "bank_branch": "西安分行高新区支行",
            "company_name": "陕西媄月商业艺术有限责任公司",
            "company_credit_code": "91610131MA6XXXXXX",
            "account_type": "primary"
        }
    ]
}
```

### 2. 创建充值订单（支持选择支付方式）

**接口**：`POST /api/recharge/create-order`
**权限**：需要登录
**功能**：创建充值订单，支持选择支付方式

**请求示例**：
```json
{
    "tier_id": 1,
    "payment_method": "bank_transfer"
}
```

**响应示例**：
```json
{
    "success": true,
    "message": "订单创建成功",
    "data": {
        "order_no": "ORD202602011200001",
        "amount": 99.00,
        "total_lingzhi": 1100,
        "payment_method": "bank_transfer",
        "company_accounts": [
            {
                "account_name": "陕西媄月商业艺术有限责任公司",
                "account_number": "6222 0200 0100 1234 567",
                "bank_name": "中国工商银行",
                "bank_branch": "西安分行高新区支行"
            }
        ],
        "transfer_remark": "LZ充值-13800138000-ORD202602011200001"
    }
}
```

### 3. 上传转账凭证

**接口**：`POST /api/recharge/upload-voucher`
**权限**：需要登录
**功能**：用户上传转账凭证图片

**请求示例**：
```http
POST /api/recharge/upload-voucher
Content-Type: multipart/form-data

order_no: ORD202602011200001
voucher_file: [文件]
transfer_amount: 99.00
transfer_time: 2026-02-01 12:30:00
transfer_account: 6217 0036 0000 1234 567
remark: 已转账
```

**响应示例**：
```json
{
    "success": true,
    "message": "凭证上传成功，等待审核",
    "data": {
        "voucher_id": 1,
        "audit_status": "pending"
    }
}
```

### 4. 获取转账凭证详情

**接口**：`GET /api/recharge/voucher/<voucher_id>`
**权限**：需要登录
**功能**：获取转账凭证的详细信息

**请求示例**：
```http
GET /api/recharge/voucher/1
```

**响应示例**：
```json
{
    "success": true,
    "data": {
        "id": 1,
        "recharge_record_id": 1,
        "image_url": "https://example.com/vouchers/xxx.jpg",
        "transfer_amount": 99.00,
        "transfer_time": "2026-02-01 12:30:00",
        "transfer_account": "6217 0036 0000 1234 567",
        "audit_status": "pending",
        "created_at": "2026-02-01 12:35:00"
    }
}
```

### 5. 管理员：获取待审核凭证列表

**接口**：`GET /api/admin/vouchers/pending`
**权限**：需要管理员登录
**功能**：获取待审核的转账凭证列表

**请求示例**：
```http
GET /api/admin/vouchers/pending?page=1&page_size=20
```

**响应示例**：
```json
{
    "success": true,
    "data": {
        "total": 5,
        "page": 1,
        "page_size": 20,
        "records": [
            {
                "id": 1,
                "user_id": 1,
                "user_phone": "13800138000",
                "user_name": "张三",
                "recharge_record_id": 1,
                "order_no": "ORD202602011200001",
                "image_url": "https://example.com/vouchers/xxx.jpg",
                "transfer_amount": 99.00,
                "transfer_time": "2026-02-01 12:30:00",
                "transfer_account": "6217 0036 0000 1234 567",
                "created_at": "2026-02-01 12:35:00"
            }
        ]
    }
}
```

### 6. 管理员：审核转账凭证

**接口**：`POST /api/admin/vouchers/<voucher_id>/audit`
**权限**：需要管理员登录
**功能**：管理员审核转账凭证，通过或拒绝

**请求示例**：
```json
{
    "audit_status": "approved",
    "audit_remark": "审核通过"
}
```

**响应示例**：
```json
{
    "success": true,
    "message": "审核成功",
    "data": {
        "voucher_id": 1,
        "audit_status": "approved",
        "user_lingzhi": 1100
    }
}
```

### 7. 管理员：获取所有转账凭证

**接口**：`GET /api/admin/vouchers`
**权限**：需要管理员登录
**功能**：获取所有转账凭证记录

**请求示例**：
```http
GET /api/admin/vouchers?audit_status=pending&page=1&page_size=20
```

**响应示例**：
```json
{
    "success": true,
    "data": {
        "total": 100,
        "page": 1,
        "page_size": 20,
        "records": [...]
    }
}
```

## 智能体对话支持

### 用户询问如何充值

"您可以选择以下充值方式：

**在线支付**：
- 支持微信支付、支付宝支付
- 充值即时到账
- 适合小额充值（10000元以下）

**公司公户转账**：
- 通过银行转账到公司账户
- 1-3个工作日到账
- 适合企业用户和大额充值
- 需要上传转账凭证，审核通过后到账

您想选择哪种充值方式呢？"

### 用户询问公户转账流程

"公司公户转账的充值流程如下：

1. **选择充值档位**：选择您需要的充值包
2. **选择支付方式**：选择"公司公户转账"
3. **查看账户信息**：系统会显示公司的收款账户信息
4. **银行转账**：通过网银或手机银行转账到公司账户
5. **转账备注**：请务必在转账备注中填写：LZ充值-{手机号}-{订单号}
6. **上传凭证**：转账成功后，上传转账凭证（截图或照片）
7. **等待审核**：我们会在1个工作日内审核您的凭证
8. **充值到账**：审核通过后，灵值会立即到账

**公司收款账户信息**：
- 开户银行：中国工商银行
- 银行账号：6222 0200 0100 1234 567
- 开户名：陕西媄月商业艺术有限责任公司

如果您需要帮助，请随时联系我们的客服。"

### 用户询问审核时间

"转账凭证的审核时间为：
- 工作日：24小时内审核完成
- 节假日：顺延至下一个工作日

审核结果会通过短信通知您，您也可以在充值记录中查看审核状态。

如果审核不通过，您可以重新上传凭证，我们会详细说明不通过的原因。"

## 注意事项

### 1. 转账备注规范

用户在银行转账时，必须在备注中填写指定格式：
- 格式：`LZ充值-{手机号}-{订单号}`
- 示例：`LZ充值-13800138000-ORD202602011200001`

### 2. 凭证要求

- 支持的格式：JPG、PNG、PDF
- 文件大小：不超过5MB
- 清晰度要求：能够清楚看到转账金额、转账时间、收款账户

### 3. 审核标准

**审核通过**：
- 转账金额与订单金额一致
- 转账时间在订单创建后7天内
- 收款账户为公司账户
- 凭证清晰可辨

**审核不通过**：
- 转账金额与订单金额不符
- 转账时间超过7天
- 收款账户不是公司账户
- 凭证模糊不清
- 重复提交

### 4. 退款政策

- 如果审核不通过，用户可以重新上传凭证
- 如果需要退款，请联系客服处理
- 退款将在3-5个工作日内原路返回

## 后续优化

1. **自动识别**：集成OCR技术，自动识别转账凭证信息
2. **实时到账**：对接银行系统，实现实时到账查询
3. **发票开具**：支持在线开具发票
4. **批量审核**：管理员可以批量审核凭证
5. **消息通知**：通过短信、邮件通知审核结果

---

**文档版本**: v1.0
**创建日期**: 2026年
**维护团队**: 灵值生态园产品团队

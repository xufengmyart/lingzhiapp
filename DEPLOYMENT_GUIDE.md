# 生产环境部署指南

## 部署前准备

### 1. 检查部署文件
确认以下文件已经创建：

#### 后端文件
- `admin-backend/routes/share.py` - 分享接口
- `admin-backend/routes/referral_management.py` - 推荐关系管理接口
- `admin-backend/routes/news_articles.py` - 文章管理接口（已更新）
- `admin-backend/scripts/create_share_stats_table.py` - 分享统计表创建脚本

#### 前端文件
- `web-app/src/pages/AdminArticleManagement.tsx` - 文章管理界面
- `web-app/src/pages/ArticleDetail.tsx` - 文章详情页
- `web-app/src/components/ShareModal.tsx` - 分享弹窗组件
- `web-app/src/services/articleApi.ts` - 前端API服务
- `web-app/src/utils/notification.ts` - 通知提示工具

### 2. 数据库准备
在生产环境创建分享统计表：

```bash
ssh root@meiyueart.com
cd /app/meiyueart-backend
python3 << EOF
import sqlite3
conn = sqlite3.connect('data/lingzhi_ecosystem.db')
cursor = conn.cursor()

# 创建分享统计表
cursor.execute('''
    CREATE TABLE IF NOT EXISTS share_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        article_id INTEGER NOT NULL,
        share_type TEXT NOT NULL,
        share_url TEXT NOT NULL,
        referral_code TEXT,
        platform TEXT NOT NULL,
        share_count INTEGER DEFAULT 1,
        click_count INTEGER DEFAULT 0,
        registration_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (article_id) REFERENCES news_articles(id)
    )
''')

# 创建索引
cursor.execute('CREATE INDEX IF NOT EXISTS idx_share_stats_user_id ON share_stats(user_id)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_share_stats_article_id ON share_stats(article_id)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_share_stats_referral_code ON share_stats(referral_code)')

conn.commit()
print("分享统计表创建成功")
conn.close()
EOF
```

## 部署步骤

### 步骤1：部署后端代码

```bash
# 1. 备份当前后端代码
ssh root@meiyueart.com "cd /app/meiyueart-backend && tar -czf ../backend_backup_$(date +%Y%m%d_%H%M%S).tar.gz ."

# 2. 上传后端代码
rsync -avz --delete \
  -e "ssh -p 22" \
  /workspace/projects/admin-backend/ \
  root@meiyueart.com:/app/meiyueart-backend/

# 3. 重启后端服务
ssh root@meiyueart.com "systemctl restart lingzhi-backend"
```

### 步骤2：部署前端代码

```bash
# 1. 构建前端
cd /workspace/projects/web-app
npm install
npm run build

# 2. 上传前端代码
rsync -avz --delete \
  -e "ssh -p 22" \
  /workspace/projects/web-app/dist/ \
  root@meiyueart.com:/var/www/meiyueart.com/

# 3. 重启Nginx
ssh root@meiyueart.com "nginx -s reload"
```

### 步骤3：验证部署

```bash
# 1. 检查后端服务状态
ssh root@meiyueart.com "systemctl status lingzhi-backend"

# 2. 检查Nginx状态
ssh root@meiyueart.com "systemctl status nginx"

# 3. 测试API接口
curl https://meiyueart.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123"}'

# 4. 测试前端访问
curl -I https://meiyueart.com
```

## 功能验证

### 1. 后端接口测试

#### 测试分享接口
```bash
# 获取token
TOKEN=$(curl -s https://meiyueart.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['token'])")

# 测试分享接口
curl -s "https://meiyueart.com/api/articles/1/share?type=link" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

#### 测试推荐关系管理接口
```bash
# 获取推荐关系
curl -s "https://meiyueart.com/api/admin/referral/relationships?limit=5" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# 获取分享统计摘要
curl -s "https://meiyueart.com/api/admin/share/summary" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### 2. 前端功能测试

#### 测试文章管理界面
1. 访问: `https://meiyueart.com/admin/article-management`
2. 登录管理员账号
3. 测试创建文章功能
4. 测试编辑文章功能
5. 测试审核功能
6. 测试删除功能

#### 测试文章详情页和分享功能
1. 访问任意文章详情页
2. 点击"分享"按钮
3. 测试分享弹窗显示
4. 测试复制链接功能
5. 测试不同分享方式
6. 测试分享成功提示

### 3. 推荐关系测试

#### 测试推荐关系绑定
1. 用户A登录系统
2. 用户A分享一篇文章
3. 获取分享链接（含推荐码）
4. 用户B通过分享链接注册
5. 验证用户B的推荐人是否为用户A
6. 验证用户B是否收到推荐关系绑定成功通知

#### 测试推荐关系管理（超级管理员）
1. 使用超级管理员账号登录
2. 访问推荐关系管理界面
3. 测试查看推荐关系
4. 测试修改推荐关系
5. 测试删除推荐关系
6. 测试查看分享统计

## 常见问题

### 问题1：分享接口返回404
**解决方案**：
1. 检查蓝图是否正确注册
2. 检查路由路径是否正确
3. 检查后端服务是否重启

### 问题2：推荐关系管理接口401错误
**解决方案**：
1. 检查Token是否有效
2. 检查用户是否为超级管理员
3. 检查admins表结构

### 问题3：分享统计表不存在
**解决方案**：
1. 手动创建分享统计表
2. 检查数据库连接
3. 检查SQL语法

### 问题4：前端页面无法访问
**解决方案**：
1. 检查前端构建是否成功
2. 检查Nginx配置
3. 检查文件权限

## 回滚方案

### 回滚后端
```bash
ssh root@meiyueart.com
cd /app/meiyueart-backend
tar -xzf ../backend_backup_[TIMESTAMP].tar.gz
systemctl restart lingzhi-backend
```

### 回滚前端
```bash
# 从备份恢复
rsync -avz --delete \
  -e "ssh -p 22" \
  root@meiyueart.com:/var/www/backups/frontend_backup_[TIMESTAMP]/ \
  root@meiyueart.com:/var/www/meiyueart.com/
```

## 部署检查清单

- [ ] 备份生产环境数据
- [ ] 创建分享统计表
- [ ] 部署后端代码
- [ ] 重启后端服务
- [ ] 部署前端代码
- [ ] 重启Nginx
- [ ] 测试后端API接口
- [ ] 测试前端页面
- [ ] 测试分享功能
- [ ] 测试推荐关系绑定
- [ ] 测试推荐关系管理
- [ ] 测试文章审核通知
- [ ] 验证所有功能正常

## 注意事项

1. **数据备份**：部署前务必备份数据库和代码
2. **逐步部署**：先部署后端，验证无误后再部署前端
3. **权限设置**：确保文件权限正确
4. **服务监控**：部署后监控服务状态
5. **回滚准备**：准备好回滚方案

## 联系支持

如遇到问题，请联系：
- 技术支持: support@meiyueart.com
- 紧急联系: 400-XXX-XXXX

---

**部署版本**: v20260223-1700
**文档版本**: 1.0
**最后更新**: 2026-02-23

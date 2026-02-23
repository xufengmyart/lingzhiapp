# 灵值生态园 - 知识库侧边栏部署指南

## 问题说明

当前知识库侧边栏无法加载，API返回404错误：
```
GET https://meiyueart.com/api/v9/knowledge/items 404
```

**根本原因**: 生产环境Nginx配置缺少 `/api` 路径的代理配置。

---

## 解决方案

### 方案一：使用自动化部署脚本（推荐）

#### 1. 更新Nginx配置（快速修复）

```bash
cd /workspace/projects
./scripts/update_nginx.sh
```

这将生成Nginx配置文件并显示应用命令。

#### 2. 登录服务器应用配置

```bash
ssh root@123.56.142.143
```

然后在服务器上执行：

```bash
# 备份当前配置
cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup

# 应用新配置
mkdir -p /etc/nginx/sites-available
mkdir -p /etc/nginx/sites-enabled

# 从本地复制配置文件（在本地执行）
# scp /workspace/projects/web-app/nginx.conf root@123.56.142.143:/tmp/meiyueart_nginx.conf

# 在服务器上执行
cp /tmp/meiyueart_nginx.conf /etc/nginx/sites-available/meiyueart
ln -sf /etc/nginx/sites-available/meiyueart /etc/nginx/sites-enabled/meiyueart

# 测试配置
nginx -t

# 重启Nginx
systemctl reload nginx
```

#### 3. 验证配置

```bash
# 在本地测试
curl http://meiyueart.com/api/v9/knowledge/items

# 应该返回知识库数据
```

---

### 方案二：完整部署（推荐用于首次部署或重大更新）

```bash
cd /workspace/projects
./scripts/deploy.sh
```

选择选项 **4) 完整部署（前端+后端+Nginx）**

这将执行：
1. 构建前端
2. 部署前端到服务器
3. 部署后端到服务器
4. 更新Nginx配置
5. 重启所有服务

---

## Nginx配置说明

### 配置文件位置

本地配置：`/workspace/projects/web-app/nginx.conf`

### 配置内容

```nginx
server {
    listen 80;
    server_name meiyueart.com 123.56.142.143;

    root /var/www/meiyueart.com;
    index index.html;

    # 前端路由支持
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # API代理（关键配置）
    location /api {
        proxy_pass http://127.0.0.1:9000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;

        # 增加超时时间
        proxy_connect_timeout 600;
        proxy_send_timeout 600;
        proxy_read_timeout 600;
    }

    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/javascript application/json;
}
```

### 关键点

1. **API代理配置**：`location /api` 块将 `/api/*` 请求代理到后端 `http://127.0.0.1:9000`
2. **超时配置**：600秒超时，支持长时间AI对话
3. **WebSocket支持**：正确处理 `Upgrade` 和 `Connection` 头

---

## 验证步骤

### 1. 测试API端点

```bash
# 知识库条目
curl http://meiyueart.com/api/v9/knowledge/items

# 知识库搜索
curl http://meiyueart.com/api/v9/knowledge/search?q=签到

# 健康检查
curl http://meiyueart.com/api/health
```

### 2. 测试前端页面

访问：https://meiyueart.com/chat

检查：
- 知识库侧边栏是否显示
- 点击知识项是否能自动提问
- 搜索功能是否正常工作

### 3. 运行测试脚本

```bash
cd /workspace/projects
./scripts/test_knowledge_api.sh
```

---

## 常见问题

### 问题1: API返回404

**原因**: Nginx配置未更新或Nginx未重启

**解决**:
```bash
ssh root@123.56.142.143
nginx -t  # 检查配置
systemctl reload nginx  # 重启Nginx
```

### 问题2: Nginx配置测试失败

**原因**: 配置文件语法错误

**解决**:
```bash
nginx -t  # 查看错误信息
# 根据错误信息修复配置
```

### 问题3: 后端服务未启动

**原因**: 后端Python服务未运行

**解决**:
```bash
ssh root@123.56.142.143
cd /app/meiyueart-backend
source venv/bin/activate
nohup python app.py > /var/www/meiyueart.com/backend.log 2>&1 &
```

### 问题4: HTTPS重定向问题

**原因**: 服务器配置了HTTPS强制重定向

**解决**: 使用HTTPS地址测试
```bash
curl https://meiyueart.com/api/v9/knowledge/items
```

---

## 部署检查清单

- [ ] Nginx配置文件已上传到服务器
- [ ] Nginx配置已启用（创建软链接）
- [ ] Nginx配置测试通过（nginx -t）
- [ ] Nginx已重启（systemctl reload nginx）
- [ ] 后端服务正在运行（监听9000端口）
- [ ] 知识库API返回正确数据
- [ ] 前端页面知识库侧边栏正常显示
- [ ] 知识库搜索功能正常工作
- [ ] 点击知识项能自动提问

---

## 联系支持

如果以上步骤都无法解决问题，请检查：

1. 服务器日志：`/var/log/nginx/error.log`
2. 后端日志：`/var/www/meiyueart.com/backend.log`
3. Nginx配置文件：`/etc/nginx/sites-available/meiyueart`

---

**文档版本**: v1.0
**最后更新**: 2025-02-07

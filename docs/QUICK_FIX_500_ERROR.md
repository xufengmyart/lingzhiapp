# 500 Internal Server Error - 快速修复指南

## 问题原因

通过公网IP访问时出现500错误的根本原因是：

**前端API请求地址配置不正确**

- 前端默认使用 `window.location.origin` 作为API基础地址
- 但前端和后端运行在不同端口
- 导致API请求发送到错误的地址，无法连接到后端服务

## 快速修复（3步解决）

### 方案A：使用自动化脚本（最简单）

```bash
# 1. 给脚本添加执行权限
chmod +x setup-public-access.sh

# 2. 运行脚本
./setup-public-access.sh

# 3. 按提示操作
```

脚本会自动：
- 检测您的公网IP
- 配置后端服务
- 重新构建前端
- 配置正确的API地址
- 开放防火墙端口
- 可选：安装和配置Nginx

### 方案B：手动配置（仅需2步）

#### 步骤1：配置API地址

编辑 `web-app/.env.production`：

```bash
# 将YOUR_PUBLIC_IP替换为您的公网IP
VITE_API_BASE_URL=http://YOUR_PUBLIC_IP:8001
```

#### 步骤2：重新构建前端

```bash
cd web-app
npm run build
```

完成！现在将 `web-app/dist` 目录部署到您的Web服务器即可。

### 方案C：使用Nginx反向代理（推荐生产环境）

详见完整文档：`docs/PUBLIC_DEPLOYMENT.md`

## 验证修复

1. **检查后端是否运行**

```bash
curl http://YOUR_PUBLIC_IP:8001/api/health
```

应该返回：`{"status": "ok"}`

2. **检查前端配置**

在浏览器中打开前端，按 F12 打开开发者工具：
- 切换到 Network 标签
- 尝试登录
- 查看 `/api/login` 请求的URL是否正确（应该是 `http://YOUR_PUBLIC_IP:8001/api/login`）

3. **测试登录**

使用有效的用户名和密码登录，检查是否能成功。

## 常见错误及解决方案

### 错误1: "ERR_CONNECTION_REFUSED"

**原因:** 后端服务未启动或端口被阻止

**解决:**
```bash
# 检查后端是否运行
ps aux | grep "python app.py"

# 如果未运行，启动后端
cd admin-backend
python app.py

# 检查防火墙
sudo ufw allow 8001/tcp
```

### 错误2: "net::ERR_CONNECTION_TIMED_OUT"

**原因:** 云服务商安全组未开放端口

**解决:** 在云服务商控制台（阿里云/腾讯云/AWS等）开放端口 8001

### 错误3: 前端加载，但API返回404

**原因:** API地址配置错误

**解决:** 检查浏览器开发者工具中的请求URL，确认是否为 `http://YOUR_PUBLIC_IP:8001/api/...`

### 错误4: CORS错误

**原因:** 后端CORS配置问题

**解决:** 后端已配置CORS支持所有来源，如果仍有问题：
1. 检查Nginx配置是否正确
2. 确认请求头是否正确

## 需要帮助？

如果以上方案都无法解决：

1. 查看后端日志：`logs/app_backend.log`
2. 查看浏览器控制台错误信息（F12）
3. 确认防火墙和安全组配置
4. 参考：`docs/PUBLIC_DEPLOYMENT.md`

## 推荐部署架构

```
用户浏览器
    ↓
[公网IP:80/443] (Nginx)
    ↓
    ├→ 前端静态文件 (React)
    └→ /api/* → [127.0.0.1:8001] (Flask后端)
```

这种架构的优势：
- 只需开放80和443端口到公网
- 后端服务只监听本地，更安全
- 统一管理HTTPS
- 便于扩展和负载均衡

## 快速命令参考

```bash
# 启动后端
cd admin-backend && python app.py &

# 检查后端状态
curl http://localhost:8001/api/health

# 构建前端
cd web-app && npm run build

# 开放防火墙端口
sudo ufw allow 8001/tcp

# 查看后端日志
tail -f logs/app_backend.log

# 查看Nginx日志
tail -f /var/log/nginx/lingzhi-ecosystem-error.log
```

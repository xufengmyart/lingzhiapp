# 公网IP访问500错误 - 完整解决方案

## 问题描述

用户通过公网IP访问系统时，登录或其他API请求出现500 Internal Server Error。

## 根本原因

**前端API地址配置不正确**

前端默认使用以下逻辑确定API地址：
```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || window.location.origin
```

当用户通过公网IP（如 `http://123.45.67.89`）访问时：
- 前端运行在80端口（Nginx提供静态文件）
- 后端运行在8001端口
- API请求被发送到 `http://123.45.67.89/api/...`
- 但正确的地址应该是 `http://123.45.67.89:8001/api/...`
- 导致请求失败，返回500错误

## 已实施的解决方案

### 1. 智能API地址检测（自动修复）

修改了 `web-app/src/services/api.ts`，添加智能检测逻辑：

```typescript
const getApiBaseURL = (): string => {
  // 优先使用环境变量
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL
  }

  // 尝试从localStorage读取（允许运行时动态配置）
  const customApiURL = localStorage.getItem('apiBaseURL')
  if (customApiURL) {
    return customApiURL
  }

  // 智能检测：如果当前URL不包含:8001，自动修正
  const currentOrigin = window.location.origin
  if (!currentOrigin.includes(':8001')) {
    const url = new URL(currentOrigin)
    if (url.port === '80' || url.port === '443' || !url.port) {
      return `${url.protocol}//${url.hostname}:8001`
    }
  }

  return currentOrigin
}
```

**效果：**
- 如果访问 `http://123.45.67.89`，自动使用 `http://123.45.67.89:8001`
- 如果访问 `http://localhost`，自动使用 `http://localhost:8001`
- 无需手动配置即可正常工作

### 2. API配置页面（手动配置）

创建了 `web-app/src/pages/ApiConfig.tsx`，允许用户在UI中配置API地址。

**访问方式：**
- 登录页面底部有"API配置"链接
- 直接访问 `http://你的域名/api-config`

**功能：**
- 输入API地址
- 测试连接
- 保存配置
- 刷新页面应用

### 3. 自动化部署脚本

创建了 `setup-public-access.sh`，一键配置公网访问。

**使用方法：**
```bash
chmod +x setup-public-access.sh
./setup-public-access.sh
```

**功能：**
- 自动检测公网IP
- 配置前端和后端
- 开放防火墙端口
- 可选安装Nginx反向代理

### 4. 详细文档

创建了以下文档：
- `docs/PUBLIC_DEPLOYMENT.md` - 完整的公网部署指南
- `docs/QUICK_FIX_500_ERROR.md` - 快速修复指南
- `web-app/.env.production` - 生产环境配置模板

## 使用方法

### 方法1：自动修复（推荐）

由于已实施智能检测，大多数情况下无需任何操作，系统会自动使用正确的API地址。

1. 确保后端服务正在运行：
```bash
cd admin-backend
python app.py
```

2. 构建前端：
```bash
cd web-app
npm run build
```

3. 部署前端文件到Web服务器

4. 访问系统，系统会自动检测并使用正确的API地址

### 方法2：手动配置

如果自动检测不工作，可以使用API配置页面：

1. 访问登录页面
2. 点击"API配置"链接
3. 输入正确的API地址（如 `http://123.45.67.89:8001`）
4. 点击"测试连接"验证
5. 点击"保存配置并刷新"

### 方法3：使用部署脚本

```bash
chmod +x setup-public-access.sh
./setup-public-access.sh
```

按提示操作，脚本会自动完成所有配置。

## 验证步骤

### 1. 检查后端服务

```bash
curl http://YOUR_PUBLIC_IP:8001/api/health
```

应该返回：
```json
{"status": "ok"}
```

### 2. 检查前端配置

在浏览器中：
1. 按F12打开开发者工具
2. 切换到Network标签
3. 尝试登录
4. 查看 `/api/login` 请求

URL应该是：`http://YOUR_PUBLIC_IP:8001/api/login`

### 3. 测试登录

使用有效的用户名和密码登录，确认能成功。

## 常见问题

### Q1: 自动检测不工作怎么办？

**A:** 使用API配置页面手动设置：
1. 访问 `http://YOUR_DOMAIN/api-config`
2. 输入正确的API地址
3. 保存并刷新

### Q2: 后端服务无法访问

**A:** 检查以下几点：
1. 后端是否在运行：`ps aux | grep "python app.py"`
2. 防火墙是否开放8001端口
3. 云服务商安全组是否开放8001端口

### Q3: 修改配置后仍然500错误

**A:** 按以下步骤排查：
1. 打开浏览器开发者工具（F12）
2. 查看Network标签，找到失败的请求
3. 查看Response，获取详细错误信息
4. 查看后端日志：`tail -f logs/app_backend.log`

## 推荐部署架构

```
用户浏览器
    ↓
[公网IP:80/443] (Nginx)
    ↓
    ├→ / → 前端静态文件 (React)
    └→ /api/* → [127.0.0.1:8001] (Flask后端)
```

**优势：**
- 只需开放80/443端口到公网
- 后端更安全（只监听本地）
- 便于配置HTTPS
- 支持负载均衡

**配置方法：**
参考 `docs/PUBLIC_DEPLOYMENT.md` 中的Nginx反向代理配置。

## 防火墙配置

确保以下端口已开放：

```bash
# Ubuntu/Debian (UFW)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8001/tcp

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --permanent --add-port=8001/tcp
sudo firewall-cmd --reload
```

## 云服务商配置

如果使用云服务器，还需要在云服务商控制台开放端口：
- 80 (HTTP)
- 443 (HTTPS)
- 8001 (后端API，如果直接暴露)

## 更新内容总结

### 代码修改

1. **web-app/src/services/api.ts**
   - 添加智能API地址检测函数
   - 支持环境变量、localStorage、自动检测三种方式

2. **web-app/src/pages/ApiConfig.tsx** (新增)
   - API配置页面
   - 支持测试连接和保存配置

3. **web-app/src/App.tsx**
   - 添加 `/api-config` 路由

4. **web-app/src/pages/Login.tsx**
   - 添加"API配置"链接

### 文档新增

1. **docs/PUBLIC_DEPLOYMENT.md**
   - 完整的公网部署指南

2. **docs/QUICK_FIX_500_ERROR.md**
   - 快速修复指南

3. **web-app/.env.production**
   - 生产环境配置模板

### 脚本新增

1. **setup-public-access.sh**
   - 自动化部署脚本

## 技术支持

如果遇到其他问题，请：
1. 查看后端日志：`tail -f logs/app_backend.log`
2. 查看浏览器控制台错误（F12）
3. 参考文档：`docs/PUBLIC_DEPLOYMENT.md`
4. 使用API配置页面测试连接

## 下一步建议

1. **配置HTTPS**（生产环境必须）
2. **使用Nginx反向代理**（推荐）
3. **配置负载均衡**（高并发场景）
4. **添加监控和日志**（运维需求）

---

**最后更新：** 2026-02-02
**版本：** v1.0.0

# Vercel 部署故障排查指南

## 问题：PING 找不到主机，浏览器访问超时

## 根本原因
DNS 域名解析问题 - `lingzhiapp.vercel.app` 没有正确解析到 Vercel 服务器

## 解决方案

### 步骤 1：查看 Vercel 分配的默认域名

1. 访问 Vercel Dashboard：https://vercel.com/dashboard
2. 找到 `lingzhiapp` 项目并进入
3. 点击 **"Deployments"** 标签
4. 点击最新的部署记录（绿色的 Ready 状态）
5. 查看页面顶部的 **"Production"** URL

**复制完整的默认域名**，格式类似：
```
https://lingzhiapp-xxxxx.vercel.app
```

### 步骤 2：使用默认域名访问

将复制的默认域名粘贴到浏览器地址栏访问

### 步骤 3：如果默认域名可以访问

说明应用部署成功，只是 `lingzhiapp.vercel.app` 自定义域名有问题

**配置自定义域名**：
1. 点击 **"Domains"** 标签
2. 点击 **"Add"** 按钮
3. 输入 `lingzhiapp.vercel.app`
4. 点击 **"Add"**
5. 按照提示完成 DNS 配置

### 步骤 4：如果默认域名也无法访问

说明是网络连接问题

**尝试以下方法**：
1. 换一个网络（如手机热点）
2. 清除浏览器缓存：Ctrl + Shift + Delete
3. 清除 DNS 缓存：
   - Windows：以管理员身份运行 CMD，执行 `ipconfig /flushdns`
   - Mac：终端执行 `sudo dscacheutil -flushcache`
4. 关闭 VPN/代理

## 快速诊断命令

在 CMD 或终端中执行：

```bash
# 检查 DNS 解析
nslookup lingzhiapp.vercel.app

# 检查网络连接
curl -I https://lingzhiapp.vercel.app

# Ping 测试
ping lingzhiapp.vercel.app
```

## 需要提供的信息

如果问题仍未解决，请提供：

1. **默认域名**（从 Vercel Dashboard 复制的完整 URL）
2. **nslookup 结果**：
   ```
   nslookup lingzhiapp.vercel.app
   ```
3. **默认域名能否访问**？

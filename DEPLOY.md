# 🚀 云服务器快速部署

## ✅ 部署包已准备就绪

- **文件**: `lingzhi_ecosystem_deploy_20260202_170838.tar.gz` (3.8M)
- **位置**: `/workspace/projects/`

---

## ⚡ 3步部署到云服务器

### 1️⃣ 上传部署包

在你的本地电脑上执行：

```bash
scp /workspace/projects/lingzhi_ecosystem_deploy_20260202_170838.tar.gz root@123.56.142.143:/tmp/
```

### 2️⃣ SSH登录并部署

```bash
ssh root@123.56.142.143
cd /tmp
tar -xzf lingzhi_ecosystem_deploy_20260202_170838.tar.gz
cd admin-backend
../scripts/cloud_auto_deploy.sh
```

### 3️⃣ 开放阿里云端口并访问

1. 登录阿里云控制台：https://ecs.console.aliyun.com/
2. ECS实例 -> 安全组 -> 配置规则
3. 添加端口：80/80, 8080/8080（TCP，0.0.0.0/0）
4. 保存并等待1-2分钟
5. 访问：http://123.56.142.143

---

## 📋 部署脚本功能

自动部署脚本会：
- ✅ 关闭防火墙
- ✅ 安装依赖（Nginx、Python3等）
- ✅ 配置Nginx反向代理
- ✅ 启动后端服务（Flask）
- ✅ 启动Nginx服务
- ✅ 测试所有服务

---

## 🔍 验证部署

SSH登录后检查：

```bash
# 检查服务状态
systemctl status nginx
ps aux | grep python3

# 检查端口监听
netstat -tlnp | grep -E ":80 |:8080 "

# 查看日志
tail -f /tmp/backend.log
```

---

## 📚 详细文档

- **`docs/CLOUD_DEPLOYMENT_GUIDE.md`** - 完整部署指南
- **`docs/CONNECTION_FIX_COMPLETE.md`** - 连接问题解决
- **`docs/COMPLETE_SOLUTION_SUMMARY.md`** - 完整总结

---

## 🛠️ 常见问题

### Q：SCP上传失败？
A：检查SSH密钥配置或使用阿里云Web终端

### Q：502 Bad Gateway？
A：检查后端服务是否启动：`ps aux | grep python3`

### Q：连接被拒绝？
A：检查阿里云安全组是否开放80端口

### Q：如何重新部署？
A：重新上传部署包并运行部署脚本

---

## 🎯 下一步

部署成功后：
1. 访问 http://123.56.142.143
2. 使用 admin/admin123 登录
3. 测试签到功能
4. 配置HTTPS（可选）
5. 设置域名访问（可选）

---

**部署完成！访问 http://123.56.142.143**

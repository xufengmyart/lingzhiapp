# 🚨 生产环境502错误紧急修复指南

> **问题**: 生产环境登录返回502 Bad Gateway错误  
> **原因**: Flask服务可能无法连接或数据库未更新  
> **解决方案**: 部署更新后的数据库并重启Flask服务

---

## 🔍 问题诊断

### 错误信息
```
登录失败: AxiosError: Request failed with status code 502
```

### 502错误原因
- Nginx无法连接到Flask服务（端口8080）
- Flask服务可能未启动或崩溃
- 数据库文件可能不存在或损坏

---

## 🚀 紧急修复步骤

### 第一步：上传数据库到生产服务器

**在开发环境执行**：

```bash
# 上传更新后的数据库（7个核心用户）
scp /workspace/projects/lingzhi_ecosystem.db root@123.56.142.143:/tmp/

# 验证上传
ssh root@123.56.142.143 "ls -lh /tmp/lingzhi_ecosystem.db"
```

### 第二步：在生产服务器执行部署

**SSH登录到生产服务器**：

```bash
ssh root@123.56.142.143
```

**执行部署脚本**：

```bash
cd /var/www/meiyueart
bash scripts/emergency-deploy-production.sh
```

### 第三步：验证部署结果

```bash
# 检查Flask服务状态
systemctl status flask-app

# 查看日志
journalctl -u flask-app -n 50

# 测试健康检查
curl http://localhost:8080/api/health

# 测试登录
curl -X POST http://localhost:8080/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123456"}'
```

---

## 🛠️ 手动修复（如果脚本失败）

### 1. 停止Flask服务

```bash
systemctl stop flask-app
```

### 2. 备份旧数据库

```bash
cd /var/www/meiyueart
cp lingzhi_ecosystem.db backups/lingzhi_ecosystem.db.backup.$(date +%Y%m%d_%H%M%S)
```

### 3. 复制新数据库

```bash
cp /tmp/lingzhi_ecosystem.db ./lingzhi_ecosystem.db
chmod 644 lingzhi_ecosystem.db
```

### 4. 验证数据库

```bash
# 检查用户数量
sqlite3 lingzhi_ecosystem.db "SELECT COUNT(*) FROM users"
# 应该输出：7

# 检查用户列表
sqlite3 lingzhi_ecosystem.db "SELECT id, username FROM users ORDER BY id"
```

### 5. 启动Flask服务

```bash
systemctl start flask-app
```

### 6. 检查服务状态

```bash
systemctl status flask-app
```

---

## ✅ 验证修复结果

### 测试1：检查Flask服务

```bash
systemctl is-active flask-app
# 应该输出：active
```

### 测试2：健康检查

```bash
curl http://localhost:8080/api/health
# 应该输出：{"status":"ok"}
```

### 测试3：测试登录

```bash
curl -X POST http://localhost:8080/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123456"}'
```

应该返回：
```json
{
  "success": true,
  "message": "登录成功",
  "data": {
    "token": "...",
    "user": {...}
  }
}
```

### 测试4：Web登录

1. 打开浏览器访问：https://meiyueart.com
2. 使用账号登录：
   - 用户名：admin
   - 密码：123456

---

## 📊 核心用户信息

| ID | 用户名 | 密码 | 邮箱 | 角色 |
|----|--------|------|------|------|
| 1 | 许锋 | 123456 | xufeng@meiyueart.cn | 核心用户 |
| 2 | CTO（待定） | 123456 | cto@meiyue.com | 技术负责人 |
| 3 | CMO（待定） | 123456 | cmo@meiyue.com | 市场负责人 |
| 4 | COO（待定） | 123456 | coo@meiyue.com | 运营负责人 |
| 5 | CFO（待定） | 123456 | cfo@meiyue.com | 财务负责人 |
| 10 | admin | 123456 | admin@meiyueart.com | 管理员 |
| 201 | 17372200593 | 123456 | test@example.com | 测试用户 |

---

## 🔍 故障排查

### 问题1：Flask服务无法启动

```bash
# 查看详细错误
journalctl -u flask-app -n 100

# 检查端口占用
netstat -tlnp | grep 8080

# 检查日志文件
tail -f /var/log/flask-app-error.log
```

### 问题2：数据库验证失败

```bash
# 检查数据库文件
ls -lh /var/www/meiyueart/lingzhi_ecosystem.db

# 检查数据库完整性
sqlite3 /var/www/meiyueart/lingzhi_ecosystem.db "PRAGMA integrity_check;"
```

### 问题3：Nginx配置问题

```bash
# 测试Nginx配置
nginx -t

# 重启Nginx
systemctl restart nginx

# 检查Nginx状态
systemctl status nginx
```

---

## 📞 联系信息

- **生产服务器**: 123.56.142.143
- **域名**: meiyueart.com
- **技术支持**: Coze Coding

---

## 📝 部署检查清单

- [ ] 上传新数据库到生产服务器（/tmp/lingzhi_ecosystem.db）
- [ ] SSH登录到生产服务器
- [ ] 执行部署脚本（emergency-deploy-production.sh）
- [ ] 验证Flask服务状态（active）
- [ ] 测试健康检查接口（/api/health）
- [ ] 测试登录接口（admin/123456）
- [ ] Web端验证登录功能

---

**创建者**: Coze Coding  
**版本**: v1.0  
**创建时间**: 2026-02-11

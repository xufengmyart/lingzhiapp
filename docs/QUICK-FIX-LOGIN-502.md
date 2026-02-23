# ⚡ 登录 502 错误 - 快速修复指南（30 秒）

## 问题症状
```
登录失败: AxiosError: Request failed with status code 502
/api/login: 502 Bad Gateway
```

## 根本原因
**Flask 后端服务未运行** - 阿里云服务器（123.56.142.143）

---

## 🚀 快速修复（3 步，30 秒）

### 第 1 步: SSH 登录
```bash
ssh root@123.56.142.143
```

### 第 2 步: 运行修复脚本
```bash
cd /var/www/meiyueart
bash scripts/fix-login-issue.sh
```

### 第 3 步: 测试登录
1. 打开浏览器访问 `https://meiyueart.com`
2. 尝试登录
3. ✅ 应该可以成功登录

---

## 备用方案（如果脚本不可用）

### 手动修复（3 条命令）
```bash
# SSH 登录后执行
systemctl restart flask-app
systemctl status flask-app
curl http://localhost:8080/api/health
```

---

## 验证修复

### 浏览器验证
1. 打开开发者工具 (F12)
2. 切换到 Network 标签
3. 尝试登录
4. 检查 `/api/login` 请求
   - ✅ **200 OK** = 成功
   - ❌ **502 Bad Gateway** = 失败

### 命令行验证
```bash
# 检查服务状态
systemctl status flask-app

# 检查端口
lsof -i :8080

# 测试 API
curl http://localhost:8080/api/health
```

---

## 如果仍然失败

### 查看日志
```bash
# Flask 日志
journalctl -u flask-app -n 50

# 错误日志
tail -50 /var/log/flask-app-error.log

# Nginx 日志
tail -50 /var/log/nginx/error.log
```

### 运行完整诊断
```bash
cd /var/www/meiyueart
bash scripts/diagnose-and-fix.sh
```

---

## 预防措施（防止再次发生）

### 配置自动监控
```bash
cd /var/www/meiyueart
bash scripts/setup-cron.sh
```

### 每分钟自动检查
- ✅ 检查服务状态
- ✅ 自动重启失败的 服务
- ✅ 记录详细日志

---

## 📞 应急命令

```bash
# 一键修复
cd /var/www/meiyueart && bash scripts/fix-login-issue.sh

# 快速重启
systemctl restart flask-app

# 查看日志
journalctl -u flask-app -f
```

---

## 📖 详细文档

- [完整诊断文档](docs/LOGIN-ISSUE-COMPLETE-DIAGNOSIS.md)
- [标准部署配置](docs/STANDARD-DEPLOYMENT-CONFIG.md)
- [最终解决方案](docs/FINAL-SOLUTION-AND-PREVENTION.md)

---

**时间**: 2026-02-11  
**状态**: ✅ 已提供修复方案  
**修复时间**: 30 秒

# 🎯 立即部署指南

## ⚡ 一键部署命令（在服务器上执行）

```bash
cd /root && wget https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/quick-deploy_ff392e4c.sh?sign=1770356381-9bd68d84c1-0-0faebe802da3a4846774e91460f53edc18d10274a85fbd8e40c1e84cd1f6e1ec -O deploy.sh && bash deploy.sh
```

---

## 📋 详细步骤

### 1. 下载部署脚本

```bash
cd /root
wget https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/quick-deploy_ff392e4c.sh?sign=1770356381-9bd68d84c1-0-0faebe802da3a4846774e91460f53edc18d10274a85fbd8e40c1e84cd1f6e1ec -O deploy.sh
```

### 2. 查看脚本内容（可选）

```bash
cat deploy.sh
```

### 3. 执行部署

```bash
bash deploy.sh
```

---

## ✅ 验证部署

```bash
# 检查部署的文件
ls -lh /var/www/frontend/assets/

# 应该看到新的文件
# index-CkydMeua.js  (约704KB)
# index-CxUAxLXV.css (约82KB)

# 检查Nginx状态
systemctl status nginx
```

---

## 🌐 访问地址

清除浏览器缓存后访问：

- 🎨 **梦幻风格选择器**: https://meiyueart.com/dream-selector
- 🔐 **梦幻版登录**: https://meiyueart.com/login-full
- 📝 **梦幻版注册**: https://meiyueart.com/register-full

---

## 🔧 故障排查

### 如果部署失败

```bash
# 查看错误日志
tail -n 20 /var/log/nginx/error.log

# 恢复备份
cp -r /var/www/frontend.backup.*/* /var/www/frontend/
systemctl restart nginx
```

### 如果下载失败

检查网络连接：

```bash
ping -c 3 coze-coding-project.tos.coze.site
```

---

## 📁 部署文件说明

| 文件 | 大小 | 说明 |
|------|------|------|
| `dream-frontend-deploy.tar.gz` | 192KB | 前端构建产物 |
| `quick-deploy.sh` | ~2KB | 自动部署脚本 |

---

## 📚 相关资源

- **可视化部署指南**: https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/deploy-guide_696d66b9.html?sign=1770356412-22e371b8d1-0-cde5ed9140df62fcc6cde6e53226807175302c0cead865906049250b454f76d9
- **部署信息JSON**: `/workspace/projects/deployment-info.json`

---

## 💡 部署脚本功能

1. 自动下载构建产物
2. 备份现有文件
3. 解压并部署
4. 设置正确权限
5. 重启Nginx
6. 显示部署结果

---

## 🎉 预期结果

部署成功后，您将看到：

```
==========================================
  ✅ 部署完成！
==========================================

📍 访问地址：
   https://meiyueart.com/dream-selector
   https://meiyueart.com/login-full
   https://meiyueart.com/register-full

📝 部署的文件：
-rw-r--r-- 1 root root 704K Feb  5 13:20 index-CkydMeua.js
-rw-r--r-- 1 root root  82K Feb  5 13:20 index-CxUAxLXV.css

提示：清除浏览器缓存 (Ctrl+Shift+R)
```

---

## 📞 技术支持

如有问题，请检查：

1. 服务器是否有root权限
2. `/var/www/frontend` 目录是否可写
3. Nginx是否正常运行
4. 防火墙是否允许80/443端口

---

**生成时间**: 2025-02-05
**版本**: 1.0
**状态**: ✅ 可部署

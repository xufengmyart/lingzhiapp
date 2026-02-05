# ⚡ 立即部署 - 梦幻版页面

## 🎯 在服务器上执行以下命令

```bash
cd /root && wget https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/quick-deploy_ff392e4c.sh?sign=1770356381-9bd68d84c1-0-0faebe802da3a4846774e91460f53edc18d10274a85fbd8e40c1e84cd1f6e1ec -O deploy.sh && bash deploy.sh
```

---

## ✅ 部署完成后访问

- 🎨 **梦幻风格选择器**: https://meiyueart.com/dream-selector
- 🔐 **梦幻版登录**: https://meiyueart.com/login-full
- 📝 **梦幻版注册**: https://meiyueart.com/register-full

---

## 💡 提示

- 清除浏览器缓存：`Ctrl + Shift + R` (Windows) 或 `Cmd + Shift + R` (Mac)
- 使用无痕模式测试
- 如有问题，查看日志：`tail -n 20 /var/log/nginx/error.log`

---

## 🔧 验证部署

```bash
ls -lh /var/www/frontend/assets/
```

应该看到：
- `index-CkydMeua.js` (约704KB)
- `index-CxUAxLXV.css` (约82KB)

---

## 📋 部署说明

- **构建产物**: 192KB 压缩包
- **部署目标**: /var/www/frontend
- **自动备份**: /var/www/frontend.backup.YYYYMMDD_HHMMSS
- **服务重启**: Nginx

---

**部署状态**: ✅ 准备就绪
**最后更新**: 2025-02-05

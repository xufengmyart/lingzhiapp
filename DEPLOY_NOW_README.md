# 🚀 梦幻版页面 - 立即部署

由于需要无条件执行，请在服务器上**立即执行**以下命令：

## ⚡ 一键部署（推荐）

直接复制以下命令并在服务器上执行：

```bash
cd /root && wget https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/quick-deploy_ff392e4c.sh?sign=1770356381-9bd68d84c1-0-0faebe802da3a4846774e91460f53edc18d10274a85fbd8e40c1e84cd1f6e1ec -O deploy.sh && bash deploy.sh
```

---

## 📋 部署步骤

### 方法1：使用部署脚本（推荐）

```bash
# 1. 下载部署脚本
cd /root
wget https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/quick-deploy_ff392e4c.sh?sign=1770356381-9bd68d84c1-0-0faebe802da3a4846774e91460f53edc18d10274a85fbd8e40c1e84cd1f6e1ec -O deploy.sh

# 2. 执行部署
bash deploy.sh
```

### 方法2：直接下载tar包

```bash
# 1. 下载tar包
cd /root
wget https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/dream-frontend-deploy.tar_7a6617f3.gz?sign=1770273524-245076a2ff-0-561bd59a69ac1a9cd6cb1c2c1cf230ab25b33fcaf79bf754a78d93f32f21de38 -O dream.tar.gz

# 2. 部署
rm -rf /var/www/frontend/*
mkdir -p /tmp/dream
tar -xzf dream.tar.gz -C /tmp/dream
cp -r /tmp/dream/* /var/www/frontend/
chown -R root:root /var/www/frontend
chmod -R 755 /var/www/frontend
rm -rf /tmp/dream

# 3. 重启Nginx
systemctl restart nginx
```

---

## ✅ 验证部署

```bash
# 检查部署的文件
ls -lh /var/www/frontend/assets/

# 应该看到新的文件（不是 index-9000aff5.js）
# 例如：
# index-CkydMeua.js  (约704KB)
# index-CxUAxLXV.css (约82KB)

# 检查Nginx状态
systemctl status nginx
```

---

## 🌐 访问地址

部署完成后，清除浏览器缓存（Ctrl+Shift+R）并访问：

- 🎨 **梦幻风格选择器**: https://meiyueart.com/dream-selector
- 🔐 **梦幻版登录**: https://meiyueart.com/login-full
- 📝 **梦幻版注册**: https://meiyueart.com/register-full

---

## 🔧 故障排查

### 如果部署后无法访问

```bash
# 查看Nginx日志
tail -n 20 /var/log/nginx/error.log

# 恢复备份
ls -la /var/www/frontend.backup.*
cp -r /var/www/frontend.backup.*/ /var/www/frontend/
```

### 如果提示下载失败

检查服务器是否能够访问外网：

```bash
ping -c 3 coze-coding-project.tos.coze.site
```

---

## 📚 可视化部署指南

如果需要更详细的图文指南，请访问：

👉 **https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/deploy-guide_696d66b9.html?sign=1770356412-22e371b8d1-0-cde5ed9140df62fcc6cde6e53226807175302c0cead865906049250b454f76d9**

---

## 📝 部署说明

- **部署目标**: /var/www/frontend
- **备份位置**: /var/www/frontend.backup.YYYYMMDD_HHMMSS
- **Nginx配置**: 使用现有配置，无需修改
- **SSL证书**: 使用现有Let's Encrypt证书，无需更新

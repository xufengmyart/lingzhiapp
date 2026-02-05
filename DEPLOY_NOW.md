# 🎯 服务器端部署 - 立即执行

由于您已经在服务器上，请直接复制以下命令执行：

```bash
cat <<'EOF' > /tmp/quick-deploy.sh && bash /tmp/quick-deploy.sh
#!/bin/bash
echo "=========================================="
echo "  梦幻版页面部署"
echo "=========================================="
echo ""

FRONTEND_DIR="/var/www/frontend"
TAR_PATH="/root/dream-frontend-deploy.tar.gz"

# 检查tar包
if [ ! -f "$TAR_PATH" ]; then
    echo "❌ 错误：找不到构建产物"
    echo "   需要的文件：$TAR_PATH"
    echo ""
    echo "解决方案："
    echo "1. 在本地执行上传："
    echo "   scp /workspace/projects/dream-frontend-deploy.tar.gz root@$(hostname):/root/"
    echo ""
    echo "2. 上传后重新运行此脚本"
    exit 1
fi

# 显示文件信息
echo "找到构建产物："
ls -lh "$TAR_PATH"
echo ""

# 备份
BACKUP_DIR="/var/www/frontend.backup.$(date +%Y%m%d_%H%M%S)"
if [ -d "$FRONTEND_DIR" ] && [ "$(ls -A $FRONTEND_DIR 2>/dev/null)" ]; then
    echo "备份现有文件到：$BACKUP_DIR"
    cp -r "$FRONTEND_DIR" "$BACKUP_DIR" 2>/dev/null || true
fi

# 部署
echo "开始部署..."
mkdir -p "$FRONTEND_DIR"
rm -rf "$FRONTEND_DIR"/*
mkdir -p /tmp/dream-deploy
tar -xzf "$TAR_PATH" -C /tmp/dream-deploy
cp -r /tmp/dream-deploy/* "$FRONTEND_DIR"/
chown -R root:root "$FRONTEND_DIR"
chmod -R 755 "$FRONTEND_DIR"
rm -rf /tmp/dream-deploy

# 重启
echo "重启Nginx..."
systemctl restart nginx 2>&1

# 结果
echo ""
echo "=========================================="
echo "  部署结果"
echo "=========================================="
echo ""
echo "部署的文件："
ls -lh "$FRONTEND_DIR/assets/" 2>/dev/null | grep -E '\.(js|css)$'
echo ""
echo "✓ 部署完成！"
echo ""
echo "访问地址："
echo "  - 梦幻风格选择器: https://meiyueart.com/dream-selector"
echo "  - 梦幻版登录: https://meiyueart.com/login-full"
echo "  - 梦幻版注册: https://meiyueart.com/register-full"
echo ""
echo "提示：请清除浏览器缓存 (Ctrl+Shift+R)"
echo ""
EOF
```

---

## 如果提示找不到tar包

在您的**本地环境**执行以下命令上传：

```bash
scp /workspace/projects/dream-frontend-deploy.tar.gz root@123.56.142.143:/root/
```

上传完成后，在服务器上**重新运行**上面的部署命令。

---

## 验证部署

```bash
# 检查部署的文件
ls -lh /var/www/frontend/assets/

# 应该看到新的文件（不是 index-9000aff5.js）
# 例如：
# index-CkydMeua.js  (约704KB)
# index-CxUAxLXV.css (约82KB)

# 检查Nginx状态
systemctl status nginx

# 查看日志（如果有问题）
tail -n 20 /var/log/nginx/error.log
```

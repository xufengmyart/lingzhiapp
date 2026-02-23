#!/usr/bin/env python3
"""
手动部署前端 - 创建部署包
"""

import os
import subprocess

def main():
    # 1. 创建部署包
    print("创建前端部署包...")
    os.makedirs("/tmp/deploy", exist_ok=True)

    # 复制构建产物
    subprocess.run(f"cp -r /workspace/projects/web-app/dist /tmp/deploy/frontend", shell=True)

    # 创建Service Worker清理页面
    clear_sw_page = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>清除 Service Worker</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            text-align: center;
        }
        h1 {
            color: #2c3e50;
        }
        .success {
            color: #27ae60;
            font-size: 18px;
            margin: 20px 0;
        }
        .info {
            color: #7f8c8d;
            font-size: 14px;
            margin-top: 30px;
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
        }
        .btn {
            display: inline-block;
            margin-top: 20px;
            padding: 12px 24px;
            background: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-size: 16px;
        }
    </style>
</head>
<body>
    <h1>🧹 Service Worker 缓存清理</h1>

    <div id="loading">正在清理 Service Worker...</div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.getRegistrations().then(function(registrations) {
                    if (registrations.length === 0) {
                        document.getElementById('loading').innerHTML = '<div class="success">✓ 没有发现 Service Worker，无需清理</div>';
                        return;
                    }

                    let count = 0;
                    registrations.forEach(function(registration) {
                        registration.unregister();
                        console.log('已注销:', registration.scope);
                        count++;
                    });

                    document.getElementById('loading').innerHTML =
                        '<div class="success">✓ 已成功清除 ' + count + ' 个 Service Worker！</div>' +
                        '<div class="info">' +
                        '  <strong>请执行以下步骤：</strong><br><br>' +
                        '  1. 关闭所有浏览器标签页<br>' +
                        '  2. 清除浏览器缓存（Ctrl+Shift+Delete）<br>' +
                        '  3. 重新访问：<br>' +
                        '  <a href="https://meiyueart.com" style="color: #3498db;">https://meiyueart.com</a>' +
                        '</div>' +
                        '<a href="https://meiyueart.com" class="btn">返回首页</a>';
                });
            } else {
                document.getElementById('loading').innerHTML = '<div class="info">当前浏览器不支持 Service Worker</div>';
            }
        });
    </script>
</body>
</html>
"""

    with open("/tmp/deploy/clear_sw.html", "w", encoding="utf-8") as f:
        f.write(clear_sw_page)

    # 创建部署说明
    deploy_guide = """# 前端部署说明

## 部署步骤

### 1. 上传文件到服务器

```bash
# SSH 登录到服务器
ssh root@123.56.142.143

# 备份现有前端（如果有）
cd /var/www/html
if [ -d frontend ]; then
    mv frontend frontend.backup.$(date +%Y%m%d_%H%M%S)
fi

# 创建前端目录
mkdir -p /var/www/html/frontend
```

### 2. 上传部署文件

将以下文件从本地 `/tmp/deploy/` 目录上传到服务器：

```bash
# 方法1：使用 scp（推荐）
scp -r /tmp/deploy/* root@123.56.142.143:/var/www/html/

# 方法2：使用 tar 压缩后上传
tar -czf /tmp/frontend_deploy.tar.gz -C /tmp/deploy .
scp /tmp/frontend_deploy.tar.gz root@123.56.142.143:/tmp/
ssh root@123.56.142.143 "cd /var/www/html && tar -xzf /tmp/frontend_deploy.tar.gz"
```

### 3. 设置权限

```bash
ssh root@123.56.142.143
chown -R www-data:www-data /var/www/html/frontend
chmod -R 755 /var/www/html/frontend
chmod 644 /var/www/html/clear_sw.html
```

### 4. 验证部署

```bash
# 查看文件
ls -lh /var/www/html/frontend/

# 查看 Service Worker 清理页面
cat /var/www/html/clear_sw.html | head -20
```

### 5. 清除 Service Worker 缓存

让用户访问：`https://meiyueart.com/clear_sw.html`

并按照页面提示操作：
1. 关闭所有浏览器标签页
2. 清除浏览器缓存（Ctrl+Shift+Delete）
3. 重新访问：https://meiyueart.com

## 测试账号

- 用户名: `admin`    密码: `123`
- 用户名: `许锋`    密码: `123`

## 访问地址

- 前端: https://meiyueart.com
- API: https://meiyueart.com/api/
- 清理 Service Worker: https://meiyueart.com/clear_sw.html

## 技术说明

- 前端版本: 20260210-1029
- Service Worker: 已禁用（通过版本控制）
- API 端点: `/api/auth/login`（已修复）
- 密码加密: bcrypt
"""

    with open("/tmp/deploy/README.md", "w", encoding="utf-8") as f:
        f.write(deploy_guide)

    # 创建部署脚本（在服务器上执行）
    server_deploy_script = """#!/bin/bash
echo "========================================="
echo "前端部署脚本"
echo "========================================="
echo ""

# 备份现有前端
if [ -d /var/www/html/frontend ]; then
    BACKUP_DIR="/var/www/html/frontend.backup.$(date +%Y%m%d_%H%M%S)"
    echo "备份现有前端到: $BACKUP_DIR"
    mv /var/www/html/frontend "$BACKUP_DIR"
fi

# 创建前端目录
mkdir -p /var/www/html/frontend

# 检查是否有部署文件
if [ -f /tmp/frontend_deploy.tar.gz ]; then
    echo "解压部署文件..."
    cd /var/www/html
    tar -xzf /tmp/frontend_deploy.tar.gz
else
    echo "错误: 未找到部署文件 /tmp/frontend_deploy.tar.gz"
    exit 1
fi

# 设置权限
echo "设置文件权限..."
chown -R www-data:www-data /var/www/html/frontend
chmod -R 755 /var/www/html/frontend
chmod 644 /var/www/html/clear_sw.html

# 验证部署
echo ""
echo "========================================="
echo "部署验证"
echo "========================================="
ls -lh /var/www/html/frontend/
echo ""
echo "Service Worker 清理页面:"
ls -lh /var/www/html/clear_sw.html
echo ""
echo "========================================="
echo "✓ 部署完成！"
echo "========================================="
echo ""
echo "清除 Service Worker:"
echo "  https://meiyueart.com/clear_sw.html"
echo ""
echo "测试账号:"
echo "  admin / 123"
echo "  许锋 / 123"
"""

    with open("/tmp/deploy/deploy_server.sh", "w", encoding="utf-8") as f:
        f.write(server_deploy_script)

    print("\n部署文件已创建:")
    print(f"  - /tmp/deploy/frontend/ (前端构建产物)")
    print(f"  - /tmp/deploy/clear_sw.html (Service Worker 清理页面)")
    print(f"  - /tmp/deploy/README.md (部署说明)")
    print(f"  - /tmp/deploy/deploy_server.sh (服务器部署脚本)")
    print(f"\n请查看 README.md 了解部署步骤")

if __name__ == "__main__":
    main()

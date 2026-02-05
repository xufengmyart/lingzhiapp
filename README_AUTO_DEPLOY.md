# 🚀 梦幻版页面 - 完全自动部署包

## 📦 部署包内容

```
/workspace/projects/
├── auto-deploy.sh              # 自动部署脚本
├── dream-frontend-deploy.tar.gz # 构建产物tar包 (192 KB)
└── README_AUTO_DEPLOY.md      # 本文档
```

---

## ⚡ 快速部署（3步完成）

### 在目标服务器上执行以下命令：

```bash
# 1. 上传文件到服务器
scp auto-deploy.sh dream-frontend-deploy.tar.gz root@123.56.142.143:/root/

# 2. SSH登录服务器
ssh root@123.56.142.143

# 3. 解压并运行部署脚本
cd /root
tar -xzf dream-frontend-deploy.tar.gz
./auto-deploy.sh
```

---

## 🔍 部署流程（自动执行）

脚本会自动完成以下步骤：

### ✅ 步骤1：检查环境
- 验证前端目录 `/var/www/frontend` 存在
- 检查必要的文件权限

### ✅ 步骤2：备份现有文件
- 自动备份到 `/var/www/frontend.backup.YYYYMMDD_HHMMSS`
- 防止意外数据丢失

### ✅ 步骤3：清空目标目录
- 清理旧的构建产物
- 确保干净的部署

### ✅ 步骤4：复制新构建产物
- 从当前目录或项目目录复制文件
- 自动查找构建产物位置

### ✅ 步骤5：设置权限
- 设置正确的文件权限 (755)
- 设置正确的所有者 (root:root)

### ✅ 步骤6：验证部署
- 检查关键文件是否存在
- 验证文件名正确
- 确认文件完整性

### ✅ 步骤7：重启Nginx
- 自动重启Nginx服务
- 应用新配置

---

## 📋 部署检查清单

执行脚本前：
- [ ] 已上传 `auto-deploy.sh` 到服务器的 `/root/`
- [ ] 已上传 `dream-frontend-deploy.tar.gz` 到服务器的 `/root/`
- [ ] 拥有服务器root权限

执行脚本后：
- [ ] 看到 "✅ 部署成功！" 提示
- [ ] 看到 Nginx已重启提示
- [ ] 备份目录已创建

浏览器验证：
- [ ] 清除浏览器缓存 (Ctrl+Shift+R)
- [ ] 访问 https://meiyueart.com/dream-selector
- [ ] 验证4种风格可以切换
- [ ] 验证登录/注册按钮正常

---

## 🎯 预期结果

### 部署成功输出示例：

```
==========================================
  梦幻版页面自动部署开始
  时间: 2025-02-05 13:30:00
==========================================

步骤 1/6: 检查环境
----------------------------
✓ 前端目录存在: /var/www/frontend

步骤 2/6: 备份现有文件
----------------------------
备份现有文件到: /var/www/frontend.backup.20250205_130000
✓ 备份完成

步骤 3/6: 清空目标目录
----------------------------
✓ 目标目录已清空

步骤 4/6: 复制新构建产物
----------------------------
构建产物位置: /root/public
复制文件...
✓ 文件复制完成

步骤 5/6: 设置权限
----------------------------
✓ 权限设置完成

步骤 6/6: 验证部署
----------------------------
✓ 所有关键文件验证通过

==========================================
  ✅ 部署成功！
==========================================

部署信息：
  目标目录: /var/www/frontend
  备份位置: /var/www/frontend.backup.20250205_130000

部署的文件：
  index-CkydMeua.js (704K)
  index-CxUAxLXV.css (82K)

正在重启Nginx...
✓ Nginx已重启

==========================================
  访问地址
==========================================

  梦幻风格选择器: https://meiyueart.com/dream-selector
  梦幻版登录: https://meiyueart.com/login-full
  梦幻版注册: https://meiyueart.com/register-full

提示：
  1. 清除浏览器缓存 (Ctrl+Shift+R)
  2. 使用无痕模式测试
  3. 如有问题，恢复备份：
     cp -r /var/www/frontend.backup.20250205_130000/* /var/www/frontend/
```

---

## 🔧 如果出现问题

### 问题1：脚本执行失败

**解决方案：**
```bash
# 检查脚本权限
chmod +x /root/auto-deploy.sh

# 手动执行
bash /root/auto-deploy.sh
```

### 问题2：找不到构建产物

**解决方案：**
```bash
# 检查tar包内容
tar -tzf /root/dream-frontend-deploy.tar.gz

# 手动解压
mkdir -p /root/public
tar -xzf /root/dream-frontend-deploy.tar.gz -C /root/public/

# 再次运行脚本
./auto-deploy.sh
```

### 问题3：Nginx重启失败

**解决方案：**
```bash
# 检查Nginx配置
nginx -t

# 查看错误日志
tail -n 50 /var/log/nginx/error.log

# 手动重启
systemctl restart nginx
```

### 问题4：页面仍然显示旧版本

**解决方案：**
```bash
# 检查实际部署的文件
ls -lh /var/www/frontend/assets/

# 应该看到：
# index-CkydMeua.js  688K
# index-CxUAxLXV.css  82K

# 如果不是，重新部署
cp -r /root/public/* /var/www/frontend/
systemctl restart nginx
```

---

## 🎨 验证页面功能

访问 https://meiyueart.com/dream-selector 后，应该看到：

✅ **视觉元素：**
- 4个风格卡片（晨曦之梦、星空梦境、森林之梦、极光之梦）
- 梦幻背景效果（光晕、星星、装饰块）
- 流畅的动画效果

✅ **交互功能：**
- 点击风格卡片可以切换背景
- 点击"登录账户"跳转到梦幻版登录
- 点击"创建账户"跳转到梦幻版注册

✅ **风格特点：**
- 🌅 晨曦之梦：粉色+橙色+紫色（温暖活力）
- 🌌 星空梦境：深蓝+紫色+靛蓝（深邃宁静）
- 🌿 森林之梦：翠绿+青色+蓝绿（自然清新）
- 🌈 极光之梦：玫瑰红+紫色+蓝色（绚丽梦幻）

---

## 📞 需要帮助？

如果按照以上步骤操作后仍有问题：

1. **查看脚本输出**
   - 脚本会显示详细的执行过程
   - 注意任何错误或警告信息

2. **检查服务器日志**
   ```bash
   tail -n 50 /var/log/nginx/error.log
   ```

3. **验证文件部署**
   ```bash
   ls -lh /var/www/frontend/assets/
   ```

4. **恢复备份**
   ```bash
   cp -r /var/www/frontend.backup.*/\* /var/www/frontend/
   ```

---

## ✨ 部署成功标志

✅ 看到 "✅ 部署成功！" 提示
✅ 看到 Nginx已重启提示
✅ 访问 https://meiyueart.com/dream-selector 能看到4个风格卡片
✅ 可以点击切换风格
✅ 浏览器控制台无错误

---

## 📌 重要提醒

⚠️ **执行前必读：**
1. 确保在服务器上执行，不是在本地
2. 确保已上传两个文件到 `/root/` 目录
3. 确保有root权限
4. 执行前先备份重要数据（脚本会自动备份）

⚠️ **执行后必做：**
1. 清除浏览器缓存 (Ctrl+Shift+R)
2. 使用无痕模式测试
3. 验证所有功能正常
4. 如果有问题，检查脚本输出和日志

---

## 🚀 一键执行（推荐）

如果文件已上传到服务器，执行：

```bash
ssh root@123.56.142.143
cd /root
chmod +x auto-deploy.sh
./auto-deploy.sh
```

然后清除浏览器缓存，访问 https://meiyueart.com/dream-selector！

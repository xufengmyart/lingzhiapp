# 🔐 Git推送认证 - 用户名和密码在哪里输入

## 📍 在哪里输入

### 执行推送命令后，终端会自动提示

**命令**：
```bash
git push -u origin main
```

**执行后，终端会显示**：

```
Username for 'https://github.com': [在这里输入用户名]
Password for 'https://用户名@github.com': [在这里输入密码]
```

---

## 📝 具体操作步骤

### 步骤1：执行推送命令

```bash
cd /workspace/projects/web-app
git push -u origin main
```

### 步骤2：输入用户名

终端会显示：
```
Username for 'https://github.com':
```

**操作**：
- 输入您的GitHub用户名
- 按回车键

**示例**：
```
Username for 'https://github.com': zhangsan
```

### 步骤3：输入密码

终端会显示：
```
Password for 'https://zhangsan@github.com':
```

**操作**：
- 输入您的Personal Access Token
- 按回车键
- ⚠️ 注意：密码输入时**不会显示任何字符**（这是正常的，安全特性）

---

## 🔑 密码是什么？

### ⚠️ 重要：不是GitHub登录密码！

**密码应该是 Personal Access Token（个人访问令牌）**

**原因**：
- GitHub已取消对密码认证的支持
- 必须使用Personal Access Token替代密码

---

## 📖 如何获取Personal Access Token

### 步骤1：进入Token设置页面

访问：https://github.com/settings/tokens

### 步骤2：创建新Token

1. 点击 **"Generate new token"** → **"Generate new token (classic)"**

### 步骤3：配置Token

**Note（名称）**：
- 输入：`lingzhi-ecosystem` 或其他名称
- 用于标识这个Token的用途

**Expiration（过期时间）**：
- 选择：**No expiration**（永不过期）或选择一个合适的时间

**Select scopes（权限）**：
- 勾选：**repo**（完整仓库权限）
  - 包含：repo:status、repo_deployment、public_repo、repo:invite、security_events

### 步骤4：生成Token

- 点击页面底部的 **"Generate token"** 按钮

### 步骤5：复制Token

- Token会以 `ghp_YOUR_TOKEN_HERE` 开头
- **立即复制保存**（页面刷新后就看不到了）
- 妥善保管（不要泄露给他人）

---

## 💡 完整操作示例

### 场景1：使用Personal Access Token

```bash
# 1. 执行推送命令
$ git push -u origin main

# 2. 终端提示输入用户名
Username for 'https://github.com': zhangsan

# 3. 终端提示输入密码（注意：输入时不会显示字符）
Password for 'https://zhangsan@github.com': YOUR_GITHUB_PERSONAL_ACCESS_TOKEN

# 4. 推送成功
Enumerating objects: 83, done.
Counting objects: 100% (83/83), done.
Delta compression using up to 4 threads.
Compressing objects: 100% (75/75), done.
Writing objects: 100% (83/83), 123.45 KiB | 2.34 MiB/s, done.
Total 83 (delta 10), reused 0 (delta 0)
To https://github.com/zhangsan/lingzhi-ecosystem-app.git
 * [new branch]      main -> main
branch 'main' set up to track 'origin/main'.
```

---

## ❌ 常见错误

### 错误1：使用GitHub登录密码

**错误信息**：
```
remote: Support for password authentication was removed on August 13, 2021.
remote: Please see https://github.blog/2020-12-15-token-authentication-requirements-for-git-operations/ for more information.
fatal: Authentication failed for 'https://github.com/...'
```

**原因**：使用了GitHub登录密码而不是Personal Access Token

**解决**：使用Personal Access Token

---

### 错误2：Token权限不足

**错误信息**：
```
remote: Permission to 用户名/仓库名.git denied to 用户名
fatal: unable to access 'https://github.com/...': The requested URL returned error: 403
```

**原因**：Token没有足够的权限

**解决**：
1. 重新生成Token
2. 勾选 `repo` 权限
3. 使用新Token推送

---

### 错误3：密码输入错误

**错误信息**：
```
fatal: Authentication failed for 'https://github.com/...'
```

**原因**：
- Token输入错误
- Token已过期
- Token被撤销

**解决**：
1. 确认Token正确复制
2. 检查Token是否过期
3. 如需要，重新生成Token

---

## 🔒 安全提示

### ⚠️ 重要注意事项

1. **不要泄露Token**
   - Token等同于密码
   - 不要分享给他人
   - 不要提交到Git仓库

2. **定期更换Token**
   - 建议定期更换
   - 发现泄露立即撤销

3. **妥善保管**
   - 保存在安全的地方
   - 不要明文记录在不安全的地方

4. **使用SSH替代（可选）**
   - SSH密钥更安全
   - 不需要每次输入Token
   - 配置一次，永久使用

---

## 🚀 推荐方法：使用SSH密钥（可选）

### 优势
- ✅ 更安全
- ✅ 不需要每次输入Token
- ✅ 配置一次，永久使用

### 配置步骤

#### 1. 生成SSH密钥

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

#### 2. 启动ssh-agent

```bash
eval "$(ssh-agent -s)"
```

#### 3. 添加SSH密钥

```bash
ssh-add ~/.ssh/id_ed25519
```

#### 4. 复制公钥

```bash
cat ~/.ssh/id_ed25519.pub
```

#### 5. 添加到GitHub

1. 访问：https://github.com/settings/keys
2. 点击 "New SSH key"
3. 粘贴公钥
4. 点击 "Add SSH key"

#### 6. 修改远程仓库URL为SSH

```bash
git remote set-url origin git@github.com:用户名/仓库名.git
```

#### 7. 推送代码

```bash
git push -u origin main
```

现在推送不需要输入密码了！

---

## 📊 认证方式对比

| 方式 | 安全性 | 便捷性 | 首次配置 | 日常使用 |
|------|--------|--------|---------|---------|
| HTTPS + Token | ⭐⭐⭐ | ⭐⭐ | 简单 | 每次输入 |
| SSH密钥 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 较复杂 | 无需输入 |

---

## ✅ 总结

### 快速操作（推荐新手）

1. **创建Personal Access Token**
   - 访问：https://github.com/settings/tokens
   - 点击 "Generate new token (classic)"
   - 勾选 `repo` 权限
   - 生成并复制Token

2. **推送代码**
   ```bash
   git push -u origin main
   ```

3. **输入认证信息**
   - 用户名：GitHub用户名
   - 密码：Personal Access Token（注意输入时不显示）

4. **完成**
   - 等待推送完成
   - 看到成功提示

---

### 进阶方法（推荐有经验用户）

1. **配置SSH密钥**
   - 生成SSH密钥对
   - 添加到GitHub
   - 修改远程仓库URL

2. **推送代码**
   ```bash
   git push -u origin main
   ```

3. **完成**
   - 无需输入密码
   - 自动完成推送

---

## 🆘 遇到问题？

### 问题1：找不到Token生成页面

**解决**：
- 确保已登录GitHub
- 访问：https://github.com/settings/tokens
- 点击 "Generate new token (classic)"

---

### 问题2：Token生成后看不到

**解决**：
- 页面刷新后就看不到了
- 需要重新生成
- 这次记得立即复制保存

---

### 问题3：推送时提示403错误

**解决**：
- 检查Token权限（需要勾选`repo`）
- 检查仓库地址是否正确
- 检查是否有仓库访问权限

---

## 📖 相关文档

- [GitHub官方文档 - 管理个人访问令牌](https://docs.github.com/zh/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
- [GitHub官方文档 - 命令行Git认证](https://docs.github.com/zh/authentication/connecting-to-github-with-ssh)

---

**现在您知道在哪里输入用户名和密码了！** 🎉

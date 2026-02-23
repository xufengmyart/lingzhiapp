# 微信小程序自动化部署指南

## 快速开始

### 1. 安装依赖

```bash
cd /workspace/projects/miniprogram
npm install
```

### 2. 配置密钥

#### 步骤1: 获取小程序 AppID
1. 登录 [微信公众平台](https://mp.weixin.qq.com/)
2. 进入「开发」→「开发设置」
3. 记录「开发者ID」中的 AppID

#### 步骤2: 生成代码上传密钥
1. 在「开发设置」页面找到「小程序代码上传」
2. 点击「生成」按钮
3. 下载密钥文件（例如：`private.xxx.key`）

#### 步骤3: 配置密钥文件
```bash
# 创建密钥目录
mkdir -p /workspace/projects/miniprogram/keys

# 将下载的密钥文件复制到 keys 目录
cp /path/to/private.xxx.key /workspace/projects/miniprogram/keys/

# 设置正确的权限（只读）
chmod 600 /workspace/projects/miniprogram/keys/private.xxx.key
```

#### 步骤4: 更新配置文件

修改以下文件中的配置：

**ci/upload.js** 和 **ci/preview.js**:
```javascript
const projectConfig = {
  appid: '你的小程序AppID',  // 替换为实际的 AppID
  privateKeyPath: path.resolve(__dirname, '../keys/private.xxx.key'),
  // ...
}
```

**project.config.json**:
```json
{
  "appid": "你的小程序AppID",
  // ...
}
```

**miniprogram/utils/config.js**:
```javascript
module.exports = {
  appId: '你的小程序AppID',
  // ...
}
```

### 3. 配置 IP 白名单

1. 在微信公众平台的「开发设置」页面
2. 找到「小程序代码上传」→「IP 白名单」
3. 添加服务器的 IP 地址

获取服务器 IP：
```bash
curl ifconfig.me
```

### 4. 测试部署

#### 上传代码
```bash
# 使用默认版本号
npm run upload

# 或指定版本号和描述
VERSION=1.0.1 DESC="首次上传" npm run upload
```

#### 生成预览二维码
```bash
npm run preview

# 预览二维码会保存到 preview-qrcode.jpg
```

### 5. 微信平台发布

1. 登录微信公众平台
2. 进入「版本管理」
3. 选择刚上传的版本
4. 点击「提交审核」
5. 审核通过后点击「发布」

## 详细说明

### 上传脚本（ci/upload.js）

功能：
- 编译小程序代码
- 上传到微信服务器
- 生成可提交审核的版本

使用方法：
```bash
npm run upload

# 自定义版本号
VERSION=1.0.2 npm run upload

# 自定义描述
DESC="修复登录问题" npm run upload
```

### 预览脚本（ci/preview.js）

功能：
- 编译小程序代码
- 生成预览二维码
- 可通过微信扫码体验

使用方法：
```bash
npm run preview

# 指定预览页面
PAGE=pages/user/profile/profile npm run preview

# 添加页面参数
QUERY="id=123&type=test" npm run preview
```

## CI/CD 集成

### GitHub Actions

创建 `.github/workflows/miniprogram-deploy.yml`:

```yaml
name: Deploy Miniprogram

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '16'

      - name: Install dependencies
        run: |
          cd miniprogram
          npm install

      - name: Upload to WeChat
        run: |
          cd miniprogram
          echo "${{ secrets.WECHAT_PRIVATE_KEY }}" > keys/private.key
          chmod 600 keys/private.key
          npm run upload
        env:
          VERSION: ${{ github.ref_name }}
          DESC: "自动部署 ${{ github.sha }}"
```

### 配置 GitHub Secrets

在 GitHub 仓库的 Settings → Secrets 中添加：

- `WECHAT_PRIVATE_KEY`: 微信私钥文件的完整内容

## 常见问题

### Q1: 上传失败，提示 "IP 不在白名单"

**解决方案**：
1. 确保已在微信公众平台添加服务器 IP
2. 检查 IP 地址是否正确（使用 `curl ifconfig.me` 查看当前 IP）
3. IP 白名单配置可能有延迟，等待几分钟后再试

### Q2: 上传失败，提示 "密钥不存在"

**解决方案**：
1. 确认密钥文件路径是否正确
2. 确认密钥文件是否在 `keys/` 目录
3. 确认密钥文件名与配置中的一致

### Q3: 编译错误

**解决方案**：
1. 先在微信开发者工具中打开项目，检查是否有语法错误
2. 确保所有必要的页面文件都已创建
3. 检查 `app.json` 中的页面路径是否正确

### Q4: 预览二维码生成失败

**解决方案**：
1. 确认 `preview-qrcode.jpg` 的保存目录存在
2. 检查磁盘空间是否充足
3. 尝试使用 `qrcodeFormat: 'base64'` 模式

## 最佳实践

### 版本管理

使用语义化版本号：
- `MAJOR.MINOR.PATCH`
- 例如：`1.0.0`、`1.0.1`、`1.1.0`、`2.0.0`

### 发布流程

1. **开发阶段**: 在微信开发者工具中开发和测试
2. **提交代码**: `git add . && git commit -m "feat: xxx" && git push`
3. **自动化上传**: CI 自动触发或手动执行 `npm run upload`
4. **微信平台审核**: 提交审核，等待审核通过
5. **正式发布**: 点击发布按钮

### 安全建议

1. **密钥保护**:
   - 不要将密钥文件提交到 git
   - 使用 CI/CD Secrets 存储密钥
   - 定期轮换密钥

2. **代码审查**:
   - 每次上传前进行代码审查
   - 使用 staging 环境先测试

3. **备份**:
   - 定期备份代码
   - 保留历史版本

## 附录

### 微信官方文档

- [miniprogram-ci 官方文档](https://developers.weixin.qq.com/miniprogram/dev/devtools/ci.html)
- [小程序代码上传指南](https://developers.weixin.qq.com/miniprogram/dev/devtools/upload.html)

### 联系方式

- 项目地址: https://github.com/xxx/lingzhi-ecosystem
- 生产环境: https://meiyueart.com

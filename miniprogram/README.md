# 灵值生态园 - 微信小程序

## 项目概述

这是灵值生态园智能体系统的微信小程序版本，提供便捷的移动端访问体验。

## 技术栈

- **前端框架**: 微信小程序原生开发
- **语言**: JavaScript + WXML + WXSS
- **后端对接**: Flask REST API (https://meiyueart.com/api)
- **自动化部署**: miniprogram-ci

## 核心功能

### 1. 用户认证
- 用户登录（用户名/密码）
- 用户注册（手机号验证）
- 忘记密码（验证码重置）

### 2. 私有资源库
- 资源列表浏览
- 创建新资源
- 资源详情查看
- 资源授权管理
- 资源匹配功能

### 3. 用户中心
- 个人信息展示
- 头像上传
- 灵值查看
- 推荐人信息

### 4. 美学任务
- 任务列表
- 任务打卡
- 任务记录

### 5. 项目推荐
- 推荐项目列表
- 项目详情
- 项目收藏

### 6. 通知系统
- 消息通知
- 系统公告

## 项目结构

```
miniprogram/
├── miniprogram/              # 小程序源码目录
│   ├── pages/               # 页面文件
│   │   ├── index/          # 首页
│   │   ├── auth/           # 认证页面（登录/注册）
│   │   ├── resources/      # 资源库页面
│   │   ├── user/           # 用户中心
│   │   ├── tasks/          # 任务页面
│   │   ├── projects/       # 项目推荐
│   │   └── notifications/  # 通知页面
│   ├── components/         # 组件目录
│   ├── utils/              # 工具函数
│   ├── api/                # API 接口封装
│   ├── config/             # 配置文件
│   ├── app.js              # 小程序入口
│   ├── app.json            # 小程序配置
│   └── app.wxss            # 全局样式
├── ci/                      # 自动化部署脚本
│   ├── upload.js          # 上传脚本
│   └── preview.js         # 预览脚本
├── keys/                    # 密钥文件（不提交到git）
│   └── private.xxx.key    # 代码上传密钥
├── project.config.json      # 小程序项目配置
└── package.json             # Node.js 依赖
```

## 开发指南

### 1. 环境准备

```bash
# 安装依赖
npm install

# 安装 miniprogram-ci
npm install miniprogram-ci --save
```

### 2. 配置密钥

1. 访问微信公众平台 → 开发管理 → 开发设置 → 小程序代码上传
2. 生成「代码上传密钥」
3. 下载密钥文件并放置到 `keys/` 目录
4. 配置 IP 白名单（将服务器 IP 加入）

### 3. 本地开发

使用微信开发者工具打开 `miniprogram/` 目录进行开发。

### 4. 自动化上传

```bash
# 上传代码
npm run upload

# 预览代码
npm run preview
```

## 部署流程

### 1. 开发阶段
- 在 `miniprogram/` 目录下开发
- 使用微信开发者工具实时预览

### 2. 提交代码
```bash
git add .
git commit -m "feat: 添加新功能"
git push
```

### 3. 自动化上传
```bash
# 方式1: 使用 npm 脚本
npm run upload

# 方式2: 直接运行 CI 脚本
node ci/upload.js
```

### 4. 微信平台发布
1. 登录微信公众平台
2. 进入「版本管理」
3. 选择刚上传的版本
4. 提交审核

## 配置说明

### project.config.json

```json
{
  "appid": "你的小程序AppID",
  "projectname": "灵值生态园",
  "compileType": "miniprogram",
  "libVersion": "2.19.4",
  "setting": {
    "es6": true,
    "minified": true
  }
}
```

### 环境变量

在 `utils/config.js` 中配置：

```javascript
module.exports = {
  apiBaseUrl: 'https://meiyueart.com/api',
  appId: '你的小程序AppID'
}
```

## API 对接

所有接口对接文档参考：[API.md](../API.md)

## 注意事项

1. **密钥安全**: 
   - `keys/` 目录已在 `.gitignore` 中
   - 密钥文件切勿上传到 git

2. **IP 白名单**: 
   - 确保部署服务器的 IP 已加入微信白名单
   - 否则无法调用上传接口

3. **版本号管理**: 
   - 每次上传需要指定版本号
   - 建议使用语义化版本号（如 1.0.0, 1.0.1）

## 常见问题

### Q: 上传失败，提示 IP 不在白名单
A: 需要在微信公众平台添加服务器 IP 到 IP 白名单

### Q: 预览二维码生成失败
A: 检查 `ci/preview.js` 中的二维码输出路径是否存在

### Q: 编译错误
A: 确保微信开发者工具的编译设置与 `project.config.json` 一致

## 更新日志

### v1.0.0 (2026-02-23)
- 初始版本
- 实现核心功能（认证、资源库、用户中心）
- 配置 miniprogram-ci 自动化部署

## 联系方式

- 项目地址: https://github.com/xxx/lingzhi-ecosystem
- 生产环境: https://meiyueart.com

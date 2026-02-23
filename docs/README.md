# 文档中心

欢迎来到灵值生态园系统文档中心。

## 📚 文档索引

### 核心文档

| 文档 | 说明 | 路径 |
|------|------|------|
| **[后台管理与前端对应关系](./ADMIN_API_MAPPING.md)** | 详细说明每个前端页面对应的后端 API | [查看](./ADMIN_API_MAPPING.md) |
| **[API 参考文档](./API_REFERENCE.md)** | 完整的 API 接口文档 | [查看](./API_REFERENCE.md) |
| **[部署指南](./DEPLOYMENT_GUIDE.md)** | 详细的部署流程和故障处理 | [查看](./DEPLOYMENT_GUIDE.md) |
| **[部署归档](./DEPLOYMENT_ARCHIVE.md)** | 部署脚本归档和使用说明 | [查看](./DEPLOYMENT_ARCHIVE.md) |

---

## 🚀 快速开始

### 1. 部署系统

```bash
# 使用统一万能部署脚本
cd /workspace/projects
python3 universal_deploy.py --all
```

### 2. 访问后台

```
登录地址: https://meiyueart.com/admin/login
用户名: admin
密码: admin123
```

### 3. 查看文档

- **了解 API 对应关系**：[后台管理与前端对应关系](./ADMIN_API_MAPPING.md)
- **查看 API 文档**：[API 参考文档](./API_REFERENCE.md)
- **学习部署流程**：[部署指南](./DEPLOYMENT_GUIDE.md)
- **了解部署工具**：[部署归档](./DEPLOYMENT_ARCHIVE.md)

---

## 📖 文档说明

### 后台管理与前端对应关系 (ADMIN_API_MAPPING.md)

**包含内容：**
- 每个前端组件对应的后端 API
- API 调用示例
- 响应格式说明
- 认证机制
- 错误处理
- 分页规范
- 数据验证

**适用人群：**
- 前端开发人员
- 后端开发人员
- 全栈开发人员

---

### API 参考文档 (API_REFERENCE.md)

**包含内容：**
- 完整的 API 接口列表
- 请求/响应示例
- 参数说明
- 错误码定义

**适用人群：**
- API 使用者
- 第三方集成开发者
- 测试人员

---

### 部署指南 (DEPLOYMENT_GUIDE.md)

**包含内容：**
- 环境准备
- 快速开始
- 详细部署流程
- 模块化部署
- 故障处理
- 最佳实践

**适用人群：**
- 运维人员
- 开发人员
- 系统管理员

---

### 部署归档 (DEPLOYMENT_ARCHIVE.md)

**包含内容：**
- 部署脚本说明
- 文件结构
- 部署历史
- 故障处理
- 注意事项

**适用人群：**
- 运维人员
- 项目经理
- 新团队成员

---

## 🔧 工具和脚本

### 统一万能部署脚本

**路径：** `/workspace/projects/universal_deploy.py`

**特性：**
- ✅ 增量部署（基于文件哈希）
- ✅ 模块化部署
- ✅ 自动验证
- ✅ 备份机制
- ✅ 日志记录

**使用方法：**
```bash
# 部署所有模块
python3 universal_deploy.py --all

# 仅部署后台管理 API
python3 universal_deploy.py --admin_api

# 强制部署
python3 universal_deploy.py --all --force

# 查看帮助
python3 universal_deploy.py --help
```

---

## 📞 联系方式

如有问题，请联系：
- 技术负责人：[联系方式]
- 运维团队：[联系方式]

---

## 🔄 更新日志

| 日期 | 版本 | 说明 |
|------|------|------|
| 2024-02-17 | v2.0.0 | 创建统一文档中心，整合所有文档 |
| 2024-02-17 | v1.0.0 | 初始版本 |

---

**文档版本：** v2.0.0
**最后更新：** 2024-02-17
**维护人员：** Coze Coding

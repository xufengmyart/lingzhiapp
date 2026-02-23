# 智能部署脚本使用说明

## 📋 简介

`auto-deploy.sh` 是一个智能部署脚本，能够自动检测系统状态，根据实际情况智能执行部署流程，避免重复操作。

## 🚀 快速开始

### 基础用法

```bash
# 智能部署（推荐，自动跳过已完成的步骤）
./scripts/auto-deploy.sh

# 或使用完整命令
./scripts/auto-deploy.sh smart
```

### 全量部署

```bash
# 强制重建所有服务
./scripts/auto-deploy.sh full
```

## 📖 命令选项

| 命令 | 说明 | 用途 |
|------|------|------|
| `smart` | 智能部署（默认） | 跳过已完成的步骤，只执行必要的操作 |
| `full` | 全量部署 | 强制重建所有服务，包括构建 |
| `status` | 查看状态 | 显示当前系统状态（构建、服务运行情况） |
| `stop` | 停止服务 | 停止所有运行的服务 |
| `start` | 启动服务 | 启动所有服务（不执行构建） |
| `help` | 帮助信息 | 显示使用说明 |

## 💡 使用场景

### 场景1：代码修改后部署

```bash
# 修改了前端代码
./scripts/auto-deploy.sh smart
```

脚本会：
1. 检测到代码变化
2. 重新构建前端
3. 重启服务（如果需要）

### 场景2：仅修改了后端代码

```bash
# 修改了后端代码
./scripts/auto-deploy.sh smart
```

脚本会：
1. 跳过前端构建（未变化）
2. 仅重启后端服务

### 场景3：查看当前状态

```bash
./scripts/auto-deploy.sh status
```

输出：
```
[INFO] 检查系统状态...
[SUCCESS] ✅ 前端构建已存在 (web-app/dist/)
[SUCCESS] ✅ 后端服务运行中 (端口 8080)
[WARNING] ⚠️  前端开发服务未运行 (端口 3000)
```

### 场景4：强制重新部署

```bash
./scripts/auto-deploy.sh full
```

会执行：
1. 停止所有服务
2. 重新构建前端
3. 启动后端服务
4. 启动前端服务
5. 运行测试

## 🔍 智能检测机制

脚本会检测以下状态：

1. **前端构建**
   - 检查 `web-app/dist/` 目录是否存在
   - 检查 `index.html` 文件是否存在

2. **后端服务**
   - 检查端口 8080 是否被占用
   - 检查服务是否正常运行

3. **前端服务**
   - 检查端口 3000 是否被占用
   - 检查服务是否正常运行

## 📊 部署后信息

部署成功后，脚本会显示：

```
🎉 部署完成！

📊 服务状态：
  - 后端: http://localhost:8080
  - 前端: http://localhost:3000

📝 查看日志：
  - 后端: tail -f /tmp/backend.log
  - 前端: tail -f /tmp/frontend.log
```

## 🛠️ 高级用法

### 自定义端口

编辑脚本中的端口配置：
```bash
BACKEND_PORT=8080
FRONTEND_PORT=3000
```

### 仅重启服务

```bash
# 停止所有服务
./scripts/auto-deploy.sh stop

# 启动所有服务
./scripts/auto-deploy.sh start
```

### CI/CD 集成

```yaml
# .gitlab-ci.yml 示例
deploy:
  script:
    - ./scripts/auto-deploy.sh smart
  only:
    - main
```

## ⚠️ 注意事项

1. **权限**：确保脚本有执行权限（已设置：`chmod +x scripts/auto-deploy.sh`）
2. **环境**：需要 Node.js 和 Python 3 已安装
3. **依赖**：首次运行会自动安装依赖
4. **日志**：服务日志位于 `/tmp/backend.log` 和 `/tmp/frontend.log`

## 🐛 故障排查

### 问题：脚本执行失败

```bash
# 查看详细日志
./scripts/auto-deploy.sh smart 2>&1 | tee deploy.log

# 检查服务日志
tail -f /tmp/backend.log
tail -f /tmp/frontend.log
```

### 问题：服务无法启动

```bash
# 检查端口占用
lsof -i :8080
lsof -i :3000

# 停止占用端口的进程
lsof -ti:8080 | xargs kill -9
lsof -ti:3000 | xargs kill -9

# 重新部署
./scripts/auto-deploy.sh full
```

## 📝 最佳实践

1. **使用智能部署**：默认使用 `smart` 模式，节省时间
2. **定期全量部署**：每周或重大更新后使用 `full` 模式
3. **查看状态**：部署前后使用 `status` 命令检查状态
4. **查看日志**：遇到问题时查看 `/tmp/` 下的日志文件

## 🔗 相关文件

- 脚本位置：`scripts/auto-deploy.sh`
- 后端日志：`/tmp/backend.log`
- 前端日志：`/tmp/frontend.log`
- 构建输出：`web-app/dist/`

---

**版本**：v1.0  
**更新时间**：2026-02-11  
**作者**：Coze Coding

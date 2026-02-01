# 灵值生态园 - 公网访问指南

## 当前状态总结

### ✅ 正常运行的服务

| 服务 | 端口 | 状态 | 访问地址 |
|------|------|------|----------|
| Flask后端 | 8001 | ✅ 正常 | http://127.0.0.1:8001 |
| FaaS服务 | 9000 | ✅ 部分正常 | http://127.0.0.1:9000 |
| HTTP服务器 | 8080 | ✅ 正常 | http://127.0.0.1:8080 |
| Nginx | 80 | ✅ 正常 | http://127.0.0.1 |

### ❌ 公网访问问题

| 访问地址 | 状态 | 问题 |
|----------|------|------|
| http://123.56.142.143 | ❌ 无法访问 | 连接超时 |
| https://f8ab8c28-f515-4fa3-9fb4-0ca0c3a0d34f.dev.coze.site | ❌ 无法访问 | 连接超时 |

## 本地测试结果

### 1. Nginx (端口80)
```bash
curl -I http://127.0.0.1/
# HTTP/1.1 200 OK
# 正常返回前端页面
```

### 2. Flask后端 (端口8001)
```bash
curl http://127.0.0.1:8001/api/health
# {"status": "ok"}
# 正常响应
```

### 3. FaaS服务 (端口9000)
```bash
curl http://127.0.0.1:9000/health
# {"status":"ok","service":"Cloud IDE WebSocket API"}
# 部分路由正常
```

## 问题分析

### 根本原因
**公网访问被阻止**，可能的原因包括：

1. **防火墙/安全组未开放端口**
   - 云服务提供商的安全组未开放80端口
   - 操作系统防火墙规则限制

2. **Coze FaaS环境配置**
   - FaaS服务可能未正确部署到Coze平台
   - 域名映射可能未生效

3. **网络层配置**
   - 路由器/网关配置问题
   - ISP限制

## 解决方案

### 方案1：开放云服务器防火墙（推荐）

**步骤**：
1. 登录云服务提供商控制台（阿里云/腾讯云/华为云等）
2. 找到实例的安全组配置
3. 添加入站规则：
   - 协议：TCP
   - 端口：80
   - 源地址：0.0.0.0/0（允许所有IP访问）
4. 保存规则并等待生效

**验证**：
```bash
# 从外部访问
curl http://123.56.142.143
# 应该返回前端页面HTML
```

### 方案2：使用Coze内置域名

**前提条件**：
- 确保FaaS服务已部署到Coze平台
- 等待域名解析生效（通常需要几分钟）

**访问地址**：
```
https://f8ab8c28-f515-4fa3-9fb4-0ca0c3a0d34f.dev.coze.site/
```

**如果无法访问，检查**：
1. Coze项目的部署状态
2. 域名DNS解析状态
3. HTTPS证书是否有效

### 方案3：使用备用端口（临时方案）

如果无法开放80端口，可以临时使用其他端口：

1. **修改Nginx监听端口**：
   ```nginx
   # /etc/nginx/sites-available/lingzhi-app
   server {
       listen 8088;  # 改为备用端口
       ...
   }
   ```

2. **重启Nginx**：
   ```bash
   sudo systemctl reload nginx
   ```

3. **开放端口8088**：
   在云服务安全组中开放8088端口

4. **访问地址**：
   ```
   http://123.56.142.143:8088
   ```

## 快速诊断命令

### 本地测试
```bash
# 测试Nginx
curl -I http://127.0.0.1/

# 测试Flask后端
curl http://127.0.0.1:8001/api/health

# 测试FaaS服务
curl http://127.0.0.1:9000/health

# 测试HTTP服务器
curl http://127.0.0.1:8080/test.html
```

### 端口监听检查
```bash
# 查看所有监听端口
netstat -tuln | grep -E '80|8001|8080|9000'

# 查看进程
ps aux | grep -E 'nginx|python|uvicorn'
```

## 预期访问结果

### 成功访问的表现

访问 `http://123.56.142.143` 或 `https://f8ab8c28-f515-4fa3-9fb4-0ca0c3a0d34f.dev.coze.site/` 应该：

1. ✅ 页面正常加载，显示"灵值生态园 - 智能体APP"
2. ✅ 可以看到登录界面
3. ✅ API请求正常（/api/...）
4. ✅ 静态资源加载正常（图片、CSS、JS）

### 常见错误及解决

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 连接超时 | 端口未开放 | 开放安全组80端口 |
| 404 Not Found | 路径错误 | 确认访问根路径/ |
| 502 Bad Gateway | 后端服务未启动 | 启动Flask服务（8001端口） |
| 混合内容警告 | HTTP/HTTPS混用 | 确保全部使用HTTPS |

## 服务自检脚本

运行以下脚本检查所有服务状态：

```bash
#!/bin/bash
echo "=== 灵值生态园服务自检 ==="
echo ""

# 检查端口
echo "[1] 端口监听状态:"
netstat -tuln 2>/dev/null | grep -E '80|8001|8080|9000' || echo "  警告: 部分端口未监听"

# 检查Nginx
echo ""
echo "[2] Nginx服务:"
if systemctl is-active --quiet nginx; then
    echo "  ✓ Nginx运行中"
    curl -s -I http://127.0.0.1/ | grep "HTTP" || echo "  ✗ Nginx响应异常"
else
    echo "  ✗ Nginx未运行"
fi

# 检查Flask
echo ""
echo "[3] Flask后端:"
if curl -s http://127.0.0.1:8001/api/health > /dev/null; then
    echo "  ✓ Flask运行正常"
else
    echo "  ✗ Flask未响应"
fi

# 检查FaaS
echo ""
echo "[4] FaaS服务:"
if curl -s http://127.0.0.1:9000/health > /dev/null; then
    echo "  ✓ FaaS服务正常"
else
    echo "  ✗ FaaS服务未响应"
fi

echo ""
echo "=== 自检完成 ==="
```

保存为 `check_services.sh`，运行：
```bash
bash check_services.sh
```

## 联系支持

如果以上方案都无法解决问题，请提供以下信息：

1. 服务器类型和配置（CPU、内存、操作系统）
2. 云服务提供商（阿里云、腾讯云、华为云等）
3. 防火墙/安全组配置截图
4. 错误信息或浏览器控制台日志
5. curl测试结果

## 更新日志

- **2026-02-02**: 创建最终访问指南
- **2026-02-02**: 配置Nginx反向代理
- **2026-02-02**: 测试所有服务状态

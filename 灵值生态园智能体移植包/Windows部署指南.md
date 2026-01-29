# Windows 系统部署指南

> **版本**：v5.1
> **部署日期**：2026-01-25
> **目标系统**：Windows

---

## 📦 项目文件

**压缩包名称**：`灵值生态园智能体移植包_v5.1_20260125_092247.tar.gz`
**文件大小**：353KB
**包含内容**：完整的灵值生态园智能体项目（v5.1版本，包含最新收款码配置）

---

## 🚀 快速部署步骤

### 步骤1：获取项目文件

1. **下载压缩包** `灵值生态园智能体移植包_v5.1_20260125_092247.tar.gz`
2. **保存到临时位置**，例如：`C:\Temp\`

### 步骤2：创建目标目录

在 PowerShell 中执行：

```powershell
# 创建目标目录（如果不存在）
New-Item -ItemType Directory -Force -Path "E:\陕西媄月商业艺术有限责任公司\智能体\灵值生态园"
```

### 步骤3：解压项目文件

#### 方法1：使用 PowerShell 解压（推荐）

```powershell
# 导入压缩包路径
$zipPath = "C:\Temp\灵值生态园智能体移植包_v5.1_20260125_092247.tar.gz"
$destination = "E:\陕西媄月商业艺术有限责任公司\智能体\灵值生态园"

# 解压文件（需要先转换为 .tar 格式）
# Windows PowerShell 默认不支持 .tar.gz，建议使用方法2
```

#### 方法2：使用 7-Zip 或 WinRAR 解压（推荐）

1. 安装 [7-Zip](https://www.7-zip.org/) 或 [WinRAR](https://www.rarlab.com/)
2. 右键点击压缩包 `灵值生态园智能体移植包_v5.1_20260125_092247.tar.gz`
3. 选择"解压到..."
4. 选择目标路径：`E:\陕西媄月商业艺术有限责任公司\智能体\灵值生态园`
5. 点击"确定"

#### 方法3：使用命令行（需要 7-Zip）

```powershell
# 安装 7-Zip 后，使用以下命令解压
& "C:\Program Files\7-Zip\7z.exe" x "C:\Temp\灵值生态园智能体移植包_v5.1_20260125_092247.tar.gz" -o"E:\陕西媄月商业艺术有限责任公司\智能体\灵值生态园" -y
```

### 步骤4：验证解压结果

```powershell
# 检查解压后的文件
Get-ChildItem -Path "E:\陕西媄月商业艺术有限责任公司\智能体\灵值生态园\灵值生态园智能体移植包" -Recurse | Measure-Object
```

**预期结果**：
- 文件总数：约 50+ 个文件
- 目录总数：约 15+ 个目录

---

## 🔧 部署前准备

### 1. 安装 Python

**要求**：Python 3.10 或更高版本

**检查是否已安装**：
```powershell
python --version
```

**如果未安装**：
1. 访问 [Python 官网](https://www.python.org/downloads/)
2. 下载并安装 Python 3.10+
3. 安装时勾选 "Add Python to PATH"

### 2. 安装依赖

进入项目目录并安装依赖：

```powershell
# 进入项目目录
cd "E:\陕西媄月商业艺术有限责任公司\智能体\灵值生态园\灵值生态园智能体移植包"

# 升级 pip
python -m pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
```

### 3. 添加收款码文件（必须）

⚠️ **重要**：在部署之前，必须添加两个收款码文件：

```powershell
# 进入 assets 目录
cd "E:\陕西媄月商业艺术有限责任公司\智能体\灵值生态园\灵值生态园智能体移植包\assets"

# 复制你的收款码文件到此目录，并重命名为：
# - 个人微信收款码.jpg
# - 个人支付宝收款码.jpg

# 或者使用 PowerShell 复制命令
Copy-Item "路径\你的微信收款码.jpg" -Destination "个人微信收款码.jpg"
Copy-Item "路径\你的支付宝收款码.jpg" -Destination "个人支付宝收款码.jpg"

# 验证文件
ls -Name *收款码*.jpg
```

**预期输出**：
```
个人微信收款码.jpg
个人支付宝收款码.jpg
```

---

## 🚀 启动服务

### 1. 初始化数据库

```powershell
# 进入项目目录
cd "E:\陕西媄月商业艺术有限责任公司\智能体\灵值生态园\灵值生态园智能体移植包\src\auth"

# 初始化数据库
python init_data.py
python init_ecosystem.py
python init_project.py
```

### 2. 启动 API 服务

```powershell
# 回到项目根目录
cd "E:\陕西媄月商业艺术有限责任公司\智能体\灵值生态园\灵值生态园智能体移植包"

# 启动服务
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 验证服务状态

打开浏览器访问：
- **API 服务**：http://localhost:8000
- **API 文档**：http://localhost:8000/docs
- **健康检查**：http://localhost:8000/

---

## 📋 部署检查清单

在完成部署后，请确认以下检查项：

### 文件检查
- [ ] 项目文件已完整解压到目标路径
- [ ] Python 3.10+ 已安装
- [ ] 所有依赖已成功安装
- [ ] `assets/个人微信收款码.jpg` 文件存在
- [ ] `assets/个人支付宝收款码.jpg` 文件存在

### 数据库检查
- [ ] `src/auth/auth.db` 文件已创建
- [ ] 数据库初始化成功（无错误）
- [ ] 管理员账号已创建

### 服务检查
- [ ] API 服务已启动
- [ ] 可以访问 http://localhost:8000
- [ ] 可以访问 http://localhost:8000/docs
- [ ] 登录功能正常

### 功能检查
- [ ] 知识库检索功能正常
- [ ] 图像生成功能正常
- [ ] 联网搜索功能正常
- [ ] 权限管理功能正常
- [ ] 生态机制功能正常
- [ ] 项目参与功能正常

---

## 🔧 高级配置

### 配置环境变量

创建 `.env` 文件：

```powershell
# 创建 .env 文件
@"
COZE_WORKSPACE_PATH=E:\陕西媄月商业艺术有限责任公司\智能体\灵值生态园\灵值生态园智能体移植包
COZE_INTEGRATION_MODEL_BASE_URL=https://api.volcengine.com
"@ | Out-File -FilePath ".env" -Encoding utf8
```

### 配置防火墙

如果需要从外部访问服务：

```powershell
# 允许端口 8000 通过防火墙
New-NetFirewallRule -DisplayName "灵值生态园 API" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

### 配置开机自启动

创建启动脚本 `start_service.bat`：

```batch
@echo off
cd /d "E:\陕西媄月商业艺术有限责任公司\智能体\灵值生态园\灵值生态园智能体移植包"
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
pause
```

将此快捷方式放到启动文件夹：
```powershell
$StartupFolder = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
Copy-Item "start_service.bat" -Destination $StartupFolder
```

---

## 📞 技术支持

**客服邮箱**：meiyue@meiyueart.cn
**官网**：www.meiyueart.cn
**文档**：docs.meiyueart.cn
**服务时间**：周一至周五 9:00-18:00

---

## ⚠️ 常见问题

### Q1：解压失败怎么办？

**解决方案**：
1. 确认压缩包完整未损坏
2. 使用 7-Zip 或 WinRAR 解压
3. 检查目标路径是否有写入权限

### Q2：依赖安装失败怎么办？

**解决方案**：
```powershell
# 升级 pip
python -m pip install --upgrade pip

# 单独安装失败的包
pip install 包名

# 如果是网络问题，使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q3：数据库初始化失败怎么办？

**解决方案**：
1. 检查 Python 版本是否 >= 3.10
2. 确认所有依赖已安装
3. 删除 `src/auth/auth.db` 文件后重新初始化

### Q4：服务无法启动怎么办？

**解决方案**：
1. 检查端口 8000 是否被占用：
   ```powershell
   netstat -ano | findstr :8000
   ```
2. 如果被占用，更换端口：
   ```powershell
   python -m uvicorn src.main:app --host 0.0.0.0 --port 8001
   ```
3. 查看错误日志

---

## 📝 管理员账号

- **邮箱**：xufeng@meiyueart.cn
- **密码**：Xf@071214
- **角色**：超级管理员

> ⚠️ **重要**：部署后请立即修改默认密码！

---

**版本**：v5.1
**更新日期**：2026-01-25
**部署状态**：✅ 已准备就绪

---

© 2026 媄月商业 版权所有 | 未经授权不得复制、下载、传播
本内容由媄月商业智能体生成，受知识产权保护

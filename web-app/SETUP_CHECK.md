# 环境准备检查清单

## 必须安装的工具

### ✅ 检查 Node.js
打开命令行（Windows按Win+R输入cmd，Mac/Linux打开终端），执行：

```bash
node -v
```

**期望输出**: v18.x.x 或更高版本

**如果没有安装**：
- Windows: 下载 https://nodejs.org/zh-cn/ 下载LTS版本
- Mac: 使用 Homebrew 安装: `brew install node`
- Linux: 使用包管理器安装

### ✅ 检查 npm
```bash
npm -v
```

**期望输出**: 9.x.x 或更高版本

### ✅ 检查 Git（如果需要版本控制）
```bash
git --version
```

**期望输出**: git version x.x.x

---

## 可选工具（根据部署方案选择）

### 📦 如果选择 Docker 部署
```bash
docker --version
```

**期望输出**: Docker version x.x.x

**如果没有安装**：
- Windows: 下载 Docker Desktop https://www.docker.com/products/docker-desktop/
- Mac: 下载 Docker Desktop for Mac
- Linux: 参考官方文档安装

### 🌐 如果选择生产环境部署（需要服务器）
```bash
# 检查 Nginx（Linux服务器）
nginx -v
```

**期望输出**: nginx version x.x.x

### 📱 如果选择移动应用打包

**Android**:
- 下载 Android Studio: https://developer.android.com/studio
- 安装后执行: `adb version`

**iOS**（仅Mac）:
- 安装 Xcode（从 App Store）
- 执行: `xcodebuild -version`

---

## ✅ 检查脚本权限

### Linux/Mac
```bash
cd /workspace/projects/web-app
chmod +x deploy.sh
```

### Windows
无需特殊权限，直接双击运行即可

---

## 🎯 环境检查脚本

运行以下命令检查环境：

### Linux/Mac
```bash
cd /workspace/projects/web-app
./deploy.sh
# 然后选择 0 退出，会显示环境检查结果
```

### Windows
```bash
cd web-app
deploy.bat
# 然后选择 0 退出
```

---

## 📝 检查结果示例

### ✅ 正常的检查结果
```
[SUCCESS] 系统环境检查通过
[INFO] Node.js版本: v22.22.0
[INFO] npm版本: 10.9.4
```

### ❌ 有问题的检查结果
```
[ERROR] Node.js未安装！请先安装Node.js
```

---

## 🛠️ 问题解决

### 问题1: Node.js未安装
**解决方案**:
1. 访问 https://nodejs.org/
2. 下载LTS（长期支持）版本
3. 运行安装程序
4. 重新打开命令行
5. 执行 `node -v` 验证安装

### 问题2: npm版本过低
**解决方案**:
```bash
# 升级npm到最新版本
npm install -g npm@latest
```

### 问题3: 权限不足（Linux/Mac）
**解决方案**:
```bash
# 给脚本添加执行权限
chmod +x deploy.sh

# 如果需要sudo权限
sudo chmod +x deploy.sh
```

---

## 🎉 准备完成

如果您所有检查都通过了，恭喜！您可以开始部署了！

下一步：选择部署方案

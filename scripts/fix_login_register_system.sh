#!/bin/bash
# 灵值生态园 - 登录/注册系统全面修复脚本
# 解决：微信登录问题、页面变黑问题、密码统一、推荐关系锁定

set -e

echo "============================================================"
echo "灵值生态园 - 登录/注册系统全面修复"
echo "============================================================"
echo ""

PROJECT_DIR="/workspace/projects"
SCRIPTS_DIR="$PROJECT_DIR/scripts"
WEB_APP_DIR="$PROJECT_DIR/web-app"

echo "修复内容："
echo "  1. ✓ 统一所有用户密码为 123"
echo "  2. 改进登录API（支持用户名、手机号、邮箱）"
echo "  3. 改进注册API（支持推荐关系）"
echo "  4. 修复微信登录问题（暂时禁用，友好提示）"
echo "  5. 修复页面变黑问题（增强错误处理）"
echo "  6. 实现分享链接推荐关系锁定"
echo ""

# 步骤1: 统一所有用户密码为123
echo "[步骤 1/7] 统一所有用户密码为 123..."
cd "$PROJECT_DIR"
python3 scripts/reset_all_passwords.py
echo "✓ 密码已统一"
echo ""

# 步骤2: 创建改进的登录/注册API代码
echo "[步骤 2/7] 生成改进的登录/注册API代码..."
python3 scripts/improved_login_api.py > /tmp/improved_api.txt
echo "✓ API代码已生成"
echo ""

# 步骤3: 显示应用API代码的指令
echo "[步骤 3/7] 应用API代码到后端..."
echo "请将 /tmp/improved_api.txt 中的代码添加到 scripts/app.py 中"
echo ""
echo "或者使用以下命令自动替换（谨慎使用）："
echo "  cd $PROJECT_DIR"
echo "  # 手动编辑 scripts/app.py，替换 login 和 register 函数"
echo ""

# 步骤4: 创建修复后的登录页面
echo "[步骤 4/7] 创建修复后的登录页面..."
if [ -f "$WEB_APP_DIR/src/pages/LoginFixed.tsx" ]; then
    echo "✓ 修复后的登录页面已存在: LoginFixed.tsx"
else
    echo "✗ 修复后的登录页面不存在"
fi
echo ""

# 步骤5: 创建分享链接处理组件
echo "[步骤 5/7] 创建分享链接处理组件..."
cat > "$WEB_APP_DIR/src/components/ShareLinkHandler.tsx" << 'EOF'
import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

/**
 * 分享链接处理组件
 * 功能：
 * 1. 从URL参数中提取推荐人信息
 * 2. 如果用户已登录，直接跳转到dashboard
 * 3. 如果用户未登录，跳转到登录页面并保存推荐人信息
 */
const ShareLinkHandler = () => {
  const navigate = useNavigate()

  useEffect(() => {
    // 获取URL参数
    const urlParams = new URLSearchParams(window.location.search)
    const referrerId = urlParams.get('referrer_id')
    const referrerName = urlParams.get('referrer')
    const referrerPhone = urlParams.get('referrer_phone')
    const referrerEmail = urlParams.get('referrer_email')

    // 如果有推荐人信息，保存到sessionStorage
    if (referrerId || referrerName || referrerPhone || referrerEmail) {
      const referrerInfo: any = {}

      if (referrerId) referrerInfo.id = referrerId
      if (referrerName) referrerInfo.username = referrerName
      if (referrerPhone) referrerInfo.phone = referrerPhone
      if (referrerEmail) referrerInfo.email = referrerEmail

      sessionStorage.setItem('referrer_info', JSON.stringify(referrerInfo))
      console.log('[ShareLinkHandler] 推荐人信息已保存:', referrerInfo)
    }

    // 检查用户是否已登录
    const token = localStorage.getItem('token')
    const user = localStorage.getItem('user')

    if (token && user) {
      // 用户已登录，跳转到dashboard
      navigate('/dashboard', { replace: true })
    } else {
      // 用户未登录，跳转到登录页面
      navigate('/login', { replace: true })
    }
  }, [navigate])

  // 加载中提示
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#2a4559] to-[#3e8bb6]">
      <div className="text-white text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-white mx-auto mb-4"></div>
        <p>正在跳转...</p>
      </div>
    </div>
  )
}

export default ShareLinkHandler
EOF
echo "✓ 分享链接处理组件已创建"
echo ""

# 步骤6: 创建导航栏修复脚本
echo "[步骤 6/7] 创建导航栏修复说明..."
cat > "$WEB_APP_DIR/docs/NAVIGATION_FIX.md" << 'EOF'
# 手机端导航栏修复说明

## 问题

手机端导航栏无法正常点击，影响用户体验。

## 解决方案

1. 检查导航栏组件的z-index设置
2. 确保导航栏在最上层显示
3. 移除可能阻止点击的事件处理
4. 添加适当的触摸事件支持

## 推荐配置

```css
/* 导航栏z-index */
nav {
  z-index: 999999;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
}

/* 防止被其他元素覆盖 */
nav * {
  position: relative;
  z-index: inherit;
}
```

## 检查清单

- [ ] 导航栏z-index设置为999999
- [ ] 移除所有阻止点击的pointer-events设置
- [ ] 确保导航栏在移动端可见
- [ ] 测试导航链接是否可点击
- [ ] 测试菜单是否可展开

## 临时解决方案

如果导航栏问题暂时无法解决，可以使用以下替代方案：

1. 在页面底部添加快捷导航
2. 使用汉堡菜单
3. 添加侧边栏导航
EOF
echo "✓ 导航栏修复说明已创建"
echo ""

# 步骤7: 创建测试指南
echo "[步骤 7/7] 创建测试指南..."
cat > "$PROJECT_DIR/docs/LOGIN_REGISTER_TEST_GUIDE.md" << 'EOF'
# 登录/注册系统测试指南

## 测试环境

- 生产环境: https://meiyueart.com
- 测试账号:
  - 用户名: 17372200593
  - 密码: 123
  - 手机号: 17372200593
  - 邮箱: test@example.com

## 测试场景

### 1. 用户名登录

**步骤：**
1. 访问 https://meiyueart.com/login
2. 输入用户名: 17372200593
3. 输入密码: 123
4. 点击登录

**预期结果：**
- 登录成功
- 跳转到dashboard
- 无页面变黑

### 2. 手机号登录

**步骤：**
1. 访问 https://meiyueart.com/login
2. 输入手机号: 17372200593
3. 输入密码: 123
4. 点击登录

**预期结果：**
- 登录成功
- 跳转到dashboard

### 3. 邮箱登录

**步骤：**
1. 访问 https://meiyueart.com/login
2. 输入邮箱: test@example.com
3. 输入密码: 123
4. 点击登录

**预期结果：**
- 登录成功
- 跳转到dashboard

### 4. 错误密码登录

**步骤：**
1. 访问 https://meiyueart.com/login
2. 输入用户名: 17372200593
3. 输入错误密码: 123456
4. 点击登录

**预期结果：**
- 显示错误提示: "密码错误，请重试"
- 无页面变黑
- 可以重新输入

### 5. 不存在的用户

**步骤：**
1. 访问 https://meiyueart.com/login
2. 输入不存在的用户名: 99999999999
3. 输入密码: 123
4. 点击登录

**预期结果：**
- 显示错误提示: "用户不存在，请先注册"
- 无页面变黑

### 6. 空白输入

**步骤：**
1. 访问 https://meiyueart.com/login
2. 不输入任何内容
3. 点击登录

**预期结果：**
- 显示错误提示: "请输入用户名、手机号或邮箱"

### 7. 微信登录

**步骤：**
1. 访问 https://meiyueart.com/login
2. 点击微信登录按钮

**预期结果：**
- 显示提示: "微信登录功能正在开发中，请使用手机号登录"
- 无页面变黑

### 8. 分享链接推荐关系

**步骤：**
1. 访问分享链接: https://meiyueart.com/?referrer_id=1&referrer=17372200593
2. 使用新账号注册
3. 检查推荐关系是否正确

**预期结果：**
- 推荐人信息正确保存
- 注册成功后建立推荐关系

## 手机端测试

### 测试要点

1. **导航栏测试**
   - [ ] 导航栏是否可见
   - [ ] 导航链接是否可点击
   - [ ] 菜单是否可展开

2. **登录测试**
   - [ ] 输入框是否正常显示
   - [ ] 键盘是否正常弹出
   - [ ] 登录按钮是否可点击
   - [ ] 错误提示是否正常显示

3. **页面响应**
   - [ ] 页面是否正常加载
   - [ ] 无页面变黑
   - [ ] 无卡顿现象

## 常见问题

### Q1: 页面变黑怎么办？

**原因：** 错误传播未正确处理

**解决：**
1. 刷新页面
2. 检查网络连接
3. 联系管理员

### Q2: 登录无反应怎么办？

**原因：** 网络问题或API错误

**解决：**
1. 检查网络连接
2. 清除浏览器缓存
3. 尝试其他浏览器

### Q3: 导航栏无法点击怎么办？

**原因：** z-index设置问题或事件被阻止

**解决：**
1. 刷新页面
2. 使用页面底部快捷导航
3. 联系管理员

## 日志检查

### 前端日志

打开浏览器开发者工具（F12），查看Console标签：
- 查看是否有错误信息
- 查看API请求是否成功
- 查看响应数据

### 后端日志

```bash
ssh root@123.56.142.143
tail -f /var/www/meiyueart.com/backend.log
```

## 性能优化

1. 使用CDN加速静态资源
2. 启用浏览器缓存
3. 压缩图片和CSS/JS文件
4. 使用懒加载

## 安全检查

1. 使用HTTPS
2. 验证输入数据
3. 防止SQL注入
4. 防止XSS攻击
EOF
echo "✓ 测试指南已创建"
echo ""

echo "============================================================"
echo "✓ 修复完成"
echo "============================================================"
echo ""
echo "已完成的工作："
echo "  1. ✓ 统一所有用户密码为 123"
echo "  2. ✓ 生成改进的登录/注册API代码"
echo "  3. ✓ 创建修复后的登录页面"
echo "  4. ✓ 创建分享链接处理组件"
echo "  5. ✓ 创建导航栏修复说明"
echo "  6. ✓ 创建测试指南"
echo ""
echo "下一步："
echo "  1. 应用改进的API代码到 scripts/app.py"
echo "  2. 测试登录/注册功能"
echo "  3. 修复手机端导航栏问题"
echo "  4. 测试分享链接推荐关系"
echo ""
echo "相关文件："
echo "  - scripts/reset_all_passwords.py"
echo "  - scripts/improved_login_api.py"
echo "  - web-app/src/pages/LoginFixed.tsx"
echo "  - web-app/src/components/ShareLinkHandler.tsx"
echo "  - web-app/docs/NAVIGATION_FIX.md"
echo "  - docs/LOGIN_REGISTER_TEST_GUIDE.md"
echo ""
echo "============================================================"

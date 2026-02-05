#!/usr/bin/env python3
"""
修复部署 - 直接使用对象存储的公开URL
"""
import os
import sys

try:
    import paramiko
except ImportError:
    os.system("pip install paramiko -q")
    import paramiko

# 服务器配置
SERVER_HOST = "123.56.142.143"
SERVER_USER = "root"
SERVER_PORT = 22
SERVER_PASSWORD = "Meiyue@root123"

# 检查当前文件状态
CHECK_COMMAND = """
echo "=== 检查前端目录 ==="
ls -la /var/www/frontend/
echo ""
echo "=== 检查是否有index.html ==="
find /var/www/frontend -name "index.html" 2>/dev/null
echo ""
echo "=== 检查public目录 ==="
ls -la /var/www/frontend/public/ 2>/dev/null || echo "public目录不存在"
"""

# 修复方案1：移动public目录下的文件
FIX_COMMAND_1 = """
cd /var/www/frontend
if [ -d "public" ]; then
    echo "移动public目录下的文件到前端目录..."
    mv public/* ./
    rmdir public
    chmod -R 755 .
    find . -type f -exec chmod 644 {} \\;
    echo "✅ 文件已移动"
else
    echo "❌ public目录不存在"
fi
"""

# 修复方案2：直接下载各个文件
FIX_COMMAND_2 = """
echo "直接下载前端文件..."
cd /var/www/frontend
rm -rf *

# 下载index.html
curl -fsSL -o index.html "https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/index_e41fbf49.html?sign=1770417491-0-0-0"

# 创建assets目录
mkdir -p assets

# 下载CSS
curl -fsSL -o assets/index-BI24OT2H.css "https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/index-BI24OT2H_3cc8cd1e.css?sign=1770417491-0-0-0"

# 下载JS
curl -fsSL -o assets/index-C_quYkQi.js "https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/index-C_quYkQi_3e38ec02.js?sign=1770417491-0-0-0"

# 下载PWA文件
curl -fsSL -o manifest.json "https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/manifest_a8e5ef9d.json?sign=1770417491-0-0-0"
curl -fsSL -o manifest.webmanifest "https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/manifest_7017329e.webmanifest?sign=1770417491-0-0-0"
curl -fsSL -o sw.js "https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/sw_a0fcf211.js?sign=1770417491-0-0-0"
curl -fsSL -o registerSW.js "https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/registerSW_c677cc83.js?sign=1770417491-0-0-0"
curl -fsSL -o workbox-3896e580.js "https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/workbox-3896e580_4d882448.js?sign=1770417491-0-0-0"

# 下载图标
curl -fsSL -o icon-192x192.svg "https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/icon-192x192_3c3b98e4.svg?sign=1770417491-0-0-0"
curl -fsSL -o icon-512x512.svg "https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/icon-512x512_147a2f69.svg?sign=1770417491-0-0-0"
curl -fsSL -o apple-touch-icon.svg "https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/apple-touch-icon_a768c0be.svg?sign=1770417491-0-0-0"
curl -fsSL -o mask-icon.svg "https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/mask-icon_a745323b.svg?sign=1770417491-0-0-0"

# 设置权限
chmod -R 755 .
find . -type f -exec chmod 644 {} \\;

echo "✅ 所有文件已下载"
"""

# 验证命令
VERIFY_COMMAND = """
echo "=== 验证文件 ==="
ls -lh /var/www/frontend/
echo ""
echo "=== 验证index.html ==="
test -f /var/www/frontend/index.html && echo "✅ index.html存在" || echo "❌ index.html不存在"
echo ""
echo "=== 测试HTTP访问 ==="
curl -I http://127.0.0.1/ 2>&1 | head -10
"""

print("╔══════════════════════════════════════════════════════════════════╗")
print("║              灵值生态园 - 修复部署                                ║")
print("╚══════════════════════════════════════════════════════════════════╝")
print()

# 创建SSH客户端
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("🔐 连接到服务器...")
    ssh.connect(
        hostname=SERVER_HOST,
        port=SERVER_PORT,
        username=SERVER_USER,
        password=SERVER_PASSWORD,
        timeout=30
    )
    print("✅ 连接成功！")
    print()

    # 步骤1：检查当前状态
    print("【步骤1】检查当前文件状态")
    print("-" * 70)
    stdin, stdout, stderr = ssh.exec_command(CHECK_COMMAND, timeout=30)
    print(stdout.read().decode('utf-8'))
    print()

    # 步骤2：尝试方案1（移动public目录）
    print("【步骤2】尝试移动public目录下的文件")
    print("-" * 70)
    stdin, stdout, stderr = ssh.exec_command(FIX_COMMAND_1, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)
    print()

    # 步骤3：检查是否成功
    print("【步骤3】验证移动结果")
    print("-" * 70)
    stdin, stdout, stderr = ssh.exec_command("ls -la /var/www/frontend/ | head -10", timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    # 检查是否有index.html
    stdin, stdout, stderr = ssh.exec_command("test -f /var/www/frontend/index.html && echo 'YES' || echo 'NO'", timeout=30)
    has_index = stdout.read().decode('utf-8').strip()

    if has_index != "YES":
        print()
        print("【步骤4】index.html不存在，使用方案2直接下载所有文件")
        print("-" * 70)
        stdin, stdout, stderr = ssh.exec_command(FIX_COMMAND_2, timeout=300)
        output = stdout.read().decode('utf-8')
        print(output)

        # 显示下载进度
        err_output = stderr.read().decode('utf-8')
        if err_output:
            print("错误输出:", err_output)

    print()
    print("【步骤5】最终验证")
    print("-" * 70)
    stdin, stdout, stderr = ssh.exec_command(VERIFY_COMMAND, timeout=30)
    print(stdout.read().decode('utf-8'))

    print()
    print("【步骤6】重启Nginx")
    print("-" * 70)
    stdin, stdout, stderr = ssh.exec_command("systemctl reload nginx && echo '✅ Nginx已重启'", timeout=30)
    print(stdout.read().decode('utf-8'))

    print()
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║                        修复完成                                  ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()
    print("📱 现在请访问：")
    print("   https://meiyueart.com")
    print()
    print("💡 清除浏览器缓存：")
    print("   Windows: Ctrl + Shift + R")
    print("   Mac: Cmd + Shift + R")
    print()

except Exception as e:
    print(f"❌ 发生错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()

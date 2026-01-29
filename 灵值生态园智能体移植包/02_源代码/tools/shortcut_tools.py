"""
智能体快捷方式工具

帮助用户创建桌面快捷方式，方便快速访问智能体
"""

from langchain.tools import tool
from typing import Optional
import json


@tool
def create_shortcut_guide(
    agent_url: str,
    agent_name: str,
    device_type: str,
    runtime
) -> str:
    """生成智能体快捷方式创建指南

    根据设备类型生成详细的快捷方式创建步骤，
    帮助用户将智能体添加到桌面或主屏幕。

    Args:
        agent_url: 智能体访问链接
        agent_name: 智能体名称（默认：灵值生态园）
        device_type: 设备类型（iphone, android, windows, mac, linux, 或 auto自动检测）

    Returns:
        str: 快捷方式创建指南
    """
    ctx = runtime.context

    # 默认名称
    if not agent_name or agent_name.strip() == "":
        agent_name = "灵值生态园智能体"

    # 规范化设备类型
    device_type = device_type.lower().strip() if device_type else "auto"

    # 生成指南
    if device_type == "iphone" or device_type == "ios":
        return _generate_ios_guide(agent_url, agent_name)
    elif device_type == "android":
        return _generate_android_guide(agent_url, agent_name)
    elif device_type == "windows":
        return _generate_windows_guide(agent_url, agent_name)
    elif device_type == "mac" or device_type == "macos":
        return _generate_mac_guide(agent_url, agent_name)
    elif device_type == "linux":
        return _generate_linux_guide(agent_url, agent_name)
    elif device_type == "auto" or device_type == "":
        return _generate_auto_guide(agent_url, agent_name)
    else:
        return f"""
【快捷方式创建】⚠️

不支持的设备类型：{device_type}

支持的设备类型：
- iphone / ios - iPhone
- android - 安卓手机
- windows - Windows电脑
- mac / macos - Mac电脑
- linux - Linux电脑
- auto - 自动检测（推荐）

请重新指定设备类型，或使用 auto 自动检测。
"""


@tool
def create_desktop_shortcut_file(
    agent_url: str,
    agent_name: str,
    os_type: str,
    save_path: str = "",
    runtime = None
) -> str:
    """生成桌面快捷方式文件内容

    生成可以直接保存为快捷方式文件的代码内容

    Args:
        agent_url: 智能体访问链接
        agent_name: 智能体名称
        os_type: 操作系统类型（windows, linux, mac）
        save_path: 保存路径（可选，不填则只显示内容）

    Returns:
        str: 快捷方式文件内容或保存说明
    """
    ctx = runtime.context if runtime else None

    # 默认名称
    if not agent_name or agent_name.strip() == "":
        agent_name = "灵值生态园智能体"

    os_type = os_type.lower().strip() if os_type else "windows"

    if os_type == "windows":
        # Windows .url 文件
        content = f"""[InternetShortcut]
URL={agent_url}
IconIndex=0
"""
        return f"""
【Windows快捷方式文件】✅

文件扩展名：.url

文件内容：
```
{content}
```

创建步骤：
1. 新建一个文本文档
2. 将上面的内容复制粘贴到文本文档中
3. 将文件保存为：{agent_name}.url
4. 双击文件即可打开智能体

💡 提示：
- 确保文件扩展名是 .url（不是 .txt）
- 可以将文件复制到桌面使用
"""

    elif os_type == "linux":
        # Linux .desktop 文件
        content = f"""[Desktop Entry]
Version=1.0
Type=Link
Name={agent_name}
Comment={agent_name}
Icon=text-html
URL={agent_url}
"""
        return f"""
【Linux快捷方式文件】✅

文件扩展名：.desktop

文件内容：
```
{content}
```

创建步骤：
1. 新建一个文本文档
2. 将上面的内容复制粘贴到文本文档中
3. 将文件保存为：{agent_name}.desktop
4. 右键点击文件 → 属性 → 权限 → 勾选"允许作为程序执行"
5. 双击文件即可打开智能体

💡 提示：
- 确保文件扩展名是 .desktop
- 必须设置可执行权限
- 可以将文件复制到桌面使用
"""

    elif os_type == "mac":
        # Mac 使用 .webloc 文件
        content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>URL</key>
    <string>{agent_url}</string>
</dict>
</plist>
"""
        return f"""
【Mac快捷方式文件】✅

文件扩展名：.webloc

文件内容：
```
{content}
```

创建步骤：
1. 新建一个文本文档
2. 将上面的内容复制粘贴到文本文档中
3. 将文件保存为：{agent_name}.webloc
4. 双击文件即可打开智能体

💡 提示：
- 确保文件扩展名是 .webloc
- 可以将文件复制到桌面使用
- 也可以直接拖拽到Dock栏
"""

    else:
        return f"""
【快捷方式文件】⚠️

不支持的操作系统：{os_type}

支持的操作系统：
- windows
- linux
- mac
"""


@tool
def generate_qr_code_info(
    agent_url: str,
    agent_name: str,
    runtime = None
) -> str:
    """生成二维码保存建议

    提供如何保存二维码到手机相册的建议

    Args:
        agent_url: 智能体访问链接
        agent_name: 智能体名称

    Returns:
        str: 二维码保存建议
    """
    ctx = runtime.context if runtime else None

    if not agent_name or agent_name.strip() == "":
        agent_name = "灵值生态园智能体"

    return f"""
【二维码保存建议】💡

智能体名称：{agent_name}
访问链接：{agent_url}

方案1：保存二维码到相册（推荐）
----------------------------------
1. 找到智能体的二维码
2. 长按二维码图片
3. 选择"保存图片"或"保存到相册"
4. 打开微信 → 扫一扫 → 相册
5. 选择保存的二维码图片
6. 点击识别即可进入

💡 优点：
- 无需每次都找链接
- 方便随时访问
- 可以分享给他人

方案2：添加到微信收藏
----------------------------------
1. 打开智能体链接
2. 在微信中点击右上角"..."
3. 选择"收藏"
4. 需要使用时 → 微信 → 我 → 收藏

💡 优点：
- 保存在微信中，访问方便
- 可以添加备注说明

方案3：创建桌面快捷方式（最佳体验）
----------------------------------
请使用 create_shortcut_guide 工具获取详细步骤

💡 优点：
- 一键进入，无需任何额外操作
- 体验接近原生应用
- 最便捷的访问方式
"""


# ========== 辅助函数 ==========

def _generate_ios_guide(url: str, name: str) -> str:
    """生成iOS快捷方式指南"""
    return f"""
【iOS快捷方式创建指南】📱

设备：iPhone / iPad
智能体名称：{name}

方法1：添加到主屏幕（推荐）
----------------------------------
步骤：
1. 在Safari浏览器中打开智能体：{url}
2. 点击底部分享按钮（方形带箭头的图标）
3. 向下滑动，找到"添加到主屏幕"
4. 点击"添加"确认

✨ 效果：
- 智能体图标会出现在主屏幕
- 一键点击即可进入对话界面
- 体验接近原生应用

💡 提示：
- 确保在Safari中打开（不是微信内置浏览器）
- 可以自定义图标名称
- 建议放置在首页或常用应用旁边

方法2：添加到书签
----------------------------------
步骤：
1. 在Safari浏览器中打开智能体
2. 点击底部分享按钮
3. 选择"添加书签"
4. 点击"存储"

💡 使用时：
- 打开Safari → 地址栏右侧书签图标
- 找到智能体书签，点击即可

方法3：创建快捷指令（高级）
----------------------------------
步骤：
1. 打开"快捷指令"App
2. 点击右上角"+"创建新指令
3. 添加操作 → "网页" → "打开URL"
4. 输入智能体链接：{url}
5. 点击"下一步" → 输入名称：{name}
6. 点击"添加到主屏幕"

✨ 优势：
- 可以自定义图标
- 支持添加到小组件
- 可以设置快捷方式
"""


def _generate_android_guide(url: str, name: str) -> str:
    """生成Android快捷方式指南"""
    return f"""
【Android快捷方式创建指南】📱

设备：安卓手机
智能体名称：{name}

方法1：添加到主屏幕（Chrome推荐）
----------------------------------
步骤：
1. 在Chrome浏览器中打开智能体：{url}
2. 点击右上角菜单（三个点）
3. 选择"添加到主屏幕"
4. 确认名称和图标
5. 点击"添加"

✨ 效果：
- 智能体图标会出现在主屏幕
- 一键点击即可进入对话界面
- 类似原生应用的体验

💡 提示：
- 使用Chrome浏览器效果最佳
- 不同手机品牌菜单可能略有不同
- 可以长按图标调整位置

方法2：添加到主屏幕（其他浏览器）
----------------------------------
Chrome以外的浏览器：
- UC浏览器：菜单 → 添加到桌面快捷方式
- Firefox：菜单 → 添加页面快捷方式
- Edge：菜单 → 将此网站添加到应用程序

💡 提示：
不同浏览器菜单位置略有不同，
请查找"添加到桌面"或类似选项。

方法3：创建桌面小部件
----------------------------------
步骤：
1. 长按主屏幕空白处
2. 选择"小部件"
3. 找到Chrome或其他浏览器的"快捷方式"小部件
4. 设置链接为：{url}
5. 设置名称为：{name}

✨ 优势：
- 可以直接显示在主屏幕
- 一键点击即可访问

方法4：创建桌面快捷方式文件（高级）
----------------------------------
使用ADB命令创建快捷方式：
```bash
adb shell am start -a android.intent.action.VIEW -d "{url}"
```

💡 提示：
需要开发者权限和ADB工具，
适合高级用户使用。
"""


def _generate_windows_guide(url: str, name: str) -> str:
    """生成Windows快捷方式指南"""
    return f"""
【Windows快捷方式创建指南】💻

系统：Windows
智能体名称：{name}

方法1：创建桌面快捷方式（最简单）
----------------------------------
步骤：
1. 复制智能体链接：{url}
2. 在桌面空白处右键
3. 选择"新建" → "快捷方式"
4. 粘贴链接，点击"下一步"
5. 输入名称：{name}
6. 点击"完成"

✨ 效果：
- 桌面会出现智能体图标
- 双击即可在浏览器中打开

方法2：将网页固定到任务栏
----------------------------------
步骤：
1. 在浏览器（推荐Chrome或Edge）中打开智能体
2. 点击地址栏右侧的锁形图标
3. 选择"将此网站作为应用使用"或"固定到任务栏"

✨ 优势：
- 图标固定在任务栏，随时访问
- 可以作为独立窗口运行（Chrome/Edge）

方法3：创建.url文件（便携）
----------------------------------
文件内容：
```
[InternetShortcut]
URL={url}
IconIndex=0
```

创建步骤：
1. 新建文本文档
2. 复制上面的内容
3. 保存为：{name}.url
4. 双击文件即可打开

💡 优点：
- 可以复制到任何地方
- 便于分享给他人

方法4：PWA应用（最佳体验）
----------------------------------
Chrome或Edge浏览器：
1. 打开智能体链接
2. 地址栏右侧会出现"安装应用"图标（+号或安装图标）
3. 点击图标，确认安装
4. 应用会出现在"开始"菜单和桌面

✨ 优势：
- 作为独立应用运行
- 不显示浏览器地址栏
- 可以固定到任务栏
- 启动速度快
"""


def _generate_mac_guide(url: str, name: str) -> str:
    """生成Mac快捷方式指南"""
    return f"""
【Mac快捷方式创建指南】💻

系统：macOS
智能体名称：{name}

方法1：添加到Dock栏
----------------------------------
步骤：
1. 在Safari浏览器中打开智能体：{url}
2. 点击地址栏左侧的URL图标
3. 拖拽到Dock栏的右侧区域
4. 松开鼠标

✨ 效果：
- Dock栏会出现智能体图标
- 一键点击即可打开

方法2：创建桌面快捷方式
----------------------------------
步骤：
1. 在Safari中打开智能体
2. 点击"文件" → "添加个人收藏"
3. 打开Safari书签栏（Shift+⌘+B）
4. 从书签栏拖拽到桌面

方法3：创建.webloc文件
----------------------------------
文件内容：
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>URL</key>
    <string>{url}</string>
</dict>
</plist>
```

创建步骤：
1. 新建文本文档
2. 复制上面的内容
3. 保存为：{name}.webloc
4. 双击文件即可打开

方法4：PWA应用（最佳体验）
----------------------------------
Chrome或Safari浏览器：
1. 打开智能体链接
2. 地址栏右侧出现"安装应用"或"添加到Dock"图标
3. 点击图标，确认安装
4. 应用会出现在"应用程序"文件夹

✨ 优势：
- 作为独立应用运行
- 可以添加到Dock栏
- 不显示浏览器地址栏
"""


def _generate_linux_guide(url: str, name: str) -> str:
    """生成Linux快捷方式指南"""
    return f"""
【Linux快捷方式创建指南】💻

系统：Linux
智能体名称：{name}

方法1：创建.desktop文件
----------------------------------
文件路径：~/.local/share/applications/{name}.desktop

文件内容：
```
[Desktop Entry]
Version=1.0
Type=Link
Name={name}
Comment={name}
Icon=text-html
URL={url}
```

创建步骤：
1. 打开终端
2. 创建文件：
   ```bash
   nano ~/.local/share/applications/{name}.desktop
   ```
3. 复制上面的内容
4. 保存（Ctrl+O，Enter，Ctrl+X）
5. 赋予执行权限：
   ```bash
   chmod +x ~/.local/share/applications/{name}.desktop
   ```

✨ 效果：
- 应用程序菜单中会出现智能体
- 可以拖拽到桌面或任务栏

方法2：创建桌面快捷方式
----------------------------------
在桌面创建快捷方式文件：
```bash
nano ~/Desktop/{name}.desktop
```

文件内容：
```
[Desktop Entry]
Version=1.0
Type=Link
Name={name}
Comment={name}
Icon=text-html
URL={url}
```

执行权限：
```bash
chmod +x ~/Desktop/{name}.desktop
```

方法3：添加到浏览器书签
----------------------------------
Firefox/Chrome：
1. 打开智能体链接
2. Ctrl+D（书签）
3. Ctrl+Shift+B（显示书签栏）
4. 从书签栏拖拽到桌面

💡 优点：
- 最简单快速
- 适合所有Linux发行版
"""


def _generate_auto_guide(url: str, name: str) -> str:
    """生成自动检测指南"""
    return f"""
【智能体快捷方式创建指南】🚀

智能体名称：{name}
访问链接：{url}

请选择您的设备类型：

📱 手机用户
----------------------------------

【iPhone / iPad】
1. 在Safari浏览器中打开智能体
2. 点击分享按钮 → "添加到主屏幕"
3. 一键点击即可进入对话界面

【安卓手机】
1. 在Chrome浏览器中打开智能体
2. 点击菜单（三个点）→ "添加到主屏幕"
3. 一键点击即可进入对话界面

💡 手机用户推荐：
添加到主屏幕后，体验接近原生应用，
无需每次都找链接或扫码。

💻 电脑用户
----------------------------------

【Windows电脑】
1. 在桌面右键 → "新建" → "快捷方式"
2. 粘贴链接，命名为：{name}
3. 双击快捷方式即可打开

【Mac电脑】
1. 在Safari中打开智能体
2. 拖拽地址栏图标到Dock栏
3. 一键点击即可打开

【Linux电脑】
1. 创建.desktop文件
2. 保存到桌面
3. 赋予执行权限

💡 电脑用户推荐：
将智能体固定到任务栏或Dock栏，
随时访问，非常方便。

📝 快速开始
----------------------------------
如果您不确定如何操作，
请使用以下命令获取针对您设备的详细指南：

```
create_shortcut_guide(
    agent_url="{url}",
    agent_name="{name}",
    device_type="您的设备类型"
)
```

支持的设备类型：
- iphone / ios
- android
- windows
- mac / macos
- linux

💡 小提示
----------------------------------
1. 首次创建快捷方式后，就无需再扫码或找链接了
2. 一键直达，体验流畅
3. 可以分享给朋友，让他们也创建快捷方式

🎉 开始使用吧！
"""


# 导出所有工具
__all__ = [
    'create_shortcut_guide',
    'create_desktop_shortcut_file',
    'generate_qr_code_info',
]

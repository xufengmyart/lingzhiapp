#!/usr/bin/env python3
"""
将媄月API集成到app.py中
"""

import os

# 读取app.py文件
with open('app.py', 'r', encoding='utf-8') as f:
    app_content = f.read()

# 检查是否已经集成了媄月API
if 'from meiyue_apis import register_meiyue_apis' in app_content:
    print("⚠️  媄月API已经集成，跳过")
else:
    # 在文件末尾添加集成代码
    integration_code = '''

# ==================== 媄月商业艺术系统 API ====================
try:
    from meiyue_apis import register_meiyue_apis
    register_meiyue_apis(app)
    print("✅ 媄月商业艺术系统API已注册")
except ImportError as e:
    print(f"⚠️  媄月API模块导入失败: {e}")
'''

    with open('app.py', 'a', encoding='utf-8') as f:
        f.write(integration_code)

    print("✅ 媄月API集成代码已添加到app.py")

print("\n现在请重启Flask应用以使更改生效")

#!/usr/bin/env python3
"""
应用改进的登录/注册API到scripts/app.py
"""

import re

# 读取改进的API代码
with open('/tmp/improved_api.txt', 'r') as f:
    improved_code = f.read()

# 读取app.py
with open('scripts/app.py', 'r') as f:
    app_content = f.read()

# 查找并替换login函数（从@app.route('/api/login', methods=['POST'])开始，到下一个@app.route结束）
login_pattern = r"@app\.route\('/api/login', methods=\['POST'\]\).*?(?=\n@app\.route|\n\n# ============|\Z)"
login_match = re.search(login_pattern, app_content, re.DOTALL)

if login_match:
    old_login = login_match.group(0)
    # 提取新的login函数
    new_login_pattern = r"@app\.route\('/api/login', methods=\['POST'\]\).*?(?=\n@app\.route|\n\n# ============)"
    new_login_match = re.search(new_login_pattern, improved_code, re.DOTALL)
    if new_login_match:
        new_login = new_login_match.group(0)
        app_content = app_content.replace(old_login, new_login)
        print("✓ login函数已替换")
    else:
        print("✗ 未找到新的login函数")
else:
    print("✗ 未找到旧的login函数")

# 查找并替换register函数
register_pattern = r"@app\.route\('/api/register', methods=\['POST'\]\).*?(?=\n@app\.route|\n\n# ============|\Z)"
register_match = re.search(register_pattern, app_content, re.DOTALL)

if register_match:
    old_register = register_match.group(0)
    # 提取新的register函数
    new_register_pattern = r"@app\.route\('/api/register', methods=\['POST'\]\).*?(?=\n@app\.route|\n\n# ============)"
    new_register_match = re.search(new_register_pattern, improved_code, re.DOTALL)
    if new_register_match:
        new_register = new_register_match.group(0)
        app_content = app_content.replace(old_register, new_register)
        print("✓ register函数已替换")
    else:
        print("✗ 未找到新的register函数")
else:
    print("✗ 未找到旧的register函数")

# 检查是否需要添加wechat_login和check_user_exists函数
if '@app.route(\'/api/wechat/login\'' not in app_content:
    # 提取wechat_login函数
    wechat_pattern = r"@app\.route\('/api/wechat/login'.*?(?=\n@app\.route|\n\n# ============|\Z)"
    wechat_match = re.search(wechat_pattern, improved_code, re.DOTALL)
    if wechat_match:
        new_wechat = wechat_match.group(0)
        # 在login函数后面添加
        app_content = app_content.replace(new_login, new_login + '\n\n' + new_wechat)
        print("✓ wechat_login函数已添加")

if '@app.route(\'/api/user/check-exists\'' not in app_content:
    # 提取check_user_exists函数
    check_pattern = r"@app\.route\('/api/user/check-exists'.*?(?=\n@app\.route|\n\n# ============|\Z)"
    check_match = re.search(check_pattern, improved_code, re.DOTALL)
    if check_match:
        new_check = check_match.group(0)
        # 在wechat_login函数后面添加
        app_content = app_content + '\n\n' + new_check
        print("✓ check_user_exists函数已添加")

# 写回app.py
with open('scripts/app.py', 'w') as f:
    f.write(app_content)

print("\n✓ API代码应用完成")

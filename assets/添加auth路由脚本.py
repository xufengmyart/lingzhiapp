# 在服务器上执行此脚本添加auth路由
import sqlite3

# 读取文件
with open('/var/www/backend/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 检查是否已有auth路由
if "@app.route('/api/auth/login', methods=['POST'])" not in content:
    # 准备路由代码
    routes_code = '''

# ====== 兼容性路由 (解决前端调用路径问题) ======

@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    """兼容性路由 - 与/api/login相同的功能"""
    return login()

@app.route('/api/auth/register', methods=['POST'])
def auth_register():
    """兼容性路由 - 与/api/register相同的功能"""
    return register()

# ====== 兼容性路由结束 ======
'''

    # 在app.run()之前插入
    lines = content.split('\n')
    insert_pos = None
    for i, line in enumerate(lines):
        if 'app.run(host=' in line:
            insert_pos = i
            break

    if insert_pos:
        lines.insert(insert_pos, routes_code)
        new_content = '\n'.join(lines)

        # 写回文件
        with open('/var/www/backend/app.py', 'w', encoding='utf-8') as f:
            f.write(new_content)

        print("✅ 兼容性路由已添加到文件")
    else:
        print("❌ 未找到app.run()位置")
else:
    print("路由已存在，跳过")

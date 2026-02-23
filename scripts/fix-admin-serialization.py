#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
灵值生态园 - 修复后台管理接口的序列化问题
用途：修复用户列表等接口的Row对象序列化问题
作者：Coze Coding
版本：v1.0
日期：2026-02-11
"""

import sqlite3

def row_to_dict(row):
    """将Row对象转换为字典"""
    if row is None:
        return None
    return dict(row)

def fix_admin_users_endpoint():
    """修复admin_get_users接口"""
    # 读取文件
    with open('admin-backend/app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 查找并替换用户列表返回部分
    # 原代码：
    # return jsonify({
    #     'success': True,
    #     'data': {
    #         'users': users,
    #         ...
    #     }
    # })
    
    # 替换为：
    # return jsonify({
    #     'success': True,
    #     'data': {
    #         'users': [dict(row) for row in users],
    #         ...
    #     }
    # })
    
    old_code = "return jsonify({\n            'success': True,\n            'data': {\n                'users': users,\n                'total': total,\n                'page': page,\n                'limit': limit,\n                'totalPages': (total + limit - 1) // limit\n            }\n        })"
    
    new_code = "return jsonify({\n            'success': True,\n            'data': {\n                'users': [dict(row) for row in users],\n                'total': total,\n                'page': page,\n                'limit': limit,\n                'totalPages': (total + limit - 1) // limit\n            }\n        })"
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        print('✅ 已修复 admin_get_users 接口')
    else:
        print('⚠️  未找到需要修复的 admin_get_users 接口代码')
    
    # 写回文件
    with open('admin-backend/app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print('✅ 修复完成')

if __name__ == '__main__':
    fix_admin_users_endpoint()

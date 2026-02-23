# 用户信息功能问题诊断和修复方案

## 检查结果汇总

### ✓ 正常功能
1. 用户注册功能 - 正常工作
2. 用户登录功能 - 正常工作
3. 用户信息获取功能 - 正常工作
4. 用户信息更新功能 - 基本正常

### ⚠️ 发现的问题

#### 1. 用户信息API不一致
**问题描述**：
- `/api/user/info` 返回完整用户信息（包括totalLingzhi、created_at、updated_at等）
- `/api/user/profile` 返回简化的用户信息（只有username、email、phone、avatar_url等）
- 两个API返回的字段不一致，导致前端获取用户信息时可能丢失数据

**影响**：
- 前端在AuthContext中使用`/api/user/info`获取用户信息
- 但在某些页面可能使用`/api/user/profile`，导致字段不一致

**修复方案**：
统一用户信息API，确保所有API返回完整的用户信息字段。

#### 2. 用户头像上传功能缺失
**问题描述**：
- 后端没有头像上传API
- 前端没有头像上传UI
- 用户无法更新头像

**影响**：
- 用户无法个性化设置头像
- 头像URL始终为null

**修复方案**：
添加头像上传API和前端UI组件。

#### 3. 用户信息更新功能不完整
**问题描述**：
- PUT `/api/user/profile` 只能更新username、email、phone
- 不能更新real_name、address等其他字段
- 用户完善信息的字段无法通过此API更新

**影响**：
- 用户完善信息后，无法再次修改某些字段
- 用户体验不佳

**修复方案**：
扩展用户信息更新API，支持更新所有用户信息字段。

#### 4. 用户profile信息与用户信息分离
**问题描述**：
- 用户基本信息存储在`users`表
- 用户详细信息存储在`user_profiles`表
- 两个表的字段可能不一致

**影响**：
- 数据管理复杂
- 可能出现数据不一致

**修复方案**：
确保两个表的数据同步，简化数据管理。

## 修复实施

### 修复1: 统一用户信息API

#### 后端修改 (app.py)

修改`/api/user/profile` GET接口，确保返回完整的用户信息：

```python
@app.route('/api/user/profile', methods=['GET'])
def get_user_profile():
    """获取用户详细信息"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)

        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        conn = get_db()
        cursor = conn.cursor()

        # 获取完整的用户信息（包括所有字段）
        cursor.execute("""
            SELECT id, username, email, phone, avatar_url, real_name, wechat_nickname, wechat_avatar,
                   totalLingzhi, is_verified, login_type, created_at, updated_at
            FROM users WHERE id = ?
        """, (user_id,))
        user = cursor.fetchone()

        # 获取用户详细信息
        cursor.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,))
        profile = cursor.fetchone()

        conn.close()

        # 合并用户信息
        if profile:
            user_data = dict(user) if user else {}
            profile_data = dict(profile) if profile else {}
            # 不重复的字段
            for key in profile_data:
                if key not in user_data:
                    user_data[key] = profile_data[key]

        return jsonify({
            'success': True,
            'data': {
                'user': user_data,
                'profile': dict(profile) if profile else None,
                'is_completed': profile['is_completed'] if profile else False
            }
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'获取用户信息失败: {str(e)}'}), 500
```

### 修复2: 添加头像上传API

#### 后端修改 (app.py)

添加头像上传接口：

```python
@app.route('/api/user/avatar', methods=['POST'])
def upload_avatar():
    """上传用户头像"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)

        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        # 检查是否有上传的文件
        if 'avatar' not in request.files:
            return jsonify({'success': False, 'message': '未上传文件'}), 400

        file = request.files['avatar']
        if file.filename == '':
            return jsonify({'success': False, 'message': '未选择文件'}), 400

        # 验证文件类型
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'success': False, 'message': '不支持的文件类型'}), 400

        # 生成文件名
        import os
        import uuid
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"avatar_{user_id}_{uuid.uuid4().hex}.{ext}"
        upload_path = os.path.join('static', 'avatars', filename)

        # 确保目录存在
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)

        # 保存文件
        file.save(upload_path)

        # 更新用户头像URL
        avatar_url = f"/static/avatars/{filename}"
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET avatar_url = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                      (avatar_url, user_id))
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '头像上传成功',
            'data': {'avatar_url': avatar_url}
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'头像上传失败: {str(e)}'}), 500
```

#### 前端修改

创建头像上传组件（如果需要）。

### 修复3: 扩展用户信息更新API

#### 后端修改 (app.py)

修改PUT `/api/user/profile`接口，支持更新更多字段：

```python
@app.route('/api/user/profile', methods=['PUT'])
def update_user_profile():
    """更新用户基本信息"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)

        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        data = request.json
        username = data.get('username')
        email = data.get('email')
        phone = data.get('phone')
        real_name = data.get('real_name')
        address = data.get('address')

        if not any([username, email, phone, real_name, address]):
            return jsonify({'success': False, 'message': '至少需要更新一个字段'}), 400

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT username, email, phone, real_name FROM users WHERE id = ?", (user_id,))
        current_user = cursor.fetchone()

        if not current_user:
            conn.close()
            return jsonify({'success': False, 'message': '用户不存在'}), 404

        # 验证唯一性
        if username and username != current_user['username']:
            cursor.execute("SELECT id FROM users WHERE username = ? AND id != ?", (username, user_id))
            if cursor.fetchone():
                conn.close()
                return jsonify({'success': False, 'message': '用户名已被使用'}), 400

        if email and email != current_user['email']:
            cursor.execute("SELECT id FROM users WHERE email = ? AND id != ?", (email, user_id))
            if cursor.fetchone():
                conn.close()
                return jsonify({'success': False, 'message': '邮箱已被使用'}), 400

        if phone and phone != current_user['phone']:
            cursor.execute("SELECT id FROM users WHERE phone = ? AND id != ?", (phone, user_id))
            if cursor.fetchone():
                conn.close()
                return jsonify({'success': False, 'message': '手机号已被使用'}), 400

        # 更新字段
        update_fields = []
        update_values = []

        if username:
            update_fields.append("username = ?")
            update_values.append(username)
        if email is not None:
            update_fields.append("email = ?")
            update_values.append(email)
        if phone is not None:
            update_fields.append("phone = ?")
            update_values.append(phone)
        if real_name:
            update_fields.append("real_name = ?")
            update_values.append(real_name)
        if address:
            update_fields.append("address = ?")
            update_values.append(address)

        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        update_values.append(user_id)

        update_sql = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(update_sql, update_values)

        conn.commit()

        # 获取更新后的用户数据
        cursor.execute("""
            SELECT id, username, email, phone, avatar_url, real_name, wechat_nickname, wechat_avatar,
                   totalLingzhi, is_verified, login_type, created_at, updated_at
            FROM users WHERE id = ?
        """, (user_id,))
        updated_user = cursor.fetchone()

        conn.close()

        return jsonify({
            'success': True,
            'message': '用户信息更新成功',
            'data': format_user_data(updated_user)
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'更新用户信息失败: {str(e)}'}), 500
```

## 优先级

### 高优先级
1. **统一用户信息API** - 确保数据一致性
2. **扩展用户信息更新API** - 改善用户体验

### 中优先级
3. **添加头像上传功能** - 增强个性化体验

### 低优先级
4. **优化数据结构** - 简化数据管理

## 测试计划

修复完成后，需要测试以下场景：

1. 用户注册后获取信息
2. 用户登录后获取信息
3. 用户更新基本信息
4. 用户更新详细资料
5. 用户上传头像
6. 数据一致性验证

## 注意事项

1. 所有修改需要保持向后兼容
2. 确保数据库字段存在
3. 添加适当的错误处理
4. 验证用户权限
5. 记录操作日志

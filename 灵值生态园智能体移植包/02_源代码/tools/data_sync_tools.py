"""
数据同步工具
提供用户数据的批量导入、导出和同步功能
"""
import json
import csv
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from langchain.tools import tool, ToolRuntime
from sqlalchemy.orm import Session

from storage.database.shared.model import Users, Roles
from coze_coding_dev_sdk.database import get_session


@tool
def export_users_to_csv(runtime: ToolRuntime, output_file: str = "assets/users_export.csv", status_filter: Optional[str] = None) -> str:
    """
    导出用户数据到CSV文件
    
    Args:
        output_file: 输出文件路径，默认为 assets/users_export.csv
        status_filter: 可选的状态过滤条件，如 'active', 'inactive', 'locked'
    
    Returns:
        导出结果信息
    """
    db = get_session()
    try:
        query = db.query(Users)
        
        if status_filter:
            query = query.filter(Users.status == status_filter)
        
        users = query.all()
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            
            # 写入表头
            writer.writerow([
                'id', 'name', 'email', 'status', 'is_superuser', 'is_ceo',
                'two_factor_enabled', 'phone', 'wechat', 'department', 'position',
                'created_at', 'last_login'
            ])
            
            # 写入数据
            for user in users:
                writer.writerow([
                    user.id,
                    user.name,
                    user.email,
                    user.status,
                    user.is_superuser,
                    user.is_ceo,
                    user.two_factor_enabled,
                    user.phone or '',
                    user.wechat or '',
                    user.department or '',
                    user.position or '',
                    user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else '',
                    user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else ''
                ])
        
        return f"✅ 成功导出 {len(users)} 条用户数据到 {output_file}"
    
    except Exception as e:
        return f"❌ 导出失败: {str(e)}"
    finally:
        db.close()


@tool
def import_users_from_csv(runtime: ToolRuntime, input_file: str, is_test_data: bool = False, update_existing: bool = False) -> str:
    """
    从CSV文件导入用户数据
    
    Args:
        input_file: 输入CSV文件路径
        is_test_data: 是否标记为测试数据（如果是，会在name前添加[测试]标记）
        update_existing: 是否更新已存在的用户（根据email匹配）
    
    Returns:
        导入结果信息
    """
    db = get_session()
    try:
        if not os.path.exists(input_file):
            return f"❌ 文件不存在: {input_file}"
        
        imported_count = 0
        updated_count = 0
        skipped_count = 0
        
        with open(input_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                email = row.get('email', '').strip()
                if not email:
                    skipped_count += 1
                    continue
                
                # 检查用户是否已存在
                existing_user = db.query(Users).filter(Users.email == email).first()
                
                if existing_user:
                    if update_existing:
                        # 更新现有用户
                        existing_user.name = row.get('name', existing_user.name)
                        existing_user.phone = row.get('phone') or existing_user.phone
                        existing_user.wechat = row.get('wechat') or existing_user.wechat
                        existing_user.department = row.get('department') or existing_user.department
                        existing_user.position = row.get('position') or existing_user.position
                        updated_count += 1
                    else:
                        skipped_count += 1
                        continue
                else:
                    # 创建新用户
                    import hashlib
                    default_password = "123456"  # 默认密码
                    
                    # 标记测试数据
                    name = row.get('name', '').strip()
                    if is_test_data:
                        name = f"[测试] {name}"
                    
                    # 创建密码哈希
                    password_hash = hashlib.sha256(default_password.encode()).hexdigest()
                    
                    user = Users(
                        name=name,
                        email=email,
                        password_hash=password_hash,
                        status='inactive' if is_test_data else 'active',
                        is_superuser=False,
                        is_ceo=False,
                        two_factor_enabled=False,
                        phone=row.get('phone') or None,
                        wechat=row.get('wechat') or None,
                        department=row.get('department') or None,
                        position=row.get('position') or None
                    )
                    
                    db.add(user)
                    imported_count += 1
        
        db.commit()
        
        result = f"✅ 导入完成:\n"
        result += f"  - 新增用户: {imported_count} 条\n"
        result += f"  - 更新用户: {updated_count} 条\n"
        result += f"  - 跳过用户: {skipped_count} 条"
        
        if is_test_data:
            result += f"\n\n💡 提示: 测试数据已标记，所有测试用户的name都带有'[测试]'前缀，默认状态为'inactive'，默认密码为'123456'"
        
        return result
    
    except Exception as e:
        db.rollback()
        return f"❌ 导入失败: {str(e)}"
    finally:
        db.close()


@tool
def export_users_to_json(runtime: ToolRuntime, output_file: str = "assets/users_export.json", status_filter: Optional[str] = None) -> str:
    """
    导出用户数据到JSON文件
    
    Args:
        output_file: 输出文件路径，默认为 assets/users_export.json
        status_filter: 可选的状态过滤条件
    
    Returns:
        导出结果信息
    """
    db = get_session()
    try:
        query = db.query(Users)
        
        if status_filter:
            query = query.filter(Users.status == status_filter)
        
        users = query.all()
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        data = []
        for user in users:
            user_data = {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'status': user.status,
                'is_superuser': user.is_superuser,
                'is_ceo': user.is_ceo,
                'two_factor_enabled': user.two_factor_enabled,
                'phone': user.phone,
                'wechat': user.wechat,
                'department': user.department,
                'position': user.position,
                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else None,
                'last_login': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else None
            }
            data.append(user_data)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return f"✅ 成功导出 {len(users)} 条用户数据到 {output_file}"
    
    except Exception as e:
        return f"❌ 导出失败: {str(e)}"
    finally:
        db.close()


@tool
def import_users_from_json(runtime: ToolRuntime, input_file: str, is_test_data: bool = False, update_existing: bool = False) -> str:
    """
    从JSON文件导入用户数据
    
    Args:
        input_file: 输入JSON文件路径
        is_test_data: 是否标记为测试数据
        update_existing: 是否更新已存在的用户
    
    Returns:
        导入结果信息
    """
    db = get_session()
    try:
        if not os.path.exists(input_file):
            return f"❌ 文件不存在: {input_file}"
        
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        imported_count = 0
        updated_count = 0
        skipped_count = 0
        
        for row in data:
            email = row.get('email', '').strip()
            if not email:
                skipped_count += 1
                continue
            
            # 检查用户是否已存在
            existing_user = db.query(Users).filter(Users.email == email).first()
            
            if existing_user:
                if update_existing:
                    existing_user.name = row.get('name', existing_user.name)
                    existing_user.phone = row.get('phone') or existing_user.phone
                    existing_user.wechat = row.get('wechat') or existing_user.wechat
                    existing_user.department = row.get('department') or existing_user.department
                    existing_user.position = row.get('position') or existing_user.position
                    updated_count += 1
                else:
                    skipped_count += 1
                    continue
            else:
                # 创建新用户
                import hashlib
                default_password = "123456"
                password_hash = hashlib.sha256(default_password.encode()).hexdigest()
                
                name = row.get('name', '').strip()
                if is_test_data:
                    name = f"[测试] {name}"
                
                user = Users(
                    name=name,
                    email=email,
                    password_hash=password_hash,
                    status='inactive' if is_test_data else 'active',
                    is_superuser=False,
                    is_ceo=False,
                    two_factor_enabled=False,
                    phone=row.get('phone') or None,
                    wechat=row.get('wechat') or None,
                    department=row.get('department') or None,
                    position=row.get('position') or None
                )
                
                db.add(user)
                imported_count += 1
        
        db.commit()
        
        result = f"✅ 导入完成:\n"
        result += f"  - 新增用户: {imported_count} 条\n"
        result += f"  - 更新用户: {updated_count} 条\n"
        result += f"  - 跳过用户: {skipped_count} 条"
        
        if is_test_data:
            result += f"\n\n💡 提示: 测试数据已标记，默认密码为'123456'"
        
        return result
    
    except Exception as e:
        db.rollback()
        return f"❌ 导入失败: {str(e)}"
    finally:
        db.close()


@tool
def create_test_users(runtime: ToolRuntime, count: int = 5, department: str = "测试部门", position: str = "测试员工") -> str:
    """
    批量创建测试用户数据
    
    Args:
        count: 要创建的测试用户数量
        department: 部门名称
        position: 职位名称
    
    Returns:
        创建结果信息
    """
    db = get_session()
    try:
        import hashlib
        created_count = 0
        
        for i in range(1, count + 1):
            # 生成测试邮箱
            email = f"test_user_{i}@test.meiyueart.cn"
            
            # 检查邮箱是否已存在
            existing_user = db.query(Users).filter(Users.email == email).first()
            if existing_user:
                continue
            
            # 创建密码哈希
            password_hash = hashlib.sha256("123456".encode()).hexdigest()
            
            user = Users(
                name=f"[测试] 员工{i}",
                email=email,
                password_hash=password_hash,
                status='inactive',  # 测试用户默认为inactive
                is_superuser=False,
                is_ceo=False,
                two_factor_enabled=False,
                phone=f"1380013800{i:02d}",
                department=department,
                position=position
            )
            
            db.add(user)
            created_count += 1
        
        db.commit()
        
        return f"✅ 成功创建 {created_count} 个测试用户\n\n💡 提示:\n  - 测试用户密码统一为: 123456\n  - 测试用户状态为: inactive\n  - 邮箱格式: test_user_1@test.meiyueart.cn"
    
    except Exception as e:
        db.rollback()
        return f"❌ 创建失败: {str(e)}"
    finally:
        db.close()


@tool
def delete_test_users(runtime: ToolRuntime, confirm: bool = False) -> str:
    """
    删除所有测试用户（name包含'[测试]'标记的用户）
    
    Args:
        confirm: 是否确认删除，必须设置为True才会执行删除
    
    Returns:
        删除结果信息
    """
    if not confirm:
        return "⚠️ 警告: 此操作将删除所有测试用户（name包含'[测试]'的用户）。\n\n请再次调用此工具并设置 confirm=True 以确认删除。"
    
    db = get_session()
    try:
        # 查找所有测试用户
        test_users = db.query(Users).filter(Users.name.like('[测试]%')).all()
        
        deleted_count = len(test_users)
        
        for user in test_users:
            db.delete(user)
        
        db.commit()
        
        return f"✅ 成功删除 {deleted_count} 个测试用户"
    
    except Exception as e:
        db.rollback()
        return f"❌ 删除失败: {str(e)}"
    finally:
        db.close()


@tool
def get_data_sync_guide(runtime: ToolRuntime) -> str:
    """
    获取数据同步使用指南
    
    Returns:
        数据同步工具使用说明
    """
    guide = """
# 数据同步工具使用指南

## 📋 可用功能

### 1. 导出用户数据

#### 导出为CSV
```
使用: export_users_to_csv
参数:
  - output_file: 输出文件路径（默认: assets/users_export.csv）
  - status_filter: 可选的状态过滤（如 'active', 'inactive', 'locked'）
```

#### 导出为JSON
```
使用: export_users_to_json
参数:
  - output_file: 输出文件路径（默认: assets/users_export.json）
  - status_filter: 可选的状态过滤
```

### 2. 导入用户数据

#### 从CSV导入
```
使用: import_users_from_csv
参数:
  - input_file: 输入CSV文件路径
  - is_test_data: 是否标记为测试数据（默认: false）
  - update_existing: 是否更新已存在用户（默认: false）
```

#### 从JSON导入
```
使用: import_users_from_json
参数:
  - input_file: 输入JSON文件路径
  - is_test_data: 是否标记为测试数据（默认: false）
  - update_existing: 是否更新已存在用户（默认: false）
```

### 3. 批量创建测试用户
```
使用: create_test_users
参数:
  - count: 创建数量（默认: 5）
  - department: 部门名称（默认: "测试部门"）
  - position: 职位名称（默认: "测试员工"）
```

### 4. 删除测试用户
```
使用: delete_test_users
参数:
  - confirm: 是否确认删除（必须设置为True才会执行）
```

## 💡 使用场景

### 场景1: 从测试环境同步数据到生产环境
1. 在测试环境导出数据: `export_users_to_csv`
2. 在生产环境导入数据: `import_users_from_csv`

### 场景2: 创建测试数据用于开发
1. 创建测试用户: `create_test_users(count=10)`
2. 测试完成后清理: `delete_test_users(confirm=True)`

### 场景3: 备份和恢复
1. 导出现有数据: `export_users_to_json`
2. 需要时恢复: `import_users_from_json`

## ⚠️ 注意事项

1. **测试数据标记**: 使用 `is_test_data=true` 导入时，会在用户名前添加 '[测试]' 标记，状态设为 'inactive'
2. **默认密码**: 测试用户默认密码为 '123456'
3. **数据安全**: 删除测试用户需要二次确认
4. **邮箱唯一性**: 同一邮箱不会重复导入，除非设置 `update_existing=true`
5. **生产环境**: 谨慎在生产环境创建测试数据

## 📊 CSV文件格式示例

```csv
id,name,email,status,is_superuser,is_ceo,phone,wechat,department,position
1,张三,zhangsan@example.com,active,false,false,13800138000,zhangsan,技术部,工程师
2,李四,lisi@example.com,active,false,false,13800138001,lisi,市场部,经理
```

## 📄 JSON文件格式示例

```json
[
  {
    "name": "张三",
    "email": "zhangsan@example.com",
    "phone": "13800138000",
    "wechat": "zhangsan",
    "department": "技术部",
    "position": "工程师"
  },
  {
    "name": "李四",
    "email": "lisi@example.com",
    "phone": "13800138001",
    "wechat": "lisi",
    "department": "市场部",
    "position": "经理"
  }
]
```
"""
    return guide

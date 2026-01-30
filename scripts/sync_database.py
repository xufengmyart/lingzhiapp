"""
同步数据库模型文件到移植包
"""

import os
import shutil
import hashlib


def sync_database_model():
    """同步数据库模型文件"""
    
    print("="*70)
    print("数据库模型文件同步")
    print("="*70)
    print()
    
    source_file = "src/storage/database/shared/model.py"
    target_file = "灵值生态园智能体移植包/02_源代码/storage/database/shared/model.py"
    
    # 确保目标目录存在
    target_dir = os.path.dirname(target_file)
    os.makedirs(target_dir, exist_ok=True)
    
    try:
        # 读取源文件
        with open(source_file, 'rb') as f:
            source_content = f.read()
        
        # 写入目标文件
        with open(target_file, 'wb') as f:
            f.write(source_content)
        
        # 计算哈希值
        source_hash = hashlib.md5(source_content).hexdigest()
        
        print(f"✅ 数据库模型文件同步成功")
        print(f"   源文件: {source_file}")
        print(f"   目标文件: {target_file}")
        print(f"   MD5: {source_hash}")
        print()
        
        # 验证coze_id字段
        content = source_content.decode('utf-8')
        if 'coze_id' in content and '扣子平台注册ID' in content:
            print("✅ coze_id字段验证通过: 已添加扣子平台注册ID字段")
        else:
            print("⚠️  coze_id字段未找到")
        
        print()
        print("="*70)
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库模型文件同步失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def sync_super_admin_manager():
    """同步超级管理员管理器文件"""
    
    print()
    print("="*70)
    print("超级管理员管理器文件同步")
    print("="*70)
    print()
    
    source_file = "src/storage/database/super_admin_manager.py"
    target_file = "灵值生态园智能体移植包/02_源代码/storage/database/super_admin_manager.py"
    
    # 确保目标目录存在
    target_dir = os.path.dirname(target_file)
    os.makedirs(target_dir, exist_ok=True)
    
    try:
        # 读取源文件
        with open(source_file, 'rb') as f:
            source_content = f.read()
        
        # 写入目标文件
        with open(target_file, 'wb') as f:
            f.write(source_content)
        
        # 计算哈希值
        source_hash = hashlib.md5(source_content).hexdigest()
        
        print(f"✅ 超级管理员管理器文件同步成功")
        print(f"   源文件: {source_file}")
        print(f"   目标文件: {target_file}")
        print(f"   MD5: {source_hash}")
        print()
        print("="*70)
        
        return True
        
    except Exception as e:
        print(f"❌ 超级管理员管理器文件同步失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success1 = sync_database_model()
    success2 = sync_super_admin_manager()
    
    exit(0 if (success1 and success2) else 1)

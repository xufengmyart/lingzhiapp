"""
同步配置文件到移植包
"""

import os
import shutil
import hashlib


def sync_config_file():
    """同步配置文件"""
    
    print("="*70)
    print("配置文件同步")
    print("="*70)
    print()
    
    source_file = "src/config/super_admin_config.py"
    target_file = "灵值生态园智能体移植包/02_源代码/config/super_admin_config.py"
    
    try:
        # 读取源文件
        with open(source_file, 'rb') as f:
            source_content = f.read()
        
        # 写入目标文件
        with open(target_file, 'wb') as f:
            f.write(source_content)
        
        # 计算哈希值
        source_hash = hashlib.md5(source_content).hexdigest()
        
        print(f"✅ 配置文件同步成功")
        print(f"   源文件: {source_file}")
        print(f"   目标文件: {target_file}")
        print(f"   MD5: {source_hash}")
        print()
        
        # 验证邮箱配置
        content = source_content.decode('utf-8')
        if 'xufeng@meiyueart.cn' in content:
            print("✅ 邮箱配置验证通过: xufeng@meiyueart.cn")
        else:
            print("⚠️  邮箱配置未找到")
        
        print()
        print("="*70)
        
        return True
        
    except Exception as e:
        print(f"❌ 配置文件同步失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = sync_config_file()
    exit(0 if success else 1)

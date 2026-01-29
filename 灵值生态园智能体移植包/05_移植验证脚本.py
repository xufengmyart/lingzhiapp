"""
灵值生态园智能体移植验证脚本
版本：v5.1
更新日期：2026年1月25日
"""

import os
import json
import sys
import sqlite3
from pathlib import Path
from datetime import datetime


class MigrationPackageValidator:
    """移植包验证器"""
    
    def __init__(self, root_dir="."):
        """初始化验证器
        
        Args:
            root_dir: 移植包根目录
        """
        self.root_dir = Path(root_dir)
        self.check_results = []
    
    def check_file_exists(self, file_path, description):
        """检查文件是否存在
        
        Args:
            file_path: 文件路径
            description: 文件描述
        
        Returns:
            bool: 文件是否存在
        """
        full_path = self.root_dir / file_path
        exists = full_path.exists()
        
        status = "✅" if exists else "❌"
        result = f"{status} {description}: {file_path}"
        self.check_results.append(result)
        
        if not exists:
            print(result)
        
        return exists
    
    def check_json_valid(self, file_path, description):
        """检查JSON文件是否有效
        
        Args:
            file_path: JSON文件路径
            description: 文件描述
        
        Returns:
            bool: JSON文件是否有效
        """
        full_path = self.root_dir / file_path
        
        if not full_path.exists():
            self.check_results.append(f"❌ {description}: 文件不存在")
            return False
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                json.load(f)
            
            self.check_results.append(f"✅ {description}: {file_path}")
            return True
        except Exception as e:
            self.check_results.append(f"❌ {description}: JSON解析失败 - {str(e)}")
            return False
    
    def check_config_keys(self, file_path, required_keys, description):
        """检查配置文件是否包含必需的键
        
        Args:
            file_path: 配置文件路径
            required_keys: 必需的键列表
            description: 文件描述
        
        Returns:
            bool: 配置文件是否包含所有必需的键
        """
        full_path = self.root_dir / file_path
        
        if not full_path.exists():
            self.check_results.append(f"❌ {description}: 文件不存在")
            return False
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            missing_keys = [key for key in required_keys if key not in data]
            
            if missing_keys:
                self.check_results.append(f"❌ {description}: 缺少必需的键 - {', '.join(missing_keys)}")
                return False
            else:
                self.check_results.append(f"✅ {description}: {file_path}")
                return True
        except Exception as e:
            self.check_results.append(f"❌ {description}: 配置解析失败 - {str(e)}")
            return False
    
    def check_database(self, db_path="src/auth/auth.db"):
        """检查数据库
        
        Args:
            db_path: 数据库文件路径
        
        Returns:
            bool: 数据库是否有效
        """
        full_path = self.root_dir / db_path
        
        if not full_path.exists():
            self.check_results.append(f"❌ 数据库文件不存在: {db_path}")
            return False
        
        try:
            conn = sqlite3.connect(full_path)
            cursor = conn.cursor()
            
            # 检查表数量
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]
            
            # 检查用户数量
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            # 检查角色数量
            cursor.execute("SELECT COUNT(*) FROM roles")
            role_count = cursor.fetchone()[0]
            
            # 检查权限数量
            cursor.execute("SELECT COUNT(*) FROM permissions")
            perm_count = cursor.fetchone()[0]
            
            # 检查专家数量
            cursor.execute("SELECT COUNT(*) FROM experts")
            expert_count = cursor.fetchone()[0]
            
            conn.close()
            
            # 验证数据库内容
            if table_count >= 20 and user_count >= 1 and role_count >= 5:
                self.check_results.append(f"✅ 数据库验证通过")
                self.check_results.append(f"   - 文件大小: {full_path.stat().st_size / 1024:.2f} KB")
                self.check_results.append(f"   - 表数量: {table_count}")
                self.check_results.append(f"   - 用户数: {user_count}")
                self.check_results.append(f"   - 角色数: {role_count}")
                self.check_results.append(f"   - 权限数: {perm_count}")
                self.check_results.append(f"   - 资源库专家数: {expert_count}")
                return True
            else:
                self.check_results.append(f"❌ 数据库内容不完整")
                return False
                
        except Exception as e:
            self.check_results.append(f"❌ 数据库验证失败: {str(e)}")
            return False
    
    def run_all_checks(self):
        """运行所有检查"""
        print("=" * 80)
        print("灵值生态园智能体 - 移植包验证")
        print(f"版本: v5.1")
        print(f"验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()
        
        # 检查核心文件
        print("1️⃣  检查核心文件...")
        checks = [
            ("README.md", "移植包说明"),
            ("00_移植指南.md", "移植指南"),
            ("00_完整部署指南.md", "完整部署指南"),
            ("04_部署检查清单.md", "部署检查清单"),
            ("05_移植验证脚本.py", "移植验证脚本"),
            ("quick_test.py", "快速测试脚本"),
        ]
        
        for file_path, description in checks:
            self.check_file_exists(file_path, description)
        
        print()
        
        # 检查智能体配置
        print("2️⃣  检查智能体配置...")
        checks = [
            ("01_智能体配置/基本信息.json", "基本信息"),
            ("01_智能体配置/系统提示词.md", "系统提示词"),
            ("01_智能体配置/模型配置.json", "模型配置"),
            ("01_智能体配置/工具配置.md", "工具配置"),
        ]
        
        for file_path, description in checks:
            self.check_file_exists(file_path, description)
        
        print()
        
        # 检查源代码
        print("3️⃣  检查源代码...")
        checks = [
            ("02_源代码/agent.py", "智能体核心代码"),
            ("02_源代码/tools/knowledge_retrieval_tool.py", "知识库检索工具"),
            ("02_源代码/tools/image_generation_tool.py", "图像生成工具"),
            ("02_源代码/tools/web_search_tool.py", "联网搜索工具"),
        ]
        
        for file_path, description in checks:
            self.check_file_exists(file_path, description)
        
        print()
        
        # 检查知识库文档
        print("4️⃣  检查知识库文档...")
        checks = [
            ("03_知识库文档/00_知识库文档索引.md", "知识库文档索引"),
            ("知识库/灵值生态一体化服务总纲.md", "灵值生态一体化服务总纲"),
            ("知识库/贡献值经济价值锚定方案.md", "贡献值经济价值锚定方案"),
            ("知识库/情绪价值体系实施方案.md", "情绪价值体系实施方案"),
            ("知识库/西安文化基因库.md", "西安文化基因库"),
        ]
        
        for file_path, description in checks:
            self.check_file_exists(file_path, description)
        
        print()
        
        # 检查认证系统
        print("5️⃣  检查认证系统...")
        checks = [
            ("src/auth/auth.db", "数据库文件"),
            ("src/auth/database.py", "数据库模型"),
            ("src/auth/auth_service.py", "认证服务"),
            ("src/auth/verify_database.py", "数据库验证工具"),
        ]
        
        for file_path, description in checks:
            self.check_file_exists(file_path, description)
        
        print()
        
        # 检查配置文件
        print("6️⃣  检查配置文件...")
        checks = [
            ("config/agent_llm_config.json", "LLM配置"),
            ("config/02_系统提示词.md", "系统提示词配置"),
        ]
        
        for file_path, description in checks:
            self.check_file_exists(file_path, description)
        
        print()
        
        # 验证JSON文件
        print("7️⃣  验证JSON文件...")
        checks = [
            ("01_智能体配置/基本信息.json", "基本信息"),
            ("01_智能体配置/模型配置.json", "模型配置"),
            ("config/agent_llm_config.json", "LLM配置"),
        ]
        
        for file_path, description in checks:
            self.check_json_valid(file_path, description)
        
        print()
        
        # 验证配置文件
        print("8️⃣  验证配置文件...")
        checks = [
            ("01_智能体配置/基本信息.json", ["name", "description", "tags", "category"], "基本信息"),
            ("01_智能体配置/模型配置.json", ["config", "sp", "tools"], "模型配置"),
            ("config/agent_llm_config.json", ["config", "sp", "tools"], "LLM配置"),
        ]
        
        for file_path, required_keys, description in checks:
            self.check_config_keys(file_path, required_keys, description)
        
        print()
        
        # 验证数据库
        print("9️⃣  验证数据库...")
        self.check_database()
        
        print()
        print("=" * 80)
        
        # 统计结果
        total_checks = len(self.check_results)
        passed_checks = len([r for r in self.check_results if r.startswith("✅")])
        failed_checks = len([r for r in self.check_results if r.startswith("❌")])
        
        print(f"📊 验证结果汇总")
        print(f"   总检查项: {total_checks}")
        print(f"   ✅ 通过: {passed_checks}")
        print(f"   ❌ 失败: {failed_checks}")
        print("=" * 80)
        
        if failed_checks == 0:
            print()
            print("🎉 移植包验证通过！")
            print()
            print("✅ 所有检查项都已通过")
            print("✅ 数据库连接正常")
            print("✅ 配置文件完整")
            print("✅ 智能体代码就绪")
            print()
            print("可以开始部署了！")
            print()
            print("📖 下一步:")
            print("   1. 阅读 00_完整部署指南.md")
            print("   2. 按照指南进行部署")
            print("   3. 运行 python quick_test.py 进行测试")
            print()
            return True
        else:
            print()
            print("⚠️  移植包验证失败！")
            print()
            print("❌ 以下检查项未通过:")
            for result in self.check_results:
                if result.startswith("❌"):
                    print(f"   {result}")
            print()
            return False


def main():
    """主函数"""
    validator = MigrationPackageValidator()
    success = validator.run_all_checks()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

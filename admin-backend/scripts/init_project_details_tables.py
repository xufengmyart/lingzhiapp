"""
初始化项目详情相关数据库表
支持数据资产完整工作流
"""

import sqlite3
import os

def init_tables():
    """创建项目详情相关的数据库表"""
    
    # 数据库路径
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'site.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. 数据化要素表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS data_elements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            element_name VARCHAR(255) NOT NULL,
            element_type VARCHAR(100) NOT NULL,
            description TEXT,
            data_source VARCHAR(500),
            processing_method TEXT,
            status VARCHAR(50) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    """)

    # 2. 资源表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS data_resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            element_id INTEGER NOT NULL,
            resource_name VARCHAR(255) NOT NULL,
            resource_type VARCHAR(100) NOT NULL,
            resource_url VARCHAR(500),
            file_size INTEGER DEFAULT 0,
            metadata TEXT,
            status VARCHAR(50) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY (element_id) REFERENCES data_elements(id) ON DELETE CASCADE
        )
    """)

    # 3. 数据资产表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS data_assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            asset_name VARCHAR(255) NOT NULL,
            asset_type VARCHAR(100) NOT NULL,
            data_value DECIMAL(20, 2) DEFAULT 0,
            estimated_value DECIMAL(20, 2) DEFAULT 0,
            token_address VARCHAR(500),
            token_symbol VARCHAR(50),
            total_supply DECIMAL(20, 2) DEFAULT 0,
            circulating_supply DECIMAL(20, 2) DEFAULT 0,
            current_price DECIMAL(20, 2) DEFAULT 0,
            market_cap DECIMAL(20, 2) DEFAULT 0,
            status VARCHAR(50) DEFAULT 'processing',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    """)

    # 4. 资产权益/确权表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS asset_rights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            asset_id INTEGER NOT NULL,
            rights_type VARCHAR(100) NOT NULL,
            rights_holder VARCHAR(255) NOT NULL,
            rights_value DECIMAL(20, 2) DEFAULT 0,
            certificate_no VARCHAR(255),
            certificate_url VARCHAR(500),
            expiry_date DATE,
            status VARCHAR(50) DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY (asset_id) REFERENCES data_assets(id) ON DELETE CASCADE
        )
    """)

    # 5. 通证化记录表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS asset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            asset_id INTEGER NOT NULL,
            token_address VARCHAR(500) NOT NULL,
            token_symbol VARCHAR(50) NOT NULL,
            total_supply DECIMAL(20, 2) NOT NULL,
            decimals INTEGER DEFAULT 18,
            mint_date TIMESTAMP,
            mint_tx VARCHAR(500),
            contract_type VARCHAR(100) DEFAULT 'ERC721',
            status VARCHAR(50) DEFAULT 'minted',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY (asset_id) REFERENCES data_assets(id) ON DELETE CASCADE
        )
    """)

    # 6. 资产交易记录表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS asset_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            asset_id INTEGER NOT NULL,
            token_address VARCHAR(500),
            transaction_type VARCHAR(50) NOT NULL,
            from_address VARCHAR(500),
            to_address VARCHAR(500) NOT NULL,
            amount DECIMAL(20, 2) NOT NULL,
            price DECIMAL(20, 2) DEFAULT 0,
            total_value DECIMAL(20, 2) DEFAULT 0,
            tx_hash VARCHAR(500),
            block_number INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY (asset_id) REFERENCES data_assets(id) ON DELETE CASCADE
        )
    """)

    # 7. 项目收入统计表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS project_revenue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            total_revenue DECIMAL(20, 2) DEFAULT 0,
            total_transactions INTEGER DEFAULT 0,
            avg_transaction_value DECIMAL(20, 2) DEFAULT 0,
            last_transaction_date TIMESTAMP,
            period VARCHAR(50) DEFAULT 'all',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    """)

    # 创建索引以提高查询性能
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_data_elements_project ON data_elements(project_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_data_resources_project ON data_resources(project_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_data_resources_element ON data_resources(element_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_data_assets_project ON data_assets(project_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_asset_rights_project ON asset_rights(project_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_asset_rights_asset ON asset_rights(asset_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_asset_tokens_project ON asset_tokens(project_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_asset_tokens_asset ON asset_tokens(asset_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_asset_transactions_project ON asset_transactions(project_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_asset_transactions_asset ON asset_transactions(asset_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_project_revenue_project ON project_revenue(project_id)")

    conn.commit()
    conn.close()

    print("✓ 数据库表创建成功！")
    print("已创建的表：")
    print("  - data_elements (数据化要素)")
    print("  - data_resources (资源)")
    print("  - data_assets (数据资产)")
    print("  - asset_rights (资产权益)")
    print("  - asset_tokens (通证化记录)")
    print("  - asset_transactions (交易记录)")
    print("  - project_revenue (项目收入统计)")

if __name__ == '__main__':
    init_tables()

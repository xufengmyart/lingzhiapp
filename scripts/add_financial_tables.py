#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
添加财务管理相关表
执行时间：2026-01-28
"""

import sys
sys.path.insert(0, '/workspace/projects/src')

from coze_coding_dev_sdk.database import get_session
from sqlalchemy import text


def add_financial_tables():
    """添加财务管理相关表"""

    print("=" * 60)
    print("开始添加财务管理相关表")
    print("=" * 60)

    db = get_session()

    try:
        # 1. 创建公司信息表
        print("\n1. 创建公司信息表...")
        try:
            db.execute(text("""
                CREATE TABLE IF NOT EXISTS company_info (
                    id SERIAL PRIMARY KEY,
                    company_name VARCHAR(200) NOT NULL,
                    tax_number VARCHAR(50) NOT NULL,
                    address VARCHAR(500),
                    phone VARCHAR(20),
                    bank_name VARCHAR(200),
                    bank_account VARCHAR(50),
                    status VARCHAR(20) DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """))
            db.commit()
            print("   ✅ 公司信息表创建成功")
        except Exception as e:
            db.rollback()
            print(f"   ⚠️  公司信息表创建失败或已存在: {e}")

        # 2. 创建提现申请表
        print("\n2. 创建提现申请表...")
        try:
            db.execute(text("""
                CREATE TABLE IF NOT EXISTS withdrawal_requests (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    amount DECIMAL(10, 2) NOT NULL,
                    contribution_value INTEGER NOT NULL,
                    payment_method VARCHAR(20) NOT NULL,
                    payment_account VARCHAR(200) NOT NULL,
                    status VARCHAR(20) DEFAULT 'pending',
                    reject_reason TEXT,
                    approved_by INTEGER,
                    approved_at TIMESTAMP,
                    processed_at TIMESTAMP,
                    transaction_id VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (approved_by) REFERENCES users(id)
                )
            """))
            db.commit()
            print("   ✅ 提现申请表创建成功")
        except Exception as e:
            db.rollback()
            print(f"   ⚠️  提现申请表创建失败或已存在: {e}")

        # 3. 创建财务交易记录表
        print("\n3. 创建财务交易记录表...")
        try:
            db.execute(text("""
                CREATE TABLE IF NOT EXISTS financial_transactions (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    type VARCHAR(20) NOT NULL,
                    amount DECIMAL(10, 2) NOT NULL,
                    contribution_value INTEGER,
                    transaction_id VARCHAR(100),
                    status VARCHAR(20) DEFAULT 'success',
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """))
            db.commit()
            print("   ✅ 财务交易记录表创建成功")
        except Exception as e:
            db.rollback()
            print(f"   ⚠️  财务交易记录表创建失败或已存在: {e}")

        # 4. 创建贡献值兑换记录表
        print("\n4. 创建贡献值兑换记录表...")
        try:
            db.execute(text("""
                CREATE TABLE IF NOT EXISTS contribution_value_exchanges (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    contribution_value INTEGER NOT NULL,
                    exchange_amount DECIMAL(10, 2) NOT NULL,
                    exchange_rate DECIMAL(10, 4) DEFAULT 0.1,
                    status VARCHAR(20) DEFAULT 'pending',
                    withdrawal_request_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (withdrawal_request_id) REFERENCES withdrawal_requests(id)
                )
            """))
            db.commit()
            print("   ✅ 贡献值兑换记录表创建成功")
        except Exception as e:
            db.rollback()
            print(f"   ⚠️  贡献值兑换记录表创建失败或已存在: {e}")

        # 5. 插入公司信息
        print("\n5. 插入公司信息...")
        try:
            db.execute(text("""
                INSERT INTO company_info (
                    company_name,
                    tax_number,
                    address,
                    phone,
                    bank_name,
                    bank_account,
                    status
                ) VALUES (
                    '陕西媄月商业艺术有限责任公司',
                    '91610132MAG0GQ2J24',
                    '陕西省西安市经济技术开发区海逸国际A座1601室-X048',
                    '15332290123',
                    '中国工商银行股份有限公司西安锦业路支行',
                    '3700084709100270877',
                    'active'
                )
            """))
            db.commit()
            print("   ✅ 公司信息插入成功")
        except Exception as e:
            db.rollback()
            if "duplicate key" in str(e).lower():
                print("   ⚠️  公司信息已存在，跳过插入")
            else:
                print(f"   ⚠️  公司信息插入失败: {e}")

        print("\n" + "=" * 60)
        print("✅ 所有财务管理相关表创建完成")
        print("=" * 60)

        # 显示创建的表
        print("\n📋 已创建的表：")
        print("1. company_info           - 公司信息表")
        print("2. withdrawal_requests    - 提现申请表")
        print("3. financial_transactions - 财务交易记录表")
        print("4. contribution_value_exchanges - 贡献值兑换记录表")

        # 显示公司信息
        print("\n🏢 公司信息：")
        result = db.execute(text("SELECT * FROM company_info LIMIT 1"))
        row = result.fetchone()
        if row:
            print(f"   公司名称: {row[1]}")
            print(f"   税号: {row[2]}")
            print(f"   地址: {row[3]}")
            print(f"   电话: {row[4]}")
            print(f"   开户银行: {row[5]}")
            print(f"   银行账户: {row[6]}")

    except Exception as e:
        print(f"\n❌ 创建表失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    add_financial_tables()

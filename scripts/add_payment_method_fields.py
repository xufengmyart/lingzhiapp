#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
添加用户收款方式字段
执行时间：2026-01-28
"""

import sys
sys.path.insert(0, '/workspace/projects/src')

from coze_coding_dev_sdk.database import get_session
from sqlalchemy import text


def add_payment_method_fields():
    """添加用户收款方式字段"""

    print("=" * 60)
    print("开始添加用户收款方式字段")
    print("=" * 60)

    db = get_session()

    try:
        # 1. 添加微信账号字段
        print("\n1. 添加微信账号字段...")
        try:
            db.execute(text(
                "ALTER TABLE users ADD COLUMN wechat_account VARCHAR(50)"
            ))
            db.commit()
            print("   ✅ 微信账号字段添加成功")
        except Exception as e:
            db.rollback()
            if "duplicate column name" in str(e).lower():
                print("   ⚠️  微信账号字段已存在，跳过")
            else:
                raise

        # 2. 添加微信二维码字段
        print("\n2. 添加微信二维码字段...")
        try:
            db.execute(text(
                "ALTER TABLE users ADD COLUMN wechat_qrcode VARCHAR(500)"
            ))
            db.commit()
            print("   ✅ 微信二维码字段添加成功")
        except Exception as e:
            db.rollback()
            if "duplicate column name" in str(e).lower():
                print("   ⚠️  微信二维码字段已存在，跳过")
            else:
                raise

        # 3. 添加支付宝账号字段
        print("\n3. 添加支付宝账号字段...")
        try:
            db.execute(text(
                "ALTER TABLE users ADD COLUMN alipay_account VARCHAR(100)"
            ))
            db.commit()
            print("   ✅ 支付宝账号字段添加成功")
        except Exception as e:
            db.rollback()
            if "duplicate column name" in str(e).lower():
                print("   ⚠️  支付宝账号字段已存在，跳过")
            else:
                raise

        # 4. 添加支付宝二维码字段
        print("\n4. 添加支付宝二维码字段...")
        try:
            db.execute(text(
                "ALTER TABLE users ADD COLUMN alipay_qrcode VARCHAR(500)"
            ))
            db.commit()
            print("   ✅ 支付宝二维码字段添加成功")
        except Exception as e:
            db.rollback()
            if "duplicate column name" in str(e).lower():
                print("   ⚠️  支付宝二维码字段已存在，跳过")
            else:
                raise

        # 5. 添加银行卡号字段
        print("\n5. 添加银行卡号字段...")
        try:
            db.execute(text(
                "ALTER TABLE users ADD COLUMN bank_card_number VARCHAR(20)"
            ))
            db.commit()
            print("   ✅ 银行卡号字段添加成功")
        except Exception as e:
            db.rollback()
            if "duplicate column name" in str(e).lower():
                print("   ⚠️  银行卡号字段已存在，跳过")
            else:
                raise

        # 6. 添加开户行名称字段
        print("\n6. 添加开户行名称字段...")
        try:
            db.execute(text(
                "ALTER TABLE users ADD COLUMN bank_name VARCHAR(100)"
            ))
            db.commit()
            print("   ✅ 开户行名称字段添加成功")
        except Exception as e:
            db.rollback()
            if "duplicate column name" in str(e).lower():
                print("   ⚠️  开户行名称字段已存在，跳过")
            else:
                raise

        # 7. 添加银行账户姓名字段
        print("\n7. 添加银行账户姓名字段...")
        try:
            db.execute(text(
                "ALTER TABLE users ADD COLUMN bank_account_name VARCHAR(50)"
            ))
            db.commit()
            print("   ✅ 银行账户姓名字段添加成功")
        except Exception as e:
            db.rollback()
            if "duplicate column name" in str(e).lower():
                print("   ⚠️  银行账户姓名字段已存在，跳过")
            else:
                raise

        # 8. 添加首选收款方式字段
        print("\n8. 添加首选收款方式字段...")
        try:
            db.execute(text(
                "ALTER TABLE users ADD COLUMN preferred_payment_method VARCHAR(20)"
            ))
            db.commit()
            print("   ✅ 首选收款方式字段添加成功")
        except Exception as e:
            db.rollback()
            if "duplicate column name" in str(e).lower():
                print("   ⚠️  首选收款方式字段已存在，跳过")
            else:
                raise

        print("\n" + "=" * 60)
        print("✅ 所有收款方式字段添加完成")
        print("=" * 60)

        # 显示添加的字段
        print("\n📋 已添加的字段：")
        print("1. wechat_account          - 微信账号")
        print("2. wechat_qrcode           - 微信收款二维码URL")
        print("3. alipay_account          - 支付宝账号")
        print("4. alipay_qrcode           - 支付宝收款二维码URL")
        print("5. bank_card_number        - 银行卡号")
        print("6. bank_name               - 开户行名称")
        print("7. bank_account_name       - 银行账户姓名")
        print("8. preferred_payment_method- 首选收款方式")

    except Exception as e:
        print(f"\n❌ 添加字段失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    add_payment_method_fields()

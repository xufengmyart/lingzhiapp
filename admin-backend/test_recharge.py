#!/usr/bin/env python3
"""
充值和支付功能测试脚本
验证充值流程、订单创建、支付处理和灵值到账
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000/api"

def print_test(test_name, passed, details=""):
    """打印测试结果"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"\n{status} - {test_name}")
    if details:
        print(f"   {details}")

def test_recharge_tiers():
    """测试充值档位"""
    print("\n" + "="*60)
    print("测试充值档位")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/recharge/tiers", timeout=10)
        data = response.json()
        print_test("获取充值档位", response.status_code == 200 and data.get('success'))
        
        if response.status_code == 200:
            tiers = data.get('data', [])
            print(f"   找到 {len(tiers)} 个充值档位")
            
            if tiers:
                for tier in tiers[:2]:  # 显示前两个
                    print(f"   - {tier.get('name')}: ¥{tier.get('price')} ({tier.get('baseLingzhi')}灵值)")
                
                return tiers[0]['id']  # 返回第一个档位ID
    except Exception as e:
        print_test("获取充值档位", False, str(e))
    return None

def test_create_recharge_order(tier_id, user_id=10):
    """测试创建充值订单"""
    if not tier_id:
        print("\n" + "="*60)
        print("跳过创建充值订单（无有效档位ID）")
        print("="*60)
        return None
    
    print("\n" + "="*60)
    print("测试创建充值订单")
    print("="*60)
    
    try:
        response = requests.post(
            f"{BASE_URL}/recharge/create-order",
            json={
                'user_id': user_id,
                'tier_id': tier_id,
                'payment_method': 'alipay'
            },
            timeout=10
        )
        data = response.json()
        print_test("创建充值订单", response.status_code == 200 and data.get('success'))
        
        if response.status_code == 200 and data.get('success'):
            order_data = data.get('data', {})
            order_no = order_data.get('order_no')
            print(f"   订单号: {order_no}")
            print(f"   订单金额: ¥{order_data.get('amount')}")
            print(f"   获得灵值: {order_data.get('total_lingzhi')}")
            return order_no
    except Exception as e:
        print_test("创建充值订单", False, str(e))
    return None

def test_company_accounts():
    """测试公司收款账户"""
    print("\n" + "="*60)
    print("测试公司收款账户")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/company/accounts", timeout=10)
        data = response.json()
        print_test("获取收款账户", response.status_code == 200 and data.get('success'))
        
        if response.status_code == 200:
            accounts = data.get('data', [])
            print(f"   找到 {len(accounts)} 个收款账户")
            
            if accounts:
                for account in accounts:
                    print(f"   - {account.get('account_name')}: {account.get('bank_name')}")
    except Exception as e:
        print_test("获取收款账户", False, str(e))

def test_alipay_payment(order_no):
    """测试支付宝支付创建"""
    if not order_no:
        print("\n" + "="*60)
        print("跳过支付宝支付测试（无有效订单号）")
        print("="*60)
        return None
    
    print("\n" + "="*60)
    print("测试支付宝支付创建")
    print("="*60)
    
    try:
        response = requests.post(
            f"{BASE_URL}/payment/alipay/create",
            json={'order_no': order_no},
            timeout=10
        )
        data = response.json()
        print_test("创建支付宝支付", response.status_code == 200 and data.get('success'))
        
        if response.status_code == 200 and data.get('success'):
            payment_data = data.get('data', {})
            print(f"   支付URL: {payment_data.get('payment_url')}")
            print(f"   二维码: {payment_data.get('qr_code')}")
    except Exception as e:
        print_test("创建支付宝支付", False, str(e))

def test_simulate_payment(order_no):
    """测试模拟支付"""
    if not order_no:
        print("\n" + "="*60)
        print("跳过模拟支付测试（无有效订单号）")
        print("="*60)
        return None
    
    print("\n" + "="*60)
    print("测试模拟支付")
    print("="*60)
    
    try:
        response = requests.post(
            f"{BASE_URL}/payment/simulate/{order_no}",
            timeout=10
        )
        data = response.json()
        print_test("模拟支付", response.status_code == 200 and data.get('success'))
        
        if response.status_code == 200 and data.get('success'):
            payment_data = data.get('data', {})
            print(f"   交易ID: {payment_data.get('transaction_id')}")
            print(f"   支付金额: ¥{payment_data.get('amount')}")
            print(f"   到账灵值: {payment_data.get('total_lingzhi')}")
            print(f"   新余额: {payment_data.get('new_balance')}")
            return payment_data
    except Exception as e:
        print_test("模拟支付", False, str(e))
    return None

def test_payment_status(order_no):
    """测试查询支付状态"""
    if not order_no:
        print("\n" + "="*60)
        print("跳过支付状态查询（无有效订单号）")
        print("="*60)
        return None
    
    print("\n" + "="*60)
    print("测试支付状态查询")
    print("="*60)
    
    try:
        response = requests.get(
            f"{BASE_URL}/payment/status/{order_no}",
            timeout=10
        )
        data = response.json()
        print_test("查询支付状态", response.status_code == 200 and data.get('success'))
        
        if response.status_code == 200 and data.get('success'):
            status_data = data.get('data', {})
            print(f"   订单号: {status_data.get('order_no')}")
            print(f"   支付状态: {status_data.get('payment_status')}")
            print(f"   支付时间: {status_data.get('payment_time')}")
            print(f"   交易ID: {status_data.get('transaction_id')}")
    except Exception as e:
        print_test("查询支付状态", False, str(e))

def test_user_lingzhi_balance(user_id=10):
    """测试用户灵值余额"""
    print("\n" + "="*60)
    print("测试用户灵值余额")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/user/info", timeout=10)
        data = response.json()
        
        if response.status_code == 200 and data.get('success'):
            user_data = data.get('data', {})
            balance = user_data.get('balance', user_data.get('totalLingzhi', 0))
            print_test(f"用户灵值余额", True, f"当前余额: {balance} 灵值")
            return balance
    except Exception as e:
        print_test("查询用户灵值余额", False, str(e))
    return None

def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("🚀 充值和支付功能测试")
    print("="*60)
    print(f"   时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   API地址: {BASE_URL}")
    print("="*60)
    
    # 检查服务是否运行
    try:
        response = requests.get(f"{BASE_URL}/recharge/tiers", timeout=5)
        print("\n✅ 后端服务运行正常")
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到后端服务")
        print("   请确保后端服务正在运行: cd admin-backend && python3 app.py")
        return
    
    # 测试前记录用户余额
    print("\n" + "="*60)
    print("记录初始余额")
    print("="*60)
    initial_balance = test_user_lingzhi_balance()
    
    # 运行所有测试
    tier_id = test_recharge_tiers()
    test_company_accounts()
    
    order_no = None
    if tier_id:
        order_no = test_create_recharge_order(tier_id)
    
    if order_no:
        test_alipay_payment(order_no)
        payment_data = test_simulate_payment(order_no)
        test_payment_status(order_no)
    
    # 测试后记录用户余额
    print("\n" + "="*60)
    print("验证充值到账")
    print("="*60)
    final_balance = test_user_lingzhi_balance()
    
    if initial_balance is not None and final_balance is not None and payment_data:
        expected_balance = initial_balance + payment_data.get('total_lingzhi', 0)
        if final_balance >= expected_balance:
            print_test("充值到账验证", True, f"余额增加: {final_balance - initial_balance}")
        else:
            print_test("充值到账验证", False, f"期望: {expected_balance}, 实际: {final_balance}")
    
    # 打印总结
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    print("   充值功能测试完成")
    print("   请检查测试结果是否符合预期")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
测试脚本：验证前端修复后API调用是否正常
"""

import requests
import json

# API配置
API_URL = "https://meiyueart.com/api/chat"
TEST_MESSAGE = "公司"

def test_api():
    """测试API调用"""
    print("=" * 60)
    print("测试前端修复后的API调用")
    print("=" * 60)

    # 构造请求数据（模拟前端发送的数据）
    payload = {
        "message": TEST_MESSAGE,
        "conversationId": f"test_fix_{__import__('time').time()}",
        "agentId": 1,
        "enableThinking": False
    }

    print(f"\n请求路径: {API_URL}")
    print(f"请求数据: {json.dumps(payload, ensure_ascii=False)}")

    try:
        # 发送请求
        response = requests.post(
            API_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        print(f"\n响应状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            if data.get('success'):
                reply = data.get('data', {}).get('reply', '')
                reply_length = len(reply)

                print(f"\n✅ API调用成功")
                print(f"回复长度: {reply_length} 字符")
                print(f"\n回复预览（前200字）:")
                print(reply[:200])
                print("...")

                # 验证回复是否详细
                if reply_length > 100:
                    print(f"\n✅ 回复详细程度验证通过（> 100字）")
                    return True
                else:
                    print(f"\n❌ 回复过于简短（< 100字）")
                    return False
            else:
                print(f"\n❌ API返回失败: {data.get('error', '未知错误')}")
                return False
        else:
            print(f"\n❌ API调用失败: HTTP {response.status_code}")
            print(f"响应内容: {response.text}")
            return False

    except Exception as e:
        print(f"\n❌ 请求异常: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_api()

    print("\n" + "=" * 60)
    if success:
        print("✅ 测试通过：前端修复成功，API返回详细回复")
    else:
        print("❌ 测试失败：前端修复无效，API返回简短回复")
    print("=" * 60)

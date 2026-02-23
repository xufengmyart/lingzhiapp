#!/usr/bin/env python3
"""详细检查 app.py 导入过程"""

import sys
import os

# 设置环境变量
os.environ['COZE_WORKLOAD_IDENTITY_API_KEY'] = 'WU9RNGFQTmZTc3VnbnRCMmsyWUtDcDZHOWJMa0g5ZVk6NVN5cHNRbkNidjFzWHNEVnJ4UTZKQlN1SUxYMlU3ZEtidVRXbDYwWDFyZW9sdmhQbTU1QVdQaVJHcVo4b1BoWA=='
os.environ['COZE_INTEGRATION_MODEL_BASE_URL'] = 'https://integration.coze.cn/api/v3'
os.environ['COZE_INTEGRATION_BASE_URL'] = 'https://integration.coze.cn'
os.environ['COZE_PROJECT_ID'] = '7597768668038643746'

print("=" * 60)
print("步骤 1: 检查 Python 环境")
print("=" * 60)
print(f"Python 版本: {sys.version}")
print(f"Python 路径: {sys.executable}")

print("\n" + "=" * 60)
print("步骤 2: 检查环境变量")
print("=" * 60)
for key in ['COZE_WORKLOAD_IDENTITY_API_KEY', 'COZE_INTEGRATION_MODEL_BASE_URL', 'COZE_INTEGRATION_BASE_URL', 'COZE_PROJECT_ID']:
    print(f"{key}: {os.getenv(key, 'NOT_SET')}")

print("\n" + "=" * 60)
print("步骤 3: 测试导入 langchain_core")
print("=" * 60)
try:
    from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
    print("✓ langchain_core 导入成功")
except Exception as e:
    print(f"✗ langchain_core 导入失败: {e}")

print("\n" + "=" * 60)
print("步骤 4: 测试导入 coze_coding_dev_sdk")
print("=" * 60)
try:
    from coze_coding_dev_sdk import LLMClient
    print("✓ coze_coding_dev_sdk 导入成功")
    LLM_AVAILABLE = True
except ImportError as e:
    print(f"✗ coze_coding_dev_sdk 导入失败: {e}")
    LLM_AVAILABLE = False
except Exception as e:
    print(f"✗ coze_coding_dev_sdk 导入异常: {e}")
    LLM_AVAILABLE = False

print(f"\nLLM_AVAILABLE = {LLM_AVAILABLE}")

print("\n" + "=" * 60)
print("步骤 5: 测试导入 coze_coding_utils")
print("=" * 60)
try:
    from coze_coding_utils.runtime_ctx.context import new_context
    print("✓ coze_coding_utils 导入成功")
except Exception as e:
    print(f"✗ coze_coding_utils 导入失败: {e}")

print("\n" + "=" * 60)
print("总结")
print("=" * 60)
print(f"LLM 可用: {LLM_AVAILABLE}")

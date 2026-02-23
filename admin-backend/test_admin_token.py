#!/usr/bin/env python
"""
测试admin token解码
"""
import sys
sys.path.append('admin-backend')

import jwt
from config import config

# 从登录响应中获取的token
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMCwidXNlcm5hbWUiOiJhZG1pbiIsImV4cCI6MTc3MjI1ODkzNiwiaWF0IjoxNzcxNjU0MTM2fQ.AExV_FywVnFs7FtvB9CP7nzhzGejk-qJ5IcLyrHB-CE"

print("尝试解码admin token...")
print("=" * 80)

try:
    # 尝试解码
    payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=['HS256'])
    print("✓ Token解码成功")
    print(f"Payload: {payload}")
except jwt.ExpiredSignatureError:
    print("✗ Token已过期")
except jwt.InvalidTokenError as e:
    print(f"✗ Token无效: {e}")
except Exception as e:
    print(f"✗ 解码失败: {e}")

print()
print("=" * 80)
print("JWT密钥:", config.JWT_SECRET_KEY[:20] + "...")

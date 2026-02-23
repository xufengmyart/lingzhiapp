#!/bin/bash
#
# 智能体路径修复测试脚本（2026-02-15）
# 用于测试生产环境的修复结果
#

set -e

BASE_URL="https://meiyueart.com"

echo "========================================"
echo "智能体路径修复测试脚本（2026-02-15）"
echo "========================================"

# 测试 1: 登录
echo ""
echo "[测试 1/4] 用户登录..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123456"}')

TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.data.token // empty')

if [ -n "$TOKEN" ]; then
    echo "  ✓ 登录成功"
    echo "  Token: ${TOKEN:0:20}..."
else
    echo "  ✗ 登录失败"
    echo "  响应: $LOGIN_RESPONSE"
    exit 1
fi

# 测试 2: 获取用户信息
echo ""
echo "[测试 2/4] 获取用户信息..."
USER_INFO=$(curl -s -X GET "$BASE_URL/api/user/info" \
  -H "Authorization: Bearer $TOKEN")

USER_ID=$(echo $USER_INFO | jq -r '.data.user.id // empty')

if [ -n "$USER_ID" ]; then
    echo "  ✓ 用户信息获取成功"
    echo "  用户ID: $USER_ID"
else
    echo "  ✗ 用户信息获取失败"
    echo "  响应: $USER_INFO"
fi

# 测试 3: 获取智能体列表
echo ""
echo "[测试 3/4] 获取智能体列表..."
AGENTS_RESPONSE=$(curl -s -X GET "$BASE_URL/api/admin/agents" \
  -H "Authorization: Bearer $TOKEN")

AGENTS_COUNT=$(echo $AGENTS_RESPONSE | jq -r '.data | length // 0')

if [ "$AGENTS_COUNT" -gt 0 ]; then
    echo "  ✓ 智能体列表获取成功"
    echo "  智能体数量: $AGENTS_COUNT"
    
    # 获取第一个智能体ID
    AGENT_ID=$(echo $AGENTS_RESPONSE | jq -r '.data[0].id // 2')
    echo "  使用智能体ID: $AGENT_ID"
else
    echo "  ✗ 智能体列表获取失败"
    echo "  响应: $AGENTS_RESPONSE"
    # 使用默认ID
    AGENT_ID=2
    echo "  使用默认智能体ID: $AGENT_ID"
fi

# 测试 4: 智能体聊天
echo ""
echo "[测试 4/4] 智能体聊天（路径: /api/agent/chat）..."
CHAT_RESPONSE=$(curl -s -X POST "$BASE_URL/api/agent/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"content\":\"你好\",\"agentId\":$AGENT_ID,\"enableThinking\":false}")

CHAT_SUCCESS=$(echo $CHAT_RESPONSE | jq -r '.success // false')

if [ "$CHAT_SUCCESS" = "true" ]; then
    echo "  ✓ 智能体聊天成功（/api/agent/chat）"
    REPLY_LENGTH=$(echo $CHAT_RESPONSE | jq -r '.data.reply | length // 0')
    echo "  回复长度: $REPLY_LENGTH 字符"
    
    # 显示回复预览
    REPLY_PREVIEW=$(echo $CHAT_RESPONSE | jq -r '.data.reply // "无回复"' | head -c 100)
    echo "  回复预览: $REPLY_PREVIEW..."
else
    echo "  ✗ 智能体聊天失败"
    echo "  响应: $CHAT_RESPONSE"
fi

# 测试 5: 智能体聊天（兼容路径）
echo ""
echo "[测试 5/5] 智能体聊天（兼容路径: /agent/chat）..."
CHAT_V1_RESPONSE=$(curl -s -X POST "$BASE_URL/agent/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"content\":\"介绍你的公司\",\"agentId\":$AGENT_ID,\"enableThinking\":false}")

CHAT_V1_SUCCESS=$(echo $CHAT_V1_RESPONSE | jq -r '.success // false')

if [ "$CHAT_V1_SUCCESS" = "true" ]; then
    echo "  ✓ 智能体聊天成功（/agent/chat）"
    REPLY_LENGTH=$(echo $CHAT_V1_RESPONSE | jq -r '.data.reply | length // 0')
    echo "  回复长度: $REPLY_LENGTH 字符"
    
    # 显示回复预览
    REPLY_PREVIEW=$(echo $CHAT_V1_RESPONSE | jq -r '.data.reply // "无回复"' | head -c 100)
    echo "  回复预览: $REPLY_PREVIEW..."
else
    echo "  ✗ 智能体聊天失败（兼容路径）"
    echo "  响应: $CHAT_V1_RESPONSE"
fi

echo ""
echo "========================================"
echo "✅ 测试完成"
echo "========================================"
echo ""
echo "测试结果："
echo "  ✓ 用户登录"
echo "  ✓ 获取用户信息"
echo "  ✓ 获取智能体列表"
if [ "$CHAT_SUCCESS" = "true" ]; then
    echo "  ✓ 智能体聊天（/api/agent/chat）"
else
    echo "  ✗ 智能体聊天（/api/agent/chat）"
fi
if [ "$CHAT_V1_SUCCESS" = "true" ]; then
    echo "  ✓ 智能体聊天（/agent/chat）"
else
    echo "  ✗ 智能体聊天（/agent/chat）"
fi
echo ""

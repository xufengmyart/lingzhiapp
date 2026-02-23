#!/bin/bash

# 智能体API测试脚本

API_URL="http://localhost:8080/api/chat"

echo "=========================================="
echo "测试1: 询问公司信息"
echo "=========================================="
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{"message": "公司是谁开发的？", "enable_memory": false}' \
  --max-time 120 \
  -s | python -m json.tool | grep -A 50 '"reply"'

echo ""
echo "=========================================="
echo "测试2: 询问灵值获取"
echo "=========================================="
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{"message": "如何获取灵值？", "enable_memory": false}' \
  --max-time 120 \
  -s | python -m json.tool | grep -A 50 '"reply"'

echo ""
echo "=========================================="
echo "测试3: 询问合伙人制度"
echo "=========================================="
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{"message": "什么是合伙人？如何申请？", "enable_memory": false}' \
  --max-time 120 \
  -s | python -m json.tool | grep -A 50 '"reply"'

echo ""
echo "=========================================="
echo "测试4: 询问西安文化"
echo "=========================================="
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{"message": "西安文化有哪些特色？", "enable_memory": false}' \
  --max-time 120 \
  -s | python -m json.tool | grep -A 50 '"reply"'

echo ""
echo "=========================================="
echo "测试完成"
echo "=========================================="

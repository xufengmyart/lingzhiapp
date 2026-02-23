#!/bin/bash
# 快速修复导航栏z-index

echo "============================================================"
echo "快速修复导航栏z-index"
echo "============================================================"
echo ""

NAV_FILE="/workspace/projects/web-app/src/components/Navigation.tsx"

if [ ! -f "$NAV_FILE" ]; then
    echo "❌ 找不到导航栏文件: $NAV_FILE"
    exit 1
fi

echo "当前z-index设置:"
grep -n "z-50" "$NAV_FILE" | head -5
echo ""

echo "正在替换z-50为z-[999999]..."
sed -i 's/z-50/z-[999999]/g' "$NAV_FILE"

echo "✓ 替换完成"
echo ""
echo "新的z-index设置:"
grep -n "z-\[999999\]" "$NAV_FILE" | head -5
echo ""

echo "============================================================"
echo "✓ 导航栏z-index修复完成"
echo "============================================================"
echo ""
echo "请刷新页面测试导航栏功能"
echo ""

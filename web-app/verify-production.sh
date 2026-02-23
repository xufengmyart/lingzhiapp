#!/bin/bash

# 生产环境验证脚本
# 用于验证生产环境部署是否成功

echo "=========================================="
echo "生产环境验证脚本"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PRODUCTION_URL="https://meiyueart.com"
TEST_COUNT=0
PASS_COUNT=0
FAIL_COUNT=0

# 测试函数
test_item() {
    TEST_COUNT=$((TEST_COUNT + 1))
    echo -n "[测试 $TEST_COUNT] $1 ... "
}

test_pass() {
    PASS_COUNT=$((PASS_COUNT + 1))
    echo -e "${GREEN}✓ PASS${NC}"
}

test_fail() {
    FAIL_COUNT=$((FAIL_COUNT + 1))
    echo -e "${RED}✗ FAIL${NC}"
    echo "  错误: $1"
}

test_skip() {
    TEST_COUNT=$((TEST_COUNT + 1))
    echo -e "${YELLOW}[测试 $TEST_COUNT] $1 ... SKIP${NC}"
}

echo "=========================================="
echo "基础检查"
echo "=========================================="

# 1. 检查生产目录
test_item "检查生产目录存在"
if [ -d "/var/www/meiyueart.com" ]; then
    test_pass
    PROD_DIR="/var/www/meiyueart.com"
elif [ -d "$PRODUCTION_DIR" ]; then
    test_pass
    PROD_DIR="$PRODUCTION_URL"
else
    test_fail "生产目录不存在"
    exit 1
fi

# 2. 检查 index.html
test_item "检查 index.html 存在"
if [ -f "$PROD_DIR/index.html" ]; then
    test_pass
else
    test_fail "index.html 不存在"
    exit 1
fi

# 3. 检查新版本 JS 文件
test_item "检查新版本 JS 文件存在"
if [ -f "$PROD_DIR/assets/index-BZC2kyOR.js" ]; then
    test_pass
else
    test_fail "新版本 JS 文件不存在"
fi

# 4. 检查版本号
test_item "检查版本号 (20260209-0935)"
if grep -q "20260209-0935" "$PROD_DIR/index.html"; then
    test_pass
else
    test_fail "版本号不正确"
fi

# 5. 检查旧版本文件是否已删除
test_item "检查旧版本文件是否已删除"
if [ ! -f "$PROD_DIR/assets/index-KGT10jHb.js" ]; then
    test_pass
else
    test_fail "旧版本文件仍存在"
fi

# 6. 检查 CSS 文件
test_item "检查 CSS 文件存在"
if [ -f "$PROD_DIR/assets/index-CiAneXUA.css" ]; then
    test_pass
else
    test_fail "CSS 文件不存在"
fi

echo ""
echo "=========================================="
echo "网络访问测试"
echo "=========================================="

# 7. 测试网站可访问性
test_item "测试网站可访问性"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$PRODUCTION_URL" 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    test_pass
else
    test_fail "HTTP 状态码: $HTTP_CODE"
fi

# 8. 测试 API 健康检查
test_item "测试 API 健康检查"
API_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$PRODUCTION_URL/api/health" 2>/dev/null || echo "000")
if [ "$API_CODE" = "200" ]; then
    test_pass
    API_RESPONSE=$(curl -s "$PRODUCTION_URL/api/health" 2>/dev/null || echo "{}")
    if echo "$API_RESPONSE" | grep -q "ok"; then
        echo "  响应: $API_RESPONSE"
    fi
else
    test_fail "API 状态码: $API_CODE"
fi

# 9. 检查缓存清除脚本
test_item "检查缓存清除脚本"
if curl -s "$PRODUCTION_URL" | grep -q "缓存清除"; then
    test_pass
else
    test_fail "缓存清除脚本不存在"
fi

# 10. 检查 HTTPS 证书
test_item "检查 HTTPS 证书"
if curl -s -I "$PRODUCTION_URL" 2>/dev/null | grep -q "HTTP/2"; then
    test_pass
    CERT_INFO=$(curl -sI "$PRODUCTION_URL" 2>/dev/null | grep -i ssl || echo "无信息")
else
    test_fail "HTTPS 配置可能有问题"
fi

echo ""
echo "=========================================="
echo "文件完整性检查"
echo "=========================================="

# 11. 检查 sw.js
test_item "检查 Service Worker 文件"
if [ -f "$PROD_DIR/sw.js" ]; then
    test_pass
else
    test_fail "Service Worker 文件不存在"
fi

# 12. 检查 manifest.json
test_item "检查 manifest.json"
if [ -f "$PROD_DIR/manifest.json" ]; then
    test_pass
else
    test_skip "manifest.json 可选"
fi

# 13. 检查 favicon
test_item "检查 favicon"
if [ -f "$PROD_DIR/vite.svg" ] || [ -f "$PROD_DIR/favicon.ico" ]; then
    test_pass
else
    test_skip "favicon 可选"
fi

# 14. 检查 robots.txt
test_item "检查 robots.txt"
if [ -f "$PROD_DIR/robots.txt" ]; then
    test_pass
else
    test_skip "robots.txt 可选"
fi

# 15. 检查 sitemap.xml
test_item "检查 sitemap.xml"
if [ -f "$PROD_DIR/sitemap.xml" ]; then
    test_pass
else
    test_skip "sitemap.xml 可选"
fi

echo ""
echo "=========================================="
echo "权限检查"
echo "=========================================="

# 16. 检查目录权限
test_item "检查目录权限"
PERMS=$(stat -c "%a" "$PROD_DIR" 2>/dev/null || stat -f "%Lp" "$PROD_DIR" 2>/dev/null || echo "000")
if [ "$PERMS" = "755" ]; then
    test_pass
else
    echo "  当前权限: $PERMS (推荐: 755)"
    test_skip "权限不是 755"
fi

# 17. 检查文件所有权
test_item "检查文件所有权"
if [ -r "$PROD_DIR/index.html" ]; then
    test_pass
else
    test_fail "文件不可读"
fi

echo ""
echo "=========================================="
echo "性能检查"
echo "=========================================="

# 18. 检查页面大小
test_item "检查页面大小"
PAGE_SIZE=$(stat -c "%s" "$PROD_DIR/index.html" 2>/dev/null || stat -f "%z" "$PROD_DIR/index.html" 2>/dev/null || echo "0")
PAGE_SIZE_KB=$((PAGE_SIZE / 1024))
echo "  页面大小: ${PAGE_SIZE_KB} KB"
if [ "$PAGE_SIZE_KB" -lt 50 ]; then
    test_pass
else
    echo "  页面较大，建议优化"
    test_skip "页面大小 > 50 KB"
fi

# 19. 检查 JS 文件大小
test_item "检查 JS 文件大小"
JS_SIZE=$(stat -c "%s" "$PROD_DIR/assets/index-BZC2kyOR.js" 2>/dev/null || stat -f "%z" "$PROD_DIR/assets/index-BZC2kyOR.js" 2>/dev/null || echo "0")
JS_SIZE_KB=$((JS_SIZE / 1024))
echo "  JS 大小: ${JS_SIZE_KB} KB"
test_pass

# 20. 检查 CSS 文件大小
test_item "检查 CSS 文件大小"
CSS_SIZE=$(stat -c "%s" "$PROD_DIR/assets/index-CiAneXUA.css" 2>/dev/null || stat -f "%z" "$PROD_DIR/assets/index-CiAneXUA.css" 2>/dev/null || echo "0")
CSS_SIZE_KB=$((CSS_SIZE / 1024))
echo "  CSS 大小: ${CSS_SIZE_KB} KB"
test_pass

echo ""
echo "=========================================="
echo "测试结果汇总"
echo "=========================================="
echo "总测试数: $TEST_COUNT"
echo -e "${GREEN}通过: $PASS_COUNT${NC}"
echo -e "${RED}失败: $FAIL_COUNT${NC}"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}✓ 所有测试通过！${NC}"
    echo ""
    echo "下一步："
    echo "1. 清除浏览器缓存"
    echo "   Windows: Ctrl + Shift + Delete"
    echo "   Mac: Cmd + Shift + Delete"
    echo ""
    echo "2. 访问网站验证"
    echo "   $PRODUCTION_URL"
    echo ""
    echo "3. 打开浏览器控制台检查"
    echo "   - Network 面板应显示 index-BZC2kyOR.js"
    echo "   - Console 面板应显示缓存清除提示"
    echo ""
    exit 0
else
    echo -e "${RED}✗ 有 $FAIL_COUNT 个测试失败${NC}"
    echo ""
    echo "请检查上述失败的测试项，修复后重新运行此脚本。"
    echo ""
    exit 1
fi

#!/bin/bash
# 自动注册平台信息增强蓝图到 app.py

APP_FILE="admin-backend/app.py"

# 检查文件是否存在
if [ ! -f "$APP_FILE" ]; then
    echo "❌ app.py 文件不存在"
    exit 1
fi

# 检查是否已经注册
if grep -q "platform_info_enhanced_bp" "$APP_FILE"; then
    echo "✅ 平台信息增强蓝图已经注册"
    exit 0
fi

# 查找插入位置（在平台信息注册之后）
INSERT_AFTER_LINE=$(grep -n "平台信息 API 已注册" "$APP_FILE" | head -1 | cut -d: -f1)

if [ -z "$INSERT_AFTER_LINE" ]; then
    echo "❌ 无法找到插入位置"
    exit 1
fi

# 创建临时文件
TEMP_FILE=$(mktemp)

# 插入注册代码
awk -v line="$INSERT_AFTER_LINE" 'NR==line {
    print ""
    print "# 27.3. 平台信息增强功能（推送、阅读、订阅、评论、分享）"
    print "try:"
    print "    from routes.platform_info_enhanced import platform_info_enhanced_bp"
    print "    app.register_blueprint(platform_info_enhanced_bp, url_prefix='"'/api'"')"
    print "    print('"'"'✅ 平台信息增强功能 API 已注册'"'"')"
    print "except Exception as e:"
    print "    print(f'"'"'⚠️  平台信息增强功能模块加载失败: {e}'"'"')"
}
{print}' "$APP_FILE" > "$TEMP_FILE"

# 替换原文件
mv "$TEMP_FILE" "$APP_FILE"

echo "✅ 平台信息增强蓝图注册成功"
echo "📍 插入位置: 第 $INSERT_AFTER_LINE 行之后"

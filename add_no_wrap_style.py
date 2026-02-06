#!/usr/bin/env python3
"""
批量添加不换行样式到所有页面
"""

import os
import re

def add_no_wrap_to_file(file_path):
    """为文件中的标题和重要文本添加no-wrap类"""
    print(f"处理: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 为h1, h2, h3标签添加no-wrap类（如果还没有）
    # 匹配: className="text-xxx font-xxx"
    def add_no_wrap(match):
        class_str = match.group(1)
        if 'no-wrap' not in class_str and 'whitespace' not in class_str:
            return f'className="{class_str} no-wrap"'
        return match.group(0)
    
    # 匹配h1标签
    content = re.sub(
        r'<h1[^>]*className="([^"]+text-[^"]+)"',
        add_no_wrap,
        content
    )
    
    # 匹配h2标签
    content = re.sub(
        r'<h2[^>]*className="([^"]+text-[^"]+)"',
        add_no_wrap,
        content
    )
    
    # 匹配h3标签
    content = re.sub(
        r'<h3[^>]*className="([^"]+text-[^"]+)"',
        add_no_wrap,
        content
    )
    
    # 为重要的span文本添加no-wrap（特别是导航和按钮文本）
    # 匹配: <span>文本</span>，文本较短（<20字符）
    def add_no_wrap_to_span(match):
        full_match = match.group(0)
        text = match.group(1)
        # 只为短文本添加（标题、标签等）
        if len(text) < 20 and text not in ['灵值', '元', '%']:
            if 'className=' not in full_match:
                return f'<span className="no-wrap">{text}</span>'
        return full_match
    
    # 跳过某些已处理过的span
    content = re.sub(
        r'<span>([^<]{1,19})</span>',
        add_no_wrap_to_span,
        content
    )
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ 已更新")
        return True
    else:
        print(f"  ℹ️  无需更新")
        return False

def main():
    # 需要处理的文件列表
    files_to_process = [
        'web-app/src/pages/Dashboard.tsx',
        'web-app/src/pages/Chat.tsx',
        'web-app/src/pages/Economy.tsx',
        'web-app/src/pages/Partner.tsx',
        'web-app/src/pages/Profile.tsx',
        'web-app/src/pages/Login.tsx',
        'web-app/src/pages/Register.tsx',
    ]
    
    updated_count = 0
    
    for file_path in files_to_process:
        if os.path.exists(file_path):
            if add_no_wrap_to_file(file_path):
                updated_count += 1
        else:
            print(f"⚠️  文件不存在: {file_path}")
    
    print(f"\n总计更新了 {updated_count} 个文件")

if __name__ == '__main__':
    main()

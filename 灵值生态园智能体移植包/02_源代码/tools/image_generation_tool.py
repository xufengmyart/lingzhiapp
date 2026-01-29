"""
图像生成工具（融合统一版）

版本：v6.0 融合统一版
更新日期：2026年1月26日
融合内容：
- 支持多种尺寸（2K、1K、自定义）
- 支持多种风格（写实、动漫、艺术等）
- 支持自定义图片数量
- 支持水印控制
- 更友好的输出格式
"""

from langchain.tools import tool
from langchain.tools import ToolRuntime
from coze_coding_dev_sdk import ImageGenerationClient
from typing import Optional, Literal


@tool
def generate_image(
    prompt: str,
    runtime: ToolRuntime,
    style: Literal["realistic", "anime", "art", "sketch"] = "realistic",
    size: Literal["2K", "1K", "512x512", "768x768", "1024x1024"] = "2K",
    num_images: int = 1,
    watermark: bool = False
) -> str:
    """生成品牌视觉创意、空间设计方案等图像（融合统一版）
    
    支持多种风格和尺寸，满足不同场景需求：
    - 风格选择：写实、动漫、艺术、素描
    - 尺寸选择：2K（超高清）、1K（高清）、512x512、768x768、1024x1024
    - 批量生成：一次可生成1-15张图片
    
    Args:
        prompt: 图像生成提示词，例如"唐风茶馆设计，优雅大气"
        runtime: 运行时上下文
        style: 图像风格，可选：realistic（写实）、anime（动漫）、art（艺术）、sketch（素描），默认为realistic
        size: 图像尺寸，可选：2K、1K、512x512、768x768、1024x1024，默认为2K
        num_images: 生成图片数量，1-15张，默认为1
        watermark: 是否添加水印，默认为False
    
    Returns:
        返回生成图像的URL列表和相关信息
    """
    ctx = runtime.context
    client = ImageGenerationClient(ctx=ctx)
    
    # 验证参数
    if num_images < 1 or num_images > 15:
        return "❌ 图片数量必须在1-15张之间"
    
    # 尺寸映射
    size_mapping = {
        "2K": "2K",
        "1K": "1K",
        "512x512": "512x512",
        "768x768": "768x768",
        "1024x1024": "1024x1024"
    }
    
    actual_size = size_mapping.get(size, "2K")
    
    # 风格映射
    style_mapping = {
        "realistic": "写实风格",
        "anime": "动漫风格",
        "art": "艺术风格",
        "sketch": "素描风格"
    }
    
    style_desc = style_mapping.get(style, "写实风格")
    
    try:
        response = client.generate(
            prompt=prompt,
            style=style,
            size=actual_size,
            num_images=num_images,
            watermark=watermark
        )
        
        if response.code == 0 and hasattr(response, 'images') and response.images:
            # 构建友好的返回结果
            result_parts = [
                f"✅ 图片生成成功！\n",
                f"📋 生成参数：\n",
                f"   - 描述: {prompt[:100]}{'...' if len(prompt) > 100 else ''}\n",
                f"   - 风格: {style_desc}\n",
                f"   - 尺寸: {size}\n",
                f"   - 数量: {len(response.images)}张\n",
                f"   - 水印: {'是' if watermark else '否'}\n",
                f"\n📸 图片链接："
            ]
            
            for i, img in enumerate(response.images, 1):
                result_parts.append(f"\n   {i}. {img.url}")
            
            result_parts.append("\n\n💡 提示：点击链接查看或下载图片")
            
            return "".join(result_parts)
        else:
            error_msg = response.message if hasattr(response, 'message') else "未知错误"
            return f"❌ 图像生成失败: {error_msg}\n💡 建议：\n   - 检查描述是否清晰\n   - 尝试使用更简洁的描述\n   - 稍后重试"
            
    except Exception as e:
        return f"❌ 图像生成出错: {str(e)}\n💡 请稍后重试或联系技术支持。"

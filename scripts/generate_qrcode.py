"""
生成带标题的二维码
用于推广"灵值生态"品牌文化转译官智能体
"""
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, SquareModuleDrawer


def generate_qr_code_with_title(url, title, output_path="assets/lingzhi_qrcode.png"):
    """
    生成带标题的二维码
    
    Args:
        url: 二维码跳转链接（智能体分享链接）
        title: 二维码标题文字
        output_path: 输出文件路径
    """
    # 创建二维码
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # 生成图片（使用圆角样式）
    img = qr.make_image(
        fill_color="#E74C3C",  # 品牌主色（红色）
        back_color="white",
        image_factory=StyledPilImage,
        module_drawer=SquareModuleDrawer()
    )

    # 添加标题
    from PIL import Image, ImageDraw, ImageFont

    # 创建新画布（二维码下方留出标题空间）
    qr_width, qr_height = img.size
    new_height = qr_height + 80  # 标题区域高度
    new_img = Image.new('RGB', (qr_width, new_height), 'white')
    
    # 将二维码粘贴到新画布上
    new_img.paste(img, (0, 0))

    # 绘制标题
    draw = ImageDraw.Draw(new_img)
    
    # 尝试加载中文字体
    try:
        # 尝试使用常见的中文字体
        font = ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", 24)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 24)
        except:
            # 如果没有找到中文字体，使用默认字体（可能无法显示中文）
            font = ImageFont.load_default()
    
    # 计算标题位置（居中）
    text_bbox = draw.textbbox((0, 0), title, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_x = (qr_width - text_width) // 2
    text_y = qr_height + 25  # 二维码下方25像素
    
    # 绘制标题
    draw.text((text_x, text_y), title, fill="#2C3E50", font=font)
    
    # 保存图片
    new_img.save(output_path)
    print(f"✅ 二维码已生成: {output_path}")
    print(f"📝 标题: {title}")
    print(f"🔗 链接: {url}")


if __name__ == "__main__":
    # 灵值生态园智能体分享链接（发布到Coze后需要替换为真实链接）
    BOT_SHARE_URL = "https://www.coze.cn/store/bot/XXXXXXXX?from=qrcode"

    # 二维码标题（更新为灵值生态园）
    QR_TITLE = "灵值生态园 - 首席生态官"
    
    # 生成二维码
    generate_qr_code_with_title(
        url=BOT_SHARE_URL,
        title=QR_TITLE,
        output_path="assets/lingzhi_qrcode.png"
    )

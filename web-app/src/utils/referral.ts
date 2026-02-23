// 推荐码生成和验证工具
// 支持推荐码生成、验证、解析

// 推荐码配置
const REFERRAL_CONFIG = {
  CODE_LENGTH: 8,
  CODE_PREFIX: 'LZ',
  EXPIRE_DAYS: 365, // 推荐码有效期（天）
  MIN_CODE_LENGTH: 6,
  MAX_CODE_LENGTH: 10,
};

/**
 * 生成推荐码
 * @param userId 用户ID
 * @returns 推荐码
 */
export function generateReferralCode(userId: number): string {
  const timestamp = Date.now().toString(36);
  const randomPart = Math.random().toString(36).substring(2, 6);
  const userPart = userId.toString(36).toUpperCase();

  return `${REFERRAL_CONFIG.CODE_PREFIX}${userPart}${randomPart}${timestamp}`.toUpperCase();
}

/**
 * 生成推荐链接
 * @param referrerId 推荐人ID
 * @param baseUrl 基础URL（默认使用当前网站域名）
 * @returns 推荐链接
 */
export function generateReferralUrl(referrerId: number, baseUrl?: string): string {
  const referralCode = generateReferralCode(referrerId);
  
  // 如果未提供 baseUrl，使用当前网站的域名
  if (!baseUrl) {
    baseUrl = window.location.origin;
  }
  
  return `${baseUrl}/referral?code=${referralCode}`;
}

/**
 * 解析推荐码
 * @param referralCode 推荐码
 * @returns 推荐人ID和过期时间，如果无效返回null
 */
export function parseReferralCode(referralCode: string): { userId: number; createdAt: number } | null {
  try {
    // 验证推荐码格式
    if (!referralCode.startsWith(REFERRAL_CONFIG.CODE_PREFIX)) {
      return null;
    }

    // 去掉前缀
    const codeBody = referralCode.substring(REFERRAL_CONFIG.CODE_PREFIX.length);

    // 提取用户ID部分（前几个字符）
    const userIdStr = codeBody.substring(0, Math.min(8, codeBody.length));
    const userId = parseInt(userIdStr, 36);

    if (isNaN(userId) || userId <= 0) {
      return null;
    }

    // 从推荐码中提取时间戳
    const timestampStr = codeBody.substring(codeBody.length - 10);
    const timestamp = parseInt(timestampStr, 36);

    if (isNaN(timestamp)) {
      return null;
    }

    return {
      userId,
      createdAt: timestamp,
    };
  } catch (error) {
    console.error('解析推荐码失败:', error);
    return null;
  }
}

/**
 * 验证推荐码是否有效
 * @param referralCode 推荐码
 * @returns 是否有效
 */
export function validateReferralCode(referralCode: string): boolean {
  const parsed = parseReferralCode(referralCode);
  if (!parsed) {
    return false;
  }

  // 检查是否过期
  const now = Date.now();
  const expireTime = parsed.createdAt + REFERRAL_CONFIG.EXPIRE_DAYS * 24 * 60 * 60 * 1000;

  return now <= expireTime;
}

/**
 * 从URL中提取推荐码
 * @param url URL字符串
 * @returns 推荐码或null
 */
export function extractReferralCodeFromUrl(url: string): string | null {
  try {
    const urlObj = new URL(url);
    return urlObj.searchParams.get('code');
  } catch (error) {
    console.error('解析URL失败:', error);
    return null;
  }
}

/**
 * 生成短推荐码（用于分享）
 * @param userId 用户ID
 * @returns 短推荐码
 */
export function generateShortReferralCode(userId: number): string {
  const randomPart = Math.random().toString(36).substring(2, 8);
  const userPart = userId.toString(36).toUpperCase().substring(0, 4);

  return `${userPart}${randomPart}`.toUpperCase();
}

/**
 * 验证短推荐码（需要后端查询数据库）
 * @param shortCode 短推荐码
 * @returns 是否有效
 */
export function validateShortReferralCode(shortCode: string): boolean {
  if (!shortCode || shortCode.length < REFERRAL_CONFIG.MIN_CODE_LENGTH) {
    return false;
  }

  // 检查是否只包含字母和数字
  const codeRegex = /^[A-Z0-9]+$/;
  return codeRegex.test(shortCode);
}

/**
 * 生成分享文本
 * @param referralUrl 推荐链接
 * @param userName 用户名
 * @returns 分享文本
 */
export function generateShareText(referralUrl: string, userName?: string): string {
  const greeting = userName ? `我是 ${userName}，` : '';
  return `🎉 ${greeting}邀请您加入灵值生态园！

🌟 智能体APP - 用户旅程管理、经济模型计算、智能对话

📱 通过我的链接注册，成为我的推荐伙伴！

🔗 点击链接加入：${referralUrl}

✨ 期待您的到来！`;
}

/**
 * 生成分享标题
 * @returns 分享标题
 */
export function generateShareTitle(): string {
  return '🎉 邀请您加入灵值生态园';
}

/**
 * 生成分享描述
 * @param userName 用户名
 * @returns 分享描述
 */
export function generateShareDescription(userName?: string): string {
  const greeting = userName ? `${userName}邀请您加入灵值生态园！` : '邀请您加入灵值生态园！';
  return `${greeting} 智能体APP - 用户旅程管理、经济模型计算、智能对话`;
}

/**
 * 复制推荐链接到剪贴板
 * @param referralUrl 推荐链接
 * @returns 是否成功
 */
export async function copyReferralUrl(referralUrl: string): Promise<boolean> {
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(referralUrl);
      return true;
    }

    // 降级方案：使用传统方法
    const textArea = document.createElement('textarea');
    textArea.value = referralUrl;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    document.body.appendChild(textArea);
    textArea.select();
    const successful = document.execCommand('copy');
    document.body.removeChild(textArea);
    return successful;
  } catch (error) {
    console.error('复制失败:', error);
    return false;
  }
}

/**
 * 生成推荐二维码URL
 * @param referralUrl 推荐链接
 * @returns 二维码URL
 */
export function generateQrCodeUrl(referralUrl: string): string {
  const encodedUrl = encodeURIComponent(referralUrl);
  return `https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${encodedUrl}`;
}

/**
 * 检测推荐码是否过期
 * @param referralCode 推荐码
 * @returns 是否过期
 */
export function isReferralCodeExpired(referralCode: string): boolean {
  const parsed = parseReferralCode(referralCode);
  if (!parsed) {
    return true;
  }

  const now = Date.now();
  const expireTime = parsed.createdAt + REFERRAL_CONFIG.EXPIRE_DAYS * 24 * 60 * 60 * 1000;

  return now > expireTime;
}

/**
 * 获取推荐码剩余有效天数
 * @param referralCode 推荐码
 * @returns 剩余天数，如果已过期返回0
 */
export function getReferralCodeRemainingDays(referralCode: string): number {
  const parsed = parseReferralCode(referralCode);
  if (!parsed) {
    return 0;
  }

  const now = Date.now();
  const expireTime = parsed.createdAt + REFERRAL_CONFIG.EXPIRE_DAYS * 24 * 60 * 60 * 1000;
  const remainingMs = expireTime - now;

  return Math.max(0, Math.floor(remainingMs / (24 * 60 * 60 * 1000)));
}

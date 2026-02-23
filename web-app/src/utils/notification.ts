import { message, notification } from 'antd';

/**
 * 分享成功提示
 */
export const showShareSuccess = (platform: string) => {
  const platformNames: Record<string, string> = {
    wechat: '微信',
    weibo: '微博',
    qq: 'QQ',
    link: '链接',
  };

  notification.success({
    message: '分享成功',
    description: `成功分享到${platformNames[platform] || platform}`,
    duration: 3,
    placement: 'topRight',
  });
};

/**
 * 推荐关系绑定成功提示
 */
export const showReferralBindSuccess = (referrerName?: string) => {
  notification.success({
    message: '推荐关系绑定成功',
    description: referrerName 
      ? `已成功绑定到推荐人：${referrerName}`
      : '推荐关系绑定成功，您将享受推荐权益',
    duration: 5,
    placement: 'topRight',
  });
};

/**
 * 文章发布成功提示
 */
export const showArticlePublishSuccess = () => {
  message.success('文章发布成功');
};

/**
 * 文章审核通过提示
 */
export const showArticleApproved = (articleTitle: string) => {
  notification.success({
    message: '文章审核通过',
    description: `您的文章《${articleTitle}》已通过审核并发布`,
    duration: 5,
    placement: 'topRight',
  });
};

/**
 * 文章审核拒绝提示
 */
export const showArticleRejected = (articleTitle: string, reason: string) => {
  notification.error({
    message: '文章未通过审核',
    description: (
      <div>
        <p>您的文章《{articleTitle}》未通过审核</p>
        <p style={{ marginTop: 8, color: '#ff4d4f' }}>拒绝原因：{reason}</p>
      </div>
    ),
    duration: 10,
    placement: 'topRight',
  });
};

/**
 * 复制成功提示
 */
export const showCopySuccess = (text: string = '已复制到剪贴板') => {
  message.success(text);
};

/**
 * 加载失败提示
 */
export const showLoadError = (action: string) => {
  message.error(`${action}失败，请稍后重试`);
};

/**
 * 操作成功提示
 */
export const showSuccess = (action: string) => {
  message.success(`${action}成功`);
};

/**
 * 操作失败提示
 */
export const showError = (action: string, errorMsg?: string) => {
  message.error(errorMsg || `${action}失败`);
};

/**
 * 确认操作提示
 */
export const showConfirm = (content: string, onConfirm: () => void) => {
  notification.warning({
    message: '确认操作',
    description: content,
    duration: 0,
    placement: 'topRight',
    btn: (
      <div>
        <button
          onClick={() => {
            onConfirm();
            notification.destroy();
          }}
          style={{
            background: '#1890ff',
            color: 'white',
            border: 'none',
            padding: '6px 12px',
            borderRadius: 4,
            marginRight: 8,
            cursor: 'pointer',
          }}
        >
          确定
        </button>
        <button
          onClick={() => notification.destroy()}
          style={{
            background: '#fff',
            color: '#666',
            border: '1px solid #d9d9d9',
            padding: '6px 12px',
            borderRadius: 4,
            cursor: 'pointer',
          }}
        >
          取消
        </button>
      </div>
    ),
  });
};

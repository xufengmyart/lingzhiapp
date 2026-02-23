/**
 * 版本管理器
 *
 * 功能：
 * 1. 自动检测版本更新
 * 2. 发现新版本时自动刷新页面
 * 3. 处理 Service Worker 更新
 */

(function() {
  class VersionManager {
    constructor() {
      this.currentVersion = null;
      this.checkInterval = null;
      this.checkIntervalTime = 60000; // 每分钟检查一次
      this.init();
    }

    /**
     * 初始化
     */
    init() {
      // 获取当前版本
      this.getCurrentVersion().then(version => {
        this.currentVersion = version;
        console.log(`[版本管理] 初始化，当前版本: ${this.currentVersion}`);

        // 首次访问，保存版本
        if (!localStorage.getItem('app_version')) {
          localStorage.setItem('app_version', version);
          console.log('[版本管理] 首次访问，保存版本:', version);
        }

        // 检查版本是否一致
        const savedVersion = localStorage.getItem('app_version');
        if (savedVersion !== version) {
          console.log(`[版本管理] 版本不一致: ${savedVersion} -> ${version}`);
          this.handleVersionUpdate(version);
        } else {
          console.log('[版本管理] 版本一致，无需更新:', version);
        }

        // 开始定期检查
        this.startPeriodicCheck();
      });

      // 监听来自 Service Worker 的消息
      if ('serviceWorker' in navigator) {
        navigator.serviceWorker.addEventListener('message', this.handleSWMessage.bind(this));
      }

      // 监听页面可见性变化
      document.addEventListener('visibilitychange', this.handleVisibilityChange.bind(this));
    }

    /**
     * 获取当前版本
     */
    async getCurrentVersion() {
      try {
        const response = await fetch('/version.json?t=' + Date.now());
        const data = await response.json();
        return data.version;
      } catch (error) {
        console.error('[版本管理] 获取版本失败:', error);
        return localStorage.getItem('app_version') || 'unknown';
      }
    }

    /**
     * 开始定期检查
     */
    startPeriodicCheck() {
      if (this.checkInterval) {
        clearInterval(this.checkInterval);
      }

      this.checkInterval = setInterval(async () => {
        const newVersion = await this.getCurrentVersion();
        if (newVersion !== this.currentVersion) {
          console.log(`[版本管理] 发现新版本: ${this.currentVersion} -> ${newVersion}`);
          this.handleVersionUpdate(newVersion);
        }
      }, this.checkIntervalTime);

      console.log(`[版本管理] 开始定期检查，间隔: ${this.checkIntervalTime}ms`);
    }

    /**
     * 停止定期检查
     */
    stopPeriodicCheck() {
      if (this.checkInterval) {
        clearInterval(this.checkInterval);
        this.checkInterval = null;
      }
    }

    /**
     * 处理版本更新
     */
    handleVersionUpdate(newVersion) {
      console.log(`[版本管理] 版本更新: ${this.currentVersion} -> ${newVersion}`);

      // 更新本地版本
      localStorage.setItem('app_version', newVersion);
      this.currentVersion = newVersion;

      // 显示更新提示
      this.showUpdateNotification();

      // 延迟刷新页面
      setTimeout(() => {
        this.forceReload();
      }, 3000);
    }

    /**
     * 显示更新通知
     */
    showUpdateNotification() {
      // 创建通知元素
      const notification = document.createElement('div');
      notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 16px 24px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 999999;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        font-size: 14px;
        animation: slideIn 0.3s ease-out;
      `;
      notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 12px;">
          <div style="font-size: 20px;">🔄</div>
          <div>
            <div style="font-weight: 600; margin-bottom: 4px;">发现新版本</div>
            <div style="opacity: 0.9;">页面将在 3 秒后自动刷新...</div>
          </div>
        </div>
      `;

      // 添加动画
      const style = document.createElement('style');
      style.textContent = `
        @keyframes slideIn {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
      `;
      document.head.appendChild(style);

      document.body.appendChild(notification);

      // 5秒后移除通知
      setTimeout(() => {
        notification.style.animation = 'slideIn 0.3s ease-out reverse';
        setTimeout(() => notification.remove(), 300);
      }, 5000);
    }

    /**
     * 强制重新加载页面
     */
    forceReload() {
      console.log('[版本管理] 强制刷新页面');
      localStorage.setItem('app_version', this.currentVersion);
      window.location.reload(true);
    }

    /**
     * 处理 Service Worker 消息
     */
    handleSWMessage(event) {
      console.log('[版本管理] 收到 SW 消息:', event.data);

      if (event.data && event.data.type === 'NEW_VERSION_AVAILABLE') {
        this.handleVersionUpdate(event.data.version);
      }
    }

    /**
     * 处理页面可见性变化
     */
    handleVisibilityChange() {
      if (document.visibilityState === 'visible') {
        console.log('[版本管理] 页面重新可见，检查版本');
        this.getCurrentVersion().then(version => {
          if (version !== this.currentVersion) {
            console.log(`[版本管理] 页面可见时发现新版本: ${this.currentVersion} -> ${version}`);
            this.handleVersionUpdate(version);
          }
        });
      }
    }

    /**
     * 手动检查更新
     */
    async checkForUpdates() {
      console.log('[版本管理] 手动检查更新');
      const newVersion = await this.getCurrentVersion();

      if (newVersion !== this.currentVersion) {
        console.log(`[版本管理] 手动检查发现新版本: ${this.currentVersion} -> ${newVersion}`);
        this.handleVersionUpdate(newVersion);
        return true;
      }

      console.log('[版本管理] 手动检查，版本已是最新:', newVersion);
      return false;
    }
  }

  // 在页面加载时初始化
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      window.versionManager = new VersionManager();
    });
  } else {
    window.versionManager = new VersionManager();
  }
})();

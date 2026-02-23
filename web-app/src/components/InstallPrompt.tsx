import { useEffect, useState } from 'react'
import { X, Download } from 'lucide-react'

interface InstallPromptProps {
  onClose: () => void
  onInstall: () => void
}

const InstallPrompt = ({ onClose, onInstall }: InstallPromptProps) => {
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null)
  const [isIOS, setIsIOS] = useState(false)

  useEffect(() => {
    // 检测是否为 iOS 设备
    const isIOSDevice = /iPad|iPhone|iPod/.test(navigator.userAgent) || (/Macintosh/.test(navigator.userAgent) && 'ontouchend' in document)
    setIsIOS(isIOSDevice)

    // 监听 beforeinstallprompt 事件
    const handler = (e: Event) => {
      e.preventDefault()
      setDeferredPrompt(e)
    }

    window.addEventListener('beforeinstallprompt', handler)
    window.addEventListener('appinstalled', () => {
      setDeferredPrompt(null)
    })

    return () => {
      window.removeEventListener('beforeinstallprompt', handler)
      window.removeEventListener('appinstalled', () => {
        setDeferredPrompt(null)
      })
    }
  }, [])

  const handleInstallClick = async () => {
    if (deferredPrompt) {
      deferredPrompt.prompt()
      const { outcome } = await deferredPrompt.userChoice
      if (outcome === 'accepted') {
        onInstall()
      }
      setDeferredPrompt(null)
    }
  }

  if (isIOS) {
    return (
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-lg z-50 animate-slide-up">
        <div className="max-w-md mx-auto p-4">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center mb-2">
                <Download className="w-5 h-5 text-primary-600 mr-2" />
                <h3 className="font-bold text-gray-900">安装到主屏幕</h3>
              </div>
              <p className="text-sm text-gray-600">
                在 Safari 浏览器中，点击底部的<span className="font-bold text-primary-600">「分享」</span>按钮，
                然后选择<span className="font-bold text-primary-600">「添加到主屏幕」</span>
              </p>
            </div>
            <button
              onClick={onClose}
              className="ml-4 text-gray-400 hover:text-gray-600"
              aria-label="关闭"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (!deferredPrompt) {
    return null
  }

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-lg z-50 animate-slide-up">
      <div className="max-w-md mx-auto p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center flex-1">
            <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-xl flex items-center justify-center mr-4">
              <Download className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="font-bold text-gray-900">安装到主屏幕</h3>
              <p className="text-sm text-gray-600">离线访问，更佳体验</p>
            </div>
          </div>
          <div className="flex items-center space-x-2 ml-4">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 font-medium"
            >
              暂不安装
            </button>
            <button
              onClick={handleInstallClick}
              className="px-6 py-2 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-lg font-medium hover:from-primary-600 hover:to-secondary-600 flex items-center"
            >
              安装
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default InstallPrompt

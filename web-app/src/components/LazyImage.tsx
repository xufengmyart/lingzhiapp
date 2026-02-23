import { useState, useRef, useEffect } from 'react'

interface LazyImageProps {
  src: string
  alt: string
  className?: string
  placeholder?: string
  threshold?: number
  onLoad?: () => void
  onError?: () => void
}

/**
 * 图片懒加载组件
 * 使用 Intersection Observer API 实现高性能懒加载
 */
const LazyImage: React.FC<LazyImageProps> = ({
  src,
  alt,
  className = '',
  placeholder = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300"%3E%3Crect width="400" height="300" fill="%23f3f4f6"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" fill="%239ca3af"%3E加载中...%3C/text%3E%3C/svg%3E',
  threshold = 0.1,
  onLoad,
  onError
}) => {
  const [isLoaded, setIsLoaded] = useState(false)
  const [isInView, setIsInView] = useState(false)
  const [hasError, setHasError] = useState(false)
  const imgRef = useRef<HTMLImageElement>(null)
  const observerRef = useRef<IntersectionObserver | null>(null)

  useEffect(() => {
    // 设置 Intersection Observer
    observerRef.current = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsInView(true)
            // 图片进入视图后停止观察
            if (observerRef.current && imgRef.current) {
              observerRef.current.unobserve(imgRef.current)
            }
          }
        })
      },
      {
        threshold,
        rootMargin: '50px' // 提前50px开始加载
      }
    )

    // 开始观察图片元素
    if (imgRef.current) {
      observerRef.current.observe(imgRef.current)
    }

    // 清理函数
    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect()
      }
    }
  }, [threshold])

  const handleLoad = () => {
    setIsLoaded(true)
    if (onLoad) onLoad()
  }

  const handleError = () => {
    setHasError(true)
    if (onError) onError()
  }

  return (
    <div
      ref={imgRef}
      className={`lazy-image-wrapper ${className} ${isLoaded ? 'loaded' : 'loading'}`}
      style={{
        display: 'inline-block',
        overflow: 'hidden'
      }}
    >
      <img
        src={isInView ? src : placeholder}
        alt={alt}
        className={className}
        loading="lazy"
        onLoad={handleLoad}
        onError={handleError}
        style={{
          opacity: isLoaded ? 1 : 0,
          transition: 'opacity 0.3s ease-in-out',
          objectFit: 'cover'
        }}
      />
      {!isLoaded && !hasError && (
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: '#f3f4f6'
          }}
        >
          <div
            style={{
              width: '40px',
              height: '40px',
              border: '3px solid #e5e7eb',
              borderTopColor: '#6366f1',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite'
            }}
          />
        </div>
      )}
      {hasError && (
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: '#fef2f2',
            color: '#ef4444',
            fontSize: '14px'
          }}
        >
          图片加载失败
        </div>
      )}
      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
}

export default LazyImage

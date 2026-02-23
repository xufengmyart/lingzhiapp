/**
 * API响应缓存中间件
 * 支持内存缓存和本地存储缓存
 */

interface CacheConfig {
  key: string
  data: any
  timestamp: number
  ttl?: number // 过期时间（毫秒）
}

class ApiCache {
  private memoryCache: Map<string, CacheConfig> = new Map()
  private readonly defaultTTL = 5 * 60 * 1000 // 默认5分钟缓存

  /**
   * 生成缓存键
   */
  private generateKey(url: string, params?: any): string {
    const paramsStr = params ? JSON.stringify(params) : ''
    return `${url}?${paramsStr}`
  }

  /**
   * 设置缓存
   */
  set(key: string, data: any, ttl?: number): void {
    const cacheData: CacheConfig = {
      key,
      data,
      timestamp: Date.now(),
      ttl: ttl || this.defaultTTL
    }
    this.memoryCache.set(key, cacheData)
    
    // 同时保存到localStorage（仅限数据量小于1MB的）
    try {
      const dataSize = JSON.stringify(cacheData).length
      if (dataSize < 1024 * 1024) {
        localStorage.setItem(`api_cache_${key}`, JSON.stringify(cacheData))
      }
    } catch (e) {
      // localStorage空间不足或无法访问，忽略错误
      console.warn('Failed to save to localStorage:', e)
    }
  }

  /**
   * 获取缓存
   */
  get(url: string, params?: any): any | null {
    const key = this.generateKey(url, params)
    
    // 先从内存缓存获取
    let cacheData = this.memoryCache.get(key)
    
    // 如果内存缓存没有，尝试从localStorage获取
    if (!cacheData) {
      try {
        const stored = localStorage.getItem(`api_cache_${key}`)
        if (stored) {
          cacheData = JSON.parse(stored)
          // 恢复到内存缓存
          this.memoryCache.set(key, cacheData)
        }
      } catch (e) {
        console.warn('Failed to get from localStorage:', e)
      }
    }
    
    if (!cacheData) {
      return null
    }
    
    // 检查是否过期
    const now = Date.now()
    const cacheAge = now - cacheData.timestamp
    const ttl = cacheData.ttl || this.defaultTTL
    
    if (cacheAge > ttl) {
      this.delete(key)
      return null
    }
    
    return cacheData.data
  }

  /**
   * 删除缓存
   */
  delete(key: string): void {
    this.memoryCache.delete(key)
    try {
      localStorage.removeItem(`api_cache_${key}`)
    } catch (e) {
      console.warn('Failed to delete from localStorage:', e)
    }
  }

  /**
   * 清空所有缓存
   */
  clear(): void {
    this.memoryCache.clear()
    try {
      const keys = Object.keys(localStorage)
      keys.forEach(key => {
        if (key.startsWith('api_cache_')) {
          localStorage.removeItem(key)
        }
      })
    } catch (e) {
      console.warn('Failed to clear localStorage:', e)
    }
  }

  /**
   * 清理过期缓存
   */
  cleanup(): void {
    const now = Date.now()
    
    // 清理内存缓存
    this.memoryCache.forEach((cacheData, key) => {
      const cacheAge = now - cacheData.timestamp
      const ttl = cacheData.ttl || this.defaultTTL
      
      if (cacheAge > ttl) {
        this.delete(key)
      }
    })
    
    // 清理localStorage缓存
    try {
      const keys = Object.keys(localStorage)
      keys.forEach(key => {
        if (key.startsWith('api_cache_')) {
          try {
            const stored = localStorage.getItem(key)
            if (stored) {
              const cacheData = JSON.parse(stored) as CacheConfig
              const cacheAge = now - cacheData.timestamp
              const ttl = cacheData.ttl || this.defaultTTL
              
              if (cacheAge > ttl) {
                localStorage.removeItem(key)
              }
            }
          } catch (e) {
            // 忽略解析错误
          }
        }
      })
    } catch (e) {
      console.warn('Failed to cleanup localStorage:', e)
    }
  }

  /**
   * 获取缓存统计信息
   */
  getStats(): {
    memoryCount: number
    localStorageCount: number
    totalSize: number
  } {
    let localStorageCount = 0
    let totalSize = 0
    
    try {
      const keys = Object.keys(localStorage)
      keys.forEach(key => {
        if (key.startsWith('api_cache_')) {
          localStorageCount++
          try {
            const stored = localStorage.getItem(key)
            if (stored) {
              totalSize += stored.length
            }
          } catch (e) {
            // 忽略错误
          }
        }
      })
    } catch (e) {
      console.warn('Failed to get localStorage stats:', e)
    }
    
    return {
      memoryCount: this.memoryCache.size,
      localStorageCount,
      totalSize
    }
  }
}

// 创建全局缓存实例
const apiCache = new ApiCache()

// 定期清理过期缓存（每5分钟）
if (typeof window !== 'undefined') {
  setInterval(() => {
    apiCache.cleanup()
  }, 5 * 60 * 1000)
}

/**
 * 带缓存的API请求包装器
 */
export async function fetchWithCache(
  url: string,
  options?: RequestInit,
  config?: {
    cache?: boolean // 是否使用缓存，默认true
    ttl?: number // 缓存时间（毫秒）
    forceRefresh?: boolean // 强制刷新
  }
): Promise<any> {
  const {
    cache: useCache = true,
    ttl,
    forceRefresh = false
  } = config || {}

  const cacheKey = url

  // 如果不使用缓存或强制刷新，直接请求
  if (!useCache || forceRefresh) {
    const response = await fetch(url, options)
    const data = await response.json()
    
    // 保存到缓存
    if (useCache && response.ok) {
      apiCache.set(cacheKey, data, ttl)
    }
    
    return data
  }

  // 尝试从缓存获取
  const cachedData = apiCache.get(cacheKey)
  if (cachedData) {
    console.log(`[Cache Hit] ${url}`)
    return cachedData
  }

  console.log(`[Cache Miss] ${url}`)

  // 缓存未命中，发起请求
  const response = await fetch(url, options)
  const data = await response.json()

  // 保存到缓存
  if (response.ok) {
    apiCache.set(cacheKey, data, ttl)
  }

  return data
}

export default apiCache

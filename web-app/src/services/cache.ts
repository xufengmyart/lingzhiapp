// 请求缓存管理
type CacheEntry = {
  data: any
  timestamp: number
  expires: number
}

const CACHE_DURATION = 5 * 60 * 1000 // 5分钟缓存

class RequestCache {
  private cache: Map<string, CacheEntry> = new Map()

  set(key: string, data: any, duration: number = CACHE_DURATION): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      expires: Date.now() + duration,
    })
  }

  get(key: string): any | null {
    const entry = this.cache.get(key)
    if (!entry) return null

    if (Date.now() > entry.expires) {
      this.cache.delete(key)
      return null
    }

    return entry.data
  }

  delete(key: string): void {
    this.cache.delete(key)
  }

  clear(): void {
    this.cache.clear()
  }

  clearPattern(pattern: string): void {
    const regex = new RegExp(pattern)
    for (const key of this.cache.keys()) {
      if (regex.test(key)) {
        this.cache.delete(key)
      }
    }
  }
}

export const requestCache = new RequestCache()

// 生成缓存键
export function generateCacheKey(method: string, url: string, params?: any): string {
  const paramsStr = params ? JSON.stringify(params) : ''
  return `${method}:${url}:${paramsStr}`
}

// 清除特定类型的缓存
export function clearAuthCache(): void {
  requestCache.clearPattern('^GET:/api/user')
  requestCache.clearPattern('^GET:/checkin')
}

// 清除签到相关缓存
export function clearCheckInCache(): void {
  requestCache.clearPattern('/checkin')
}

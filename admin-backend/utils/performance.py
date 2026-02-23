# -*- coding: utf-8 -*-
"""
性能优化模块
包含缓存机制、数据库查询优化、异步处理
"""

import time
import json
import threading
from functools import wraps
from typing import Optional, Callable, Any
import hashlib
from collections import defaultdict

# ==================== 缓存机制 ====================

class SimpleCache:
    """简单缓存实现"""
    
    def __init__(self, default_ttl: int = 300):
        self._cache: dict = {}
        self._expiry: dict = {}
        self._lock = threading.RLock()
        self.default_ttl = default_ttl
        
        # 启动清理线程
        self._start_cleanup_thread()
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        with self._lock:
            if key not in self._cache:
                return None
            
            if time.time() > self._expiry[key]:
                del self._cache[key]
                del self._expiry[key]
                return None
            
            return self._cache[key]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """设置缓存"""
        with self._lock:
            ttl = ttl or self.default_ttl
            self._cache[key] = value
            self._expiry[key] = time.time() + ttl
    
    def delete(self, key: str) -> None:
        """删除缓存"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                del self._expiry[key]
    
    def clear(self) -> None:
        """清空所有缓存"""
        with self._lock:
            self._cache.clear()
            self._expiry.clear()
    
    def _start_cleanup_thread(self):
        """启动清理过期缓存的线程"""
        def cleanup():
            while True:
                time.sleep(60)  # 每分钟清理一次
                self._cleanup_expired()
        
        thread = threading.Thread(target=cleanup, daemon=True)
        thread.start()
    
    def _cleanup_expired(self):
        """清理过期缓存"""
        with self._lock:
            now = time.time()
            expired_keys = [
                key for key, expiry in self._expiry.items()
                if expiry <= now
            ]
            for key in expired_keys:
                del self._cache[key]
                del self._expiry[key]

# 全局缓存实例
_cache = SimpleCache()

def cache_decorator(ttl: int = 300, key_prefix: str = ""):
    """缓存装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            key_parts = [key_prefix, func.__name__, str(args), str(kwargs)]
            cache_key = hashlib.md5(json.dumps(key_parts).encode()).hexdigest()
            
            # 尝试从缓存获取
            cached_result = _cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 缓存结果
            _cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

def invalidate_cache(key_prefix: str) -> None:
    """使缓存失效"""
    # 简化版本：清空所有缓存
    # 生产环境应该更精确地匹配key
    _cache.clear()

# ==================== 数据库查询优化 ====================

class QueryOptimizer:
    """数据库查询优化器"""
    
    def __init__(self, connection):
        self.connection = connection
        self._query_cache: dict = {}
        self._query_stats: dict = defaultdict(int)
    
    def execute_with_cache(self, query: str, params: tuple = (), ttl: int = 60):
        """带缓存的查询执行"""
        cache_key = hashlib.md5((query + str(params)).encode()).hexdigest()
        
        # 尝试从缓存获取
        if cache_key in self._query_cache:
            cached_data, cached_time = self._query_cache[cache_key]
            if time.time() - cached_time < ttl:
                return cached_data
        
        # 执行查询
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        
        # 缓存结果
        self._query_cache[cache_key] = (result, time.time())
        self._query_stats[query] += 1
        
        return result
    
    def get_slow_queries(self, threshold: int = 100) -> list:
        """获取慢查询（执行次数超过阈值的查询）"""
        return [
            (query, count) for query, count in self._query_stats.items()
            if count > threshold
        ]
    
    def optimize_query(self, query: str) -> str:
        """优化查询语句"""
        # 简化版本的查询优化
        
        # 1. 检查是否使用了索引
        if "WHERE" in query and "ORDER BY" in query:
            # 如果查询同时有 WHERE 和 ORDER BY，建议添加复合索引
            pass
        
        # 2. 检查是否使用了 SELECT *
        if "SELECT *" in query:
            # 建议明确指定列名
            pass
        
        # 3. 检查是否有 JOIN 操作
        if "JOIN" in query:
            # 确保 JOIN 字段有索引
            pass
        
        return query

# ==================== 异步任务队列 ====================

import queue
import threading
from typing import Callable

class AsyncTaskQueue:
    """异步任务队列"""
    
    def __init__(self, max_workers: int = 5):
        self._queue = queue.Queue()
        self._workers = []
        self._stop_event = threading.Event()
        
        # 创建工作线程
        for _ in range(max_workers):
            worker = threading.Thread(target=self._worker, daemon=True)
            worker.start()
            self._workers.append(worker)
    
    def _worker(self):
        """工作线程"""
        while not self._stop_event.is_set():
            try:
                task = self._queue.get(timeout=1)
                if task is None:
                    break
                
                func, args, kwargs, callback = task
                try:
                    result = func(*args, **kwargs)
                    if callback:
                        callback(result)
                except Exception as e:
                    if callback:
                        callback(None, error=str(e))
                
                self._queue.task_done()
            except queue.Empty:
                continue
    
    def add_task(self, func: Callable, args: tuple = (), kwargs: dict = None, 
                 callback: Callable = None) -> None:
        """添加任务到队列"""
        kwargs = kwargs or {}
        self._queue.put((func, args, kwargs, callback))
    
    def wait_completion(self) -> None:
        """等待所有任务完成"""
        self._queue.join()
    
    def stop(self) -> None:
        """停止队列"""
        self._stop_event.set()
        for _ in self._workers:
            self._queue.put(None)

# 全局任务队列实例
_task_queue = AsyncTaskQueue()

def async_task(callback: Callable = None):
    """异步任务装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            _task_queue.add_task(func, args, kwargs, callback)
        return wrapper
    return decorator

# ==================== 性能监控 ====================

class PerformanceMonitor:
    """性能监控"""
    
    def __init__(self):
        self._metrics: dict = defaultdict(list)
        self._lock = threading.Lock()
    
    def record(self, name: str, value: float) -> None:
        """记录性能指标"""
        with self._lock:
            self._metrics[name].append(value)
            
            # 只保留最近1000条记录
            if len(self._metrics[name]) > 1000:
                self._metrics[name] = self._metrics[name][-1000:]
    
    def get_stats(self, name: str) -> dict:
        """获取统计信息"""
        with self._lock:
            if name not in self._metrics or not self._metrics[name]:
                return {}
            
            values = self._metrics[name]
            return {
                'count': len(values),
                'min': min(values),
                'max': max(values),
                'avg': sum(values) / len(values),
                'median': sorted(values)[len(values) // 2]
            }
    
    def get_all_stats(self) -> dict:
        """获取所有统计信息"""
        with self._lock:
            return {name: self.get_stats(name) for name in self._metrics.keys()}

# 全局性能监控实例
_perf_monitor = PerformanceMonitor()

def performance_monitor(name: str):
    """性能监控装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                elapsed_time = time.time() - start_time
                _perf_monitor.record(name, elapsed_time)
        return wrapper
    return decorator

# ==================== 导出接口 ====================

__all__ = [
    'SimpleCache',
    'cache_decorator',
    'invalidate_cache',
    'QueryOptimizer',
    'AsyncTaskQueue',
    'async_task',
    'PerformanceMonitor',
    'performance_monitor',
]

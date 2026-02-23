"""
数据库连接管理器
使用单例模式和连接池管理，避免SQLite数据库锁定问题
"""
import sqlite3
import threading
import time
from contextlib import contextmanager
from config import config  # 导入config实例
import os

# 全局连接锁
_db_lock = threading.Lock()
_connections = {}

class DatabaseManager:
    """数据库管理器 - 单例模式"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化数据库管理器"""
        self.db_path = config.DATABASE_PATH  # 使用config实例
        self.timeout = 30  # 30秒超时
        self.retries = 3  # 重试3次
        self.retry_delay = 1  # 每次重试间隔1秒
        
        # 确保数据库目录存在
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
    
    def get_connection(self):
        """获取数据库连接（带重试机制）"""
        for attempt in range(self.retries):
            try:
                # 使用WAL模式，减少锁定
                print(f"[DB_MANAGER] 尝试连接数据库 (第{attempt + 1}次)...")
                conn = sqlite3.connect(
                    self.db_path,
                    timeout=self.timeout,
                    isolation_level=None,  # 自动提交模式
                    check_same_thread=False  # 允许跨线程使用
                )
                
                # 禁用WAL模式（避免并发问题）
                conn.execute('PRAGMA journal_mode=DELETE')
                conn.execute('PRAGMA synchronous=FULL')
                conn.execute('PRAGMA busy_timeout=30000')  # 30秒超时
                conn.execute('PRAGMA cache_size=10000')  # 增加缓存
                conn.execute('PRAGMA temp_store=MEMORY')  # 临时表存储在内存
                
                conn.row_factory = sqlite3.Row
                print(f"[DB_MANAGER] 数据库连接成功")
                return conn
                
            except sqlite3.OperationalError as e:
                print(f"[DB_MANAGER] 连接失败: {e}")
                if "database is locked" in str(e) and attempt < self.retries - 1:
                    print(f"[DB_MANAGER] 数据库锁定，第{attempt + 1}次重试...")
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    print(f"[DB_MANAGER] 数据库连接失败（已重试{self.retries}次）")
                    raise
    
    @contextmanager
    def get_connection_context(self):
        """上下文管理器，自动关闭连接"""
        conn = self.get_connection()
        try:
            yield conn
        finally:
            conn.close()
    
    def cleanup_locks(self):
        """清理数据库锁定文件"""
        db_dir = os.path.dirname(self.db_path)
        if os.path.exists(db_dir):
            for pattern in ['-wal', '-shm', '-journal', '.lock']:
                lock_file = self.db_path + pattern
                if os.path.exists(lock_file):
                    try:
                        os.remove(lock_file)
                        print(f"✅ 已删除锁定文件: {lock_file}")
                    except Exception as e:
                        print(f"⚠️  无法删除锁定文件 {lock_file}: {e}")


# 全局数据库管理器实例
db_manager = DatabaseManager()

# 便捷函数
def get_db():
    """获取数据库连接"""
    return db_manager.get_connection()

@contextmanager
def get_db_context():
    """获取数据库连接（上下文管理器）"""
    with db_manager.get_connection_context() as conn:
        yield conn

def cleanup_db_locks():
    """清理数据库锁定文件"""
    db_manager.cleanup_locks()


if __name__ == '__main__':
    # 测试数据库连接
    print("测试数据库连接...")
    try:
        with get_db_context() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"✅ 数据库连接测试成功: {result}")
    except Exception as e:
        print(f"❌ 数据库连接测试失败: {e}")
        print("尝试清理锁定文件...")
        cleanup_db_locks()

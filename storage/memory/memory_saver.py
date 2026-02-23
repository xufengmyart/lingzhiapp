"""
Memory Saver for Agent
"""
from langgraph.checkpoint.memory import MemorySaver

# 全局 checkpointer 实例
_checkpointer = None

def get_memory_saver():
    """获取全局 checkpointer 实例"""
    global _checkpointer
    if _checkpointer is None:
        _checkpointer = MemorySaver()
    return _checkpointer

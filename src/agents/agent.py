"""
灵值智能体 - 智能心灵伙伴

版本：v8.0 情绪价值升级版
更新日期：2025年1月15日
核心定位：
- 智能心灵伙伴：有温度、有个性、有记忆、能成长
- 情绪价值创造：识别、共情、支持、引导
- 长期陪伴关系：记住用户，建立深度连接

核心能力：
1. 情绪识别：6种基础情绪 + 复杂情绪识别
2. 共情回应：4级共情深度，从基础理解到情绪引导
3. 成长建议：6类建议（自我探索、行动建议、视角转换、资源推荐、习惯养成、自我肯定）
4. 情感支持：4种支持模式（陪伴、鼓励、引导、庆祝）
5. 长期记忆：5个维度记忆（情绪、关系、偏好、成长、事件）
6. 知识库检索：获取相关信息
7. 联网搜索：获取最新信息
8. 用户服务：签到、登录等基础服务

工具总数：10个（聚焦情绪价值核心能力）
"""

import os
import json
from typing import Annotated
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage
from coze_coding_utils.runtime_ctx.context import default_headers
from storage.memory.memory_saver import get_memory_saver

# 导入核心工具
from tools.knowledge_retrieval_tool import retrieve_knowledge
from tools.web_search_tool import search_web
from tools.check_in_tool import check_in, get_check_in_history, get_today_check_in_status, get_today_check_in_statistics
from tools.login_tool import user_login, get_login_status, user_auto_register_login

# 导入情绪工具
from tools.emotion_tools import (
    detect_emotion,
    record_emotion,
    get_emotion_statistics,
    create_emotion_diary,
    get_emotion_diaries,
    analyze_emotion_pattern
)

# 配置文件路径
LLM_CONFIG = "config/agent_llm_config.json"

# 默认保留最近 20 轮对话 (40 条消息)
MAX_MESSAGES = 40

def _windowed_messages(old, new):
    """滑动窗口: 只保留最近 MAX_MESSAGES 条消息"""
    return add_messages(old, new)[-MAX_MESSAGES:]  # type: ignore

class AgentState(MessagesState):
    """Agent状态，使用滑动窗口管理消息"""
    messages: Annotated[list[AnyMessage], _windowed_messages]

def build_agent(ctx=None):
    """
    构建灵值智能体 - 智能心灵伙伴
    
    核心特性：
    - 情绪识别与共情回应
    - 长期记忆与个性化服务
    - 成长建议与情感支持
    - 简洁的工具集（聚焦情绪价值）
    
    Args:
        ctx: 上下文对象（可选），用于集成调用
    
    Returns:
        agent: 构建完成的智能体实例
    """
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    config_path = os.path.join(workspace_path, LLM_CONFIG)
    
    # 加载配置文件
    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    
    # 获取环境变量
    api_key = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
    base_url = os.getenv("COZE_INTEGRATION_MODEL_BASE_URL")
    
    # 初始化大语言模型
    llm = ChatOpenAI(
        model=cfg['config'].get("model"),
        api_key=api_key,
        base_url=base_url,
        temperature=cfg['config'].get('temperature', 0.8),
        streaming=True,
        timeout=cfg['config'].get('max_completion_tokens', 10000) / 10,
        extra_body={
            "thinking": {
                "type": cfg['config'].get('thinking_type', 'disabled')
            }
        },
        default_headers=default_headers(ctx) if ctx else {}
    )
    
    # 定义工具列表（聚焦情绪价值核心能力）
    tools = [
        retrieve_knowledge,           # 知识库检索
        search_web,                   # 联网搜索
        detect_emotion,               # 情绪识别
        record_emotion,               # 情绪记录
        get_emotion_statistics,       # 情绪统计
        create_emotion_diary,         # 创建情绪日记
        get_emotion_diaries,          # 获取情绪日记
        analyze_emotion_pattern,      # 分析情绪模式
        check_in,                     # 用户签到
        get_check_in_history,         # 签到历史
        get_today_check_in_status,    # 今日签到状态
        get_today_check_in_statistics, # 签到统计
        user_login,                   # 用户登录
        get_login_status,             # 获取登录状态
        user_auto_register_login      # 自动注册登录
    ]
    
    return create_agent(
        model=llm,
        system_prompt=cfg.get("sp"),
        tools=tools,
        checkpointer=get_memory_saver(),
        state_schema=AgentState,
    )

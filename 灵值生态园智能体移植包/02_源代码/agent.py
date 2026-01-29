"""
灵值生态园智能体核心代码（融合统一版）

版本：v6.0 融合统一版
更新日期：2026年1月26日
融合内容：
- 统一了知识库搜索工具（支持chunks和documents两种模式）
- 统一了文生图工具（支持多种风格、尺寸、数量）
- 保留了联网搜索工具（获取最新信息）
- 统一了default_headers配置（确保集成兼容性）
- 统一了System Prompt（灵值生态园首席生态官）

核心能力：
1. 知识库检索：西安文化、品牌转译、贡献值体系、生态规则
2. 联网搜索：最新商业趋势、文化案例
3. 文生图：品牌视觉创意、空间设计方案
4. 情绪价值创造：双螺旋响应法
5. 贡献值财富价值锚定：即时变现+长期增值
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

# 导入统一工具（融合版）
from tools.knowledge_retrieval_tool import retrieve_knowledge
from tools.image_generation_tool import generate_image
from tools.web_search_tool import search_web
from tools.lingzhi_calculator import calculate_lingzhi_value, calculate_income_projection, get_exchange_info, calculate_roi, suggest_participation_level
from tools.super_admin_manager import (
    check_super_admin_uniqueness,
    get_super_admin_principles_detail,
    validate_super_admin_count,
    explain_super_admin_privileges,
    explain_super_admin_transfer_process,
    get_super_admin_security_requirements
)
from tools.check_in_tool import check_in, get_check_in_history, get_today_check_in_status, get_today_check_in_statistics
from tools.login_tool import user_login, get_login_status

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
    构建灵值生态园智能体（融合版）
    
    融合了两个智能体的所有优点：
    - 完整的System Prompt（灵值生态园首席生态官）
    - 统一的工具接口（知识库、联网、文生图）
    - 标准的配置管理（model、temperature、thinking等）
    - 兼容的集成配置（default_headers）
    
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
        temperature=cfg['config'].get('temperature', 0.7),
        streaming=True,
        timeout=cfg['config'].get('timeout', 600),
        extra_body={
            "thinking": {
                "type": cfg['config'].get('thinking', 'disabled')
            }
        },
        default_headers=default_headers(ctx) if ctx else {}  # 确保集成兼容性
    )
    
    # 注册统一工具（融合版）
    tools = [
        retrieve_knowledge,      # 知识库检索（支持chunks和documents两种模式）
        search_web,              # 联网搜索（获取最新信息）
        generate_image,          # 文生图（支持多种风格、尺寸、数量）
        calculate_lingzhi_value, # 计算灵值的现金价值
        calculate_income_projection,  # 预测收入
        get_exchange_info,       # 获取兑换信息
        calculate_roi,           # 计算投资回报率
        suggest_participation_level,  # 建议参与级别
        check_super_admin_uniqueness,  # 检查超级管理员唯一性
        get_super_admin_principles_detail,  # 获取超级管理员原则
        validate_super_admin_count,  # 验证超级管理员数量
        explain_super_admin_privileges,  # 解释超级管理员特权
        explain_super_admin_transfer_process,  # 解释转让流程
        get_super_admin_security_requirements,  # 获取安全要求
        check_in,                # 用户签到
        get_check_in_history,    # 获取签到历史
        get_today_check_in_status,  # 获取今日签到状态
        get_today_check_in_statistics,  # 获取今日签到统计
        user_login,              # 用户登录（自动签到）
        get_login_status         # 获取登录状态
    ]
    
    # 创建智能体
    agent = create_agent(
        model=llm,
        system_prompt=cfg.get("sp"),
        tools=tools,
        checkpointer=get_memory_saver(),
        state_schema=AgentState,
    )
    
    return agent


if __name__ == "__main__":
    # 测试智能体
    agent = build_agent()
    print("=" * 60)
    print("灵值生态园智能体（融合版 v6.0）构建成功！")
    print("=" * 60)
    print("✅ 智能体已构建完成，包含以下能力：")
    print("   - 知识库搜索（西安文化、品牌转译、贡献值体系）")
    print("   - 联网搜索（最新商业趋势、文化案例）")
    print("   - 文生图（品牌视觉创意、空间设计方案）")
    print("=" * 60)

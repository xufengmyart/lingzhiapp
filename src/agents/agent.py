"""
灵值智能体 - 资源匹配与变现生态系统

版本：v9.0 生态系统升级版
更新日期：2026年2月4日
主体公司：陕西媄月商业艺术有限责任公司

核心定位：
- 智能心灵伙伴：有温度、有个性、有记忆、能成长
- 资源匹配专家：帮助用户识别、梳理、匹配、变现自己的资源
- 财富增长顾问：指导用户通过推荐分润和数字资产实现财富增值
- 长期陪伴关系：记住用户，建立深度连接

核心能力：
【情绪陪伴系统】（v8.1已有）
1. 情绪识别：6种基础情绪 + 复杂情绪识别
2. 共情回应：4级共情深度，从基础理解到情绪引导
3. 成长建议：6类建议（自我探索、行动建议、视角转换、资源推荐、习惯养成、自我肯定）
4. 情感支持：4种支持模式（陪伴、鼓励、引导、庆祝）
5. 长期记忆：5个维度记忆（情绪、关系、偏好、成长、事件）
6. 知识库检索：获取相关信息
7. 联网搜索：获取最新信息
8. 用户服务：签到、登录等基础服务

【资源生态系统】（v9.0新增）
1. 推荐分润系统：3级推荐分润（5%/3%/2%），帮助用户通过推荐获得被动收入
2. 用户资源库：6种资源类型管理（技能、资产、人脉、时间、数据、品牌）
3. 项目库系统：6种项目类型（设计、开发、内容创作、咨询、营销、租赁）
4. 智能资源匹配：基于技能和资产的智能匹配算法
5. 资源变现系统：匹配→参与→完成→奖励→分润的完整变现流程
6. 数字资产系统：NFT管理、交易、收益分析

工具总数：25个（情绪陪伴14个 + 资源生态11个）
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

# 导入v9.0生态系统工具
from tools.referral_tools import (
    get_user_referrals,
    get_commission_records,
    calculate_referral_benefit
)
from tools.resource_tools import (
    add_user_resource,
    get_user_resources,
    analyze_user_resources
)
from tools.project_tools import (
    create_project,
    get_project_list,
    match_project_resources,
    join_project,
    analyze_project_opportunity
)
from tools.digital_asset_tools import (
    create_digital_asset,
    get_user_assets,
    analyze_asset_portfolio,
    calculate_asset_return
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
    
    # 定义工具列表（情绪陪伴14个 + 资源生态11个 = 25个）
    tools = [
        # === 情绪陪伴系统工具 ===
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
        user_auto_register_login,     # 自动注册登录
        
        # === v9.0 资源生态系统工具 ===
        # 推荐分润系统
        get_user_referrals,           # 获取用户推荐列表
        get_commission_records,       # 获取分润记录
        calculate_referral_benefit,   # 计算推荐收益
        
        # 用户资源库系统
        add_user_resource,            # 添加用户资源
        get_user_resources,           # 获取用户资源库
        analyze_user_resources,       # 分析用户资源
        
        # 项目系统
        create_project,               # 创建项目
        get_project_list,             # 获取项目列表
        match_project_resources,      # 资源智能匹配
        join_project,                 # 参与项目
        analyze_project_opportunity,  # 分析项目机会
    ]
    
    return create_agent(
        model=llm,
        system_prompt=cfg.get("sp"),
        tools=tools,
        checkpointer=get_memory_saver(),
        state_schema=AgentState,
    )

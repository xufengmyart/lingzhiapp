"""
灵值生态园智能体核心代码（融合统一版）

版本：v7.2 双智能体完全融合版
更新日期：2026年1月28日
融合内容：
- 融合灵值生态园-开发智能体和灵值生态园智能体
- 融合两个配置文件的优势（用户旅程引导系统 + 完整工具集）
- 统一了知识库搜索工具（支持chunks和documents两种模式）
- 统一了文生图工具（支持多种风格、尺寸、数量）
- 保留了联网搜索工具（获取最新信息）
- 统一了default_headers配置（确保集成兼容性）
- 统一了System Prompt（灵值生态园首席生态官）
- 新增：经济模型配置和工具（6个）
- 新增：用户旅程管理工具（5个）
- 新增：合伙人管理工具（5个）
- 新增：安全框架工具（5个）
- 新增：用户旅程引导系统（7个阶段详细引导）

核心能力：
1. 知识库检索：西安文化、品牌转译、贡献值体系、生态规则
2. 联网搜索：最新商业趋势、文化案例
3. 文生图：品牌视觉创意、空间设计方案
4. 情绪价值创造：双螺旋响应法
5. 贡献值财富价值锚定：即时变现+长期增值
6. 经济模型计算：基于统一经济模型的价值计算和预测
7. 用户旅程管理：7阶段用户旅程引导和追踪
8. 合伙人管理：合伙人资格、申请、权益管理
9. 安全防护：SQL注入防护、输入验证、权限控制、审计日志

工具总数：85个
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
from tools.super_admin_manager_enhanced import (
    prevent_super_admin_operation,
    transfer_super_admin
)
from tools.check_in_tool import check_in, get_check_in_history, get_today_check_in_status, get_today_check_in_statistics
from tools.login_tool import user_login, get_login_status, user_auto_register_login
from tools.password_change_tool import change_password, force_change_user_password
from tools.user_registration_tool import (
    get_real_name_authentication_notice,
    validate_id_card,
    submit_real_name_authentication
)
from tools.payment_method_tool import (
    get_payment_method_notice,
    validate_payment_method,
    submit_payment_method,
    get_user_payment_method
)
from tools.financial_management_tool import (
    get_company_info,
    submit_withdrawal_request,
    approve_withdrawal_request,
    get_withdrawal_requests,
    get_financial_report
)
from tools.today_statistics_tool import (
    get_today_registration_count,
    get_today_active_users,
    get_platform_statistics
)
from tools.security_tools import (
    financial_security_check,
    comprehensive_security_check,
    detect_abnormal_operation,
    check_permission
)
from tools.lingzhi_security_tools import (
    validate_lingzhi_gain,
    record_lingzhi_gain,
    get_lingzhi_gain_rules,
    check_lingzhi_security
)
from tools.shortcut_tools import (
    create_shortcut_guide,
    create_desktop_shortcut_file,
    generate_qr_code_info
)
from tools.user_query_tools import (
    get_all_users,
    get_user_by_id,
    search_users
)
from tools.database_tools import (
    test_database_connection,
    get_database_status,
    get_user_statistics,
    get_table_structure,
    execute_sql_query
)
from tools.data_sync_tools import (
    export_users_to_csv,
    import_users_from_csv,
    export_users_to_json,
    import_users_from_json,
    create_test_users,
    delete_test_users,
    get_data_sync_guide
)
from tools.user_journey_tool import (
    get_user_journey_stage,
    update_user_journey_progress,
    get_journey_recommended_path,
    get_journey_milestone,
    get_new_user_guide
)
from tools.partner_tool import (
    check_partner_qualification,
    submit_partner_application,
    get_partner_application_status,
    get_partner_privileges,
    get_partner_development_guide
)
from tools.economic_model_tool import (
    get_economic_model_info,
    calculate_lingzhi_value_advanced,
    get_income_projection_advanced,
    get_exchange_info_advanced,
    get_new_user_bonus_info,
    compare_investment_options
)

# 导入安全框架工具
from tools.secure_database_tool import (
    execute_sql_query,
    get_table_schema,
    get_data_statistics,
    batch_execute_sql,
    build_safe_query
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
                "type": cfg['config'].get('thinking_type', 'disabled'),
                "reasoning_effort": cfg['config'].get('reasoning_effort', 'medium')
            }
        },
        default_headers=default_headers(ctx) if ctx else {}  # 确保集成兼容性
    )
    
    # 注册统一工具（融合版 + 安全增强）
    tools = [
        # ========== 安全框架工具（新增） ==========
        execute_sql_query,       # 安全SQL查询（防止注入）
        get_table_schema,        # 获取表结构（安全版）
        get_data_statistics,     # 获取数据统计
        batch_execute_sql,       # 批量安全查询
        build_safe_query,        # 安全查询构建器

        # ========== 原有工具（融合版） ==========
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
        prevent_super_admin_operation,  # 防止超级管理员禁止操作
        transfer_super_admin,     # 转让超级管理员
        check_in,                # 用户签到
        get_check_in_history,    # 获取签到历史
        get_today_check_in_status,  # 获取今日签到状态
        get_today_check_in_statistics,  # 获取今日签到统计
        user_login,              # 用户登录（自动签到）
        get_login_status,        # 获取登录状态
        user_auto_register_login,  # 用户自动注册并登录
        change_password,         # 修改密码
        force_change_user_password,  # 强制修改用户密码（超级管理员）
        get_real_name_authentication_notice,  # 获取实名认证通知
        validate_id_card,        # 验证身份证号码
        submit_real_name_authentication,  # 提交实名认证
        get_payment_method_notice,  # 获取收款方式通知
        validate_payment_method,  # 验证收款方式
        submit_payment_method,    # 提交收款方式
        get_user_payment_method,  # 获取用户收款方式信息
        get_company_info,         # 获取公司信息
        submit_withdrawal_request,  # 提交提现申请
        approve_withdrawal_request,  # 审核提现申请
        get_withdrawal_requests,    # 获取提现申请列表
        get_financial_report,       # 获取财务报表
        get_today_registration_count,  # 获取今日注册用户数量
        get_today_active_users,    # 获取今日活跃用户数量
        get_platform_statistics,   # 获取平台综合统计
        financial_security_check,  # 财务安全检查
        comprehensive_security_check,  # 综合安全检查
        detect_abnormal_operation,  # 异常操作检测
        check_permission,         # 权限检查
        create_shortcut_guide,    # 创建快捷方式指南
        create_desktop_shortcut_file,  # 创建桌面快捷方式文件
        generate_qr_code_info,    # 生成二维码保存建议
        get_all_users,            # 获取所有用户信息
        get_user_by_id,           # 根据ID获取用户信息
        search_users,             # 搜索用户
        test_database_connection, # 测试数据库连接
        get_database_status,      # 获取数据库状态
        get_user_statistics,      # 获取用户统计
        get_table_structure,      # 获取表结构
        execute_sql_query,        # 执行SQL查询
        export_users_to_csv,      # 导出用户到CSV
        import_users_from_csv,    # 从CSV导入用户
        export_users_to_json,     # 导出用户到JSON
        import_users_from_json,   # 从JSON导入用户
        create_test_users,        # 创建测试用户
        delete_test_users,        # 删除测试用户
        get_data_sync_guide,      # 获取数据同步指南
        validate_lingzhi_gain,    # 验证灵值获取
        record_lingzhi_gain,      # 记录灵值获取
        get_lingzhi_gain_rules,   # 获取灵值获取规则
        check_lingzhi_security,   # 检查灵值安全
        get_user_journey_stage,   # 获取用户旅程阶段
        update_user_journey_progress,  # 更新用户旅程进度
        get_journey_recommended_path,  # 获取推荐路径
        get_journey_milestone,    # 获取用户里程碑
        get_new_user_guide,       # 获取新用户引导指南
        check_partner_qualification,  # 检查合伙人资格
        submit_partner_application,  # 提交合伙人申请
        get_partner_application_status,  # 获取合伙人申请状态
        get_partner_privileges,   # 获取合伙人权益
        get_partner_development_guide,  # 获取合伙人发展指南
        get_economic_model_info,  # 获取经济模型核心信息
        calculate_lingzhi_value_advanced,  # 高级灵值价值计算
        get_income_projection_advanced,  # 高级收入预测
        get_exchange_info_advanced,  # 高级兑换信息
        get_new_user_bonus_info,  # 新用户权益信息
        compare_investment_options  # 投资选项比较
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
    print("灵值生态园智能体（融合版 v7.0）构建成功！")
    print("=" * 60)
    print("✅ 智能体已构建完成，包含以下能力：")
    print("   - 知识库搜索（西安文化、品牌转译、贡献值体系）")
    print("   - 联网搜索（最新商业趋势、文化案例）")
    print("   - 文生图（品牌视觉创意、空间设计方案）")
    print("   - 经济模型（价值计算、收入预测、投资分析）")
    print("   - 用户旅程（7阶段引导、里程碑追踪）")
    print("   - 合伙人管理（资格验证、申请流程、权益管理）")
    print("=" * 60)

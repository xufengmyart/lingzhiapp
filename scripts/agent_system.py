#!/usr/bin/env python3
"""
智能体系统架构和实现
集成 LangChain 实现智能对话、多模态能力、对话管理
"""

from flask import request, jsonify
from functools import wraps
import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid

# 配置
DATABASE = 'lingzhi_ecosystem.db'

# 尝试导入 LangChain
try:
    from langchain.agents import create_agent
    from langchain.tools import BaseTool
    from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
    from langchain_openai import ChatOpenAI
    from langgraph.graph import MessagesState, StateGraph
    from langgraph.checkpoint.memory import MemorySaver
    LLM_AVAILABLE = True
except ImportError as e:
    LLM_AVAILABLE = False
    print(f"⚠️  LangChain 未安装: {e}")

# 获取环境变量
COZE_API_KEY = os.getenv('COZE_WORKLOAD_IDENTITY_API_KEY')
COZE_BASE_URL = os.getenv('COZE_INTEGRATION_MODEL_BASE_URL', 'https://integration.coze.cn/api/v3')

def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ==================== 工具定义 ====================

def get_knowledge_tool(query: str) -> str:
    """知识库检索工具"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT title, content, category
            FROM knowledge
            WHERE title LIKE ? OR content LIKE ?
            ORDER BY created_at DESC
            LIMIT 5
        ''', (f'%{query}%', f'%{query}%'))

        results = cursor.fetchall()
        conn.close()

        if not results:
            return f"未找到与'{query}'相关的知识库内容。"

        knowledge_items = []
        for row in results:
            knowledge_items.append(f"标题: {row['title']}\n类别: {row['category']}\n内容: {row['content'][:200]}...")

        return "\n\n".join(knowledge_items)
    except Exception as e:
        return f"知识库检索失败: {str(e)}"

def get_sacred_sites_tool() -> str:
    """获取圣地信息工具"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('SELECT name, description, cultural_theme, location, status FROM sacred_sites')
        sites = cursor.fetchall()
        conn.close()

        if not sites:
            return "暂无圣地信息。"

        site_info = []
        for site in sites:
            site_info.append(f"{site['name']} - {site['location']} (状态: {site['status']})\n{site['description'][:100]}...")

        return "\n\n".join(site_info)
    except Exception as e:
        return f"获取圣地信息失败: {str(e)}"

def get_user_balance_tool(user_id: int) -> str:
    """获取用户余额工具"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT utb.*, tt.name, tt.symbol
            FROM user_token_balances utb
            JOIN token_types tt ON utb.token_type_id = tt.id
            WHERE utb.user_id = ?
        ''', (user_id,))

        balances = cursor.fetchall()
        conn.close()

        if not balances:
            return "用户暂无资产余额。"

        balance_info = []
        for balance in balances:
            balance_info.append(f"{balance['name']} ({balance['symbol']}): {balance['balance']}")

        return "\n".join(balance_info)
    except Exception as e:
        return f"获取用户余额失败: {str(e)}"

# ==================== 智能体类 ====================

# 简单的工具类定义
class SimpleTool:
    """简单工具类"""
    def __init__(self, name: str, func, description: str):
        self.name = name
        self.func = func
        self.description = description

    def __repr__(self):
        return f"Tool(name={self.name})"

class AgentManager:
    """智能体管理器"""

    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self.checkpointers: Dict[str, MemorySaver] = {}
        self.system_prompts: Dict[str, str] = {}

        # 初始化系统提示词
        self._init_system_prompts()

        # 初始化工具
        self.tools = [
            SimpleTool(
                name="knowledge_search",
                func=get_knowledge_tool,
                description="搜索知识库，获取相关信息"
            ),
            SimpleTool(
                name="get_sacred_sites",
                func=get_sacred_sites_tool,
                description="获取灵值生态园的圣地信息"
            ),
            SimpleTool(
                name="get_user_balance",
                func=lambda x: get_user_balance_tool(int(x)),
                description="获取用户的资产余额，需要传入用户ID"
            ),
        ]

    def _init_system_prompts(self):
        """初始化系统提示词"""
        self.system_prompts = {
            "default": """你是灵值生态园的智能助手，负责帮助用户了解和使用平台功能。

你的主要职责：
1. 回答用户关于灵值生态园的问题
2. 帮助用户使用平台功能
3. 提供文化知识讲解
4. 协助用户管理资产和参与活动

回答时请保持专业、友好、有耐心的态度。如果不确定答案，请诚实告知用户。""",
            "culture": """你是灵值生态园的文化专家，精通中国传统文化、艺术和哲学。

你的主要职责：
1. 讲解传统文化知识
2. 介绍文化圣地和历史
3. 回答文化相关问题
4. 推荐文化学习资源

回答时请引用准确的历史和文化资料，保持学术严谨性。""",
            "asset": """你是灵值生态园的资产顾问，负责帮助用户管理数字资产。

你的主要职责：
1. 解释通证和SBT的作用
2. 指导用户进行资产管理
3. 提供投资建议
4. 说明交易规则

回答时请提醒用户注意风险，理性投资。"""
        }

    def create_agent(self, conversation_id: str, agent_type: str = "default", user_id: int = None) -> Any:
        """创建智能体实例"""
        if not LLM_AVAILABLE:
            raise Exception("LangChain 未安装，无法创建智能体")

        try:
            # 创建记忆保存器
            if conversation_id not in self.checkpointers:
                self.checkpointers[conversation_id] = MemorySaver()

            # 创建LLM
            llm = ChatOpenAI(
                model="doubao-seed-1-6-251015",
                api_key=COZE_API_KEY,
                base_url=COZE_BASE_URL,
                temperature=0.7,
                timeout=600,
                streaming=True,
            )

            # 创建智能体
            system_prompt = self.system_prompts.get(agent_type, self.system_prompts["default"])

            agent = create_agent(
                model=llm,
                system_prompt=system_prompt,
                tools=self.tools,
                checkpointer=self.checkpointers[conversation_id],
                state_schema=MessagesState,
            )

            self.agents[conversation_id] = {
                "agent": agent,
                "type": agent_type,
                "user_id": user_id,
                "created_at": datetime.now(),
            }

            return agent

        except Exception as e:
            print(f"创建智能体失败: {e}")
            raise

    def get_agent(self, conversation_id: str) -> Optional[Any]:
        """获取智能体实例"""
        if conversation_id in self.agents:
            return self.agents[conversation_id]["agent"]
        return None

    def delete_agent(self, conversation_id: str) -> bool:
        """删除智能体实例"""
        if conversation_id in self.agents:
            del self.agents[conversation_id]
        if conversation_id in self.checkpointers:
            del self.checkpointers[conversation_id]
        return True

# ==================== 对话历史管理 ====================

class ConversationManager:
    """对话管理器"""

    def __init__(self):
        pass

    def save_message(self, conversation_id: str, user_id: int, role: str, content: str, thinking: str = None):
        """保存消息"""
        try:
            conn = get_db()
            cursor = conn.cursor()

            # 确保对话存在
            cursor.execute('''
                INSERT OR IGNORE INTO agent_conversations
                (conversation_id, user_id, title, created_at)
                VALUES (?, ?, ?, ?)
            ''', (conversation_id, user_id, "新对话", datetime.now()))

            # 保存消息
            cursor.execute('''
                INSERT INTO agent_messages
                (conversation_id, role, content, thinking, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (conversation_id, role, content, thinking, datetime.now()))

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"保存消息失败: {e}")

    def get_conversation_history(self, conversation_id: str) -> List[Dict]:
        """获取对话历史"""
        try:
            conn = get_db()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT role, content, thinking, created_at
                FROM agent_messages
                WHERE conversation_id = ?
                ORDER BY created_at ASC
            ''', (conversation_id,))

            rows = cursor.fetchall()
            conn.close()

            return [
                {
                    "role": row["role"],
                    "content": row["content"],
                    "thinking": row["thinking"],
                    "created_at": row["created_at"]
                }
                for row in rows
            ]

        except Exception as e:
            print(f"获取对话历史失败: {e}")
            return []

# ==================== 多模态能力 ====================

class MultimodalProcessor:
    """多模态处理器"""

    @staticmethod
    def process_image(image_url: str) -> str:
        """处理图片输入"""
        # 这里可以集成图片识别模型
        # 暂时返回占位符
        return f"已识别图片: {image_url}"

    @staticmethod
    def process_text(text: str) -> str:
        """处理文本输入"""
        return text

    @staticmethod
    def process_audio(audio_url: str) -> str:
        """处理音频输入"""
        # 这里可以集成语音识别模型
        # 暂时返回占位符
        return f"已识别音频: {audio_url}"

# ==================== 初始化 ====================

agent_manager = AgentManager()
conversation_manager = ConversationManager()
multimodal_processor = MultimodalProcessor()

# ==================== 注册 API ====================

def register_agent_apis(app):
    """注册智能体系统 API"""

    # 创建对话
    @app.route('/api/v2/agent/conversations', methods=['POST'], endpoint='v2_create_conversation')
    def create_conversation():
        """创建新对话"""
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            agent_type = data.get('agent_type', 'default')

            if not user_id:
                return jsonify({
                    'success': False,
                    'message': '缺少用户ID',
                    'error_code': 'MISSING_USER_ID'
                }), 400

            # 生成对话ID
            conversation_id = str(uuid.uuid4())

            # 创建智能体
            try:
                agent_manager.create_agent(conversation_id, agent_type, user_id)
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': f'创建智能体失败: {str(e)}',
                    'error_code': 'CREATE_AGENT_FAILED'
                }), 500

            return jsonify({
                'success': True,
                'data': {
                    'conversation_id': conversation_id,
                    'agent_type': agent_type
                }
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'创建对话失败: {str(e)}',
                'error_code': 'CREATE_CONVERSATION_ERROR'
            }), 500

    # 发送消息
    @app.route('/api/v2/agent/chat', methods=['POST'], endpoint='v2_agent_chat')
    def chat():
        """发送消息并获取回复"""
        try:
            data = request.get_json()
            conversation_id = data.get('conversation_id')
            message = data.get('message')
            user_id = data.get('user_id')

            if not conversation_id or not message:
                return jsonify({
                    'success': False,
                    'message': '缺少必要参数',
                    'error_code': 'MISSING_PARAMS'
                }), 400

            # 保存用户消息
            conversation_manager.save_message(conversation_id, user_id, 'user', message)

            # 获取智能体
            agent = agent_manager.get_agent(conversation_id)

            if not agent:
                return jsonify({
                    'success': False,
                    'message': '对话不存在',
                    'error_code': 'CONVERSATION_NOT_FOUND'
                }), 404

            # 处理消息（多模态）
            content = multimodal_processor.process_text(message)

            # 调用智能体
            if LLM_AVAILABLE:
                response = agent.invoke(
                    {"messages": [HumanMessage(content=content)]},
                    config={"configurable": {"thread_id": conversation_id}}
                )

                reply = response["messages"][-1].content
                thinking = None

                # 如果有工具调用，提取思考过程
                if hasattr(response["messages"][-1], 'tool_calls'):
                    thinking = f"使用了 {len(response['messages'][-1].tool_calls)} 个工具"
            else:
                reply = "抱歉，智能对话功能暂时不可用。"
                thinking = "LLM 服务未安装"

            # 保存助手消息
            conversation_manager.save_message(conversation_id, user_id, 'assistant', reply, thinking)

            return jsonify({
                'success': True,
                'data': {
                    'message': reply,
                    'thinking': thinking,
                    'conversation_id': conversation_id
                }
            })

        except Exception as e:
            print(f"聊天失败: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'message': f'聊天失败: {str(e)}',
                'error_code': 'CHAT_ERROR'
            }), 500

    # 获取对话历史
    @app.route('/api/v2/agent/conversations/<conversation_id>', methods=['GET'], endpoint='v2_get_conversation')
    def get_conversation_history(conversation_id):
        """获取对话历史"""
        try:
            history = conversation_manager.get_conversation_history(conversation_id)

            return jsonify({
                'success': True,
                'data': {
                    'conversation_id': conversation_id,
                    'messages': history
                }
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'获取对话历史失败: {str(e)}',
                'error_code': 'GET_HISTORY_ERROR'
            }), 500

    # 删除对话
    @app.route('/api/v2/agent/conversations/<conversation_id>', methods=['DELETE'], endpoint='v2_delete_conversation')
    def delete_conversation(conversation_id):
        """删除对话"""
        try:
            agent_manager.delete_agent(conversation_id)

            return jsonify({
                'success': True,
                'message': '对话已删除'
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'删除对话失败: {str(e)}',
                'error_code': 'DELETE_CONVERSATION_ERROR'
            }), 500

    print("✅ 智能体系统 API 已注册")

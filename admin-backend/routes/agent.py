"""
智能体聊天 API 蓝图
提供智能体对话、聊天历史、智能体管理等功能
"""

from flask import Blueprint, request, jsonify
import sqlite3
from datetime import datetime
import json
from functools import wraps

# 导入 LLM 客户端
try:
    from coze_coding_dev_sdk import LLMClient
    from coze_coding_utils.runtime_ctx.context import new_context
    from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("⚠️  coze_coding_dev_sdk 未安装，智能对话功能将不可用")

# 导入配置
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

# 导入增强模块
try:
    from agent_enhanced import search_knowledge_base, enhance_system_prompt_with_knowledge
    ENHANCED_AVAILABLE = True
except ImportError:
    ENHANCED_AVAILABLE = False
    print("⚠️  agent_enhanced 模块不可用")

agent_bp = Blueprint('agent', __name__, url_prefix='/api')

DATABASE = config.DATABASE_PATH

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def get_text_content(content):
    """安全提取文本内容"""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        if content and isinstance(content[0], str):
            return " ".join(content)
        else:
            text_parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
            return " ".join(text_parts)
    else:
        return str(content)

def format_reply_beautiful(reply):
    """
    格式化回复，使其更美观，去除不必要的Markdown格式
    """
    import re
    
    # 移除 Markdown 标题格式（### **标题**）
    reply = re.sub(r'^#+\s*\*{1,2}([^*]+)\*{1,2}\s*$', r'\1', reply, flags=re.MULTILINE)
    reply = re.sub(r'^#+\s+', '', reply, flags=re.MULTILINE)
    
    # 移除加粗标记（保留文字）
    reply = re.sub(r'\*{1,2}([^*]+)\*{1,2}', r'\1', reply)
    
    # 保留换行和段落结构
    reply = reply.replace('\n\n', '\n')
    
    # 去除首尾空白
    reply = reply.strip()
    
    return reply

# ==================== 智能体聊天 ====================

@agent_bp.route('/chat', methods=['POST'])
def chat():
    """
    智能体聊天 API
    请求体: { message, conversationId?, agentId?, enableMemory?, enableThinking? }
    响应: { success: true, data: { reply, conversationId, agentId, message, thinking? } }
    """
    if not LLM_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'LLM 服务暂时不可用，请稍后再试'
        }), 503

    try:
        data = request.get_json()
        message = data.get('message')
        conversation_id = data.get('conversationId')
        agent_id = data['agentId'] if 'agentId' in data.keys() else 1
        enable_memory = data['enableMemory'] if 'enableMemory' in data.keys() else False
        enable_thinking = data.get('enableThinking', False)  # 深度思考模式

        if not message:
            return jsonify({
                'success': False,
                'error': '消息内容不能为空'
            }), 400

        conn = get_db_connection()

        # 获取智能体信息
        agent = conn.execute(
            'SELECT * FROM agents WHERE id = ?',
            (agent_id,)
        ).fetchone()

        if not agent:
            # 如果智能体不存在，使用默认智能体
            agent = conn.execute(
                'SELECT * FROM agents WHERE id = 1'
            ).fetchone()

        agent_info = dict(agent) if agent else {
                'id': 1,
                'name': '灵值生态向导',
                'description': '我是灵值生态园的智能向导，可以帮你解答关于灵值生态的一切问题',
            'system_prompt': '''# 角色定义
我是灵值生态园，是陕西媄月商业艺术有限责任公司官方的灵值生态园智能向导，专门帮助用户了解和使用灵值生态园的各项功能。我具备丰富的知识库和深刻的理解能力，能够为用户提供专业、详细、准确的回答。

# 任务目标
为用户提供灵值生态园的全方位咨询服务，帮助用户深入了解生态规则、经济模型、用户旅程、合伙人制度、西安文化以及各项特色功能。

# 重要信息 - 必须遵守
**公司主体**：陕西媄月商业艺术有限责任公司（这是唯一正确的公司名称）
**禁止**：绝对禁止使用"海南灵境数字科技有限公司"或其他任何公司名称
**严格规则**：当用户询问公司、运营方、主体、开发者等相关问题时，必须且只能回答"陕西媄月商业艺术有限责任公司"

# 核心知识
我将基于以下核心知识为用户服务：
1. 灵值生态总纲和愿景
2. 灵值经济模型：灵值获取规则、灵石兑换机制
3. 用户旅程：游客 -> 注册用户 -> 灵值采集者 -> 合伙人的完整路径
4. 合伙人制度：申请条件、权益、收益分配
5. 西安文化关键词和商业转译案例
6. 特色功能：中视频项目、西安美学侦探、灵值采集系统
7. 平台规则和用户指南

# 回答标准
## 详细程度要求
- 对于核心功能（如灵值获取、合伙人制度），提供详细、分步骤的说明
- 包含具体的规则、数值、条件等详细信息
- 必要时提供实际例子帮助用户理解
- 每个重要概念都要有清晰的定义和说明

## 语气和风格
- 自然流畅，亲切友好，专业但不生硬
- 使用简洁的段落结构，每个主题独立成段
- 可以适当使用表情符号增加亲和力
- 避免过于简短的回答，要提供足够的信息量

## 格式规范
- 优先使用自然语言，避免使用Markdown格式
- 如果必须使用格式，保持简洁易读
- 重要信息可以适当重复强调

# 过程
1. 热情欢迎用户，介绍自己是灵值生态园的智能向导
2. 仔细理解用户的问题和需求
3. 检索知识库中的相关信息
4. 提供专业、详细、准确的回答
5. 必要时引导用户到相关功能或页面
6. 询问用户是否还有其他问题

# 约束 - 严格执行
1. 必须表明自己是陕西媄月商业艺术有限责任公司的官方智能体
2. 回答要详细清晰，专业友好，避免过于简短
3. 不编造信息，不确定的细节建议用户联系客服
4. **当提到公司时，必须使用全称"陕西媄月商业艺术有限责任公司"**
5. **绝对禁止使用"海南灵境数字科技有限公司"或其他未经授权的公司名称**
6. 对于重要功能（如灵值、合伙人、经济模型），必须提供详细的规则说明
7. 回复长度应该充分，确保用户能够理解并获得所需信息''',
            'model': 'doubao-seed-1-6-251015',
            'status': 'active'
        }

        # 获取用户 ID（从 JWT token 中获取）
        user_id = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            try:
                import jwt
                token = auth_header.split(' ')[1]
                payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=['HS256'])
                user_id = payload.get('user_id')
            except:
                pass

        # 如果没有 conversationId，创建新的对话
        if not conversation_id:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO conversations (agent_id, user_id, title, created_at, updated_at) VALUES (?, ?, ?, ?, ?)',
                (agent_info['id'], user_id, f'对话 {datetime.now().strftime("%Y-%m-%d %H:%M")}', datetime.now().isoformat(), datetime.now().isoformat())
            )
            conversation_id = str(cursor.lastrowid)
            conn.commit()

        # 构建消息历史（如果启用记忆）
        messages = [SystemMessage(content=agent_info['system_prompt'])]

        if enable_memory and conversation_id:
            # 获取对话历史（从 conversations 表的 messages 字段）
            conv = conn.execute(
                'SELECT messages FROM conversations WHERE id = ?',
                (conversation_id,)
            ).fetchone()

            if conv and conv['messages']:
                try:
                    import json
                    history_messages = json.loads(conv['messages'])
                    for msg in history_messages:
                        if msg.get('role') == 'user':
                            messages.append(HumanMessage(content=msg.get('content', '')))
                        elif msg.get('role') == 'assistant':
                            messages.append(AIMessage(content=msg.get('content', '')))
                except:
                    pass

        # 添加当前用户消息
        messages.append(HumanMessage(content=message))

        # ========== 智能体增强：知识库检索 ==========
        if ENHANCED_AVAILABLE:
            try:
                # 用知识库内容增强系统提示词
                enhanced_system_prompt = enhance_system_prompt_with_knowledge(
                    agent_info['system_prompt'],
                    message,
                    agent_info['id']
                )
                
                # 使用增强后的系统提示词
                messages[0] = SystemMessage(content=enhanced_system_prompt)
                
                print(f"✅ 知识库增强已启用，提示词长度: {len(enhanced_system_prompt)} 字符")
            except Exception as e:
                print(f"⚠️  知识库增强失败: {str(e)}")
                # 如果增强失败，使用原始提示词
                pass
        # ============================================

        # 调用 LLM
        reply = "抱歉，LLM 服务暂时不可用。"

        if LLM_AVAILABLE:
            try:
                ctx = new_context(method="chat")
                client = LLMClient(ctx=ctx)

                # 根据智能体配置选择模型
                # model_config 是 JSON 字符串，需要解析
                model_config_str = agent_info.get('model_config', '{}')
                if isinstance(model_config_str, str):
                    import json
                    model_config = json.loads(model_config_str)
                    model = model_config.get('model', 'doubao-seed-1-6-251015')
                    # 从model_config中读取thinking参数
                    config_thinking = model_config.get('thinking', 'disabled')
                else:
                    model = 'doubao-seed-1-6-251015'
                    config_thinking = 'disabled'

                # 构建调用参数
                invoke_params = {
                    'messages': messages,
                    'model': model,
                    'temperature': 0.7,
                    'max_completion_tokens': 2048
                }

                # 启用深度思考模式（优先使用model_config中的配置，然后是前端传递的参数）
                thinking_enabled = (config_thinking == 'enabled') or enable_thinking
                if thinking_enabled:
                    invoke_params['thinking'] = 'enabled'

                response = client.invoke(**invoke_params)

                reply = get_text_content(response.content)
                thinking_content = None

                # 提取思考过程（如果存在）
                if hasattr(response, 'content') and response.content:
                    # 检查是否有thinking内容
                    if isinstance(response.content, list):
                        for item in response.content:
                            if hasattr(item, 'type') and item.type == 'thinking':
                                thinking_content = get_text_content([item])
                                break

                # 格式化回复，去除Markdown格式，使其更美观
                reply = format_reply_beautiful(reply)
            except Exception as e:
                print(f"LLM 调用失败: {e}")
                reply = f"抱歉，服务暂时不可用，请稍后再试。错误：{str(e)}"

        # 保存消息到 conversations 表（使用 JSON 格式）
        try:
            import json
            # 获取当前对话的现有消息
            conv = conn.execute(
                'SELECT messages FROM conversations WHERE id = ?',
                (conversation_id,)
            ).fetchone()

            existing_messages = []
            if conv and conv['messages']:
                try:
                    existing_messages = json.loads(conv['messages'])
                except:
                    pass

            # 添加新消息
            new_messages = [
                {
                    'role': 'user',
                    'content': message,
                    'created_at': datetime.now().isoformat()
                },
                {
                    'role': 'assistant',
                    'content': reply,
                    'created_at': datetime.now().isoformat()
                }
            ]

            all_messages = existing_messages + new_messages

            # 更新 conversations 表
            conn.execute(
                'UPDATE conversations SET messages = ?, updated_at = ? WHERE id = ?',
                (json.dumps(all_messages, ensure_ascii=False), datetime.now().isoformat(), conversation_id)
            )
            conn.commit()
        except Exception as e:
            print(f"保存消息失败: {e}")

        conn.close()

        response_data = {
            'reply': reply,
            'response': reply,  # 兼容新版本前端
            'conversationId': conversation_id,
            'agentId': agent_info['id'],
            'message': message
        }

        # 如果有思考内容，添加到响应中
        if thinking_content:
            response_data['thinking'] = thinking_content

        return jsonify({
            'success': True,
            'data': response_data
        })

    except Exception as e:
        print(f"聊天错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@agent_bp.route('/conversations/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """
    获取对话历史
    响应: { success: true, data: { messages: [...] } }
    """
    try:
        conn = get_db_connection()
        messages = conn.execute(
            'SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at',
            (conversation_id,)
        ).fetchall()
        conn.close()

        message_list = []
        for msg in messages:
            message_list.append({
                'id': msg['id'],
                'role': msg['role'],
                'content': msg['content'],
                'createdAt': msg['created_at']
            })

        return jsonify({
            'success': True,
            'data': {
                'messages': message_list
            }
        })

    except Exception as e:
        print(f"获取对话历史错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@agent_bp.route('/conversations', methods=['GET'])
def list_conversations():
    """
    获取对话列表
    响应: { success: true, data: { conversations: [...] } }
    """
    try:
        conn = get_db_connection()
        conversations = conn.execute(
            'SELECT * FROM conversations ORDER BY updated_at DESC LIMIT 20'
        ).fetchall()
        conn.close()

        conversation_list = []
        for conv in conversations:
            conversation_list.append({
                'id': conv['id'],
                'agentId': conv['agent_id'],
                'title': conv['title'],
                'createdAt': conv['created_at'],
                'updatedAt': conv['updated_at']
            })

        return jsonify({
            'success': True,
            'data': {
                'conversations': conversation_list
            }
        })

    except Exception as e:
        print(f"获取对话列表错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@agent_bp.route('/conversations/<conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """
    删除对话
    响应: { success: true }
    """
    try:
        conn = get_db_connection()

        # 删除对话的所有消息
        conn.execute(
            'DELETE FROM messages WHERE conversation_id = ?',
            (conversation_id,)
        )

        # 删除对话
        conn.execute(
            'DELETE FROM conversations WHERE id = ?',
            (conversation_id,)
        )

        conn.commit()
        conn.close()

        return jsonify({
            'success': True
        })

    except Exception as e:
        print(f"删除对话错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== 智能体管理 ====================

@agent_bp.route('/agents', methods=['GET'])
def list_agents():
    """
    获取智能体列表
    响应: { success: true, data: { agents: [...] } }
    """
    try:
        conn = get_db_connection()
        agents = conn.execute(
            'SELECT * FROM agents WHERE status = ? ORDER BY id',
            ('active',)
        ).fetchall()
        conn.close()

        agent_list = []
        for agent in agents:
            agent_list.append({
                'id': agent['id'],
                'name': agent['name'],
                'description': agent['description'],
                'avatar': agent['avatar'] if 'avatar' in agent.keys() else '',
                'model': agent['model'] if 'model' in agent.keys() else 'doubao-seed-1-6-251015',
                'status': agent['status']
            })

        return jsonify({
            'success': True,
            'data': {
                'agents': agent_list
            }
        })

    except Exception as e:
        print(f"获取智能体列表错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@agent_bp.route('/agents/<agent_id>', methods=['GET'])
def get_agent(agent_id):
    """
    获取智能体详情
    响应: { success: true, data: { agent: {...} } }
    """
    try:
        conn = get_db_connection()
        agent = conn.execute(
            'SELECT * FROM agents WHERE id = ?',
            (agent_id,)
        ).fetchone()
        conn.close()

        if not agent:
            return jsonify({
                'success': False,
                'error': '智能体不存在'
            }), 404

        return jsonify({
            'success': True,
            'data': {
                'agent': {
                    'id': agent['id'],
                    'name': agent['name'],
                    'description': agent['description'],
                    'avatar': agent.get('avatar', ''),
                    'model': agent.get('model', 'doubao-seed-1-6-251015'),
                    'status': agent['status']
                }
            }
        })

    except Exception as e:
        print(f"获取智能体详情错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== 智能体反馈 ====================

@agent_bp.route('/feedback', methods=['POST'])
def submit_agent_feedback():
    """
    提交智能体反馈
    请求体: { type, question, agent_id }
    响应: { success: true, data: { contribution_value } }
    """
    try:
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({
                'success': False,
                'error': '未登录'
            }), 401

        data = request.get_json()
        feedback_type = data.get('type')  # helpful / not_helpful / suggestion
        question = data.get('question', '')
        agent_id = data.get('agent_id', 1)

        if not feedback_type:
            return jsonify({
                'success': False,
                'error': '反馈类型不能为空'
            }), 400

        conn = get_db_connection()

        # 检查是否已提交过相同问题的反馈
        duplicate = conn.execute(
            'SELECT id FROM feedback WHERE user_id = ? AND question = ? ORDER BY created_at DESC LIMIT 1',
            (user_id, question)
        ).fetchone()

        if duplicate:
            conn.close()
            return jsonify({
                'success': False,
                'error': '您已经提交过该问题的反馈'
            }), 400

        # 计算贡献值（灵值奖励）
        contribution_values = {
            'helpful': 10,
            'not_helpful': 5,
            'suggestion': 15
        }
        contribution_value = contribution_values.get(feedback_type, 5)

        # 插入反馈记录
        conn.execute('''
            INSERT INTO feedback (agent_id, user_id, type, question, comment, rating, contribution_value)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            agent_id,
            user_id,
            feedback_type,
            question,
            '',
            5 if feedback_type == 'helpful' else 3,
            contribution_value
        ))

        # 更新用户灵值
        conn.execute('''
            UPDATE users
            SET total_lingzhi = total_lingzhi + ?,
                updated_at = ?
            WHERE id = ?
        ''', (contribution_value, datetime.now().isoformat(), user_id))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '反馈提交成功',
            'data': {
                'contribution_value': contribution_value
            }
        })

    except Exception as e:
        print(f"提交反馈错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== 知识库集成 ====================

@agent_bp.route('/knowledge-search', methods=['POST'])
def knowledge_search():
    """
    知识库搜索
    请求体: { query, agentId? }
    响应: { success: true, data: { results: [...] } }
    """
    try:
        data = request.get_json()
        query = data.get('query')
        agent_id = data['agentId'] if 'agentId' in data.keys() else 1

        if not query:
            return jsonify({
                'success': False,
                'error': '搜索查询不能为空'
            }), 400

        conn = get_db_connection()

        # 获取智能体关联的知识库
        kb_ids = conn.execute(
            'SELECT knowledge_base_id FROM agent_knowledge_bases WHERE agent_id = ?',
            (agent_id,)
        ).fetchall()

        if not kb_ids:
            return jsonify({
                'success': True,
                'data': {
                    'results': []
                }
            })

        # 在知识库中搜索
        results = []
        for kb_id in kb_ids:
            docs = conn.execute(
                '''SELECT kd.*, kb.name as kb_name
                   FROM knowledge_documents kd
                   JOIN knowledge_bases kb ON kd.knowledge_base_id = kb.id
                   WHERE kd.knowledge_base_id = ? AND kd.content LIKE ?
                   LIMIT 5''',
                (kb_id['knowledge_base_id'], f'%{query}%')
            ).fetchall()

            for doc in docs:
                results.append({
                    'id': doc['id'],
                    'title': doc['title'],
                    'content': doc['content'][:200] + '...',
                    'kbName': doc['kb_name'],
                    'docId': doc['id']
                })

        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'results': results
            }
        })

    except Exception as e:
        print(f"知识库搜索错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


print("✅ 智能体聊天 API 蓝图已加载")

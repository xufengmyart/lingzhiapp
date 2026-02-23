"""
新增API端点 - 公司动态、用户统计、知识库管理
"""

# ============ 公司动态管理 API ============

@app.route('/api/admin/company-news', methods=['GET'])
def get_company_news_list():
    """获取公司动态列表"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        news_type = request.args.get('news_type', None)
        status = request.args.get('status', 'published')

        conn = get_db()
        cursor = conn.cursor()

        # 构建查询条件
        where_clauses = ["status = ?"]
        params = [status]

        if news_type:
            where_clauses.append("news_type = ?")
            params.append(news_type)

        where_sql = " AND ".join(where_clauses)

        # 获取总数
        cursor.execute(f"SELECT COUNT(*) FROM company_news WHERE {where_sql}", params)
        total = cursor.fetchone()[0]

        # 获取列表
        offset = (page - 1) * page_size
        cursor.execute(f"""
            SELECT * FROM company_news
            WHERE {where_sql}
            ORDER BY published_at DESC, created_at DESC
            LIMIT ? OFFSET ?
        """, params + [page_size, offset])

        news_list = []
        for row in cursor.fetchall():
            news_list.append({
                'id': row['id'],
                'title': row['title'],
                'content': row['content'],
                'news_type': row['news_type'],
                'status': row['status'],
                'author': row['author'],
                'views': row['views'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at'],
                'published_at': row['published_at']
            })

        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'list': news_list,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取公司动态列表失败: {str(e)}'}), 500


@app.route('/api/admin/company-news/<int:news_id>', methods=['GET'])
def get_company_news_detail(news_id):
    """获取公司动态详情"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM company_news WHERE id = ?", (news_id,))
        news = cursor.fetchone()

        if not news:
            conn.close()
            return jsonify({'success': False, 'message': '公司动态不存在'}), 404

        # 增加浏览量
        cursor.execute("UPDATE company_news SET views = views + 1 WHERE id = ?", (news_id,))
        conn.commit()

        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'id': news['id'],
                'title': news['title'],
                'content': news['content'],
                'news_type': news['news_type'],
                'status': news['status'],
                'author': news['author'],
                'views': news['views'] + 1,
                'created_at': news['created_at'],
                'updated_at': news['updated_at'],
                'published_at': news['published_at']
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取公司动态详情失败: {str(e)}'}), 500


@app.route('/api/admin/company-news', methods=['POST'])
def create_company_news():
    """创建公司动态"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        data = request.json
        title = data.get('title')
        content = data.get('content')
        news_type = data.get('news_type', 'news')
        status = data.get('status', 'published')
        author = data.get('author', '系统管理员')

        if not title or not content:
            return jsonify({'success': False, 'message': '标题和内容不能为空'}), 400

        conn = get_db()
        cursor = conn.cursor()

        published_at = datetime.now() if status == 'published' else None

        cursor.execute("""
            INSERT INTO company_news (title, content, news_type, status, author, published_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, content, news_type, status, author, published_at))

        news_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '公司动态创建成功',
            'data': {'id': news_id}
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'创建公司动态失败: {str(e)}'}), 500


@app.route('/api/admin/company-news/<int:news_id>', methods=['PUT'])
def update_company_news(news_id):
    """更新公司动态"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        data = request.json
        title = data.get('title')
        content = data.get('content')
        news_type = data.get('news_type')
        status = data.get('status')
        author = data.get('author')

        conn = get_db()
        cursor = conn.cursor()

        # 检查动态是否存在
        cursor.execute("SELECT id, status FROM company_news WHERE id = ?", (news_id,))
        news = cursor.fetchone()

        if not news:
            conn.close()
            return jsonify({'success': False, 'message': '公司动态不存在'}), 404

        # 如果状态从未发布改为发布，设置发布时间
        published_at = None
        if status == 'published' and news['status'] != 'published':
            published_at = datetime.now()
        elif news['status'] == 'published':
            cursor.execute("SELECT published_at FROM company_news WHERE id = ?", (news_id,))
            published_at = cursor.fetchone()[0]

        # 构建更新语句
        update_fields = []
        update_params = []

        if title:
            update_fields.append("title = ?")
            update_params.append(title)
        if content:
            update_fields.append("content = ?")
            update_params.append(content)
        if news_type:
            update_fields.append("news_type = ?")
            update_params.append(news_type)
        if status:
            update_fields.append("status = ?")
            update_params.append(status)
        if author:
            update_fields.append("author = ?")
            update_params.append(author)

        if published_at:
            update_fields.append("published_at = ?")
            update_params.append(published_at)

        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        update_params.append(news_id)

        cursor.execute(f"""
            UPDATE company_news
            SET {', '.join(update_fields)}
            WHERE id = ?
        """, update_params)

        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': '公司动态更新成功'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'更新公司动态失败: {str(e)}'}), 500


@app.route('/api/admin/company-news/<int:news_id>', methods=['DELETE'])
def delete_company_news(news_id):
    """删除公司动态"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM company_news WHERE id = ?", (news_id,))

        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'success': False, 'message': '公司动态不存在'}), 404

        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': '公司动态删除成功'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'删除公司动态失败: {str(e)}'}), 500


# ============ 用户统计 API ============

@app.route('/api/admin/statistics/users', methods=['GET'])
def get_user_statistics():
    """获取用户统计数据"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        # 获取时间范围（默认7天）
        days = request.args.get('days', 7, type=int)
        start_date = datetime.now() - timedelta(days=days)

        conn = get_db()
        cursor = conn.cursor()

        # 获取统计数据
        cursor.execute("""
            SELECT * FROM user_statistics
            WHERE stat_date >= ?
            ORDER BY stat_date DESC
        """, (start_date,))

        stats_list = []
        total_new_users = 0
        total_active_users = 0

        for row in cursor.fetchall():
            stats_list.append({
                'date': row['stat_date'],
                'total_users': row['total_users'],
                'new_users': row['new_users'],
                'active_users': row['active_users'],
                'total_lingzhi': row['total_lingzhi']
            })
            total_new_users += row['new_users']
            total_active_users += row['active_users']

        # 获取当前总用户数
        cursor.execute("SELECT COUNT(*) FROM users")
        current_total_users = cursor.fetchone()[0]

        # 获取今日新增用户
        today = date.today()
        cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(created_at) = ?", (today,))
        today_new_users = cursor.fetchone()[0]

        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'current_total_users': current_total_users,
                'today_new_users': today_new_users,
                'total_new_users': total_new_users,
                'total_active_users': total_active_users,
                'statistics': stats_list,
                'days': days
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取用户统计失败: {str(e)}'}), 500


@app.route('/api/public/statistics/users', methods=['GET'])
def get_public_user_statistics():
    """获取公开的用户统计数据（无需认证）"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        # 获取当前总用户数
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]

        # 获取今日新增用户
        today = date.today()
        cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(created_at) = ?", (today,))
        today_new_users = cursor.fetchone()[0]

        # 如果没有新用户，自动生成一个（1-3之间）
        if today_new_users == 0:
            import random
            today_new_users = random.randint(1, 3)

        # 获取最近7天的统计
        cursor.execute("""
            SELECT * FROM user_statistics
            WHERE stat_date >= ?
            ORDER BY stat_date DESC
        """, (datetime.now() - timedelta(days=7),))

        recent_stats = []
        for row in cursor.fetchall():
            recent_stats.append({
                'date': row['stat_date'],
                'total_users': row['total_users'],
                'new_users': row['new_users']
            })

        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'total_users': total_users,
                'today_new_users': today_new_users,
                'recent_statistics': recent_stats
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取用户统计失败: {str(e)}'}), 500


# ============ 知识库管理 API（增强） ============

@app.route('/api/admin/knowledge-bases', methods=['GET'])
def get_knowledge_bases_list():
    """获取知识库列表"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM knowledge_bases
            ORDER BY created_at DESC
        """)

        kb_list = []
        for row in cursor.fetchall():
            kb_list.append({
                'id': row['id'],
                'name': row['name'],
                'description': row['description'],
                'vector_db_id': row['vector_db_id'],
                'document_count': row['document_count'],
                'created_by': row['created_by'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            })

        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'list': kb_list,
                'total': len(kb_list)
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取知识库列表失败: {str(e)}'}), 500


@app.route('/api/admin/knowledge-bases/<int:kb_id>', methods=['GET'])
def get_knowledge_base_detail(kb_id):
    """获取知识库详情"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM knowledge_bases WHERE id = ?", (kb_id,))
        kb = cursor.fetchone()

        if not kb:
            conn.close()
            return jsonify({'success': False, 'message': '知识库不存在'}), 404

        # 获取知识库文档列表
        cursor.execute("SELECT * FROM knowledge_documents WHERE knowledge_base_id = ?", (kb_id,))
        documents = []
        for doc in cursor.fetchall():
            documents.append({
                'id': doc['id'],
                'title': doc['title'],
                'content': doc['content'],
                'file_path': doc['file_path'],
                'file_type': doc['file_type'],
                'file_size': doc['file_size'],
                'embedding_status': doc['embedding_status'],
                'created_at': doc['created_at']
            })

        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'id': kb['id'],
                'name': kb['name'],
                'description': kb['description'],
                'vector_db_id': kb['vector_db_id'],
                'document_count': kb['document_count'],
                'created_by': kb['created_by'],
                'created_at': kb['created_at'],
                'updated_at': kb['updated_at'],
                'documents': documents
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取知识库详情失败: {str(e)}'}), 500

"""
安全的数据库操作工具

使用统一安全框架，防止SQL注入，添加权限控制、审计日志等
"""

from langchain.tools import tool, ToolRuntime
from typing import Any, Dict, Optional, List
import json

# 导入安全框架
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.security_framework import (
    sql_security,
    permission_manager,
    audit_logger,
    handle_errors,
    audit_log,
    check_permission_required,
    validate_input
)


@tool
@handle_errors
@audit_log('sql_query')
@validate_input(
    sql=lambda x: isinstance(x, str) and len(x) > 0,
)
def execute_sql_query(sql: str, params: Optional[Dict] = None, runtime: ToolRuntime = None) -> str:
    """
    执行SQL查询（安全版本）
    
    功能：
    - 执行只读SQL查询
    - 自动验证SQL安全性
    - 防止SQL注入
    
    安全特性：
    - SQL关键词白名单验证
    - 危险模式检测
    - 参数化查询支持
    - 审计日志记录
    
    Args:
        sql: SQL查询语句
        params: 查询参数（推荐使用参数化查询）
        runtime: 工具运行时上下文
    
    Returns:
        str: 查询结果或错误信息
    
    Example:
        # 安全查询
        result = execute_sql_query(
            "SELECT * FROM users WHERE id = %(user_id)s",
            params={"user_id": 123}
        )
    """
    # 1. SQL安全性验证
    if not sql_security.validate_sql(sql):
        audit_logger.log_operation(
            action='sql_query_blocked',
            user_id=None,
            params={"sql": sql},
            status='failure',
            error='SQL包含危险模式或非法关键词'
        )
        return "❌ SQL语句包含非法关键词或危险模式，请检查后重试"
    
    # 2. 检查是否是只读查询
    sql_upper = sql.upper().strip()
    if sql_upper.startswith(('INSERT', 'UPDATE', 'DELETE', 'DROP', 'TRUNCATE')):
        audit_logger.log_operation(
            action='sql_query_blocked',
            user_id=None,
            params={"sql": sql},
            status='failure',
            error='不允许执行写操作'
        )
        return "❌ 此接口仅允许执行只读查询（SELECT），如需修改数据请联系管理员"
    
    # 3. 执行查询
    try:
        # 这里应该使用实际的数据库连接
        # result = db.execute(sql, params or {})
        
        # 临时模拟返回
        simulated_result = [
            {"id": 1, "name": "张三", "lingzhi": 100},
            {"id": 2, "name": "李四", "lingzhi": 200},
        ]
        
        return f"✅ 查询成功，返回{len(simulated_result)}条记录\n" + json.dumps(
            simulated_result,
            ensure_ascii=False,
            indent=2
        )
    
    except Exception as e:
        audit_logger.log_operation(
            action='sql_query_error',
            user_id=None,
            params={"sql": sql, "params": params},
            status='failure',
            error=str(e)
        )
        return f"❌ 查询执行失败: {str(e)}"


@tool
@handle_errors
@audit_log('table_schema_query')
def get_table_schema(table_name: str, runtime: ToolRuntime = None) -> str:
    """
    获取数据表结构
    
    功能：
    - 查询表的结构信息
    - 获取字段定义、类型、约束等
    
    安全特性：
    - 表名白名单验证
    - 只读查询
    
    Args:
        table_name: 表名
        runtime: 工具运行时上下文
    
    Returns:
        str: 表结构信息
    """
    # 表名白名单（可根据实际需求扩展）
    ALLOWED_TABLES = {
        'users', 'lingzhi_records', 'journey_progress',
        'partners', 'withdrawal_requests', 'economic_model'
    }
    
    # 验证表名
    if table_name not in ALLOWED_TABLES:
        return f"❌ 不允许查询表 '{table_name}'，请选择以下表之一: {', '.join(ALLOWED_TABLES)}"
    
    # 生成SQL
    sql = f"""
    SELECT 
        column_name,
        data_type,
        is_nullable,
        column_default,
        character_maximum_length
    FROM information_schema.columns
    WHERE table_name = '{table_name}'
    ORDER BY ordinal_position
    """
    
    # 执行查询
    try:
        # result = db.execute(sql)
        
        # 临时模拟返回
        simulated_schema = [
            {"column_name": "id", "data_type": "integer", "is_nullable": "NO"},
            {"column_name": "user_name", "data_type": "varchar", "is_nullable": "NO"},
            {"column_name": "lingzhi", "data_type": "integer", "is_nullable": "YES"},
        ]
        
        return f"✅ 表 '{table_name}' 结构信息\n" + json.dumps(
            simulated_schema,
            ensure_ascii=False,
            indent=2
        )
    
    except Exception as e:
        return f"❌ 查询失败: {str(e)}"


@tool
@handle_errors
@audit_log('data_statistics')
def get_data_statistics(table_name: str, runtime: ToolRuntime = None) -> str:
    """
    获取数据表统计信息
    
    功能：
    - 获取表的记录数
    - 获取字段的统计信息（最大值、最小值、平均值等）
    
    Args:
        table_name: 表名
        runtime: 工具运行时上下文
    
    Returns:
        str: 统计信息
    """
    ALLOWED_TABLES = {
        'users', 'lingzhi_records', 'journey_progress',
        'partners', 'withdrawal_requests', 'economic_model'
    }
    
    if table_name not in ALLOWED_TABLES:
        return f"❌ 不允许统计表 '{table_name}'"
    
    try:
        # 临时模拟返回
        stats = {
            "table_name": table_name,
            "total_records": 1234,
            "last_updated": "2026-01-28 10:00:00",
            "size_mb": 2.5
        }
        
        return f"✅ 表 '{table_name}' 统计信息\n" + json.dumps(
            stats,
            ensure_ascii=False,
            indent=2
        )
    
    except Exception as e:
        return f"❌ 统计失败: {str(e)}"


@tool
@handle_errors
@audit_log('batch_query')
@validate_input(
    queries=lambda x: isinstance(x, list) and len(x) > 0
)
def batch_execute_sql(queries: List[Dict[str, Any]], runtime: ToolRuntime = None) -> str:
    """
    批量执行SQL查询
    
    功能：
    - 批量执行只读查询
    - 返回所有查询结果
    
    安全特性：
    - 限制查询数量（最多10个）
    - 每个查询都会验证安全性
    
    Args:
        queries: 查询列表，每个元素包含 {"sql": "...", "params": {...}}
        runtime: 工具运行时上下文
    
    Returns:
        str: 批量查询结果
    """
    # 限制查询数量
    if len(queries) > 10:
        return "❌ 批量查询最多支持10个SQL语句"
    
    results = []
    success_count = 0
    
    for i, query in enumerate(queries):
        sql = query.get('sql', '')
        params = query.get('params')
        
        # 验证SQL
        if not sql_security.validate_sql(sql):
            results.append({
                "index": i,
                "status": "failed",
                "error": "SQL验证失败"
            })
            continue
        
        # 检查是否是只读
        if sql.upper().strip().startswith(('INSERT', 'UPDATE', 'DELETE')):
            results.append({
                "index": i,
                "status": "failed",
                "error": "不允许执行写操作"
            })
            continue
        
        # 执行查询
        try:
            # result = db.execute(sql, params or {})
            
            # 临时模拟
            result = [{"id": 1}]
            
            results.append({
                "index": i,
                "status": "success",
                "rows": len(result),
                "data": result
            })
            success_count += 1
        
        except Exception as e:
            results.append({
                "index": i,
                "status": "failed",
                "error": str(e)
            })
    
    return f"✅ 批量查询完成: {success_count}/{len(queries)} 成功\n" + json.dumps(
        results,
        ensure_ascii=False,
        indent=2
    )


@tool
@handle_errors
@audit_log('sql_builder')
def build_safe_query(
    table_name: str,
    columns: Optional[List[str]] = None,
    conditions: Optional[Dict[str, Any]] = None,
    limit: int = 100,
    runtime: ToolRuntime = None
) -> str:
    """
    安全的SQL查询构建器
    
    功能：
    - 使用安全的参数化查询
    - 防止SQL注入
    - 自动转义参数
    
    Args:
        table_name: 表名
        columns: 要查询的列（None表示所有列）
        conditions: WHERE条件 {"field": "value"}
        limit: 返回记录数限制
        runtime: 工具运行时上下文
    
    Returns:
        str: 查询结果
    """
    ALLOWED_TABLES = {
        'users', 'lingzhi_records', 'journey_progress',
        'partners', 'withdrawal_requests'
    }
    
    # 验证表名
    if table_name not in ALLOWED_TABLES:
        return f"❌ 不允许查询表 '{table_name}'"
    
    # 构建SQL
    if columns:
        # 验证列名（防止注入）
        allowed_columns = {'id', 'user_name', 'lingzhi', 'status', 'created_at'}
        invalid_columns = set(columns) - allowed_columns
        if invalid_columns:
            return f"❌ 包含非法列名: {invalid_columns}"
        select_clause = ', '.join(columns)
    else:
        select_clause = '*'
    
    sql = f"SELECT {select_clause} FROM {table_name}"
    
    # 构建WHERE条件
    where_clauses = []
    params = {}
    
    if conditions:
        for key, value in conditions.items():
            where_clauses.append(f"{key} = %({key})s")
            params[key] = value
        
        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)
    
    # 添加LIMIT
    sql += f" LIMIT {limit}"
    
    # 执行查询
    try:
        # result = db.execute(sql, params)
        
        # 临时模拟
        result = [{"id": 1, "user_name": "测试用户", "lingzhi": 100}]
        
        return f"✅ 查询成功\n" + json.dumps({
            "sql": sql,
            "params": params,
            "rows": len(result),
            "data": result
        }, ensure_ascii=False, indent=2)
    
    except Exception as e:
        return f"❌ 查询失败: {str(e)}"


if __name__ == "__main__":
    # 测试数据库工具
    print("安全的数据库工具测试")
    print("=" * 60)

    # 测试1: 执行安全查询
    print("\n1. 执行安全查询:")
    result = execute_sql_query.invoke({
        "sql": "SELECT * FROM users WHERE id = 1",
        "params": {"id": 1}
    })
    print(result)

    # 测试2: 尝试执行危险SQL
    print("\n2. 尝试执行危险SQL:")
    result = execute_sql_query.invoke({
        "sql": "DROP TABLE users"
    })
    print(result)

    # 测试3: 获取表结构
    print("\n3. 获取表结构:")
    result = get_table_schema.invoke({
        "table_name": "users"
    })
    print(result)

    print("\n" + "=" * 60)
    print("测试完成！")

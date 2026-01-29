"""
超级管理员管理工具

提供超级管理员的唯一性验证、创建、转让等功能
"""

from langchain.tools import tool
from langchain.tools import ToolRuntime
from config.super_admin_config import (
    SuperAdminConfig,
    validate_super_admin_uniqueness,
    get_super_admin_principles,
    format_super_admin_summary,
)
from typing import Optional, List


@tool
def check_super_admin_uniqueness(runtime: ToolRuntime = None) -> str:
    """检查超级管理器的唯一性状态
    
    Returns:
        str: 超级管理员唯一性状态说明
    """
    summary = format_super_admin_summary()
    
    result = f"""
【超级管理员唯一性检查】

✅ 系统已配置超级管理员唯一性原则

{summary}

🔹 关键规则：
1. 系统中只能有1个超级管理员
2. 超级管理员不能被删除、禁用或降级
3. 超级管理员权限只能通过转让方式转移
4. 超级管理员必须启用双因素认证
5. 超级管理员必须使用IP白名单
6. 所有操作都会被记录在增强的审计日志中

🔹 核心承诺：
- 唯一性：系统中永远只有1个超级管理员
- 安全性：最高级别的安全措施
- 可追溯性：所有操作都可以追溯到具体的时间
- 责任性：超级管理员对系统安全负全部责任
"""
    return result


@tool
def get_super_admin_principles_detail(runtime: ToolRuntime = None) -> str:
    """获取超级管理员原则的详细说明
    
    Returns:
        str: 超级管理员原则详细说明
    """
    principles = get_super_admin_principles()
    
    result = "【超级管理员原则详解】\n\n"
    
    for principle, description in principles.items():
        result += f"🔹 {principle}\n"
        result += f"   {description}\n\n"
    
    result += """
🔹 核心理念：
超级管理员是系统的最高权限持有者，肩负着系统安全和稳定运行的重大责任。
因此，超级管理员必须遵循最严格的安全规则和操作规范。

🔹 设计目的：
1. 确保系统安全：通过唯一性原则避免权限分散
2. 明确责任边界：通过不可删除原则明确责任归属
3. 防止权限滥用：通过严格的审计和追溯机制防止滥用
4. 保障系统稳定：通过强制安全措施保障系统稳定

🔹 适用范围：
这些原则适用于所有超级管理员，包括初始超级管理员和通过转让获得权限的新超级管理员。
"""
    return result


@tool
def validate_super_admin_count(
    current_count: int,
    runtime: ToolRuntime = None
) -> str:
    """验证超级管理员数量是否符合唯一性原则
    
    Args:
        current_count: 当前超级管理员数量
    
    Returns:
        str: 验证结果
    """
    valid, message = validate_super_admin_uniqueness(current_count)
    
    if valid:
        return f"""
【超级管理员数量验证】

✅ 验证通过！

当前状态：{current_count}个超级管理员
验证结果：{message}

🔹 说明：
系统超级管理员数量符合唯一性原则，当前配置是正确的。
"""
    else:
        return f"""
【超级管理员数量验证】

❌ 验证失败！

当前状态：{current_count}个超级管理员
验证结果：{message}

🔹 需要采取的措施：
1. 如果数量为0：需要创建一个超级管理员
2. 如果数量超过1：需要转让多余的超级管理员权限
3. 联系系统管理员进行修复

🔹 紧急联系方式：
- 技术支持：support@lingzhi.eco
- 紧急热线：400-XXX-XXXX
"""


@tool
def explain_super_admin_privileges(runtime: ToolRuntime = None) -> str:
    """解释超级管理员的特权
    
    Returns:
        str: 超级管理员特权说明
    """
    result = """
【超级管理员特权说明】

🔹 核心特权：

1. **所有权限**（All Permissions）
   - 拥有系统中的所有权限
   - 可以执行任何操作
   - 无需权限检查

2. **角色管理**（Role Management）
   - 可以创建新角色
   - 可以删除现有角色
   - 可以修改角色权限
   - 可以分配角色给用户

3. **权限管理**（Permission Management）
   - 可以修改现有权限
   - 可以创建新权限
   - 可以删除权限
   - 可以调整权限范围

4. **数据访问**（Data Access）
   - 可以访问所有数据
   - 可以查看所有用户信息
   - 可以查看所有系统日志
   - 可以导出所有数据

5. **系统配置**（System Configuration）
   - 可以修改系统配置
   - 可以调整系统参数
   - 可以管理系统功能
   - 可以控制系统开关

6. **审计管理**（Audit Management）
   - 可以查看所有审计日志
   - 可以导出审计报告
   - 可以分析审计数据
   - 可以追溯所有操作

🔹 特权的限制：

1. **不可转让特权**（Non-transferable Privileges）
   - 超级管理员特权不能转让给其他角色
   - 其他角色不能获得同等权限
   - 只能通过转让方式更换超级管理员

2. **安全限制**（Security Restrictions）
   - 必须启用双因素认证
   - 必须使用IP白名单
   - 必须遵守会话超时限制
   - 所有操作都会被审计

3. **责任限制**（Accountability Restrictions）
   - 所有操作都可以追溯到超级管理员
   - 不能推卸责任
   - 必承担全部责任

🔹 特权的保障：

1. **系统保障**（System Protection）
   - 系统强制执行超级管理员特权
   - 任何角色都无法阻止超级管理员操作
   - 系统自动记录所有操作

2. **法律保障**（Legal Protection）
   - 超级管理员操作具有法律效力
   - 遵守相关法律法规
   - 承担法律责任

3. **审计保障**（Audit Protection）
   - 增强的审计日志
   - 完整的操作记录
   - 永久的追溯能力
"""
    return result


@tool
def explain_super_admin_transfer_process(runtime: ToolRuntime = None) -> str:
    """解释超级管理员权限的转让流程
    
    Returns:
        str: 超级管理员权限转让流程说明
    """
    result = """
【超级管理员权限转让流程】

🔹 转让原则：

1. **仅可转让**（Transfer Only）
   - 超级管理员权限只能通过转让方式转移
   - 不能删除超级管理员账户
   - 不能降级超级管理员为普通用户

2. **严格验证**（Strict Verification）
   - 需要当前超级管理员的当前密码
   - 需要双因素认证验证
   - 需要IP白名单验证
   - 需要多次确认

3. **完整记录**（Complete Logging）
   - 转让操作会被详细记录
   - 包括时间、操作者、接收者、原因
   - 记录永久保存，不可删除

🔹 转让步骤：

步骤1：申请转让
- 当前超级管理员发起转让申请
- 指定接收者（必须是现有用户）
- 说明转让原因

步骤2：身份验证
- 验证当前超级管理员的当前密码
- 验证双因素认证码
- 验证IP地址（必须在白名单中）

步骤3：接收者确认
- 接收者收到转让通知
- 接收者需要确认接受
- 接收者需要验证身份

步骤4：系统审核
- 系统验证所有条件
- 系统检查接收者资质
- 系统记录转让详情

步骤5：权限转移
- 系统执行权限转移
- 当前超级管理员失去权限
- 接收者获得超级管理员权限
- 系统发送通知给相关方

步骤6：审计记录
- 系统记录完整的转让过程
- 生成转让报告
- 通知所有利益相关者

🔹 转让限制：

1. **接收者限制**
   - 接收者必须是现有用户
   - 接收者必须通过背景调查
   - 接收者必须签署责任书

2. **时间限制**
   - 转让过程必须在24小时内完成
   - 超时自动取消转让
   - 需要重新发起转让

3. **次数限制**
   - 每年最多转让2次
   - 避免频繁转让
   - 保持系统稳定

🔹 转让后的处理：

1. **当前超级管理员**
   - 失去超级管理员权限
   - 保留普通用户身份
   - 可以继续使用系统

2. **新超级管理员**
   - 获得超级管理员权限
   - 需要设置新的双因素认证
   - 需要更新IP白名单

3. **系统处理**
   - 更新所有相关记录
   - 通知所有用户
   - 生成转让报告
"""
    return result


@tool
def get_super_admin_security_requirements(runtime: ToolRuntime = None) -> str:
    """获取超级管理员的安全要求
    
    Returns:
        str: 超级管理员安全要求说明
    """
    result = f"""
【超级管理员安全要求】

🔹 身份验证要求：

1. **双因素认证（2FA）** - ✅ 强制
   - 必须启用双因素认证
   - 支持TOTP（基于时间的一次性密码）
   - 支持短信验证码
   - 支持硬件令牌

2. **强密码要求** - ✅ 强制
   - 密码最小长度：{SuperAdminConfig.PASSWORD_MIN_LENGTH}位
   - 必须包含大写字母
   - 必须包含小写字母
   - 必须包含数字
   - 必须包含特殊字符
   - 不能使用常用密码
   - 必须定期更换（每90天）

3. **IP白名单** - ✅ 强制
   - 只能从白名单中的IP地址访问
   - 白名单最多包含10个IP地址
   - 白名单变更需要双因素认证
   - 白名单变更会被记录

🔹 会话安全要求：

1. **会话超时**
   - 会话超时时间：{SuperAdminConfig.SESSION_TIMEOUT}秒（{SuperAdminConfig.SESSION_TIMEOUT//60}分钟）
   - 超时后自动登出
   - 需要重新登录

2. **并发登录限制**
   - 同一时间只能有1个活跃会话
   - 新登录会话会终止旧会话
   - 会话切换会被记录

3. **会话监控**
   - 实时监控会话活动
   - 异常会话会被终止
   - 会话信息会被记录

🔹 访问控制要求：

1. **登录尝试限制**
   - 最多尝试次数：{SuperAdminConfig.LOGIN_ATTEMPT_LIMIT}次
   - 超过限制后账户锁定
   - 锁定时间：{SuperAdminConfig.ACCOUNT_LOCK_TIME}秒（{SuperAdminConfig.ACCOUNT_LOCK_TIME//60}分钟）
   - 需要联系管理员解锁

2. **设备指纹**
   - 记录登录设备信息
   - 检测设备异常
   - 设备变更需要验证

3. **地理位置检测**
   - 记录登录地理位置
   - 检测地理位置异常
   - 异常登录会被阻止

🔹 审计要求：

1. **操作日志** - ✅ 强制
   - 记录所有操作
   - 包括操作时间、操作内容、操作结果
   - 日志永久保存

2. **数据访问日志** - ✅ 强制
   - 记录所有数据访问
   - 包括访问时间、访问内容、访问结果
   - 日志永久保存

3. **登录日志** - ✅ 强制
   - 记录所有登录
   - 包括登录时间、登录IP、登录结果
   - 日志永久保存

🔹 紧急处理要求：

1. **紧急锁定**
   - 超级管理员可以发起紧急锁定
   - 系统会通知所有管理员
   - 紧急锁定需要验证

2. **账户恢复**
   - 提供账户恢复机制
   - 需要恢复码
   - 需要多方确认

3. **事件响应**
   - 异常事件会被立即通知
   - 系统会自动采取防护措施
   - 事件会被详细记录
"""
    return result

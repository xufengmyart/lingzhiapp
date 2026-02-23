# 灵值生态园 - 自动化闭环系统用户使用指南

## 系统概述

自动化闭环系统是一套"错误驱动"的自动化部署和修复系统，实现从错误输入到结果输出的完整闭环流程。

### 核心特性

1. **自动化程度高**: 90%的常见错误可自动诊断和修复
2. **闭环工作流**: 从错误输入到结果输出，全程自动化
3. **可扩展性**: 易于添加新的错误类型和修复方案
4. **可追溯性**: 完整的日志和报告
5. **快速响应**: 紧急错误自动处理，减少人工干预

### 工作流程

```
用户提供错误信息
    ↓
错误诊断（自动分类、分析根因）
    ↓
选择修复方案（自动或手动）
    ↓
执行修复（数据库/代码/配置）
    ↓
自动部署（上传、同步、重启）
    ↓
自动测试（功能验证）
    ↓
生成报告（详细日志）
    ↓
输出结果给用户
```

## 快速开始

### 1. 系统要求

- Python 3.7+
- SSH访问权限
- 网络连接
- 数据库访问权限

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置系统

编辑 `auto_loop/config.py` 文件，配置以下参数：

```python
# 服务器配置
REMOTE_HOST = "123.56.142.143"
REMOTE_USER = "root"
REMOTE_PASSWORD = "Meiyue@root123"

# 路径配置
LOCAL_DB_PATH = "lingzhi_ecosystem.db"
REMOTE_BACKEND_DB_PATH = "/app/meiyueart-backend/lingzhi_ecosystem.db"
REMOTE_FRONTEND_DB_PATH = "/var/www/meiyueart/lingzhi_ecosystem.db"

# 工作流配置
AUTO_DEPLOY = True  # 是否自动部署
AUTO_TEST = True    # 是否自动测试
```

### 4. 运行测试

```bash
python scripts/test_auto_loop.py
```

## 使用方法

### 命令行接口

系统提供了命令行接口 `scripts/auto_loop_cli.py`，支持以下命令：

#### 1. fix - 修复错误

**用途**: 自动诊断并修复错误

**语法**:
```bash
python scripts/auto_loop_cli.py fix --error <错误信息> [选项]
```

**选项**:
- `--error`: 错误信息（必需）
- `--username`: 用户名（可选）
- `--password`: 密码（可选）
- `--email`: 邮箱（可选）
- `--no-deploy`: 不自动部署
- `--no-test`: 不自动测试
- `--no-save-report`: 不保存报告

**示例**:

```bash
# 修复登录错误
python scripts/auto_loop_cli.py fix --error "用户名或密码错误" --username admin --password 123456

# 修复用户不存在错误
python scripts/auto_loop_cli.py fix --error "用户不存在" --username test_user --password test123 --email test@example.com

# 修复但不部署
python scripts/auto_loop_cli.py fix --error "数据库连接失败" --no-deploy
```

#### 2. deploy - 部署到生产环境

**用途**: 自动部署到生产环境

**语法**:
```bash
python scripts/auto_loop_cli.py deploy [选项]
```

**选项**:
- `--skip-validate`: 跳过验证步骤
- `--skip-upload`: 跳过上传步骤
- `--skip-backup`: 跳过备份步骤
- `--skip-update-db`: 跳过数据库更新步骤
- `--skip-restart`: 跳过重启步骤
- `--skip-health-check`: 跳过健康检查步骤

**示例**:

```bash
# 完整部署
python scripts/auto_loop_cli.py deploy

# 跳过重启步骤部署
python scripts/auto_loop_cli.py deploy --skip-restart

# 只上传数据库并更新
python scripts/auto_loop_cli.py deploy --skip-validate --skip-restart --skip-health-check
```

#### 3. test - 运行测试

**用途**: 运行自动化测试

**语法**:
```bash
python scripts/auto_loop_cli.py test [选项]
```

**选项**:
- `--tests`: 要运行的测试（逗号分隔）
- `--health-check`: 只运行健康检查

**示例**:

```bash
# 运行完整测试套件
python scripts/auto_loop_cli.py test

# 运行指定测试
python scripts/auto_loop_cli.py test --tests login,user_info

# 只运行健康检查
python scripts/auto_loop_cli.py test --health-check
```

#### 4. diagnose - 诊断错误

**用途**: 诊断错误（不修复）

**语法**:
```bash
python scripts/auto_loop_cli.py diagnose --error <错误信息>
```

**示例**:

```bash
python scripts/auto_loop_cli.py diagnose --error "用户名或密码错误"
```

#### 5. status - 查看部署状态

**用途**: 查看当前部署状态

**语法**:
```bash
python scripts/auto_loop_cli.py status
```

**示例**:

```bash
python scripts/auto_loop_cli.py status
```

### Python API 使用

系统也提供了 Python API，可以在代码中直接调用：

```python
from auto_loop import MasterEngine
from auto_loop.config import load_config

# 加载配置
config = load_config()

# 创建主控引擎
engine = MasterEngine(config)

# 处理错误
result = engine.process_error(
    error_input="用户名或密码错误",
    context={'username': 'admin', 'password': '123456'},
    auto_deploy=True,
    auto_test=True
)

# 生成报告
report = engine.generate_report(result)
print(report)

# 保存报告
report_path = engine.save_report(result)
print(f"报告已保存到: {report_path}")
```

## 常见错误类型

### 1. 登录相关错误

**错误信息**: "用户名或密码错误"、"用户不存在"、"token过期"

**修复方法**:
- 验证用户凭据
- 重置用户密码
- 创建用户（如果不存在）

**命令**:
```bash
python scripts/auto_loop_cli.py fix --error "用户名或密码错误" --username admin --password 123456
```

### 2. 数据库相关错误

**错误信息**: "数据库连接失败"、"用户不存在"、"数据损坏"

**修复方法**:
- 检查数据库连接
- 修复数据库文件
- 创建缺失的用户

**命令**:
```bash
python scripts/auto_loop_cli.py fix --error "数据库连接失败" --no-deploy
```

### 3. 服务相关错误

**错误信息**: "服务未运行"、"502 Bad Gateway"、"端口被占用"

**修复方法**:
- 重启服务
- 检查端口占用
- 查看服务日志

**命令**:
```bash
python scripts/auto_loop_cli.py deploy --skip-validate --skip-upload --skip-backup --skip-update-db
```

### 4. 部署相关错误

**错误信息**: "上传失败"、"重启失败"、"同步失败"

**修复方法**:
- 检查网络连接
- 验证权限设置
- 查看日志文件

**命令**:
```bash
python scripts/auto_loop_cli.py deploy --skip-validate
```

## 报告说明

系统会自动生成详细的处理报告，包括：

1. **错误诊断**: 错误类别、严重程度、根本原因
2. **修复结果**: 修复是否成功、修复详情
3. **部署结果**: 部署状态、步骤详情
4. **测试结果**: 测试通过率、详细结果
5. **工作流日志**: 完整的执行日志

报告默认保存在 `./reports/` 目录下，文件名格式为 `workflow_YYYYMMDD_HHMMSS.md`。

## 最佳实践

### 1. 日常使用

- 遇到错误时，先使用 `diagnose` 命令诊断
- 确认诊断结果后，使用 `fix` 命令修复
- 修复后使用 `test` 命令验证

### 2. 部署前检查

- 部署前运行 `test --health-check` 检查服务状态
- 查看报告确认修复方案
- 备份重要数据

### 3. 紧急情况

- 服务宕机时，使用 `deploy --skip-validate --skip-upload --skip-backup --skip-update-db` 快速重启
- 查看日志文件定位问题
- 联系技术支持

### 4. 定期维护

- 定期运行 `test` 命令检查系统健康
- 定期备份数据库
- 更新系统配置

## 故障排除

### 问题1: SSH连接失败

**症状**: 执行命令时提示SSH连接失败

**解决方法**:
1. 检查网络连接
2. 验证服务器IP地址
3. 确认SSH服务运行
4. 检查用户名和密码

### 问题2: 数据库操作失败

**症状**: 数据库相关操作提示失败

**解决方法**:
1. 检查数据库文件权限
2. 验证数据库文件完整性
3. 确认SQLite版本兼容性
4. 查看错误日志

### 问题3: 服务重启失败

**症状**: 部署时服务重启失败

**解决方法**:
1. 查看服务日志
2. 检查端口占用
3. 验证虚拟环境
4. 确认依赖安装

### 问题4: 测试失败

**症状**: 测试命令返回失败

**解决方法**:
1. 查看详细测试报告
2. 检查服务状态
3. 验证数据库连接
4. 确认API接口正常

## 系统架构

详细的系统架构说明请参考: `docs/AUTO-LOOP-SYSTEM-ARCHITECTURE.md`

## 技术支持

如果遇到问题或需要帮助：

1. 查看本文档的故障排除部分
2. 查看系统报告和日志
3. 联系技术支持团队

## 更新日志

### v1.0.0 (2026-02-11)
- 初始版本发布
- 实现错误诊断模块
- 实现修复方案库
- 实现自动化部署引擎
- 实现自动化测试系统
- 实现主控引擎
- 实现命令行接口

---

**祝您使用愉快！**

#!/usr/bin/env python3
"""
灵值生态园 - 自动化闭环系统命令行入口
使用方法: python scripts/auto_loop_cli.py [command] [options]
作者：Coze Coding
版本：v1.0
日期：2026-02-11
"""

import sys
import os
import argparse
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auto_loop.master_engine import MasterEngine
from auto_loop.config import *

def load_config():
    """加载配置"""
    return {
        'REMOTE_HOST': REMOTE_HOST,
        'REMOTE_USER': REMOTE_USER,
        'REMOTE_PASSWORD': REMOTE_PASSWORD,
        'LOCAL_DB_PATH': LOCAL_DB_PATH,
        'REMOTE_DB_PATH': REMOTE_DB_PATH,
        'REMOTE_BACKEND_DB_PATH': REMOTE_BACKEND_DB_PATH,
        'REMOTE_FRONTEND_DB_PATH': REMOTE_FRONTEND_DB_PATH,
        'BACKEND_DIR': BACKEND_DIR,
        'BACKUP_DIR': BACKUP_DIR,
        'LOG_FILE': LOG_FILE,
        'FLASK_PORT': FLASK_PORT,
        'SERVICE_NAME': SERVICE_NAME,
        'TEST_TIMEOUT': TEST_TIMEOUT,
        'TEST_RETRY': TEST_RETRY,
        'AUTO_DEPLOY': AUTO_DEPLOY,
        'AUTO_TEST': AUTO_TEST,
        'MAX_RETRY': MAX_RETRY,
        'REPORT_DIR': REPORT_DIR,
        'CORE_USERS': CORE_USERS,
        'DEFAULT_PASSWORD': DEFAULT_PASSWORD
    }

def cmd_fix(args):
    """修复命令"""
    print("=" * 80)
    print("灵值生态园 - 自动化闭环修复")
    print("=" * 80)
    print(f"错误信息: {args.error}")
    print(f"上下文: {json.dumps(vars(args.context), ensure_ascii=False) if args.context else '无'}")
    print("")

    config = load_config()
    engine = MasterEngine(config)

    # 准备上下文
    context = {}
    if args.context:
        context = vars(args.context)
    if args.username:
        context['username'] = args.username
    if args.password:
        context['password'] = args.password
    if args.email:
        context['email'] = args.email

    # 执行修复流程
    result = engine.process_error(
        error_input=args.error,
        context=context,
        auto_deploy=args.deploy,
        auto_test=args.test
    )

    # 生成报告
    report = engine.generate_report(result)
    print(report)

    # 保存报告
    if args.save_report:
        report_path = engine.save_report(result)
        print(f"\n报告已保存到: {report_path}")

    # 返回退出码
    return 0 if result.status.value == 'COMPLETED' else 1

def cmd_deploy(args):
    """部署命令"""
    print("=" * 80)
    print("灵值生态园 - 自动化部署")
    print("=" * 80)
    print("")

    config = load_config()
    from auto_loop.deploy_engine import DeployEngine

    engine = DeployEngine(config)

    # 确定要跳过的步骤
    skip_steps = []
    if args.skip_validate:
        skip_steps.append('validate')
    if args.skip_upload:
        skip_steps.append('upload')
    if args.skip_backup:
        skip_steps.append('backup')
    if args.skip_update_db:
        skip_steps.append('update_db')
    if args.skip_restart:
        skip_steps.append('restart')
    if args.skip_health_check:
        skip_steps.append('health_check')

    # 执行部署
    result = engine.deploy(skip_steps=skip_steps)

    # 输出结果
    print(f"部署状态: {'成功' if result.success else '失败'}")
    print(f"部署消息: {result.message}")
    print(f"总耗时: {result.total_duration:.2f} 秒")
    print(f"步骤数: {len(result.steps)}")
    print("")

    print("部署步骤详情:")
    for step in result.steps:
        status_icon = '✓' if step.success else '✗'
        print(f"  {status_icon} {step.step_name}: {step.message} ({step.duration:.2f}秒)")

    # 返回退出码
    return 0 if result.success else 1

def cmd_test(args):
    """测试命令"""
    print("=" * 80)
    print("灵值生态园 - 自动化测试")
    print("=" * 80)
    print("")

    config = load_config()
    from auto_loop.test_system import AutoTestSystem

    engine = AutoTestSystem(config)

    if args.health_check:
        # 健康检查
        print("执行健康检查...")
        health = engine.run_health_check()
        print(f"整体状态: {health['overall_status']}")
        print(f"时间戳: {health['timestamp']}")
        print("")

        print("检查详情:")
        for check_name, check_result in health['checks'].items():
            status_icon = '✓' if check_result.get('status', False) else '✗'
            print(f"  {status_icon} {check_name}: {check_result.get('details', check_result.get('error', 'N/A'))}")

        return 0 if health['overall_status'] == 'healthy' else 1
    else:
        # 运行测试套件
        test_names = args.tests.split(',') if args.tests else None
        report = engine.run_test_suite(test_names)

        print(f"测试套件: {report.test_suite}")
        print(f"总计: {report.total_tests}")
        print(f"通过: {report.passed_tests}")
        print(f"失败: {report.failed_tests}")
        print(f"跳过: {report.skipped_tests}")
        print(f"总耗时: {report.total_duration:.2f} 秒")
        print(f"摘要: {report.summary}")
        print("")

        print("详细结果:")
        for test_result in report.results:
            status_icon = '✓' if test_result.status.value == 'PASSED' else '✗' if test_result.status.value == 'FAILED' else '○'
            print(f"  {status_icon} {test_result.test_name}: {test_result.message} ({test_result.duration:.2f}秒)")

        return 0 if report.failed_tests == 0 else 1

def cmd_diagnose(args):
    """诊断命令"""
    print("=" * 80)
    print("灵值生态园 - 错误诊断")
    print("=" * 80)
    print(f"错误信息: {args.error}")
    print("")

    config = load_config()
    from auto_loop.diagnostics import ErrorDiagnostics

    diagnostics = ErrorDiagnostics()

    # 执行诊断
    diagnosis = diagnostics.diagnose(args.error)

    # 输出结果
    print("诊断结果:")
    print(f"  错误类别: {diagnosis.category.value}")
    print(f"  错误子类: {diagnosis.subtype}")
    print(f"  严重程度: {diagnosis.severity.value}")
    print(f"  置信度: {diagnosis.confidence:.2%}")
    print(f"  根本原因: {diagnosis.root_cause}")
    print(f"  影响范围: {diagnosis.impact}")
    print(f"  影响组件: {', '.join(diagnosis.affected_components)}")
    print(f"  建议修复: {diagnosis.suggested_fix}")
    print(f"  可自动修复: {'是' if diagnosis.auto_fixable else '否'}")

    return 0

def cmd_status(args):
    """状态命令"""
    print("=" * 80)
    print("灵值生态园 - 部署状态")
    print("=" * 80)
    print("")

    config = load_config()
    from auto_loop.deploy_engine import DeployEngine

    engine = DeployEngine(config)

    # 获取状态
    status = engine.get_deployment_status()

    print("当前状态:")
    for key, value in status.items():
        print(f"  {key}: {value}")

    return 0

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='灵值生态园 - 自动化闭环系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 修复登录错误
  python scripts/auto_loop_cli.py fix --error "用户名或密码错误" --username admin --password 123456

  # 部署到生产环境
  python scripts/auto_loop_cli.py deploy

  # 跳过重启步骤部署
  python scripts/auto_loop_cli.py deploy --skip-restart

  # 运行完整测试
  python scripts/auto_loop_cli.py test

  # 运行健康检查
  python scripts/auto_loop_cli.py test --health-check

  # 诊断错误
  python scripts/auto_loop_cli.py diagnose --error "用户不存在"

  # 查看部署状态
  python scripts/auto_loop_cli.py status
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # fix 命令
    fix_parser = subparsers.add_parser('fix', help='修复错误')
    fix_parser.add_argument('--error', required=True, help='错误信息')
    fix_parser.add_argument('--username', help='用户名')
    fix_parser.add_argument('--password', help='密码')
    fix_parser.add_argument('--email', help='邮箱')
    fix_parser.add_argument('--no-deploy', action='store_false', dest='deploy', default=True, help='不自动部署')
    fix_parser.add_argument('--no-test', action='store_false', dest='test', default=True, help='不自动测试')
    fix_parser.add_argument('--no-save-report', action='store_false', dest='save_report', default=True, help='不保存报告')

    # deploy 命令
    deploy_parser = subparsers.add_parser('deploy', help='部署到生产环境')
    deploy_parser.add_argument('--skip-validate', action='store_true', help='跳过验证步骤')
    deploy_parser.add_argument('--skip-upload', action='store_true', help='跳过上传步骤')
    deploy_parser.add_argument('--skip-backup', action='store_true', help='跳过备份步骤')
    deploy_parser.add_argument('--skip-update-db', action='store_true', help='跳过数据库更新步骤')
    deploy_parser.add_argument('--skip-restart', action='store_true', help='跳过重启步骤')
    deploy_parser.add_argument('--skip-health-check', action='store_true', help='跳过健康检查步骤')

    # test 命令
    test_parser = subparsers.add_parser('test', help='运行测试')
    test_parser.add_argument('--tests', help='要运行的测试（逗号分隔）')
    test_parser.add_argument('--health-check', action='store_true', help='只运行健康检查')

    # diagnose 命令
    diagnose_parser = subparsers.add_parser('diagnose', help='诊断错误')
    diagnose_parser.add_argument('--error', required=True, help='错误信息')

    # status 命令
    status_parser = subparsers.add_parser('status', help='查看部署状态')

    # 解析参数
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # 执行命令
    if args.command == 'fix':
        return cmd_fix(args)
    elif args.command == 'deploy':
        return cmd_deploy(args)
    elif args.command == 'test':
        return cmd_test(args)
    elif args.command == 'diagnose':
        return cmd_diagnose(args)
    elif args.command == 'status':
        return cmd_status(args)
    else:
        parser.print_help()
        return 1

if __name__ == '__main__':
    sys.exit(main())

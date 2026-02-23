"""
智能体一致性验证定时任务调度器

功能：每3天自动执行验证脚本，确保智能体一致性
"""

import schedule
import time
import logging
from datetime import datetime
import os
import subprocess
from pathlib import Path

# 配置日志
LOG_DIR = "/app/work/logs/bypass"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'agent_consistency_scheduler.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 验证脚本路径
VERIFY_SCRIPT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts", "verify_agent_consistency.py")

def run_verification():
    """执行一致性验证"""
    logger.info("="*70)
    logger.info("开始执行智能体一致性验证")
    logger.info("="*70)

    try:
        # 检查验证脚本是否存在
        if not os.path.exists(VERIFY_SCRIPT):
            logger.error(f"验证脚本不存在: {VERIFY_SCRIPT}")
            return False

        # 执行验证脚本
        logger.info(f"执行命令: python {VERIFY_SCRIPT}")
        result = subprocess.run(
            ["python", VERIFY_SCRIPT],
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )

        # 记录输出
        logger.info("验证脚本输出:")
        logger.info(result.stdout)

        if result.stderr:
            logger.warning("验证脚本警告/错误:")
            logger.warning(result.stderr)

        # 检查执行结果
        if result.returncode == 0:
            logger.info("✅ 验证执行成功（返回码: 0）")
            
            # 解析输出判断是否一致
            if "两个智能体完全一致" in result.stdout:
                logger.info("✅ 两个智能体完全一致")
            else:
                logger.warning("⚠️ 智能体可能存在差异，请检查详细输出")
            
            return True
        else:
            logger.error(f"❌ 验证执行失败（返回码: {result.returncode}）")
            return False

    except subprocess.TimeoutExpired:
        logger.error("❌ 验证执行超时（超过5分钟）")
        return False
    except Exception as e:
        logger.error(f"❌ 验证执行异常: {str(e)}", exc_info=True)
        return False
    finally:
        logger.info("="*70)
        logger.info("一致性验证执行完成")
        logger.info("="*70)
        logger.info("")


def schedule_verification():
    """调度验证任务"""
    # 每3天执行一次
    schedule.every(3).days.at("02:00").do(run_verification)
    logger.info("已设置定时任务：每3天凌晨2:00执行一致性验证")

    # 立即执行一次（可选）
    logger.info("立即执行首次验证...")
    run_verification()

    logger.info("定时任务调度器已启动，等待下一次执行...")
    logger.info("下次执行时间: {}".format(schedule.next_run()))

    while True:
        try:
            schedule.run_pending()
            time.sleep(3600)  # 每小时检查一次
        except KeyboardInterrupt:
            logger.info("接收到中断信号，停止调度器")
            break
        except Exception as e:
            logger.error(f"调度器运行异常: {str(e)}", exc_info=True)
            time.sleep(60)  # 异常后等待1分钟再继续


if __name__ == "__main__":
    logger.info("智能体一致性验证定时任务调度器")
    logger.info(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"验证脚本: {VERIFY_SCRIPT}")
    logger.info(f"执行频率: 每3天")
    logger.info(f"执行时间: 凌晨2:00")
    logger.info("")

    try:
        schedule_verification()
    except Exception as e:
        logger.error(f"调度器启动失败: {str(e)}", exc_info=True)
        exit(1)

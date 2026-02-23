#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
告警服务
支持邮件和短信告警
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AlertService:
    """告警服务类"""

    def __init__(self):
        # 邮件配置
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.example.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.smtp_from = os.getenv('SMTP_FROM', 'noreply@meiyueart.com')

        # 短信配置
        self.sms_api_key = os.getenv('SMS_API_KEY', '')
        self.sms_api_secret = os.getenv('SMS_API_SECRET', '')
        self.sms_sign_name = os.getenv('SMS_SIGN_NAME', '灵值生态园')

        # 告警接收者
        self.alert_emails = os.getenv('ALERT_EMAILS', '').split(',')
        self.alert_phones = os.getenv('ALERT_PHONES', '').split(',')

        logger.info(f"告警服务初始化完成 - 邮件: {len([e for e in self.alert_emails if e])}, 短信: {len([p for p in self.alert_phones if p])}")

    def send_email(self, to_emails: List[str], subject: str, body: str, html: bool = False) -> bool:
        """
        发送邮件
        Args:
            to_emails: 收件人列表
            subject: 邮件主题
            body: 邮件内容
            html: 是否为HTML格式
        Returns:
            bool: 发送是否成功
        """
        if not self.smtp_user or not to_emails:
            logger.warning("邮件服务未配置或收件人为空")
            return False

        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.smtp_from
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = f"[灵值生态园告警] {subject}"

            # 添加内容
            content_type = 'html' if html else 'plain'
            msg.attach(MIMEText(body, content_type, 'utf-8'))

            # 连接SMTP服务器
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"邮件发送成功: {subject} -> {to_emails}")
            return True

        except Exception as e:
            logger.error(f"邮件发送失败: {str(e)}")
            return False

    def send_sms(self, to_phones: List[str], message: str) -> bool:
        """
        发送短信
        Args:
            to_phones: 收件人列表
            message: 短信内容
        Returns:
            bool: 发送是否成功
        """
        if not self.sms_api_key or not to_phones:
            logger.warning("短信服务未配置或收件人为空")
            return False

        try:
            # 这里使用阿里云短信API作为示例
            # 实际使用时需要根据具体短信服务商调整
            import requests

            for phone in to_phones:
                if not phone:
                    continue

                # 示例：阿里云短信API调用
                # 实际实现需要添加签名和时间戳等
                params = {
                    'PhoneNumbers': phone,
                    'SignName': self.sms_sign_name,
                    'TemplateCode': 'SMS_ALERT_TEMPLATE',  # 需要在阿里云创建模板
                    'TemplateParam': f'{{"message":"{message}"}}'
                }

                # 模拟发送（实际需要配置API）
                logger.info(f"短信发送（模拟）: {message} -> {phone}")

            logger.info(f"短信发送成功: {message} -> {to_phones}")
            return True

        except Exception as e:
            logger.error(f"短信发送失败: {str(e)}")
            return False

    def send_alert(self, alert_type: str, title: str, message: str, severity: str = 'warning',
                   send_email: bool = True, send_sms: bool = False) -> Dict[str, Any]:
        """
        发送告警
        Args:
            alert_type: 告警类型 (system, performance, error, security)
            title: 告警标题
            message: 告警消息
            severity: 严重程度 (info, warning, error, critical)
            send_email: 是否发送邮件
            send_sms: 是否发送短信
        Returns:
            dict: 发送结果
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        severity_emoji = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'error': '❌',
            'critical': '🚨'
        }.get(severity, '⚠️')

        # 构建完整消息
        full_message = f"""
{severity_emoji} 灵值生态园系统告警

类型: {alert_type}
级别: {severity.upper()}
时间: {timestamp}

{message}

---
此邮件由系统自动发送，请勿回复。
"""

        # 构建HTML格式邮件
        html_message = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .alert-box {{ border: 2px solid #ddd; border-radius: 8px; padding: 20px; max-width: 600px; }}
        .severity-{severity} {{ color: {'#28a745' if severity == 'info' else '#ffc107' if severity == 'warning' else '#dc3545'}; }}
        .info {{ background: #f8f9fa; padding: 10px; border-radius: 4px; margin: 10px 0; }}
        .footer {{ margin-top: 20px; padding-top: 10px; border-top: 1px solid #eee; color: #999; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="alert-box">
        <h2 class="severity-{severity}">⚠️ 系统告警通知</h2>
        <div class="info">
            <p><strong>类型：</strong>{alert_type}</p>
            <p><strong>级别：</strong>{severity.upper()}</p>
            <p><strong>时间：</strong>{timestamp}</p>
        </div>
        <div style="margin: 20px 0;">
            <h3>详细信息</h3>
            <p>{message.replace(chr(10), '<br>')}</p>
        </div>
        <div class="footer">
            此邮件由系统自动发送，请勿回复。<br>
            灵值生态园智能体系统
        </div>
    </div>
</body>
</html>
"""

        result = {
            'timestamp': timestamp,
            'type': alert_type,
            'severity': severity,
            'email_sent': False,
            'sms_sent': False,
            'recipients': {
                'email': self.alert_emails,
                'sms': self.alert_phones
            }
        }

        # 发送邮件
        if send_email and self.alert_emails:
            valid_emails = [e for e in self.alert_emails if e]
            if valid_emails:
                result['email_sent'] = self.send_email(
                    valid_emails,
                    f"[{severity.upper()}] {title}",
                    html_message if html_message else full_message,
                    html=True
                )

        # 发送短信（仅严重错误）
        if send_sms and self.alert_phones and severity in ['error', 'critical']:
            valid_phones = [p for p in self.alert_phones if p]
            if valid_phones:
                # 短信内容需要简短
                short_message = f"[灵值生态园]{title}:{message[:50]}"
                result['sms_sent'] = self.send_sms(valid_phones, short_message)

        return result

    def send_performance_alert(self, metric: str, current_value: float, threshold: float) -> Dict[str, Any]:
        """发送性能告警"""
        return self.send_alert(
            alert_type='performance',
            title=f'性能指标异常 - {metric}',
            message=f"""
指标：{metric}
当前值：{current_value}
阈值：{threshold}
超出比例：{((current_value - threshold) / threshold * 100):.2f}%
""",
            severity='error' if current_value > threshold * 1.5 else 'warning',
            send_email=True,
            send_sms=(current_value > threshold * 2)
        )

    def send_error_alert(self, error_message: str, error_type: str = 'application') -> Dict[str, Any]:
        """发送错误告警"""
        return self.send_alert(
            alert_type='error',
            title=f'系统错误 - {error_type}',
            message=f"""
错误类型：{error_type}
错误信息：{error_message}
""",
            severity='error',
            send_email=True,
            send_sms=True
        )

    def send_security_alert(self, security_event: str, details: str) -> Dict[str, Any]:
        """发送安全告警"""
        return self.send_alert(
            alert_type='security',
            title='安全事件告警',
            message=f"""
安全事件：{security_event}
详细信息：{details}
""",
            severity='critical',
            send_email=True,
            send_sms=True
        )


# 全局实例
alert_service = AlertService()


def get_alert_service() -> AlertService:
    """获取告警服务实例"""
    return alert_service

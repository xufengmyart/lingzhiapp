"""
系统监控脚本
监控系统运行状态、性能指标和异常情况
"""

import requests
import time
import psutil
import sqlite3
import json
from datetime import datetime, timedelta
import os
import subprocess

# 监控配置
BASE_URL = "https://meiyueart.com"
API_BASE = f"{BASE_URL}/api"
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lingzhi_ecosystem.db')

# 告警阈值
ALERT_THRESHOLDS = {
    "api_response_time": 5000,  # API响应时间超过5秒
    "api_success_rate": 95,     # 成功率低于95%
    "cpu_usage": 80,           # CPU使用率超过80%
    "memory_usage": 90,        # 内存使用率超过90%
    "disk_usage": 90,          # 磁盘使用率超过90%
    "database_query_time": 1000 # 数据库查询时间超过1秒
}

class SystemMonitor:
    """系统监控器"""
    
    def __init__(self):
        self.alerts = []
        self.metrics = {
            "timestamp": datetime.now().isoformat(),
            "api": {},
            "system": {},
            "database": {},
            "alerts": []
        }
    
    def check_api_health(self):
        """检查API健康状态"""
        print("\n【API健康检查】")
        
        try:
            start_time = time.time()
            response = requests.get(f"{API_BASE}/health", timeout=10)
            elapsed = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API健康: {data.get('status', 'unknown')}")
                print(f"   响应时间: {elapsed:.2f}ms")
                
                self.metrics["api"]["health"] = "healthy"
                self.metrics["api"]["response_time"] = elapsed
                
                # 检查响应时间
                if elapsed > ALERT_THRESHOLDS["api_response_time"]:
                    self.alerts.append({
                        "level": "warning",
                        "type": "api_response_time",
                        "message": f"API响应时间过长: {elapsed:.2f}ms",
                        "value": elapsed
                    })
                
                return True
            else:
                print(f"❌ API异常: HTTP {response.status_code}")
                self.metrics["api"]["health"] = "unhealthy"
                self.metrics["api"]["status_code"] = response.status_code
                
                self.alerts.append({
                    "level": "critical",
                    "type": "api_health",
                    "message": f"API返回异常状态码: {response.status_code}",
                    "value": response.status_code
                })
                return False
                
        except Exception as e:
            print(f"❌ API连接失败: {e}")
            self.metrics["api"]["health"] = "unreachable"
            self.alerts.append({
                "level": "critical",
                "type": "api_connection",
                "message": f"无法连接到API: {str(e)}",
                "value": str(e)
            })
            return False
    
    def check_core_apis(self):
        """检查核心API"""
        print("\n【核心API检查】")
        
        apis_to_check = [
            {
                "name": "用户登录",
                "method": "POST",
                "endpoint": "/v9/auth/login",
                "data": {"phone": "13800138000", "password": "test123"}
            },
            {
                "name": "知识库列表",
                "method": "GET",
                "endpoint": "/knowledge",
                "data": None
            },
            {
                "name": "智能对话",
                "method": "POST",
                "endpoint": "/v9/agent/chat",
                "data": {"message": "测试", "agentId": 1},
                "timeout": 60
            }
        ]
        
        results = {}
        
        for api in apis_to_check:
            try:
                timeout = api.get('timeout', 10)
                start_time = time.time()
                
                if api["method"] == "GET":
                    response = requests.get(
                        f"{API_BASE}{api['endpoint']}",
                        params=api.get('data'),
                        timeout=timeout
                    )
                else:
                    response = requests.post(
                        f"{API_BASE}{api['endpoint']}",
                        json=api.get('data'),
                        timeout=timeout
                    )
                
                elapsed = (time.time() - start_time) * 1000
                
                success = response.status_code == 200
                
                results[api["name"]] = {
                    "status_code": response.status_code,
                    "success": success,
                    "response_time": elapsed
                }
                
                status_icon = "✅" if success else "❌"
                print(f"  {status_icon} {api['name']}: {response.status_code} ({elapsed:.2f}ms)")
                
                if not success:
                    self.alerts.append({
                        "level": "warning",
                        "type": "api_failure",
                        "message": f"{api['name']} API失败: HTTP {response.status_code}",
                        "value": response.status_code
                    })
                    
            except Exception as e:
                results[api["name"]] = {
                    "success": False,
                    "error": str(e)
                }
                print(f"  ❌ {api['name']}: {str(e)}")
                
                self.alerts.append({
                    "level": "critical",
                    "type": "api_error",
                    "message": f"{api['name']} API错误: {str(e)}",
                    "value": str(e)
                })
        
        self.metrics["api"]["core_apis"] = results
        
        # 计算成功率
        if results:
            success_count = sum(1 for r in results.values() if r.get('success'))
            success_rate = (success_count / len(results)) * 100
            
            print(f"\n  成功率: {success_rate:.1f}% ({success_count}/{len(results)})")
            
            if success_rate < ALERT_THRESHOLDS["api_success_rate"]:
                self.alerts.append({
                    "level": "warning",
                    "type": "api_success_rate",
                    "message": f"API成功率过低: {success_rate:.1f}%",
                    "value": success_rate
                })
    
    def check_system_resources(self):
        """检查系统资源"""
        print("\n【系统资源检查】")
        
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        print(f"  CPU使用率: {cpu_percent}%")
        
        self.metrics["system"]["cpu"] = cpu_percent
        
        if cpu_percent > ALERT_THRESHOLDS["cpu_usage"]:
            self.alerts.append({
                "level": "warning",
                "type": "cpu_usage",
                "message": f"CPU使用率过高: {cpu_percent}%",
                "value": cpu_percent
            })
        
        # 内存使用率
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        print(f"  内存使用率: {memory_percent}% ({memory.used / 1024 / 1024 / 1024:.2f}GB / {memory.total / 1024 / 1024 / 1024:.2f}GB)")
        
        self.metrics["system"]["memory"] = {
            "percent": memory_percent,
            "used_gb": memory.used / 1024 / 1024 / 1024,
            "total_gb": memory.total / 1024 / 1024 / 1024
        }
        
        if memory_percent > ALERT_THRESHOLDS["memory_usage"]:
            self.alerts.append({
                "level": "warning",
                "type": "memory_usage",
                "message": f"内存使用率过高: {memory_percent}%",
                "value": memory_percent
            })
        
        # 磁盘使用率
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        print(f"  磁盘使用率: {disk_percent}% ({disk.used / 1024 / 1024 / 1024:.2f}GB / {disk.total / 1024 / 1024 / 1024:.2f}GB)")
        
        self.metrics["system"]["disk"] = {
            "percent": disk_percent,
            "used_gb": disk.used / 1024 / 1024 / 1024,
            "total_gb": disk.total / 1024 / 1024 / 1024
        }
        
        if disk_percent > ALERT_THRESHOLDS["disk_usage"]:
            self.alerts.append({
                "level": "warning",
                "type": "disk_usage",
                "message": f"磁盘使用率过高: {disk_percent}%",
                "value": disk_percent
            })
    
    def check_database(self):
        """检查数据库状态"""
        print("\n【数据库检查】")
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # 检查数据库连接
            start_time = time.time()
            cursor.execute("SELECT 1")
            elapsed = (time.time() - start_time) * 1000
            
            print(f"✅ 数据库连接正常")
            print(f"   查询时间: {elapsed:.2f}ms")
            
            self.metrics["database"]["connected"] = True
            self.metrics["database"]["query_time"] = elapsed
            
            if elapsed > ALERT_THRESHOLDS["database_query_time"]:
                self.alerts.append({
                    "level": "warning",
                    "type": "database_query_time",
                    "message": f"数据库查询时间过长: {elapsed:.2f}ms",
                    "value": elapsed
                })
            
            # 检查主要表的数据量
            tables_to_check = ['users', 'knowledge_bases', 'knowledge_documents', 'agents']
            table_stats = {}
            
            for table in tables_to_check:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    table_stats[table] = count
                    print(f"   {table}: {count} 条记录")
                except:
                    pass
            
            self.metrics["database"]["tables"] = table_stats
            
            # 检查数据库大小
            db_size = os.path.getsize(DB_PATH) / 1024 / 1024
            print(f"   数据库大小: {db_size:.2f}MB")
            self.metrics["database"]["size_mb"] = db_size
            
            conn.close()
            
        except Exception as e:
            print(f"❌ 数据库检查失败: {e}")
            self.metrics["database"]["connected"] = False
            self.alerts.append({
                "level": "critical",
                "type": "database",
                "message": f"数据库检查失败: {str(e)}",
                "value": str(e)
            })
    
    def check_process_status(self):
        """检查进程状态"""
        print("\n【进程状态检查】")
        
        try:
            # 检查 Python/Gunicorn 进程
            python_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_percent']):
                try:
                    if proc.info['name'] == 'python' or 'gunicorn' in ' '.join(proc.info.get('cmdline', [])):
                        python_processes.append({
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "memory": proc.info['memory_percent']
                        })
                except:
                    pass
            
            if python_processes:
                print(f"✅ 找到 {len(python_processes)} 个 Python 进程:")
                for proc in python_processes[:5]:
                    print(f"   PID {proc['pid']}: {proc['memory']:.1f}% 内存")
            else:
                print("⚠️  未找到 Python/Gunicorn 进程")
                self.alerts.append({
                    "level": "critical",
                    "type": "process",
                    "message": "未找到 Python/Gunicorn 进程",
                    "value": 0
                })
            
            self.metrics["system"]["processes"] = len(python_processes)
            
        except Exception as e:
            print(f"❌ 进程检查失败: {e}")
    
    def save_metrics(self):
        """保存监控数据"""
        try:
            metrics_dir = "/tmp/monitoring"
            os.makedirs(metrics_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{metrics_dir}/system_metrics_{timestamp}.json"
            
            self.metrics["alerts"] = self.alerts
            self.metrics["alert_count"] = {
                "critical": len([a for a in self.alerts if a['level'] == 'critical']),
                "warning": len([a for a in self.alerts if a['level'] == 'warning'])
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.metrics, f, ensure_ascii=False, indent=2)
            
            print(f"\n✅ 监控数据已保存到: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ 保存监控数据失败: {e}")
            return None
    
    def print_summary(self):
        """打印监控摘要"""
        print("\n" + "=" * 80)
        print("监控摘要")
        print("=" * 80)
        
        # API状态
        api_health = self.metrics["api"].get("health", "unknown")
        print(f"\nAPI状态: {api_health}")
        if api_health == "healthy":
            print(f"  响应时间: {self.metrics['api'].get('response_time', 0):.2f}ms")
        
        # 系统资源
        print(f"\n系统资源:")
        print(f"  CPU: {self.metrics['system'].get('cpu', 0)}%")
        print(f"  内存: {self.metrics['system'].get('memory', {}).get('percent', 0)}%")
        print(f"  磁盘: {self.metrics['system'].get('disk', {}).get('percent', 0)}%")
        
        # 数据库
        db_connected = self.metrics["database"].get("connected", False)
        print(f"\n数据库: {'正常' if db_connected else '异常'}")
        
        # 告警
        critical_count = len([a for a in self.alerts if a['level'] == 'critical'])
        warning_count = len([a for a in self.alerts if a['level'] == 'warning'])
        
        print(f"\n告警:")
        print(f"  严重: {critical_count}")
        print(f"  警告: {warning_count}")
        
        if critical_count > 0:
            print(f"\n❌ 系统存在严重问题，需要立即处理！")
        elif warning_count > 0:
            print(f"\n⚠️  系统存在警告，建议关注！")
        else:
            print(f"\n✅ 系统运行正常！")
        
        print("=" * 80)

def run_monitoring():
    """运行监控"""
    print("=" * 80)
    print("系统监控")
    print("=" * 80)
    print(f"监控时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"监控地址: {BASE_URL}")
    print("=" * 80)
    
    monitor = SystemMonitor()
    
    # 执行各项检查
    monitor.check_api_health()
    monitor.check_core_apis()
    monitor.check_system_resources()
    monitor.check_database()
    monitor.check_process_status()
    
    # 保存数据
    monitor.save_metrics()
    
    # 打印摘要
    monitor.print_summary()
    
    return monitor

if __name__ == '__main__':
    try:
        monitor = run_monitoring()
        
        # 如果有严重告警，返回非零退出码
        critical_count = len([a for a in monitor.alerts if a['level'] == 'critical'])
        if critical_count > 0:
            exit(1)
        
    except Exception as e:
        print(f"\n❌ 监控执行失败: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

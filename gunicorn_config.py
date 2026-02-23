# Gunicorn 配置文件 - 灵值生态园后端

import multiprocessing
import os

# 服务器套接字
bind = "0.0.0.0:5000"
backlog = 2048

# Worker 进程
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 120
keepalive = 5
graceful_timeout = 30
preload_app = True
sendfile = True
reuse_port = True
chdir = "/workspace/projects/admin-backend"

# 日志
loglevel = "info"
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 进程命名
proc_name = "lingzhi-backend"

# 安全
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# SSL/TLS (可选)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# 环境变量
raw_env = [
    'ENV=production',
    'PYTHONPATH=/workspace/projects',
    'FLASK_APP=app',
    'FLASK_ENV=production'
]

# 重启
daemon = False
pidfile = "/tmp/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# 服务器钩子
def on_starting(server):
    print("Gunicorn starting...")

def on_reload(server):
    print("Gunicorn reloading...")

def when_ready(server):
    print("Gunicorn ready. Listening on: %s" % server.address)

def pre_fork(server, worker):
    pass

def post_fork(server, worker):
    pass

def pre_exec(server):
    print("Forked child, re-executing.")

def worker_int(worker):
    print("worker received INT or QUIT signal")

def worker_abort(worker):
    print("worker received SIGABRT signal")

def pre_request(worker, req):
    worker.log.debug("%s %s" % (req.method, req.path))

def post_request(worker, req, environ, resp):
    pass

def child_exit(server, worker):
    print("worker died with exit status %s" % worker.status)

def worker_exit(server, worker):
    print("worker exiting...")

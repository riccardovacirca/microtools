import os
from dotenv import load_dotenv

load_dotenv("/workspace/.env")

# Server socket
bind = f"{os.getenv('GUNICORN_HOST', '127.0.0.1')}:{os.getenv('GUNICORN_PORT', '8001')}"
backlog = 2048

# Worker processes
workers = int(os.getenv("THREAD_COUNT", "4"))
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
accesslog = "/workspace/logs/gunicorn-access.log"
errorlog = "/workspace/logs/gunicorn-error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = os.getenv("PROJECT_NAME", "api") + "-gunicorn"

# Server mechanics
daemon = False
pidfile = "/tmp/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# Preload app for better performance
preload_app = True

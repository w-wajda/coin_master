wsgi_app = "app.main:app"
worker_class = "uvicorn.workers.UvicornWorker"
bind = "0.0.0.0:8000"
raw_env = ["ENV=production"]
chdir = "/app"
loglevel = "INFO"
workers = 5
threads = 2

timeout = 60
keepalive = 30
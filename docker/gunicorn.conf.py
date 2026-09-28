import os

bind = "0.0.0.0:8000"
workers = int(os.environ.get("GUNICORN_WORKERS", 3))
timeout = int(os.environ.get("GUNICORN_TIMEOUT", 60))

# restart workers from time to time to avoid memory leaks
max_requests = 1000
max_requests_jitter = 100

accesslog = "-"
errorlog = "-"

# only nginx can reach this container
forwarded_allow_ips = "*"

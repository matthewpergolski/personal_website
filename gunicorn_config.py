"""
Gunicorn configuration for production deployment on Render
"""

# Server socket settings
bind = "0.0.0.0:10000"  # The port is overridden by Render
workers = 2  # Number of worker processes
worker_class = "sync"  # Worker type
timeout = 120  # Timeout in seconds

# Logging settings
accesslog = "-"  # Log to stdout
errorlog = "-"  # Log to stderr
loglevel = "info"

# Process naming
proc_name = "personal_website"

# Reload settings (disable in production)
reload = False 
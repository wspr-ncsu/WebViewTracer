import os

def create_log_directory(base_dir="/app/logs/"):
    """Create a log directory if it doesn't exist."""
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    return base_dir

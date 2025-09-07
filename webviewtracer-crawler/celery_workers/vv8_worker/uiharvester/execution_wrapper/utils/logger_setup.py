import logging

def setup_logger(name, log_file):
    """Set up a logger with the given name and log file."""
    logger = logging.getLogger(name)
    handler = logging.FileHandler(log_file)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger

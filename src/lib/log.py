import sys
import datetime

# Global log level
LOG_LEVEL = "INFO"

# Valid log levels in order of severity
LOG_LEVELS = {
    "DEBUG": 10,
    "INFO": 20,
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50
}

def log(*args, level="INFO"):
    """Centralized logging function with level control, supporting multiple arguments."""
    if LOG_LEVELS[level] >= LOG_LEVELS.get(LOG_LEVEL, 20):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = " ".join(str(arg) for arg in args)
        print(f"[{timestamp}] [{level}] {message}", file=sys.stdout if level != "ERROR" else sys.stderr)

def set_log_level(level):
    """Update the global log level."""
    global LOG_LEVEL
    if level.upper() in LOG_LEVELS:
        LOG_LEVEL = level.upper()
    else:
        raise ValueError(f"Invalid log level: {level}. Valid levels are {list(LOG_LEVELS.keys())}")


import logging
import sys
import json
from datetime import datetime, timezone
from src.core.config import settings

class JSONFormatter(logging.Formatter):
    """
    Custom formatter that outputs logs as JSON lines.
    Useful for production log aggregation (ELK, GCP Logging, Datadog, etc.).
    """
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "filename": record.filename,
            "line": record.lineno,
        }
        
        # Capture tracebacks if there is an exception
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_data)

def setup_logging() -> None:
    """
    Configure the root logger with handlers, formatters, and levels.
    Prevents duplicate logger setup and standardizes log structure.
    """
    # Create or get root logger
    root_logger = logging.getLogger()
    
    # Set logging level from application configuration
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    root_logger.setLevel(log_level)

    # Clear existing handlers to prevent duplicate message emissions
    if root_logger.handlers:
        root_logger.handlers.clear()

    # Setup standard console handler pointing to stdout
    handler = logging.StreamHandler(sys.stdout)
    
    # Simple check for JSON structured logs: we can configure a toggle
    # For now, default to structured-like human-readable console logging.
    # In production environments, replace with JSONFormatter().
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] (%(name)s:%(funcName)s:%(lineno)d): %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Prevent noisy libraries from flooding standard out
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("langchain").setLevel(logging.WARNING)

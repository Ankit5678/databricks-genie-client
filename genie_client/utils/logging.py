import logging
import json
from logging import Logger, LogRecord

def setup_logger(name: str, level=logging.INFO) -> Logger:
    """Configures structured JSON logging"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = StructuredFormatter()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    return logger

class StructuredFormatter(logging.Formatter):
    """Formats log records as JSON strings"""
    def format(self, record: LogRecord) -> str:
        log_data = {
            "timestamp": self.formatTime(record),
            "logger": record.name,
            "level": record.levelname,
            "message": record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add custom context if available
        if hasattr(record, "context"):
            log_data.update(record.context)
        
        # Add NL generation metrics
        if hasattr(record, 'nl_generated'):
            log_data["nl_generated"] = record.nl_generated
            
        return json.dumps(log_data)

# Configure package-level logger
logger = setup_logger("genie_client")
# backend/app/utils/logger.py

"""
Logger utility for the application
"""

import logging
import sys
import os
from pathlib import Path

def get_logger(name: str = __name__) -> logging.Logger:
    """Get a configured logger instance"""
    
    # Set UTF-8 encoding for Windows console
    if sys.platform == "win32":
        os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
    
    # Create logger
    logger = logging.getLogger(name)
    
    # Avoid adding multiple handlers
    if logger.handlers:
        return logger
    
    # Set level
    logger.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler with UTF-8 encoding
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Handle encoding for Windows
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    logger.addHandler(console_handler)
    
    # File handler (optional)
    try:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(log_dir / "app.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception:
        # If file logging fails, continue with console only
        pass
    
    return logger

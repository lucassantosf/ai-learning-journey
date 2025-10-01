import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

class LoggerConfig:
    """
    Centralized logging configuration for the entire application
    """
    @staticmethod
    def get_log_directory():
        """
        Ensures log directory exists and returns its path
        """
        log_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            'logs'
        )
        os.makedirs(log_dir, exist_ok=True)
        return log_dir

    @classmethod
    def setup_logger(cls, name, filename, level=logging.INFO):
        """
        Creates a configured logger with rotating file handler
        
        Args:
            name (str): Name of the logger
            filename (str): Log file name
            level (int): Logging level (default: logging.INFO)
        
        Returns:
            logging.Logger: Configured logger instance
        """
        # Create log directory if not exists
        log_dir = cls.get_log_directory()
        log_path = os.path.join(log_dir, filename)

        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # Clear any existing handlers to prevent duplicate logs
        logger.handlers.clear()

        # Create rotating file handler
        file_handler = RotatingFileHandler(
            log_path, 
            maxBytes=10*1024*1024,  # 10MB per file
            backupCount=5  # Keep 5 backup files
        )

        # Create console handler
        console_handler = logging.StreamHandler()

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Set formatter for both handlers
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

# Predefined loggers for different purposes
app_logger = LoggerConfig.setup_logger('app', 'app.log')
classification_logger = LoggerConfig.setup_logger('classification', 'classification.log')
error_logger = LoggerConfig.setup_logger('errors', 'errors.log')
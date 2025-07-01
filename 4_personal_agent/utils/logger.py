import os
import json
import logging
import sentry_sdk
from dotenv import load_dotenv
import prometheus_client
import socket
import threading
from logging.handlers import RotatingFileHandler

# Load environment variables
load_dotenv()

# Prometheus Metrics
REQUEST_COUNT = prometheus_client.Counter(
    'personal_agent_requests_total', 
    'Total number of agent requests',
    ['method', 'endpoint']
)

TOOL_USAGE_COUNT = prometheus_client.Counter(
    'personal_agent_tool_usage_total',
    'Total number of tool usages',
    ['tool_name']
)

ERROR_COUNT = prometheus_client.Counter(
    'personal_agent_errors_total',
    'Total number of errors',
    ['error_type']
)

# Configure Sentry for error tracking
sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN', ''),
    traces_sample_rate=0.1,
    environment=os.getenv('FLASK_ENV', 'development')
)

class CustomFormatter(logging.Formatter):
    """
    Custom log formatter to reduce verbosity and improve readability
    """
    def format(self, record):
        # Use formatTime to get the timestamp
        record.asctime = self.formatTime(record)
        
        # Simplified log format
        if record.levelno == logging.INFO:
            return f"{record.asctime} - {record.levelname}: {record.getMessage()}"
        elif record.levelno in [logging.WARNING, logging.ERROR, logging.CRITICAL]:
            return f"{record.asctime} - {record.levelname}: {record.getMessage()}"
        return super().format(record)

class AgentLogger:
    def __init__(self):
        """
        Initialize logging with reduced verbosity and file rotation
        """
        # Ensure log directory exists
        os.makedirs('logs', exist_ok=True)
        
        # Configure logging
        self.logger = logging.getLogger('PersonalAgent')
        self.logger.setLevel(logging.INFO)
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Rotating File Handler
        file_handler = RotatingFileHandler(
            'logs/agent.log', 
            maxBytes=1_048_576,  # 1 MB
            backupCount=3
        )
        formatter = CustomFormatter('%(asctime)s - %(levelname)s: %(message)s')
        file_handler.setFormatter(formatter)
        
        # Console Handler with custom formatting
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Reduce logging for noisy libraries
        logging.getLogger('werkzeug').setLevel(logging.ERROR)
        logging.getLogger('transformers').setLevel(logging.ERROR)
        logging.getLogger('urllib3').setLevel(logging.ERROR)

    def log_agent_interaction(self, user_question, agent_response, tools_used=None):
        """
        Log detailed agent interactions
        
        Args:
            user_question (str): The user's input
            agent_response (str): The agent's response
            tools_used (list): List of tools used in the interaction
        """
        log_data = {
            'event': 'agent_interaction',
            'user_question': user_question,
            'agent_response': agent_response,
            'tools_used': tools_used or []
        }
        
        # Log to standard logger
        self.logger.info(json.dumps(log_data))
        
        # Log to Prometheus metrics
        if tools_used:
            for tool in tools_used:
                TOOL_USAGE_COUNT.labels(tool_name=tool).inc()

    def log_error(self, error_type, error_message, context=None):
        """
        Log errors with detailed context
        
        Args:
            error_type (str): Type of error
            error_message (str): Detailed error description
            context (dict): Additional context about the error
        """
        log_message = {
            'event': 'error',
            'error_type': error_type,
            'error_message': str(error_message),
            'context': context or {}
        }
        
        # Log to standard logger
        self.logger.error(json.dumps(log_message))
        
        # Send error to Sentry
        sentry_sdk.capture_message(
            f"{error_type}: {error_message}",
            level='error'
        )
        
        # Log to Prometheus metrics
        ERROR_COUNT.labels(error_type=error_type).inc()

    def track_request(self, method, endpoint):
        """
        Track request metrics
        
        Args:
            method (str): HTTP method
            endpoint (str): Request endpoint
        """
        REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()

    def start_prometheus_server(self, port=8000):
        """
        Start Prometheus metrics server with port availability check
        
        Args:
            port (int): Port to expose metrics
        """
        def find_free_port(start_port):
            """Find the next available port starting from start_port"""
            port = start_port
            while port < start_port + 100:  # Try up to 100 ports
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.bind(('', port))
                        return port
                except OSError:
                    port += 1
            raise RuntimeError(f"Could not find a free port starting from {start_port}")

        try:
            # Find a free port
            metrics_port = find_free_port(port)
            
            # Start Prometheus metrics server in a separate thread
            threading.Thread(
                target=prometheus_client.start_http_server, 
                args=(metrics_port,), 
                daemon=True
            ).start()
            
            # Use print instead of logger to avoid potential formatting issues
            print(f"Prometheus metrics server started on port {metrics_port}")
        except Exception as e:
            # Use print for error reporting
            print(f"Error starting Prometheus metrics server: {e}")

# Create a global logger instance
agent_logger = AgentLogger()

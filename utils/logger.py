"""Logging utilities for the XN Mental Health Chatbot."""

import logging
import sys
from datetime import datetime
from typing import Optional
from config import config

class ChatbotLogger:
    """Custom logger for the mental health chatbot with privacy considerations."""
    
    def __init__(self, name: str = "xn_chatbot"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, config.LOG_LEVEL.upper()))
        
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up logging handlers."""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler (if enabled)
        if config.ENABLE_LOGGING:
            try:
                file_handler = logging.FileHandler(config.LOG_FILE)
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
            except Exception as e:
                self.logger.warning(f"Could not create file handler: {e}")
    
    def log_user_interaction(self, session_id: str, interaction_type: str, 
                           severity: Optional[str] = None):
        """Log user interaction without sensitive content."""
        self.logger.info(
            f"Session {session_id[:8]}... - {interaction_type}" + 
            (f" - Severity: {severity}" if severity else "")
        )
    
    def log_crisis_detection(self, session_id: str, risk_level: str):
        """Log crisis detection events."""
        self.logger.warning(
            f"CRISIS DETECTED - Session {session_id[:8]}... - Risk Level: {risk_level}"
        )
    
    def log_resource_recommendation(self, session_id: str, resource_count: int):
        """Log resource recommendations."""
        self.logger.info(
            f"Session {session_id[:8]}... - Recommended {resource_count} resources"
        )
    
    def log_llm_usage(self, provider: str, success: bool, fallback_used: bool = False):
        """Log LLM API usage."""
        status = "SUCCESS" if success else "FAILED"
        fallback_msg = " (Fallback used)" if fallback_used else ""
        self.logger.info(f"LLM {provider} - {status}{fallback_msg}")
    
    def log_error(self, error: Exception, context: str = ""):
        """Log errors with context."""
        self.logger.error(f"Error in {context}: {str(error)}", exc_info=True)
    
    def debug(self, message: str):
        """Log debug messages."""
        if config.DEBUG_MODE:
            self.logger.debug(message)
    
    def info(self, message: str):
        """Log info messages."""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning messages."""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error messages."""
        self.logger.error(message)

# Global logger instance
logger = ChatbotLogger()
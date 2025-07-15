"""
Consistent logging framework with sensitive data masking.
"""

import logging
import logging.handlers
import os
import re
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from security.credential_manager import mask_sensitive_data


class SensitiveDataFilter(logging.Filter):
    """Filter to mask sensitive data in log messages."""
    
    def __init__(self):
        super().__init__()
        # Patterns to detect sensitive data
        self.patterns = [
            (r'password["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)', 'password'),
            (r'token["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)', 'token'),
            (r'api_key["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)', 'api_key'),
            (r'secret["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)', 'secret'),
            (r'auth["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)', 'auth'),
            (r'email["\']?\s*[:=]\s*["\']?([^"\'\s,}]+@[^"\'\s,}]+)', 'email'),
            # Credit card patterns
            (r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', 'credit_card'),
            # Social security numbers
            (r'\b\d{3}-\d{2}-\d{4}\b', 'ssn'),
        ]
        
        # Compile patterns for performance
        self.compiled_patterns = [
            (re.compile(pattern, re.IGNORECASE), name)
            for pattern, name in self.patterns
        ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log record to mask sensitive data."""
        try:
            # Mask sensitive data in the message
            record.msg = self._mask_sensitive_data(str(record.msg))
            
            # Mask sensitive data in arguments
            if record.args:
                masked_args = []
                for arg in record.args:
                    if isinstance(arg, str):
                        masked_args.append(self._mask_sensitive_data(arg))
                    else:
                        masked_args.append(arg)
                record.args = tuple(masked_args)
            
            return True
            
        except Exception:
            # If filtering fails, don't block the log message
            return True
    
    def _mask_sensitive_data(self, text: str) -> str:
        """Mask sensitive data in text."""
        for pattern, name in self.compiled_patterns:
            def replace_match(match):
                if name == 'email':
                    # Special handling for emails - mask the username part
                    email = match.group(1)
                    at_index = email.find('@')
                    if at_index > 0:
                        username = email[:at_index]
                        domain = email[at_index:]
                        return f'{name}="{mask_sensitive_data(username)}{domain}"'
                    return f'{name}="{mask_sensitive_data(email)}"'
                else:
                    # Mask other sensitive data
                    sensitive_value = match.group(1)
                    return match.group(0).replace(sensitive_value, mask_sensitive_data(sensitive_value))
            
            text = pattern.sub(replace_match, text)
        
        return text


class PlatformFilter(logging.Filter):
    """Filter to add platform information to log records."""
    
    def __init__(self, platform: str):
        super().__init__()
        self.platform = platform
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add platform information to log record."""
        record.platform = self.platform
        return True


class JobBotLogger:
    """Centralized logging configuration for job bot."""
    
    def __init__(self, name: str = "job_bot", log_dir: str = "logs"):
        """
        Initialize job bot logger.
        
        Args:
            name: Logger name
            log_dir: Directory for log files
        """
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create main logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Setup handlers
        self._setup_handlers()
    
    def _setup_handlers(self) -> None:
        """Setup logging handlers."""
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        console_handler.addFilter(SensitiveDataFilter())
        self.logger.addHandler(console_handler)
        
        # Main log file handler
        main_log_file = self.log_dir / f"{self.name}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            main_log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        file_handler.addFilter(SensitiveDataFilter())
        self.logger.addHandler(file_handler)
        
        # Error log file handler
        error_log_file = self.log_dir / f"{self.name}_errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        error_handler.addFilter(SensitiveDataFilter())
        self.logger.addHandler(error_handler)
    
    def get_logger(self, name: str = None) -> logging.Logger:
        """
        Get logger instance.
        
        Args:
            name: Logger name suffix
            
        Returns:
            Logger instance
        """
        if name:
            logger_name = f"{self.name}.{name}"
        else:
            logger_name = self.name
        
        return logging.getLogger(logger_name)
    
    def get_platform_logger(self, platform: str) -> logging.Logger:
        """
        Get platform-specific logger.
        
        Args:
            platform: Platform name
            
        Returns:
            Platform-specific logger
        """
        logger = self.get_logger(f"platform.{platform}")
        
        # Add platform-specific handler
        platform_log_file = self.log_dir / f"{platform}.log"
        platform_handler = logging.handlers.RotatingFileHandler(
            platform_log_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        platform_handler.setLevel(logging.DEBUG)
        platform_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        platform_handler.setFormatter(platform_formatter)
        platform_handler.addFilter(SensitiveDataFilter())
        platform_handler.addFilter(PlatformFilter(platform))
        
        # Check if handler already exists
        handler_exists = any(
            isinstance(h, logging.handlers.RotatingFileHandler) and 
            h.baseFilename == str(platform_log_file)
            for h in logger.handlers
        )
        
        if not handler_exists:
            logger.addHandler(platform_handler)
        
        return logger
    
    def log_application_attempt(
        self, 
        platform: str, 
        job_title: str, 
        company: str, 
        success: bool,
        details: Dict[str, Any] = None
    ) -> None:
        """
        Log job application attempt.
        
        Args:
            platform: Platform name
            job_title: Job title
            company: Company name
            success: Whether application was successful
            details: Additional details
        """
        logger = self.get_platform_logger(platform)
        
        status = "SUCCESS" if success else "FAILED"
        message = f"Application {status}: {job_title} at {company}"
        
        if details:
            message += f" - Details: {details}"
        
        if success:
            logger.info(message)
        else:
            logger.error(message)
    
    def log_platform_error(
        self, 
        platform: str, 
        operation: str, 
        error: Exception,
        details: Dict[str, Any] = None
    ) -> None:
        """
        Log platform-specific error.
        
        Args:
            platform: Platform name
            operation: Operation that failed
            error: Exception that occurred
            details: Additional details
        """
        logger = self.get_platform_logger(platform)
        
        message = f"Platform error in {operation}: {error}"
        
        if details:
            message += f" - Details: {details}"
        
        logger.error(message, exc_info=True)
    
    def log_security_event(
        self, 
        event_type: str, 
        details: Dict[str, Any] = None
    ) -> None:
        """
        Log security-related event.
        
        Args:
            event_type: Type of security event
            details: Event details
        """
        logger = self.get_logger("security")
        
        message = f"Security event: {event_type}"
        
        if details:
            # Be extra careful with security log details
            safe_details = {}
            for key, value in details.items():
                if key.lower() in ['password', 'token', 'secret', 'key']:
                    safe_details[key] = mask_sensitive_data(str(value))
                else:
                    safe_details[key] = value
            message += f" - Details: {safe_details}"
        
        logger.warning(message)
    
    def create_daily_summary(self) -> Dict[str, Any]:
        """
        Create daily summary of log events.
        
        Returns:
            Dictionary with summary statistics
        """
        summary = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'total_logs': 0,
            'errors': 0,
            'warnings': 0,
            'info': 0,
            'platforms': {},
            'applications': {
                'successful': 0,
                'failed': 0
            }
        }
        
        # This would be implemented to parse log files and generate statistics
        # For now, return the template
        return summary


# Global logger instance
job_bot_logger = JobBotLogger()


def get_logger(name: str = None) -> logging.Logger:
    """
    Get logger instance.
    
    Args:
        name: Logger name suffix
        
    Returns:
        Logger instance
    """
    return job_bot_logger.get_logger(name)


def get_platform_logger(platform: str) -> logging.Logger:
    """
    Get platform-specific logger.
    
    Args:
        platform: Platform name
        
    Returns:
        Platform-specific logger
    """
    return job_bot_logger.get_platform_logger(platform)


def log_application_attempt(
    platform: str, 
    job_title: str, 
    company: str, 
    success: bool,
    details: Dict[str, Any] = None
) -> None:
    """
    Log job application attempt.
    
    Args:
        platform: Platform name
        job_title: Job title
        company: Company name
        success: Whether application was successful
        details: Additional details
    """
    job_bot_logger.log_application_attempt(platform, job_title, company, success, details)


def log_platform_error(
    platform: str, 
    operation: str, 
    error: Exception,
    details: Dict[str, Any] = None
) -> None:
    """
    Log platform-specific error.
    
    Args:
        platform: Platform name
        operation: Operation that failed
        error: Exception that occurred
        details: Additional details
    """
    job_bot_logger.log_platform_error(platform, operation, error, details)


def log_security_event(
    event_type: str, 
    details: Dict[str, Any] = None
) -> None:
    """
    Log security-related event.
    
    Args:
        event_type: Type of security event
        details: Event details
    """
    job_bot_logger.log_security_event(event_type, details)
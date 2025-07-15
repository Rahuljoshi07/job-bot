"""
Retry logic with exponential backoff for platform operations.
"""

import time
import random
import logging
from typing import Callable, Any, Optional, Dict, Union
from functools import wraps

from .exceptions import (
    JobBotError, PlatformError, NetworkError, TimeoutError, 
    RateLimitError, AuthenticationError, CaptchaError
)


logger = logging.getLogger(__name__)


class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        jitter: bool = True,
        retryable_exceptions: tuple = None
    ):
        """
        Initialize retry configuration.
        
        Args:
            max_attempts: Maximum number of retry attempts
            base_delay: Base delay between retries (seconds)
            max_delay: Maximum delay between retries (seconds)
            backoff_factor: Exponential backoff factor
            jitter: Whether to add random jitter to delays
            retryable_exceptions: Tuple of exception types that should trigger retries
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions or (
            NetworkError,
            TimeoutError,
            RateLimitError,
            PlatformError,
        )


class RetryManager:
    """Manages retry logic with exponential backoff."""
    
    def __init__(self, config: RetryConfig = None):
        """
        Initialize retry manager.
        
        Args:
            config: Retry configuration
        """
        self.config = config or RetryConfig()
        self.attempt_counts = {}
    
    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for given attempt number.
        
        Args:
            attempt: Attempt number (0-based)
            
        Returns:
            Delay in seconds
        """
        delay = self.config.base_delay * (self.config.backoff_factor ** attempt)
        delay = min(delay, self.config.max_delay)
        
        if self.config.jitter:
            # Add random jitter (±25% of delay)
            jitter = delay * 0.25 * (2 * random.random() - 1)
            delay += jitter
        
        return max(0, delay)
    
    def should_retry(self, exception: Exception, attempt: int) -> bool:
        """
        Determine if operation should be retried.
        
        Args:
            exception: Exception that occurred
            attempt: Current attempt number (0-based)
            
        Returns:
            True if should retry, False otherwise
        """
        if attempt >= self.config.max_attempts:
            return False
        
        # Check if exception is retryable
        if not isinstance(exception, self.config.retryable_exceptions):
            return False
        
        # Don't retry authentication errors or captcha errors
        if isinstance(exception, (AuthenticationError, CaptchaError)):
            return False
        
        # Special handling for rate limits
        if isinstance(exception, RateLimitError):
            # Extract rate limit delay if available
            if hasattr(exception, 'details') and 'retry_after' in exception.details:
                return True
        
        return True
    
    def get_rate_limit_delay(self, exception: RateLimitError) -> Optional[float]:
        """
        Get rate limit delay from exception details.
        
        Args:
            exception: Rate limit exception
            
        Returns:
            Delay in seconds or None
        """
        if hasattr(exception, 'details') and exception.details:
            return exception.details.get('retry_after')
        return None
    
    def execute_with_retry(
        self, 
        func: Callable, 
        *args, 
        operation_name: str = None,
        platform: str = None,
        **kwargs
    ) -> Any:
        """
        Execute function with retry logic.
        
        Args:
            func: Function to execute
            *args: Function arguments
            operation_name: Name of operation for logging
            platform: Platform name for logging
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Last exception if all retries failed
        """
        operation_name = operation_name or func.__name__
        last_exception = None
        
        for attempt in range(self.config.max_attempts):
            try:
                logger.info(f"Attempting {operation_name} (attempt {attempt + 1}/{self.config.max_attempts})")
                result = func(*args, **kwargs)
                
                # Success - reset attempt count
                key = f"{platform}:{operation_name}"
                if key in self.attempt_counts:
                    del self.attempt_counts[key]
                
                return result
                
            except Exception as e:
                last_exception = e
                
                # Track attempt count
                key = f"{platform}:{operation_name}"
                self.attempt_counts[key] = attempt + 1
                
                if not self.should_retry(e, attempt):
                    logger.error(f"Operation {operation_name} failed (not retryable): {e}")
                    raise
                
                if attempt < self.config.max_attempts - 1:
                    # Calculate delay
                    if isinstance(e, RateLimitError):
                        delay = self.get_rate_limit_delay(e)
                        if delay is None:
                            delay = self.calculate_delay(attempt)
                    else:
                        delay = self.calculate_delay(attempt)
                    
                    logger.warning(
                        f"Operation {operation_name} failed (attempt {attempt + 1}): {e}. "
                        f"Retrying in {delay:.2f} seconds..."
                    )
                    time.sleep(delay)
        
        # All retries failed
        logger.error(f"Operation {operation_name} failed after {self.config.max_attempts} attempts")
        raise last_exception


def retry_on_platform_error(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    platform: str = None
):
    """
    Decorator for retrying platform operations.
    
    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Base delay between retries
        max_delay: Maximum delay between retries
        backoff_factor: Exponential backoff factor
        platform: Platform name for logging
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            config = RetryConfig(
                max_attempts=max_attempts,
                base_delay=base_delay,
                max_delay=max_delay,
                backoff_factor=backoff_factor
            )
            
            retry_manager = RetryManager(config)
            return retry_manager.execute_with_retry(
                func, 
                *args, 
                operation_name=func.__name__,
                platform=platform,
                **kwargs
            )
        
        return wrapper
    return decorator


# Platform-specific retry configurations
PLATFORM_RETRY_CONFIGS = {
    'linkedin': RetryConfig(
        max_attempts=5,
        base_delay=2.0,
        max_delay=120.0,
        backoff_factor=2.0
    ),
    'indeed': RetryConfig(
        max_attempts=3,
        base_delay=1.0,
        max_delay=60.0,
        backoff_factor=2.0
    ),
    'dice': RetryConfig(
        max_attempts=3,
        base_delay=1.5,
        max_delay=90.0,
        backoff_factor=2.0
    ),
    'remoteok': RetryConfig(
        max_attempts=2,
        base_delay=0.5,
        max_delay=30.0,
        backoff_factor=2.0
    ),
    'flexjobs': RetryConfig(
        max_attempts=3,
        base_delay=1.0,
        max_delay=60.0,
        backoff_factor=2.0
    ),
    'twitter': RetryConfig(
        max_attempts=4,
        base_delay=3.0,
        max_delay=180.0,
        backoff_factor=2.0
    ),
    'turing': RetryConfig(
        max_attempts=3,
        base_delay=1.0,
        max_delay=60.0,
        backoff_factor=2.0
    ),
}


def get_platform_retry_config(platform: str) -> RetryConfig:
    """
    Get retry configuration for a specific platform.
    
    Args:
        platform: Platform name
        
    Returns:
        Platform-specific retry configuration
    """
    return PLATFORM_RETRY_CONFIGS.get(platform.lower(), RetryConfig())


def retry_for_platform(platform: str):
    """
    Decorator that applies platform-specific retry configuration.
    
    Args:
        platform: Platform name
    """
    config = get_platform_retry_config(platform)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            retry_manager = RetryManager(config)
            return retry_manager.execute_with_retry(
                func, 
                *args, 
                operation_name=func.__name__,
                platform=platform,
                **kwargs
            )
        
        return wrapper
    return decorator
"""
Base platform interface for job bot.
"""

import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime

from application_tracking.tracker import JobApplication, ApplicationStatus
from error_handling.exceptions import PlatformError, create_platform_error
from error_handling.retry_logic import retry_for_platform
from logging_framework.logger import get_platform_logger
from security.credential_manager import load_credentials_securely


class BasePlatform(ABC):
    """Base class for all job platforms."""
    
    def __init__(self, platform_name: str):
        """
        Initialize platform.
        
        Args:
            platform_name: Name of the platform
        """
        self.platform_name = platform_name
        self.logger = get_platform_logger(platform_name)
        self.credentials = {}
        self.session_active = False
    
    @abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticate with the platform.
        
        Returns:
            True if authentication successful, False otherwise
        """
        pass
    
    @abstractmethod
    def search_jobs(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search for jobs based on criteria.
        
        Args:
            criteria: Search criteria
            
        Returns:
            List of job dictionaries
        """
        pass
    
    @abstractmethod
    def apply_to_job(self, job: Dict[str, Any]) -> JobApplication:
        """
        Apply to a specific job.
        
        Args:
            job: Job dictionary
            
        Returns:
            JobApplication instance
        """
        pass
    
    def load_credentials(self) -> bool:
        """
        Load credentials for the platform.
        
        Returns:
            True if credentials loaded successfully, False otherwise
        """
        try:
            self.credentials = load_credentials_securely(self.platform_name)
            
            if not self.credentials:
                self.logger.error(f"No credentials found for platform {self.platform_name}")
                return False
            
            self.logger.info(f"Credentials loaded for platform {self.platform_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load credentials: {e}")
            return False
    
    def create_job_application(self, job: Dict[str, Any]) -> JobApplication:
        """
        Create JobApplication instance from job dictionary.
        
        Args:
            job: Job dictionary
            
        Returns:
            JobApplication instance
        """
        return JobApplication(
            platform=self.platform_name,
            job_id=job.get('id', ''),
            title=job.get('title', ''),
            company=job.get('company', ''),
            url=job.get('url', ''),
            metadata=job.get('metadata', {})
        )
    
    def handle_error(self, operation: str, error: Exception, details: Dict[str, Any] = None) -> PlatformError:
        """
        Handle platform-specific errors.
        
        Args:
            operation: Operation that failed
            error: Original exception
            details: Additional details
            
        Returns:
            Platform-specific error
        """
        platform_error = create_platform_error(
            self.platform_name,
            f"Error in {operation}: {error}",
            details=details
        )
        
        self.logger.error(f"Platform error in {operation}: {error}", exc_info=True)
        return platform_error
    
    def cleanup(self) -> None:
        """Clean up platform resources."""
        self.session_active = False
        self.logger.info(f"Platform {self.platform_name} cleanup completed")
    
    def get_platform_info(self) -> Dict[str, Any]:
        """
        Get platform information.
        
        Returns:
            Platform information dictionary
        """
        return {
            'name': self.platform_name,
            'session_active': self.session_active,
            'has_credentials': bool(self.credentials),
            'last_activity': datetime.now().isoformat()
        }


class APIPlatform(BasePlatform):
    """Base class for API-based platforms."""
    
    def __init__(self, platform_name: str, base_url: str = None):
        """
        Initialize API platform.
        
        Args:
            platform_name: Name of the platform
            base_url: Base API URL
        """
        super().__init__(platform_name)
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make API request with error handling.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional request parameters
            
        Returns:
            Response data
        """
        try:
            import requests
            
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            
            response = requests.request(
                method,
                url,
                headers=self.headers,
                timeout=30,
                **kwargs
            )
            
            response.raise_for_status()
            return response.json()
            
        except ImportError:
            raise self.handle_error(
                "make_request",
                Exception("requests library not available"),
                {"method": method, "endpoint": endpoint}
            )
        except Exception as e:
            raise self.handle_error(
                "make_request",
                e,
                {"method": method, "endpoint": endpoint}
            )


class WebPlatform(BasePlatform):
    """Base class for web-based platforms."""
    
    def __init__(self, platform_name: str, base_url: str = None):
        """
        Initialize web platform.
        
        Args:
            platform_name: Name of the platform
            base_url: Base website URL
        """
        super().__init__(platform_name)
        self.base_url = base_url
        self.driver = None
    
    def init_driver(self) -> bool:
        """
        Initialize web driver.
        
        Returns:
            True if driver initialized successfully, False otherwise
        """
        try:
            # This would initialize Selenium WebDriver
            # For now, just simulate
            self.driver = "simulated_driver"
            self.logger.info(f"Web driver initialized for {self.platform_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize web driver: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up web driver and resources."""
        if self.driver:
            # This would quit the WebDriver
            self.driver = None
            self.logger.info(f"Web driver cleanup completed for {self.platform_name}")
        
        super().cleanup()


class PlatformFactory:
    """Factory for creating platform instances."""
    
    @staticmethod
    def create_platform(platform_name: str) -> BasePlatform:
        """
        Create platform instance.
        
        Args:
            platform_name: Name of the platform
            
        Returns:
            Platform instance
        """
        platform_configs = {
            'remoteok': {
                'class': APIPlatform,
                'base_url': 'https://remoteok.io/api'
            },
            'linkedin': {
                'class': WebPlatform,
                'base_url': 'https://www.linkedin.com'
            },
            'indeed': {
                'class': WebPlatform,
                'base_url': 'https://www.indeed.com'
            },
            'dice': {
                'class': WebPlatform,
                'base_url': 'https://www.dice.com'
            },
            'flexjobs': {
                'class': WebPlatform,
                'base_url': 'https://www.flexjobs.com'
            },
            'twitter': {
                'class': WebPlatform,
                'base_url': 'https://twitter.com'
            },
            'turing': {
                'class': WebPlatform,
                'base_url': 'https://www.turing.com'
            },
        }
        
        config = platform_configs.get(platform_name.lower())
        if not config:
            raise ValueError(f"Unknown platform: {platform_name}")
        
        platform_class = config['class']
        base_url = config['base_url']
        
        return platform_class(platform_name, base_url)
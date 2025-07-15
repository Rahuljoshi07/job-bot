"""
Enhanced Job Bot with security, reliability, and tracking improvements.
"""

import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from security.credential_manager import CredentialManager, load_credentials_securely
from application_tracking.tracker import ApplicationTracker, JobApplication, ApplicationStatus
from error_handling.exceptions import JobBotError, PlatformError
from error_handling.retry_logic import retry_for_platform, get_platform_retry_config
from logging_framework.logger import get_logger, log_application_attempt, log_platform_error
from platforms.base import PlatformFactory, BasePlatform


class EnhancedJobBot:
    """
    Enhanced job bot with security, reliability, and tracking improvements.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize enhanced job bot.
        
        Args:
            config: Bot configuration
        """
        self.config = config or {}
        self.logger = get_logger("enhanced_job_bot")
        
        # Initialize components
        self.credential_manager = CredentialManager()
        self.application_tracker = ApplicationTracker()
        self.platforms = {}
        self.stats = {
            'total_searches': 0,
            'total_applications': 0,
            'successful_applications': 0,
            'failed_applications': 0,
            'errors': 0,
            'start_time': datetime.now()
        }
        
        # Load configuration
        self.job_preferences = self.config.get('job_preferences', {
            'titles': [
                "DevOps Engineer", "Cloud Engineer", "Site Reliability Engineer",
                "Infrastructure Engineer", "Platform Engineer", "AWS Engineer",
                "Kubernetes Administrator", "CI/CD Engineer"
            ],
            'skills': [
                "DevOps", "AWS", "Docker", "Kubernetes", "Python", "Linux",
                "CI/CD", "Jenkins", "Terraform", "Ansible"
            ],
            'remote_only': True,
            'salary_min': 50000,
            'experience_levels': ['entry', 'junior', 'mid']
        })
        
        self.platform_names = self.config.get('platforms', [
            'remoteok', 'linkedin', 'indeed', 'dice', 'flexjobs'
        ])
        
        self.logger.info("Enhanced job bot initialized")
    
    def initialize_platforms(self) -> None:
        """Initialize all configured platforms."""
        for platform_name in self.platform_names:
            try:
                platform = PlatformFactory.create_platform(platform_name)
                if platform.load_credentials():
                    self.platforms[platform_name] = platform
                    self.logger.info(f"Platform {platform_name} initialized successfully")
                else:
                    self.logger.warning(f"Failed to load credentials for platform {platform_name}")
                    
            except Exception as e:
                self.logger.error(f"Failed to initialize platform {platform_name}: {e}")
                log_platform_error(platform_name, "initialize", e)
    
    def authenticate_platforms(self) -> Dict[str, bool]:
        """
        Authenticate with all platforms.
        
        Returns:
            Dictionary mapping platform names to authentication success
        """
        results = {}
        
        for platform_name, platform in self.platforms.items():
            try:
                success = platform.authenticate()
                results[platform_name] = success
                
                if success:
                    self.logger.info(f"Successfully authenticated with {platform_name}")
                else:
                    self.logger.warning(f"Failed to authenticate with {platform_name}")
                    
            except Exception as e:
                results[platform_name] = False
                self.logger.error(f"Authentication error for {platform_name}: {e}")
                log_platform_error(platform_name, "authenticate", e)
        
        return results
    
    def search_jobs_on_platform(self, platform_name: str) -> List[Dict[str, Any]]:
        """
        Search for jobs on a specific platform.
        
        Args:
            platform_name: Name of the platform
            
        Returns:
            List of job dictionaries
        """
        if platform_name not in self.platforms:
            self.logger.warning(f"Platform {platform_name} not initialized")
            return []
        
        platform = self.platforms[platform_name]
        
        try:
            # Apply retry logic for platform
            @retry_for_platform(platform_name)
            def search_with_retry():
                return platform.search_jobs(self.job_preferences)
            
            jobs = search_with_retry()
            self.stats['total_searches'] += 1
            
            # Filter out already applied jobs
            applied_job_ids = self.application_tracker.get_applied_job_ids(platform_name)
            filtered_jobs = [
                job for job in jobs 
                if job.get('id') not in applied_job_ids
            ]
            
            self.logger.info(
                f"Found {len(jobs)} jobs on {platform_name}, "
                f"{len(filtered_jobs)} new jobs after filtering"
            )
            
            return filtered_jobs
            
        except Exception as e:
            self.stats['errors'] += 1
            self.logger.error(f"Error searching jobs on {platform_name}: {e}")
            log_platform_error(platform_name, "search_jobs", e)
            return []
    
    def apply_to_job_on_platform(self, platform_name: str, job: Dict[str, Any]) -> JobApplication:
        """
        Apply to a job on a specific platform.
        
        Args:
            platform_name: Name of the platform
            job: Job dictionary
            
        Returns:
            JobApplication instance
        """
        if platform_name not in self.platforms:
            self.logger.warning(f"Platform {platform_name} not initialized")
            return None
        
        platform = self.platforms[platform_name]
        
        try:
            # Create job application record
            application = platform.create_job_application(job)
            
            # Check for duplicates
            if self.application_tracker.is_duplicate(application.fingerprint):
                application.status = ApplicationStatus.DUPLICATE
                self.logger.info(f"Duplicate application detected: {application.title} at {application.company}")
                return application
            
            # Apply retry logic for platform
            @retry_for_platform(platform_name)
            def apply_with_retry():
                return platform.apply_to_job(job)
            
            # Attempt to apply
            result = apply_with_retry()
            
            if result:
                application.status = ApplicationStatus.APPLIED
                self.stats['successful_applications'] += 1
                self.logger.info(f"Successfully applied to {application.title} at {application.company}")
                
                log_application_attempt(
                    platform_name,
                    application.title,
                    application.company,
                    True,
                    {'job_id': application.job_id, 'url': application.url}
                )
            else:
                application.status = ApplicationStatus.FAILED
                self.stats['failed_applications'] += 1
                self.logger.warning(f"Failed to apply to {application.title} at {application.company}")
                
                log_application_attempt(
                    platform_name,
                    application.title,
                    application.company,
                    False,
                    {'job_id': application.job_id, 'url': application.url}
                )
            
            # Save to tracking system
            self.application_tracker.add_application(application)
            self.stats['total_applications'] += 1
            
            return application
            
        except Exception as e:
            self.stats['errors'] += 1
            self.logger.error(f"Error applying to job on {platform_name}: {e}")
            log_platform_error(platform_name, "apply_to_job", e, {'job': job})
            
            # Create failed application record
            application = platform.create_job_application(job)
            application.status = ApplicationStatus.FAILED
            application.metadata['error'] = str(e)
            self.application_tracker.add_application(application)
            
            return application
    
    def run_job_search_cycle(self) -> Dict[str, Any]:
        """
        Run a complete job search cycle.
        
        Returns:
            Dictionary with cycle results
        """
        cycle_start = datetime.now()
        self.logger.info("Starting job search cycle")
        
        results = {
            'cycle_start': cycle_start.isoformat(),
            'platforms': {},
            'total_jobs_found': 0,
            'total_applications_sent': 0,
            'errors': []
        }
        
        # Initialize platforms if not already done
        if not self.platforms:
            self.initialize_platforms()
            auth_results = self.authenticate_platforms()
            results['authentication'] = auth_results
        
        # Search and apply on each platform
        for platform_name in self.platforms:
            platform_results = {
                'jobs_found': 0,
                'applications_sent': 0,
                'errors': []
            }
            
            try:
                # Search for jobs
                jobs = self.search_jobs_on_platform(platform_name)
                platform_results['jobs_found'] = len(jobs)
                results['total_jobs_found'] += len(jobs)
                
                # Apply to jobs
                for job in jobs:
                    try:
                        application = self.apply_to_job_on_platform(platform_name, job)
                        if application and application.status == ApplicationStatus.APPLIED:
                            platform_results['applications_sent'] += 1
                            results['total_applications_sent'] += 1
                        
                        # Rate limiting
                        time.sleep(2)  # 2 second delay between applications
                        
                    except Exception as e:
                        error_msg = f"Error applying to job {job.get('title', 'Unknown')}: {e}"
                        platform_results['errors'].append(error_msg)
                        self.logger.error(error_msg)
                
            except Exception as e:
                error_msg = f"Error processing platform {platform_name}: {e}"
                platform_results['errors'].append(error_msg)
                results['errors'].append(error_msg)
                self.logger.error(error_msg)
            
            results['platforms'][platform_name] = platform_results
            
            # Delay between platforms
            time.sleep(5)
        
        cycle_end = datetime.now()
        results['cycle_end'] = cycle_end.isoformat()
        results['cycle_duration'] = (cycle_end - cycle_start).total_seconds()
        
        self.logger.info(f"Job search cycle completed in {results['cycle_duration']:.2f} seconds")
        self.logger.info(f"Found {results['total_jobs_found']} jobs, sent {results['total_applications_sent']} applications")
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get bot statistics.
        
        Returns:
            Dictionary with statistics
        """
        runtime = datetime.now() - self.stats['start_time']
        
        stats = {
            'runtime_seconds': runtime.total_seconds(),
            'runtime_formatted': str(runtime),
            **self.stats,
            'application_tracking': self.application_tracker.get_statistics(),
            'platforms': {
                name: platform.get_platform_info()
                for name, platform in self.platforms.items()
            }
        }
        
        return stats
    
    def cleanup(self) -> None:
        """Clean up bot resources."""
        self.logger.info("Cleaning up bot resources")
        
        for platform_name, platform in self.platforms.items():
            try:
                platform.cleanup()
            except Exception as e:
                self.logger.error(f"Error cleaning up platform {platform_name}: {e}")
        
        # Clean up old applications
        cleaned = self.application_tracker.cleanup_old_applications()
        if cleaned > 0:
            self.logger.info(f"Cleaned up {cleaned} old applications")
        
        self.logger.info("Bot cleanup completed")


def main():
    """Main entry point for enhanced job bot."""
    # Example configuration
    config = {
        'job_preferences': {
            'titles': [
                "DevOps Engineer", "Cloud Engineer", "Site Reliability Engineer",
                "Infrastructure Engineer", "Platform Engineer"
            ],
            'skills': [
                "DevOps", "AWS", "Docker", "Kubernetes", "Python", "Linux"
            ],
            'remote_only': True,
            'salary_min': 60000
        },
        'platforms': ['remoteok', 'linkedin', 'indeed']
    }
    
    # Create and run bot
    bot = EnhancedJobBot(config)
    
    try:
        # Run job search cycle
        results = bot.run_job_search_cycle()
        
        # Print statistics
        stats = bot.get_statistics()
        print(f"Bot Statistics: {stats}")
        
    except KeyboardInterrupt:
        print("\nBot interrupted by user")
    except Exception as e:
        print(f"Bot error: {e}")
    finally:
        bot.cleanup()


if __name__ == "__main__":
    main()
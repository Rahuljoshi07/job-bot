"""
Test cases for enhanced job bot security and reliability features.
"""

import os
import tempfile
import shutil
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Test security features
from security.credential_manager import CredentialManager, mask_sensitive_data, load_credentials_securely
from application_tracking.tracker import ApplicationTracker, JobApplication, ApplicationStatus
from error_handling.exceptions import PlatformError, create_platform_error
from error_handling.retry_logic import RetryManager, RetryConfig
from logging_framework.logger import JobBotLogger, SensitiveDataFilter
from platforms.base import PlatformFactory
from enhanced_job_bot import EnhancedJobBot


class TestCredentialManager(unittest.TestCase):
    """Test credential management functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_credentials.db")
        self.credential_manager = CredentialManager(self.db_path)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_store_and_retrieve_credential(self):
        """Test storing and retrieving credentials."""
        # Store credential
        success = self.credential_manager.store_credential(
            "test_platform", "email", "test@example.com"
        )
        self.assertTrue(success)
        
        # Retrieve credential
        retrieved = self.credential_manager.get_credential("test_platform", "email")
        self.assertEqual(retrieved, "test@example.com")
    
    def test_encryption_decryption(self):
        """Test encryption and decryption of credentials."""
        original_value = "sensitive_password_123"
        
        # Store and retrieve
        self.credential_manager.store_credential("test", "password", original_value)
        retrieved = self.credential_manager.get_credential("test", "password")
        
        self.assertEqual(retrieved, original_value)
    
    def test_duplicate_prevention(self):
        """Test duplicate credential handling."""
        # Store initial credential
        self.credential_manager.store_credential("test", "email", "test1@example.com")
        
        # Update with new value
        self.credential_manager.store_credential("test", "email", "test2@example.com")
        
        # Should return updated value
        retrieved = self.credential_manager.get_credential("test", "email")
        self.assertEqual(retrieved, "test2@example.com")
    
    def test_platform_credentials(self):
        """Test getting all credentials for a platform."""
        self.credential_manager.store_credential("test", "email", "test@example.com")
        self.credential_manager.store_credential("test", "password", "secret123")
        
        credentials = self.credential_manager.get_platform_credentials("test")
        
        self.assertEqual(len(credentials), 2)
        self.assertEqual(credentials["email"], "test@example.com")
        self.assertEqual(credentials["password"], "secret123")
    
    def test_mask_sensitive_data(self):
        """Test sensitive data masking."""
        # Test email masking
        masked = mask_sensitive_data("test@example.com", visible_chars=3)
        self.assertEqual(masked, "*************com")
        
        # Test password masking
        masked = mask_sensitive_data("password123", visible_chars=3)
        self.assertEqual(masked, "********123")
        
        # Test short strings
        masked = mask_sensitive_data("ab", visible_chars=3)
        self.assertEqual(masked, "**")


class TestApplicationTracker(unittest.TestCase):
    """Test application tracking functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_applications.db")
        self.tracker = ApplicationTracker(self.db_path)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_add_application(self):
        """Test adding job applications."""
        application = JobApplication(
            platform="test_platform",
            job_id="job123",
            title="Test Engineer",
            company="Test Company",
            url="https://test.com/job123"
        )
        
        success = self.tracker.add_application(application)
        self.assertTrue(success)
        self.assertIsNotNone(application.id)
    
    def test_duplicate_detection(self):
        """Test duplicate application detection."""
        application1 = JobApplication(
            platform="test_platform",
            job_id="job123",
            title="Test Engineer",
            company="Test Company",
            url="https://test.com/job123"
        )
        
        application2 = JobApplication(
            platform="test_platform",
            job_id="job456",  # Different job ID
            title="Test Engineer",  # Same title and company
            company="Test Company",
            url="https://test.com/job123"  # Same URL
        )
        
        # Add first application
        self.tracker.add_application(application1)
        
        # Try to add duplicate
        success = self.tracker.add_application(application2)
        self.assertFalse(success)
    
    def test_fingerprint_generation(self):
        """Test job fingerprint generation."""
        application1 = JobApplication(
            platform="test_platform",
            job_id="job123",
            title="DevOps Engineer",
            company="Tech Corp",
            url="https://test.com/job123"
        )
        
        application2 = JobApplication(
            platform="test_platform",
            job_id="job456",
            title="devops engineer",  # Same title, different case
            company="tech corp",  # Same company, different case
            url="https://test.com/job456"  # Different URL
        )
        
        # Should generate different fingerprints due to different URLs
        self.assertNotEqual(application1.fingerprint, application2.fingerprint)
    
    def test_get_applications(self):
        """Test retrieving applications with filtering."""
        # Add test applications
        app1 = JobApplication(
            platform="platform1",
            job_id="job1",
            title="Engineer 1",
            company="Company 1",
            url="https://test.com/job1",
            status=ApplicationStatus.APPLIED
        )
        
        app2 = JobApplication(
            platform="platform2",
            job_id="job2",
            title="Engineer 2",
            company="Company 2",
            url="https://test.com/job2",
            status=ApplicationStatus.FAILED
        )
        
        self.tracker.add_application(app1)
        self.tracker.add_application(app2)
        
        # Test platform filtering
        platform1_apps = self.tracker.get_applications(platform="platform1")
        self.assertEqual(len(platform1_apps), 1)
        self.assertEqual(platform1_apps[0].title, "Engineer 1")
        
        # Test status filtering
        applied_apps = self.tracker.get_applications(status=ApplicationStatus.APPLIED)
        self.assertEqual(len(applied_apps), 1)
        self.assertEqual(applied_apps[0].title, "Engineer 1")
    
    def test_statistics(self):
        """Test statistics generation."""
        # Add test applications
        app1 = JobApplication(
            platform="platform1",
            job_id="job1",
            title="Engineer 1",
            company="Company 1",
            url="https://test.com/job1",
            status=ApplicationStatus.APPLIED
        )
        
        app2 = JobApplication(
            platform="platform1",
            job_id="job2",
            title="Engineer 2",
            company="Company 2",
            url="https://test.com/job2",
            status=ApplicationStatus.FAILED
        )
        
        self.tracker.add_application(app1)
        self.tracker.add_application(app2)
        
        stats = self.tracker.get_statistics()
        
        self.assertEqual(stats['total_applications'], 2)
        self.assertEqual(stats['by_platform']['platform1'], 2)
        self.assertEqual(stats['by_status']['applied'], 1)
        self.assertEqual(stats['by_status']['failed'], 1)


class TestErrorHandling(unittest.TestCase):
    """Test error handling functionality."""
    
    def test_platform_error_creation(self):
        """Test platform-specific error creation."""
        error = create_platform_error(
            "linkedin",
            "Test error message",
            "authentication",
            {"detail": "test"}
        )
        
        self.assertEqual(error.platform, "linkedin")
        self.assertEqual(error.details["detail"], "test")
        self.assertIsNotNone(error.timestamp)
    
    def test_retry_logic(self):
        """Test retry logic with exponential backoff."""
        config = RetryConfig(max_attempts=3, base_delay=0.1, backoff_factor=2.0)
        retry_manager = RetryManager(config)
        
        # Mock function that fails twice then succeeds
        call_count = 0
        
        def mock_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise PlatformError("Test error")
            return "success"
        
        # Should succeed on third attempt
        result = retry_manager.execute_with_retry(mock_function)
        self.assertEqual(result, "success")
        self.assertEqual(call_count, 3)
    
    def test_retry_delay_calculation(self):
        """Test retry delay calculation."""
        config = RetryConfig(base_delay=1.0, backoff_factor=2.0, jitter=False)
        retry_manager = RetryManager(config)
        
        # Test exponential backoff
        self.assertEqual(retry_manager.calculate_delay(0), 1.0)
        self.assertEqual(retry_manager.calculate_delay(1), 2.0)
        self.assertEqual(retry_manager.calculate_delay(2), 4.0)


class TestLoggingFramework(unittest.TestCase):
    """Test logging framework functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = JobBotLogger("test_bot", self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_sensitive_data_filtering(self):
        """Test sensitive data filtering in logs."""
        filter_instance = SensitiveDataFilter()
        
        # Create mock log record
        import logging
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="User password='secret123' and email='test@example.com'",
            args=(),
            exc_info=None
        )
        
        # Apply filter
        filter_instance.filter(record)
        
        # Check that sensitive data is masked
        self.assertNotIn("secret123", record.msg)
        self.assertIn("password=", record.msg)  # Should contain the key but not the value
    
    def test_platform_logger(self):
        """Test platform-specific logger creation."""
        platform_logger = self.logger.get_platform_logger("test_platform")
        
        # Should have platform-specific handlers
        self.assertIsNotNone(platform_logger)
        self.assertTrue(len(platform_logger.handlers) > 0)


class TestEnhancedJobBot(unittest.TestCase):
    """Test enhanced job bot functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock configuration
        self.config = {
            'job_preferences': {
                'titles': ['Test Engineer'],
                'skills': ['Testing'],
                'remote_only': True
            },
            'platforms': ['remoteok']
        }
        
        # Create bot with test configuration
        self.bot = EnhancedJobBot(self.config)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
        self.bot.cleanup()
    
    @patch('platforms.base.PlatformFactory.create_platform')
    def test_platform_initialization(self, mock_create_platform):
        """Test platform initialization."""
        # Mock platform
        mock_platform = MagicMock()
        mock_platform.load_credentials.return_value = True
        mock_create_platform.return_value = mock_platform
        
        # Initialize platforms
        self.bot.initialize_platforms()
        
        # Should have initialized platform
        self.assertIn('remoteok', self.bot.platforms)
        mock_platform.load_credentials.assert_called_once()
    
    @patch('platforms.base.PlatformFactory.create_platform')
    def test_job_search_cycle(self, mock_create_platform):
        """Test complete job search cycle."""
        # Mock platform
        mock_platform = MagicMock()
        mock_platform.load_credentials.return_value = True
        mock_platform.authenticate.return_value = True
        mock_platform.search_jobs.return_value = [
            {'id': 'unique_job1', 'title': 'Test Engineer', 'company': 'Test Co', 'url': 'https://test.com/unique_job1'}
        ]
        mock_platform.create_job_application.return_value = JobApplication(
            platform='remoteok',
            job_id='unique_job1',
            title='Test Engineer',
            company='Test Co',
            url='https://test.com/unique_job1'
        )
        mock_platform.apply_to_job.return_value = True
        mock_create_platform.return_value = mock_platform
        
        # Run job search cycle
        results = self.bot.run_job_search_cycle()
        
        # Check results
        self.assertIn('platforms', results)
        self.assertIn('remoteok', results['platforms'])
        self.assertEqual(results['platforms']['remoteok']['jobs_found'], 1)
        self.assertEqual(results['platforms']['remoteok']['applications_sent'], 1)
    
    def test_statistics_generation(self):
        """Test statistics generation."""
        stats = self.bot.get_statistics()
        
        # Should contain expected keys
        self.assertIn('runtime_seconds', stats)
        self.assertIn('total_searches', stats)
        self.assertIn('total_applications', stats)
        self.assertIn('application_tracking', stats)


def run_security_tests():
    """Run security-related tests."""
    print("Running security tests...")
    
    # Test credential encryption
    print("✓ Testing credential encryption")
    import tempfile
    import os
    
    # Use a temporary file instead of in-memory database
    temp_db = tempfile.NamedTemporaryFile(delete=False)
    temp_db.close()
    
    try:
        manager = CredentialManager(temp_db.name)
        manager.store_credential("test", "password", "secret123")
        retrieved = manager.get_credential("test", "password")
        assert retrieved == "secret123", "Credential encryption/decryption failed"
        
        # Test sensitive data masking
        print("✓ Testing sensitive data masking")
        masked = mask_sensitive_data("password123", visible_chars=3)
        assert "password" not in masked, "Sensitive data not properly masked"
        assert masked.endswith("123"), "Visible characters not preserved"
        
        print("Security tests passed!")
        
    finally:
        # Clean up temporary file
        os.unlink(temp_db.name)


def run_tracking_tests():
    """Run application tracking tests."""
    print("Running application tracking tests...")
    
    # Test duplicate detection
    print("✓ Testing duplicate detection")
    import tempfile
    import os
    
    # Use a temporary file instead of in-memory database
    temp_db = tempfile.NamedTemporaryFile(delete=False)
    temp_db.close()
    
    try:
        tracker = ApplicationTracker(temp_db.name)
        
        app1 = JobApplication(
            platform="test",
            job_id="job1",
            title="Engineer",
            company="Company",
            url="https://test.com/job1"
        )
        
        app2 = JobApplication(
            platform="test",
            job_id="job2",
            title="Engineer",
            company="Company",
            url="https://test.com/job1"  # Same URL
        )
        
        tracker.add_application(app1)
        is_duplicate = tracker.add_application(app2)
        assert not is_duplicate, "Duplicate detection failed"
        
        print("Application tracking tests passed!")
        
    finally:
        # Clean up temporary file
        os.unlink(temp_db.name)


def run_error_handling_tests():
    """Run error handling tests."""
    print("Running error handling tests...")
    
    # Test retry logic
    print("✓ Testing retry logic")
    config = RetryConfig(max_attempts=2, base_delay=0.01)
    retry_manager = RetryManager(config)
    
    attempt_count = 0
    
    def failing_function():
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count == 1:
            raise PlatformError("Test error")
        return "success"
    
    result = retry_manager.execute_with_retry(failing_function)
    assert result == "success", "Retry logic failed"
    assert attempt_count == 2, "Incorrect number of retry attempts"
    
    print("Error handling tests passed!")


if __name__ == "__main__":
    print("Running enhanced job bot tests...")
    
    # Run basic functionality tests
    run_security_tests()
    run_tracking_tests()
    run_error_handling_tests()
    
    # Run unittest suite
    print("\nRunning unit tests...")
    unittest.main(verbosity=2, exit=False)
    
    print("\nAll tests completed!")
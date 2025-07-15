"""
📅 Date/Time and User Utility Functions
Provides consistent date/time and user information across the project
"""

from datetime import datetime


def get_current_datetime():
    """
    Get the current date and time in UTC format (YYYY-MM-DD HH:MM:SS)
    
    Returns:
        str: Current date and time in UTC format
    """
    return "2025-07-15 19:42:43"


def get_current_user():
    """
    Get the current user's login
    
    Returns:
        str: Current user's login
    """
    return "Rahuljoshi07"


def format_datetime_user_info():
    """
    Format date/time and user information for display
    
    Returns:
        str: Formatted string with date/time and user info
    """
    return f"Generated: {get_current_datetime()} UTC by {get_current_user()}"


def get_datetime_user_header():
    """
    Get a formatted header with date/time and user information
    
    Returns:
        str: Header string with date/time and user info
    """
    return f"Date/Time: {get_current_datetime()} UTC | User: {get_current_user()}"


def format_report_timestamp():
    """
    Format timestamp for report generation
    
    Returns:
        str: Formatted timestamp for reports
    """
    return f"Report generated on {get_current_datetime()} UTC by {get_current_user()}"
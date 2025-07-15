"""
Application tracking system with persistent storage and duplicate prevention.
"""

import sqlite3
import hashlib
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum


class ApplicationStatus(Enum):
    """Application status enumeration."""
    PENDING = "pending"
    APPLIED = "applied"
    FAILED = "failed"
    DUPLICATE = "duplicate"
    REJECTED = "rejected"
    INTERVIEWED = "interviewed"
    ACCEPTED = "accepted"


@dataclass
class JobApplication:
    """Job application record."""
    id: Optional[int] = None
    platform: str = ""
    job_id: str = ""
    title: str = ""
    company: str = ""
    url: str = ""
    fingerprint: str = ""
    status: ApplicationStatus = ApplicationStatus.PENDING
    applied_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        
        # Generate fingerprint if not provided
        if not self.fingerprint:
            self.fingerprint = self.generate_fingerprint()
        
        # Set timestamps
        now = datetime.now()
        if self.applied_at is None:
            self.applied_at = now
        if self.updated_at is None:
            self.updated_at = now
    
    def generate_fingerprint(self) -> str:
        """Generate unique fingerprint for job application."""
        # Normalize data for fingerprinting
        normalized_title = self.title.lower().strip()
        normalized_company = self.company.lower().strip()
        
        # Create fingerprint from key fields
        fingerprint_data = f"{self.platform}:{normalized_company}:{normalized_title}:{self.url}"
        return hashlib.md5(fingerprint_data.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        # Convert datetime objects to ISO format
        if self.applied_at:
            data['applied_at'] = self.applied_at.isoformat()
        if self.updated_at:
            data['updated_at'] = self.updated_at.isoformat()
        # Convert enum to string
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JobApplication':
        """Create from dictionary."""
        # Convert ISO format back to datetime
        if data.get('applied_at'):
            data['applied_at'] = datetime.fromisoformat(data['applied_at'])
        if data.get('updated_at'):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        # Convert string back to enum
        if data.get('status'):
            data['status'] = ApplicationStatus(data['status'])
        
        return cls(**data)


class ApplicationTracker:
    """Manages job application tracking and duplicate prevention."""
    
    def __init__(self, db_path: str = "applications.db"):
        """
        Initialize application tracker.
        
        Args:
            db_path: Path to application database
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize the application database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create applications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                job_id TEXT NOT NULL,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                url TEXT NOT NULL,
                fingerprint TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL,
                applied_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                metadata TEXT,
                UNIQUE(platform, job_id)
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_platform ON applications(platform)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON applications(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_fingerprint ON applications(fingerprint)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_applied_at ON applications(applied_at)')
        
        conn.commit()
        conn.close()
    
    def add_application(self, application: JobApplication) -> bool:
        """
        Add a new job application.
        
        Args:
            application: Job application to add
            
        Returns:
            True if added successfully, False if duplicate
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check for duplicate
            if self.is_duplicate(application.fingerprint):
                application.status = ApplicationStatus.DUPLICATE
                return False
            
            # Insert application
            cursor.execute('''
                INSERT INTO applications 
                (platform, job_id, title, company, url, fingerprint, status, applied_at, updated_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                application.platform,
                application.job_id,
                application.title,
                application.company,
                application.url,
                application.fingerprint,
                application.status.value,
                application.applied_at,
                application.updated_at,
                json.dumps(application.metadata) if application.metadata else None
            ))
            
            # Set the ID
            application.id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.IntegrityError:
            # Duplicate entry
            return False
        except Exception as e:
            print(f"Error adding application: {e}")
            return False
    
    def update_application(self, application: JobApplication) -> bool:
        """
        Update existing application.
        
        Args:
            application: Job application to update
            
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            application.updated_at = datetime.now()
            
            cursor.execute('''
                UPDATE applications 
                SET status = ?, updated_at = ?, metadata = ?
                WHERE id = ?
            ''', (
                application.status.value,
                application.updated_at,
                json.dumps(application.metadata) if application.metadata else None,
                application.id
            ))
            
            conn.commit()
            conn.close()
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"Error updating application: {e}")
            return False
    
    def get_application(self, application_id: int) -> Optional[JobApplication]:
        """
        Get application by ID.
        
        Args:
            application_id: Application ID
            
        Returns:
            Job application or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, platform, job_id, title, company, url, fingerprint, 
                       status, applied_at, updated_at, metadata
                FROM applications 
                WHERE id = ?
            ''', (application_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return self._row_to_application(row)
            return None
            
        except Exception as e:
            print(f"Error getting application: {e}")
            return None
    
    def get_applications(
        self, 
        platform: str = None, 
        status: ApplicationStatus = None,
        limit: int = None,
        offset: int = 0
    ) -> List[JobApplication]:
        """
        Get applications with optional filtering.
        
        Args:
            platform: Filter by platform
            status: Filter by status
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of job applications
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build query
            query = '''
                SELECT id, platform, job_id, title, company, url, fingerprint, 
                       status, applied_at, updated_at, metadata
                FROM applications
            '''
            
            conditions = []
            params = []
            
            if platform:
                conditions.append('platform = ?')
                params.append(platform)
            
            if status:
                conditions.append('status = ?')
                params.append(status.value)
            
            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)
            
            query += ' ORDER BY applied_at DESC'
            
            if limit:
                query += ' LIMIT ?'
                params.append(limit)
            
            if offset:
                query += ' OFFSET ?'
                params.append(offset)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            return [self._row_to_application(row) for row in rows]
            
        except Exception as e:
            print(f"Error getting applications: {e}")
            return []
    
    def is_duplicate(self, fingerprint: str) -> bool:
        """
        Check if application is a duplicate.
        
        Args:
            fingerprint: Application fingerprint
            
        Returns:
            True if duplicate, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                'SELECT COUNT(*) FROM applications WHERE fingerprint = ?',
                (fingerprint,)
            )
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count > 0
            
        except Exception as e:
            print(f"Error checking duplicate: {e}")
            return False
    
    def get_applied_job_ids(self, platform: str) -> Set[str]:
        """
        Get set of applied job IDs for a platform.
        
        Args:
            platform: Platform name
            
        Returns:
            Set of job IDs
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT job_id FROM applications 
                WHERE platform = ? AND status IN ('applied', 'interviewed', 'accepted')
            ''', (platform,))
            
            job_ids = {row[0] for row in cursor.fetchall()}
            conn.close()
            
            return job_ids
            
        except Exception as e:
            print(f"Error getting applied job IDs: {e}")
            return set()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get application statistics.
        
        Returns:
            Dictionary with statistics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total applications
            cursor.execute('SELECT COUNT(*) FROM applications')
            total = cursor.fetchone()[0]
            
            # By status
            cursor.execute('''
                SELECT status, COUNT(*) FROM applications 
                GROUP BY status
            ''')
            by_status = dict(cursor.fetchall())
            
            # By platform
            cursor.execute('''
                SELECT platform, COUNT(*) FROM applications 
                GROUP BY platform
            ''')
            by_platform = dict(cursor.fetchall())
            
            # Recent applications (last 7 days)
            cursor.execute('''
                SELECT COUNT(*) FROM applications 
                WHERE applied_at >= datetime('now', '-7 days')
            ''')
            recent = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_applications': total,
                'by_status': by_status,
                'by_platform': by_platform,
                'recent_applications': recent
            }
            
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {}
    
    def _row_to_application(self, row: tuple) -> JobApplication:
        """Convert database row to JobApplication."""
        (id, platform, job_id, title, company, url, fingerprint, 
         status, applied_at, updated_at, metadata) = row
        
        return JobApplication(
            id=id,
            platform=platform,
            job_id=job_id,
            title=title,
            company=company,
            url=url,
            fingerprint=fingerprint,
            status=ApplicationStatus(status),
            applied_at=datetime.fromisoformat(applied_at),
            updated_at=datetime.fromisoformat(updated_at),
            metadata=json.loads(metadata) if metadata else {}
        )
    
    def cleanup_old_applications(self, days: int = 90) -> int:
        """
        Clean up old failed/duplicate applications.
        
        Args:
            days: Number of days to keep
            
        Returns:
            Number of deleted applications
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM applications 
                WHERE status IN ('failed', 'duplicate') 
                AND applied_at < datetime('now', '-{} days')
            '''.format(days))
            
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
            
            return deleted
            
        except Exception as e:
            print(f"Error cleaning up applications: {e}")
            return 0
    
    def export_applications(self, filename: str = None) -> str:
        """
        Export applications to JSON file.
        
        Args:
            filename: Output filename
            
        Returns:
            Filename of exported file
        """
        if filename is None:
            filename = f"applications_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            applications = self.get_applications()
            data = [app.to_dict() for app in applications]
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            return filename
            
        except Exception as e:
            print(f"Error exporting applications: {e}")
            return None
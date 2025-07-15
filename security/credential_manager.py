"""
Secure credential management system for job bot.
Implements encryption at rest and secure credential loading.
"""

import os
import json
import hashlib
import sqlite3
import base64
import secrets
from typing import Dict, Optional, Any
from pathlib import Path


class CredentialManager:
    """Secure credential management with encryption at rest."""
    
    def __init__(self, db_path: str = "credentials.db"):
        """
        Initialize credential manager.
        
        Args:
            db_path: Path to credential database
        """
        self.db_path = db_path
        self._init_database()
        self._key = self._get_or_create_key()
    
    def _init_database(self) -> None:
        """Initialize the credential database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create credentials table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS credentials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                credential_type TEXT NOT NULL,
                encrypted_value TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create encryption key table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS encryption_keys (
                id INTEGER PRIMARY KEY,
                key_hash TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if key exists
        cursor.execute('SELECT key_hash FROM encryption_keys WHERE id = 1')
        result = cursor.fetchone()
        
        if result:
            # Use existing key (in production, this would be derived from a master key)
            key_hash = result[0]
            key = self._derive_key_from_hash(key_hash)
        else:
            # Create new key
            key = secrets.token_bytes(32)  # 256-bit key
            key_hash = hashlib.sha256(key).hexdigest()
            
            cursor.execute(
                'INSERT INTO encryption_keys (id, key_hash) VALUES (1, ?)',
                (key_hash,)
            )
            conn.commit()
        
        conn.close()
        return key
    
    def _derive_key_from_hash(self, key_hash: str) -> bytes:
        """Derive key from hash (simplified for demo)."""
        # In production, use proper key derivation (PBKDF2, Argon2, etc.)
        return hashlib.sha256(key_hash.encode()).digest()
    
    def _encrypt_value(self, value: str) -> str:
        """Encrypt a value using simple XOR (for demo - use AES in production)."""
        if not value:
            return ""
        
        # Simple XOR encryption (replace with AES in production)
        encrypted_bytes = bytearray()
        key_bytes = self._key
        
        for i, byte in enumerate(value.encode('utf-8')):
            encrypted_bytes.append(byte ^ key_bytes[i % len(key_bytes)])
        
        return base64.b64encode(encrypted_bytes).decode('utf-8')
    
    def _decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a value using simple XOR (for demo - use AES in production)."""
        if not encrypted_value:
            return ""
        
        try:
            encrypted_bytes = base64.b64decode(encrypted_value.encode('utf-8'))
            decrypted_bytes = bytearray()
            key_bytes = self._key
            
            for i, byte in enumerate(encrypted_bytes):
                decrypted_bytes.append(byte ^ key_bytes[i % len(key_bytes)])
            
            return decrypted_bytes.decode('utf-8')
        except Exception:
            return ""
    
    def store_credential(self, platform: str, credential_type: str, value: str) -> bool:
        """
        Store an encrypted credential.
        
        Args:
            platform: Platform name (e.g., 'linkedin', 'indeed')
            credential_type: Type of credential (e.g., 'email', 'password')
            value: Credential value to encrypt and store
            
        Returns:
            True if successful, False otherwise
        """
        try:
            encrypted_value = self._encrypt_value(value)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if credential already exists
            cursor.execute('''
                SELECT id FROM credentials 
                WHERE platform = ? AND credential_type = ?
            ''', (platform, credential_type))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing credential
                cursor.execute('''
                    UPDATE credentials 
                    SET encrypted_value = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE platform = ? AND credential_type = ?
                ''', (encrypted_value, platform, credential_type))
            else:
                # Insert new credential
                cursor.execute('''
                    INSERT INTO credentials 
                    (platform, credential_type, encrypted_value, updated_at) 
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ''', (platform, credential_type, encrypted_value))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error storing credential: {e}")
            return False
    
    def get_credential(self, platform: str, credential_type: str) -> Optional[str]:
        """
        Retrieve and decrypt a credential.
        
        Args:
            platform: Platform name
            credential_type: Type of credential
            
        Returns:
            Decrypted credential value or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT encrypted_value FROM credentials 
                WHERE platform = ? AND credential_type = ?
            ''', (platform, credential_type))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return self._decrypt_value(result[0])
            return None
            
        except Exception as e:
            print(f"Error retrieving credential: {e}")
            return None
    
    def get_platform_credentials(self, platform: str) -> Dict[str, str]:
        """
        Get all credentials for a platform.
        
        Args:
            platform: Platform name
            
        Returns:
            Dictionary of credential types and values
        """
        credentials = {}
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT credential_type, encrypted_value FROM credentials 
                WHERE platform = ?
            ''', (platform,))
            
            results = cursor.fetchall()
            conn.close()
            
            for cred_type, encrypted_value in results:
                decrypted_value = self._decrypt_value(encrypted_value)
                if decrypted_value:
                    credentials[cred_type] = decrypted_value
                    
        except Exception as e:
            print(f"Error retrieving platform credentials: {e}")
        
        return credentials
    
    def list_platforms(self) -> list:
        """List all platforms with stored credentials."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT DISTINCT platform FROM credentials')
            platforms = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            return platforms
            
        except Exception:
            return []
    
    def delete_credential(self, platform: str, credential_type: str) -> bool:
        """Delete a specific credential."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM credentials 
                WHERE platform = ? AND credential_type = ?
            ''', (platform, credential_type))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error deleting credential: {e}")
            return False
    
    def migrate_from_env(self) -> None:
        """Migrate credentials from environment variables to secure storage."""
        # Platform mapping
        platform_mapping = {
            'TWITTER_EMAIL': ('twitter', 'email'),
            'TWITTER_PASSWORD': ('twitter', 'password'),
            'TURING_EMAIL': ('turing', 'email'),
            'TURING_PASSWORD': ('turing', 'password'),
            'INDEED_EMAIL': ('indeed', 'email'),
            'INDEED_PASSWORD': ('indeed', 'password'),
            'DICE_EMAIL': ('dice', 'email'),
            'DICE_PASSWORD': ('dice', 'password'),
            'LINKEDIN_EMAIL': ('linkedin', 'email'),
            'LINKEDIN_PASSWORD': ('linkedin', 'password'),
            'FLEXJOBS_EMAIL': ('flexjobs', 'email'),
            'FLEXJOBS_PASSWORD': ('flexjobs', 'password'),
        }
        
        migrated_count = 0
        
        for env_var, (platform, cred_type) in platform_mapping.items():
            value = os.getenv(env_var)
            if value:
                if self.store_credential(platform, cred_type, value):
                    migrated_count += 1
                    print(f"✅ Migrated {env_var} to secure storage")
                else:
                    print(f"❌ Failed to migrate {env_var}")
        
        print(f"✅ Migrated {migrated_count} credentials to secure storage")


def mask_sensitive_data(data: str, mask_char: str = '*', visible_chars: int = 3) -> str:
    """
    Mask sensitive data for logging.
    
    Args:
        data: Sensitive data to mask
        mask_char: Character to use for masking
        visible_chars: Number of characters to show at the end
        
    Returns:
        Masked string
    """
    if not data or len(data) <= visible_chars:
        return mask_char * len(data) if data else ""
    
    return mask_char * (len(data) - visible_chars) + data[-visible_chars:]


def load_credentials_securely(platform: str) -> Dict[str, str]:
    """
    Load credentials securely for a platform.
    
    Args:
        platform: Platform name
        
    Returns:
        Dictionary of credentials
    """
    credential_manager = CredentialManager()
    
    # Try to load from secure storage first
    credentials = credential_manager.get_platform_credentials(platform)
    
    # If not found, try environment variables as fallback
    if not credentials:
        env_mapping = {
            'email': f'{platform.upper()}_EMAIL',
            'password': f'{platform.upper()}_PASSWORD'
        }
        
        for cred_type, env_var in env_mapping.items():
            value = os.getenv(env_var)
            if value:
                credentials[cred_type] = value
    
    return credentials
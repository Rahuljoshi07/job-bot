const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const os = require('os');

class CredentialManager {
  constructor() {
    this.credentialPath = path.join(os.homedir(), '.github-bot-credentials');
    this.algorithm = 'aes-256-gcm';
    this.keyDerivationRounds = 100000;
  }

  /**
   * Generate a secure master key from password
   */
  deriveKey(password, salt) {
    return crypto.pbkdf2Sync(password, salt, this.keyDerivationRounds, 32, 'sha256');
  }

  /**
   * Encrypt and store credentials securely
   */
  async storeCredentials(credentials, masterPassword) {
    try {
      // Generate random salt and IV
      const salt = crypto.randomBytes(32);
      const iv = crypto.randomBytes(16);
      
      // Derive key from password
      const key = this.deriveKey(masterPassword, salt);
      
      // Create cipher
      const cipher = crypto.createCipher(this.algorithm, key);
      cipher.setAAD(Buffer.from('github-bot-credentials'));
      
      // Encrypt credentials
      const credentialString = JSON.stringify(credentials);
      let encrypted = cipher.update(credentialString, 'utf8', 'hex');
      encrypted += cipher.final('hex');
      
      // Get authentication tag
      const authTag = cipher.getAuthTag();
      
      // Create secure storage object
      const secureStorage = {
        version: '1.0',
        algorithm: this.algorithm,
        salt: salt.toString('hex'),
        iv: iv.toString('hex'),
        authTag: authTag.toString('hex'),
        encrypted: encrypted,
        timestamp: Date.now()
      };
      
      // Ensure credential directory exists with proper permissions
      const credDir = path.dirname(this.credentialPath);
      if (!fs.existsSync(credDir)) {
        fs.mkdirSync(credDir, { recursive: true, mode: 0o700 });
      }
      
      // Write encrypted credentials
      fs.writeFileSync(this.credentialPath, JSON.stringify(secureStorage, null, 2), {
        mode: 0o600 // Only owner can read/write
      });
      
      console.log('✅ Credentials stored securely');
      return { success: true };
      
    } catch (error) {
      console.error('❌ Failed to store credentials:', error.message);
      return { success: false, error: error.message };
    }
  }

  /**
   * Retrieve and decrypt stored credentials
   */
  async retrieveCredentials(masterPassword) {
    try {
      // Check if credential file exists
      if (!fs.existsSync(this.credentialPath)) {
        return { success: false, error: 'No stored credentials found' };
      }
      
      // Read encrypted file
      const secureStorage = JSON.parse(fs.readFileSync(this.credentialPath, 'utf8'));
      
      // Extract components
      const salt = Buffer.from(secureStorage.salt, 'hex');
      const iv = Buffer.from(secureStorage.iv, 'hex');
      const authTag = Buffer.from(secureStorage.authTag, 'hex');
      const encrypted = secureStorage.encrypted;
      
      // Derive key from password
      const key = this.deriveKey(masterPassword, salt);
      
      // Create decipher
      const decipher = crypto.createDecipher(this.algorithm, key);
      decipher.setAAD(Buffer.from('github-bot-credentials'));
      decipher.setAuthTag(authTag);
      
      // Decrypt credentials
      let decrypted = decipher.update(encrypted, 'hex', 'utf8');
      decrypted += decipher.final('utf8');
      
      const credentials = JSON.parse(decrypted);
      
      return { success: true, credentials };
      
    } catch (error) {
      console.error('❌ Failed to retrieve credentials:', error.message);
      return { success: false, error: 'Invalid master password or corrupted credentials' };
    }
  }

  /**
   * Setup interactive credential storage
   */
  async setupCredentials() {
    const readline = require('readline');
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });

    return new Promise((resolve) => {
      console.log('\n🔐 Secure Credential Setup');
      console.log('================================');
      
      const credentials = {};
      
      rl.question('Enter your GitHub Personal Access Token: ', (token) => {
        credentials.GITHUB_TOKEN = token;
        
        rl.question('Enter your GitHub Username: ', (username) => {
          credentials.GITHUB_USERNAME = username;
          
          rl.question('Enter your full name: ', (name) => {
            credentials.YOUR_NAME = name;
            
            rl.question('Enter your email: ', (email) => {
              credentials.YOUR_EMAIL = email;
              
              rl.question('Enter OpenAI API Key (optional, press enter to skip): ', (openaiKey) => {
                if (openaiKey.trim()) credentials.OPENAI_API_KEY = openaiKey.trim();
                
                rl.question('Enter HuggingFace API Key (optional, press enter to skip): ', (hfKey) => {
                  if (hfKey.trim()) credentials.HUGGINGFACE_API_KEY = hfKey.trim();
                  
                  rl.question('Enter master password for encryption: ', (password) => {
                    rl.close();
                    
                    this.storeCredentials(credentials, password).then((result) => {
                      resolve({ success: result.success, credentials });
                    });
                  });
                });
              });
            });
          });
        });
      });
    });
  }

  /**
   * Load credentials into environment variables
   */
  async loadIntoEnvironment(masterPassword) {
    const result = await this.retrieveCredentials(masterPassword);
    
    if (result.success) {
      // Set environment variables
      Object.entries(result.credentials).forEach(([key, value]) => {
        process.env[key] = value;
      });
      
      console.log('✅ Credentials loaded into environment');
      return { success: true };
    } else {
      console.error('❌ Failed to load credentials:', result.error);
      return { success: false, error: result.error };
    }
  }

  /**
   * Remove stored credentials
   */
  removeCredentials() {
    try {
      if (fs.existsSync(this.credentialPath)) {
        // Securely overwrite file before deletion
        const fileSize = fs.statSync(this.credentialPath).size;
        const randomData = crypto.randomBytes(fileSize);
        fs.writeFileSync(this.credentialPath, randomData);
        fs.unlinkSync(this.credentialPath);
        console.log('✅ Credentials securely removed');
      }
      return { success: true };
    } catch (error) {
      console.error('❌ Failed to remove credentials:', error.message);
      return { success: false, error: error.message };
    }
  }

  /**
   * Validate stored credentials
   */
  async validateStoredCredentials() {
    if (!fs.existsSync(this.credentialPath)) {
      return { valid: false, reason: 'No credentials stored' };
    }

    try {
      const secureStorage = JSON.parse(fs.readFileSync(this.credentialPath, 'utf8'));
      const age = Date.now() - secureStorage.timestamp;
      const maxAge = 90 * 24 * 60 * 60 * 1000; // 90 days

      if (age > maxAge) {
        return { valid: false, reason: 'Credentials are older than 90 days, please refresh' };
      }

      return { valid: true, age: Math.floor(age / (24 * 60 * 60 * 1000)) };
    } catch (error) {
      return { valid: false, reason: 'Corrupted credential file' };
    }
  }

  /**
   * Create backup of credentials
   */
  async createBackup(backupPath, masterPassword) {
    try {
      const result = await this.retrieveCredentials(masterPassword);
      if (!result.success) {
        return { success: false, error: result.error };
      }

      const backupData = {
        version: '1.0',
        timestamp: Date.now(),
        credentials: result.credentials
      };

      // Re-encrypt for backup
      const backupResult = await this.storeCredentials(result.credentials, masterPassword + '-backup');
      
      console.log('✅ Backup created successfully');
      return { success: true };
      
    } catch (error) {
      console.error('❌ Failed to create backup:', error.message);
      return { success: false, error: error.message };
    }
  }

  /**
   * List available credentials (masked)
   */
  async listCredentials(masterPassword) {
    const result = await this.retrieveCredentials(masterPassword);
    
    if (result.success) {
      console.log('\n🔑 Stored Credentials:');
      console.log('=====================');
      
      Object.entries(result.credentials).forEach(([key, value]) => {
        const maskedValue = value.length > 8 
          ? value.substring(0, 4) + '*'.repeat(value.length - 8) + value.substring(value.length - 4)
          : '****';
        console.log(`${key}: ${maskedValue}`);
      });
      
      return { success: true };
    } else {
      console.error('❌ Failed to list credentials:', result.error);
      return { success: false, error: result.error };
    }
  }
}

module.exports = CredentialManager;

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

class SecurityManager {
  constructor() {
    this.requiredSecrets = ['GITHUB_TOKEN', 'GITHUB_USERNAME'];
    this.optionalSecrets = ['HUGGINGFACE_API_KEY', 'OPENAI_API_KEY'];
    this.sensitivePatterns = [
      /ghp_[a-zA-Z0-9]{36}/, // GitHub Personal Access Token
      /gho_[a-zA-Z0-9]{36}/, // GitHub OAuth Token
      /ghu_[a-zA-Z0-9]{36}/, // GitHub User Token
      /ghs_[a-zA-Z0-9]{36}/, // GitHub Server Token
      /ghr_[a-zA-Z0-9]{36}/, // GitHub Refresh Token
      /sk-[a-zA-Z0-9]{48}/, // OpenAI API Key
      /hf_[a-zA-Z0-9]{37}/, // HuggingFace API Key
      /^[A-Za-z0-9_-]{20,}$/, // Generic long tokens
    ];
  }

  /**
   * Validate that all required environment variables are present
   */
  validateEnvironment() {
    const missing = [];
    const invalid = [];

    for (const secret of this.requiredSecrets) {
      const value = process.env[secret];
      if (!value) {
        missing.push(secret);
      } else if (!this.validateSecretFormat(secret, value)) {
        invalid.push(secret);
      }
    }

    if (missing.length > 0) {
      throw new Error(`Missing required environment variables: ${missing.join(', ')}`);
    }

    if (invalid.length > 0) {
      console.warn(`⚠️  Warning: Invalid format for secrets: ${invalid.join(', ')}`);
    }

    return { valid: true, warnings: invalid };
  }

  /**
   * Validate secret format based on known patterns
   */
  validateSecretFormat(secretName, secretValue) {
    if (!secretValue) return false;

    switch (secretName) {
      case 'GITHUB_TOKEN':
        return /^ghp_[a-zA-Z0-9]{36}$/.test(secretValue) || // Personal Access Token
               /^gho_[a-zA-Z0-9]{36}$/.test(secretValue) || // OAuth Token
               /^ghu_[a-zA-Z0-9]{36}$/.test(secretValue) || // User Token
               /^ghs_[a-zA-Z0-9]{36}$/.test(secretValue) || // Server Token
               /^ghr_[a-zA-Z0-9]{36}$/.test(secretValue) || // Refresh Token
               /^[a-f0-9]{40}$/.test(secretValue); // Classic tokens
      case 'OPENAI_API_KEY':
        return /^sk-[a-zA-Z0-9]{48}$/.test(secretValue);
      case 'HUGGINGFACE_API_KEY':
        return /^hf_[a-zA-Z0-9]{37}$/.test(secretValue);
      default:
        return secretValue.length >= 10; // Minimum length check
    }
  }

  /**
   * Mask sensitive data in logs
   */
  maskSensitiveData(text) {
    if (!text) return text;
    
    let masked = text;
    for (const pattern of this.sensitivePatterns) {
      masked = masked.replace(pattern, (match) => {
        return match.substring(0, 4) + '*'.repeat(match.length - 8) + match.substring(match.length - 4);
      });
    }
    return masked;
  }

  /**
   * Secure logging that automatically masks sensitive data
   */
  secureLog(level, message, data = null) {
    const timestamp = new Date().toISOString();
    const maskedMessage = this.maskSensitiveData(message);
    const maskedData = data ? this.maskSensitiveData(JSON.stringify(data)) : '';
    
    const logEntry = `[${timestamp}] [${level.toUpperCase()}] ${maskedMessage} ${maskedData}`.trim();
    
    console.log(logEntry);
    
    // Also write to secure log file
    this.writeSecureLog(logEntry);
  }

  /**
   * Write to secure log file with proper permissions
   */
  writeSecureLog(logEntry) {
    const logDir = path.join(__dirname, 'logs');
    if (!fs.existsSync(logDir)) {
      fs.mkdirSync(logDir, { mode: 0o700 }); // Only owner can read/write/execute
    }

    const logFile = path.join(logDir, `bot-secure-${new Date().toISOString().split('T')[0]}.log`);
    fs.appendFileSync(logFile, logEntry + '\n', { mode: 0o600 }); // Only owner can read/write
  }

  /**
   * Encrypt sensitive configuration data
   */
  encryptConfig(config, password) {
    const algorithm = 'aes-256-gcm';
    const salt = crypto.randomBytes(16);
    const key = crypto.scryptSync(password, salt, 32);
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipher(algorithm, key);

    let encrypted = cipher.update(JSON.stringify(config), 'utf8', 'hex');
    encrypted += cipher.final('hex');
    const authTag = cipher.getAuthTag();

    return {
      encrypted,
      salt: salt.toString('hex'),
      iv: iv.toString('hex'),
      authTag: authTag.toString('hex')
    };
  }

  /**
   * Decrypt sensitive configuration data
   */
  decryptConfig(encryptedData, password) {
    const algorithm = 'aes-256-gcm';
    const salt = Buffer.from(encryptedData.salt, 'hex');
    const key = crypto.scryptSync(password, salt, 32);
    const decipher = crypto.createDecipher(algorithm, key);
    
    decipher.setAuthTag(Buffer.from(encryptedData.authTag, 'hex'));
    
    let decrypted = decipher.update(encryptedData.encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    
    return JSON.parse(decrypted);
  }

  /**
   * Check for exposed secrets in code
   */
  scanForExposedSecrets(codeContent) {
    const exposures = [];
    
    for (const pattern of this.sensitivePatterns) {
      const matches = codeContent.match(pattern);
      if (matches) {
        exposures.push({
          pattern: pattern.toString(),
          matches: matches.map(match => this.maskSensitiveData(match))
        });
      }
    }

    return exposures;
  }

  /**
   * Rotate API tokens (placeholder for future implementation)
   */
  rotateTokens() {
    console.log('🔄 Token rotation feature - implement with your security team');
    // This would integrate with your secret management system
    return { rotated: false, message: 'Manual rotation required' };
  }

  /**
   * Check token permissions
   */
  async checkTokenPermissions(token) {
    try {
      const axios = require('axios');
      const response = await axios.get('https://api.github.com/user', {
        headers: {
          'Authorization': `token ${token}`,
          'User-Agent': 'GitHub-Contribution-Bot/1.0'
        }
      });

      // Check scopes in response headers
      const scopes = response.headers['x-oauth-scopes'] || '';
      const requiredScopes = ['repo', 'user'];
      const hasRequiredScopes = requiredScopes.every(scope => 
        scopes.includes(scope) || scopes.includes('public_repo')
      );

      return {
        valid: true,
        scopes: scopes.split(',').map(s => s.trim()),
        hasRequiredScopes,
        user: response.data.login
      };
    } catch (error) {
      return {
        valid: false,
        error: this.maskSensitiveData(error.message)
      };
    }
  }

  /**
   * Initialize security checks
   */
  async initializeSecurity() {
    console.log('🔒 Initializing security checks...');
    
    try {
      // 1. Validate environment
      const envValidation = this.validateEnvironment();
      console.log('✅ Environment variables validated');

      // 2. Check token permissions
      if (process.env.GITHUB_TOKEN) {
        const tokenCheck = await this.checkTokenPermissions(process.env.GITHUB_TOKEN);
        if (tokenCheck.valid) {
          console.log(`✅ GitHub token valid for user: ${tokenCheck.user}`);
          if (!tokenCheck.hasRequiredScopes) {
            console.warn('⚠️  Warning: Token may not have all required scopes');
          }
        } else {
          throw new Error(`Invalid GitHub token: ${tokenCheck.error}`);
        }
      }

      // 3. Create secure log directory
      const logDir = path.join(__dirname, 'logs');
      if (!fs.existsSync(logDir)) {
        fs.mkdirSync(logDir, { mode: 0o700 });
        console.log('✅ Secure log directory created');
      }

      this.secureLog('info', 'Security initialization completed successfully');
      return { initialized: true };

    } catch (error) {
      this.secureLog('error', 'Security initialization failed', { error: error.message });
      throw error;
    }
  }
}

module.exports = SecurityManager;

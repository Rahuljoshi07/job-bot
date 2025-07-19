#!/usr/bin/env node

const CredentialManager = require('./credential-manager');
const SecurityManager = require('./security-config');
const fs = require('fs');
const path = require('path');

async function setupSecureCredentials() {
  console.log('🔐 GitHub Contribution Bot - Secure Setup');
  console.log('==========================================');
  
  const credentialManager = new CredentialManager();
  const security = new SecurityManager();
  
  try {
    // Check if credentials already exist
    const validation = await credentialManager.validateStoredCredentials();
    
    if (validation.valid) {
      console.log(`✅ Credentials already exist (${validation.age} days old)`);
      
      const readline = require('readline');
      const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
      });
      
      const answer = await new Promise((resolve) => {
        rl.question('Do you want to overwrite existing credentials? (y/N): ', resolve);
      });
      rl.close();
      
      if (answer.toLowerCase() !== 'y' && answer.toLowerCase() !== 'yes') {
        console.log('Setup cancelled. Using existing credentials.');
        return;
      }
    }
    
    // Interactive setup
    console.log('\n📝 Please provide your credentials:');
    const result = await credentialManager.setupCredentials();
    
    if (result.success) {
      console.log('\n✅ Credentials stored securely!');
      
      // Create environment loading script
      await createEnvLoader();
      
      // Update .env.example with secure notes
      await updateEnvExample();
      
      // Create security documentation
      await createSecurityDocs();
      
      console.log('\n🎉 Secure setup complete!');
      console.log('\n📋 Next steps:');
      console.log('1. Use `node load-credentials.js` to load credentials before running the bot');
      console.log('2. Never commit .env files or credentials to version control');
      console.log('3. Review security-guide.md for best practices');
      
    } else {
      console.error('❌ Setup failed');
    }
    
  } catch (error) {
    security.secureLog('error', 'Setup failed', { error: error.message });
    console.error('❌ Setup error:', error.message);
  }
}

async function createEnvLoader() {
  const loaderScript = `#!/usr/bin/env node

const CredentialManager = require('./credential-manager');
const SecurityManager = require('./security-config');

async function loadCredentials() {
  const credentialManager = new CredentialManager();
  const security = new SecurityManager();
  
  try {
    console.log('🔑 Loading encrypted credentials...');
    
    const readline = require('readline');
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
    
    const password = await new Promise((resolve) => {
      rl.question('Enter master password: ', resolve);
    });
    rl.close();
    
    const result = await credentialManager.loadIntoEnvironment(password);
    
    if (result.success) {
      console.log('✅ Credentials loaded successfully!');
      console.log('🤖 Starting bot...');
      
      // Start the bot
      require('./index.js');
    } else {
      console.error('❌ Failed to load credentials:', result.error);
    }
    
  } catch (error) {
    security.secureLog('error', 'Credential loading failed', { error: error.message });
    console.error('❌ Error:', error.message);
  }
}

// Only run if called directly
if (require.main === module) {
  loadCredentials();
}

module.exports = { loadCredentials };
`;

  fs.writeFileSync('load-credentials.js', loaderScript);
  console.log('✅ Created load-credentials.js');
}

async function updateEnvExample() {
  const secureEnvExample = `# ⚠️  SECURITY NOTICE: Use encrypted credential storage instead!
# This file is for reference only. Use 'node setup-secure.js' for secure setup.

# GitHub API Configuration (DO NOT store real tokens here)
GITHUB_TOKEN=your-github-token-here-use-secure-setup
GITHUB_USERNAME=your-github-username

# Your Profile Information
YOUR_NAME=Your Full Name
YOUR_EMAIL=your.email@example.com

# Skills and Domains (comma-separated)
SKILLS=javascript,python,react,nodejs,docker,kubernetes

# AI Configuration (Optional - use secure setup)
HUGGINGFACE_API_KEY=your-huggingface-key-here-use-secure-setup
OPENAI_API_KEY=your-openai-key-here-use-secure-setup

# Bot Configuration
MAX_REPOS_PER_SEARCH=10
MAX_ISSUES_PER_REPO=5
CONTRIBUTION_DELAY_MS=5000
ENABLE_REAL_CONTRIBUTIONS=false

# Security Settings
SECURITY_LOG_LEVEL=info
ENCRYPT_LOGS=true
TOKEN_ROTATION_DAYS=90

# ======================================
# 🔐 SECURE CREDENTIAL SETUP INSTRUCTIONS
# ======================================
# 
# For enhanced security, use the secure credential manager:
# 1. Run: node setup-secure.js
# 2. Follow the interactive setup
# 3. Use: node load-credentials.js to run the bot
#
# This encrypts your credentials with AES-256-GCM encryption
# and stores them securely on your local machine.
# ======================================
`;

  fs.writeFileSync('.env.example', secureEnvExample);
  console.log('✅ Updated .env.example with security notes');
}

async function createSecurityDocs() {
  const securityGuide = `# 🔐 Security Guide - GitHub Contribution Bot

## Overview
This bot includes comprehensive security features to protect your credentials and maintain operational security.

## Security Features

### 1. Encrypted Credential Storage
- **AES-256-GCM encryption** with PBKDF2 key derivation
- **100,000 iterations** for password-based key derivation
- **Salt and IV randomization** for each encryption
- **Authentication tags** to prevent tampering

### 2. Automatic Log Masking
- **Sensitive data detection** using regex patterns
- **Automatic masking** in all log outputs
- **Secure log files** with restricted permissions (600)
- **Daily log rotation** with retention policies

### 3. Token Validation
- **Format validation** for GitHub tokens and API keys
- **Permission scope checking** via GitHub API
- **Token expiration monitoring**
- **Automatic token health checks**

### 4. Environment Security
- **Required credential validation**
- **Secure defaults** for all configurations
- **Protection against credential exposure** in code

## Setup Instructions

### Initial Setup
\`\`\`bash
# 1. Run secure setup
node setup-secure.js

# 2. Follow interactive prompts
# 3. Choose a strong master password
\`\`\`

### Daily Usage
\`\`\`bash
# Load credentials and start bot
node load-credentials.js
\`\`\`

### Credential Management
\`\`\`bash
# List stored credentials (masked)
node -e "const cm = new (require('./credential-manager'))(); cm.listCredentials('your-master-password')"

# Remove stored credentials
node -e "const cm = new (require('./credential-manager'))(); cm.removeCredentials()"

# Create backup
node -e "const cm = new (require('./credential-manager'))(); cm.createBackup('./backup.enc', 'your-master-password')"
\`\`\`

## Security Best Practices

### 1. Password Security
- Use a **strong master password** (12+ characters)
- Include **uppercase, lowercase, numbers, and symbols**
- **Don't reuse** passwords from other services
- Consider using a **password manager**

### 2. Token Management
- Use **fine-grained personal access tokens** when possible
- Set **minimum required scopes** only
- **Rotate tokens regularly** (every 90 days)
- **Monitor token usage** through GitHub settings

### 3. Environment Security
- **Never commit** .env files to version control
- Use **environment-specific** configurations
- **Restrict file permissions** on credential files
- **Regularly audit** access logs

### 4. Operational Security
- **Monitor bot activity** through generated logs
- **Review contributions** before they're made in production
- **Use dry-run mode** for testing
- **Keep dependencies updated**

## Security Monitoring

### Log Files
- \`logs/bot-secure-YYYY-MM-DD.log\` - Masked security logs
- \`logs/activity_log.json\` - Bot activity tracking
- \`contributions.json\` - Contribution history

### Security Alerts
The bot will warn you about:
- Invalid or expired tokens
- Missing required credentials  
- Suspicious activity patterns
- Failed authentication attempts

## Incident Response

### If Credentials are Compromised
1. **Immediately rotate** all affected tokens
2. **Remove stored credentials**: \`cm.removeCredentials()\`
3. **Review recent activity** in GitHub settings
4. **Update passwords** and re-run setup
5. **Check logs** for unauthorized access

### If Bot Behaves Unexpectedly  
1. **Stop the bot** immediately
2. **Review logs** for error patterns
3. **Check token permissions** on GitHub
4. **Validate environment** configuration
5. **Run in dry-run mode** before resuming

## Compliance Notes

### Data Protection
- Credentials are **encrypted at rest**
- **No plaintext storage** of sensitive data
- **Automatic masking** in all outputs
- **Secure deletion** of temporary files

### Access Control
- **File-level permissions** (600/700)
- **User-only access** to credential files
- **No network transmission** of raw credentials
- **Local storage only** for encrypted data

## Support

For security-related questions or incidents:
1. Check this guide first
2. Review the source code in \`security-config.js\`
3. Test in dry-run mode
4. Contact your security team if needed

Remember: **Security is a shared responsibility**. Always follow your organization's security policies in addition to these guidelines.
`;

  fs.writeFileSync('security-guide.md', securityGuide);
  console.log('✅ Created security-guide.md');
}

// Only run if called directly
if (require.main === module) {
  setupSecureCredentials();
}

module.exports = { setupSecureCredentials };

const CredentialManager = require('./credential-manager');
const TelegramSecurityManager = require('./telegram-security-config');

class TelegramCredentialManager extends CredentialManager {
  constructor() {
    super();
    this.credentialPath = require('path').join(require('os').homedir(), '.telegram-bot-credentials');
    this.telegramSecurity = new TelegramSecurityManager();
  }

  /**
   * Telegram bot specific credential setup
   */
  async setupTelegramCredentials() {
    const readline = require('readline');
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });

    return new Promise((resolve) => {
      console.log('\n🤖 Telegram Bot - Secure Credential Setup');
      console.log('==========================================');
      
      const credentials = {};
      
      // Get Telegram Bot Token
      rl.question('Enter your Telegram Bot Token (from @BotFather): ', (token) => {
        
        // Validate token format
        const validation = this.telegramSecurity.validateTelegramToken(token);
        if (!validation.valid) {
          console.log(`❌ ${validation.error}`);
          console.log('Please get a valid token from @BotFather on Telegram');
          rl.close();
          resolve({ success: false, error: validation.error });
          return;
        }
        
        console.log(`✅ Valid token for Bot ID: ${validation.botId}`);
        credentials.BOT_TOKEN = token;
        credentials.TELEGRAM_BOT_TOKEN = token; // Backup key name
        
        // Get Chat ID (optional)
        rl.question('Enter default Chat ID (optional, press enter to skip): ', (chatId) => {
          if (chatId.trim()) {
            const chatValidation = this.telegramSecurity.validateChatId(chatId.trim());
            if (chatValidation.valid) {
              credentials.CHAT_ID = chatId.trim();
              console.log(`✅ Chat ID validated: ${chatValidation.type}`);
            } else {
              console.log(`⚠️  Warning: ${chatValidation.error}`);
            }
          }
          
          // Get Admin User ID (optional)
          rl.question('Enter Admin User ID (optional, press enter to skip): ', (adminId) => {
            if (adminId.trim()) {
              credentials.ADMIN_USER_ID = adminId.trim();
            }
            
            // Get Webhook URL (optional)
            rl.question('Enter Webhook URL (optional, press enter to skip): ', (webhookUrl) => {
              if (webhookUrl.trim()) {
                if (webhookUrl.startsWith('https://')) {
                  credentials.WEBHOOK_URL = webhookUrl.trim();
                  console.log('✅ Webhook URL added');
                } else {
                  console.log('⚠️  Warning: Webhook URL should use HTTPS');
                  credentials.WEBHOOK_URL = webhookUrl.trim();
                }
              }
              
              // Get API Base URL (optional, for custom Telegram servers)
              rl.question('Enter custom API Base URL (optional, press enter for default): ', (apiBase) => {
                if (apiBase.trim()) {
                  credentials.API_BASE_URL = apiBase.trim();
                }
                
                // Get master password
                rl.question('Enter master password for encryption: ', (password) => {
                  rl.close();
                  
                  console.log('\n🔐 Encrypting and storing credentials...');
                  this.storeCredentials(credentials, password).then((result) => {
                    if (result.success) {
                      console.log('\n✅ Telegram bot credentials stored securely!');
                      console.log('\n📋 Credential Summary:');
                      console.log(`   🤖 Bot Token: ${validation.botId}:***********`);
                      if (credentials.CHAT_ID) console.log(`   💬 Chat ID: ${credentials.CHAT_ID}`);
                      if (credentials.ADMIN_USER_ID) console.log(`   👤 Admin ID: ${credentials.ADMIN_USER_ID}`);
                      if (credentials.WEBHOOK_URL) console.log(`   🔗 Webhook: ${credentials.WEBHOOK_URL.substring(0, 30)}...`);
                      
                      resolve({ success: true, credentials, botId: validation.botId });
                    } else {
                      resolve({ success: false, error: result.error });
                    }
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
   * Load and validate Telegram credentials
   */
  async loadTelegramCredentials(masterPassword) {
    const result = await this.retrieveCredentials(masterPassword);
    
    if (result.success) {
      // Validate loaded credentials
      const token = result.credentials.BOT_TOKEN || result.credentials.TELEGRAM_BOT_TOKEN;
      
      if (token) {
        const validation = this.telegramSecurity.validateTelegramToken(token);
        if (validation.valid) {
          console.log(`✅ Telegram bot credentials loaded for Bot ID: ${validation.botId}`);
          
          // Set environment variables
          Object.entries(result.credentials).forEach(([key, value]) => {
            process.env[key] = value;
          });
          
          return { 
            success: true, 
            credentials: result.credentials,
            botId: validation.botId
          };
        } else {
          return { 
            success: false, 
            error: `Invalid stored token: ${validation.error}` 
          };
        }
      } else {
        return { 
          success: false, 
          error: 'No bot token found in stored credentials' 
        };
      }
    } else {
      return result;
    }
  }

  /**
   * Test bot connectivity with stored credentials
   */
  async testBotConnection(masterPassword) {
    console.log('🧪 Testing bot connection...');
    
    const loadResult = await this.loadTelegramCredentials(masterPassword);
    if (!loadResult.success) {
      return { success: false, error: loadResult.error };
    }
    
    const token = process.env.BOT_TOKEN || process.env.TELEGRAM_BOT_TOKEN;
    const permissionCheck = await this.telegramSecurity.checkTelegramTokenPermissions(token);
    
    if (permissionCheck.valid) {
      const bot = permissionCheck.botInfo;
      console.log(`✅ Connection successful!`);
      console.log(`   🤖 Bot: @${bot.username} (${bot.firstName})`);
      console.log(`   🆔 ID: ${bot.id}`);
      console.log(`   🔹 Groups: ${bot.canJoinGroups ? 'Yes' : 'No'}`);
      console.log(`   🔹 Group Messages: ${bot.canReadAllGroupMessages ? 'Yes' : 'No'}`);
      console.log(`   🔹 Inline Queries: ${bot.supportsInlineQueries ? 'Yes' : 'No'}`);
      
      return { success: true, botInfo: bot };
    } else {
      return { 
        success: false, 
        error: `Connection failed: ${permissionCheck.error}` 
      };
    }
  }

  /**
   * Create secure bot loader script
   */
  createBotLoader() {
    const loaderScript = `#!/usr/bin/env node

const TelegramCredentialManager = require('./telegram-credential-manager');
const TelegramSecurityManager = require('./telegram-security-config');

async function startSecureBot() {
  const credentialManager = new TelegramCredentialManager();
  const security = new TelegramSecurityManager();
  
  try {
    console.log('🔑 Loading encrypted Telegram bot credentials...');
    
    const readline = require('readline');
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
    
    const password = await new Promise((resolve) => {
      rl.question('Enter master password: ', resolve);
    });
    rl.close();
    
    const result = await credentialManager.loadTelegramCredentials(password);
    
    if (result.success) {
      console.log('✅ Credentials loaded successfully!');
      
      // Initialize bot with enhanced security
      const initResult = await security.initializeTelegramBot();
      
      if (initResult.initialized) {
        console.log('🚀 Starting Telegram bot with enterprise security...');
        
        // Start your bot here
        require('./telegram-docker-bot/bot.js'); // Adjust path as needed
      }
    } else {
      console.error('❌ Failed to load credentials:', result.error);
      process.exit(1);
    }
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

// Only run if called directly
if (require.main === module) {
  startSecureBot();
}

module.exports = { startSecureBot };
`;

    require('fs').writeFileSync('load-telegram-bot.js', loaderScript);
    console.log('✅ Created load-telegram-bot.js');
    
    return 'load-telegram-bot.js';
  }

  /**
   * Generate secure environment template
   */
  generateSecureEnvTemplate() {
    const template = `# 🔐 SECURE TELEGRAM BOT CONFIGURATION
# This file is for reference only. Use 'node setup-secure.js' for actual setup.

# === TELEGRAM BOT CREDENTIALS ===
# DO NOT store real tokens here! Use encrypted storage instead.
BOT_TOKEN=your-bot-token-from-botfather-use-secure-setup
TELEGRAM_BOT_TOKEN=your-bot-token-backup-key

# === OPTIONAL CONFIGURATION ===
CHAT_ID=your-default-chat-id
ADMIN_USER_ID=your-admin-user-id
WEBHOOK_URL=https://your-domain.com/webhook

# === API CONFIGURATION ===
API_BASE_URL=https://api.telegram.org  # Default Telegram API
MAX_CONNECTIONS=40                      # Webhook connections
TIMEOUT=10000                          # Request timeout (ms)

# === SECURITY SETTINGS ===
SECURITY_LOG_LEVEL=info
ENCRYPT_LOGS=true
METRICS_ENABLED=true
RATE_LIMIT_ENABLED=true

# === BOT BEHAVIOR ===
BOT_NAME=MySecureBot
BOT_DESCRIPTION=Securely configured Telegram bot
AUTO_RETRY=true
MAX_RETRIES=3

# ======================================
# 🔐 SECURE CREDENTIAL SETUP INSTRUCTIONS
# ======================================
# 
# For maximum security, use the encrypted credential manager:
# 1. Run: node setup-secure.js
# 2. Enter your bot token from @BotFather
# 3. Configure optional settings
# 4. Use: node load-telegram-bot.js to start bot securely
#
# This encrypts your tokens with AES-256-GCM encryption
# and protects them from accidental exposure.
# ======================================
`;

    require('fs').writeFileSync('.env.telegram.example', template);
    console.log('✅ Created .env.telegram.example');
    
    return '.env.telegram.example';
  }
}

module.exports = TelegramCredentialManager;

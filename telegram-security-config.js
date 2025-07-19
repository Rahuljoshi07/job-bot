const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const SecurityManager = require('./security-config');

class TelegramSecurityManager extends SecurityManager {
  constructor() {
    super();
    this.requiredSecrets = ['BOT_TOKEN', 'TELEGRAM_BOT_TOKEN'];
    this.optionalSecrets = ['CHAT_ID', 'ADMIN_USER_ID', 'WEBHOOK_URL', 'API_BASE_URL'];
    
    // Enhanced patterns for Telegram-specific tokens
    this.sensitivePatterns = [
      ...this.sensitivePatterns,
      /\d{8,10}:[A-Za-z0-9_-]{35}/, // Telegram bot token pattern
      /chat_id=[-\d]+/, // Chat ID patterns
      /user_id=\d+/, // User ID patterns
      /webhook.*[A-Za-z0-9_-]{20,}/, // Webhook URLs with tokens
    ];
    
    // Telegram-specific rate limits
    this.rateLimits = {
      messagesPerSecond: 30,
      messagesPerMinute: 20,
      messagesPerChat: 1,
      bulkMessagesPerHour: 100,
      apiCallsPerSecond: 30
    };
    
    this.botMetrics = {
      messagesSent: 0,
      errorsEncountered: 0,
      apiCallsToday: 0,
      lastActivity: null,
      uptime: Date.now()
    };
  }

  /**
   * Validate Telegram bot token format
   */
  validateTelegramToken(token) {
    if (!token) return { valid: false, error: 'Token is required' };
    
    // Telegram bot token format: XXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    const tokenPattern = /^\d{8,10}:[A-Za-z0-9_-]{35}$/;
    
    if (!tokenPattern.test(token)) {
      return {
        valid: false,
        error: 'Invalid Telegram bot token format. Expected: XXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
      };
    }
    
    // Extract bot ID from token
    const botId = token.split(':')[0];
    
    return {
      valid: true,
      botId: botId,
      tokenLength: token.length,
      format: 'valid'
    };
  }

  /**
   * Validate chat ID format
   */
  validateChatId(chatId) {
    if (!chatId) return { valid: true, warning: 'Chat ID not provided' };
    
    // Chat IDs can be positive (groups/channels) or negative (users)
    const chatIdPattern = /^-?\d+$/;
    
    return {
      valid: chatIdPattern.test(chatId),
      type: chatId.startsWith('-') ? 'group/channel' : 'user',
      error: chatIdPattern.test(chatId) ? null : 'Invalid chat ID format'
    };
  }

  /**
   * Enhanced token validation for Telegram
   */
  async checkTelegramTokenPermissions(token) {
    try {
      const axios = require('axios');
      const response = await axios.get(`https://api.telegram.org/bot${token}/getMe`, {
        timeout: 10000
      });

      if (response.data.ok) {
        return {
          valid: true,
          botInfo: {
            id: response.data.result.id,
            username: response.data.result.username,
            firstName: response.data.result.first_name,
            canJoinGroups: response.data.result.can_join_groups,
            canReadAllGroupMessages: response.data.result.can_read_all_group_messages,
            supportsInlineQueries: response.data.result.supports_inline_queries
          }
        };
      }
      
      return {
        valid: false,
        error: 'Bot token validation failed',
        details: response.data
      };
    } catch (error) {
      return {
        valid: false,
        error: 'Unable to validate bot token',
        details: this.maskSensitiveData(error.message)
      };
    }
  }

  /**
   * Rate limiting for Telegram API calls
   */
  async enforceRateLimit(operation = 'api_call') {
    const now = Date.now();
    const currentSecond = Math.floor(now / 1000);
    
    if (!this.rateLimitTracker) {
      this.rateLimitTracker = {
        lastSecond: currentSecond,
        callsThisSecond: 0,
        callsThisMinute: 0,
        callsThisHour: 0,
        minuteTracker: {},
        hourTracker: {}
      };
    }
    
    const tracker = this.rateLimitTracker;
    
    // Reset second counter
    if (tracker.lastSecond !== currentSecond) {
      tracker.callsThisSecond = 0;
      tracker.lastSecond = currentSecond;
    }
    
    // Check rate limits
    if (tracker.callsThisSecond >= this.rateLimits.apiCallsPerSecond) {
      const waitTime = 1000 - (now % 1000);
      this.secureLog('warn', `Rate limit hit for ${operation}, waiting ${waitTime}ms`);
      await new Promise(resolve => setTimeout(resolve, waitTime));
    }
    
    // Increment counters
    tracker.callsThisSecond++;
    this.botMetrics.apiCallsToday++;
    
    return { allowed: true, remaining: this.rateLimits.apiCallsPerSecond - tracker.callsThisSecond };
  }

  /**
   * Secure bot initialization
   */
  async initializeTelegramBot() {
    console.log('🤖 Initializing Telegram Bot with Enhanced Security...');
    
    try {
      // 1. Initialize base security
      await this.initializeSecurity();
      
      // 2. Validate Telegram token
      const token = process.env.BOT_TOKEN || process.env.TELEGRAM_BOT_TOKEN;
      if (!token) {
        throw new Error('Telegram bot token not found. Please run: node setup-secure.js');
      }
      
      const tokenValidation = this.validateTelegramToken(token);
      if (!tokenValidation.valid) {
        throw new Error(`Invalid token: ${tokenValidation.error}`);
      }
      
      console.log(`✅ Token format valid for Bot ID: ${tokenValidation.botId}`);
      
      // 3. Check bot permissions
      const permissionCheck = await this.checkTelegramTokenPermissions(token);
      if (permissionCheck.valid) {
        const bot = permissionCheck.botInfo;
        console.log(`✅ Bot authenticated: @${bot.username} (${bot.firstName})`);
        console.log(`   🔹 Can join groups: ${bot.canJoinGroups}`);
        console.log(`   🔹 Can read group messages: ${bot.canReadAllGroupMessages}`);
        console.log(`   🔹 Supports inline queries: ${bot.supportsInlineQueries}`);
      } else {
        this.secureLog('error', 'Bot token validation failed', permissionCheck);
        throw new Error(`Token validation failed: ${permissionCheck.error}`);
      }
      
      // 4. Validate optional configurations
      const chatId = process.env.CHAT_ID;
      if (chatId) {
        const chatValidation = this.validateChatId(chatId);
        if (chatValidation.valid) {
          console.log(`✅ Chat ID validated: ${chatValidation.type}`);
        } else {
          console.warn(`⚠️  Chat ID warning: ${chatValidation.error}`);
        }
      }
      
      // 5. Setup monitoring and metrics
      this.setupMetricsCollection();
      
      this.secureLog('info', 'Telegram bot security initialization completed successfully');
      return { 
        initialized: true, 
        botInfo: permissionCheck.botInfo,
        securityLevel: 'enterprise'
      };
      
    } catch (error) {
      this.secureLog('error', 'Telegram bot security initialization failed', { error: error.message });
      throw error;
    }
  }

  /**
   * Setup metrics collection and monitoring
   */
  setupMetricsCollection() {
    // Create metrics directory
    const metricsDir = path.join(__dirname, 'metrics');
    if (!fs.existsSync(metricsDir)) {
      fs.mkdirSync(metricsDir, { mode: 0o700 });
    }
    
    // Setup periodic metrics saving
    this.metricsInterval = setInterval(() => {
      this.saveMetrics();
    }, 60000); // Save metrics every minute
    
    console.log('📊 Bot metrics collection initialized');
  }

  /**
   * Save bot metrics securely
   */
  saveMetrics() {
    const metricsFile = path.join(__dirname, 'metrics', `bot-metrics-${new Date().toISOString().split('T')[0]}.json`);
    const metrics = {
      timestamp: new Date().toISOString(),
      messagesSent: this.botMetrics.messagesSent,
      errorsEncountered: this.botMetrics.errorsEncountered,
      apiCallsToday: this.botMetrics.apiCallsToday,
      uptime: Date.now() - this.botMetrics.uptime,
      lastActivity: this.botMetrics.lastActivity
    };
    
    try {
      fs.writeFileSync(metricsFile, JSON.stringify(metrics, null, 2), { mode: 0o600 });
    } catch (error) {
      this.secureLog('error', 'Failed to save metrics', { error: error.message });
    }
  }

  /**
   * Secure message logging
   */
  logBotActivity(activity, details = {}) {
    const maskedDetails = this.maskSensitiveData(JSON.stringify(details));
    this.secureLog('info', `Bot Activity: ${activity}`, { details: maskedDetails });
    
    // Update metrics
    this.botMetrics.lastActivity = new Date().toISOString();
    if (activity === 'message_sent') this.botMetrics.messagesSent++;
    if (activity === 'error') this.botMetrics.errorsEncountered++;
  }

  /**
   * Secure webhook setup
   */
  async setupSecureWebhook(url) {
    if (!url) return { setup: false, reason: 'No webhook URL provided' };
    
    try {
      await this.enforceRateLimit('webhook_setup');
      
      // Validate webhook URL
      if (!url.startsWith('https://')) {
        throw new Error('Webhook URL must use HTTPS');
      }
      
      const axios = require('axios');
      const token = process.env.BOT_TOKEN || process.env.TELEGRAM_BOT_TOKEN;
      
      const response = await axios.post(`https://api.telegram.org/bot${token}/setWebhook`, {
        url: url,
        max_connections: 40,
        allowed_updates: ['message', 'callback_query', 'inline_query']
      });
      
      if (response.data.ok) {
        this.secureLog('info', 'Webhook setup successful', { url: this.maskSensitiveData(url) });
        return { setup: true, url: url };
      } else {
        throw new Error(`Webhook setup failed: ${response.data.description}`);
      }
    } catch (error) {
      this.secureLog('error', 'Webhook setup failed', { error: error.message });
      return { setup: false, error: error.message };
    }
  }

  /**
   * Enhanced environment validation for Telegram bots
   */
  validateTelegramEnvironment() {
    const validation = this.validateEnvironment();
    const telegramSpecific = {
      botToken: !!process.env.BOT_TOKEN || !!process.env.TELEGRAM_BOT_TOKEN,
      chatId: !!process.env.CHAT_ID,
      webhookUrl: !!process.env.WEBHOOK_URL,
      adminUserId: !!process.env.ADMIN_USER_ID
    };
    
    return {
      ...validation,
      telegram: telegramSpecific,
      ready: telegramSpecific.botToken
    };
  }
}

module.exports = TelegramSecurityManager;

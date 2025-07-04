# 🔒 Secure Setup Guide for Job Bot

## ⚠️ IMPORTANT SECURITY NOTICE

**NEVER** commit your actual credentials to the public repository. This guide shows you how to set up the bot securely.

## 🔐 GitHub Secrets Setup (Recommended for GitHub Actions)

1. Go to your GitHub repository: https://github.com/Rahuljoshi07/job-bot
2. Click on **Settings** tab
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret** for each of the following:

### Required Secrets:

**Personal Information:**
- `PERSONAL_FULL_NAME` → Your full name (e.g., "Rahul Joshi")
- `PERSONAL_EMAIL` → Your email address
- `PERSONAL_PHONE` → Your phone number (e.g., "+1234567890")
- `PERSONAL_LINKEDIN` → Your LinkedIn profile URL
- `PERSONAL_GITHUB` → Your GitHub profile URL
- `PERSONAL_LOCATION` → Your location (e.g., "Remote" or "New York, NY")

**Platform Credentials:**
- `TWITTER_EMAIL` → Your Twitter/X account email
- `TWITTER_PASSWORD` → Your Twitter/X account password
- `TURING_EMAIL` → Your Turing.com account email
- `TURING_PASSWORD` → Your Turing.com account password
- `INDEED_EMAIL` → Your Indeed account email
- `INDEED_PASSWORD` → Your Indeed account password
- `DICE_EMAIL` → Your Dice account email
- `DICE_PASSWORD` → Your Dice account password

**Optional Platform Credentials:**
- `WEWORKREMOTELY_EMAIL` → WeWorkRemotely account email
- `WEWORKREMOTELY_PASSWORD` → WeWorkRemotely account password
- `FLEXJOBS_EMAIL` → FlexJobs account email
- `FLEXJOBS_PASSWORD` → FlexJobs account password
- `REMOTEOK_EMAIL` → RemoteOK account email
- `REMOTEOK_PASSWORD` → RemoteOK account password

## 🏠 Local Development Setup

For local testing, create a `.env` file in your project directory:

```bash
# Copy the example file
cp .env.example .env

# Edit with your actual credentials
notepad .env  # Windows
nano .env     # Linux/Mac
```

**Example .env content:**
```
PERSONAL_FULL_NAME=Your Full Name
PERSONAL_EMAIL=your.email@example.com
PERSONAL_PHONE=+1234567890
PERSONAL_LINKEDIN=https://linkedin.com/in/yourprofile
PERSONAL_GITHUB=https://github.com/yourusername
PERSONAL_LOCATION=Your City, Country

TWITTER_EMAIL=your.twitter@email.com
TWITTER_PASSWORD=your_twitter_password
TURING_EMAIL=your.turing@email.com
TURING_PASSWORD=your_turing_password
INDEED_EMAIL=your.indeed@email.com
INDEED_PASSWORD=your_indeed_password
DICE_EMAIL=your.dice@email.com
DICE_PASSWORD=your_dice_password
```

## 🛡️ Security Best Practices

1. **Never commit .env files** - They're already in .gitignore
2. **Use strong, unique passwords** for each platform
3. **Enable 2FA** where possible (you may need app passwords)
4. **Regularly rotate passwords** especially if the bot stops working
5. **Monitor your accounts** for unusual activity
6. **Use different emails** for job platforms if possible

## 🔍 Verification

After setting up secrets, check the GitHub Actions logs for:
- ✅ All environment variables are loaded
- ✅ Configuration validation passes
- ✅ No credential-related errors

## 🚨 If Credentials are Compromised

1. **Immediately change passwords** on affected platforms
2. **Update GitHub Secrets** with new credentials
3. **Check account activity** on all platforms
4. **Enable additional security measures** (2FA, etc.)

## 📞 Support

If you need help with setup:
1. Check the diagnostics output in GitHub Actions
2. Ensure all required secrets are set
3. Verify credentials work by logging in manually first

**Remember: Your security is paramount. Never share or commit actual credentials!**

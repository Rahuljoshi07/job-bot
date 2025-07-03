# 🤖 Automated Job Application Bot

A 24/7 automated job bot that searches and applies to relevant jobs based on your resume and preferences.

## ✨ Features

- **Resume Analysis**: Automatically extracts skills and contact info from your CV
- **Multi-Platform Search**: Searches RemoteOK, LinkedIn, Indeed, DICE, and more
- **Smart Matching**: Matches jobs based on your skills and preferences  
- **Auto Application**: Automatically applies to suitable jobs
- **24/7 Monitoring**: Continuous job monitoring and application
- **Global Search**: Searches worldwide including remote positions
- **Scam Detection**: Avoids suspicious or paid job postings

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Your Profile
```bash
python setup.py
```
This will ask for:
- Personal information (name, email, phone, etc.)
- Job platform credentials (LinkedIn, Indeed, DICE)
- Resume file path
- Job preferences

### 3. Run the Bot

**One-time test run:**
```bash
python job_bot_with_login.py
```

**24/7 continuous monitoring (FIXED VERSION):**
```bash
python start_fixed_bot.py
```

**Single test run (FIXED VERSION):**
```bash
python job_bot_fixed.py
```

## 📁 Files Structure

- `job_bot.py` - Basic bot without login (for testing)
- `job_bot_with_login.py` - Full bot with platform login capabilities
- `config.py` - Configuration and credentials management
- `resume_analyzer.py` - Resume parsing and skill extraction
- `setup.py` - Interactive setup script
- `applications.txt` - Log of job applications
- `user_config.json` - Your saved configuration

## 🔧 Configuration

Your credentials are stored in `user_config.json`. The bot supports:

### Job Platforms
- **X/Twitter Jobs** - Full login and job search
- **RemoteOK** - API-based search (WORKING)
- **Indeed** - Login and apply
- **DICE** - Simulated search (WORKING)

### Job Preferences
- Preferred job titles
- Skills matching
- Salary requirements
- Remote vs on-site
- Experience level

## 📋 Current Setup

✅ **Personal Info**: Rahul Joshi (rahuljoshisg@gmail.com)  
✅ **Resume**: DevOps Resume loaded with 16 skills detected  
✅ **Skills Found**: Python, AWS, Docker, Kubernetes, Jenkins, CI/CD, DevOps, Linux, etc.  
✅ **Platforms**: X/Twitter, RemoteOK, DICE configured
✅ **Preferences**: Entry/Mid level DevOps positions  

## 🛡️ Security

- Credentials are stored locally in encrypted JSON
- Browser automation uses secure session management
- No credentials are logged or transmitted

## ⚡ Usage Tips

1. **Test First**: Run `job_bot_with_login.py` once to ensure everything works
2. **Monitor Logs**: Check `applications.txt` for application history
3. **Rate Limiting**: Bot includes delays to avoid being blocked
4. **Manual Review**: Some applications may require manual completion

## 🚨 Important Notes

- **LinkedIn**: May require manual CAPTCHA solving occasionally
- **Rate Limits**: Bot respects platform rate limits
- **Resume**: Keep your resume updated in the job-bot folder
- **Monitoring**: Bot runs every 2 hours to avoid detection

## 🎯 Job Matching

The bot matches jobs based on:
- Skills from your resume
- Preferred job titles
- Experience level
- Location preferences
- Salary requirements

## 📊 Statistics

The bot logs all activities and provides:
- Number of jobs found
- Applications submitted
- Success/failure rates
- Platform-wise statistics

## 🛠️ Troubleshooting

**Browser Issues**: Make sure Chrome is installed  
**Login Failures**: Check credentials in `user_config.json`  
**Resume Not Found**: Verify resume.pdf exists in job-bot folder  
**No Jobs Found**: Check if your skills match available positions  

---

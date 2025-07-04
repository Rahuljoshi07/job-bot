# GitHub Actions Job Bot Troubleshooting Guide

## Overview
This guide helps troubleshoot common issues with the automated job application bot running in GitHub Actions.

## Common Issues & Solutions

### 1. Environment Variables Not Set (❌ PERSONAL_FULL_NAME: NOT SET)

**Problem**: Secrets are not being passed to the workflow properly.

**Solution**:
1. **Verify GitHub Secrets**: Go to your repository → Settings → Secrets and variables → Actions
2. **Check Secret Names**: Ensure they match exactly (case-sensitive):
   - `PERSONAL_FULL_NAME`
   - `PERSONAL_EMAIL`
   - `PERSONAL_PHONE`
   - `TWITTER_EMAIL`
   - `TWITTER_PASSWORD`
   - `TURING_EMAIL`
   - `TURING_PASSWORD`
   - etc.

3. **Verify Secret Values**: Make sure secrets have actual values, not empty strings

4. **Check Workflow**: The updated workflow now passes secrets as environment variables directly to each step

### 2. Python Module Import Errors (❌ beautifulsoup4: MISSING)

**Problem**: Required Python packages are not installed or imported correctly.

**Solutions**:
1. **Check requirements.txt**: Ensure all required packages are listed:
   ```
   beautifulsoup4==4.12.2
   python-dotenv==1.0.0
   selenium==4.15.0
   # ... other packages
   ```

2. **Module Name Issues**: Some packages have different import names:
   - `python-dotenv` → import as `dotenv`
   - `beautifulsoup4` → import as `bs4`

3. **Installation Issues**: The workflow installs packages with:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Testing Your Setup

**Run Local Tests**:
```bash
# Test secrets and modules
python test_secrets.py

# Run full diagnostics
python diagnose.py
```

**In GitHub Actions**:
The workflow now includes a "Test secrets access" step that runs before the main bot.

### 4. GitHub Actions Workflow Structure

The updated workflow follows this order:
1. **Setup**: Install Python, Firefox, dependencies
2. **Environment**: Create .env file and verify it
3. **Test**: Run test_secrets.py to verify setup
4. **Diagnose**: Run diagnose.py for comprehensive checks
5. **Execute**: Run the actual bot

### 5. Secret Management Best Practices

1. **Never Commit Secrets**: Keep `.env` in `.gitignore`
2. **Use Repository Secrets**: Store all credentials in GitHub → Settings → Secrets
3. **Test Locally**: Use a local `.env` file for development
4. **Verify Access**: Use the test scripts to verify secrets are accessible

### 6. Debugging Steps

If the bot still fails:

1. **Check Workflow Logs**: Go to Actions tab → Latest run → Check each step's logs
2. **Look for Error Messages**: Focus on the "Test secrets access" and "Run diagnostics" steps
3. **Verify Secret Names**: Ensure GitHub secret names match exactly what the code expects
4. **Check Secret Values**: Make sure secrets aren't empty or malformed

### 7. Environment Variable Approach

The updated workflow uses two approaches:
1. **Create .env file**: For compatibility with existing code
2. **Pass as env vars**: Direct environment variable passing to each step

Both methods ensure your secrets are available to the bot.

### 8. Quick Fix Checklist

- [ ] All secrets set in GitHub repository settings
- [ ] Secret names match exactly (case-sensitive)
- [ ] requirements.txt contains all needed packages
- [ ] Local test passes: `python test_secrets.py`
- [ ] Workflow has been updated with the new environment variable passing
- [ ] No empty or malformed secret values

### 9. Manual Testing

You can manually trigger the workflow to test:
1. Go to Actions tab in your repository
2. Click "24/7 Automated Job Bot"
3. Click "Run workflow"
4. Monitor the logs for any issues

## Contact & Support

If issues persist after following this guide:
1. Check the workflow logs carefully
2. Ensure all secrets are properly set
3. Run local tests to verify your setup
4. Review the error messages in the diagnostic steps

The updated workflow should resolve the original issues with secrets not being accessible and Python module import problems.

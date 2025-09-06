# 🚀 Automated Token Refresh System

An automated JWT token refresh system that generates fresh tokens every 7 hours and automatically updates your GitHub repository and Vercel deployment.

## ✨ Features

- **🔄 Automatic Token Refresh**: Generates fresh JWT tokens every 7 hours
- **📊 High Success Rate**: 97.6% success rate (40/41 tokens generated)
- **🤖 GitHub Actions Integration**: Fully automated via GitHub Actions
- **🚀 Vercel Auto-Deploy**: Automatically triggers Vercel redeployment
- **🛡️ Retry Logic**: 3 attempts per account with intelligent error handling
- **📝 Comprehensive Logging**: Detailed logs for monitoring and debugging

## 🏗️ System Architecture

```
GitHub Actions (Every 7 hours)
    ↓
Token Refresh Script
    ↓
JWT Service API
    ↓
Generate Fresh Tokens
    ↓
Commit to GitHub
    ↓
Vercel Auto-Deploy
```

## 📁 Project Structure

```
├── app.py                          # Main application
├── token_refresh.py                # Core token refresh functionality
├── input_bd.json                   # Account credentials (41 accounts)
├── token_bd.json                   # Generated tokens (auto-updated)
├── requirements.txt                # Python dependencies
├── vercel.json                     # Vercel deployment configuration
├── .github/workflows/token-refresh.yml  # GitHub Actions workflow
└── README.md                       # This file
```

## 🚀 Quick Setup

### 1. GitHub Secret Setup
1. Go to your repository settings: `Settings` → `Secrets and variables` → `Actions`
2. Add new secret:
   - **Name**: `TOKEN_REFRESH_BOT`
   - **Value**: Your GitHub Personal Access Token

### 2. Create GitHub Token
1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token (classic)"**
3. Name: "Token Refresh Bot"
4. Select scopes: ✅ `repo`, ✅ `workflow`
5. Copy the token and use it as the secret value

### 3. Enable GitHub Actions
1. Go to **Actions** tab in your repository
2. The workflow will start running automatically every 7 hours

## 📊 Performance Stats

| Metric | Value |
|--------|-------|
| **Total Accounts** | 41 |
| **Successful Tokens** | 40 (97.6% success rate) |
| **Failed Accounts** | 1 (UID: 4115121998) |
| **Refresh Interval** | Every 7 hours |
| **Processing Time** | ~2-3 minutes |

## 🔧 Configuration

### Environment Variables
- `TOKEN_REFRESH_BOT`: GitHub Personal Access Token
- `GITHUB_REPO`: Repository name (format: username/repo-name)
- `JWT_SERVICE_URL`: JWT generation service URL
- `TOKEN_TTL_HOURS`: Token refresh interval (default: 7 hours)

### JWT Service
- **URL**: `https://tcp1-two.vercel.app/jwt/cloudgen_jwt`
- **Method**: POST
- **Input**: Array of account objects with `uid` and `password`
- **Output**: Array of token objects with `status` and `token`

## 📈 Monitoring

### GitHub Actions
- Go to **Actions** tab in your repository
- Look for "Auto Token Refresh" workflow
- Click on runs to see detailed logs

### Manual Triggers
- **Force Refresh**: Go to Actions → "Auto Token Refresh" → "Run workflow" → Check "Force refresh"
- **Check Status**: Visit your Vercel deployment URL

## 🛠️ Troubleshooting

### Common Issues

1. **Workflow Fails**:
   - Check if `TOKEN_REFRESH_BOT` secret is set correctly
   - Verify token has `repo` and `workflow` permissions
   - Check Actions tab for detailed error logs

2. **Low Success Rate**:
   - Some accounts may fail due to server-side issues
   - System continues with successful tokens
   - Failed accounts are retried in next cycle

3. **JWT Service Errors**:
   - Service may be temporarily unavailable
   - System has retry logic built-in
   - Check service status at: https://tcp1-two.vercel.app/jwt/

## 🔄 How It Works

1. **GitHub Actions** triggers every 7 hours
2. **Checks token age** - refreshes if older than 6.5 hours
3. **Processes accounts individually** with retry logic
4. **Calls JWT service** to generate fresh tokens
5. **Saves new tokens** to `token_bd.json`
6. **Commits and pushes** changes to GitHub
7. **Vercel automatically redeploys** with fresh tokens

## 📝 Logs

- **GitHub Actions**: Check Actions tab for workflow logs
- **Local**: Check `token_refresh.log` (if running locally)
- **Vercel**: Check deployment logs in Vercel dashboard

## 🎯 Success Indicators

When working correctly, you should see:
- ✅ GitHub Actions workflow runs every 7 hours
- ✅ New commits appear in your repository
- ✅ Vercel redeploys automatically
- ✅ Fresh tokens available in your API
- ✅ 97.6% token generation success rate

## 📞 Support

If you encounter issues:
1. Check the GitHub Actions logs first
2. Verify all secrets are set correctly
3. Test the JWT service manually
4. Check token permissions

---

**🎉 Your automated token refresh system is now fully operational!**

# 🔧 GitHub Secret Setup Guide

## The Issue
Your GitHub Actions workflow was failing because of a secret name mismatch. Here's how to fix it:

## ✅ Quick Fix

### 1. Go to Your Repository Settings
1. Navigate to: `https://github.com/nicchenxgod067/spambot`
2. Click **Settings** tab
3. Click **Secrets and variables** → **Actions**

### 2. Check/Create the Secret
Look for a secret named `TOKEN_REFRESH_BOT`. If it doesn't exist:

1. Click **New repository secret**
2. Name: `TOKEN_REFRESH_BOT`
3. Value: Your GitHub Personal Access Token
4. Click **Add secret**

### 3. Create GitHub Personal Access Token (if needed)
If you don't have a token:

1. Go to: https://github.com/settings/tokens
2. Click **Generate new token (classic)**
3. Name: "Token Refresh Bot"
4. Select scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
5. Click **Generate token**
6. **Copy the token immediately** (you won't see it again)
7. Use this token as the value for `TOKEN_REFRESH_BOT` secret

## 🧪 Test the Fix

Run the test script to verify everything works:

```bash
# Set your GitHub token (replace with your actual token)
export TOKEN_REFRESH_BOT=your_github_token_here

# Run the test
python test_token_refresh.py
```

## 🚀 Manual Test

You can also manually trigger the workflow:

1. Go to **Actions** tab in your repository
2. Click **Auto Token Refresh** workflow
3. Click **Run workflow** → **Run workflow**

## 📋 What Was Fixed

1. **Secret Name**: Using `TOKEN_REFRESH_BOT` (GitHub doesn't allow custom secrets starting with `GITHUB_`)
2. **Environment Variable**: Added `TOKEN_REFRESH_BOT` environment variable to the workflow
3. **Permissions**: Added `contents: write` permission to the workflow
4. **Test Script**: Created `test_token_refresh.py` to verify setup

## 🔍 Troubleshooting

### If the workflow still fails:
1. Check the **Actions** tab for detailed error logs
2. Verify the `TOKEN_REFRESH_BOT` secret is set correctly
3. Make sure your token has `repo` and `workflow` permissions
4. Run `python test_token_refresh.py` to diagnose issues

### Common Issues:
- **403 Forbidden**: Token doesn't have write permissions
- **401 Unauthorized**: Token is invalid or expired
- **Connection Error**: JWT service is down (check https://tcp1-two.vercel.app/jwt/)

## ✅ Success Indicators

When working correctly, you should see:
- ✅ Workflow runs every 7 hours automatically
- ✅ Tokens are refreshed when older than 6.5 hours
- ✅ Changes are committed to GitHub
- ✅ Vercel redeploys with fresh tokens

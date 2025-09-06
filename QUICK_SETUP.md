# 🚀 Quick Setup Guide for Automated Token Refresh

## What This System Does
- **Automatically refreshes your JWT tokens every 7 hours**
- **Updates your GitHub repository with fresh tokens**
- **Vercel automatically redeploys with new tokens**
- **No manual intervention needed!**

## 📋 Setup Steps (5 minutes)

### 1. Push to GitHub
```bash
git add .
git commit -m "Add automated token refresh system"
git push origin main
```

### 2. Create GitHub Personal Access Token
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name: "Token Refresh Bot"
4. Select: `repo` (full control)
5. Click "Generate token"
6. **Copy the token** (you'll need it next)

### 3. Add GitHub Secret
1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `TOKEN_REFRESH_BOT`
5. Value: (paste the token from step 2)
6. Click **Add secret**

### 4. Enable GitHub Actions
1. Go to **Actions** tab in your repository
2. Click **I understand my workflows, go ahead and enable them**
3. The workflow will start running automatically!

## ✅ That's It!

The system will now:
- ✅ Run every 7 hours automatically
- ✅ Refresh tokens when they're older than 6.5 hours
- ✅ Commit changes to GitHub
- ✅ Vercel will redeploy with fresh tokens

## 🔍 How to Monitor

### Check GitHub Actions
- Go to **Actions** tab in your repository
- Look for "Auto Token Refresh" workflow
- Click on it to see logs

### Manual Refresh (if needed)
- Go to **Actions** → **Auto Token Refresh**
- Click **Run workflow** → **Run workflow**

### Check Token Age
- Visit: `https://spambot-api.vercel.app/health`
- Look for "tokens_loaded" count

## 🛠️ Troubleshooting

### If tokens don't refresh:
1. Check GitHub Actions logs
2. Verify `TOKEN_REFRESH_BOT` secret is set
3. Check if `input_bd.json` has valid data

### If GitHub push fails:
1. Verify token has `repo` permissions
2. Check repository name is correct

### If JWT service fails:
1. Check if `https://tcp1-two.vercel.app/jwt/` is accessible
2. Verify `input_bd.json` format is correct

## 📊 What Happens Next

1. **Every 7 hours**: GitHub Actions runs automatically
2. **Checks token age**: If older than 6.5 hours, refreshes
3. **Calls JWT service**: Gets fresh tokens from your input data
4. **Updates file**: Saves new tokens to `token_bd.json`
5. **Commits to GitHub**: Pushes changes automatically
6. **Vercel redeploys**: Your spam bot gets fresh tokens!

## 🎉 Success!

Your spam bot will now have fresh tokens every 7 hours without any manual work!

---

**Need help?** Check the logs in GitHub Actions or run `python test_automation.py` locally.

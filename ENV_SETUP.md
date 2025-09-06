# 🔧 Environment Variables Setup

## Create .env File

Since you renamed `.env.example` to `.env`, here's what you need to configure:

### 1. Create the .env file
```bash
# In your push_spam_repo directory, create a .env file with:
touch .env
# or on Windows:
echo. > .env
```

### 2. Add the following content to your .env file:

```env
# Token Refresh Bot Configuration
# GitHub Personal Access Token for automated token refresh
# Get this from: https://github.com/settings/tokens
# Required scopes: repo, workflow
TOKEN_REFRESH_BOT=your_github_token_here

# GitHub Repository (format: username/repo-name)
GITHUB_REPO=nicchenxgod067/spambot

# JWT Service URL
JWT_SERVICE_URL=https://tcp1-two.vercel.app/jwt/cloudgen_jwt

# Token refresh settings
TOKEN_TTL_HOURS=7
ENABLE_BACKGROUND_REFRESH=true

# Optional: Vercel deployment settings
# VERCEL_PROJECT_ID=your_vercel_project_id
# VERCEL_TOKEN=your_vercel_token
```

### 3. Replace the placeholder values:

- **`TOKEN_REFRESH_BOT`**: Your actual GitHub Personal Access Token
- **`GITHUB_REPO`**: Your repository (already set correctly)
- **`JWT_SERVICE_URL`**: Already set correctly
- **`TOKEN_TTL_HOURS`**: How often to refresh tokens (7 hours is good)

## 🔑 Getting Your GitHub Token

1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token (classic)"**
3. Name: "Token Refresh Bot"
4. Select scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
5. Click **"Generate token"**
6. **Copy the token immediately** (you won't see it again)
7. Replace `your_github_token_here` in your .env file

## 🧪 Test Your Setup

After creating the .env file with your token:

```bash
# Test the token refresh system
python test_token_refresh.py

# Or test manually
python token_refresh.py
```

## 🔒 Security Notes

- **Never commit .env files to Git** - they contain sensitive tokens
- The .env file should be in your `.gitignore`
- Only use the token for the specific repository
- Regenerate the token if you suspect it's compromised

## 📋 Example .env File

Here's what your .env file should look like (with your actual token):

```env
TOKEN_REFRESH_BOT=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GITHUB_REPO=nicchenxgod067/spambot
JWT_SERVICE_URL=https://tcp1-two.vercel.app/jwt/cloudgen_jwt
TOKEN_TTL_HOURS=7
ENABLE_BACKGROUND_REFRESH=true
```

## 🚀 Next Steps

1. Create the .env file with your GitHub token
2. Test locally with `python test_token_refresh.py`
3. Set up the `TOKEN_REFRESH_BOT` secret in GitHub repository settings
4. Test the GitHub Actions workflow manually

The automated token refresh should work once both the local .env file and GitHub secret are configured correctly!

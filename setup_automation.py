#!/usr/bin/env python3
"""
Setup script for automated token refresh system
This script helps configure the automated token refresh system
"""

import os
import json
import subprocess
import sys

def create_gitignore():
    """Create .gitignore file"""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment variables
.env
.env.local
.env.production

# Logs
*.log
token_refresh.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.temp
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    print("✅ Created .gitignore file")

def create_env_template():
    """Create environment variables template"""
    env_template = """# GitHub Configuration
GITHUB_TOKEN=your_github_token_here
GITHUB_REPO=your-username/your-repo-name

# Token Service Configuration
ENABLE_BACKGROUND_REFRESH=true
PORT=5001

# JWT Service URL (usually don't need to change)
JWT_SERVICE_URL=https://tcp1-two.vercel.app/jwt/cloudgen_jwt
"""
    
    with open('.env.template', 'w') as f:
        f.write(env_template)
    print("✅ Created .env.template file")

def create_readme():
    """Create comprehensive README"""
    readme_content = """# Automated Token Refresh System

This system automatically refreshes JWT tokens every 7 hours and updates your GitHub repository.

## 🚀 Quick Setup

### 1. GitHub Actions Setup (Recommended)

1. **Enable GitHub Actions** in your repository settings
2. **Set up secrets**:
   - Go to Settings → Secrets and variables → Actions
   - Add `GITHUB_TOKEN` with a Personal Access Token that has repo permissions

3. **The workflow will automatically run** every 7 hours

### 2. Manual Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r token_service_requirements.txt
   ```

2. **Set environment variables**:
   ```bash
   export GITHUB_TOKEN=your_github_token
   export GITHUB_REPO=your-username/your-repo-name
   ```

3. **Run the refresh script**:
   ```bash
   python token_refresh.py
   ```

### 3. Deploy Token Service (Optional)

Deploy the token service to Vercel for additional monitoring:

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Deploy**:
   ```bash
   vercel --prod
   ```

3. **Set environment variables** in Vercel dashboard

## 📁 File Structure

```
├── app.py                          # Main spam bot application
├── token_bd.json                   # Generated tokens (auto-updated)
├── input_bd.json                   # Input data for token generation
├── token_refresh.py                # Standalone refresh script
├── token_service.py                # Token refresh service
├── .github/workflows/token-refresh.yml  # GitHub Actions workflow
├── vercel.json                     # Vercel config for main app
├── vercel_token_service.json       # Vercel config for token service
└── requirements.txt                # Dependencies
```

## 🔧 Configuration

### Environment Variables

- `GITHUB_TOKEN`: GitHub Personal Access Token with repo permissions
- `GITHUB_REPO`: Your repository in format `username/repo-name`
- `ENABLE_BACKGROUND_REFRESH`: Enable background refresh (default: true)
- `JWT_SERVICE_URL`: JWT generation service URL

### GitHub Actions

The workflow runs every 7 hours and:
1. Checks if tokens need refresh
2. Calls the JWT service to generate new tokens
3. Commits and pushes changes to GitHub
4. Vercel automatically redeploys with new tokens

## 📊 Monitoring

### Health Checks

- **Main App**: `https://spambot-api.vercel.app/health`
- **Token Service**: `https://your-token-service.vercel.app/health`

### Manual Refresh

- **Via API**: `POST https://your-token-service.vercel.app/refresh`
- **Via GitHub**: Go to Actions → "Auto Token Refresh" → "Run workflow"

### Status Check

- **Token Status**: `GET https://your-token-service.vercel.app/status`

## 🛠️ Troubleshooting

### Common Issues

1. **Tokens not refreshing**:
   - Check GitHub Actions logs
   - Verify `GITHUB_TOKEN` has correct permissions
   - Check JWT service is accessible

2. **Git push fails**:
   - Verify `GITHUB_TOKEN` has write permissions
   - Check repository name format

3. **JWT service errors**:
   - Verify `input_bd.json` is valid
   - Check JWT service URL is accessible

### Logs

- **GitHub Actions**: Check Actions tab in your repository
- **Token Service**: Check Vercel function logs
- **Local**: Check `token_refresh.log`

## 🔄 How It Works

1. **GitHub Actions** triggers every 7 hours
2. **Checks token age** - refreshes if older than 6.5 hours
3. **Calls JWT service** with `input_bd.json` data
4. **Saves new tokens** to `token_bd.json`
5. **Commits and pushes** changes to GitHub
6. **Vercel redeploys** automatically with new tokens

## 📝 Manual Commands

```bash
# Check token age
python -c "import os, time; print(f'Age: {(time.time() - os.path.getmtime(\"token_bd.json\"))/3600:.1f} hours')"

# Force refresh
python token_refresh.py

# Start token service locally
python token_service.py

# Check GitHub Actions status
gh run list --workflow="Auto Token Refresh"
```

## 🆘 Support

If you encounter issues:
1. Check the logs first
2. Verify all environment variables are set
3. Test the JWT service manually
4. Check GitHub token permissions
"""
    
    with open('README_AUTOMATION.md', 'w') as f:
        f.write(readme_content)
    print("✅ Created README_AUTOMATION.md file")

def check_requirements():
    """Check if required files exist"""
    required_files = [
        'token_bd.json',
        'input_bd.json',
        'app.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files present")
    return True

def setup_git():
    """Initialize git repository if not already done"""
    try:
        # Check if git is initialized
        subprocess.run(['git', 'status'], check=True, capture_output=True)
        print("✅ Git repository already initialized")
    except subprocess.CalledProcessError:
        try:
            subprocess.run(['git', 'init'], check=True)
            subprocess.run(['git', 'add', '.'], check=True)
            subprocess.run(['git', 'commit', '-m', 'Initial commit with automation setup'], check=True)
            print("✅ Git repository initialized")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to initialize git: {e}")
            return False
    
    return True

def main():
    """Main setup function"""
    print("🚀 Setting up automated token refresh system...")
    
    # Check requirements
    if not check_requirements():
        print("❌ Setup failed: Missing required files")
        return
    
    # Create necessary files
    create_gitignore()
    create_env_template()
    create_readme()
    
    # Setup git
    if not setup_git():
        print("❌ Setup failed: Git initialization failed")
        return
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Set up your GitHub repository")
    print("2. Add GITHUB_TOKEN to repository secrets")
    print("3. Update GITHUB_REPO in .env.template")
    print("4. Push to GitHub to enable automated refresh")
    print("\n📖 See README_AUTOMATION.md for detailed instructions")

if __name__ == "__main__":
    main()

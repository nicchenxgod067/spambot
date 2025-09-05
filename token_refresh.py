#!/usr/bin/env python3
"""
Automated Token Refresh Script for Spam Bot
This script refreshes JWT tokens every 7 hours and commits changes to GitHub
"""

import json
import requests
import os
import time
import subprocess
import sys
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('token_refresh.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration
TOKENS_FILE = "token_bd.json"
INPUT_FILE = "input_bd.json"
JWT_SERVICE_URL = "https://tcp1-two.vercel.app/jwt/cloudgen_jwt"
TOKEN_TTL_SECONDS = 7 * 60 * 60  # 7 hours
GITHUB_REPO = "nicchenxgod067/spambot"  # Your actual repo
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')  # Set this as environment variable

def load_input_data():
    """Load input data for token generation"""
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load {INPUT_FILE}: {e}")
        return None

def refresh_tokens():
    """Refresh tokens using the JWT service"""
    try:
        input_data = load_input_data()
        if not input_data:
            raise RuntimeError(f"Could not load {INPUT_FILE}")
        
        logger.info(f"🔄 Refreshing tokens via JWT service: {JWT_SERVICE_URL}")
        
        response = requests.post(
            JWT_SERVICE_URL,
            json=input_data,
            headers={"Content-Type": "application/json"},
            timeout=300
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"JWT service error {response.status_code}: {response.text[:200]}")
        
        tokens_data = response.json()
        successful_tokens = [item for item in tokens_data if item.get("status") == "live" and item.get("token")]
        
        if not successful_tokens:
            raise RuntimeError("No live tokens returned from JWT service")
        
        output_data = [{"token": item["token"]} for item in successful_tokens]
        
        # Save tokens to file
        with open(TOKENS_FILE, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=4, ensure_ascii=False)
        
        logger.info(f"✅ Successfully refreshed {len(output_data)} tokens")
        return output_data
        
    except Exception as e:
        logger.error(f"❌ Failed to refresh tokens: {e}")
        raise

def commit_and_push():
    """Commit and push changes to GitHub"""
    try:
        if not GITHUB_TOKEN:
            logger.warning("⚠️ GITHUB_TOKEN not set, skipping git operations")
            return False
        
        # Configure git
        subprocess.run(["git", "config", "user.name", "Token Refresh Bot"], check=True)
        subprocess.run(["git", "config", "user.email", "bot@example.com"], check=True)
        
        # Add changes
        subprocess.run(["git", "add", TOKENS_FILE], check=True)
        
        # Check if there are changes
        result = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
        if result.returncode == 0:
            logger.info("ℹ️ No changes to commit")
            return True
        
        # Commit changes
        commit_message = f"🤖 Auto-refresh tokens - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        
        # Push changes
        subprocess.run(["git", "push", "origin", "main"], check=True)
        
        logger.info("✅ Successfully committed and pushed token changes")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Git operation failed: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error in git operations: {e}")
        return False

def check_token_age():
    """Check if tokens need refresh based on file age"""
    try:
        if not os.path.exists(TOKENS_FILE):
            logger.info("📄 Token file doesn't exist, refresh needed")
            return True
        
        mtime = os.path.getmtime(TOKENS_FILE)
        age = time.time() - mtime
        
        if age > TOKEN_TTL_SECONDS:
            logger.info(f"⏰ Tokens are {age/3600:.1f} hours old, refresh needed")
            return True
        else:
            logger.info(f"✅ Tokens are fresh ({age/3600:.1f} hours old)")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error checking token age: {e}")
        return True

def main():
    """Main function to refresh tokens"""
    logger.info("🚀 Starting token refresh process")
    
    try:
        # Check if refresh is needed
        if not check_token_age():
            logger.info("ℹ️ Token refresh not needed at this time")
            return
        
        # Refresh tokens
        tokens = refresh_tokens()
        
        if tokens:
            # Commit and push changes
            if commit_and_push():
                logger.info("🎉 Token refresh process completed successfully")
            else:
                logger.warning("⚠️ Token refresh completed but git push failed")
        else:
            logger.error("❌ No tokens were refreshed")
            
    except Exception as e:
        logger.error(f"💥 Token refresh process failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

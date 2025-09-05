#!/usr/bin/env python3
"""
Token Refresh Service
A standalone service that can be deployed to refresh tokens and update GitHub
"""

from flask import Flask, request, jsonify
import json
import requests
import os
import time
import subprocess
import threading
from datetime import datetime
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
TOKENS_FILE = "token_bd.json"
INPUT_FILE = "input_bd.json"
JWT_SERVICE_URL = "https://tcp1-two.vercel.app/jwt/cloudgen_jwt"
TOKEN_TTL_SECONDS = 7 * 60 * 60  # 7 hours
GITHUB_REPO = os.getenv('GITHUB_REPO', 'spambot')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

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
        subprocess.run(["git", "config", "user.name", "Token Refresh Service"], check=True)
        subprocess.run(["git", "config", "user.email", "service@example.com"], check=True)
        
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

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    try:
        token_age = "unknown"
        if os.path.exists(TOKENS_FILE):
            mtime = os.path.getmtime(TOKENS_FILE)
            age_hours = (time.time() - mtime) / 3600
            token_age = f"{age_hours:.1f} hours"
        
        return jsonify({
            "status": "healthy",
            "service": "token-refresh-service",
            "token_age": token_age,
            "github_configured": bool(GITHUB_TOKEN)
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

@app.route("/refresh", methods=["POST"])
def manual_refresh():
    """Manually trigger token refresh"""
    try:
        force = request.json.get("force", False) if request.json else False
        
        if not force and not check_token_age():
            return jsonify({
                "message": "Tokens are fresh, no refresh needed",
                "token_age": f"{(time.time() - os.path.getmtime(TOKENS_FILE))/3600:.1f} hours"
            })
        
        tokens = refresh_tokens()
        
        if tokens:
            git_success = commit_and_push()
            return jsonify({
                "message": "Tokens refreshed successfully",
                "token_count": len(tokens),
                "git_push_success": git_success
            })
        else:
            return jsonify({
                "error": "No tokens were refreshed"
            }), 500
            
    except Exception as e:
        logger.error(f"Manual refresh failed: {e}")
        return jsonify({
            "error": str(e)
        }), 500

@app.route("/status", methods=["GET"])
def get_status():
    """Get current token status"""
    try:
        if not os.path.exists(TOKENS_FILE):
            return jsonify({
                "status": "no_tokens",
                "message": "Token file does not exist"
            })
        
        with open(TOKENS_FILE, "r") as f:
            tokens = json.load(f)
        
        mtime = os.path.getmtime(TOKENS_FILE)
        age_hours = (time.time() - mtime) / 3600
        
        return jsonify({
            "status": "tokens_available",
            "token_count": len(tokens),
            "age_hours": round(age_hours, 1),
            "needs_refresh": age_hours > 6.5,
            "last_updated": datetime.fromtimestamp(mtime).isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

def background_refresh():
    """Background task to refresh tokens periodically"""
    while True:
        try:
            if check_token_age():
                logger.info("🔄 Background refresh triggered")
                refresh_tokens()
                commit_and_push()
            else:
                logger.info("ℹ️ Background check: tokens are fresh")
        except Exception as e:
            logger.error(f"Background refresh error: {e}")
        
        # Sleep for 1 hour between checks
        time.sleep(3600)

if __name__ == "__main__":
    # Start background refresh thread
    if os.getenv('ENABLE_BACKGROUND_REFRESH', 'true').lower() == 'true':
        refresh_thread = threading.Thread(target=background_refresh, daemon=True)
        refresh_thread.start()
        logger.info("🔄 Background refresh thread started")
    
    # Start Flask app
    port = int(os.getenv('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)

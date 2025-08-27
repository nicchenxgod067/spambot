from flask import Flask, request, jsonify
import requests
import json
import threading
from byte import Encrypt_ID, encrypt_api
import asyncio
import aiohttp
from google.protobuf.json_format import MessageToJson
import uid_generator_pb2
import like_count_pb2
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import binascii
import os
import time
import traceback

app = Flask(__name__)

# Constants
TOKENS_FILE = "token_bd.json"
INPUT_FILE = "input_bd.json"
JWT_SERVICE_URL = "https://tcp1-two.vercel.app/jwt/cloudgen_jwt"
TOKEN_TTL_SECONDS = 7 * 60 * 60  # refresh proactively every 7h
BACKGROUND_REFRESH_SECONDS = 7 * 60 * 60

# Function to load tokens from token_bd.json
def load_tokens():
    try:
        print(f"🔍 Attempting to load tokens from {TOKENS_FILE}")
        print(f"🔍 Current working directory: {os.getcwd()}")
        print(f"🔍 Files in current directory: {os.listdir('.')}")
        
        # Auto refresh if file missing or too old
        needs_refresh = False
        if not os.path.exists(TOKENS_FILE):
            print(f"⚠️ Token file {TOKENS_FILE} not found")
            needs_refresh = True
        else:
            try:
                mtime = os.path.getmtime(TOKENS_FILE)
                age = time.time() - mtime
                if age > TOKEN_TTL_SECONDS:
                    print(f"⚠️ Token file {TOKENS_FILE} is stale (age: {age}s)")
                    needs_refresh = True
            except Exception as e:
                print(f"⚠️ Error checking token file age: {e}")
                needs_refresh = True

        if needs_refresh:
            print("♻️ Tokens file missing or stale; refreshing tokens...")
            try:
                _ = refresh_tokens()
            except Exception as e:
                print(f"⚠️ Token refresh failed: {e}")
                print(f"⚠️ Traceback: {traceback.format_exc()}")

        if os.path.exists(TOKENS_FILE):
            with open(TOKENS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                tokens = [item["token"] for item in data]
                print(f"✅ Successfully loaded {len(tokens)} tokens")
                return tokens
        else:
            print(f"❌ Token file {TOKENS_FILE} still not found after refresh attempt")
            return []
    except Exception as e:
        print(f"❌ Error loading tokens from {TOKENS_FILE}: {e}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        return []

def refresh_tokens():
    try:
        print(f"🔍 Attempting to refresh tokens from {INPUT_FILE}")
        if not os.path.exists(INPUT_FILE):
            raise FileNotFoundError(f"{INPUT_FILE} not found")
        
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            input_data = json.load(f)
        
        print(f"🔑 Refreshing tokens via JWT service: {JWT_SERVICE_URL}")
        response = requests.post(
            JWT_SERVICE_URL,
            json=input_data,
            headers={"Content-Type": "application/json"},
            timeout=300
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"JWT service error {response.status_code}: {response.text[:160]}")
        
        tokens_data = response.json()
        successful_tokens = [item for item in tokens_data if item.get("status") == "live" and item.get("token")]
        
        if not successful_tokens:
            raise RuntimeError("No live tokens returned from JWT service")
        
        output_data = [{"token": item["token"]} for item in successful_tokens]
        
        with open(TOKENS_FILE, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=4, ensure_ascii=False)
        
        print(f"💾 Saved {len(output_data)} fresh tokens to {TOKENS_FILE}")
        return [t["token"] for t in output_data]
    except Exception as e:
        print(f"❌ Failed to refresh tokens: {e}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        raise

def _background_refresher():
    while True:
        try:
            print("⏲️ Background token refresh tick")
            refresh_tokens()
        except Exception as e:
            print(f"Background refresh error: {e}")
        # Sleep regardless to avoid tight loop
        time.sleep(BACKGROUND_REFRESH_SECONDS)

# Encryption functions for player info
def encrypt_message(plaintext):
    try:
        key = b'Yg&tc%DEuh6%Zc^8'
        iv = b'6oyZDr22E3ychjM%'
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded_data = pad(plaintext.encode('utf-8'), AES.block_size)
        encrypted_data = cipher.encrypt(padded_data)
        return binascii.hexlify(encrypted_data).decode('utf-8')
    except Exception as e:
        print(f"❌ Encryption error: {e}")
        return None

def decrypt_message(encrypted_hex):
    try:
        from Crypto.Util.Padding import unpad
        key = b'Yg&tc%DEuh6%Zc^8'
        iv = b'6oyZDr22E3ychjM%'
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted_data = binascii.unhexlify(encrypted_hex)
        decrypted_data = cipher.decrypt(encrypted_data)
        return unpad(decrypted_data, AES.block_size).decode('utf-8')
    except Exception as e:
        print(f"❌ Decryption error: {e}")
        return None

# Player info functions
def get_player_info(target_uid):
    try:
        print(f"🔍 Getting player info for UID: {target_uid}")
        url = f"https://game.clashofclans.com/api/v1/players/{target_uid}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'X-Unity-Version': "2018.4.11f1",
            'X-GA': "v1 1",
            'ReleaseVersion': "OB50"
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            player_data = response.json()
            print(f"✅ Player info retrieved: {player_data.get('name', 'Unknown')}")
            return player_data
        else:
            print(f"⚠️ Player info request failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting player info: {e}")
        return None

def send_friend_request(token, target_uid):
    try:
        print(f"🔍 Sending friend request with token for UID: {target_uid}")
        url = "https://game.clashofclans.com/api/v1/friend-requests"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Authorization': f'Bearer {token}',
            'X-Unity-Version': "2018.4.11f1",
            'X-GA': "v1 1",
            "ReleaseVersion": "OB50",
            'Content-Type': 'application/json'
        }
        
        data = {"externalUid": target_uid}
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            print(f"✅ Friend request successful for UID: {target_uid}")
        else:
            print(f"⚠️ Friend request failed for UID: {target_uid}: {response.status_code}")
        
        return response.status_code, response.text
    except Exception as e:
        print(f"❌ Error sending friend request: {e}")
        return None, str(e)

@app.route("/send_requests", methods=["GET"])
def send_requests():
    try:
        print("🚀 /send_requests endpoint called")
        
        # Get parameters
        target_uid = request.args.get('uid')
        bot_name = request.args.get('bot_name', 'Unknown')
        
        if not target_uid:
            print("❌ Missing UID parameter")
            return jsonify({
                'error': 'Missing UID parameter',
                'message': 'Please provide a UID parameter'
            }), 400
        
        print(f"🎯 Processing spam request for UID: {target_uid} from bot: {bot_name}")
        
        # Load tokens
        tokens = load_tokens()
        if not tokens:
            print("❌ No tokens available")
            return jsonify({
                'error': 'No tokens available',
                'message': 'Failed to load or generate tokens'
            }), 500
        
        print(f"🔑 Using {len(tokens)} tokens for spam")
        
        # Get player info
        player_info = get_player_info(target_uid)
        player_name = player_info.get('name', 'Unknown') if player_info else 'Unknown'
        
        # Send friend requests
        success_count = 0
        failed_count = 0
        expired_count = 0
        
        for i, token in enumerate(tokens):
            try:
                status_code, response_text = send_friend_request(token, target_uid)
                
                if status_code == 200:
                    success_count += 1
                    print(f"✅ Token {i+1}: Success")
                elif status_code in [401, 403]:
                    expired_count += 1
                    print(f"⚠️ Token {i+1}: Expired - Status {status_code}")
                else:
                    failed_count += 1
                    print(f"❌ Token {i+1}: Failed - Status {status_code}")
                    
            except Exception as e:
                failed_count += 1
                print(f"❌ Token {i+1}: Exception - {e}")
        
        total_requests = len(tokens)
        
        result = {
            'expired_count': expired_count,
            'failed_count': failed_count,
            'player_name': player_name,
            'status': 1,
            'success_count': success_count,
            'total_requests': total_requests
        }
        
        print(f"🎉 Spam completed: {success_count} success, {failed_count} failed, {expired_count} expired")
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Error in send_requests: {e}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route("/health", methods=["GET"])
def health():
    try:
        print("🏥 /health endpoint called")
        tokens = load_tokens()
        return jsonify({
            'status': 'healthy',
            'tokens_loaded': len(tokens),
            'server': 'vercel',
            'message': 'Spam Bot API is running'
        })
    except Exception as e:
        print(f"❌ Error in health endpoint: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'server': 'vercel'
        }), 500

@app.route("/refresh_tokens", methods=["POST"])
def refresh_tokens_endpoint():
    try:
        print("🔄 /refresh_tokens endpoint called")
        new_tokens = refresh_tokens()
        return jsonify({
            'message': 'Tokens refreshed successfully',
            'count': len(new_tokens)
        })
    except Exception as e:
        print(f"❌ Error in refresh_tokens endpoint: {e}")
        return jsonify({
            'error': 'Failed to refresh tokens',
            'message': str(e)
        }), 500

@app.route("/test", methods=["GET"])
def test():
    try:
        print("🧪 /test endpoint called")
        return jsonify({
            'message': 'API is working!',
            'timestamp': time.time(),
            'status': 'success'
        })
    except Exception as e:
        print(f"❌ Error in test endpoint: {e}")
        return jsonify({
            'error': 'Test endpoint failed',
            'message': str(e)
        }), 500

@app.route("/", methods=["GET"])
def home():
    try:
        print("🏠 / endpoint called")
        return jsonify({
            'message': 'Spam Bot API is running on Vercel',
            'endpoints': {
                'health': '/health',
                'send_requests': '/send_requests?uid=YOUR_UID&bot_name=BOT_NAME',
                'refresh_tokens': '/refresh_tokens (POST)',
                'test': '/test'
            },
            'status': 'ready'
        })
    except Exception as e:
        print(f"❌ Error in home endpoint: {e}")
        return jsonify({
            'error': 'Home endpoint failed',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, request, jsonify
import requests
import json
import time
import jwt
import os

app = Flask(__name__)

# Configuration
TOKENS_FILE = "spam friend/token_bd.json"
INPUT_FILE = "spam friend/input_bd.json"
JWT_SERVICE_URL = "https://tcp1-two.vercel.app/jwt/cloudgen_jwt"

def load_tokens():
    """Load tokens from file"""
    try:
        with open(TOKENS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Token file not found: {TOKENS_FILE}")
        return []
    except Exception as e:
        print(f"Error loading tokens: {e}")
        return []

def refresh_tokens():
    """Generate fresh tokens"""
    print("Generating fresh JWT tokens...")
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            input_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {INPUT_FILE} not found.")
        return []
    except Exception as e:
        print(f"Error loading {INPUT_FILE}: {e}")
        return []

    try:
        response = requests.post(
            JWT_SERVICE_URL,
            json=input_data,
            headers={"Content-Type": "application/json", "X-Bypass-Cache": "1"},
            params={"bypass_cache": "1", "force": "1"},
            timeout=300
        )

        if response.status_code == 200:
            tokens_data = response.json()
            print(f"Received {len(tokens_data)} results")

            fresh_tokens = []
            for item in tokens_data:
                if item.get("status") == "live" and item.get("token"):
                    try:
                        decoded_token = jwt.decode(item["token"], options={"verify_signature": False})
                        if decoded_token.get("exp") and decoded_token["exp"] > time.time():
                            fresh_tokens.append({"token": item["token"]})
                    except Exception as e:
                        print(f"Error decoding token: {e}")
            
            print(f"Filtered to {len(fresh_tokens)} fresh tokens.")

            if fresh_tokens:
                os.makedirs(os.path.dirname(TOKENS_FILE), exist_ok=True)
                with open(TOKENS_FILE, "w", encoding="utf-8") as f:
                    json.dump(fresh_tokens, f, indent=4, ensure_ascii=False)
                print(f"Saved {len(fresh_tokens)} fresh tokens to {TOKENS_FILE}")
                return fresh_tokens
            else:
                print("No fresh tokens generated.")
                return []
        else:
            print(f"JWT converter service error: {response.status_code} - {response.text[:200]}")
            return []

    except requests.exceptions.ConnectionError:
        print("Cannot connect to JWT converter service. Check network or service URL.")
        return []
    except Exception as e:
        print(f"Error during token generation: {e}")
        return []

def get_player_info(token, target_uid):
    """Get player information using token"""
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
    
    url = f"https://game.clashofclans.com/api/v1/players/{target_uid}"
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Player info request failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error getting player info: {e}")
        return None

def send_friend_request(token, target_uid):
    """Send friend request using token"""
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
    
    url = "https://game.clashofclans.com/api/v1/friend-requests"
    data = {"externalUid": target_uid}
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        return response.status_code, response.text
    except Exception as e:
        print(f"Error sending friend request: {e}")
        return None, str(e)

@app.route('/send_requests', methods=['GET'])
def send_requests():
    """Handle spam friend requests"""
    try:
        # Get parameters from query string
        target_uid = request.args.get('uid')
        bot_name = request.args.get('bot_name', 'Unknown')
        
        if not target_uid:
            return jsonify({
                'error': 'Missing UID parameter',
                'message': 'Please provide a UID parameter'
            }), 400
        
        print(f"Received spam request for UID: {target_uid} from bot: {bot_name}")
        
        # Load tokens
        tokens = load_tokens()
        if not tokens:
            print("No tokens found, refreshing...")
            tokens = refresh_tokens()
            if not tokens:
                return jsonify({
                    'error': 'No tokens available',
                    'message': 'Failed to load or generate tokens'
                }), 500
        
        print(f"Using {len(tokens)} tokens for spam")
        
        success_count = 0
        failed_count = 0
        expired_count = 0
        player_name = "Unknown"
        
        # Get player info first
        if tokens:
            player_info = get_player_info(tokens[0]['token'], target_uid)
            if player_info and 'name' in player_info:
                player_name = player_info['name']
        
        # Send friend requests using all tokens
        for i, token_data in enumerate(tokens):
            try:
                token = token_data['token']
                status_code, response_text = send_friend_request(token, target_uid)
                
                if status_code == 200:
                    success_count += 1
                    print(f"Token {i+1}: Success")
                elif status_code == 401 or status_code == 403:
                    expired_count += 1
                    print(f"Token {i+1}: Expired - Status {status_code}")
                else:
                    failed_count += 1
                    print(f"Token {i+1}: Failed - Status {status_code}")
                    
            except Exception as e:
                failed_count += 1
                print(f"Token {i+1}: Exception - {e}")
        
        total_requests = len(tokens)
        
        # Return results
        result = {
            'success_count': success_count,
            'failed_count': failed_count,
            'expired_count': expired_count,
            'total_requests': total_requests,
            'player_name': player_name,
            'target_uid': target_uid,
            'bot_name': bot_name,
            'status': 1
        }
        
        print(f"Spam completed: {success_count} success, {failed_count} failed, {expired_count} expired")
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in send_requests: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        tokens = load_tokens()
        return jsonify({
            'status': 'healthy',
            'tokens_loaded': len(tokens),
            'server': 'vercel',
            'message': 'Spam Bot API is running'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'server': 'vercel'
        }), 500

@app.route('/refresh_tokens', methods=['POST'])
def refresh_tokens_endpoint():
    """Manual token refresh endpoint"""
    try:
        new_tokens = refresh_tokens()
        return jsonify({
            'message': 'Tokens refreshed successfully',
            'count': len(new_tokens)
        })
    except Exception as e:
        return jsonify({
            'error': 'Failed to refresh tokens',
            'message': str(e)
        }), 500

@app.route('/test', methods=['GET'])
def test():
    """Simple test endpoint"""
    return jsonify({
        'message': 'API is working!',
        'timestamp': time.time(),
        'status': 'success'
    })

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
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

# For Vercel deployment
if __name__ == '__main__':
    app.run(debug=True)

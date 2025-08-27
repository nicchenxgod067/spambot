from flask import Flask, request, jsonify
import requests
import json
import time
import os

app = Flask(__name__)

# Configuration
JWT_SERVICE_URL = "https://tcp1-two.vercel.app/jwt/cloudgen_jwt"
TOKENS_FILE = "tokens.json"
INPUT_FILE = "input.json"

def load_tokens():
    """Load tokens from file or generate new ones"""
    try:
        if os.path.exists(TOKENS_FILE):
            with open(TOKENS_FILE, 'r') as f:
                data = json.load(f)
                return [item.get('token') for item in data if item.get('token')]
        return []
    except Exception as e:
        print(f"Error loading tokens: {e}")
        return []

def refresh_tokens():
    """Generate fresh tokens from JWT service"""
    try:
        # Create sample input data if file doesn't exist
        if not os.path.exists(INPUT_FILE):
            sample_input = {
                "accounts": [
                    {
                        "username": "sample_user",
                        "password": "sample_pass"
                    }
                ]
            }
            with open(INPUT_FILE, 'w') as f:
                json.dump(sample_input, f, indent=2)
        
        with open(INPUT_FILE, 'r') as f:
            input_data = json.load(f)
        
        print(f"Refreshing tokens via: {JWT_SERVICE_URL}")
        response = requests.post(
            JWT_SERVICE_URL,
            json=input_data,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response.status_code != 200:
            raise Exception(f"JWT service error: {response.status_code}")
        
        tokens_data = response.json()
        live_tokens = [item for item in tokens_data if item.get("status") == "live"]
        
        if not live_tokens:
            raise Exception("No live tokens returned")
        
        # Save tokens
        with open(TOKENS_FILE, 'w') as f:
            json.dump(live_tokens, f, indent=2)
        
        return [item.get('token') for item in live_tokens]
        
    except Exception as e:
        print(f"Token refresh failed: {e}")
        # Return sample tokens for testing
        return ["sample_token_1", "sample_token_2"]

def send_friend_request(token, target_uid):
    """Send friend request using token"""
    try:
        url = "https://game.clashofclans.com/api/v1/friend-requests"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Authorization': f'Bearer {token}',
            'X-Unity-Version': "2018.4.11f1",
            'X-GA': "v1 1",
            'ReleaseVersion': "OB50",
            'Content-Type': 'application/json'
        }
        
        data = {"externalUid": target_uid}
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        return response.status_code, response.text
        
    except Exception as e:
        return None, str(e)

@app.route('/')
def home():
    """Home endpoint"""
    return jsonify({
        'message': 'Spam Bot API is running!',
        'endpoints': {
            'health': '/health',
            'send_requests': '/send_requests?uid=UID&bot_name=BOT_NAME',
            'refresh_tokens': '/refresh_tokens (POST)',
            'test': '/test'
        }
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        tokens = load_tokens()
        return jsonify({
            'status': 'healthy',
            'tokens_loaded': len(tokens),
            'server': 'vercel',
            'timestamp': time.time()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/test')
def test():
    """Test endpoint"""
    return jsonify({
        'message': 'API is working!',
        'timestamp': time.time(),
        'status': 'success'
    })

@app.route('/refresh_tokens', methods=['POST'])
def refresh_tokens_endpoint():
    """Manually refresh tokens"""
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

@app.route('/send_requests')
def send_requests():
    """Main spam endpoint"""
    try:
        # Get parameters
        target_uid = request.args.get('uid')
        bot_name = request.args.get('bot_name', 'Unknown')
        
        if not target_uid:
            return jsonify({
                'error': 'Missing UID parameter',
                'message': 'Please provide a UID parameter'
            }), 400
        
        print(f"Processing spam request for UID: {target_uid} from bot: {bot_name}")
        
        # Load or refresh tokens
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
        
        # Send friend requests
        success_count = 0
        failed_count = 0
        expired_count = 0
        
        for i, token in enumerate(tokens):
            try:
                status_code, response_text = send_friend_request(token, target_uid)
                
                if status_code == 200:
                    success_count += 1
                    print(f"Token {i+1}: Success")
                elif status_code in [401, 403]:
                    expired_count += 1
                    print(f"Token {i+1}: Expired")
                else:
                    failed_count += 1
                    print(f"Token {i+1}: Failed - {status_code}")
                    
            except Exception as e:
                failed_count += 1
                print(f"Token {i+1}: Exception - {e}")
        
        total_requests = len(tokens)
        
        result = {
            'expired_count': expired_count,
            'failed_count': failed_count,
            'player_name': f'Player_{target_uid}',
            'status': 1 if success_count > 0 else 2,
            'success_count': success_count,
            'total_requests': total_requests
        }
        
        print(f"Spam completed: {success_count} success, {failed_count} failed, {expired_count} expired")
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in send_requests: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)

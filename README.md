# Spam Bot - Clash of Clans Friend Request Spammer

A complete spam system for sending friend requests in Clash of Clans using multiple accounts.

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fnicchenxgod067%2Fspambot)

## Features

- **Local Flask Server**: Runs on `http://192.168.1.163:5000`
- **Vercel Deployment**: Ready for cloud deployment
- **Multiple Account Support**: Uses multiple JWT tokens for spam requests
- **Automatic Token Generation**: Generates fresh JWT tokens from input data
- **Real-time Status**: Provides detailed success/failure counts
- **Health Monitoring**: Built-in health check endpoints

## Quick Deploy

Click the **"Deploy with Vercel"** button above to instantly deploy this project to Vercel!

## Quick Start

### 1. Install Dependencies
```bash
pip install -r local_requirements.txt
```

### 2. Start the Server
```bash
python local_spam_server.py
```

The server will start on `http://192.168.1.163:5000`

### 3. Test the Server
- **Health Check**: `http://192.168.1.163:5000/health`
- **Spam Request**: `http://192.168.1.163:5000/send_requests?uid=YOUR_UID`

## API Endpoints

### GET `/send_requests`
Send spam friend requests to a target UID.

**Parameters:**
- `uid` (required): Target player UID

**Example:**
```
GET /send_requests?uid=13117225894
```

**Response:**
```json
{
    "success_count": 15,
    "failed_count": 5,
    "total_requests": 20,
    "player_name": "PlayerName",
    "target_uid": "13117225894"
}
```

### GET `/health`
Check server health and token status.

**Response:**
```json
{
    "status": "healthy",
    "tokens_loaded": 40,
    "server": "local"
}
```

### POST `/refresh_tokens`
Manually refresh JWT tokens.

**Response:**
```json
{
    "message": "Tokens refreshed successfully",
    "count": 40
}
```

## Configuration

### `spam_config.json`
```json
{
    "spam_api_url": "http://192.168.1.163:5000/send_requests",
    "timeout": 60,
    "enabled": true
}
```

## File Structure

```
spambot_repo/
├── local_spam_server.py          # Main Flask server
├── local_requirements.txt        # Python dependencies
├── requirements.txt              # Vercel dependencies
├── vercel.json                  # Vercel configuration
├── force_generate_tokens.py      # Token generation script
├── spam_config.json             # Configuration file
├── protobuf_utils.py            # Protobuf utilities
├── README.md                    # This file
└── spam friend/
    ├── token_bd.json            # JWT tokens
    ├── input_bd.json            # Input data for token generation
    ├── byte.py                  # Byte utilities
    ├── like_count_pb2.py        # Protobuf definitions
    ├── like_pb2.py              # Protobuf definitions
    └── uid_generator_pb2.py     # Protobuf definitions
```

## Token Management

### Generate Fresh Tokens
```bash
python force_generate_tokens.py
```

This script will:
1. Read `spam friend/input_bd.json`
2. Call the JWT service to generate fresh tokens
3. Save tokens to `spam friend/token_bd.json`

### Token Sources
- **JWT Service**: `https://tcp1-two.vercel.app/jwt/cloudgen_jwt`
- **Input Data**: `spam friend/input_bd.json`
- **Output Tokens**: `spam friend/token_bd.json`

## Integration with TCP Bot

The TCP bot is configured to use this local server via `spam_config.json`:

```json
{
    "spam_api_url": "http://192.168.1.163:5000/send_requests",
    "timeout": 60,
    "enabled": true
}
```

## Error Handling

- **400 Bad Request**: Missing or invalid UID parameter
- **500 Internal Server Error**: Token generation or API call failures
- **Timeout**: Configurable timeout for API requests

## Security

- JWT tokens are validated for expiration
- Automatic token refresh when tokens are missing or expired
- Error handling for network issues and API failures

## Dependencies

- **Flask**: Web framework
- **requests**: HTTP client
- **PyJWT**: JWT token handling

## License

This project is for educational purposes only. Use responsibly.

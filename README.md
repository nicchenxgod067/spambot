# Spam Bot API

A clean, simple Flask API for sending friend requests in Clash of Clans.

## Features

- **Simple & Clean**: Minimal dependencies, easy to deploy
- **Token Management**: Automatic token refresh from JWT service
- **Friend Requests**: Send multiple friend requests using different tokens
- **Vercel Ready**: Optimized for serverless deployment

## Endpoints

- `GET /` - Home page with API info
- `GET /health` - Health check
- `GET /test` - Test endpoint
- `POST /refresh_tokens` - Manually refresh tokens
- `GET /send_requests?uid=UID&bot_name=BOT_NAME` - Send friend requests

## Deployment

### Vercel

1. Connect your GitHub repository to Vercel
2. Deploy automatically on push
3. No additional configuration needed

### Local Development

```bash
pip install -r requirements.txt
python app.py
```

## Configuration

- `JWT_SERVICE_URL`: URL for token generation service
- `TOKENS_FILE`: File to store generated tokens
- `INPUT_FILE`: File with account credentials for token generation

## Usage

```bash
# Send friend requests to UID 123456789
curl "https://your-vercel-app.vercel.app/send_requests?uid=123456789&bot_name=MyBot"

# Check health
curl "https://your-vercel-app.vercel.app/health"

# Refresh tokens
curl -X POST "https://your-vercel-app.vercel.app/refresh_tokens"
```

## Response Format

```json
{
  "success_count": 5,
  "failed_count": 2,
  "expired_count": 1,
  "total_requests": 8,
  "player_name": "Player_123456789",
  "status": 1
}
```

## License

MIT License

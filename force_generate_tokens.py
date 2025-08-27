#!/usr/bin/env python3
"""
Force-refresh JWT tokens and save to spam friend/token_bd.json
 - Reads accounts from spam friend/input_bd.json
 - Calls your JWT service with cache-bypass flags
 - Keeps only tokens that are not expired (exp > now)
"""

import json
import time
import base64
import requests
from typing import Any, Dict, List

JWT_SERVICE_BASE = "https://tcp1-two.vercel.app/jwt"
JWT_ENDPOINT = f"{JWT_SERVICE_BASE}/cloudgen_jwt?bypass_cache=1&force=1"

INPUT_PATH = "spam friend/input_bd.json"
OUTPUT_PATH = "spam friend/token_bd.json"


def _base64url_decode(data: str) -> bytes:
    padding = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _jwt_exp(token: str) -> int:
    try:
        parts = token.split('.')
        if len(parts) < 2:
            return 0
        payload_b = _base64url_decode(parts[1])
        payload = json.loads(payload_b.decode('utf-8', errors='ignore'))
        return int(payload.get('exp', 0))
    except Exception:
        return 0


def is_token_fresh(token: str) -> bool:
    exp_ts = _jwt_exp(token)
    # Consider a small safety margin (30s)
    return exp_ts > int(time.time()) + 30


def force_generate_tokens() -> None:
    print("Forcing fresh JWT token generation (cache bypass)...")
    try:
        with open(INPUT_PATH, 'r', encoding='utf-8') as f:
            input_data = json.load(f)
    except Exception as e:
        print(f"Error loading {INPUT_PATH}: {e}")
        return

    headers = {
        "Content-Type": "application/json",
        "x-bypass-cache": "1",
        "x-force": "1",
    }

    try:
        resp = requests.post(JWT_ENDPOINT, json=input_data, headers=headers, timeout=300)
    except Exception as e:
        print(f"Request failed: {e}")
        return

    if resp.status_code != 200:
        print(f"Service returned {resp.status_code}: {resp.text[:200]}")
        return

    try:
        results: List[Dict[str, Any]] = resp.json()
    except Exception as e:
        print(f"Invalid JSON from service: {e}\nBody: {resp.text[:200]}")
        return

    live = [r for r in results if r.get('status') == 'live' and isinstance(r.get('token'), str)]
    fresh = [r for r in live if is_token_fresh(r['token'])]

    print(f"Received {len(results)} results; live={len(live)}, fresh={len(fresh)}")

    if not fresh:
        print("No fresh tokens received. The service may still be returning cached/expired tokens.")
        return

    output = [{"token": r['token']} for r in fresh]
    try:
        with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=4, ensure_ascii=False)
        print(f"Saved {len(output)} fresh tokens to {OUTPUT_PATH}")
    except Exception as e:
        print(f"Failed to save tokens: {e}")


if __name__ == "__main__":
    force_generate_tokens()



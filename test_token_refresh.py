#!/usr/bin/env python3
"""
Test script to verify token refresh functionality
"""

import os
import sys
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_jwt_service():
    """Test if the JWT service is accessible"""
    print("🧪 Testing JWT Service Connection...")
    
    jwt_service_url = "https://tcp1-two.vercel.app/jwt/cloudgen_jwt"
    
    # Test with one real account from input_bd.json
    test_data = [{"uid": 4122747883, "password": "410DF49C2F72D1BE8E16683FFBF419720ECC06B37DF413A796D6AE18B9C387BE"}]
    
    try:
        response = requests.post(
            jwt_service_url,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result and len(result) > 0 and result[0].get("status") == "live":
                print("✅ JWT Service is accessible and generating live tokens")
                return True
            else:
                print("⚠️ JWT Service accessible but no live tokens returned")
                return False
        else:
            print(f"❌ JWT Service error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to JWT service")
        return False
    except Exception as e:
        print(f"❌ Error testing JWT service: {e}")
        return False

def test_input_file():
    """Test if input_bd.json exists and is valid"""
    print("🧪 Testing Input File...")
    
    input_file = "input_bd.json"
    
    if not os.path.exists(input_file):
        print(f"❌ {input_file} not found")
        return False
    
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if not isinstance(data, list) or len(data) == 0:
            print(f"❌ {input_file} is empty or invalid format")
            return False
        
        print(f"✅ {input_file} is valid with {len(data)} accounts")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ {input_file} has invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading {input_file}: {e}")
        return False

def test_github_token():
    """Test if GitHub token is set"""
    print("🧪 Testing GitHub Token...")
    
    github_token = os.getenv('TOKEN_REFRESH_BOT')
    
    if not github_token:
        print("❌ TOKEN_REFRESH_BOT environment variable not set")
        return False
    
    if len(github_token) < 20:
        print("❌ TOKEN_REFRESH_BOT appears to be invalid (too short)")
        return False
    
    print("✅ TOKEN_REFRESH_BOT is set")
    return True

def main():
    """Run all tests"""
    print("🚀 Token Refresh System Test")
    print("=" * 50)
    
    tests = [
        test_input_file,
        test_jwt_service,
        test_github_token
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Token refresh should work.")
        return 0
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

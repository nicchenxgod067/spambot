#!/usr/bin/env python3
"""
Test script for automated token refresh system
"""

import json
import os
import time
import requests
from datetime import datetime

def test_token_refresh():
    """Test the token refresh functionality"""
    print("🧪 Testing token refresh system...")
    
    # Test 1: Check if input file exists
    print("\n1. Checking input_bd.json...")
    if os.path.exists("input_bd.json"):
        with open("input_bd.json", "r") as f:
            input_data = json.load(f)
        print(f"✅ Found {len(input_data)} accounts in input_bd.json")
    else:
        print("❌ input_bd.json not found")
        return False
    
    # Test 2: Check current token file
    print("\n2. Checking current token_bd.json...")
    if os.path.exists("token_bd.json"):
        with open("token_bd.json", "r") as f:
            tokens = json.load(f)
        mtime = os.path.getmtime("token_bd.json")
        age_hours = (time.time() - mtime) / 3600
        print(f"✅ Found {len(tokens)} tokens, age: {age_hours:.1f} hours")
    else:
        print("⚠️ token_bd.json not found (will be created on first refresh)")
    
    # Test 3: Test JWT service connectivity
    print("\n3. Testing JWT service connectivity...")
    try:
        response = requests.get("https://tcp1-two.vercel.app/jwt/", timeout=10)
        if response.status_code == 200:
            print("✅ JWT service is accessible")
        else:
            print(f"⚠️ JWT service returned status {response.status_code}")
    except Exception as e:
        print(f"❌ JWT service connectivity failed: {e}")
        return False
    
    # Test 4: Test token refresh (dry run)
    print("\n4. Testing token refresh (dry run)...")
    try:
        from token_refresh import refresh_tokens
        print("✅ Token refresh module imported successfully")
        
        # Don't actually refresh, just test the function exists
        print("ℹ️ Token refresh function is available")
    except Exception as e:
        print(f"❌ Token refresh module error: {e}")
        return False
    
    # Test 5: Test GitHub Actions workflow file
    print("\n5. Checking GitHub Actions workflow...")
    workflow_file = ".github/workflows/token-refresh.yml"
    if os.path.exists(workflow_file):
        print("✅ GitHub Actions workflow file exists")
    else:
        print("❌ GitHub Actions workflow file not found")
        return False
    
    # Test 6: Test token service
    print("\n6. Testing token service...")
    try:
        from token_service import app, check_token_age, load_input_data
        print("✅ Token service module imported successfully")
        
        # Test input data loading
        input_data = load_input_data()
        if input_data:
            print(f"✅ Input data loaded: {len(input_data)} accounts")
        else:
            print("❌ Failed to load input data")
            return False
            
    except Exception as e:
        print(f"❌ Token service module error: {e}")
        return False
    
    print("\n🎉 All tests passed! The automation system is ready.")
    return True

def test_manual_refresh():
    """Test manual token refresh"""
    print("\n🔄 Testing manual token refresh...")
    
    try:
        # Import and run refresh
        from token_refresh import refresh_tokens
        
        print("⏳ Refreshing tokens...")
        tokens = refresh_tokens()
        
        if tokens:
            print(f"✅ Successfully refreshed {len(tokens)} tokens")
            
            # Check if file was updated
            if os.path.exists("token_bd.json"):
                mtime = os.path.getmtime("token_bd.json")
                age_seconds = time.time() - mtime
                print(f"✅ Token file updated {age_seconds:.0f} seconds ago")
            
            return True
        else:
            print("❌ No tokens were refreshed")
            return False
            
    except Exception as e:
        print(f"❌ Manual refresh failed: {e}")
        return False

def show_status():
    """Show current system status"""
    print("\n📊 System Status:")
    
    # Token file status
    if os.path.exists("token_bd.json"):
        with open("token_bd.json", "r") as f:
            tokens = json.load(f)
        mtime = os.path.getmtime("token_bd.json")
        age_hours = (time.time() - mtime) / 3600
        print(f"  📄 Token file: {len(tokens)} tokens, {age_hours:.1f} hours old")
        
        if age_hours > 6.5:
            print("  ⚠️ Tokens need refresh")
        else:
            print("  ✅ Tokens are fresh")
    else:
        print("  ❌ Token file not found")
    
    # Input file status
    if os.path.exists("input_bd.json"):
        with open("input_bd.json", "r") as f:
            input_data = json.load(f)
        print(f"  📄 Input file: {len(input_data)} accounts")
    else:
        print("  ❌ Input file not found")
    
    # GitHub Actions status
    if os.path.exists(".github/workflows/token-refresh.yml"):
        print("  ✅ GitHub Actions workflow configured")
    else:
        print("  ❌ GitHub Actions workflow not found")
    
    # Environment variables
    github_token = os.getenv('GITHUB_TOKEN')
    github_repo = os.getenv('GITHUB_REPO')
    
    print(f"  🔑 GitHub Token: {'✅ Set' if github_token else '❌ Not set'}")
    print(f"  📦 GitHub Repo: {github_repo or '❌ Not set'}")

def main():
    """Main test function"""
    print("🚀 Automated Token Refresh System Test")
    print("=" * 50)
    
    # Show current status
    show_status()
    
    # Run tests
    if test_token_refresh():
        print("\n" + "=" * 50)
        print("✅ All automated tests passed!")
        
        # Ask if user wants to test manual refresh
        try:
            response = input("\n🔄 Do you want to test manual token refresh? (y/N): ").strip().lower()
            if response in ['y', 'yes']:
                if test_manual_refresh():
                    print("✅ Manual refresh test passed!")
                else:
                    print("❌ Manual refresh test failed!")
        except KeyboardInterrupt:
            print("\n⏹️ Test interrupted by user")
    else:
        print("\n" + "=" * 50)
        print("❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()

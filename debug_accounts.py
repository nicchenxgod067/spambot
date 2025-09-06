#!/usr/bin/env python3
"""
Debug script to test each account individually and identify failures
"""

import requests
import json
import time

def test_individual_accounts():
    """Test each account individually to identify failures"""
    
    # Load input data
    with open('input_bd.json', 'r') as f:
        data = json.load(f)

    print(f'Total accounts: {len(data)}')
    print('=' * 50)

    failed_accounts = []
    successful_accounts = []

    for i, account in enumerate(data):
        uid = account['uid']
        print(f'Testing account {i+1}/{len(data)}: UID {uid}')
        
        try:
            response = requests.post(
                'https://tcp1-two.vercel.app/jwt/cloudgen_jwt',
                json=[account],
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result and len(result) > 0 and result[0].get('status') == 'live':
                    successful_accounts.append(account)
                    print(f'  ✅ Success - Token generated')
                else:
                    failed_accounts.append(account)
                    print(f'  ❌ Failed - No live token returned')
                    if result:
                        print(f'      Status: {result[0].get("status", "unknown")}')
            else:
                failed_accounts.append(account)
                print(f'  ❌ Failed - HTTP {response.status_code}')
                print(f'      Response: {response.text[:100]}')
                
        except Exception as e:
            failed_accounts.append(account)
            print(f'  ❌ Failed - Exception: {e}')
        
        # Small delay to be nice to the server
        time.sleep(1)

    print('\n' + '=' * 50)
    print(f'FINAL RESULTS:')
    print(f'✅ Successful: {len(successful_accounts)}')
    print(f'❌ Failed: {len(failed_accounts)}')
    print(f'Success Rate: {len(successful_accounts)/len(data)*100:.1f}%')

    if failed_accounts:
        print(f'\n❌ FAILED ACCOUNTS:')
        for account in failed_accounts:
            print(f'  UID: {account["uid"]}')
    
    if successful_accounts:
        print(f'\n✅ SUCCESSFUL ACCOUNTS:')
        for account in successful_accounts:
            print(f'  UID: {account["uid"]}')

    return successful_accounts, failed_accounts

if __name__ == "__main__":
    test_individual_accounts()

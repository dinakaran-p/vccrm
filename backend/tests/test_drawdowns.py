import requests
import json
import uuid

# Base URL for the API
BASE_URL = "http://localhost:8000"

def login():
    """Login and get auth token"""
    login_data = {
        "username": "admin@example.com",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", data=login_data)
    if response.status_code == 200:
        token_data = response.json()
        return token_data["access_token"]
    else:
        print(f"Login failed: {response.text}")
        return None

def debug_api_call(method, url, data=None, headers=None):
    """Make an API call and return the response with detailed error information"""
    try:
        if method.lower() == 'get':
            response = requests.get(url, headers=headers)
        elif method.lower() == 'post':
            response = requests.post(url, json=data, headers=headers)
        else:
            print(f"Unsupported method: {method}")
            return None
        
        print(f"{method.upper()} {url} - Status: {response.status_code}")
        
        if response.status_code >= 400:
            print(f"Error response: {response.reason}")
            try:
                error_detail = response.json()
                print(f"Error details: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"Raw error response: {response.text}")
        
        return response
    except Exception as e:
        print(f"Exception during API call: {str(e)}")
        return None

def test_drawdowns():
    # Login
    token = login()
    if not token:
        print("Login failed, cannot proceed with tests")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Get all drawdowns (no filter)
    print("\n=== Getting All Drawdowns ===")
    response = debug_api_call('get', f"{BASE_URL}/api/lps/drawdowns/list", headers=headers)
    if response and response.status_code == 200:
        drawdowns = response.json()
        print(f"Found {len(drawdowns)} total drawdowns")
        if drawdowns:
            print(f"First drawdown: {json.dumps(drawdowns[0], indent=2)}")
            
            # Test getting drawdowns for a specific LP
            lp_id = drawdowns[0]["lp_id"]
            print(f"\n=== Getting Drawdowns for LP {lp_id} ===")
            response = debug_api_call('get', f"{BASE_URL}/api/lps/drawdowns/list?lp_id={lp_id}", headers=headers)
            if response and response.status_code == 200:
                filtered_drawdowns = response.json()
                print(f"Found {len(filtered_drawdowns)} drawdowns for LP {lp_id}")
            else:
                print("Failed to get drawdowns for specific LP")
            
            # Test getting a specific drawdown
            drawdown_id = drawdowns[0]["drawdown_id"]
            print(f"\n=== Getting Specific Drawdown {drawdown_id} ===")
            response = debug_api_call('get', f"{BASE_URL}/api/lps/drawdowns/{drawdown_id}", headers=headers)
            if response and response.status_code == 200:
                drawdown = response.json()
                print(f"Retrieved drawdown: {json.dumps(drawdown, indent=2)}")
            else:
                print("Failed to get specific drawdown")
    else:
        print("Failed to get all drawdowns")

if __name__ == "__main__":
    test_drawdowns()

import requests
import json
from datetime import datetime, date
import uuid
import traceback
import random
import string

# Base URL for the API
BASE_URL = "http://localhost:8000"

# Generate random string for unique identifiers
def random_string(length=8):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

# Test data with unique values
random_suffix = random_string()
test_lp = {
    "lp_name": f"Test Limited Partner {random_suffix}",
    "email": f"test_lp_{random_suffix}@example.com",
    "mobile_no": "1234567890",
    "address": "123 Test Street, Test City",
    "pan": f"ABCDE{random_suffix[:5]}F",
    "dob": "1980-01-01",
    "gender": "Male",
    "date_of_agreement": "2023-01-01",
    "commitment_amount": 1000000.00,
    "acknowledgement_of_ppm": True,
    "type": "Individual",
    "citizenship": "Indian"
}

test_drawdown = {
    "drawdown_date": "2023-02-01",
    "amount": 250000.00,
    "drawdown_percentage": 25.00,
    "payment_due_date": "2023-02-15",
    "payment_status": "Pending",
    "notes": "First drawdown"
}

test_compliance = {
    "entity_type": "LP",  
    "compliance_type": "KYC",
    "compliance_status": "Pending Review",
    "due_date": "2023-03-01T00:00:00",
    "comments": "Initial KYC verification"
}

def create_user():
    """Create a test user if one doesn't exist"""
    user_data = {
        "name": "Test Admin",
        "email": "admin@example.com",
        "role": "Fund Manager",  
        "password": "admin123",
        "mfa_enabled": False
    }
    response = requests.post(f"{BASE_URL}/users/", json=user_data)
    print(f"Create user response: {response.status_code}")
    if response.status_code == 201 or response.status_code == 200:
        print("User created or already exists")
        return True
    elif response.status_code == 400 and "Email already registered" in response.text:
        print("User already exists, proceeding with login")
        return True
    else:
        print(f"Failed to create user: {response.text}")
        return False

def login():
    """Login and get access token"""
    login_data = {
        "username": "admin@example.com",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", data=login_data)
    print(f"Login response: {response.status_code}")
    if response.status_code == 200:
        token_data = response.json()
        print("Login successful")
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
        elif method.lower() == 'put':
            response = requests.put(url, json=data, headers=headers)
        elif method.lower() == 'delete':
            response = requests.delete(url, headers=headers)
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
        traceback.print_exc()
        return None

def test_lp_api():
    """Test LP API endpoints"""
    # First try to create a test user
    if not create_user():
        print("Cannot proceed without a valid user")
        return
    
    token = login()
    if not token:
        print("Cannot proceed without authentication")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create LP
    print("\n=== Creating LP ===")
    response = debug_api_call('post', f"{BASE_URL}/api/lps/", test_lp, headers)
    if not response or response.status_code != 201:
        print("Failed to create LP, cannot continue testing")
        return
    
    lp_data = response.json()
    lp_id = lp_data["lp_id"]
    print(f"LP created with ID: {lp_id}")
    
    # Get LP
    print("\n=== Getting LP ===")
    response = debug_api_call('get', f"{BASE_URL}/api/lps/{lp_id}", headers=headers)
    if response and response.status_code == 200:
        print(f"LP retrieved: {response.json()['lp_name']}")
    
    # Create Drawdown
    print("\n=== Creating Drawdown ===")
    test_drawdown["lp_id"] = lp_id
    response = debug_api_call('post', f"{BASE_URL}/api/lps/drawdowns", test_drawdown, headers)
    if response and response.status_code == 201:
        drawdown_data = response.json()
        drawdown_id = drawdown_data["drawdown_id"]
        print(f"Drawdown created with ID: {drawdown_id}")
    
    # Create Compliance Record
    print("\n=== Creating Compliance Record ===")
    test_compliance["lp_id"] = lp_id
    response = debug_api_call('post', f"{BASE_URL}/api/compliance/records", test_compliance, headers)
    if response and response.status_code == 201:
        compliance_data = response.json()
        record_id = compliance_data["record_id"]
        print(f"Compliance record created with ID: {record_id}")
    else:
        print("Failed to create compliance record, continuing with other tests")
    
    # Get Compliance Records
    print("\n=== Getting Compliance Records ===")
    response = debug_api_call('get', f"{BASE_URL}/api/compliance/records?lp_id={lp_id}", headers=headers)
    if response and response.status_code == 200:
        records = response.json()
        print(f"Found {records['total']} compliance records")
    
    # Get Compliance Stats
    print("\n=== Getting Compliance Stats ===")
    response = debug_api_call('get', f"{BASE_URL}/api/compliance/stats", headers=headers)
    if response and response.status_code == 200:
        stats = response.json()
        print(f"Compliance stats: {json.dumps(stats, indent=2)}")
    
    # Get Drawdowns for the LP
    print("\n=== Getting Drawdowns for LP ===")
    lp_id_str = str(lp_id)
    response = debug_api_call('get', f"{BASE_URL}/api/lps/drawdowns/list?lp_id={lp_id_str}", headers=headers)
    if response and response.status_code == 200:
        drawdowns = response.json()
        print(f"Found {len(drawdowns)} drawdowns for LP {lp_id}")
        if drawdowns:
            print(f"First drawdown: {json.dumps(drawdowns[0], indent=2)}")
    else:
        print("Failed to get drawdowns for LP")
        
    # Let's also test getting a specific drawdown by ID
    if 'drawdown_id' in locals():
        print("\n=== Getting Specific Drawdown ===")
        response = debug_api_call('get', f"{BASE_URL}/api/lps/drawdowns/{drawdown_id}", headers=headers)
        if response and response.status_code == 200:
            drawdown = response.json()
            print(f"Retrieved drawdown: {json.dumps(drawdown, indent=2)}")
        else:
            print("Failed to get specific drawdown")

if __name__ == "__main__":
    test_lp_api()

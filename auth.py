import os
import time
import requests

# Global variables to store token information
_auth_token = None
_refresh_token = None
_token_expiry = 0

def get_alai_auth_token():
    """
    Get Alai authentication token using the correct Supabase API endpoint
    Returns the access token and stores the refresh token for future use
    """
    global _auth_token, _refresh_token, _token_expiry

    # Check if we have a valid token that's not expired
    current_time = int(time.time())
    if _auth_token and _token_expiry > current_time + 300:  # 5 minutes buffer
        return _auth_token

    # If we have a refresh token, try to use it first
    if _refresh_token:
        try:
            return refresh_auth_token()
        except Exception as e:
            print(f"Refresh token failed: {str(e)}. Falling back to password auth.")

    # Otherwise, authenticate with email/password
    alai_email = os.getenv("ALAI_EMAIL")
    alai_password = os.getenv("ALAI_PASSWORD")

    if not alai_email or not alai_password:
        raise ValueError("ALAI_EMAIL or ALAI_PASSWORD not found in environment variables")

    auth_url = "https://api.getalai.com/auth/v1/token?grant_type=password"

    api_key = os.getenv("ALAI_API_KEY")

    headers = {
        "accept": "*/*",
        "accept-language": "en",
        "apikey": api_key,
        "authorization": "Bearer " + api_key,
        "content-type": "application/json;charset=UTF-8",
        "x-client-info": "supabase-js-web/2.45.4",
        "x-supabase-api-version": "2024-01-01"
    }

    payload = {
        "email": alai_email,
        "password": alai_password
    }

    response = requests.post(auth_url, headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception(f"Alai authentication error: {response.status_code}, {response.text}")

    data = response.json()

    # Store tokens and expiry time
    _auth_token = data.get("access_token")
    _refresh_token = data.get("refresh_token")
    _token_expiry = int(time.time()) + data.get("expires_in", 3600)  # Default to 1 hour if not provided

    return _auth_token

def refresh_auth_token():
    """
    Refresh the authentication token using the stored refresh token
    """
    global _auth_token, _refresh_token, _token_expiry

    if not _refresh_token:
        raise ValueError("No refresh token available")

    auth_url = "https://api.getalai.com/auth/v1/token?grant_type=refresh_token"
    api_key = os.getenv("ALAI_API_KEY")

    headers = {
        "accept": "*/*",
        "accept-language": "en",
        "apikey": api_key,
        "authorization": "Bearer " + api_key,
        "content-type": "application/json;charset=UTF-8",
        "x-client-info": "supabase-js-web/2.45.4",
        "x-supabase-api-version": "2024-01-01"
    }

    payload = {
        "refresh_token": _refresh_token
    }

    response = requests.post(auth_url, headers=headers, json=payload)

    if response.status_code != 200:
        # Clear the refresh token if it's invalid
        _refresh_token = None
        raise Exception(f"Refresh token error: {response.status_code}, {response.text}")

    data = response.json()

    # Update tokens and expiry time
    _auth_token = data.get("access_token")
    _refresh_token = data.get("refresh_token")  # Get the new refresh token
    _token_expiry = int(time.time()) + data.get("expires_in", 3600)  # Default to 1 hour if not provided

    return _auth_token

def ensure_valid_token(token):
    """
    Ensure we have a valid token before making API calls
    """
    global _token_expiry

    # Check if token is about to expire (within 5 minutes)
    current_time = int(time.time())
    if _token_expiry <= current_time + 300:  # 5 minutes buffer
        # Get a fresh token
        return get_alai_auth_token()

    return token
"""
Diagnostic script to test backend connectivity to Spotify Web API & OAuth endpoints.
"""

import requests
from echosense.config import settings

def test_spotify():
    print("🔍 Testing EchoSense -> Spotify Backend Connectivity...\n")
    
    # 1. Test Spotify Accounts API Reachability
    accounts_url = "https://accounts.spotify.com/authorize"
    params = {
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "scope": "user-top-read"
    }
    
    try:
        res = requests.get(accounts_url, params=params, timeout=10)
        print(f"1. Spotify Accounts Authorize Endpoint Status: {res.status_code}")
        if res.status_code in [200, 302, 303]:
            print("   ✅ Spotify OAuth Accounts service is reachable and responsive.")
        else:
            print(f"   ⚠️ Spotify returned status {res.status_code}")
    except Exception as e:
        print(f"   ❌ Failed to connect to Spotify Accounts API: {e}")

    # 2. Test Spotify Web API Reachability
    api_url = "https://api.spotify.com/v1/"
    try:
        res = requests.get(api_url, timeout=10)
        print(f"\n2. Spotify Web API Endpoint Status: {res.status_code}")
        if res.status_code in [200, 401]:  # 401 is expected without token
            print("   ✅ Spotify Web API endpoint is online and reachable.")
        else:
            print(f"   ⚠️ Spotify Web API returned status {res.status_code}")
    except Exception as e:
        print(f"   ❌ Failed to connect to Spotify Web API: {e}")

    # 3. Check Current Config Credentials
    print("\n3. Current EchoSense Spotify Configuration:")
    print(f"   - Client ID: {settings.SPOTIFY_CLIENT_ID}")
    print(f"   - Redirect URI: {settings.SPOTIFY_REDIRECT_URI}")
    has_secret = bool(settings.SPOTIFY_CLIENT_SECRET) and not settings.SPOTIFY_CLIENT_SECRET.startswith("mock_")
    print(f"   - Client Secret Configured: {has_secret}")

if __name__ == "__main__":
    test_spotify()

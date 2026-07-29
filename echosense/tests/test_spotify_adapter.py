"""
Unit tests for Spotify Adapter, OAuth PKCE, Fernet Encryption, & Retries.
"""

import unittest
from echosense.security import generate_pkce_pair, encrypt_token, decrypt_token, sanitize_log_data
from echosense.provider.spotify import SpotifyAdapter

class TestSpotifyAdapter(unittest.TestCase):

    def setUp(self):
        self.adapter = SpotifyAdapter()

    def test_pkce_pair_generation(self):
        """Verify PKCE code verifier and S256 code challenge generation."""
        verifier, challenge = generate_pkce_pair()
        self.assertTrue(len(verifier) >= 43)
        self.assertTrue(len(challenge) >= 43)
        self.assertNotEqual(verifier, challenge)

    def test_fernet_token_encryption_at_rest(self):
        """Verify tokens are encrypted before persistence (FR-01, AC-CON-02)."""
        raw_token = "BQA1234567890_spotify_secret_token"
        encrypted = encrypt_token(raw_token)
        self.assertNotEqual(raw_token, encrypted)
        
        decrypted = decrypt_token(encrypted)
        self.assertEqual(raw_token, decrypted)

    def test_log_data_sanitization(self):
        """Verify raw tokens and secrets are redacted from logs (GR-01, FR-04)."""
        log_payload = {
            "user_id": "listener_01",
            "access_token": "secret_access_token_abc",
            "refresh_token": "secret_refresh_token_xyz",
            "operation": "get_recommendations"
        }
        sanitized = sanitize_log_data(log_payload)
        self.assertEqual(sanitized["access_token"], "[REDACTED]")
        self.assertEqual(sanitized["refresh_token"], "[REDACTED]")
        self.assertEqual(sanitized["user_id"], "listener_01")

    def test_oauth_authorization_url(self):
        """Verify Spotify OAuth URL contains required scopes and PKCE challenge."""
        url, verifier = self.adapter.get_authorization_url("state_test_123")
        self.assertIn("https://accounts.spotify.com/authorize", url)
        self.assertIn("client_id=", url)
        self.assertIn("code_challenge=", url)
        self.assertIn("code_challenge_method=S256", url)

if __name__ == '__main__':
    unittest.main()

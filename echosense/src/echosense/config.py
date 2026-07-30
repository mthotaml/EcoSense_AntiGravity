"""
EchoSense Configuration & Security Settings
"""

import os
from cryptography.fernet import Fernet

class Settings:
    PROJECT_NAME: str = "EchoSense"
    VERSION: str = "1.0.0"
    
    DATABASE_URL: str = os.getenv("ECHOSENSE_DATABASE_URL", "sqlite:///./echosense.db")
    
    # Encryption key for Spotify OAuth tokens at rest
    ENCRYPTION_KEY: str = os.getenv("ECHOSENSE_TOKEN_ENCRYPTION_KEY", Fernet.generate_key().decode())
    
    # Spotify OAuth credentials
    SPOTIFY_CLIENT_ID: str = os.getenv("SPOTIFY_CLIENT_ID", "0e8cdc56698447498f5f855450f62a8d")
    SPOTIFY_CLIENT_SECRET: str = os.getenv("SPOTIFY_CLIENT_SECRET", "mock_spotify_client_secret_echosense")
    SPOTIFY_REDIRECT_URI: str = os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8001/auth/spotify/callback")
    SPOTIFY_SCOPES: str = os.getenv(
        "SPOTIFY_SCOPES",
        "user-top-read user-read-recently-played user-read-email user-read-private streaming user-read-playback-state user-modify-playback-state user-library-read user-library-modify playlist-read-private playlist-read-collaborative"
    )

    # Ranking & Contextual policy boundaries
    MAX_CONTEXT_INFLUENCE_PCT: float = 0.35  # Capped at 35% of pre-diversity score
    DNA_FLOOR_THRESHOLD: float = 0.20        # Candidate must pass DNA floor
    ARTIST_FATIGUE_CAP: int = 2              # Max 2 tracks per artist in Autopilot preview

settings = Settings()

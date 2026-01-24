import os
import sys
import logging
from pathlib import Path
from typing import List, Optional

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
except ImportError:
    print("Required packages not installed.")
    sys.exit(1)

logger = logging.getLogger("GoogleAuth")

def get_gmail_service(
    credentials_file: Path,
    token_file: Path,
    scopes: List[str]
):
    """Authenticate and return Gmail API service."""
    creds = None

    # Load existing token
    if token_file.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_file), scopes)
        except Exception as e:
            logger.warning(f"Error loading token: {e}")

    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Refreshing expired credentials...")
            try:
                creds.refresh(Request())
            except Exception as e:
                logger.warning(f"Failed to refresh token: {e}")
                creds = None
        
        if not creds:
            if not credentials_file.exists():
                raise FileNotFoundError(f"credentials.json not found at {credentials_file}")

            logger.info("Starting OAuth flow...")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_file), scopes
            )
            creds = flow.run_local_server(port=0)

        # Save credentials
        with open(token_file, "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)

def get_calendar_service(
    credentials_file: Path,
    token_file: Path,
    scopes: List[str]
):
    """Authenticate and return Google Calendar API service."""
    creds = None

    # Load existing token
    if token_file.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_file), scopes)
        except Exception as e:
            logger.warning(f"Error loading token: {e}")

    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Refreshing expired credentials...")
            try:
                creds.refresh(Request())
            except Exception as e:
                logger.warning(f"Failed to refresh token: {e}")
                creds = None
        
        if not creds:
            if not credentials_file.exists():
                raise FileNotFoundError(f"credentials.json not found at {credentials_file}")

            logger.info("Starting OAuth flow...")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_file), scopes
            )
            creds = flow.run_local_server(port=0)

        # Save credentials
        with open(token_file, "w") as token:
            token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)

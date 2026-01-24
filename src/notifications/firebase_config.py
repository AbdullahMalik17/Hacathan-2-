import firebase_admin
from firebase_admin import credentials
from pathlib import Path
import logging
import os
import json

logger = logging.getLogger(__name__)

_firebase_initialized = False

def init_firebase():
    """
    Initialize Firebase Admin SDK.

    Supports credentials from:
    1. FIREBASE_SERVICE_ACCOUNT env var (JSON string) - for cloud deployment
    2. config/firebase-service-account.json file - for local development
    """
    global _firebase_initialized
    if _firebase_initialized:
        return True

    cred = None

    # Method 1: Environment variable (for Fly.io/cloud deployment)
    firebase_json = os.getenv("FIREBASE_SERVICE_ACCOUNT")
    if firebase_json:
        try:
            service_account_info = json.loads(firebase_json)
            cred = credentials.Certificate(service_account_info)
            logger.info("Firebase credentials loaded from environment variable")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid FIREBASE_SERVICE_ACCOUNT JSON: {e}")

    # Method 2: File path from environment variable
    if not cred:
        firebase_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
        if firebase_path and Path(firebase_path).exists():
            cred = credentials.Certificate(firebase_path)
            logger.info(f"Firebase credentials loaded from {firebase_path}")

    # Method 3: Default file locations
    if not cred:
        for path in ["config/firebase-service-account.json", "firebase-service-account.json"]:
            if Path(path).exists():
                cred = credentials.Certificate(path)
                logger.info(f"Firebase credentials loaded from {path}")
                break

    if not cred:
        logger.warning("Firebase credentials not found. FCM disabled.")
        logger.info("Set FIREBASE_SERVICE_ACCOUNT env var or add config/firebase-service-account.json")
        return False

    try:
        # Check if app is already initialized
        try:
            firebase_admin.get_app()
            _firebase_initialized = True
        except ValueError:
            firebase_admin.initialize_app(cred)
            _firebase_initialized = True

        logger.info("Firebase Admin SDK initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Firebase init failed: {e}")
        return False

#!/usr/bin/env python3
"""
Simple runner for the API server.
Run with: python run_api.py
"""

import sys
import os
from pathlib import Path

# Add src to Python path
PROJECT_ROOT = Path(__file__).parent
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))
sys.path.insert(0, str(PROJECT_ROOT))

# Set working directory
os.chdir(SRC_DIR)

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("API_PORT", 8000))

    print("=" * 50)
    print("Abdullah Junior API Server")
    print("=" * 50)
    print(f"Starting on http://localhost:{port}")
    print("Press Ctrl+C to stop")
    print("=" * 50)

    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )

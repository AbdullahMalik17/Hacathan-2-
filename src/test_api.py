#!/usr/bin/env python3
"""
Test script to call the API and see the actual error.
"""

import requests
import traceback

def test_api():
    try:
        print("Testing /api/tasks endpoint...")
        response = requests.get("http://localhost:8000/api/tasks?folder=Needs_Action&limit=1")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error calling API: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_api()
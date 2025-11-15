#!/usr/bin/env python3
"""
Test script to ingest Canvas submissions from a specific assignment.
Usage: python test_canvas_ingest.py
"""

import requests
import json
from dotenv import load_dotenv
import os
load_dotenv()
# Canvas credentials and assignment info
CANVAS_BASE_URL = "https://canvas.its.virginia.edu"
API_TOKEN = os.getenv("CANVAS_API_TOKEN")
COURSE_ID = 175906
ASSIGNMENT_ID = 790778

# FastAPI endpoint (assumes server running locally)
API_ENDPOINT = "http://127.0.0.1:8000/canvas/submissions/ingest"

def test_ingest():
    """Test the Canvas submissions ingest endpoint."""
    
    payload = {
        "canvas_base_url": CANVAS_BASE_URL,
        "api_token": API_TOKEN,
        "course_id": COURSE_ID,
        "assignment_id": ASSIGNMENT_ID
        # Optional: "student_id": 12345  # to ingest only one student
    }
    
    print(f"Testing Canvas ingestion for assignment {ASSIGNMENT_ID}...")
    print(f"Endpoint: {API_ENDPOINT}")
    print(f"Payload: {json.dumps({**payload, 'api_token': '***REDACTED***'}, indent=2)}")
    print("\nSending request...\n")
    
    try:
        response = requests.post(
            API_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120  # 2 minute timeout for large downloads
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}\n")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"\nIngested {len(result.get('ingested', []))} submission(s):\n")
            
            for idx, sub in enumerate(result.get('ingested', []), 1):
                print(f"  {idx}. Student ID: {sub.get('student_id')}")
                print(f"     Student Name: {sub.get('student_name')}")
                print(f"     DB Record ID: {sub.get('submission_db_id')}")
                print(f"     Files: {len([f for f in sub.get('files', []) if isinstance(f, str)])}")
                
                # Show file paths
                for file_path in sub.get('files', []):
                    if isinstance(file_path, str):
                        print(f"       - {file_path}")
                    else:
                        print(f"       - ERROR: {file_path}")
                print()
        else:
            print("❌ ERROR!")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR!")
        print("Make sure the FastAPI server is running:")
        print("  uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")

if __name__ == "__main__":
    test_ingest()
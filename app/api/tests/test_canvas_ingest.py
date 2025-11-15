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
            
            # Display rubric information if available
            if result.get('rubric'):
                print("=" * 60)
                print("ASSIGNMENT & RUBRIC INFORMATION:")
                print("=" * 60)
                
                # Display assignment information
                assignment_info = result.get('assignment_info', {})
                print(f"\nAssignment:")
                print(f"  Name: {assignment_info.get('name', 'N/A')}")
                print(f"  ID: {assignment_info.get('id', 'N/A')}")
                print(f"  Points Possible: {assignment_info.get('points_possible', 'N/A')}")
                print(f"  Due Date: {assignment_info.get('due_at', 'N/A')}")
                if assignment_info.get('description'):
                    import re
                    description = re.sub('<[^<]+?>', '', assignment_info.get('description', ''))
                    print(f"\n  Assignment Text:\n{description}")
                
                # Display rubric settings
                rubric_settings = result.get('rubric_settings', {})
                print(f"\nRubric:")
                print(f"  Title: {rubric_settings.get('title', 'N/A')}")
                print(f"  Points Possible: {rubric_settings.get('points_possible', 'N/A')}")
                print(f"  ID: {rubric_settings.get('id', 'N/A')}")
                print(f"\nCriteria:")
                for criterion in result.get('rubric', []):
                    print(f"\n  • {criterion.get('description', 'N/A')} ({criterion.get('points', 0)} points)")
                    if criterion.get('long_description'):
                        print(f"    Description: {criterion.get('long_description')}")
                    print(f"    Ratings:")
                    for rating in criterion.get('ratings', []):
                        print(f"      - {rating.get('description', 'N/A')}: {rating.get('points', 0)} points")
                print("\n" + "=" * 60 + "\n")
            
            # Save rubric to text file if available
            if result.get('rubric'):
                rubric_file = f"data/submissions/{ASSIGNMENT_ID}/rubric.txt"
                os.makedirs(os.path.dirname(rubric_file), exist_ok=True)
                with open(rubric_file, 'w') as f:
                    f.write("ASSIGNMENT & RUBRIC\n")
                    f.write("=" * 60 + "\n\n")
                    
                    # Write assignment information
                    assignment_info = result.get('assignment_info', {})
                    f.write("ASSIGNMENT:\n")
                    f.write("-" * 60 + "\n")
                    f.write(f"Name: {assignment_info.get('name', 'N/A')}\n")
                    f.write(f"ID: {assignment_info.get('id', 'N/A')}\n")
                    f.write(f"Points Possible: {assignment_info.get('points_possible', 'N/A')}\n")
                    f.write(f"Due Date: {assignment_info.get('due_at', 'N/A')}\n")
                    
                    # Write assignment text/description
                    if assignment_info.get('description'):
                        import re
                        description = re.sub('<[^<]+?>', '', assignment_info.get('description', ''))
                        f.write(f"\nAssignment Text:\n{description}\n")
                    
                    # Write rubric settings
                    f.write("\n" + "=" * 60 + "\n\n")
                    rubric_settings = result.get('rubric_settings', {})
                    f.write("RUBRIC:\n")
                    f.write("-" * 60 + "\n")
                    f.write(f"Title: {rubric_settings.get('title', 'N/A')}\n")
                    f.write(f"Points Possible: {rubric_settings.get('points_possible', 'N/A')}\n")
                    f.write(f"ID: {rubric_settings.get('id', 'N/A')}\n\n")
                    f.write("CRITERIA:\n")
                    f.write("-" * 60 + "\n\n")
                    for criterion in result.get('rubric', []):
                        f.write(f"{criterion.get('description', 'N/A')} ({criterion.get('points', 0)} points)\n")
                        if criterion.get('long_description'):
                            f.write(f"Description: {criterion.get('long_description')}\n")
                        f.write(f"\nRatings:\n")
                        for rating in criterion.get('ratings', []):
                            f.write(f"  • {rating.get('description', 'N/A')}: {rating.get('points', 0)} points\n")
                            if rating.get('long_description'):
                                f.write(f"    {rating.get('long_description')}\n")
                        f.write("\n")
                print(f"✅ Rubric saved to: {rubric_file}\n")
            
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
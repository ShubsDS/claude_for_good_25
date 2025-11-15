"""
Test script to demonstrate the essay grading pipeline.

This script shows how to:
1. Upload an essay
2. Upload a rubric
3. Grade the essay
4. Retrieve grading results with highlights
"""

import requests
import json
import os
from dotenv import load_dotenv

BASE_URL = "http://localhost:8000"


def test_grading_pipeline():
    """Test the complete essay grading pipeline."""

    print("=" * 70)
    print("Essay Grading Pipeline Test")
    print("=" * 70)

    # Step 1: Upload essay
    print("\n1. Uploading essay...")
    essay_path = "example_essays/essay.txt"

    with open(essay_path, 'rb') as f:
        files = {'file': (os.path.basename(essay_path), f, 'text/plain')}
        response = requests.post(f"{BASE_URL}/essays/", files=files)

    if response.status_code != 200:
        print(f"Error uploading essay: {response.text}")
        return

    essay_data = response.json()
    essay_id = essay_data['id']
    print(f"✓ Essay uploaded successfully (ID: {essay_id})")
    print(f"  Filename: {essay_data['filename']}")
    print(f"  Content length: {len(essay_data['content'])} characters")

    # Step 2: Upload rubric
    print("\n2. Uploading rubric...")
    rubric_path = "example_rubrics/sample_rubric.txt"

    with open(rubric_path, 'rb') as f:
        files = {'file': (os.path.basename(rubric_path), f, 'text/plain')}
        response = requests.post(f"{BASE_URL}/rubrics/", files=files)

    if response.status_code != 200:
        print(f"Error uploading rubric: {response.text}")
        return

    rubric_data = response.json()
    rubric_id = rubric_data['id']
    print(f"✓ Rubric uploaded successfully (ID: {rubric_id})")
    print(f"  Name: {rubric_data['name']}")
    print(f"  Criteria found: {list(rubric_data['criteria'].keys())}")

    # Step 3: Grade the essay
    print("\n3. Grading essay (this may take a moment)...")
    response = requests.post(
        f"{BASE_URL}/grade",
        data={'essay_id': essay_id, 'rubric_id': rubric_id}
    )

    if response.status_code != 200:
        print(f"Error grading essay: {response.text}")
        return

    grading_data = response.json()
    grading_id = grading_data['id']
    print(f"✓ Essay graded successfully (ID: {grading_id})")
    print(f"  Total score: {grading_data['total_score']:.1f}/10")

    # Step 4: Display results with highlights
    print("\n4. Grading Results:")
    print("=" * 70)

    results = grading_data['results']

    if 'overall_feedback' in results:
        print(f"\nOverall Feedback: {results['overall_feedback']}")

    print("\nDetailed Scores by Criterion:")
    print("-" * 70)

    for criterion_result in results.get('criteria_results', []):
        criterion = criterion_result['criterion']
        score = criterion_result['score']
        feedback = criterion_result['feedback']
        highlights = criterion_result.get('highlights', [])

        print(f"\n{criterion}: {score}/10")
        print(f"Feedback: {feedback}")

        if highlights:
            print(f"Highlighted text ({len(highlights)} section(s)):")
            for i, highlight in enumerate(highlights, 1):
                text = highlight['text']
                start = highlight.get('start', -1)
                end = highlight.get('end', -1)

                # Truncate long text for display
                display_text = text[:100] + "..." if len(text) > 100 else text

                if start >= 0:
                    print(f"  [{i}] Position {start}-{end}: \"{display_text}\"")
                else:
                    print(f"  [{i}] (Not found in essay): \"{display_text}\"")

    # Step 5: Show how UI would use this data
    print("\n" + "=" * 70)
    print("How the UI would use this data:")
    print("=" * 70)
    print("""
The frontend would:
1. Fetch the essay content from GET /essays/{essay_id}
2. Fetch the grading results from GET /gradings/{grading_id}
3. For each criterion in the results:
   - Display the score and feedback
   - Use the 'start' and 'end' positions to wrap text in highlight elements
   - Color-code highlights by criterion (e.g., THESIS=blue, CITATIONS=green)

Example JavaScript pseudocode:
    const essay = await fetch('/essays/1').then(r => r.json());
    const grading = await fetch('/gradings/1').then(r => r.json());

    // For each criterion's highlights
    grading.results.criteria_results.forEach(criterion => {
        criterion.highlights.forEach(highlight => {
            const start = highlight.start;
            const end = highlight.end;
            const color = getCriterionColor(criterion.criterion);

            // Wrap text from position [start:end] in a <mark> element
            wrapTextInHighlight(essay.content, start, end, color);
        });
    });
    """)

    print("\n" + "=" * 70)
    print("Test completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    # Check if server is running
    load_dotenv()
    try:
        response = requests.get(f"{BASE_URL}/ping")
        if response.status_code != 200:
            print("Error: Server is not responding properly")
            exit(1)
    except requests.exceptions.ConnectionError:
        print("Error: Server is not running!")
        print("Please start the server with: uvicorn app.main:app --reload")
        exit(1)

    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Warning: ANTHROPIC_API_KEY environment variable not set")
        print("Please set it before running this test:")
        print("  export ANTHROPIC_API_KEY='your-api-key'  (Linux/Mac)")
        print("  set ANTHROPIC_API_KEY=your-api-key      (Windows)")
        exit(1)

    test_grading_pipeline()

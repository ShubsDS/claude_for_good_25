"""
Test script to demonstrate fuzzy matching capabilities.

This shows how the system handles LLM citations that aren't exact matches.
"""

from app.essay_grader import EssayGrader


def test_fuzzy_matching():
    """Test the fuzzy matching functionality with various scenarios."""

    grader = EssayGrader(api_key="dummy")  # We won't actually call the API

    essay_text = """
    This essay demonstrates the importance of structured writing and proper citation formatting.
    Research shows that citations improve credibility (Smith, 2019).

    Good essays also have clear structure with well-organized paragraphs.
    """

    print("=" * 70)
    print("Fuzzy Matching Test Cases")
    print("=" * 70)

    # Test Case 1: Exact match
    print("\n1. EXACT MATCH")
    quoted = "This essay demonstrates the importance of structured writing"
    start, end, found = grader._find_text_position(essay_text, quoted)
    print(f"   Quoted: '{quoted}'")
    print(f"   Found:  '{found}'")
    print(f"   Position: {start}-{end}")
    print(f"   Status: {'[OK] FOUND' if start != -1 else '[X] NOT FOUND'}")

    # Test Case 2: Extra whitespace
    print("\n2. WHITESPACE VARIATION")
    quoted = "This essay  demonstrates   the importance"  # Extra spaces
    start, end, found = grader._find_text_position(essay_text, quoted)
    print(f"   Quoted: '{quoted}'")
    print(f"   Found:  '{found}'")
    print(f"   Position: {start}-{end}")
    print(f"   Status: {'[OK] FOUND (normalized)' if start != -1 else '[X] NOT FOUND'}")

    # Test Case 3: Case variation (handled by fuzzy)
    print("\n3. CASE VARIATION")
    quoted = "research shows that citations improve credibility"
    start, end, found = grader._find_text_position(essay_text, quoted)
    print(f"   Quoted: '{quoted}'")
    print(f"   Found:  '{found}'")
    print(f"   Position: {start}-{end}")
    print(f"   Status: {'[OK] FOUND (fuzzy)' if start != -1 else '[X] NOT FOUND'}")

    # Test Case 4: Slight paraphrase (should still match with fuzzy)
    print("\n4. SIMILAR TEXT (FUZZY)")
    quoted = "research demonstrates citations improve credibility"
    start, end, found = grader._find_text_position(essay_text, quoted)
    print(f"   Quoted: '{quoted}'")
    print(f"   Found:  '{found}'")
    print(f"   Position: {start}-{end}")
    print(f"   Status: {'[OK] FOUND (fuzzy match)' if start != -1 else '[X] NOT FOUND'}")

    # Test Case 5: Citation format
    print("\n5. CITATION")
    quoted = "(Smith, 2019)"
    start, end, found = grader._find_text_position(essay_text, quoted)
    print(f"   Quoted: '{quoted}'")
    print(f"   Found:  '{found}'")
    print(f"   Position: {start}-{end}")
    print(f"   Status: {'[OK] FOUND' if start != -1 else '[X] NOT FOUND'}")

    # Test Case 6: Completely different text
    print("\n6. NO MATCH (DIFFERENT TEXT)")
    quoted = "This text does not exist in the essay at all"
    start, end, found = grader._find_text_position(essay_text, quoted)
    print(f"   Quoted: '{quoted}'")
    print(f"   Found:  '{found}'")
    print(f"   Position: {start}-{end}")
    print(f"   Status: {'[OK] FOUND' if start != -1 else '[X] NOT FOUND (expected)'}")

    print("\n" + "=" * 70)
    print("Fuzzy Matching Test Complete!")
    print("=" * 70)
    print("\nKey Takeaways:")
    print("- Exact matches are found instantly")
    print("- Whitespace variations are normalized and matched")
    print("- Case differences are handled by fuzzy matching")
    print("- Similar text can be matched with high confidence")
    print("- Completely different text is correctly rejected")


if __name__ == "__main__":
    test_fuzzy_matching()

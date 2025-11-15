import json
import re
from typing import Dict, List, Any, Tuple
from anthropic import Anthropic
from rapidfuzz import fuzz
import os


class EssayGrader:
    """Service for grading essays using Claude AI with text highlighting."""

    def __init__(self, api_key: str = None):
        """Initialize the grader with Anthropic API key."""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable must be set")
        self.client = Anthropic(api_key=self.api_key)

    def parse_rubric(self, rubric_text: str) -> Dict[str, str]:
        """
        Parse rubric text into structured criteria.

        Args:
            rubric_text: Raw rubric text content

        Returns:
            Dictionary mapping criterion IDs to descriptions
        """
        criteria = {}
        lines = rubric_text.strip().split('\n')

        for line in lines:
            line = line.strip()
            # Look for lines starting with criterion ID (e.g., "THESIS:")
            if ':' in line and line.split(':')[0].isupper():
                parts = line.split(':', 1)
                criterion_id = parts[0].strip()
                description = parts[1].strip()
                criteria[criterion_id] = description

        return criteria

    def grade_essay(self, essay_text: str, rubric_text: str) -> Dict[str, Any]:
        """
        Grade an essay based on a rubric and identify relevant text spans.

        Args:
            essay_text: The essay content to grade
            rubric_text: The rubric text with grading criteria

        Returns:
            Dictionary with grading results including scores, feedback, and highlights
        """
        criteria = self.parse_rubric(rubric_text)

        # Construct the grading prompt
        prompt = self._build_grading_prompt(essay_text, criteria)

        # Call Claude API
        message = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Parse the response
        response_text = message.content[0].text
        grading_results = self._parse_grading_response(response_text, essay_text)

        return grading_results

    def _build_grading_prompt(self, essay_text: str, criteria: Dict[str, str]) -> str:
        """Build the prompt for Claude to grade the essay."""
        criteria_list = "\n".join([f"- {key}: {desc}" for key, desc in criteria.items()])

        prompt = f"""You are an expert essay grader. Please grade the following essay based on the provided rubric criteria.

ESSAY:
{essay_text}

RUBRIC CRITERIA:
{criteria_list}

For each criterion, you must:
1. Provide a score from 0-10
2. Write brief feedback explaining the score
3. Identify specific text spans in the essay that are relevant to this criterion (provide the EXACT text as it appears in the essay)

IMPORTANT: For the text spans, you must quote the EXACT text from the essay, word-for-word. This is critical for highlighting.

CRITICAL JSON FORMATTING RULES:
- When quoting text that contains quotation marks, replace them with single quotes or remove them to avoid JSON parsing errors
- For example: Instead of "He said \"hello\"" use "He said 'hello'" or "He said hello"
- Make absolutely sure the JSON is valid and parseable - no unescaped quotes in text fields

Please respond in the following JSON format:
{{
  "criteria_results": [
    {{
      "criterion": "CRITERION_ID",
      "score": 8,
      "feedback": "Brief explanation of the score",
      "highlights": [
        {{
          "text": "exact text from essay that is relevant"
        }}
      ]
    }}
  ],
  "total_score": 75.5,
  "overall_feedback": "General comments about the essay"
}}

Respond ONLY with valid JSON, no additional text."""

        return prompt

    def _find_text_position(self, essay_text: str, quoted_text: str, threshold: int = 75) -> Tuple[int, int, str]:
        """
        Find the position of quoted text in the essay using exact and fuzzy matching.

        Args:
            essay_text: The full essay text
            quoted_text: The text to find (from LLM response)
            threshold: Minimum similarity score for fuzzy matching (0-100)

        Returns:
            Tuple of (start_position, end_position, actual_text_found)
            Returns (-1, -1, quoted_text) if no match found
        """
        # Step 1: Try exact match
        start_pos = essay_text.find(quoted_text)
        if start_pos != -1:
            return (start_pos, start_pos + len(quoted_text), quoted_text)

        # Step 2: Try with normalized whitespace
        normalized_quote = ' '.join(quoted_text.split())
        normalized_essay = ' '.join(essay_text.split())

        start_pos = normalized_essay.find(normalized_quote)
        if start_pos != -1:
            # Map back to original essay position
            # Count non-whitespace chars to find position in original
            original_pos = self._map_normalized_position(essay_text, normalized_essay, start_pos)
            if original_pos != -1:
                # Find the actual text in the original essay
                actual_text = essay_text[original_pos:original_pos + len(normalized_quote)]
                return (original_pos, original_pos + len(actual_text), actual_text)

        # Step 3: Fuzzy matching with sliding window
        quote_len = len(quoted_text)
        best_score = 0
        best_start = -1
        best_text = quoted_text

        # Use a sliding window approach
        window_size = min(len(quoted_text) + 50, len(essay_text))  # Allow some length variance
        step_size = max(1, quote_len // 4)  # Overlap windows for better coverage

        for i in range(0, len(essay_text) - quote_len + 1, step_size):
            # Try windows of varying sizes around the expected length
            for window_len in [quote_len, int(quote_len * 0.8), int(quote_len * 1.2)]:
                if i + window_len > len(essay_text):
                    continue

                window = essay_text[i:i + window_len]
                score = fuzz.ratio(quoted_text.lower(), window.lower())

                if score > best_score:
                    best_score = score
                    best_start = i
                    best_text = window

        # Accept match if above threshold
        if best_score >= threshold:
            return (best_start, best_start + len(best_text), best_text)

        # Step 4: No good match found
        return (-1, -1, quoted_text)

    def _map_normalized_position(self, original: str, normalized: str, norm_pos: int) -> int:
        """Map a position in normalized text back to original text position."""
        # This is a simplified mapping - count non-whitespace characters
        char_count = 0
        for i, char in enumerate(original):
            if not char.isspace():
                if char_count == norm_pos:
                    return i
                char_count += 1
        return -1

    def _parse_grading_response(self, response_text: str, essay_text: str) -> Dict[str, Any]:
        """Parse Claude's response and add character positions for highlights using fuzzy matching."""
        # Extract JSON from response
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group()

            # Normalize curly quotes to straight quotes for JSON parsing
            response_text = response_text.replace('"', '"').replace('"', '"').replace(''', "'").replace(''', "'")

            grading_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse grading response as JSON: {e}\nResponse: {response_text}")

        # Add character positions to highlights using fuzzy matching
        for criterion_result in grading_data.get("criteria_results", []):
            for highlight in criterion_result.get("highlights", []):
                quoted_text = highlight["text"]

                # Use fuzzy matching to find the text
                start_pos, end_pos, actual_text = self._find_text_position(essay_text, quoted_text)

                # Update highlight with positions and actual matched text
                highlight["start"] = start_pos
                highlight["end"] = end_pos
                highlight["text"] = actual_text  # Update to actual matched text

                # Add note only if not found
                if start_pos == -1:
                    highlight["note"] = "Text not found in essay (fuzzy match failed)"

        return grading_data

    def calculate_total_score(self, grading_results: Dict[str, Any]) -> float:
        """Calculate the total score from individual criterion scores."""
        scores = [cr["score"] for cr in grading_results.get("criteria_results", [])]
        if not scores:
            return 0.0
        return sum(scores) / len(scores)

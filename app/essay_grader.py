import json
import re
from typing import Dict, List, Any
from anthropic import Anthropic
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

    def _parse_grading_response(self, response_text: str, essay_text: str) -> Dict[str, Any]:
        """Parse Claude's response and add character positions for highlights."""
        # Extract JSON from response
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group()

            grading_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse grading response as JSON: {e}\nResponse: {response_text}")

        # Add character positions to highlights
        for criterion_result in grading_data.get("criteria_results", []):
            for highlight in criterion_result.get("highlights", []):
                text = highlight["text"]
                # Find the position of this text in the essay
                start_pos = essay_text.find(text)
                if start_pos != -1:
                    highlight["start"] = start_pos
                    highlight["end"] = start_pos + len(text)
                else:
                    # If exact match not found, mark as not found
                    highlight["start"] = -1
                    highlight["end"] = -1
                    highlight["note"] = "Exact text not found in essay"

        return grading_data

    def calculate_total_score(self, grading_results: Dict[str, Any]) -> float:
        """Calculate the total score from individual criterion scores."""
        scores = [cr["score"] for cr in grading_results.get("criteria_results", [])]
        if not scores:
            return 0.0
        return sum(scores) / len(scores)

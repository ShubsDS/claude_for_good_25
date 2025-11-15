# Text Highlighting Logic - Detailed Explanation

## The Problem

You want to show a graded essay in a UI where different parts of the essay are highlighted based on which rubric criterion they relate to. For example:
- The thesis should be highlighted in blue
- Citations should be highlighted in green
- Supporting evidence in yellow
- etc.

**The Challenge**: How does the backend tell the frontend WHICH text to highlight?

## The Solution: Character Positions

Instead of just saying "the thesis is good", the backend says:
> "The thesis is good, and it's located at characters 145-203 in the essay"

Then the frontend can extract `essay_text[145:203]` and wrap it in a highlight.

## Step-by-Step Flow

### Step 1: Essay & Rubric Upload

```
User uploads:
├── essay.txt (the essay to grade)
└── rubric.txt (grading criteria)

Backend stores:
├── Essay in database with ID=1
└── Rubric in database with ID=1
```

### Step 2: Grading Request

```
POST /grade
{
  "essay_id": 1,
  "rubric_id": 1
}
```

### Step 3: Backend Processing

#### 3a. Fetch Data from Database

```python
essay = get_essay(1)
rubric = get_rubric(1)

essay_text = "This essay demonstrates the importance..."
rubric_criteria = {
  "THESIS": "Does the essay have a clear thesis?",
  "CITATIONS": "Are there proper citations?",
  ...
}
```

#### 3b. Build Prompt for Claude

```python
prompt = f"""
You are grading this essay:

{essay_text}

Based on these criteria:
{rubric_criteria}

For each criterion:
1. Give a score 0-10
2. Provide feedback
3. Quote the EXACT text from the essay that relates to this criterion

Respond in JSON format with the exact text quotes.
"""
```

#### 3c. Claude AI Response

Claude analyzes the essay and returns:

```json
{
  "criteria_results": [
    {
      "criterion": "THESIS",
      "score": 8,
      "feedback": "Clear thesis in introduction",
      "highlights": [
        {
          "text": "This essay demonstrates the importance of structured writing"
        }
      ]
    },
    {
      "criterion": "CITATIONS",
      "score": 9,
      "feedback": "Multiple citations present",
      "highlights": [
        { "text": "(Smith, 2019)" },
        { "text": "(Lee & Patel, 2020)" },
        { "text": "(Garcia, 2018)" }
      ]
    }
  ]
}
```

**Key Point**: Claude quotes the EXACT text as it appears in the essay.

#### 3d. Convert Quotes to Positions

Now the backend needs to find WHERE these quotes appear in the essay:

```python
def add_positions(essay_text, grading_results):
    for criterion_result in grading_results["criteria_results"]:
        for highlight in criterion_result["highlights"]:
            quoted_text = highlight["text"]

            # Find where this text appears in the essay
            start_pos = essay_text.find(quoted_text)

            if start_pos != -1:  # Found it!
                highlight["start"] = start_pos
                highlight["end"] = start_pos + len(quoted_text)
            else:  # Not found (Claude paraphrased)
                highlight["start"] = -1
                highlight["end"] = -1
                highlight["note"] = "Exact text not found"

    return grading_results
```

**Example**:

```
Essay text: "This essay demonstrates the importance of structured writing..."
                        ^                                      ^
                      start=5                              end=66

Quoted text: "This essay demonstrates the importance of structured writing"

find() returns: 5
length is: 61
So: start=5, end=66
```

#### 3e. Final Data Structure

```json
{
  "criteria_results": [
    {
      "criterion": "THESIS",
      "score": 8,
      "feedback": "Clear thesis in introduction",
      "highlights": [
        {
          "text": "This essay demonstrates the importance of structured writing",
          "start": 5,
          "end": 66
        }
      ]
    },
    {
      "criterion": "CITATIONS",
      "score": 9,
      "feedback": "Multiple citations present",
      "highlights": [
        { "text": "(Smith, 2019)", "start": 438, "end": 451 },
        { "text": "(Lee & Patel, 2020)", "start": 682, "end": 701 },
        { "text": "(Garcia, 2018)", "start": 945, "end": 959 }
      ]
    }
  ]
}
```

### Step 4: Store in Database

```python
grading = Grading(
    essay_id=1,
    rubric_id=1,
    results=grading_results,  # The full JSON above
    total_score=8.5
)
db.save(grading)
```

### Step 5: Frontend Retrieval

```javascript
// Fetch essay content
const essay = await fetch('/essays/1').then(r => r.json());
// essay.content = "This essay demonstrates..."

// Fetch grading with highlights
const grading = await fetch('/gradings/1').then(r => r.json());
// grading.results = { criteria_results: [...] }
```

### Step 6: Rendering Highlights

#### Visual Example

**Essay text**:
```
"This essay demonstrates the importance of structured writing. Citations like (Smith, 2019) are important."
```

**Highlights to apply**:
```
[
  { criterion: "THESIS", start: 0, end: 61, color: "blue" },
  { criterion: "CITATIONS", start: 79, end: 92, color: "green" }
]
```

**Rendering algorithm**:

```javascript
function renderWithHighlights(essayText, highlights) {
    let html = '';
    let position = 0;

    // Sort highlights by start position
    highlights.sort((a, b) => a.start - b.start);

    for (const highlight of highlights) {
        // Add plain text before highlight
        html += escapeHtml(essayText.slice(position, highlight.start));

        // Add highlighted text
        const highlightedText = essayText.slice(highlight.start, highlight.end);
        html += `<mark style="background: ${highlight.color}">
                   ${escapeHtml(highlightedText)}
                 </mark>`;

        position = highlight.end;
    }

    // Add any remaining text
    html += escapeHtml(essayText.slice(position));

    return html;
}
```

**Result**:

```html
<mark style="background: blue">This essay demonstrates the importance of structured writing</mark>. Citations like <mark style="background: green">(Smith, 2019)</mark> are important.
```

**Rendered**:

<span style="background: lightblue">This essay demonstrates the importance of structured writing</span>. Citations like <span style="background: lightgreen">(Smith, 2019)</span> are important.

## Complete Example with Real Data

### Input Essay

```
A Simple Essay

This essay demonstrates the importance of citations. Research shows that proper citation improves credibility (Smith, 2019).

Good essays also have clear structure. Each paragraph should develop a single idea (Jones, 2020).

In conclusion, essays need both citations and structure.
```

### Claude's Response

```json
{
  "criteria_results": [
    {
      "criterion": "THESIS",
      "score": 7,
      "feedback": "Thesis could be more explicit",
      "highlights": [
        { "text": "This essay demonstrates the importance of citations." }
      ]
    },
    {
      "criterion": "CITATIONS",
      "score": 9,
      "feedback": "Two well-formatted citations",
      "highlights": [
        { "text": "(Smith, 2019)" },
        { "text": "(Jones, 2020)" }
      ]
    }
  ]
}
```

### After Position Mapping

```json
{
  "criteria_results": [
    {
      "criterion": "THESIS",
      "score": 7,
      "feedback": "Thesis could be more explicit",
      "highlights": [
        {
          "text": "This essay demonstrates the importance of citations.",
          "start": 18,
          "end": 70
        }
      ]
    },
    {
      "criterion": "CITATIONS",
      "score": 9,
      "feedback": "Two well-formatted citations",
      "highlights": [
        {
          "text": "(Smith, 2019)",
          "start": 130,
          "end": 143
        },
        {
          "text": "(Jones, 2020)",
          "start": 242,
          "end": 255
        }
      ]
    }
  ]
}
```

### Frontend Rendering

```javascript
// Color map
const colors = {
  'THESIS': '#FFE0B2',
  'CITATIONS': '#C8E6C9'
};

// Build highlight array
const highlights = [];
grading.results.criteria_results.forEach(cr => {
  cr.highlights.forEach(h => {
    if (h.start >= 0) {
      highlights.push({
        start: h.start,
        end: h.end,
        color: colors[cr.criterion],
        criterion: cr.criterion
      });
    }
  });
});

// Render
const html = renderWithHighlights(essay.content, highlights);
document.getElementById('essay').innerHTML = html;
```

### Final Rendered HTML

```html
<div id="essay">
  A Simple Essay

  <mark style="background: #FFE0B2" data-criterion="THESIS">
    This essay demonstrates the importance of citations.
  </mark>
  Research shows that proper citation improves credibility
  <mark style="background: #C8E6C9" data-criterion="CITATIONS">
    (Smith, 2019)
  </mark>.

  Good essays also have clear structure. Each paragraph should develop a single idea
  <mark style="background: #C8E6C9" data-criterion="CITATIONS">
    (Jones, 2020)
  </mark>.

  In conclusion, essays need both citations and structure.
</div>
```

## Why This Approach Works

### ✅ Advantages

1. **Precise**: Exact character positions, no ambiguity
2. **Fast**: No text parsing needed in frontend
3. **Cached**: Highlights stored in database, no recomputation
4. **Flexible**: UI can style highlights however it wants
5. **Auditable**: Full history of what was highlighted and why

### ⚠️ Edge Cases

#### Overlapping Highlights

If two criteria highlight the same text:

```
Option 1: Stack them
<mark class="thesis"><mark class="structure">text</mark></mark>

Option 2: Use first one only
<mark class="thesis">text</mark>

Option 3: Show multiple views
Tab 1: Show thesis highlights
Tab 2: Show structure highlights
```

#### Text Not Found

If Claude paraphrases instead of quoting exactly:

```json
{
  "text": "approximately what was said",
  "start": -1,
  "end": -1,
  "note": "Exact text not found in essay"
}
```

UI can:
- Skip these highlights
- Show them in a separate "suggestions" section
- Use fuzzy matching to find closest match

#### Very Long Essays

For essays > 10,000 words:
- Consider chunking (analyze sections separately)
- Use lazy loading (only render visible highlights)
- Add search/navigation to jump to highlights

## Summary

The highlight logic is simple:

1. **Backend**: Ask AI to quote exact text → Find quotes in essay → Return character positions
2. **Frontend**: Use positions to slice text → Wrap in `<mark>` → Style by criterion

The key insight is that **character positions** (start, end) are a universal, precise way to communicate "highlight this part" from backend to frontend.

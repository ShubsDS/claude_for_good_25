# Essay Grading System with Text Highlighting

## Overview

This system provides an AI-powered essay grading pipeline that:
1. Accepts essays and rubrics as text files
2. Uses Claude AI to grade essays based on rubric criteria
3. Returns structured results with **character-level text positions** for highlighting in the UI

## How It Works

### Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Upload    │      │   Claude AI   │      │   Results   │
│ Essay + Rubric ──▶ │   Grading     │ ──▶ │ with Highlights│
└─────────────┘      └──────────────┘      └─────────────┘
```

### Data Flow

1. **Upload Essay** → Stored in database with ID
2. **Upload Rubric** → Parsed into criteria and stored
3. **Grade Request** → Claude analyzes essay against rubric
4. **AI Response** → Structured JSON with:
   - Scores (0-10) for each criterion
   - Feedback for each criterion
   - **Exact text quotes** from the essay
5. **Text Position Mapping** → Convert quotes to character positions (start, end)
6. **Store Results** → Save to database with all highlight data
7. **UI Retrieval** → Frontend fetches and renders highlights

## Database Models

### Essay
- `id`: Auto-generated ID
- `filename`: Original file name
- `content`: Full essay text
- `created_at`: Timestamp

### Rubric
- `id`: Auto-generated ID
- `name`: Rubric file name
- `content`: Original rubric text
- `criteria`: Parsed criteria (JSON)
- `created_at`: Timestamp

### Grading
- `id`: Auto-generated ID
- `essay_id`: Foreign key to Essay
- `rubric_id`: Foreign key to Rubric
- `results`: Full grading results (JSON) - **includes highlight positions**
- `total_score`: Average score across criteria
- `created_at`: Timestamp

## API Endpoints

### Essay Management
- `POST /essays/` - Upload essay file
- `GET /essays/` - List all essays
- `GET /essays/{id}` - Get specific essay

### Rubric Management
- `POST /rubrics/` - Upload rubric file
- `GET /rubrics/` - List all rubrics
- `GET /rubrics/{id}` - Get specific rubric

### Grading
- `POST /grade` - Grade an essay (requires essay_id and rubric_id)
- `GET /gradings/` - List all gradings
- `GET /gradings/{id}` - Get specific grading with highlight data

## Highlight Data Structure

The grading results include highlight information for each criterion:

```json
{
  "criteria_results": [
    {
      "criterion": "THESIS",
      "score": 8,
      "feedback": "Clear thesis statement present in introduction",
      "highlights": [
        {
          "text": "This essay demonstrates the importance of structure...",
          "start": 145,
          "end": 203
        }
      ]
    },
    {
      "criterion": "CITATIONS",
      "score": 9,
      "feedback": "Multiple well-formatted citations throughout",
      "highlights": [
        {
          "text": "(Smith, 2019)",
          "start": 456,
          "end": 469
        },
        {
          "text": "(Lee & Patel, 2020)",
          "start": 678,
          "end": 697
        }
      ]
    }
  ],
  "total_score": 8.5,
  "overall_feedback": "Well-structured essay with good evidence"
}
```

## How to Use Highlights in the UI

### Step 1: Fetch Data

```javascript
// Get the essay content
const essay = await fetch('/essays/1').then(r => r.json());

// Get the grading with highlights
const grading = await fetch('/gradings/1').then(r => r.json());
```

### Step 2: Render with Highlights

```javascript
// Define colors for each criterion
const criterionColors = {
  'THESIS': '#FFE0B2',        // Orange
  'CITATIONS': '#C8E6C9',     // Green
  'SUPPORTING_EVIDENCE': '#BBDEFB', // Blue
  'STRUCTURE': '#F8BBD0',     // Pink
  'REFERENCES': '#D1C4E9'     // Purple
};

// Build an array of all highlights with metadata
const highlights = [];
grading.results.criteria_results.forEach(criterion => {
  criterion.highlights.forEach(highlight => {
    if (highlight.start >= 0) { // Only valid highlights
      highlights.push({
        start: highlight.start,
        end: highlight.end,
        criterion: criterion.criterion,
        color: criterionColors[criterion.criterion],
        score: criterion.score,
        feedback: criterion.feedback
      });
    }
  });
});

// Sort by position to avoid overlapping issues
highlights.sort((a, b) => a.start - b.start);

// Render the essay with highlights
function renderEssayWithHighlights(essayText, highlights) {
  let result = '';
  let lastIndex = 0;

  highlights.forEach(highlight => {
    // Add text before highlight
    result += escapeHtml(essayText.slice(lastIndex, highlight.start));

    // Add highlighted text
    const highlightedText = essayText.slice(highlight.start, highlight.end);
    result += `<mark
      style="background-color: ${highlight.color};"
      data-criterion="${highlight.criterion}"
      data-score="${highlight.score}"
      title="${highlight.feedback}"
    >${escapeHtml(highlightedText)}</mark>`;

    lastIndex = highlight.end;
  });

  // Add remaining text
  result += escapeHtml(essayText.slice(lastIndex));

  return result;
}
```

### Step 3: Interactive UI

```html
<!-- Display the highlighted essay -->
<div id="essay-display" class="essay-content"></div>

<!-- Show criterion legend -->
<div class="criterion-legend">
  <h3>Rubric Criteria</h3>
  <div class="criterion-item" style="background: #FFE0B2">
    <strong>THESIS</strong> (8/10): Clear thesis present
  </div>
  <div class="criterion-item" style="background: #C8E6C9">
    <strong>CITATIONS</strong> (9/10): Well-formatted citations
  </div>
  <!-- ... more criteria ... -->
</div>

<script>
// Render the essay
document.getElementById('essay-display').innerHTML =
  renderEssayWithHighlights(essay.content, highlights);

// Add hover effects
document.querySelectorAll('mark').forEach(mark => {
  mark.addEventListener('mouseenter', (e) => {
    const criterion = e.target.dataset.criterion;
    // Highlight all marks with same criterion
    document.querySelectorAll(`mark[data-criterion="${criterion}"]`)
      .forEach(m => m.classList.add('active'));
  });

  mark.addEventListener('mouseleave', (e) => {
    document.querySelectorAll('mark').forEach(m =>
      m.classList.remove('active')
    );
  });
});
</script>
```

## Running the System

### 1. Set up environment

```bash
# Install dependencies
pip install -r requirements.txt

# Set your Anthropic API key
export ANTHROPIC_API_KEY='your-api-key-here'  # Linux/Mac
set ANTHROPIC_API_KEY=your-api-key-here       # Windows
```

### 2. Start the server

```bash
uvicorn app.main:app --reload
```

Server will run at: http://localhost:8000

### 3. Run the test script

```bash
python test_grading.py
```

This will:
- Upload the example essay
- Upload the example rubric
- Grade the essay
- Display results with highlight positions

### 4. View API documentation

Open in browser: http://localhost:8000/docs

## Example Rubric Format

Rubrics are simple text files with this format:

```
Essay Grading Rubric

CRITERION_ID: Description of what to look for
- Additional details
- Scoring guidance
- Score: 0-10 points

ANOTHER_CRITERION: Description
- Details
- Score: 0-10 points
```

See [example_rubrics/sample_rubric.txt](example_rubrics/sample_rubric.txt) for a complete example.

## How the Highlight Logic Works

### In the Backend ([app/essay_grader.py](app/essay_grader.py))

1. **Claude extracts relevant text**: The AI identifies and quotes exact text from the essay
2. **String matching**: We use `essay_text.find(quoted_text)` to get character positions
3. **Position storage**: Save `start` and `end` character indices
4. **JSON response**: Return structured data with positions

```python
# Example from essay_grader.py
text = highlight["text"]  # "This is the thesis statement"
start_pos = essay_text.find(text)  # Returns: 145
if start_pos != -1:
    highlight["start"] = start_pos      # 145
    highlight["end"] = start_pos + len(text)  # 173
```

### In the Frontend

1. **Split text by positions**: Use `start` and `end` to extract substrings
2. **Wrap in HTML**: Create `<mark>` elements with appropriate styling
3. **Add interactivity**: Attach event listeners for hover effects

## Handling Edge Cases

### Overlapping Highlights

If multiple criteria highlight the same text:

```javascript
// Option 1: Layer highlights with nested marks
// Option 2: Show primary criterion with indicator for others
// Option 3: Create separate "tabs" for each criterion view
```

### Text Not Found

If Claude quotes text that doesn't exactly match:

```json
{
  "text": "approximately what the essay said",
  "start": -1,
  "end": -1,
  "note": "Exact text not found in essay"
}
```

The UI can skip these or show them separately.

### Long Essays

For very long essays:
- Consider chunking the analysis
- Use lazy loading for highlights
- Implement scroll-to-highlight navigation

## Benefits of This Approach

1. **Precise Highlighting**: Character positions ensure exact text locations
2. **Backend-Driven**: No complex text parsing needed in frontend
3. **Persistent**: Highlights saved in database, no re-computation needed
4. **Flexible**: UI can render highlights in various ways
5. **Auditable**: Full grading history stored with exact positions

## Future Enhancements

- **Confidence scores**: Add AI confidence for each highlight
- **Alternative highlights**: Multiple text spans per criterion
- **Annotation tools**: Let users adjust or add highlights
- **Export options**: PDF with highlights, annotated HTML
- **Batch grading**: Process multiple essays at once
- **Custom rubrics**: Web UI for rubric creation
- **Comment threads**: Attach discussions to specific highlights

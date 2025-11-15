# Essay Grading System - Quick Start Guide

## What This System Does

This is a complete pipeline for AI-powered essay grading with **text highlighting**. It:

1. Takes an essay (text file) and a rubric (text file) as input
2. Uses Claude AI to grade the essay based on the rubric criteria
3. Returns scores, feedback, AND **exact character positions** for highlighting relevant text
4. Stores everything in a database for later retrieval

## Key Innovation: Character-Level Highlighting

The system returns data like this:

```json
{
  "criterion": "THESIS",
  "score": 8,
  "feedback": "Clear thesis present",
  "highlights": [
    {
      "text": "This essay demonstrates...",
      "start": 145,    ← Character position where text starts
      "end": 203       ← Character position where text ends
    }
  ]
}
```

Your UI can use `start` and `end` to wrap that exact text in a `<mark>` element with color coding.

## Project Structure

```
claude_for_good_25/
├── app/
│   ├── main.py              # FastAPI endpoints
│   ├── models.py            # Database models (Essay, Rubric, Grading)
│   ├── essay_grader.py      # LLM grading logic with highlight extraction
│   └── database.py          # Database setup
├── example_essays/
│   └── essay.txt            # Sample essay for testing
├── example_rubrics/
│   └── sample_rubric.txt    # Sample rubric
├── example_ui.html          # Interactive demo showing highlighting in action
├── test_grading.py          # Script to test the full pipeline
├── ESSAY_GRADING_GUIDE.md   # Detailed documentation
└── requirements.txt         # Python dependencies
```

## Quick Start (5 Minutes)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set API Key

```bash
# Linux/Mac
export ANTHROPIC_API_KEY='your-api-key-here'

# Windows (Command Prompt)
set ANTHROPIC_API_KEY=your-api-key-here

# Windows (PowerShell)
$env:ANTHROPIC_API_KEY='your-api-key-here'
```

### 3. Start the Server

```bash
uvicorn app.main:app --reload
```

Server runs at: http://localhost:8000

### 4. Try the Interactive Demo

Open `example_ui.html` in your browser to see how highlighting works visually.

### 5. Test the API

```bash
python test_grading.py
```

This will:
- Upload the example essay
- Upload the example rubric
- Grade the essay
- Show results with highlight positions

## How the Highlighting Logic Works

### Backend ([app/essay_grader.py](app/essay_grader.py))

```python
# 1. Claude AI extracts relevant text quotes
prompt = """Find the thesis statement and quote it exactly..."""
response = claude.messages.create(...)

# 2. Parse the quoted text
grading_data = json.loads(response)
quoted_text = grading_data["highlights"][0]["text"]

# 3. Find character positions in the essay
start_pos = essay_text.find(quoted_text)  # e.g., 145
end_pos = start_pos + len(quoted_text)    # e.g., 203

# 4. Store positions
highlight = {
    "text": quoted_text,
    "start": start_pos,
    "end": end_pos
}
```

### Frontend (Your UI)

```javascript
// 1. Get data from API
const essay = await fetch('/essays/1').then(r => r.json());
const grading = await fetch('/gradings/1').then(r => r.json());

// 2. Build HTML with highlights
let html = '';
let lastIndex = 0;

grading.results.criteria_results.forEach(criterion => {
  criterion.highlights.forEach(highlight => {
    // Add text before highlight
    html += essay.content.slice(lastIndex, highlight.start);

    // Add highlighted text
    const text = essay.content.slice(highlight.start, highlight.end);
    html += `<mark style="background: ${getColor(criterion)}">${text}</mark>`;

    lastIndex = highlight.end;
  });
});

// Add remaining text
html += essay.content.slice(lastIndex);

// 3. Render
document.getElementById('essay').innerHTML = html;
```

## API Endpoints

### Upload Essay
```bash
curl -X POST http://localhost:8000/essays/ \
  -F "file=@example_essays/essay.txt"
```

### Upload Rubric
```bash
curl -X POST http://localhost:8000/rubrics/ \
  -F "file=@example_rubrics/sample_rubric.txt"
```

### Grade Essay
```bash
curl -X POST http://localhost:8000/grade \
  -d "essay_id=1&rubric_id=1"
```

### Get Grading Results
```bash
curl http://localhost:8000/gradings/1
```

## Example Response

```json
{
  "id": 1,
  "essay_id": 1,
  "rubric_id": 1,
  "total_score": 8.4,
  "results": {
    "criteria_results": [
      {
        "criterion": "THESIS",
        "score": 8,
        "feedback": "Clear thesis statement in introduction",
        "highlights": [
          {
            "text": "This essay demonstrates the importance...",
            "start": 34,
            "end": 162
          }
        ]
      },
      {
        "criterion": "CITATIONS",
        "score": 9,
        "feedback": "Well-formatted citations throughout",
        "highlights": [
          { "text": "(Smith, 2019)", "start": 438, "end": 451 },
          { "text": "(Lee & Patel, 2020)", "start": 682, "end": 701 },
          { "text": "(Garcia, 2018)", "start": 945, "end": 959 }
        ]
      }
    ],
    "overall_feedback": "Well-structured essay with good evidence"
  }
}
```

## UI Implementation Example

See [example_ui.html](example_ui.html) for a complete working example with:
- Color-coded highlights by criterion
- Hover effects
- Interactive criterion selection
- Score display

## Customization

### Create Your Own Rubric

```
My Custom Rubric

CREATIVITY: Does the essay show original thinking?
- Look for unique perspectives
- Score: 0-10 points

GRAMMAR: Is the writing grammatically correct?
- Check for errors
- Score: 0-10 points
```

Save as `.txt` file and upload via `/rubrics/` endpoint.

### Adjust AI Model

In [app/essay_grader.py](app/essay_grader.py):

```python
message = self.client.messages.create(
    model="claude-sonnet-4-5-20250929",  # Change this
    max_tokens=4000,
    messages=[...]
)
```

## Troubleshooting

**Error: ANTHROPIC_API_KEY not set**
- Make sure you've exported the environment variable
- Check it's in the same terminal session where you run the server

**Highlights not found (start: -1, end: -1)**
- Claude quoted text that doesn't exactly match the essay
- Usually happens with paraphrasing
- The system marks these as "not found"

**Server won't start**
- Check if port 8000 is already in use
- Try: `uvicorn app.main:app --reload --port 8001`

## Next Steps

1. **View API Docs**: http://localhost:8000/docs
2. **Read Full Guide**: [ESSAY_GRADING_GUIDE.md](ESSAY_GRADING_GUIDE.md)
3. **Build Your UI**: Use the example as a template
4. **Customize Rubrics**: Create rubrics for your specific needs

## Architecture Summary

```
┌──────────────┐
│  Upload Essay │
│  & Rubric     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Claude AI    │  1. Analyzes essay
│  Grading      │  2. Extracts relevant text quotes
└──────┬───────┘  3. Provides scores & feedback
       │
       ▼
┌──────────────┐
│  Backend      │  1. Finds character positions
│  Processing   │  2. Maps quotes to positions
└──────┬───────┘  3. Stores in database
       │
       ▼
┌──────────────┐
│  API Response │  Returns JSON with:
│  with Positions│  - Scores
└──────┬───────┘  - Feedback
       │           - Highlight positions (start, end)
       ▼
┌──────────────┐
│  Frontend     │  1. Fetches data
│  Rendering    │  2. Wraps text at positions in <mark>
└──────────────┘  3. Adds colors & interactivity
```

## Key Files to Understand

1. **[app/essay_grader.py](app/essay_grader.py)** - The core grading logic
2. **[app/main.py](app/main.py)** - API endpoints
3. **[example_ui.html](example_ui.html)** - How to use the data in a UI
4. **[ESSAY_GRADING_GUIDE.md](ESSAY_GRADING_GUIDE.md)** - Comprehensive documentation

Happy grading! 🎓

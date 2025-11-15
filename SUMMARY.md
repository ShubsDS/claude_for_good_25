# Complete System Summary

## Your Question

> "I want to have a chatbot grade essays. Part of the rubric may ask for citations or another part may ask for a thesis. I want my LLM to identify those and then when I am in the UI, I want it to highlight each part, how would the logic work for that?"

## The Answer

I've built you a complete working system that does exactly this! Here's how it works:

## The Core Innovation: Character Positions

The key insight is that the backend returns **exact character positions** where text should be highlighted:

```json
{
  "criterion": "THESIS",
  "highlights": [
    {
      "text": "This essay demonstrates...",
      "start": 145,    ← Character position in essay
      "end": 203       ← End position
    }
  ]
}
```

Your UI can then use these positions to extract and highlight the text:

```javascript
const highlightedText = essay.content.slice(145, 203);
// Wrap in <mark> element with color for "THESIS" criterion
```

## What I Built For You

### 1. Backend API ([app/main.py](app/main.py))

**Endpoints**:
- `POST /essays/` - Upload essay text files
- `POST /rubrics/` - Upload rubric text files
- `POST /grade` - Grade an essay against a rubric
- `GET /gradings/{id}` - Retrieve grading with highlight data

### 2. AI Grading Engine ([app/essay_grader.py](app/essay_grader.py))

**What it does**:
1. Sends essay + rubric to Claude AI
2. Claude analyzes and quotes relevant text
3. Finds those quotes in the essay using `string.find()`
4. Returns character positions (start, end) for each quote

**Example**:
```python
text = "This is the thesis statement"
start = essay_text.find(text)  # Returns: 145
end = start + len(text)         # Returns: 173

highlight = {
    "text": text,
    "start": 145,
    "end": 173
}
```

### 3. Database Models ([app/models.py](app/models.py))

- **Essay**: Stores essay content
- **Rubric**: Stores rubric criteria
- **Grading**: Stores results with highlight positions (as JSON)

### 4. Example Files

- [example_essays/essay.txt](example_essays/essay.txt) - Sample essay with citations
- [example_rubrics/sample_rubric.txt](example_rubrics/sample_rubric.txt) - Sample grading rubric
- [example_ui.html](example_ui.html) - **Interactive demo showing highlighting in action**
- [test_grading.py](test_grading.py) - Test script to run the full pipeline

### 5. Documentation

- [QUICKSTART.md](QUICKSTART.md) - 5-minute setup guide
- [ESSAY_GRADING_GUIDE.md](ESSAY_GRADING_GUIDE.md) - Complete system docs
- [HIGHLIGHTING_LOGIC.md](HIGHLIGHTING_LOGIC.md) - Deep dive into the highlighting algorithm

## How to Use It

### Quick Test (2 minutes)

```bash
# 1. Install
pip install -r requirements.txt

# 2. Set API key
export ANTHROPIC_API_KEY='your-key'

# 3. Start server
uvicorn app.main:app --reload

# 4. Open example_ui.html in your browser
# See interactive highlighting demo!
```

### Full Test (5 minutes)

```bash
# Run the automated test
python test_grading.py
```

This will:
1. Upload the example essay
2. Upload the example rubric
3. Grade the essay
4. Show you the results with exact character positions for highlighting

## The Complete Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. USER UPLOADS                                             │
│    - Essay: "This essay demonstrates..."                   │
│    - Rubric: "THESIS: Does it have a thesis?"              │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. BACKEND SENDS TO CLAUDE AI                               │
│    Prompt: "Grade this essay. For each criterion,          │
│             quote EXACT text that's relevant."              │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. CLAUDE ANALYZES                                          │
│    Returns: {                                               │
│      "criterion": "THESIS",                                 │
│      "score": 8,                                            │
│      "feedback": "Clear thesis present",                    │
│      "highlights": [                                        │
│        { "text": "This essay demonstrates..." }            │
│      ]                                                      │
│    }                                                        │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. BACKEND FINDS CHARACTER POSITIONS                        │
│    essay_text.find("This essay demonstrates...")           │
│    → Returns start position: 145                            │
│                                                             │
│    Updated response: {                                      │
│      "text": "This essay demonstrates...",                 │
│      "start": 145,                                          │
│      "end": 203                                             │
│    }                                                        │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. SAVE TO DATABASE                                         │
│    Grading record with full JSON including positions       │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. FRONTEND FETCHES                                         │
│    GET /essays/1      → essay content                       │
│    GET /gradings/1    → results with positions             │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. FRONTEND RENDERS HIGHLIGHTS                              │
│                                                             │
│    const text = essay.content.slice(145, 203)              │
│    → "This essay demonstrates..."                          │
│                                                             │
│    html += `<mark style="background: blue">                │
│              ${text}                                        │
│            </mark>`                                         │
└─────────────────────────────────────────────────────────────┘
```

## Example Request/Response

### Request

```bash
POST /grade
{
  "essay_id": 1,
  "rubric_id": 1
}
```

### Response

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
            "text": "This essay demonstrates the importance of structured writing",
            "start": 34,
            "end": 94
          }
        ]
      },
      {
        "criterion": "CITATIONS",
        "score": 9,
        "feedback": "Multiple well-formatted citations",
        "highlights": [
          { "text": "(Smith, 2019)", "start": 438, "end": 451 },
          { "text": "(Lee & Patel, 2020)", "start": 682, "end": 701 },
          { "text": "(Garcia, 2018)", "start": 945, "end": 959 }
        ]
      }
    ]
  }
}
```

## Frontend Implementation

### Basic Example

```javascript
// 1. Fetch data
const essay = await fetch('/essays/1').then(r => r.json());
const grading = await fetch('/gradings/1').then(r => r.json());

// 2. Define colors
const colors = {
  'THESIS': '#FFE0B2',
  'CITATIONS': '#C8E6C9'
};

// 3. Build highlights
let html = '';
let pos = 0;

grading.results.criteria_results.forEach(cr => {
  cr.highlights.forEach(h => {
    // Text before highlight
    html += essay.content.slice(pos, h.start);

    // Highlighted text
    html += `<mark style="background: ${colors[cr.criterion]}">
              ${essay.content.slice(h.start, h.end)}
            </mark>`;

    pos = h.end;
  });
});

// Remaining text
html += essay.content.slice(pos);

// 4. Render
document.getElementById('essay').innerHTML = html;
```

### See It In Action

Open [example_ui.html](example_ui.html) in your browser for a complete working example with:
- Color-coded highlights by criterion
- Hover effects
- Interactive criterion selection
- Score display

## Key Files

### Must Read

1. **[QUICKSTART.md](QUICKSTART.md)** - Start here!
2. **[example_ui.html](example_ui.html)** - See the highlighting in action
3. **[app/essay_grader.py](app/essay_grader.py)** - The core grading logic

### Reference

4. **[ESSAY_GRADING_GUIDE.md](ESSAY_GRADING_GUIDE.md)** - Full documentation
5. **[HIGHLIGHTING_LOGIC.md](HIGHLIGHTING_LOGIC.md)** - Algorithm deep dive
6. **[app/main.py](app/main.py)** - API endpoints
7. **[app/models.py](app/models.py)** - Database schema

## Customization

### Create Your Own Rubric

Create a text file like this:

```
My Rubric

CREATIVITY: Does the essay show original thinking?
- Look for unique perspectives
- Score: 0-10 points

GRAMMAR: Is the writing grammatically correct?
- Check for errors
- Score: 0-10 points
```

Upload it:
```bash
curl -X POST http://localhost:8000/rubrics/ \
  -F "file=@my_rubric.txt"
```

### Adjust Colors in UI

```javascript
const criterionColors = {
  'CREATIVITY': '#FFF9C4',  // Yellow
  'GRAMMAR': '#FFCCBC'      // Orange
};
```

## Next Steps

1. **Try it out**: Run `python test_grading.py`
2. **See the demo**: Open `example_ui.html`
3. **Read the docs**: Check out `QUICKSTART.md`
4. **Build your UI**: Use the example as a template
5. **Customize rubrics**: Create your own grading criteria

## Questions?

- **How does it find the text?** Uses Python's `string.find()` method
- **What if text isn't found?** Returns `start: -1, end: -1`
- **Can highlights overlap?** Yes, you can handle this in the UI
- **Is it fast?** Yes, positions are cached in the database
- **Can I use different AI models?** Yes, edit `app/essay_grader.py`

## Summary

You asked: "How would the logic work for highlighting?"

**Answer**:
1. AI quotes exact text from the essay
2. Backend finds character positions using `string.find()`
3. Returns positions to frontend
4. Frontend uses positions to render highlights

**You now have**:
- ✅ Working backend API
- ✅ AI grading with Claude
- ✅ Character position extraction
- ✅ Database storage
- ✅ Interactive UI demo
- ✅ Complete documentation
- ✅ Test scripts

Everything is ready to use! 🎉

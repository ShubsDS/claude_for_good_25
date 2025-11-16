# Essay Grading System with AI-Powered Text Highlighting

**Claude for Good 2025 Submission**

An intelligent essay grading system that uses Claude AI to analyze essays against custom rubrics and provides **character-level text highlighting** for UI integration.

## What Makes This Special?

Most grading systems just return scores and comments. This system goes further by identifying **exactly where** in the essay each rubric criterion applies, returning character positions (start/end) so your UI can highlight the relevant text.

**Example Output**:
```json
{
  "criterion": "THESIS",
  "score": 8,
  "feedback": "Clear thesis statement",
  "highlights": [
    {
      "text": "This essay demonstrates...",
      "start": 145,  // Exact character position
      "end": 203     // Highlighting made easy!
    }
  ]
}
```

## Features

- 📝 **Essay Upload** - Submit essays as text files
- 📋 **Custom Rubrics** - Define grading criteria in simple text format
- 🤖 **AI Grading** - Claude analyzes essays and provides detailed feedback
- 🎨 **Text Highlighting** - Returns exact character positions for UI highlighting
- 💾 **Database Storage** - All essays, rubrics, and gradings saved
- 🔗 **REST API** - Easy integration with any frontend
- 📊 **Structured Results** - JSON responses with scores, feedback, and highlights

## Quick Start

### 1. Install Dependencies

This project has both Python (backend) and Node.js (frontend) dependencies.

```bash
# Install Python dependencies (backend)
pip install -r requirements.txt

# Install Node.js dependencies (frontend)
cd frontend
npm install
cd ..
```

### 2. Set API Key

```bash
# Linux/Mac
export ANTHROPIC_API_KEY='your-api-key-here'

# Windows
set ANTHROPIC_API_KEY=your-api-key-here
```

### 3. Start Server

```bash
uvicorn app.main:app --reload
```

Server runs at: http://localhost:8000

### 4. Start Frontend

The frontend is a separate application located in the `frontend/` directory.

```bash
cd frontend
npm run dev
```

The frontend will typically run at: http://localhost:5173 (or similar)

### 5. Try the Demo

**Option A**: Open the running frontend (e.g., http://localhost:5173) in your browser to see the interactive web application.

**Option B**: Open [example_ui.html](example_ui.html) in your browser to see interactive highlighting

**Option C**: Run the test script
```bash
python test_grading.py
```

## Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- **[ESSAY_GRADING_GUIDE.md](ESSAY_GRADING_GUIDE.md)** - Complete system documentation
- **[HIGHLIGHTING_LOGIC.md](HIGHLIGHTING_LOGIC.md)** - Deep dive into how highlighting works
- **API Docs** - http://localhost:8000/docs (when server is running)

## Project Structure

```
claude_for_good_25/
├── app/
│   ├── main.py              # FastAPI endpoints
│   ├── models.py            # Database models
│   ├── essay_grader.py      # AI grading logic
│   └── database.py          # Database setup
├── example_essays/          # Sample essays
├── example_rubrics/         # Sample rubrics
├── example_ui.html          # Interactive demo
├── test_grading.py          # Test script
└── docs/                    # Documentation
```

## How It Works

```
1. Upload Essay & Rubric
   ↓
2. Claude AI analyzes essay
   ↓
3. AI identifies relevant text sections
   ↓
4. Backend maps text to character positions
   ↓
5. Returns JSON with scores + highlight positions
   ↓
6. Frontend uses positions to render highlights
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/essays/` | POST | Upload an essay |
| `/rubrics/` | POST | Upload a rubric |
| `/grade` | POST | Grade an essay |
| `/gradings/{id}` | GET | Get grading results with highlights |
| `/canvas/submissions/ingest` | POST | Ingest submissions from Canvas |
| `/canvas/post_grade` | POST | Post grade back to Canvas (manual) |
| `/canvas/post_grade/from_grading` | POST | Post grade back to Canvas using stored context |

## Example Usage

### Upload and Grade

```bash
# 1. Upload essay
curl -X POST http://localhost:8000/essays/ \
  -F "file=@example_essays/essay.txt"
# Returns: {"id": 1, ...}

# 2. Upload rubric
curl -X POST http://localhost:8000/rubrics/ \
  -F "file=@example_rubrics/sample_rubric.txt"
# Returns: {"id": 1, ...}

# 3. Grade the essay
curl -X POST http://localhost:8000/grade \
  -d "essay_id=1&rubric_id=1"
# Returns: Full grading with highlights
```

### Use in Frontend

```javascript
// Fetch data
const essay = await fetch('/essays/1').then(r => r.json());
const grading = await fetch('/gradings/1').then(r => r.json());

// Render with highlights
grading.results.criteria_results.forEach(criterion => {
  criterion.highlights.forEach(highlight => {
    // Use highlight.start and highlight.end to wrap text
    const text = essay.content.slice(highlight.start, highlight.end);
    const color = getColorForCriterion(criterion.criterion);
    renderHighlight(text, color, highlight.start);
  });
});
```

## Tech Stack

- **Backend**: FastAPI + SQLModel + SQLite
- **AI**: Anthropic Claude (Sonnet 4.5)
- **Frontend**: React/Vite/TypeScript

## Use Cases

- 📚 **Educational platforms** - Automated essay grading with visual feedback
- 🎓 **Teacher tools** - Highlight areas needing improvement
- 📊 **Writing analytics** - Identify patterns in student writing
- 🔍 **Quality assurance** - Check academic writing standards

## Why Character Positions?

Instead of just saying "the thesis is good", we return:
```json
{
  "feedback": "Strong thesis statement",
  "highlights": [
    {"text": "...", "start": 145, "end": 203}
  ]
}
```

This lets your UI:
- Highlight exact text with color coding
- Make highlights clickable/hoverable
- Show which parts relate to which criteria
- Provide interactive feedback

## Contributing

This is a Claude for Good 2025 submission. Feel free to fork and adapt for your needs!

## License

MIT

## Acknowledgments

Built with Claude AI for Claude for Good 2025 hackathon.

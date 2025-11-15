# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-powered essay grading system with **character-level text highlighting**. Uses Claude AI to grade essays against custom rubrics and returns exact character positions (start/end) for UI highlighting. Built for the Claude for Good 2025 hackathon.

**Key Innovation**: Backend identifies rubric-relevant text and returns precise character positions, enabling the frontend to highlight exact passages (thesis, citations, evidence, etc.) with color coding.

## Tech Stack

- **Backend**: FastAPI + SQLModel + SQLite
- **Frontend**: React 19 + TypeScript + Vite + TailwindCSS + React Router
- **AI**: Anthropic Claude Sonnet 4.5 (`claude-sonnet-4-5-20250929`)
- **Text Matching**: rapidfuzz for fuzzy text matching
- **PDF Processing**: PyMuPDF for extracting text from PDFs
- **Canvas LMS**: canvasapi for ingesting student submissions

## Architecture

### Backend Structure (`app/`)

**Core grading logic** ([app/essay_grader.py](app/essay_grader.py:1)):
- `EssayGrader` class handles Claude API interaction
- Sends essay + rubric to Claude with instructions to quote exact text
- Uses `_find_text_position()` with fuzzy matching to map quoted text to character positions
- Returns JSON with scores, feedback, and highlights (text + start/end positions)

**API endpoints** ([app/main.py](app/main.py:1)):
- Essays: POST `/essays/`, GET `/essays/`, GET `/essays/{id}`
- Rubrics: POST `/rubrics/`, GET `/rubrics/`, GET `/rubrics/{id}`
- Grading: POST `/grade`, GET `/gradings/{id}`
- Canvas: POST `/canvas/submissions/ingest` - ingests submissions from Canvas LMS

**Database models** ([app/models.py](app/models.py:1)):
- `Essay`: stores essay content
- `Rubric`: stores rubric content + parsed criteria (JSON)
- `Grading`: stores results with highlight positions (JSON)
- `Submission`: Canvas submission metadata + file paths

**Canvas integration** ([app/api/canvas.py](app/api/canvas.py:1)):
- Downloads PDF/text submissions from Canvas
- Extracts text using PyMuPDF ([app/utils/pdf_extractor.py](app/utils/pdf_extractor.py))
- Creates Essay records in database

### Frontend Structure (`frontend/src/`)

**Routing** ([frontend/src/App.tsx](frontend/src/App.tsx:1)):
- `/` - Home
- `/teacher/upload` - Upload essays/rubrics or ingest from Canvas
- `/teacher/grading` - Select essay + rubric and trigger grading
- `/teacher/results` - Display graded essay with highlights

**API client** ([frontend/src/services/api.ts](frontend/src/services/api.ts:1)):
- Axios-based client wrapping backend endpoints
- Base URL: `http://localhost:8000`

**Highlighting implementation** ([frontend/src/pages/ResultsPage.tsx](frontend/src/pages/ResultsPage.tsx:34)):
- `HighlightedText` component renders essay with highlights
- Uses character positions from grading results
- Color-codes by criterion with opacity transitions for interactivity
- Sorts highlights by position to avoid overlaps

## Development Commands

### Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key (required)
export ANTHROPIC_API_KEY='your-api-key'  # Linux/Mac
set ANTHROPIC_API_KEY=your-api-key       # Windows CMD
$env:ANTHROPIC_API_KEY='your-api-key'    # Windows PowerShell

# Start development server
uvicorn app.main:app --reload

# Run tests
python test_grading.py
python test_fuzzy_matching.py

# View database
python view_data.py
```

Server runs at http://localhost:8000 (API docs at /docs)

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Run linter
npm run lint

# Preview production build
npm run preview
```

Dev server runs at http://localhost:5173

### Full Stack Development

1. Terminal 1: `uvicorn app.main:app --reload` (backend)
2. Terminal 2: `cd frontend && npm run dev` (frontend)
3. Open http://localhost:5173

## How Text Highlighting Works

**Flow**:
1. Claude analyzes essay and quotes exact text for each rubric criterion
2. Backend uses fuzzy matching (`rapidfuzz`) to find quoted text in essay
3. Returns character positions: `{"text": "...", "start": 145, "end": 203}`
4. Frontend slices essay text and wraps in `<mark>` elements with color coding

**Fuzzy matching** ([app/essay_grader.py](app/essay_grader.py:116)):
- Tries exact match first
- Falls back to normalized whitespace matching
- Finally uses sliding window with fuzzy string matching (threshold: 75%)
- Handles minor variations in LLM quotes

## Working with Rubrics

Rubric format (plain text):

```
Rubric Name

CRITERION_ID: Description of what to evaluate
- Additional details
- Score: 0-10 points

ANOTHER_CRITERION: Description
- Details
```

Parser extracts lines with `CRITERION_ID:` pattern where ID is uppercase ([app/essay_grader.py](app/essay_grader.py:19)).

## Canvas Integration

POST `/canvas/submissions/ingest` with:
```json
{
  "canvas_base_url": "https://canvas.example.edu",
  "api_token": "...",
  "course_id": 12345,
  "assignment_id": 67890,
  "student_id": null  // optional, null = all students
}
```

Downloads PDFs/text files to `data/submissions/{assignment_id}/{student_id}/`, extracts text, creates Essay records.

## Database

SQLite database: `db.sqlite` (auto-created on startup)

Schema managed by SQLModel with auto-migrations. To reset: delete `db.sqlite` and restart server.

## Configuration

- Backend API key: Set `ANTHROPIC_API_KEY` environment variable
- Frontend API URL: Hard-coded in [frontend/src/services/api.ts](frontend/src/services/api.ts:10) as `http://localhost:8000`
- CORS origins: Configured in [app/main.py](app/main.py:19) for ports 3000, 5173, 5174

## Key Files for Understanding the System

1. [documentation/QUICKSTART.md](documentation/QUICKSTART.md) - 5-minute setup guide
2. [documentation/HIGHLIGHTING_LOGIC.md](documentation/HIGHLIGHTING_LOGIC.md) - Deep dive into highlighting algorithm
3. [app/essay_grader.py](app/essay_grader.py) - Core grading + fuzzy matching logic
4. [frontend/src/pages/ResultsPage.tsx](frontend/src/pages/ResultsPage.tsx) - Highlighting UI implementation
5. [SUMMARY.md](SUMMARY.md) - Complete system overview with examples

## Testing

- [test_grading.py](test_grading.py) - End-to-end grading test
- [test_fuzzy_matching.py](test_fuzzy_matching.py) - Fuzzy text matching tests
- [app/api/tests/](app/api/tests/) - Canvas and PDF extractor tests

## Common Tasks

**Add new API endpoint**: Add route to [app/main.py](app/main.py), corresponding function to [frontend/src/services/api.ts](frontend/src/services/api.ts)

**Modify grading logic**: Edit [app/essay_grader.py](app/essay_grader.py), particularly `_build_grading_prompt()` for prompt changes

**Change AI model**: Update model ID in [app/essay_grader.py](app/essay_grader.py:61)

**Adjust highlighting colors**: Modify `COLOR_PALETTE` in [frontend/src/pages/ResultsPage.tsx](frontend/src/pages/ResultsPage.tsx:12)

**Add database table**: Create model in [app/models.py](app/models.py), restart server for auto-migration

## Git Workflow

Currently on `frontend` branch. Main branch is `main`.

Recent commits focus on frontend implementation and highlighting fixes.

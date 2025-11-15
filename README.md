# claude_for_good_25

This repository contains a minimal FastAPI backend initialized to use SQLite via SQLModel.

Quick start (macOS / zsh):

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the development server:

```bash
uvicorn app.main:app --reload --port 8000
```

4. Smoke test:

```bash
curl http://127.0.0.1:8000/items/
```

Notes:
- The SQLite database file `db.sqlite` will be created in the repository root when the app first runs.
- Endpoints available: POST /items/, GET /items/, GET /items/{id}, PUT /items/{id}, DELETE /items/{id}.

Submission to Claude for Good 2025


initial commit
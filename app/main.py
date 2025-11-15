from typing import Optional
import os
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from sqlalchemy import func

from .database import engine, init_db
from .models import Item, Essay, Rubric, Grading, Submission
from .essay_grader import EssayGrader
from .api.canvas import router as canvas_router, CanvasClientService

app = FastAPI(title="FastAPI + SQLite (SQLModel) example")
load_dotenv()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:5174",  # Vite alternative port
        "http://localhost:3000",  # Alternative dev port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(canvas_router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def root():
    return {"ok": True, "message": "FastAPI + SQLite (SQLModel)", "docs": "/docs"}


@app.get("/ping")
def ping():
    return {"ping": "pong"}


@app.get("/health")
def health():
    try:
        # quick DB reachability check
        with Session(engine) as session:
            session.exec(select(Item).limit(1)).first()
        return {"ok": True, "database": "reachable"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.post("/items/", response_model=Item)
def create_item(item: Item):
    with Session(engine) as session:
        session.add(item)
        session.commit()
        session.refresh(item)
        return item


@app.get("/items/", response_model=list[Item])
def read_items():
    with Session(engine) as session:
        statement = select(Item)
        items = session.exec(statement).all()
        return items


@app.get("/items/count")
def items_count():
    with Session(engine) as session:
        count = session.exec(select(func.count()).select_from(Item)).one()
        return {"count": count}


@app.get("/items/search", response_model=list[Item])
def search_items(q: Optional[str] = None, name: Optional[str] = None):
    with Session(engine) as session:
        stmt = select(Item)
        if q:
            stmt = stmt.where((Item.name.contains(q)) | (Item.description.contains(q)))
        if name:
            stmt = stmt.where(Item.name == name)
        items = session.exec(stmt).all()
        return items


@app.get("/items/{item_id}", response_model=Item)
def read_item(item_id: int):
    with Session(engine) as session:
        item = session.get(Item, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        return item


@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, item_data: Item):
    with Session(engine) as session:
        item = session.get(Item, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        item.name = item_data.name
        item.description = item_data.description
        session.add(item)
        session.commit()
        session.refresh(item)
        return item


@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    with Session(engine) as session:
        item = session.get(Item, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        session.delete(item)
        session.commit()
        return {"ok": True}


# ============================================================================
# Essay Grading Endpoints
# ============================================================================

@app.post("/essays/", response_model=Essay)
async def upload_essay(file: UploadFile = File(...)):
    """Upload an essay text file."""
    content = await file.read()
    essay_text = content.decode('utf-8')

    with Session(engine) as session:
        essay = Essay(
            filename=file.filename,
            content=essay_text
        )
        session.add(essay)
        session.commit()
        session.refresh(essay)
        return essay


@app.get("/essays/", response_model=list[Essay])
def list_essays():
    """List all uploaded essays."""
    with Session(engine) as session:
        essays = session.exec(select(Essay)).all()
        return essays


@app.get("/essays/{essay_id}", response_model=Essay)
def get_essay(essay_id: int):
    """Get a specific essay by ID."""
    with Session(engine) as session:
        essay = session.get(Essay, essay_id)
        if not essay:
            raise HTTPException(status_code=404, detail="Essay not found")
        return essay


@app.delete("/essays/")
def delete_all_essays():
    """Delete all essays from the database."""
    with Session(engine) as session:
        essays = session.exec(select(Essay)).all()
        count = len(essays)
        for essay in essays:
            session.delete(essay)
        session.commit()
        return {"ok": True, "deleted": count}


@app.post("/rubrics/", response_model=Rubric)
async def upload_rubric(file: UploadFile = File(...)):
    """Upload a rubric text file."""
    content = await file.read()
    rubric_text = content.decode('utf-8')

    # Parse the rubric
    grader = EssayGrader()
    criteria = grader.parse_rubric(rubric_text)

    with Session(engine) as session:
        rubric = Rubric(
            name=file.filename,
            content=rubric_text,
            criteria=criteria
        )
        session.add(rubric)
        session.commit()
        session.refresh(rubric)
        return rubric


@app.get("/rubrics/", response_model=list[Rubric])
def list_rubrics():
    """List all uploaded rubrics."""
    with Session(engine) as session:
        rubrics = session.exec(select(Rubric)).all()
        return rubrics


@app.get("/rubrics/{rubric_id}", response_model=Rubric)
def get_rubric(rubric_id: int):
    """Get a specific rubric by ID."""
    with Session(engine) as session:
        rubric = session.get(Rubric, rubric_id)
        if not rubric:
            raise HTTPException(status_code=404, detail="Rubric not found")
        return rubric


@app.post("/grade", response_model=Grading)
def grade_essay(essay_id: int = Form(...), rubric_id: int = Form(...)):
    """
    Grade an essay based on a rubric.

    Returns grading results with scores, feedback, and text highlights.
    """
    with Session(engine) as session:
        # Get essay and rubric
        essay = session.get(Essay, essay_id)
        if not essay:
            raise HTTPException(status_code=404, detail="Essay not found")

        rubric = session.get(Rubric, rubric_id)
        if not rubric:
            raise HTTPException(status_code=404, detail="Rubric not found")

        # Grade the essay
        try:
            grader = EssayGrader()
            grading_results = grader.grade_essay(essay.content, rubric.content)
            total_score = grader.calculate_total_score(grading_results)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error grading essay: {str(e)}"
            )

        # Save grading to database
        grading = Grading(
            essay_id=essay_id,
            rubric_id=rubric_id,
            results=grading_results,
            total_score=total_score
        )
        session.add(grading)
        session.commit()
        session.refresh(grading)

        # Attempt automatic post to Canvas if this essay came from an ingested Submission.
        # Robust behavior:
        # - Prefer credentials saved on the Submission.
        # - Fall back to environment variables CANVAS_BASE_URL / CANVAS_API_TOKEN / CANVAS_COURSE_ID.
        try:
            submission = None
            if getattr(essay, "submission_id", None):
                submission = session.get(Submission, essay.submission_id)

            if not submission:
                # Nothing to do
                pass
            else:
                # Determine Canvas connection info (prefer submission values)
                canvas_base_url = getattr(submission, "canvas_base_url", None) or os.getenv("CANVAS_BASE_URL")
                canvas_api_token = getattr(submission, "canvas_api_token", None) or os.getenv("CANVAS_API_TOKEN")
                course_id = getattr(submission, "course_id", None) or (int(os.getenv("CANVAS_COURSE_ID")) if os.getenv("CANVAS_COURSE_ID") else None)

                if not canvas_base_url or not canvas_api_token:
                    print(f"Skipping Canvas post for submission {submission.id}: no Canvas credentials available")
                elif not submission.assignment_id or not submission.student_id:
                    print(f"Skipping Canvas post for submission {submission.id}: missing assignment_id or student_id")
                else:
                    try:
                        service = CanvasClientService(canvas_base_url, canvas_api_token)

                        # Ensure we have a course id (either stored or provided via env)
                        if not course_id:
                            raise RuntimeError("Course ID not available on submission and CANVAS_COURSE_ID not set in environment")

                        course = service.get_course(course_id)
                        assignment = service.get_assignment(course, submission.assignment_id)

                        # Determine points possible and compute final points
                        points_possible = getattr(assignment, "points_possible", None) or getattr(assignment, "points", None) or 10.0
                        try:
                            final_points = float(total_score) / 10.0 * float(points_possible)
                        except Exception:
                            final_points = float(total_score)

                        # Post the grade
                        canvas_submission = assignment.get_submission(submission.student_id)
                        canvas_submission.edit(submission={'posted_grade': final_points})
                        print(f"Posted grade to Canvas for submission {submission.id}: {final_points}")
                    except Exception as e:
                        print(f"Failed to post grade to Canvas for submission {submission.id if submission else 'unknown'}: {e}")
        except Exception as e:
            print(f"Unexpected error checking/submitting Canvas grade: {e}")

        return grading


@app.get("/gradings/", response_model=list[Grading])
def list_gradings():
    """List all gradings."""
    with Session(engine) as session:
        gradings = session.exec(select(Grading)).all()
        return gradings


@app.get("/gradings/{grading_id}", response_model=Grading)
def get_grading(grading_id: int):
    """Get a specific grading by ID with all highlight information."""
    with Session(engine) as session:
        grading = session.get(Grading, grading_id)
        if not grading:
            raise HTTPException(status_code=404, detail="Grading not found")
        return grading

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from pathlib import Path
import os
import requests

from sqlmodel import Session

# Handle both package and direct imports
try:
    from ..database import engine
    from ..models import Submission, Essay, Grading
    from ..utils.pdf_extractor import pdf_to_text
    from ..jwtvalidate import Bearer
except ImportError:
    from app.database import engine
    from app.models import Submission, Essay, Grading
    from app.utils.pdf_extractor import pdf_to_text
    from app.jwtvalidate import Bearer

try:
    from canvasapi import Canvas
except Exception:
    Canvas = None


class CanvasIngestRequest(BaseModel):
    canvas_base_url: str
    api_token: Optional[str] = None  # Optional, will use env var if not provided
    course_id: int
    assignment_id: int
    student_id: Optional[int] = None


class CanvasClientService:
    """
    Single Responsibility: encapsulate Canvas API interactions.
    Keeps external API concerns isolated for testability and SRP adherence.
    """
    def __init__(self, base_url: str, api_token: str):
        if Canvas is None:
            raise RuntimeError("canvasapi package not installed. pip install canvasapi")
        self.canvas = Canvas(base_url, api_token)
        self.api_token = api_token

    def get_courses(self, **kwargs):
        """Return an iterable of courses (pass-through to canvas.get_courses)."""
        return self.canvas.get_courses(**kwargs)

    def get_course(self, course_id: int):
        return self.canvas.get_course(course_id)

    def get_assignment(self, course, assignment_id: int):
        return course.get_assignment(assignment_id)

    def get_submissions(self, assignment, student_id: Optional[int] = None):
        if student_id:
            return [assignment.get_submission(student_id)]
        return assignment.get_submissions()

    def download_fileobj(self, file_obj, target_path: Path):
        # Canvas File object may provide download(path)
        if hasattr(file_obj, "download"):
            file_obj.download(str(target_path))
            return str(target_path)
        # try to fetch URL from object JSON
        url = getattr(file_obj, "url", None) or getattr(file_obj, "html_url", None) or (getattr(file_obj, "_json", {}).get("url") if hasattr(file_obj, "_json") else None)
        return self._http_download(url, target_path)

    def _http_download(self, url: str, target_path: Path):
        headers = {"Authorization": f"Bearer {self.api_token}"}
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        with open(target_path, "wb") as fh:
            fh.write(resp.content)
        return str(target_path)


router = APIRouter(prefix="/canvas", tags=["canvas"])

# Initialize Bearer authentication
auth = Bearer()


def _safe_get_attr(obj: Any, *attrs, default=None):
    cur = obj
    for a in attrs:
        try:
            cur = getattr(cur, a)
        except Exception:
            try:
                cur = cur[a]
            except Exception:
                return default
        if cur is None:
            return default
    return cur


@router.post("/submissions/ingest")
def ingest_submissions(req: CanvasIngestRequest, payload: dict = Depends(auth)):
    """
    Ingest submissions for an assignment from Canvas, download attached files (PDFs),
    and create Submission DB records with saved file paths.
    """
    user_email = payload.get("email")
    
    # Get Canvas API token from environment variable or request
    canvas_api_token = os.getenv("CANVAS_API_TOKEN") or req.api_token
    if not canvas_api_token:
        raise HTTPException(status_code=400, detail="Canvas API token not configured in environment and not provided in request")
    
    service = CanvasClientService(req.canvas_base_url, canvas_api_token)
    try:
        course = service.get_course(req.course_id)
        assignment = service.get_assignment(course, req.assignment_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch course/assignment: {e}")

    try:
        submissions_list = service.get_submissions(assignment, req.student_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch submissions: {e}")

    base_storage = Path("data/submissions")
    results: List[Dict[str, Any]] = []

    for sub in submissions_list:
        student_id = _safe_get_attr(sub, "user_id", default=None) or _safe_get_attr(sub, "user", "id", default=None)
        student_name = _safe_get_attr(sub, "user", "name", default=None) or _safe_get_attr(sub, "user_name", default=None)

        attachments: List[Dict[str, Any]] = []
        att = _safe_get_attr(sub, "attachments", default=None)
        if att:
            for a in att:
                if isinstance(a, dict):
                    attachments.append(a)
                else:
                    attachments.append({
                        "url": _safe_get_attr(a, "url", default=None) or _safe_get_attr(a, "html_url", default=None),
                        "filename": _safe_get_attr(a, "filename", default=None) or _safe_get_attr(a, "display_name", default=None)
                    })

        if not attachments:
            try:
                files = sub.get_files()
                for f in files:
                    url = _safe_get_attr(f, "url", default=None) or _safe_get_attr(f, "html_url", default=None) or (getattr(f, "_json", {}).get("url") if hasattr(f, "_json") else None)
                    filename = _safe_get_attr(f, "display_name", default=None) or _safe_get_attr(f, "filename", default=None) or _safe_get_attr(f, "name", default=None)
                    attachments.append({"url": url, "filename": filename, "file_obj": f})
            except Exception:
                pass

        if not attachments:
            raw = _safe_get_attr(sub, "_raw", default=None) or _safe_get_attr(sub, "submission", default=None)
            if isinstance(raw, dict):
                maybe = raw.get("attachments") or raw.get("files") or (raw.get("submission_data", {}) or {}).get("attachments")
                if isinstance(maybe, list):
                    for a in maybe:
                        if isinstance(a, dict):
                            attachments.append(a)

        saved_files: List[Any] = []
        if not attachments:
            results.append({"student_id": student_id, "student_name": student_name, "files": []})
            continue

        target_dir = base_storage / str(req.assignment_id) / (str(student_id) if student_id else "unknown_student")
        os.makedirs(target_dir, exist_ok=True)

        for a in attachments:
            url = a.get("url") or a.get("html_url") or a.get("download_url")
            filename = a.get("filename") or a.get("display_name") or a.get("name")
            file_obj = a.get("file_obj")

            if not filename and file_obj is not None:
                filename = _safe_get_attr(file_obj, "display_name", default=None) or _safe_get_attr(file_obj, "filename", default=None)

            if file_obj is not None:
                try:
                    save_path = Path(target_dir) / (filename or "downloaded_file")
                    saved = service.download_fileobj(file_obj, save_path)
                    saved_files.append(saved)
                    continue
                except Exception:
                    pass

            if not url:
                continue

            try:
                save_path = Path(target_dir) / (filename or Path(url).name or "attachment")
                saved = service._http_download(url, save_path)
                saved_files.append(saved)
            except Exception as e:
                saved_files.append({"error": str(e), "url": url})

        # Extract text from downloaded files and create Essay records
        file_paths_str = ",".join([f for f in saved_files if isinstance(f, str)])
        with Session(engine) as session:
            # Create Submission record (persist Canvas context so we can post grades later)
            record = Submission(
                course_id=req.course_id,
                assignment_id=req.assignment_id,
                student_id=int(student_id) if student_id else 0,
                student_name=student_name,
                teacher=None,
                file_paths=file_paths_str,
                canvas_base_url=req.canvas_base_url,
                canvas_api_token=canvas_api_token
            )
            session.add(record)
            session.commit()
            session.refresh(record)

            # Process files and create Essay records
            essay_ids = []
            for file_path in saved_files:
                if not isinstance(file_path, str):
                    continue

                file_path_obj = Path(file_path)
                if not file_path_obj.exists():
                    continue

                # Extract text based on file type
                text_content = None
                filename = file_path_obj.name

                if file_path_obj.suffix.lower() == '.pdf':
                    # Extract text from PDF
                    try:
                        text_path = file_path_obj.with_suffix('.txt')
                        pdf_to_text(str(file_path_obj), str(text_path))
                        with open(text_path, 'r', encoding='utf-8') as f:
                            text_content = f.read()
                    except Exception as e:
                        # Log error but continue processing
                        print(f"Failed to extract text from PDF {file_path}: {e}")
                        continue

                elif file_path_obj.suffix.lower() == '.txt':
                    # Read text file directly
                    try:
                        with open(file_path_obj, 'r', encoding='utf-8') as f:
                            text_content = f.read()
                    except Exception as e:
                        print(f"Failed to read text file {file_path}: {e}")
                        continue
                else:
                    # Skip unsupported file types
                    continue

                if text_content:
                    # Create Essay record and link back to Submission
                    essay = Essay(
                        filename=f"{student_name or student_id}_{filename}",
                        content=text_content,
                        submission_id=record.id,
                        created_by=user_email
                    )
                    session.add(essay)
                    session.commit()
                    session.refresh(essay)
                    essay_ids.append(essay.id)

            results.append({
                "submission_db_id": record.id,
                "student_id": student_id,
                "student_name": student_name,
                "files": saved_files,
                "essay_ids": essay_ids
            })

    return {"ingested": results}

# ---------------------------------------------------------------------------
# POST grade back to Canvas
# ---------------------------------------------------------------------------
class PostGradeRequest(BaseModel):
    canvas_base_url: str
    api_token: str
    course_id: int
    assignment_id: int
    student_id: int
    grading_id: Optional[int] = None

@router.post("/post_grade")
def post_grade_to_canvas(req: PostGradeRequest):
    """
    Post a grading's total_score back to Canvas for a specific student's submission.
    Expects grading_id to exist in the local DB. Calculates points based on
    the Canvas assignment's points_possible (defaults to 10 if unavailable).
    """
    service = CanvasClientService(req.canvas_base_url, req.api_token)

    try:
        course = service.get_course(req.course_id)
        assignment = service.get_assignment(course, req.assignment_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch course/assignment: {e}")

    # Require a local grading id to determine the score to post
    if not req.grading_id:
        raise HTTPException(status_code=400, detail="grading_id is required")

    with Session(engine) as session:
        grading = session.get(Grading, req.grading_id)
        if not grading:
            raise HTTPException(status_code=404, detail="Grading not found")

    total_score = getattr(grading, "total_score", None)
    if total_score is None:
        raise HTTPException(status_code=400, detail="Grading has no total_score")

    # Get assignment points possible; fall back to 10
    points_possible = getattr(assignment, "points_possible", None) or getattr(assignment, "points", None) or 10.0

    # Scale 0-10 to assignment points
    try:
        final_points = float(total_score) / 10.0 * float(points_possible)
    except Exception:
        final_points = float(total_score)

    try:
        submission = assignment.get_submission(req.student_id)
        submission.edit(submission={'posted_grade': final_points})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to post grade to Canvas: {e}")

    return {"ok": True, "posted_grade": final_points}


# ---------------------------------------------------------------------------
# POST grade to Canvas using stored Submission context (no user input required)
# ---------------------------------------------------------------------------
class PostGradeFromGradingRequest(BaseModel):
    grading_id: int

@router.post("/post_grade/from_grading")
def post_grade_from_grading(req: PostGradeFromGradingRequest):
    """
    Post a grading's total_score back to Canvas using the Submission record saved
    during ingest. This endpoint requires only a local grading_id and will
    read the Canvas connection info and Canvas IDs from the linked Submission.

    Behavior:
    - Prefer Canvas context stored on the Submission (canvas_base_url, canvas_api_token).
    - If missing, fall back to environment variables:
        CANVAS_BASE_URL, CANVAS_API_TOKEN, CANVAS_COURSE_ID (optional)
    - Uses submission.assignment_id and submission.student_id where available.
    """
    with Session(engine) as session:
        grading = session.get(Grading, req.grading_id)
        if not grading:
            raise HTTPException(status_code=404, detail="Grading not found")

        # Resolve essay -> submission
        essay = session.get(Essay, grading.essay_id) if getattr(grading, "essay_id", None) else None

        if not essay or not getattr(essay, "submission_id", None):
            raise HTTPException(status_code=400, detail="No linked Submission found for this grading")

        submission = session.get(Submission, essay.submission_id)
        if not submission:
            raise HTTPException(status_code=404, detail="Linked Submission not found")

        # Compute final points from grading.total_score (assumes 0-10 scale)
        total_score = getattr(grading, "total_score", None)
        if total_score is None:
            raise HTTPException(status_code=400, detail="Grading has no total_score")

        # Prefer submission-stored Canvas credentials, fall back to environment
        canvas_base_url = getattr(submission, "canvas_base_url", None) or os.getenv("CANVAS_BASE_URL")
        canvas_api_token = getattr(submission, "canvas_api_token", None) or os.getenv("CANVAS_API_TOKEN")

        if not canvas_base_url or not canvas_api_token:
            raise HTTPException(status_code=400, detail="No Canvas connection info available (submission or env)")

        # Prefer submission.course_id, fall back to env CANVAS_COURSE_ID if set.
        course_id = getattr(submission, "course_id", None) or (int(os.getenv("CANVAS_COURSE_ID")) if os.getenv("CANVAS_COURSE_ID") else None)

        # Use assignment_id and student_id from submission where possible
        assignment_id = getattr(submission, "assignment_id", None)
        student_id = getattr(submission, "student_id", None)

        if not assignment_id or not student_id:
            raise HTTPException(status_code=400, detail="Submission missing assignment_id or student_id")

        # Use Canvas client and post
        try:
            service = CanvasClientService(canvas_base_url, canvas_api_token)

            # Resolve assignment: course is required by canvasapi's course.get_assignment,
            # so ensure we have a course_id (from submission or env). If we don't, fail with clear message.
            if not course_id:
                raise RuntimeError("Course ID not available on submission and CANVAS_COURSE_ID not set in environment")

            course = service.get_course(course_id)
            assignment = service.get_assignment(course, assignment_id)

            # Determine points possible and compute final points
            points_possible = getattr(assignment, "points_possible", None) or getattr(assignment, "points", None) or 10.0
            try:
                final_points = float(total_score) / 10.0 * float(points_possible)
            except Exception:
                final_points = float(total_score)

            canvas_submission = assignment.get_submission(student_id)
            canvas_submission.edit(submission={'posted_grade': final_points})
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to post grade to Canvas: {e}")

    return {"ok": True, "posted_grade": final_points}
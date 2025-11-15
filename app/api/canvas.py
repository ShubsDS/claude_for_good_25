from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from pathlib import Path
import os
import requests

from sqlmodel import Session

# Handle both package and direct imports
try:
    from ..database import engine
    from ..models import Submission
except ImportError:
    from app.database import engine
    from app.models import Submission

try:
    from canvasapi import Canvas
except Exception:
    Canvas = None


class CanvasIngestRequest(BaseModel):
    canvas_base_url: str
    api_token: str
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
def ingest_submissions(req: CanvasIngestRequest):
    """
    Ingest submissions for an assignment from Canvas, download attached files (PDFs),
    and create Submission DB records with saved file paths.
    """
    service = CanvasClientService(req.canvas_base_url, req.api_token)
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

        file_paths_str = ",".join([f for f in saved_files if isinstance(f, str)])
        with Session(engine) as session:
            record = Submission(
                assignment_id=req.assignment_id,
                student_id=int(student_id) if student_id else 0,
                student_name=student_name,
                teacher=None,
                file_paths=file_paths_str
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            results.append({"submission_db_id": record.id, "student_id": student_id, "student_name": student_name, "files": saved_files})

    return {"ingested": results}
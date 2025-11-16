export interface Essay {
  id: number;
  filename: string;
  content: string;
  created_at: string;
}

export interface Rubric {
  id: number;
  name: string;
  content: string;
  criteria: Record<string, string>;
  created_at: string;
}

export interface Highlight {
  text: string;
  start: number;
  end: number;
  note?: string;
}

export interface CriterionResult {
  criterion: string;
  score: number;
  feedback: string;
  highlights: Highlight[];
}

export interface GradingResults {
  criteria_results: CriterionResult[];
  total_score?: number;
  overall_feedback?: string;
}

export interface Grading {
  id: number;
  essay_id: number;
  rubric_id: number;
  total_score: number;
  created_at: string;
  results: GradingResults;
}

export interface Assignment {
  id: number;
  name: string;
  teacher?: string;
}

export interface Submission {
  id: number;
  assignment_id: number;
  student_id: number;
  student_name?: string;
  teacher?: string;
  file_paths?: string;
}

export interface CanvasIngestRequest {
  canvas_base_url: string;
  api_token: string;
  course_id: number;
  assignment_id: number;
  student_id?: number | null;
}

export interface CanvasIngestResponse {
  ingested: Array<{
    submission_db_id: number;
    student_id: number;
    student_name: string;
    files: string[];
  }>;
}

export interface User {
  id: number;
  name: string;
  email: string;
}

export interface AuthResponse {
  token: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface SignupRequest {
  name: string;
  email: string;
  password: string;
}

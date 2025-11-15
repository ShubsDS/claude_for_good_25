import axios from 'axios';
import type {
  Essay,
  Rubric,
  Grading,
  CanvasIngestRequest,
  CanvasIngestResponse,
} from '../types';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Essay endpoints
export const uploadEssay = async (file: File): Promise<Essay> => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post<Essay>('/essays/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const getEssays = async (): Promise<Essay[]> => {
  const response = await api.get<Essay[]>('/essays/');
  return response.data;
};

export const getEssay = async (id: number): Promise<Essay> => {
  const response = await api.get<Essay>(`/essays/${id}`);
  return response.data;
};

export const deleteAllEssays = async (): Promise<{ ok: boolean; deleted: number }> => {
  const response = await api.delete<{ ok: boolean; deleted: number }>('/essays/');
  return response.data;
};

// Rubric endpoints
export const uploadRubric = async (file: File): Promise<Rubric> => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post<Rubric>('/rubrics/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const createRubricFromText = async (name: string, content: string): Promise<Rubric> => {
  // Create a file from text content
  const blob = new Blob([content], { type: 'text/plain' });
  const file = new File([blob], name, { type: 'text/plain' });
  return uploadRubric(file);
};

export const getRubrics = async (): Promise<Rubric[]> => {
  const response = await api.get<Rubric[]>('/rubrics/');
  return response.data;
};

export const getRubric = async (id: number): Promise<Rubric> => {
  const response = await api.get<Rubric>(`/rubrics/${id}`);
  return response.data;
};

// Grading endpoints
export const gradeEssay = async (essayId: number, rubricId: number): Promise<Grading> => {
  const formData = new FormData();
  formData.append('essay_id', essayId.toString());
  formData.append('rubric_id', rubricId.toString());
  const response = await api.post<Grading>('/grade', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
  return response.data;
};

export const getGradings = async (): Promise<Grading[]> => {
  const response = await api.get<Grading[]>('/gradings/');
  return response.data;
};

export const getGrading = async (id: number): Promise<Grading> => {
  const response = await api.get<Grading>(`/gradings/${id}`);
  return response.data;
};

// Canvas integration endpoints
export const ingestCanvasSubmissions = async (
  request: CanvasIngestRequest
): Promise<CanvasIngestResponse> => {
  const response = await api.post<CanvasIngestResponse>(
    '/canvas/submissions/ingest',
    request
  );
  return response.data;
};

// Health check
export const checkHealth = async (): Promise<{ status: string }> => {
  const response = await api.get('/health');
  return response.data;
};

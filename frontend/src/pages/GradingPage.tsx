import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Card, CardContent } from '../components/ui/card';
import { Loader2 } from 'lucide-react';
import { getEssays, gradeEssay } from '../services/api';
import type { Grading } from '../types';

export default function GradingPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { assignmentId, rubricId } = location.state || {};

  const [progress, setProgress] = useState(0);
  const [total, setTotal] = useState(0);
  const [currentStudent, setCurrentStudent] = useState('');
  const [gradings, setGradings] = useState<Grading[]>([]);
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    if (!assignmentId || !rubricId) {
      navigate('/teacher/upload');
      return;
    }

    startGrading();
  }, [assignmentId, rubricId]);

  const startGrading = async () => {
    try {
      // For now, we'll get all essays and grade them
      // In a real implementation, you'd filter by assignment_id
      const essays = await getEssays();
      console.log('Fetched essays:', essays);

      if (essays.length === 0) {
        alert('No essays found in the database. Please upload some essays first.');
        navigate('/teacher/upload');
        return;
      }

      setTotal(essays.length);

      const gradingResults: Grading[] = [];

      for (let i = 0; i < essays.length; i++) {
        const essay = essays[i];
        setCurrentStudent(essay.filename);
        setProgress(i + 1);

        try {
          const grading = await gradeEssay(essay.id, rubricId);
          console.log(`Graded essay ${essay.id}:`, grading);
          gradingResults.push(grading);
        } catch (error) {
          console.error(`Failed to grade essay ${essay.id}:`, error);
        }
      }

      console.log('All grading results:', gradingResults);
      setGradings(gradingResults);
      setIsComplete(true);

      if (gradingResults.length === 0) {
        alert('All essays failed to grade. Check console for errors.');
        navigate('/teacher/upload');
        return;
      }

      // Navigate to results after a short delay
      setTimeout(() => {
        navigate('/teacher/results', {
          state: {
            gradings: gradingResults,
            rubricId,
          },
        });
      }, 1500);
    } catch (error) {
      console.error('Error during grading:', error);
      alert(`Error during grading: ${error}`);
      navigate('/teacher/upload');
    }
  };

  const progressPercentage = total > 0 ? (progress / total) * 100 : 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardContent className="pt-6">
          <div className="text-center space-y-6">
            <div className="flex justify-center">
              {isComplete ? (
                <div className="h-16 w-16 rounded-full bg-green-100 flex items-center justify-center">
                  <svg
                    className="h-8 w-8 text-green-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                </div>
              ) : (
                <Loader2 className="h-16 w-16 text-blue-600 animate-spin" />
              )}
            </div>

            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                {isComplete ? 'Grading Complete!' : 'Grading in Progress'}
              </h2>
              <p className="text-gray-600">
                {isComplete
                  ? 'Redirecting to results...'
                  : `Processing submission ${progress} of ${total}`}
              </p>
              {!isComplete && currentStudent && (
                <p className="text-sm text-gray-500 mt-2">
                  Current: {currentStudent}
                </p>
              )}
            </div>

            {/* Progress Bar */}
            <div className="space-y-2">
              <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                <div
                  className="bg-blue-600 h-full transition-all duration-500 ease-out"
                  style={{ width: `${progressPercentage}%` }}
                />
              </div>
              <p className="text-sm text-gray-600">
                {Math.round(progressPercentage)}% complete
              </p>
            </div>

            {isComplete && (
              <div className="text-sm text-gray-600">
                Graded {gradings.length} submission{gradings.length !== 1 ? 's' : ''}
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { ChevronLeft, ChevronRight, Save, Home, Loader2 } from 'lucide-react';
import { getEssay } from '../services/api';
import type { Grading, Essay, CriterionResult } from '../types';

// Color mapping for criteria (from example_ui.html)
const CRITERION_COLORS: Record<string, string> = {
  THESIS: '#FFE0B2',
  CITATIONS: '#C8E6C9',
  SUPPORTING_EVIDENCE: '#BBDEFB',
  STRUCTURE: '#F8BBD0',
  REFERENCES: '#D1C4E9',
};

// Get color for a criterion, or default color
const getCriterionColor = (criterion: string): string => {
  return CRITERION_COLORS[criterion] || '#E0E0E0';
};

interface HighlightedTextProps {
  essayText: string;
  criteriaResults: CriterionResult[];
  activeCriterion: string | null;
}

function HighlightedText({ essayText, criteriaResults, activeCriterion }: HighlightedTextProps) {
  // Build all highlights sorted by position
  const allHighlights = criteriaResults.flatMap((cr) =>
    cr.highlights.map((h) => ({
      ...h,
      criterion: cr.criterion,
    }))
  );
  allHighlights.sort((a, b) => a.start - b.start);

  let lastPos = 0;
  const elements: JSX.Element[] = [];

  allHighlights.forEach((highlight, idx) => {
    // Add text before highlight
    if (highlight.start > lastPos) {
      elements.push(
        <span
          key={`text-${idx}`}
          style={{
            opacity: activeCriterion === null ? 1 : 0.3,
            transition: 'opacity 0.2s',
          }}
        >
          {essayText.slice(lastPos, highlight.start)}
        </span>
      );
    }

    // Add highlighted text
    const color = getCriterionColor(highlight.criterion);
    const isActive = activeCriterion === null || activeCriterion === highlight.criterion;
    const opacity = isActive ? 1 : 0.3;

    elements.push(
      <mark
        key={`highlight-${idx}`}
        style={{
          backgroundColor: color,
          opacity,
          transition: 'opacity 0.2s',
        }}
        data-criterion={highlight.criterion}
      >
        {essayText.slice(highlight.start, highlight.end)}
      </mark>
    );

    lastPos = highlight.end;
  });

  // Add remaining text
  if (lastPos < essayText.length) {
    elements.push(
      <span
        key="text-final"
        style={{
          opacity: activeCriterion === null ? 1 : 0.3,
          transition: 'opacity 0.2s',
        }}
      >
        {essayText.slice(lastPos)}
      </span>
    );
  }

  return <div className="whitespace-pre-wrap leading-relaxed">{elements}</div>;
}

export default function ResultsPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { gradings, rubricId } = location.state || {};

  const [currentIndex, setCurrentIndex] = useState(0);
  const [essays, setEssays] = useState<Record<number, Essay>>({});
  const [editedResults, setEditedResults] = useState<Record<number, CriterionResult[]>>({});
  const [activeCriterion, setActiveCriterion] = useState<string | null>(null);
  const [hasChanges, setHasChanges] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Only redirect if we have no gradings and we're not in the middle of loading
    if (!gradings || gradings.length === 0) {
      navigate('/teacher/upload');
      return;
    }

    // Load all essays
    loadEssays();
  }, []); // Run only once on mount

  const loadEssays = async () => {
    setIsLoading(true);
    const essayMap: Record<number, Essay> = {};
    const resultsMap: Record<number, CriterionResult[]> = {};

    for (const grading of gradings) {
      try {
        const essay = await getEssay(grading.essay_id);
        essayMap[grading.id] = essay;
        resultsMap[grading.id] = grading.results.criteria_results;
      } catch (error) {
        console.error(`Failed to load essay ${grading.essay_id}:`, error);
      }
    }

    setEssays(essayMap);
    setEditedResults(resultsMap);
    setIsLoading(false);
  };

  const currentGrading: Grading | undefined = gradings?.[currentIndex];
  const currentEssay = currentGrading ? essays[currentGrading.id] : undefined;
  const currentResults = currentGrading ? editedResults[currentGrading.id] : undefined;

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      setActiveCriterion(null);
    }
  };

  const handleNext = () => {
    if (currentIndex < gradings.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setActiveCriterion(null);
    }
  };

  const handleScoreChange = (criterionIndex: number, newScore: string) => {
    if (!currentGrading) return;

    const score = parseFloat(newScore);
    if (isNaN(score)) return;

    const updatedResults = [...currentResults];
    updatedResults[criterionIndex] = {
      ...updatedResults[criterionIndex],
      score,
    };

    setEditedResults({
      ...editedResults,
      [currentGrading.id]: updatedResults,
    });
    setHasChanges(true);
  };

  const handleFeedbackChange = (criterionIndex: number, newFeedback: string) => {
    if (!currentGrading) return;

    const updatedResults = [...currentResults];
    updatedResults[criterionIndex] = {
      ...updatedResults[criterionIndex],
      feedback: newFeedback,
    };

    setEditedResults({
      ...editedResults,
      [currentGrading.id]: updatedResults,
    });
    setHasChanges(true);
  };

  const handleSave = async () => {
    // TODO: Implement save functionality to backend
    console.log('Saving changes:', editedResults);
    setHasChanges(false);
    alert('Changes saved successfully!');
  };

  if (isLoading || !currentGrading || !currentEssay || !currentResults) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading results...</p>
        </div>
      </div>
    );
  }

  const totalScore = currentResults.reduce((sum, cr) => sum + cr.score, 0) / currentResults.length;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="icon" onClick={() => navigate('/')}>
                <Home className="h-5 w-5" />
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Grading Results</h1>
                <p className="text-sm text-gray-600">
                  {currentEssay.filename} - Score: {totalScore.toFixed(1)}/10
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              {hasChanges && (
                <Button onClick={handleSave} size="sm">
                  <Save className="mr-2 h-4 w-4" />
                  Save Changes
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-2 gap-6 h-[calc(100vh-200px)]">
          {/* Left Panel - Essay with Highlights */}
          <Card className="overflow-hidden flex flex-col">
            <CardHeader className="border-b border-gray-200">
              <CardTitle>Essay</CardTitle>
            </CardHeader>
            <CardContent className="flex-1 overflow-y-auto p-6">
              <HighlightedText
                essayText={currentEssay.content}
                criteriaResults={currentResults}
                activeCriterion={activeCriterion}
              />
            </CardContent>
          </Card>

          {/* Right Panel - Grading Criteria */}
          <div className="overflow-y-auto space-y-4">
            {currentResults.map((criterion, index) => (
              <Card
                key={criterion.criterion}
                className={`transition-shadow ${
                  activeCriterion === criterion.criterion ? 'ring-2 ring-blue-500' : ''
                }`}
                onMouseEnter={() => setActiveCriterion(criterion.criterion)}
                onMouseLeave={() => setActiveCriterion(null)}
              >
                <CardHeader
                  style={{
                    backgroundColor: getCriterionColor(criterion.criterion),
                  }}
                  className="pb-3"
                >
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{criterion.criterion}</CardTitle>
                    <div className="flex items-center gap-2">
                      <Input
                        type="number"
                        min="0"
                        max="10"
                        step="0.1"
                        value={criterion.score}
                        onChange={(e) => handleScoreChange(index, e.target.value)}
                        className="w-20 h-8 text-center font-bold"
                      />
                      <span className="text-sm font-medium">/ 10</span>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="pt-4">
                  <div className="space-y-3">
                    <div>
                      <label className="text-sm font-medium text-gray-700 mb-2 block">
                        Feedback
                      </label>
                      <Textarea
                        value={criterion.feedback}
                        onChange={(e) => handleFeedbackChange(index, e.target.value)}
                        rows={3}
                        className="resize-none"
                      />
                    </div>
                    <div className="text-sm text-gray-600">
                      {criterion.highlights.length} section{criterion.highlights.length !== 1 ? 's' : ''} highlighted
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Student Navigation */}
        <div className="mt-6 flex items-center justify-center gap-4">
          <Button
            variant="outline"
            onClick={handlePrevious}
            disabled={currentIndex === 0}
          >
            <ChevronLeft className="mr-2 h-4 w-4" />
            Previous
          </Button>

          <div className="text-sm text-gray-600">
            Student {currentIndex + 1} of {gradings.length}
          </div>

          <Button
            variant="outline"
            onClick={handleNext}
            disabled={currentIndex === gradings.length - 1}
          >
            Next
            <ChevronRight className="ml-2 h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}

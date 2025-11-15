import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Upload, FileText, Loader2 } from 'lucide-react';
import { createRubricFromText, uploadRubric } from '../services/api';

export default function UploadPage() {
  const navigate = useNavigate();
  const [assignmentId, setAssignmentId] = useState('');
  const [rubricFile, setRubricFile] = useState<File | null>(null);
  const [rubricText, setRubricText] = useState('');
  const [rubricName, setRubricName] = useState('');
  const [useTextEditor, setUseTextEditor] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleRubricFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setRubricFile(file);
      setError('');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!assignmentId) {
      setError('Please enter an assignment ID');
      return;
    }

    if (!useTextEditor && !rubricFile) {
      setError('Please upload a rubric file');
      return;
    }

    if (useTextEditor && (!rubricText || !rubricName)) {
      setError('Please provide both rubric name and content');
      return;
    }

    setIsLoading(true);

    try {
      // Upload the rubric
      let rubric;
      if (useTextEditor) {
        rubric = await createRubricFromText(rubricName, rubricText);
      } else if (rubricFile) {
        rubric = await uploadRubric(rubricFile);
      }

      console.log('Rubric uploaded successfully:', rubric);

      if (!rubric || !rubric.id) {
        throw new Error('Rubric upload succeeded but no ID was returned');
      }

      // Navigate to grading page with assignment ID and rubric ID
      navigate('/teacher/grading', {
        state: {
          assignmentId: parseInt(assignmentId),
          rubricId: rubric.id,
        },
      });
    } catch (err) {
      console.error('Error uploading rubric:', err);
      if (err instanceof Error) {
        setError(`Failed to upload rubric: ${err.message}`);
      } else {
        setError('Failed to upload rubric. Please try again.');
      }
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-3xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Upload Assignment</h1>
          <p className="text-gray-600">
            Enter the assignment details and upload your grading rubric
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="space-y-6">
            {/* Assignment ID Section */}
            <Card>
              <CardHeader>
                <CardTitle>Assignment Information</CardTitle>
                <CardDescription>
                  Enter the Canvas assignment ID to grade
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <label htmlFor="assignmentId" className="text-sm font-medium text-gray-700">
                    Assignment ID
                  </label>
                  <Input
                    id="assignmentId"
                    type="text"
                    placeholder="e.g., 12345"
                    value={assignmentId}
                    onChange={(e) => setAssignmentId(e.target.value)}
                    disabled={isLoading}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Rubric Upload Section */}
            <Card>
              <CardHeader>
                <CardTitle>Grading Rubric</CardTitle>
                <CardDescription>
                  Upload a rubric file or create one using the text editor
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Toggle between file upload and text editor */}
                <div className="flex gap-2">
                  <Button
                    type="button"
                    variant={!useTextEditor ? 'default' : 'outline'}
                    onClick={() => setUseTextEditor(false)}
                    disabled={isLoading}
                  >
                    <Upload className="mr-2 h-4 w-4" />
                    Upload File
                  </Button>
                  <Button
                    type="button"
                    variant={useTextEditor ? 'default' : 'outline'}
                    onClick={() => setUseTextEditor(true)}
                    disabled={isLoading}
                  >
                    <FileText className="mr-2 h-4 w-4" />
                    Text Editor
                  </Button>
                </div>

                {!useTextEditor ? (
                  // File Upload Mode
                  <div className="space-y-2">
                    <label htmlFor="rubricFile" className="text-sm font-medium text-gray-700">
                      Rubric File
                    </label>
                    <Input
                      id="rubricFile"
                      type="file"
                      accept=".txt,.md"
                      onChange={handleRubricFileChange}
                      disabled={isLoading}
                    />
                    {rubricFile && (
                      <p className="text-sm text-gray-600">
                        Selected: {rubricFile.name}
                      </p>
                    )}
                  </div>
                ) : (
                  // Text Editor Mode
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <label htmlFor="rubricName" className="text-sm font-medium text-gray-700">
                        Rubric Name
                      </label>
                      <Input
                        id="rubricName"
                        type="text"
                        placeholder="e.g., Essay Rubric 2024"
                        value={rubricName}
                        onChange={(e) => setRubricName(e.target.value)}
                        disabled={isLoading}
                      />
                    </div>
                    <div className="space-y-2">
                      <label htmlFor="rubricText" className="text-sm font-medium text-gray-700">
                        Rubric Content
                      </label>
                      <Textarea
                        id="rubricText"
                        placeholder="Enter your rubric content here...&#10;&#10;Example format:&#10;THESIS: Does the essay contain a clear thesis?&#10;CITATIONS: Are there proper citations?"
                        value={rubricText}
                        onChange={(e) => setRubricText(e.target.value)}
                        disabled={isLoading}
                        rows={12}
                        className="font-mono text-sm"
                      />
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                {error}
              </div>
            )}

            {/* Submit Button */}
            <div className="flex gap-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => navigate('/')}
                disabled={isLoading}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button type="submit" disabled={isLoading} className="flex-1">
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Processing...
                  </>
                ) : (
                  'Start Grading'
                )}
              </Button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}

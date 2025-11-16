import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Upload, FileText, Loader2, FolderOpen } from 'lucide-react';
import { createRubricFromText, uploadRubric, deleteAllEssays, loadEssaysFromFolder } from '../services/api';

export default function UploadPage() {
  const navigate = useNavigate();
  const [rubricFile, setRubricFile] = useState<File | null>(null);
  const [rubricText, setRubricText] = useState('');
  const [rubricName, setRubricName] = useState('');
  const [useTextEditor, setUseTextEditor] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
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

    // Validate rubric
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
      // Step 1: Delete all existing essays
      setLoadingMessage('Clearing existing essays...');
      console.log('Deleting all existing essays from database');
      const deleteResult = await deleteAllEssays();
      console.log(`Deleted ${deleteResult.deleted} existing essay(s)`);

      // Step 2: Load essays from example_essays folder
      setLoadingMessage('Loading essays from folder...');
      console.log('Loading essays from example_essays folder');

      const loadedEssays = await loadEssaysFromFolder();
      console.log('Loaded essays:', loadedEssays);

      if (!loadedEssays || loadedEssays.length === 0) {
        throw new Error('No essays found in example_essays folder');
      }

      setLoadingMessage(`Loaded ${loadedEssays.length} essay(s). Processing...`);

      // Step 3: Upload the rubric
      setLoadingMessage('Uploading rubric...');
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

      // Step 4: Navigate to grading page
      setLoadingMessage('Starting grading process...');
      navigate('/teacher/grading', {
        state: {
          rubricId: rubric.id,
        },
      });
    } catch (err) {
      console.error('Error during upload process:', err);
      if (err instanceof Error) {
        setError(`Failed: ${err.message}`);
      } else {
        setError('Failed to process essays. Please try again.');
      }
      setIsLoading(false);
      setLoadingMessage('');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-3xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Grade Essays</h1>
          <p className="text-gray-600">
            Upload your grading rubric and grade essays from the example_essays folder
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="space-y-6">
            {/* Info Card */}
            <Card className="bg-blue-50 border-blue-200">
              <CardContent className="pt-6">
                <div className="flex items-start gap-3">
                  <FolderOpen className="h-5 w-5 text-blue-600 mt-0.5" />
                  <div>
                    <p className="text-sm text-blue-900 font-medium">Essays will be loaded from example_essays folder</p>
                    <p className="text-sm text-blue-700 mt-1">All .txt files in the example_essays folder will be automatically loaded and graded.</p>
                  </div>
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

            {/* Loading Message */}
            {isLoading && loadingMessage && (
              <div className="bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded">
                <div className="flex items-center">
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  {loadingMessage}
                </div>
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

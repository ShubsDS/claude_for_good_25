import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { GraduationCap, UserCircle } from 'lucide-react';

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-4xl w-full">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            AI Essay Grading System
          </h1>
          <p className="text-xl text-gray-600">
            Streamline your grading process with AI-powered analysis
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer border-2 hover:border-blue-500">
            <CardHeader>
              <div className="flex justify-center mb-4">
                <GraduationCap className="h-16 w-16 text-blue-600" />
              </div>
              <CardTitle className="text-center text-2xl">Teacher</CardTitle>
              <CardDescription className="text-center text-base">
                Upload assignments and rubrics to grade student submissions
              </CardDescription>
            </CardHeader>
            <CardContent className="flex justify-center pb-6">
              <Button
                size="lg"
                className="w-full max-w-xs"
                onClick={() => navigate('/teacher/upload')}
              >
                Continue as Teacher
              </Button>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow cursor-pointer border-2 hover:border-indigo-500 opacity-60">
            <CardHeader>
              <div className="flex justify-center mb-4">
                <UserCircle className="h-16 w-16 text-indigo-600" />
              </div>
              <CardTitle className="text-center text-2xl">Student</CardTitle>
              <CardDescription className="text-center text-base">
                View your graded assignments and feedback
              </CardDescription>
            </CardHeader>
            <CardContent className="flex justify-center pb-6">
              <Button
                size="lg"
                className="w-full max-w-xs"
                variant="outline"
                disabled
              >
                Coming Soon
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

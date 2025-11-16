import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { GraduationCap, UserCircle, LogOut } from 'lucide-react';
import Logo from '../components/Logo';

export default function Home() {
  const navigate = useNavigate();
  const { isAuthenticated, logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-4xl w-full">
        {isAuthenticated && (
          <div className="flex justify-end mb-4">
            <Button variant="outline" onClick={handleLogout}>
              <LogOut className="mr-2 h-4 w-4" />
              Logout
            </Button>
          </div>
        )}
        <div className="text-center mb-12">
          <div className="flex justify-center mb-6">
            <Logo size="xl" />
          </div>
          <p className="text-xl text-gray-600">
            AI-Powered Essay Grading with Character-Level Highlighting
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

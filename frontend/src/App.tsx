import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Home from './pages/Home';
import UploadPage from './pages/UploadPage';
import GradingPage from './pages/GradingPage';
import ResultsPage from './pages/ResultsPage';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/teacher/upload" element={<UploadPage />} />
          <Route path="/teacher/grading" element={<GradingPage />} />
          <Route path="/teacher/results" element={<ResultsPage />} />
        </Routes>
      </Router>
    </QueryClientProvider>
  );
}

export default App;

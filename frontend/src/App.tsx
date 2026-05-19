import { lazy, Suspense, useState, useCallback } from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import ErrorBoundary from './components/ErrorBoundary';
import Layout from './components/Layout';
import SplashScreen from './components/SplashScreen';

const LearningStudioDemoPage = lazy(() => import('./pages/LearningStudioDemoPage'));
const MistakeBookPage = lazy(() => import('./pages/MistakeBookPage'));
const ProfilePage = lazy(() => import('./pages/ProfilePage'));

function PageLoader() {
  return (
    <div className="flex h-64 items-center justify-center">
      <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary-500 border-t-transparent" />
    </div>
  );
}

function App() {
  const [showSplash, setShowSplash] = useState(
    () => !sessionStorage.getItem('splash-seen')
  );

  const handleSplashComplete = useCallback(() => {
    sessionStorage.setItem('splash-seen', '1');
    setShowSplash(false);
  }, []);

  return (
    <ErrorBoundary>
      {showSplash && <SplashScreen onComplete={handleSplashComplete} />}
      <BrowserRouter>
        <Suspense fallback={<PageLoader />}>
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<LearningStudioDemoPage mode="qna" />} />
              <Route path="engine" element={<LearningStudioDemoPage mode="engine" />} />
              <Route path="mistakes" element={<MistakeBookPage />} />
              <Route path="profile" element={<ProfilePage />} />
            </Route>
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
      </BrowserRouter>
    </ErrorBoundary>
  );
}

export default App;

import { Routes, Route } from 'react-router-dom';
import { AuthProvider } from './hooks/useAuth.jsx';
import ProtectedRoute from './components/ProtectedRoute';
import Dashboard from './components/Dashboard';
import AuthPage from './components/AuthPage';
import './App.css';
import { Analytics } from '@vercel/analytics/react';

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<AuthPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
      </Routes>
      <Analytics />
    </AuthProvider>
  );
}

export default App;
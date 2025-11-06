import { AuthProvider } from './hooks/useAuth.jsx';
import ProtectedRoute from './components/ProtectedRoute';
import Dashboard from './components/Dashboard';
import './App.css';
import { Analytics } from '@vercel/analytics/react';

function App() {
  return (
    <div>
      <AuthProvider>
        <ProtectedRoute>
          <Dashboard />
        </ProtectedRoute>
      </AuthProvider>
      <Analytics />
    </div>
  );
}

export default App;
import { AuthProvider } from './hooks/useAuth.jsx';
import ProtectedRoute from './components/ProtectedRoute';
import Dashboard from './components/Dashboard';
import './App.css';

function App() {
  return (
    <div>
      <AuthProvider>
        <ProtectedRoute>
          <Dashboard />
        </ProtectedRoute>
      </AuthProvider>
    </div>
  );
}

export default App;
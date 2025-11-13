import { useState } from 'react';
import { useAuth } from '../hooks/useAuth.jsx';
import Settings from './Settings.jsx';
import DashboardPage from './DashboardPage.jsx'; // Importar a nova página
import PeriodSelector from './PeriodSelector.jsx';
import InvestmentForm from './InvestmentForm.jsx';
import GoalsPage from './GoalsPage.jsx';
import Charts from './Charts.jsx';
import { Sun, Moon } from 'lucide-react';
import { useTheme } from '../context/ThemeProvider.jsx';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [period, setPeriod] = useState({
    year: new Date().getFullYear(),
    month: new Date().getMonth() + 1
  });
  const [activeView, setActiveView] = useState('dashboard');

  if (!user) {
    return (
      <div className="flex justify-center items-center min-h-screen bg-background">
        <div className="text-muted-foreground">Carregando...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* HEADER */}
      <header className="bg-card p-4 flex justify-between items-center">
        <div className="flex flex-col items-start">
          <div className="flex items-center space-x-2">
            {/* Logo/Icone Livro */}
            <span className="text-2xl">📚</span>
            <h1 className="text-xl font-bold">Organizador Financeiro</h1>
          </div>
          {user && <span className="text-sm text-muted-foreground">Bem vindo, {user.username}!</span>}
        </div>
        <div className="flex items-center space-x-4">
          <button
            onClick={logout}
            className="bg-destructive hover:bg-destructive/90 text-destructive-foreground px-4 py-2 rounded-md font-medium transition-colors"
          >
            Sair
          </button>
        </div>
      </header>

      {/* MENU SUPERIOR */}
      <nav className="bg-card px-4 py-2 flex space-x-4 border-b border-border">
        <button
          onClick={() => setActiveView('dashboard')}
          className={`px-4 py-2 rounded-md ${activeView === 'dashboard' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground'}`}
        >
          Dashboard
        </button>
        <button
          onClick={() => setActiveView('goals')}
          className={`px-4 py-2 rounded-md ${activeView === 'goals' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground'}`}
        >
          Metas
        </button>
        <button
          onClick={() => setActiveView('reports')}
          className={`px-4 py-2 rounded-md ${activeView === 'reports' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground'}`}
        >
          Relatórios
        </button>
        <button
          onClick={() => setActiveView('settings')}
          className={`px-4 py-2 rounded-md ${activeView === 'settings' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground'}`}
        >
          Configurações
        </button>
      </nav>

      <main className="container mx-auto py-6 space-y-6">
        {activeView === 'dashboard' && (
          <div className="bg-card rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold mb-4">Visão Geral do Dashboard</h3>
            <DashboardPage period={period} />
          </div>
        )}

        {activeView === 'goals' && (
          <div className="bg-card rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold mb-4">Minhas Metas</h3>
            <GoalsPage />
          </div>
        )}

        {activeView === 'reports' && (
          <div className="bg-card rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold mb-4">Relatórios e Análises</h3>
            <Charts period={period} />
          </div>
        )}

        {activeView === 'settings' && (
          <div className="bg-card rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold mb-4">Configurações</h3>
            <Settings />
          </div>
        )}
      </main>
    </div>
  );
};

export default Dashboard;

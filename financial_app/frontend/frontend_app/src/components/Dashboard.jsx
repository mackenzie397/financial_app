import { useState } from 'react';
import { useAuth } from '../hooks/useAuth.jsx';
import TransactionList from './TransactionList.jsx';
import Settings from './Settings.jsx';
import DashboardCards from './DashboardCards.jsx';
import PeriodSelector from './PeriodSelector.jsx';
import TransactionForm from './TransactionForm.jsx';
import InvestmentForm from './InvestmentForm.jsx';
import GoalForm from './GoalForm.jsx';
import Charts from './Charts.jsx';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('transactions');
  const [showTransactionForm, setShowTransactionForm] = useState(false);
  const [showInvestmentForm, setShowInvestmentForm] = useState(false);
  const [showGoalForm, setShowGoalForm] = useState(false);
  const [period, setPeriod] = useState({
    year: new Date().getFullYear(),
    month: new Date().getMonth() + 1
  });

  if (!user) {
    return (
      <div className="flex justify-center items-center min-h-screen bg-background">
        <div className="text-muted-foreground">Carregando...</div>
      </div>
    );
  }

  const handleTransactionSaved = () => {
    setShowTransactionForm(false);
  };

  const handleInvestmentSaved = () => {
    setShowInvestmentForm(false);
  };

  const handleGoalSaved = () => {
    setShowGoalForm(false);
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'transactions':
        return (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold text-foreground">Lançamentos</h3>
              <button
                onClick={() => setShowTransactionForm(true)}
                className="bg-primary hover:bg-primary/90 text-primary-foreground px-4 py-2 rounded-md transition-colors duration-200"
              >
                Nova Transação
              </button>
            </div>
            <TransactionList 
              period={period} 
              onTransactionChange={() => {}} 
            />
          </div>
        );
      
      case 'investments':
        return (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold text-foreground">Investimentos</h3>
              <button
                onClick={() => setShowInvestmentForm(true)}
                className="bg-primary hover:bg-primary/90 text-primary-foreground px-4 py-2 rounded-md transition-colors duration-200"
              >
                Novo Investimento
              </button>
            </div>
            {/* A lista de investimentos será renderizada aqui */}
          </div>
        );
      
      case 'goals':
        return (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold text-foreground">Metas</h3>
              <button
                onClick={() => setShowGoalForm(true)}
                className="bg-primary hover:bg-primary/90 text-primary-foreground px-4 py-2 rounded-md transition-colors duration-200"
              >
                Nova Meta
              </button>
            </div>
            {/* A lista de metas será renderizada aqui */}
          </div>
        );
      
      case 'reports':
        return (
          <div className="space-y-6">
            <div className="bg-card rounded-lg border border-border p-6">
              <h3 className="text-lg font-semibold text-foreground mb-4">
                📊 Relatórios e Análises
              </h3>
              <p className="text-muted-foreground mb-6">
                Visualize seus dados financeiros através de gráficos e análises detalhadas.
              </p>
            </div>
            <Charts period={period} />
          </div>
        );
      
      case 'settings':
        return <Settings />;
      
      default:
        return <div>Página não encontrada</div>;
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-card border-b border-border px-4 py-3">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-xl font-bold text-foreground">Organização Financeira</h1>
            <p className="text-sm text-muted-foreground">Bem-vindo, {user?.username}!</p>
          </div>
          <button
            onClick={logout}
            className="bg-destructive hover:bg-destructive/90 text-destructive-foreground px-4 py-2 rounded-md font-medium transition-colors"
          >
            Sair
          </button>
        </div>
      </header>

      {/* Period Selector */}
      <div className="bg-card border-b border-border px-4 py-3">
        <PeriodSelector period={period} onPeriodChange={setPeriod} />
      </div>

      {/* Dashboard Cards */}
      <div className="bg-card border-b border-border px-4 py-4">
        <DashboardCards period={period} />
      </div>

      {/* Navigation Tabs */}
      <div className="bg-card border-b border-border px-4">
        <div className="flex space-x-1 overflow-x-auto">
          <button
            onClick={() => setActiveTab('transactions')}
            className={`flex items-center space-x-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
              activeTab === 'transactions'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            <span>📝</span>
            <span>Lançamentos</span>
          </button>
          
          <button
            onClick={() => setActiveTab('investments')}
            className={`flex items-center space-x-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
              activeTab === 'investments'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            <span>📈</span>
            <span>Investimentos</span>
          </button>
          
          <button
            onClick={() => setActiveTab('goals')}
            className={`flex items-center space-x-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
              activeTab === 'goals'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            <span>🎯</span>
            <span>Metas</span>
          </button>
          
          <button
            onClick={() => setActiveTab('reports')}
            className={`flex items-center space-x-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
              activeTab === 'reports'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            <span>📊</span>
            <span>Relatórios</span>
          </button>
          
          <button
            onClick={() => setActiveTab('settings')}
            className={`flex items-center space-x-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
              activeTab === 'settings'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            <span>⚙️</span>
            <span>Configurações</span>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <main className="p-4">
        {renderTabContent()}
      </main>

      {/* Modals */}
      {showTransactionForm && (
        <TransactionForm
          onSave={handleTransactionSaved}
          onCancel={() => setShowTransactionForm(false)}
        />
      )}
      {showInvestmentForm && (
        <InvestmentForm
          onSave={handleInvestmentSaved}
          onCancel={() => setShowInvestmentForm(false)}
        />
      )}
      {showGoalForm && (
        <GoalForm
          onSave={handleGoalSaved}
          onCancel={() => setShowGoalForm(false)}
        />
      )}
    </div>
  );
};

export default Dashboard;
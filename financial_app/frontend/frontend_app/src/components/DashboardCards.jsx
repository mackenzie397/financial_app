import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth.jsx';
import api from '../lib/api.js';

const DashboardCards = ({ period }) => {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState({
    balance: 0,
    totalIncome: 0,
    totalExpense: 0,
    totalInvestments: 0,
    transactionCount: 0
  });
  const [loading, setLoading] = useState(true);

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value || 0);
  };

  const fetchDashboardData = async () => {
    if (!user || !period) return;

    try {
      setLoading(true);
      
      // Buscar transações do período
      const response = await api.get('/transactions', {
        params: {
          user_id: user.id,
          year: period.year,
          month: period.month
        }
      });
      
      const transactions = response.data || [];
      
      // Calcular totais
      const income = transactions
        .filter(t => t.transaction_type === 'income')
        .reduce((sum, t) => sum + (t.amount || 0), 0);
      
      const expense = transactions
        .filter(t => t.transaction_type === 'expense')
        .reduce((sum, t) => sum + (t.amount || 0), 0);
      
      setDashboardData({
        balance: income - expense,
        totalIncome: income,
        totalExpense: expense,
        totalInvestments: 0, // Para implementar futuramente
        transactionCount: transactions.length
      });
      
    } catch (error) {
      console.error('Erro ao carregar dados do dashboard:', error);
      // Manter valores padrão em caso de erro
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [user, period]);

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="bg-card rounded-lg shadow p-6 animate-pulse">
            <div className="h-4 bg-muted rounded mb-2"></div>
            <div className="h-8 bg-muted rounded mb-2"></div>
            <div className="h-3 bg-muted rounded"></div>
          </div>
        ))}
      </div>
    );
  }

  const cards = [
    {
      title: 'Saldo',
      value: dashboardData.balance,
      color: dashboardData.balance >= 0 ? 'text-primary' : 'text-destructive',
      bgColor: 'bg-card',
      subtitle: `${dashboardData.transactionCount} transações este mês`,
      icon: '💰'
    },
    {
      title: 'Receitas',
      value: dashboardData.totalIncome,
      color: 'text-primary',
      bgColor: 'bg-card',
      subtitle: 'Este mês',
      icon: '📈'
    },
    {
      title: 'Despesas',
      value: dashboardData.totalExpense,
      color: 'text-destructive',
      bgColor: 'bg-card',
      subtitle: 'Este mês',
      icon: '📉'
    },
    {
      title: 'Investimentos',
      value: dashboardData.totalInvestments,
      color: 'text-primary',
      bgColor: 'bg-card',
      subtitle: 'Total investido',
      icon: '📊'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {cards.map((card, index) => (
        <div key={index} className={`${card.bgColor} rounded-lg shadow p-6 border-l-4 border-l-border`}>
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-muted-foreground">{card.title}</h3>
            <span className="text-2xl">{card.icon}</span>
          </div>
          <p className={`text-2xl font-bold ${card.color} mb-1`}>
            {formatCurrency(card.value)}
          </p>
          <p className="text-xs text-muted-foreground">{card.subtitle}</p>
          
          {/* Indicador de variação */}
          {card.title === 'Saldo' && (
            <div className="mt-2 flex items-center">
              <span className={`text-xs ${card.color}`}>
                {dashboardData.balance >= 0 ? '↗' : '↘'} 
                {dashboardData.balance >= 0 ? ' Positivo' : ' Negativo'}
              </span>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default DashboardCards;
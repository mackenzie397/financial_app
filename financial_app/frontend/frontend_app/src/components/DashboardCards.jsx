import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth.jsx';
import api from '../lib/api.js';
import { DollarSign, ArrowUp, ArrowDown } from 'lucide-react';

const DashboardCards = ({ period }) => {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState({
    balance: 0,
    totalIncome: 0,
    totalExpense: 0,
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
      <>
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-card rounded-lg shadow-md p-6 animate-pulse">
            <div className="h-4 bg-muted rounded mb-2"></div>
            <div className="h-8 bg-muted rounded mb-2"></div>
            <div className="h-3 bg-muted rounded"></div>
          </div>
        ))}
      </>
    );
  }

  const cards = [
    {
      title: 'Saldo Atual',
      value: dashboardData.balance,
      color: 'text-foreground',
      icon: <DollarSign className="h-8 w-8 text-foreground" />,
    },
    {
      title: 'Receita Total',
      value: dashboardData.totalIncome,
      color: 'text-primary',
      icon: <ArrowUp className="h-8 w-8 text-primary" />,
    },
    {
      title: 'Despesa Total',
      value: dashboardData.totalExpense,
      color: 'text-destructive',
      icon: <ArrowDown className="h-8 w-8 text-destructive" />,
    },
  ];

  return (
      <>
      {cards.map((card, index) => (
        <div key={index} className="bg-card rounded-lg shadow-md p-10">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-2xl font-medium text-foreground">{card.title}</h3>
            {card.icon}
          </div>
          <p className={`text-5xl font-bold ${card.color}`}>
            {formatCurrency(card.value)}
          </p>
        </div>
      ))}
      </>
  );
};

export default DashboardCards;
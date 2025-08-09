import { useState, useEffect } from 'react';
import { useAuth } from './useAuth.jsx';
import api from '../lib/api.js';

export const useDashboard = (period = null) => {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState({
    balance: 0,
    totalIncome: 0,
    totalExpense: 0,
    totalInvestments: 0,
    transactionCount: 0,
    loading: true,
    error: null
  });

  const [currentPeriod, setCurrentPeriod] = useState(
    period || {
      month: new Date().getMonth() + 1,
      year: new Date().getFullYear()
    }
  );

  const fetchDashboardData = async () => {
    if (!user) return;

    try {
      setDashboardData(prev => ({ ...prev, loading: true, error: null }));

      // Buscar resumo de transações
      const transactionSummaryResponse = await api.get('/transactions/summary', {
        params: {
          user_id: user.id,
          year: currentPeriod.year,
          month: currentPeriod.month
        }
      });

      // Buscar total de investimentos
      const investmentsResponse = await api.get('/investments', {
        params: {
          user_id: user.id,
          year: currentPeriod.year,
          month: currentPeriod.month
        }
      });

      const transactionSummary = transactionSummaryResponse.data;
      const investments = investmentsResponse.data;

      const totalInvestments = investments.reduce((sum, inv) => sum + parseFloat(inv.amount || 0), 0);
      const balance = transactionSummary.total_income - transactionSummary.total_expense;

      setDashboardData({
        balance: balance,
        totalIncome: transactionSummary.total_income || 0,
        totalExpense: transactionSummary.total_expense || 0,
        totalInvestments: totalInvestments,
        transactionCount: transactionSummary.transaction_count || 0,
        loading: false,
        error: null
      });

    } catch (error) {
      console.error('Erro ao carregar dados do dashboard:', error);
      setDashboardData(prev => ({
        ...prev,
        loading: false,
        error: 'Erro ao carregar dados do dashboard'
      }));
    }
  };

  const updatePeriod = (newPeriod) => {
    setCurrentPeriod(newPeriod);
  };

  const navigatePeriod = (direction) => {
    setCurrentPeriod(prev => {
      let newMonth = prev.month;
      let newYear = prev.year;
      
      if (direction === 'prev') {
        newMonth = prev.month === 1 ? 12 : prev.month - 1;
        newYear = prev.month === 1 ? prev.year - 1 : prev.year;
      } else {
        newMonth = prev.month === 12 ? 1 : prev.month + 1;
        newYear = prev.month === 12 ? prev.year + 1 : prev.year;
      }
      
      return { month: newMonth, year: newYear };
    });
  };

  const refreshData = () => {
    fetchDashboardData();
  };

  useEffect(() => {
    fetchDashboardData();
  }, [user, currentPeriod]);

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value || 0);
  };

  const getMonthName = (month) => {
    const monthNames = [
      'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
      'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ];
    return monthNames[month - 1];
  };

  return {
    dashboardData,
    currentPeriod,
    updatePeriod,
    navigatePeriod,
    refreshData,
    formatCurrency,
    getMonthName
  };
};


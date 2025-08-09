import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth.jsx';
import api from '../lib/api.js';

const Charts = ({ period }) => {
  const { user } = useAuth();
  const [chartData, setChartData] = useState({
    categoryExpenses: [],
    monthlyTrend: [],
    paymentMethods: []
  });
  const [loading, setLoading] = useState(true);

  const fetchChartData = async () => {
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
      
      const transactions = response.data;
      
      // Processar dados para gráficos
      const categoryExpenses = processExpensesByCategory(transactions);
      const paymentMethods = processPaymentMethods(transactions);
      
      setChartData({
        categoryExpenses,
        paymentMethods,
        monthlyTrend: [] // Para implementar futuramente
      });
      
    } catch (error) {
      console.error('Erro ao carregar dados dos gráficos:', error);
    } finally {
      setLoading(false);
    }
  };

  const processExpensesByCategory = (transactions) => {
    const expenses = transactions.filter(t => t.transaction_type === 'expense');
    const categoryTotals = {};
    
    expenses.forEach(transaction => {
      const category = transaction.category_name || 'Sem categoria';
      categoryTotals[category] = (categoryTotals[category] || 0) + transaction.amount;
    });
    
    return Object.entries(categoryTotals)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value);
  };

  const processPaymentMethods = (transactions) => {
    const methodTotals = {};
    
    transactions.forEach(transaction => {
      const method = transaction.payment_method_name || 'Sem método';
      methodTotals[method] = (methodTotals[method] || 0) + transaction.amount;
    });
    
    return Object.entries(methodTotals)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value);
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value || 0);
  };

  const getColorForIndex = (index) => {
    const colors = [
      '#3B82F6', '#EF4444', '#10B981', '#F59E0B', 
      '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16'
    ];
    return colors[index % colors.length];
  };

  useEffect(() => {
    fetchChartData();
  }, [user, period]);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="bg-card rounded-lg p-6 animate-pulse">
          <div className="h-6 bg-muted rounded w-48 mb-4"></div>
          <div className="h-32 bg-muted rounded"></div>
        </div>
        <div className="bg-card rounded-lg p-6 animate-pulse">
          <div className="h-6 bg-muted rounded w-48 mb-4"></div>
          <div className="h-32 bg-muted rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Gráfico de Despesas por Categoria */}
      <div className="bg-card rounded-lg border border-border p-6">
        <h3 className="text-lg font-semibold text-foreground mb-4">
          Despesas por Categoria
        </h3>
        
        {chartData.categoryExpenses.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <div className="text-4xl mb-2">📊</div>
            <p>Nenhuma despesa encontrada para este período</p>
          </div>
        ) : (
          <div className="space-y-3">
            {chartData.categoryExpenses.map((item, index) => {
              const total = chartData.categoryExpenses.reduce((sum, cat) => sum + cat.value, 0);
              const percentage = total > 0 ? (item.value / total) * 100 : 0;
              
              return (
                <div key={item.name} className="flex items-center space-x-3">
                  <div 
                    className="w-4 h-4 rounded-full flex-shrink-0"
                    style={{ backgroundColor: getColorForIndex(index) }}
                  ></div>
                  <div className="flex-1 min-w-0">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-sm font-medium text-foreground truncate">
                        {item.name}
                      </span>
                      <span className="text-sm text-muted-foreground">
                        {formatCurrency(item.value)} ({percentage.toFixed(1)}%)
                      </span>
                    </div>
                    <div className="w-full bg-muted rounded-full h-2">
                      <div 
                        className="h-2 rounded-full transition-all duration-300"
                        style={{ 
                          width: `${percentage}%`,
                          backgroundColor: getColorForIndex(index)
                        }}
                      ></div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Gráfico de Formas de Pagamento */}
      <div className="bg-card rounded-lg border border-border p-6">
        <h3 className="text-lg font-semibold text-foreground mb-4">
          Uso por Forma de Pagamento
        </h3>
        
        {chartData.paymentMethods.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <div className="text-4xl mb-2">💳</div>
            <p>Nenhuma transação encontrada para este período</p>
          </div>
        ) : (
          <div className="space-y-3">
            {chartData.paymentMethods.map((item, index) => {
              const total = chartData.paymentMethods.reduce((sum, method) => sum + method.value, 0);
              const percentage = total > 0 ? (item.value / total) * 100 : 0;
              
              return (
                <div key={item.name} className="flex items-center space-x-3">
                  <div 
                    className="w-4 h-4 rounded-full flex-shrink-0"
                    style={{ backgroundColor: getColorForIndex(index + 4) }}
                  ></div>
                  <div className="flex-1 min-w-0">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-sm font-medium text-foreground truncate">
                        {item.name}
                      </span>
                      <span className="text-sm text-muted-foreground">
                        {formatCurrency(item.value)} ({percentage.toFixed(1)}%)
                      </span>
                    </div>
                    <div className="w-full bg-muted rounded-full h-2">
                      <div 
                        className="h-2 rounded-full transition-all duration-300"
                        style={{ 
                          width: `${percentage}%`,
                          backgroundColor: getColorForIndex(index + 4)
                        }}
                      ></div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Resumo Rápido */}
      <div className="bg-card rounded-lg border border-border p-6">
        <h3 className="text-lg font-semibold text-foreground mb-4">
          Resumo do Período
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-primary">
              {chartData.categoryExpenses.length}
            </div>
            <div className="text-sm text-muted-foreground">Categorias com gastos</div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-primary">
              {chartData.paymentMethods.length}
            </div>
            <div className="text-sm text-muted-foreground">Formas de pagamento usadas</div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-primary">
              {formatCurrency(
                chartData.categoryExpenses.reduce((sum, cat) => sum + cat.value, 0)
              )}
            </div>
            <div className="text-sm text-muted-foreground">Total de despesas</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Charts;
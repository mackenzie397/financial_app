import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth.jsx';
import api from '../lib/api.js';

const TransactionList = ({ period, onTransactionChange }) => {
  const { user } = useAuth();
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchTransactions = async () => {
    if (!user || !period) return;

    try {
      setLoading(true);
      setError(null);
      
      const response = await api.get('/transactions', {
        params: {
          user_id: user.id,
          year: period.year,
          month: period.month
        }
      });
      
      setTransactions(response.data);
    } catch (error) {
      console.error('Erro ao carregar transações:', error);
      setError('Erro ao carregar transações');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteTransaction = async (id) => {
    if (!window.confirm('Tem certeza que deseja excluir esta transação?')) return;

    try {
      await api.delete(`/transactions/${id}`);
      setTransactions(prev => prev.filter(t => t.id !== id));
      if (onTransactionChange) onTransactionChange();
    } catch (error) {
      console.error('Erro ao excluir transação:', error);
      alert('Erro ao excluir transação');
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value || 0);
  };

  const formatDate = (dateString) => {
    return new Date(dateString + 'T00:00:00').toLocaleDateString('pt-BR');
  };

  useEffect(() => {
    fetchTransactions();
  }, [user, period]);

  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-card rounded-lg p-4 animate-pulse">
            <div className="flex justify-between items-center">
              <div className="space-y-2">
                <div className="h-4 bg-muted rounded w-32"></div>
                <div className="h-3 bg-muted rounded w-24"></div>
              </div>
              <div className="h-6 bg-muted rounded w-20"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-destructive/20 border border-destructive text-destructive-foreground rounded-lg p-4">
        <p>{error}</p>
      </div>
    );
  }

  if (transactions.length === 0) {
    return (
      <div className="text-center py-12 bg-card rounded-lg p-4">
        <div className="text-muted-foreground text-6xl mb-4">📊</div>
        <h3 className="text-lg font-medium text-foreground mb-2">
          Nenhuma transação encontrada
        </h3>
        <p className="text-muted-foreground mb-4">
          Não há transações registradas para este período.
        </p>
        <p className="text-muted-foreground text-sm">
          Clique em "Nova Transação" para começar a registrar suas movimentações financeiras.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h4 className="text-md font-medium text-foreground">
          {transactions.length} transação{transactions.length !== 1 ? 'ões' : ''} encontrada{transactions.length !== 1 ? 's' : ''}
        </h4>
      </div>

      <div className="space-y-3">
        {transactions.map((transaction) => (
          <div
            key={transaction.id}
            className="bg-card border border-border rounded-lg p-4 hover:shadow-md transition-shadow duration-200"
          >
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-2">
                  <h5 className="font-medium text-foreground">
                    {transaction.description}
                  </h5>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    transaction.transaction_type === 'income'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {transaction.transaction_type === 'income' ? 'Receita' : 'Despesa'}
                  </span>
                </div>
                
                <div className="text-sm text-muted-foreground space-y-1">
                  <p>Data: {formatDate(transaction.date)}</p>
                  {transaction.category_name && (
                    <p>Categoria: {transaction.category_name}</p>
                  )}
                  {transaction.payment_method_name && (
                    <p>Forma de pagamento: {transaction.payment_method_name}</p>
                  )}
                  {transaction.notes && (
                    <p>Observações: {transaction.notes}</p>
                  )}
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                <span className={`text-lg font-bold ${
                  transaction.transaction_type === 'income'
                    ? 'text-primary'
                    : 'text-destructive'
                }`}>
                  {transaction.transaction_type === 'income' ? '+' : '-'}
                  {formatCurrency(Math.abs(transaction.amount))}
                </span>
                
                <button
                  onClick={() => handleDeleteTransaction(transaction.id)}
                  className="text-destructive hover:text-destructive/90 text-sm"
                  title="Excluir transação"
                >
                  🗑️
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TransactionList;
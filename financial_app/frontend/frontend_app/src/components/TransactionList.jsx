import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth.jsx';
import api from '../lib/api.js';
import { Pencil, Trash2 } from 'lucide-react';
import { Button } from './ui/button';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from './ui/alert-dialog';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import TransactionForm from './TransactionForm';

const TransactionList = ({ period, refreshTrigger }) => {
  const { user } = useAuth();
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [currentTransaction, setCurrentTransaction] = useState(null);

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
  }, [user, period, refreshTrigger]);

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
            className="bg-card border border-border rounded-lg p-4 hover:shadow-md transition-shadow duration-200 flex items-center justify-between"
          >
            <div className="flex-1 flex items-center space-x-4">
              {/* Ícone de cor (placeholder) */}
              <div className="w-3 h-3 rounded-full bg-blue-500"></div> {/* Placeholder for color icon */}
              <div>
                <h5 className="font-medium text-foreground">
                  {transaction.description}
                </h5>
                <p className="text-sm text-muted-foreground">
                  {transaction.category_name} • {formatDate(transaction.date)}
                </p>
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
              
              <div className="flex items-center space-x-2">
                {/* Edit Button */}
                <Dialog open={isEditing && currentTransaction?.id === transaction.id} onOpenChange={(open) => {
                  if (!open) {
                    setIsEditing(false);
                    setCurrentTransaction(null);
                  }
                }}>
                  <DialogTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => {
                        setCurrentTransaction(transaction);
                        setIsEditing(true);
                      }}
                      title="Editar transação"
                    >
                      <Pencil className="h-4 w-4" />
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="sm:max-w-[425px]">
                    <DialogHeader>
                      <DialogTitle>Editar Transação</DialogTitle>
                    </DialogHeader>
                    <TransactionForm
                      transaction={currentTransaction}
                      onSave={() => {
                        setIsEditing(false);
                        setCurrentTransaction(null);
                        fetchTransactions(); // Re-fetch transactions after save
                        if (onTransactionChange) onTransactionChange();
                      }}
                      onCancel={() => {
                        setIsEditing(false);
                        setCurrentTransaction(null);
                      }}
                    />
                  </DialogContent>
                </Dialog>

                {/* Delete Button */}
                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="text-destructive hover:text-destructive/90"
                      title="Excluir transação"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>Tem certeza?</AlertDialogTitle>
                      <AlertDialogDescription>
                        Esta ação não pode ser desfeita. Isso excluirá permanentemente esta transação.
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Cancelar</AlertDialogCancel>
                      <AlertDialogAction onClick={() => handleDeleteTransaction(transaction.id)}>
                        Excluir
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TransactionList;
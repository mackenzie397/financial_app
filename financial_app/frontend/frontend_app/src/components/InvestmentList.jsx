import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth.jsx';
import api from '../lib/api.js';
import { Pencil, Trash2 } from 'lucide-react';
import { Button } from './ui/button';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from './ui/alert-dialog';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import InvestmentForm from './InvestmentForm';

const InvestmentList = ({ onInvestmentChange }) => {
  const { user } = useAuth();
  const [investments, setInvestments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [currentInvestment, setCurrentInvestment] = useState(null);

  const fetchInvestments = async () => {
    if (!user) return;

    try {
      setLoading(true);
      setError(null);
      
      const response = await api.get('/investments', {
        params: {
          user_id: user.id,
        }
      });
      
      setInvestments(response.data);
    } catch (error) {
      console.error('Erro ao carregar investimentos:', error);
      setError('Erro ao carregar investimentos');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteInvestment = async (id) => {
    try {
      await api.delete(`/investments/${id}`);
      setInvestments(prev => prev.filter(i => i.id !== id));
      if (onInvestmentChange) onInvestmentChange();
    } catch (error) {
      console.error('Erro ao excluir investimento:', error);
      alert('Erro ao excluir investimento');
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
    fetchInvestments();
  }, [user]);

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

  if (investments.length === 0) {
    return (
      <div className="text-center py-12 bg-card rounded-lg p-4">
        <div className="text-muted-foreground text-6xl mb-4">📈</div>
        <h3 className="text-lg font-medium text-foreground mb-2">
          Nenhum investimento encontrado
        </h3>
        <p className="text-muted-foreground mb-4">
          Não há investimentos registrados.
        </p>
        <p className="text-muted-foreground text-sm">
          Clique em "Novo Investimento" para começar a registrar seus investimentos.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h4 className="text-md font-medium text-foreground">
          {investments.length} investimento{investments.length !== 1 ? 's' : ''} encontrado{investments.length !== 1 ? 's' : ''}
        </h4>
      </div>

      <div className="space-y-3">
        {investments.map((investment) => (
          <div
            key={investment.id}
            className="bg-card border border-border rounded-lg p-4 hover:shadow-md transition-shadow duration-200"
          >
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-2">
                  <h5 className="font-medium text-foreground">
                    {investment.name}
                  </h5>
                  <span className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
                    {investment.investment_type_name}
                  </span>
                </div>
                
                <div className="text-sm text-muted-foreground space-y-1">
                  <p>Valor Inicial: {formatCurrency(investment.initial_amount)}</p>
                  <p>Valor Atual: {formatCurrency(investment.current_amount)}</p>
                  <p>Data de Compra: {formatDate(investment.purchase_date)}</p>
                  {investment.notes && (
                    <p>Observações: {investment.notes}</p>
                  )}
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                {/* Edit Button */}
                <Dialog open={isEditing && currentInvestment?.id === investment.id} onOpenChange={(open) => {
                  if (!open) {
                    setIsEditing(false);
                    setCurrentInvestment(null);
                  }
                }}>
                  <DialogTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => {
                        setCurrentInvestment(investment);
                        setIsEditing(true);
                      }}
                      title="Editar investimento"
                    >
                      <Pencil className="h-4 w-4" />
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="sm:max-w-[425px]">
                    <DialogHeader>
                      <DialogTitle>Editar Investimento</DialogTitle>
                    </DialogHeader>
                    <InvestmentForm
                      investment={currentInvestment}
                      onSave={() => {
                        setIsEditing(false);
                        setCurrentInvestment(null);
                        fetchInvestments(); // Re-fetch investments after save
                        if (onInvestmentChange) onInvestmentChange();
                      }}
                      onCancel={() => {
                        setIsEditing(false);
                        setCurrentInvestment(null);
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
                      title="Excluir investimento"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>Tem certeza?</AlertDialogTitle>
                      <AlertDialogDescription>
                        Esta ação não pode ser desfeita. Isso excluirá permanentemente este investimento.
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Cancelar</AlertDialogCancel>
                      <AlertDialogAction onClick={() => handleDeleteInvestment(investment.id)}>
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

export default InvestmentList;
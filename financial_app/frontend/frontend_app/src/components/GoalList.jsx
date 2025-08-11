import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth.jsx';
import api from '../lib/api.js';
import { Pencil, Trash2 } from 'lucide-react';
import { Button } from './ui/button';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from './ui/alert-dialog';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import GoalForm from './GoalForm';

const GoalList = ({ onGoalChange, refreshTrigger }) => {
  const { user } = useAuth();
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [currentGoal, setCurrentGoal] = useState(null);

  const fetchGoals = async () => {
    if (!user) return;

    try {
      setLoading(true);
      setError(null);
      
      const response = await api.get('/goals', {
        params: {
          user_id: user.id,
        }
      });
      
      setGoals(response.data);
    } catch (error) {
      console.error('Erro ao carregar metas:', error);
      setError('Erro ao carregar metas');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteGoal = async (id) => {
    try {
      await api.delete(`/goals/${id}`);
      setGoals(prev => prev.filter(g => g.id !== id));
      if (onGoalChange) onGoalChange();
    } catch (error) {
      console.error('Erro ao excluir meta:', error);
      alert('Erro ao excluir meta');
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

  const calculateProgress = (current, target) => {
    if (target === 0) return 0;
    return Math.min((current / target) * 100, 100);
  };

  useEffect(() => {
    fetchGoals();
  }, [user, refreshTrigger]);

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

  if (goals.length === 0) {
    return (
      <div className="text-center py-12 bg-card rounded-lg p-4">
        <div className="text-muted-foreground text-6xl mb-4">🎯</div>
        <h3 className="text-lg font-medium text-foreground mb-2">
          Nenhuma meta encontrada
        </h3>
        <p className="text-muted-foreground mb-4">
          Não há metas registradas.
        </p>
        <p className="text-muted-foreground text-sm">
          Clique em "Nova Meta" para começar a registrar suas metas.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h4 className="text-md font-medium text-foreground">
          {goals.length} meta{goals.length !== 1 ? 's' : ''} encontrada{goals.length !== 1 ? 's' : ''}
        </h4>
      </div>

      <div className="space-y-3">
        {goals.map((goal) => (
          <div
            key={goal.id}
            className="bg-card border border-border rounded-lg p-4 hover:shadow-md transition-shadow duration-200"
          >
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-2">
                  <h5 className="font-medium text-foreground">
                    {goal.name}
                  </h5>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    goal.status === 'completed'
                      ? 'bg-green-100 text-green-800'
                      : goal.status === 'active'
                      ? 'bg-blue-100 text-blue-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {goal.status === 'completed' ? 'Concluída' : goal.status === 'active' ? 'Ativa' : 'Pausada'}
                  </span>
                </div>
                
                <div className="text-sm text-muted-foreground space-y-1">
                  <p>Valor Objetivo: {formatCurrency(goal.target_amount)}</p>
                  <p>Valor Atual: {formatCurrency(goal.current_amount)}</p>
                  {goal.target_date && (
                    <p>Data Objetivo: {formatDate(goal.target_date)}</p>
                  )}
                  {goal.description && (
                    <p>Descrição: {goal.description}</p>
                  )}
                </div>
                
                {/* Progress Bar */}
                {goal.target_amount > 0 && (
                  <div className="mt-3">
                    <div className="flex justify-between text-xs text-muted-foreground mb-1">
                      <span>Progresso</span>
                      <span>{calculateProgress(goal.current_amount, goal.target_amount).toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-border rounded-full h-1.5">
                      <div
                        className="bg-primary h-1.5 rounded-full transition-all duration-300"
                        style={{ width: `${calculateProgress(goal.current_amount, goal.target_amount)}%` }}
                      ></div>
                    </div>
                  </div>
                )}
              </div>
              
              <div className="flex items-center space-x-2">
                {/* Edit Button */}
                <Dialog open={isEditing && currentGoal?.id === goal.id} onOpenChange={(open) => {
                  if (!open) {
                    setIsEditing(false);
                    setCurrentGoal(null);
                  }
                }}>
                  <DialogTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => {
                        setCurrentGoal(goal);
                        setIsEditing(true);
                      }}
                      title="Editar meta"
                    >
                      <Pencil className="h-4 w-4" />
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="sm:max-w-[425px]">
                    <DialogHeader>
                      <DialogTitle>Editar Meta</DialogTitle>
                    </DialogHeader>
                    <GoalForm
                      goal={currentGoal}
                      onSave={() => {
                        setIsEditing(false);
                        setCurrentGoal(null);
                        fetchGoals(); // Re-fetch goals after save
                        if (onGoalChange) onGoalChange();
                      }}
                      onCancel={() => {
                        setIsEditing(false);
                        setCurrentGoal(null);
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
                      title="Excluir meta"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>Tem certeza?</AlertDialogTitle>
                      <AlertDialogDescription>
                        Esta ação não pode ser desfeita. Isso excluirá permanentemente esta meta.
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Cancelar</AlertDialogCancel>
                      <AlertDialogAction onClick={() => handleDeleteGoal(goal.id)}>
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

export default GoalList;
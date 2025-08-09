import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth.jsx';
import api from '../lib/api.js';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from "@/components/ui/select";
import { DatePicker } from "@/components/ui/date-picker";

const GoalForm = ({ goal = null, onSave, onCancel }) => {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    target_amount: '',
    current_amount: '',
    status: 'active'
  });
  const [targetDate, setTargetDate] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (goal) {
      setFormData({
        name: goal.name || '',
        description: goal.description || '',
        target_amount: goal.target_amount?.toString() || '',
        current_amount: goal.current_amount?.toString() || '',
        status: goal.status || 'active'
      });
      setTargetDate(goal.target_date ? new Date(goal.target_date + 'T00:00:00') : null);
    } else {
      setFormData({
        name: '',
        description: '',
        target_amount: '',
        current_amount: '',
        status: 'active'
      });
      setTargetDate(null);
    }
  }, [goal]);

  const handleChange = (name, value) => {
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const dataToSend = {
        ...formData,
        user_id: user.id,
        target_amount: parseFloat(formData.target_amount),
        current_amount: parseFloat(formData.current_amount || 0),
        target_date: targetDate ? targetDate.toISOString().split('T')[0] : null,
      };

      if (goal) {
        await api.put(`/goals/${goal.id}`, dataToSend);
      } else {
        await api.post('/goals', dataToSend);
      }

      onSave();
    } catch (error) {
      setError(error.response?.data?.message || 'Erro ao salvar meta');
    } finally {
      setLoading(false);
    }
  };

  const calculateProgress = () => {
    const current = parseFloat(formData.current_amount || 0);
    const target = parseFloat(formData.target_amount || 0);
    if (target === 0) return 0;
    return Math.min((current / target) * 100, 100);
  };

  return (
    <div className="fixed inset-0 bg-background bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-card rounded-lg shadow-lg w-full max-w-md">
        <div className="p-6">
          <h2 className="text-xl font-bold text-foreground mb-4">
            {goal ? 'Editar Meta' : 'Nova Meta'}
          </h2>

          {error && (
            <div className="bg-destructive/20 border border-destructive text-destructive-foreground px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="name" className="block text-sm font-medium text-foreground mb-1">Nome da Meta</Label>
              <Input
                id="name"
                type="text"
                name="name"
                value={formData.name}
                onChange={(e) => handleChange(e.target.name, e.target.value)}
                required
                className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-ring bg-input text-foreground"
                placeholder="Ex: Viagem para Europa"
              />
            </div>

            <div>
              <Label htmlFor="description" className="block text-sm font-medium text-foreground mb-1">Descrição</Label>
              <textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={(e) => handleChange(e.target.name, e.target.value)}
                rows="3"
                className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-ring bg-input text-foreground"
                placeholder="Descreva sua meta..."
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="target_amount" className="block text-sm font-medium text-foreground mb-1">Valor Objetivo</Label>
                <Input
                  id="target_amount"
                  type="number"
                  name="target_amount"
                  value={formData.target_amount}
                  onChange={(e) => handleChange(e.target.name, e.target.value)}
                  required
                  step="0.01"
                  min="0"
                  className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-ring bg-input text-foreground"
                  placeholder="0,00"
                />
              </div>

              <div>
                <Label htmlFor="current_amount" className="block text-sm font-medium text-foreground mb-1">Valor Atual</Label>
                <Input
                  id="current_amount"
                  type="number"
                  name="current_amount"
                  value={formData.current_amount}
                  onChange={(e) => handleChange(e.target.name, e.target.value)}
                  step="0.01"
                  min="0"
                  className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-ring bg-input text-foreground"
                  placeholder="0,00"
                />
              </div>
            </div>

            <div>
              <Label htmlFor="target_date" className="block text-sm font-medium text-foreground mb-1">Data Objetivo</Label>
              <DatePicker
                date={targetDate}
                setDate={setTargetDate}
              />
            </div>

            <div>
              <Label htmlFor="status" className="block text-sm font-medium text-foreground mb-1">Status</Label>
              <Select name="status" value={formData.status} onValueChange={(value) => handleChange('status', value)}>
                <SelectTrigger className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-ring bg-input text-foreground">
                  <SelectValue placeholder="Selecione o status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="active">Ativa</SelectItem>
                  <SelectItem value="completed">Concluída</SelectItem>
                  <SelectItem value="paused">Pausada</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Barra de progresso */}
            {formData.target_amount && (
              <div className="bg-muted p-3 rounded-md">
                <div className="flex justify-between text-sm text-muted-foreground mb-1">
                  <span>Progresso</span>
                  <span>{calculateProgress().toFixed(1)}%</span>
                </div>
                <div className="w-full bg-border rounded-full h-2">
                  <div
                    className="bg-primary h-2 rounded-full transition-all duration-300"
                    style={{ width: `${calculateProgress()}%` }}
                  ></div>
                </div>
              </div>
            )}

            <div className="flex space-x-3 pt-4">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 bg-primary hover:bg-primary/90 text-primary-foreground py-2 px-4 rounded-md font-medium"
              >
                {loading ? 'Salvando...' : (goal ? 'Atualizar' : 'Salvar')}
              </button>
              <button
                type="button"
                onClick={onCancel}
                className="flex-1 bg-muted hover:bg-muted/90 text-muted-foreground py-2 px-4 rounded-md font-medium"
              >
                Cancelar
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default GoalForm;
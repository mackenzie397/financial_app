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

const InvestmentForm = ({ investment = null, onSave, onCancel }) => {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    name: '',
    investment_type_id: '',
    initial_amount: '',
    current_amount: '',
    notes: ''
  });
  const [purchaseDate, setPurchaseDate] = useState(new Date());
  const [investmentTypes, setInvestmentTypes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchInvestmentTypes();
    
    if (investment) {
      setFormData({
        name: investment.name || '',
        investment_type_id: investment.investment_type_id?.toString() || '',
        initial_amount: investment.initial_amount?.toString() || '',
        current_amount: investment.current_amount?.toString() || '',
        notes: investment.notes || ''
      });
      setPurchaseDate(investment.purchase_date ? new Date(investment.purchase_date + 'T00:00:00') : new Date());
    } else {
      setFormData({
        name: '',
        investment_type_id: '',
        initial_amount: '',
        current_amount: '',
        notes: ''
      });
      setPurchaseDate(new Date());
    }
  }, [investment]);

  const fetchInvestmentTypes = async () => {
    try {
      const response = await api.get(`/investment-types?user_id=${user.id}`);
      setInvestmentTypes(response.data);
    } catch (error) {
      console.error('Erro ao buscar tipos de investimento:', error);
    }
  };

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
        initial_amount: parseFloat(formData.initial_amount),
        current_amount: parseFloat(formData.current_amount),
        investment_type_id: parseInt(formData.investment_type_id),
        purchase_date: purchaseDate.toISOString().split('T')[0],
      };

      if (investment) {
        await api.put(`/investments/${investment.id}`, dataToSend);
      } else {
        await api.post('/investments', dataToSend);
      }

      onSave();
    } catch (error) {
      setError(error.response?.data?.message || 'Erro ao salvar investimento');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-background bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-card rounded-lg shadow-lg w-full max-w-md">
        <div className="p-6">
          <h2 className="text-xl font-bold text-foreground mb-4">
            {investment ? 'Editar Investimento' : 'Novo Investimento'}
          </h2>

          {error && (
            <div className="bg-destructive/20 border border-destructive text-destructive-foreground px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="name" className="block text-sm font-medium text-foreground mb-1">
                Nome do Investimento
              </Label>
              <Input
                id="name"
                type="text"
                name="name"
                value={formData.name}
                onChange={(e) => handleChange(e.target.name, e.target.value)}
                required
                className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-ring bg-input text-foreground"
                placeholder="Ex: Tesouro Selic 2030"
              />
            </div>

            <div>
              <Label htmlFor="investment_type_id" className="block text-sm font-medium text-foreground mb-1">
                Tipo de Investimento
              </Label>
              <Select name="investment_type_id" value={formData.investment_type_id} onValueChange={(value) => handleChange('investment_type_id', value)}>
                <SelectTrigger className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-ring bg-input text-foreground">
                  <SelectValue placeholder="Selecione um tipo" />
                </SelectTrigger>
                <SelectContent>
                  {investmentTypes.map(type => (
                    <SelectItem key={type.id} value={String(type.id)}>
                      {type.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="initial_amount" className="block text-sm font-medium text-foreground mb-1">
                  Valor Inicial
                </Label>
                <Input
                  id="initial_amount"
                  type="number"
                  name="initial_amount"
                  value={formData.initial_amount}
                  onChange={(e) => handleChange(e.target.name, e.target.value)}
                  required
                  step="0.01"
                  min="0"
                  className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-ring bg-input text-foreground"
                  placeholder="0,00"
                />
              </div>

              <div>
                <Label htmlFor="current_amount" className="block text-sm font-medium text-foreground mb-1">
                  Valor Atual
                </Label>
                <Input
                  id="current_amount"
                  type="number"
                  name="current_amount"
                  value={formData.current_amount}
                  onChange={(e) => handleChange(e.target.name, e.target.value)}
                  required
                  step="0.01"
                  min="0"
                  className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-ring bg-input text-foreground"
                  placeholder="0,00"
                />
              </div>
            </div>

            <div>
              <Label htmlFor="purchase_date" className="block text-sm font-medium text-foreground mb-1">
                Data da Compra
              </Label>
              <DatePicker
                date={purchaseDate}
                setDate={setPurchaseDate}
              />
            </div>

            <div>
              <Label htmlFor="notes" className="block text-sm font-medium text-foreground mb-1">
                Observações
              </Label>
              <textarea
                id="notes"
                name="notes"
                value={formData.notes}
                onChange={(e) => handleChange(e.target.name, e.target.value)}
                rows="3"
                className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-ring bg-input text-foreground"
                placeholder="Observações sobre o investimento (opcional)"
              />
            </div>

            <div className="flex space-x-3 pt-4">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 bg-primary hover:bg-primary/90 text-primary-foreground py-2 px-4 rounded-md font-medium"
              >
                {loading ? 'Salvando...' : (investment ? 'Atualizar' : 'Salvar')}
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

export default InvestmentForm;
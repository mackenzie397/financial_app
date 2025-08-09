import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth.jsx';
import api from '../lib/api.js';

const TransactionForm = ({ transaction = null, onSave, onCancel }) => {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    description: '',
    amount: '',
    transaction_type: 'expense',
    category_id: '',
    payment_method_id: '',
    date: new Date().toISOString().split('T')[0],
    notes: ''
  });
  const [categories, setCategories] = useState([]);
  const [paymentMethods, setPaymentMethods] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Fetch categories based on transaction_type
  useEffect(() => {
    const fetchFilteredCategories = async () => {
      try {
        const response = await api.get(`/categories?user_id=${user.id}&category_type=${formData.transaction_type}`);
        setCategories(response.data);
        // Reset category_id if current one is not in filtered list
        if (!response.data.some(cat => cat.id === parseInt(formData.category_id))) {
          setFormData(prev => ({ ...prev, category_id: '' }));
        }
      } catch (error) {
        console.error('Erro ao buscar categorias filtradas:', error);
      }
    };

    fetchFilteredCategories();
  }, [formData.transaction_type, user.id]);

  // Fetch payment methods (always, as they are not type-dependent)
  useEffect(() => {
    const fetchPaymentMethods = async () => {
      try {
        const response = await api.get(`/payment-methods?user_id=${user.id}`);
        setPaymentMethods(response.data);
      } catch (error) {
        console.error('Erro ao buscar formas de pagamento:', error);
      }
    };
    fetchPaymentMethods();
  }, [user.id]);

  // Initialize form data for editing
  useEffect(() => {
    if (transaction) {
      setFormData({
        description: transaction.description || '',
        amount: transaction.amount?.toString() || '',
        transaction_type: transaction.transaction_type || 'expense',
        category_id: transaction.category_id?.toString() || '',
        payment_method_id: transaction.payment_method_id?.toString() || '',
        date: transaction.date ? transaction.date.split('T')[0] : new Date().toISOString().split('T')[0],
        notes: transaction.notes || ''
      });
    }
  }, [transaction]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => {
      const newState = { ...prev, [name]: value };
      // Reset payment_method_id if transaction_type changes to income
      if (name === 'transaction_type' && value === 'income') {
        newState.payment_method_id = '';
      }
      return newState;
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const dataToSend = {
        ...formData,
        user_id: user.id,
        amount: parseFloat(formData.amount),
        category_id: parseInt(formData.category_id),
      };

      // Conditionally add payment_method_id for expense transactions
      if (formData.transaction_type === 'expense') {
        dataToSend.payment_method_id = parseInt(formData.payment_method_id);
      } else {
        // Ensure payment_method_id is not sent for income
        delete dataToSend.payment_method_id;
      }

      if (transaction) {
        await api.put(`/transactions/${transaction.id}`, dataToSend);
      } else {
        await api.post('/transactions', dataToSend);
      }

      onSave();
    } catch (error) {
      setError(error.response?.data?.message || 'Erro ao salvar transação');
    } finally {
      setLoading(false);
    }
  };

  const showPaymentMethodField = formData.transaction_type === 'expense';

  return (
    <div className="fixed inset-0 bg-background bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-card rounded-lg shadow-lg w-full max-w-md">
        <div className="p-6">
          <h2 className="text-xl font-bold text-foreground mb-4">
            {transaction ? 'Editar Transação' : 'Nova Transação'}
          </h2>

          {error && (
            <div className="bg-destructive/20 border border-destructive text-destructive-foreground px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-1">
                Descrição
              </label>
              <input
                type="text"
                name="description"
                value={formData.description}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-ring bg-input text-foreground"
                placeholder="Ex: Compra no supermercado"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground mb-1">
                Valor
              </label>
              <input
                type="number"
                name="amount"
                value={formData.amount}
                onChange={handleChange}
                required
                step="0.01"
                min="0"
                className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-ring bg-input text-foreground"
                placeholder="0,00"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground mb-1">
                Tipo
              </label>
              <select
                name="transaction_type"
                value={formData.transaction_type}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-ring bg-input text-foreground"
              >
                <option value="expense">Despesa</option>
                <option value="income">Receita</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground mb-1">
                Categoria
              </label>
              <select
                name="category_id"
                value={formData.category_id}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-ring bg-input text-foreground"
              >
                <option value="">Selecione uma categoria</option>
                {categories.map(category => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
              </select>
            </div>

            {showPaymentMethodField && (
              <div>
                <label className="block text-sm font-medium text-foreground mb-1">
                  Forma de Pagamento
                </label>
                <select
                  name="payment_method_id"
                  value={formData.payment_method_id}
                  onChange={handleChange}
                  required={showPaymentMethodField} // Make required only if visible
                  className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-ring bg-input text-foreground"
                >
                  <option value="">Selecione uma forma de pagamento</option>
                  {paymentMethods.map(method => (
                    <option key={method.id} value={method.id}>
                      {method.name}
                    </option>
                  ))}
                </select>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-foreground mb-1">
                Data
              </label>
              <input
                type="date"
                name="date"
                value={formData.date}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-ring bg-input text-foreground"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground mb-1">
                Observações
              </label>
              <textarea
                name="notes"
                value={formData.notes}
                onChange={handleChange}
                rows="3"
                className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-ring bg-input text-foreground"
                placeholder="Observações adicionais (opcional)"
              />
            </div>

            <div className="flex space-x-3 pt-4">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 bg-primary hover:bg-primary/90 text-primary-foreground py-2 px-4 rounded-md font-medium"
              >
                {loading ? 'Salvando...' : (transaction ? 'Atualizar' : 'Salvar')}
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

export default TransactionForm;
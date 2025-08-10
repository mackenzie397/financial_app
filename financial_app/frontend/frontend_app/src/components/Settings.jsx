import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth.jsx';
import api from '../lib/api.js';
import { Pencil, Trash2 } from 'lucide-react';
import { Button } from './ui/button';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from './ui/alert-dialog';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';

const Settings = () => {
  const { user } = useAuth();
  const [activeSection, setActiveSection] = useState('categories');
  const [categories, setCategories] = useState([]);
  const [paymentMethods, setPaymentMethods] = useState([]);
  const [investmentTypes, setInvestmentTypes] = useState([]);
  const [loading, setLoading] = useState(true);

  // Estados para formulários
  const [showCategoryForm, setShowCategoryForm] = useState(false);
  const [showPaymentForm, setShowPaymentForm] = useState(false);
  const [showInvestmentForm, setShowInvestmentForm] = useState(false);
  const [editingItem, setEditingItem] = useState(null);

  // Estados para novos itens
  const [newCategory, setNewCategory] = useState({ name: '', category_type: 'expense' });
  const [newPaymentMethod, setNewPaymentMethod] = useState({ name: '' });
  const [newInvestmentType, setNewInvestmentType] = useState({ name: '' });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [categoriesRes, paymentRes, investmentRes] = await Promise.all([
        api.get(`/categories?user_id=${user.id}`),
        api.get(`/payment-methods?user_id=${user.id}`),
        api.get(`/investment-types?user_id=${user.id}`)
      ]);
      
      setCategories(categoriesRes.data);
      setPaymentMethods(paymentRes.data);
      setInvestmentTypes(investmentRes.data);
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddCategory = async (e) => {
    e.preventDefault();
    try {
      const dataToSend = { ...newCategory, user_id: user.id };
      if (editingItem) {
        await api.put(`/categories/${editingItem.id}`, dataToSend);
      } else {
        await api.post('/categories', dataToSend);
      }
      setNewCategory({ name: '', category_type: 'expense' });
      setShowCategoryForm(false);
      setEditingItem(null);
      fetchData();
    } catch (error) {
      console.error('Erro ao salvar categoria:', error);
    }
  };

  const handleAddPaymentMethod = async (e) => {
    e.preventDefault();
    try {
      const dataToSend = { ...newPaymentMethod, user_id: user.id };
      if (editingItem) {
        await api.put(`/payment-methods/${editingItem.id}`, dataToSend);
      } else {
        await api.post('/payment-methods', dataToSend);
      }
      setNewPaymentMethod({ name: '' });
      setShowPaymentForm(false);
      setEditingItem(null);
      fetchData();
    } catch (error) {
      console.error('Erro ao salvar forma de pagamento:', error);
    }
  };

  const handleAddInvestmentType = async (e) => {
    e.preventDefault();
    try {
      const dataToSend = { ...newInvestmentType, user_id: user.id };
      if (editingItem) {
        await api.put(`/investment-types/${editingItem.id}`, dataToSend);
      } else {
        await api.post('/investment-types', dataToSend);
      }
      setNewInvestmentType({ name: '' });
      setShowInvestmentForm(false);
      setEditingItem(null);
      fetchData();
    } catch (error) {
      console.error('Erro ao salvar tipo de investimento:', error);
    }
  };

  const handleEdit = (item, type) => {
    setEditingItem(item);
    if (type === 'category') {
      setNewCategory({ name: item.name, category_type: item.category_type || 'expense' });
      setShowCategoryForm(true);
    } else if (type === 'payment') {
      setNewPaymentMethod({ name: item.name });
      setShowPaymentForm(true);
    } else if (type === 'investment') {
      setNewInvestmentType({ name: item.name });
      setShowInvestmentForm(true);
    }
  };

  const handleDelete = async (id, type) => {
    
    try {
      if (type === 'category') {
        await api.delete(`/categories/${id}`);
      } else if (type === 'payment') {
        await api.delete(`/payment-methods/${id}`);
      } else if (type === 'investment') {
        await api.delete(`/investment-types/${id}`);
      }
      fetchData();
    } catch (error) {
      console.error('Erro ao excluir item:', error);
      alert('Erro ao excluir item');
    }
  };

  const renderCategories = () => (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-foreground">Categorias</h3>
        <Dialog open={showCategoryForm} onOpenChange={(open) => {
          setShowCategoryForm(open);
          if (!open) {
            setEditingItem(null);
            setNewCategory({ name: '', category_type: 'expense' });
          }
        }}>
          <DialogTrigger asChild>
            <Button
              onClick={() => {
                setEditingItem(null);
                setNewCategory({ name: '', category_type: 'expense' });
              }}
            >
              Nova Categoria
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>{editingItem ? 'Editar Categoria' : 'Nova Categoria'}</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleAddCategory} className="space-y-3">
              <div>
                <input
                  type="text"
                  placeholder="Nome da categoria"
                  value={newCategory.name}
                  onChange={(e) => setNewCategory({ ...newCategory, name: e.target.value })}
                  required
                  className="w-full px-3 py-2 border border-border rounded-md bg-input text-foreground"
                />
              </div>
              <div>
                <select
                  value={newCategory.category_type}
                  onChange={(e) => setNewCategory({ ...newCategory, category_type: e.target.value })}
                  className="w-full px-3 py-2 border border-border rounded-md bg-input text-foreground"
                >
                  <option value="expense">Despesa</option>
                  <option value="income">Receita</option>
                </select>
              </div>
              <div className="flex space-x-2">
                <Button
                  type="submit"
                >
                  {editingItem ? 'Atualizar' : 'Adicionar'}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setShowCategoryForm(false);
                    setEditingItem(null);
                    setNewCategory({ name: '', category_type: 'expense' });
                  }}
                >
                  Cancelar
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="space-y-2">
        {categories.map((category) => (
          <div key={category.id} className="flex justify-between items-center p-3 bg-card border border-border rounded-lg">
            <div>
              <span className="font-medium text-foreground">{category.name}</span>
              <span className={`ml-2 px-2 py-1 text-xs rounded-full ${
                category.category_type === 'income' 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-red-100 text-red-800'
              }`}>
                {category.category_type === 'income' ? 'Receita' : 'Despesa'}
              </span>
            </div>
            <div className="space-x-2">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => {
                  handleEdit(category, 'category');
                  setShowCategoryForm(true);
                }}
                title="Editar categoria"
              >
                <Pencil className="h-4 w-4" />
              </Button>
              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="text-destructive hover:text-destructive/90"
                    title="Excluir categoria"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>Tem certeza?</AlertDialogTitle>
                    <AlertDialogDescription>
                      Esta ação não pode ser desfeita. Isso excluirá permanentemente esta categoria.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Cancelar</AlertDialogCancel>
                    <AlertDialogAction onClick={() => handleDelete(category.id, 'category')}>
                      Excluir
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderPaymentMethods = () => (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-foreground">Formas de Pagamento</h3>
        <Dialog open={showPaymentForm} onOpenChange={(open) => {
          setShowPaymentForm(open);
          if (!open) {
            setEditingItem(null);
            setNewPaymentMethod({ name: '' });
          }
        }}>
          <DialogTrigger asChild>
            <Button
              onClick={() => {
                setEditingItem(null);
                setNewPaymentMethod({ name: '' });
              }}
            >
              Nova Forma de Pagamento
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>{editingItem ? 'Editar Forma de Pagamento' : 'Nova Forma de Pagamento'}</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleAddPaymentMethod} className="space-y-3">
              <div>
                <input
                  type="text"
                  placeholder="Nome da forma de pagamento"
                  value={newPaymentMethod.name}
                  onChange={(e) => setNewPaymentMethod({ ...newPaymentMethod, name: e.target.value })}
                  required
                  className="w-full px-3 py-2 border border-border rounded-md bg-input text-foreground"
                />
              </div>
              <div className="flex space-x-2">
                <Button
                  type="submit"
                >
                  {editingItem ? 'Atualizar' : 'Adicionar'}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setShowPaymentForm(false);
                    setEditingItem(null);
                    setNewPaymentMethod({ name: '' });
                  }}
                >
                  Cancelar
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="space-y-2">
        {paymentMethods.map((method) => (
          <div key={method.id} className="flex justify-between items-center p-3 bg-card border border-border rounded-lg">
            <span className="font-medium text-foreground">{method.name}</span>
            <div className="space-x-2">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => {
                  handleEdit(method, 'payment');
                  setShowPaymentForm(true);
                }}
                title="Editar forma de pagamento"
              >
                <Pencil className="h-4 w-4" />
              </Button>
              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="text-destructive hover:text-destructive/90"
                    title="Excluir forma de pagamento"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>Tem certeza?</AlertDialogTitle>
                    <AlertDialogDescription>
                      Esta ação não pode ser desfeita. Isso excluirá permanentemente esta forma de pagamento.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Cancelar</AlertDialogCancel>
                    <AlertDialogAction onClick={() => handleDelete(method.id, 'payment')}>
                      Excluir
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderInvestmentTypes = () => (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-foreground">Tipos de Investimento</h3>
        <Dialog open={showInvestmentForm} onOpenChange={(open) => {
          setShowInvestmentForm(open);
          if (!open) {
            setEditingItem(null);
            setNewInvestmentType({ name: '' });
          }
        }}>
          <DialogTrigger asChild>
            <Button
              onClick={() => {
                setEditingItem(null);
                setNewInvestmentType({ name: '' });
              }}
            >
              Novo Tipo de Investimento
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>{editingItem ? 'Editar Tipo de Investimento' : 'Novo Tipo de Investimento'}</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleAddInvestmentType} className="space-y-3">
              <div>
                <input
                  type="text"
                  placeholder="Nome do tipo de investimento"
                  value={newInvestmentType.name}
                  onChange={(e) => setNewInvestmentType({ ...newInvestmentType, name: e.target.value })}
                  required
                  className="w-full px-3 py-2 border border-border rounded-md bg-input text-foreground"
                />
              </div>
              <div className="flex space-x-2">
                <Button
                  type="submit"
                >
                  {editingItem ? 'Atualizar' : 'Adicionar'}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setShowInvestmentForm(false);
                    setEditingItem(null);
                    setNewInvestmentType({ name: '' });
                  }}
                >
                  Cancelar
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="space-y-2">
        {investmentTypes.map((type) => (
          <div key={type.id} className="flex justify-between items-center p-3 bg-card border border-border rounded-lg">
            <span className="font-medium text-foreground">{type.name}</span>
            <div className="space-x-2">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => {
                  handleEdit(type, 'investment');
                  setShowInvestmentForm(true);
                }}
                title="Editar tipo de investimento"
              >
                <Pencil className="h-4 w-4" />
              </Button>
              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="text-destructive hover:text-destructive/90"
                    title="Excluir tipo de investimento"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>Tem certeza?</AlertDialogTitle>
                    <AlertDialogDescription>
                      Esta ação não pode ser desfeita. Isso excluirá permanentemente este tipo de investimento.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Cancelar</AlertDialogCancel>
                    <AlertDialogAction onClick={() => handleDelete(type.id, 'investment')}>
                      Excluir
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="text-muted-foreground">Carregando configurações...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="border-b border-border">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveSection('categories')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeSection === 'categories'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            Categorias
          </button>
          <button
            onClick={() => setActiveSection('payment-methods')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeSection === 'payment-methods'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            Formas de Pagamento
          </button>
          <button
            onClick={() => setActiveSection('investment-types')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeSection === 'investment-types'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            Tipos de Investimento
          </button>
        </nav>
      </div>

      <div>
        {activeSection === 'categories' && renderCategories()}
        {activeSection === 'payment-methods' && renderPaymentMethods()}
        {activeSection === 'investment-types' && renderInvestmentTypes()}
      </div>
    </div>
  );
};

export default Settings;
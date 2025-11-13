import { useState, useEffect } from 'react';
import { getPaymentMethods, addPaymentMethod, deletePaymentMethod } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { toast } from 'sonner';
import { Trash2 } from 'lucide-react';

const PaymentMethodsManager = () => {
  const [paymentMethods, setPaymentMethods] = useState([]);
  const [newMethodName, setNewMethodName] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchPaymentMethods = async () => {
    try {
      const response = await getPaymentMethods();
      setPaymentMethods(response.data);
    } catch (error) {
      toast.error('Falha ao carregar as formas de pagamento.');
    }
  };

  useEffect(() => {
    fetchPaymentMethods();
  }, []);

  const handleAddPaymentMethod = async (e) => {
    e.preventDefault();
    if (!newMethodName) {
      toast.error('O nome da forma de pagamento é obrigatório.');
      return;
    }
    setLoading(true);
    try {
      await addPaymentMethod({ name: newMethodName });
      toast.success('Forma de pagamento adicionada com sucesso!');
      setNewMethodName('');
      fetchPaymentMethods(); // Refresh a lista
    } catch (error) {
      toast.error(error.response?.data?.message || 'Falha ao adicionar a forma de pagamento.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeletePaymentMethod = async (id) => {
    try {
      await deletePaymentMethod(id);
      toast.success('Forma de pagamento deletada com sucesso!');
      fetchPaymentMethods(); // Refresh a lista
    } catch (error) {
      toast.error('Falha ao deletar a forma de pagamento.');
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Adicionar Nova Forma de Pagamento</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleAddPaymentMethod} className="flex items-end space-x-4">
            <div className="flex-grow space-y-2">
              <Label htmlFor="payment-method-name">Nome da Forma de Pagamento</Label>
              <Input
                id="payment-method-name"
                value={newMethodName}
                onChange={(e) => setNewMethodName(e.target.value)}
                placeholder="Ex: Cartão de Crédito Bradesco"
              />
            </div>
            <Button type="submit" disabled={loading}>{loading ? 'Adicionando...' : 'Adicionar'}</Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Formas de Pagamento Salvas</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nome</TableHead>
                <TableHead className="text-right">Ação</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {paymentMethods.map((method) => (
                <TableRow key={method.id}>
                  <TableCell>{method.name}</TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="icon" onClick={() => handleDeletePaymentMethod(method.id)}>
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
};

export default PaymentMethodsManager;

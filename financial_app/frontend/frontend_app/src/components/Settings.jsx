import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import CategoriesManager from './settings/CategoriesManager';
import PaymentMethodsManager from './settings/PaymentMethodsManager';

const Settings = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-2">Configurações</h2>
        <p className="text-muted-foreground">Gerencie suas categorias, formas de pagamento e tipos de investimento.</p>
      </div>

      <Tabs defaultValue="categories" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="categories">Categorias</TabsTrigger>
          <TabsTrigger value="payment-methods">Formas de Pagamento</TabsTrigger>
        </TabsList>

        <TabsContent value="categories" className="mt-6">
          <CategoriesManager />
        </TabsContent>

        <TabsContent value="payment-methods" className="mt-6">
          <PaymentMethodsManager />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Settings;
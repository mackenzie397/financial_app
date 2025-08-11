import { useState } from 'react';
import DashboardCards from './DashboardCards.jsx';
import TransactionForm from './TransactionForm.jsx';
import TransactionList from './TransactionList.jsx';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const DashboardPage = ({ period }) => {
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleTransactionSave = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <div className="space-y-6">
      {/* Main Cards Section */}
      <DashboardCards period={period} refreshTrigger={refreshTrigger} />

      {/* Add Transaction Card */}
      <Card>
        <CardHeader>
          <CardTitle>Adicionar Nova Transação</CardTitle>
        </CardHeader>
        <CardContent>
          <TransactionForm onSave={handleTransactionSave} />
        </CardContent>
      </Card>

      {/* Recent Transactions Card */}
      <Card>
        <CardHeader>
          <CardTitle>Transações Recentes</CardTitle>
        </CardHeader>
        <CardContent>
          <TransactionList period={period} refreshTrigger={refreshTrigger} />
        </CardContent>
      </Card>
    </div>
  );
};

export default DashboardPage;

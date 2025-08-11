import { useState } from 'react';
import GoalForm from './GoalForm';
import GoalList from './GoalList';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import React from 'react';

const GoalsPage = () => {
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleGoalChange = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <React.Fragment>
      <Card>
        <CardHeader>
          <CardTitle>Adicionar Nova Meta</CardTitle>
        </CardHeader>
        <CardContent>
          <GoalForm onSave={handleGoalChange} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Metas Salvas</CardTitle>
        </CardHeader>
        <CardContent>
          <GoalList refreshTrigger={refreshTrigger} onGoalChange={handleGoalChange} />
        </CardContent>
      </Card>
    </React.Fragment>
  );
};

export default GoalsPage;
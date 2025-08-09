import React from 'react';

const PeriodSelector = ({ period, onPeriodChange }) => {
  const getMonthName = (month) => {
    const months = [
      'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
      'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ];
    return months[month - 1] || 'Mês inválido';
  };

  const navigatePeriod = (direction) => {
    const newPeriod = { ...period };
    
    if (direction === 'prev') {
      if (newPeriod.month === 1) {
        newPeriod.month = 12;
        newPeriod.year -= 1;
      } else {
        newPeriod.month -= 1;
      }
    } else if (direction === 'next') {
      if (newPeriod.month === 12) {
        newPeriod.month = 1;
        newPeriod.year += 1;
      } else {
        newPeriod.month += 1;
      }
    }
    
    onPeriodChange(newPeriod);
  };

  return (
    <div className="flex items-center justify-center space-x-4 mb-6">
      <button
        onClick={() => navigatePeriod('prev')}
        className="p-2 text-primary hover:bg-primary/10 rounded-full transition-colors duration-200"
        title="Mês anterior"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      
      <div className="bg-card rounded-lg shadow px-6 py-3 min-w-[200px] text-center">
        <h2 className="text-lg font-semibold text-foreground">
          {getMonthName(period.month)} de {period.year}
        </h2>
        <p className="text-sm text-muted-foreground">Período selecionado</p>
      </div>
      
      <button
        onClick={() => navigatePeriod('next')}
        className="p-2 text-primary hover:bg-primary/10 rounded-full transition-colors duration-200"
        title="Próximo mês"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </button>
    </div>
  );
};

export default PeriodSelector;
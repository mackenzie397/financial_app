import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para adicionar token de autenticação
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para lidar com respostas
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user_id');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;



// Funções de autenticação
export const register = (userData) => api.post('/register', userData);
export const login = (credentials) => api.post('/login', credentials);
export const logout = () => api.post('/logout');
export const getCurrentUser = () => api.get('/current_user');

// Funções de transações
export const getTransactions = (params) => api.get('/transactions', { params });
export const getTransactionById = (id) => api.get(`/transactions/${id}`);
export const addTransaction = (transactionData) => api.post('/transactions', transactionData);
export const updateTransaction = (id, transactionData) => api.put(`/transactions/${id}`, transactionData);
export const deleteTransaction = (id) => api.delete(`/transactions/${id}`);
export const getTransactionsSummary = (params) => api.get('/transactions/summary', { params });

// Funções de categorias
export const getCategories = () => api.get('/categories');
export const addCategory = (categoryData) => api.post('/categories', categoryData);
export const updateCategory = (id, categoryData) => api.put(`/categories/${id}`, categoryData);
export const deleteCategory = (id) => api.delete(`/categories/${id}`);

// Funções de métodos de pagamento
export const getPaymentMethods = () => api.get('/payment-methods');
export const addPaymentMethod = (methodData) => api.post('/payment-methods', methodData);
export const updatePaymentMethod = (id, methodData) => api.put(`/payment-methods/${id}`, methodData);
export const deletePaymentMethod = (id) => api.delete(`/payment-methods/${id}`);

// Funções de metas
export const getGoals = () => api.get('/goals');
export const addGoal = (goalData) => api.post('/goals', goalData);
export const updateGoal = (id, goalData) => api.put(`/goals/${id}`, goalData);
export const deleteGoal = (id) => api.delete(`/goals/${id}`);

// Funções de tipos de investimento
export const getInvestmentTypes = () => api.get('/investment-types');
export const addInvestmentType = (typeData) => api.post('/investment-types', typeData);
export const updateInvestmentType = (id, typeData) => api.put(`/investment-types/${id}`, typeData);
export const deleteInvestmentType = (id) => api.delete(`/investment-types/${id}`);

// Funções de investimentos
export const getInvestments = () => api.get('/investments');
export const addInvestment = (investmentData) => api.post('/investments', investmentData);
export const updateInvestment = (id, investmentData) => api.put(`/investments/${id}`, investmentData);
export const deleteInvestment = (id) => api.delete(`/investments/${id}`);
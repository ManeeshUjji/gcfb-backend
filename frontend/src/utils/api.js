import axios from 'axios';

const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api').trim();

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const forecastAPI = {
  getForecast: (date = 'today') => {
    return api.get(`/forecast?date=${date}`);
  },
  
  getForecastDetail: (zipCode, date = 'today') => {
    return api.get(`/forecast/${zipCode}?date=${date}`);
  },
};

export const sitesAPI = {
  getAllSites: () => {
    return api.get('/sites');
  },
  
  getSitesByZip: (zipCode) => {
    return api.get(`/sites/${zipCode}`);
  },
};

export const dispatchAPI = {
  generatePlan: (data) => {
    return api.post('/dispatch', data);
  },
  
  assignToDispatch: (data) => {
    return api.post('/dispatch/assign', data);
  },
};

export const inventoryAPI = {
  getExpiringItems: () => {
    return api.get('/inventory/expiring');
  },
  
  getSuggestedSites: (itemId) => {
    return api.get(`/inventory/expiring/${itemId}/sites`);
  },
};

export default api;

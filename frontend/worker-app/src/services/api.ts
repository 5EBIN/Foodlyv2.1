// API service for backend communication
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      await AsyncStorage.removeItem('auth_token');
    }
    return Promise.reject(error);
  }
);

export const apiService = {
  async login(credentials: { email: string; password: string }) {
    const response = await apiClient.post('/auth/login', credentials);
    const token = response.data.access_token || response.data.token;
    await AsyncStorage.setItem('auth_token', token);
    return response.data;
  },

  async logout() {
    await AsyncStorage.removeItem('auth_token');
  },

  async getOrders() {
    const response = await apiClient.get('/orders');
    return response.data;
  },

  async acceptOrder(orderId: string) {
    const response = await apiClient.post(`/orders/accept/${orderId}`);
    const order = response.data;
    // Store current job in AsyncStorage
    await AsyncStorage.setItem('current_job', JSON.stringify(order));
    return order;
  },

  async completeOrder(orderId: string) {
    const response = await apiClient.post(`/orders/complete/${orderId}`);
    return response.data;
  },

  async getEarnings() {
    const response = await apiClient.get('/earnings');
    return response.data;
  },
};

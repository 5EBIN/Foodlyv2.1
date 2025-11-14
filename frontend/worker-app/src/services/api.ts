// API service for backend communication
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://127.0.0.1:8000/api';

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
  async login(credentials: { username: string; password: string; userType?: string }) {
    const response = await apiClient.post('/auth/login', credentials);
    const { access_token, user_type } = response.data;
    await AsyncStorage.setItem('auth_token', access_token);
    // Store user type from response (backend determines it from user record)
    if (user_type) {
      await AsyncStorage.setItem('user_type', user_type);
    }
    return response.data;
  },

  async logout() {
    await AsyncStorage.removeItem('auth_token');
    await AsyncStorage.removeItem('user_type');
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
    // Get summary and history
    const [summary, history] = await Promise.all([
      apiClient.get('/earnings').catch(() => ({ data: null })),
      apiClient.get('/earnings/history').catch(() => ({ data: [] }))
    ]);
    
    // Return history with summary data
    return (history.data || []).map((earning: any) => ({
      ...earning,
      created_at: earning.timestamp,
      paid_out: true, // All earnings are considered paid
    }));
  },

  // Restaurant APIs
  async getRestaurants(lat?: number, lng?: number) {
    const params = new URLSearchParams();
    if (lat !== undefined) params.append('lat', lat.toString());
    if (lng !== undefined) params.append('lng', lng.toString());

    const response = await apiClient.get(`/restaurants?${params}`);
    return response.data;
  },

  async getRestaurant(id: number, lat?: number, lng?: number) {
    const params = new URLSearchParams();
    if (lat !== undefined) params.append('lat', lat.toString());
    if (lng !== undefined) params.append('lng', lng.toString());

    const response = await apiClient.get(`/restaurants/${id}?${params}`);
    return response.data;
  },

  // Customer Order APIs
  async createCustomerOrder(orderData: {
    restaurant_id: number;
    amount: number;
    delivery_address: string;
    delivery_lat: number;
    delivery_lng: number;
  }) {
    const response = await apiClient.post('/customer/orders', orderData);
    return response.data;
  },

  async getActiveOrder() {
    const response = await apiClient.get('/customer/orders/active');
    return response.data;
  },

  async getOrderHistory() {
    const response = await apiClient.get('/customer/orders/history');
    return response.data;
  },

  async getCustomerOrder(id: number) {
    const response = await apiClient.get(`/customer/orders/${id}`);
    return response.data;
  },
};

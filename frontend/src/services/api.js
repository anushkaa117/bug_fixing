import axios from 'axios';

// Create axios instance
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth-storage');
    if (token) {
      const parsedToken = JSON.parse(token);
      if (parsedToken.state?.token) {
        config.headers.Authorization = `Bearer ${parsedToken.state.token}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth-storage');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API methods
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  logout: () => api.post('/auth/logout'),
  googleLogin: () => api.get('/auth/google/login'),
  googleCallback: (code) => api.get(`/auth/google/callback?code=${code}`),
};

export const bugAPI = {
  getAll: (params) => api.get('/bugs', { params }),
  getById: (id) => api.get(`/bugs/${id}`),
  create: (bugData) => api.post('/bugs', bugData),
  update: (id, bugData) => api.put(`/bugs/${id}`, bugData),
  delete: (id) => api.delete(`/bugs/${id}`),
  addComment: (id, comment) => api.post(`/bugs/${id}/comments`, comment),
  getStats: () => api.get('/bugs/stats'),
};

export const userAPI = {
  getProfile: () => api.get('/users/profile'),
  updateProfile: (userData) => api.put('/users/profile', userData),
  getAll: () => api.get('/users'),
};

export default api;

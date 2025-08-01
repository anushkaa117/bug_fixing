import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import axios from 'axios';

const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      loading: false,
      error: null,

      login: async (credentials) => {
        set({ loading: true, error: null });
        try {
          const response = await axios.post('/api/auth/login', credentials);
          const { user, token } = response.data;
          
          set({
            user,
            token,
            isAuthenticated: true,
            loading: false,
            error: null
          });

          // Set axios default header
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          
          return { success: true };
        } catch (error) {
          set({
            loading: false,
            error: error.response?.data?.message || 'Login failed'
          });
          return { success: false, error: error.response?.data?.message };
        }
      },

      register: async (userData) => {
        set({ loading: true, error: null });
        try {
          const response = await axios.post('/api/auth/register', userData);
          const { user, token } = response.data;
          
          set({
            user,
            token,
            isAuthenticated: true,
            loading: false,
            error: null
          });

          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          
          return { success: true };
        } catch (error) {
          set({
            loading: false,
            error: error.response?.data?.message || 'Registration failed'
          });
          return { success: false, error: error.response?.data?.message };
        }
      },

      googleLogin: async () => {
        set({ loading: true, error: null });
        try {
          // Get Google auth URL
          const response = await axios.get('/api/auth/google/login');
          const { auth_url } = response.data;
          
          // Redirect to Google OAuth
          window.location.href = auth_url;
        } catch (error) {
          set({
            loading: false,
            error: error.response?.data?.message || 'Google login failed'
          });
          return { success: false, error: error.response?.data?.message };
        }
      },

      handleGoogleCallback: async (userData, token) => {
        set({ loading: true, error: null });
        try {
          set({
            user: userData,
            token,
            isAuthenticated: true,
            loading: false,
            error: null
          });

          // Set axios default header
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          
          return { success: true };
        } catch (error) {
          set({
            loading: false,
            error: error.response?.data?.message || 'Google callback failed'
          });
          return { success: false, error: error.response?.data?.message };
        }
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          loading: false,
          error: null
        });
        delete axios.defaults.headers.common['Authorization'];
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

export { useAuthStore };

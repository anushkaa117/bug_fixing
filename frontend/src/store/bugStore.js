import { create } from 'zustand';
import { bugAPI } from '../services/api';

const useBugStore = create((set, get) => ({
  bugs: [],
  currentBug: null,
  loading: false,
  error: null,
  filters: {
    status: 'all',
    priority: 'all',
    assignee: 'all',
    search: ''
  },

  // Fetch all bugs
  fetchBugs: async (params = {}) => {
    set({ loading: true, error: null });
    try {
      const response = await bugAPI.getAll({ ...get().filters, ...params });
      set({ bugs: response.data, loading: false });
    } catch (error) {
      set({ 
        error: error.response?.data?.message || 'Failed to fetch bugs',
        loading: false 
      });
    }
  },

  // Fetch single bug
  fetchBug: async (id) => {
    set({ loading: true, error: null });
    try {
      const response = await bugAPI.getById(id);
      set({ currentBug: response.data, loading: false });
    } catch (error) {
      set({ 
        error: error.response?.data?.message || 'Failed to fetch bug',
        loading: false 
      });
    }
  },

  // Create new bug
  createBug: async (bugData) => {
    set({ loading: true, error: null });
    try {
      const response = await bugAPI.create(bugData);
      const newBug = response.data;
      set(state => ({ 
        bugs: [newBug, ...state.bugs],
        loading: false 
      }));
      return { success: true, bug: newBug };
    } catch (error) {
      set({ 
        error: error.response?.data?.message || 'Failed to create bug',
        loading: false 
      });
      return { success: false, error: error.response?.data?.message };
    }
  },

  // Update bug
  updateBug: async (id, bugData) => {
    set({ loading: true, error: null });
    try {
      const response = await bugAPI.update(id, bugData);
      const updatedBug = response.data;
      set(state => ({
        bugs: state.bugs.map(bug => bug.id === id ? updatedBug : bug),
        currentBug: state.currentBug?.id === id ? updatedBug : state.currentBug,
        loading: false
      }));
      return { success: true, bug: updatedBug };
    } catch (error) {
      set({ 
        error: error.response?.data?.message || 'Failed to update bug',
        loading: false 
      });
      return { success: false, error: error.response?.data?.message };
    }
  },

  // Delete bug
  deleteBug: async (id) => {
    set({ loading: true, error: null });
    try {
      await bugAPI.delete(id);
      set(state => ({
        bugs: state.bugs.filter(bug => bug.id !== id),
        loading: false
      }));
      return { success: true };
    } catch (error) {
      set({ 
        error: error.response?.data?.message || 'Failed to delete bug',
        loading: false 
      });
      return { success: false, error: error.response?.data?.message };
    }
  },

  // Add comment to bug
  addComment: async (bugId, comment) => {
    try {
      const response = await bugAPI.addComment(bugId, comment);
      const updatedBug = response.data;
      set(state => ({
        currentBug: state.currentBug?.id === bugId ? updatedBug : state.currentBug,
        bugs: state.bugs.map(bug => bug.id === bugId ? updatedBug : bug)
      }));
      return { success: true };
    } catch (error) {
      set({ error: error.response?.data?.message || 'Failed to add comment' });
      return { success: false, error: error.response?.data?.message };
    }
  },

  // Set filters
  setFilters: (newFilters) => {
    set(state => ({ 
      filters: { ...state.filters, ...newFilters } 
    }));
  },

  // Clear error
  clearError: () => set({ error: null }),

  // Clear current bug
  clearCurrentBug: () => set({ currentBug: null }),
}));

export { useBugStore };

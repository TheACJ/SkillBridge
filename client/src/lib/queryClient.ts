import { QueryClient, onlineManager } from "@tanstack/react-query";
import { apiClient } from "./api";

// Set up online manager for offline support
onlineManager.setOnline(navigator.onLine);

// Listen for online/offline events
window.addEventListener('online', () => {
  onlineManager.setOnline(true);
});

window.addEventListener('offline', () => {
  onlineManager.setOnline(false);
});

// Create query client with default options
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchInterval: false,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: (failureCount, error: any) => {
        // Don't retry on 4xx errors (client errors)
        if (error?.message?.includes('4')) {
          return false;
        }
        // Don't retry when offline
        if (!onlineManager.isOnline()) {
          return false;
        }
        // Retry up to 2 times for other errors
        return failureCount < 2;
      },
      // Enable background refetching when coming back online
      refetchOnReconnect: true,
      // Cache data for offline use
      gcTime: 24 * 60 * 60 * 1000, // 24 hours
    },
    mutations: {
      retry: false,
      // Mutations will be queued when offline
      networkMode: 'offlineFirst',
    },
  },
});

// Export API client for direct use
export { apiClient };

// Django API base URL
export const DJANGO_API_BASE = import.meta.env.VITE_DJANGO_API_URL || 'http://localhost:8000/api/v1';

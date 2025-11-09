import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import type { User, LoginCredentials, RegisterData } from "@shared/schema";

export function useAuth() {
  const { data: user, isLoading } = useQuery<User>({
    queryKey: ['user-profile'],
    queryFn: () => apiClient.getUserProfile(),
    retry: false,
    enabled: !!localStorage.getItem('access_token'),
  });

  return {
    user,
    isLoading,
    isAuthenticated: !!user,
  };
}

export function useLogin() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (credentials: LoginCredentials) => apiClient.login(credentials),
    onSuccess: (data) => {
      // Store tokens
      localStorage.setItem('access_token', data.tokens.access);
      localStorage.setItem('refresh_token', data.tokens.refresh);

      // Update user data in cache
      queryClient.setQueryData(['user-profile'], data.user);
    },
  });
}

export function useRegister() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: RegisterData) => apiClient.register(data),
    onSuccess: (data) => {
      // Store tokens
      localStorage.setItem('access_token', data.tokens.access);
      localStorage.setItem('refresh_token', data.tokens.refresh);

      // Update user data in cache
      queryClient.setQueryData(['user-profile'], data.user);
    },
  });
}

export function useLogout() {
  const queryClient = useQueryClient();

  return {
    logout: () => {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      queryClient.clear();
    }
  };
}

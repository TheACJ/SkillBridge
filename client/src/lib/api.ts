// API client for Django backend integration
import type {
  User,
  Roadmap,
  MentorMatch,
  ProgressEntry,
  ProgressAnalytics,
  Badge,
  LeaderboardEntry,
  Leaderboard,
  ForumPost,
  Notification,
  PaginatedResponse,
  ApiError,
  LoginCredentials,
  RegisterData,
  RoadmapGenerationData,
  ProgressLogData,
  MentorRequestData,
} from "@shared/schema";

interface HealthCheckResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  uptime: number;
  database: 'connected' | 'disconnected';
  version: string;
}

class DjangoAPIClient {
  private baseURL: string;

  constructor() {
    // Use environment variable for Django backend URL, fallback to localhost
    this.baseURL = import.meta.env.VITE_DJANGO_API_URL || 'http://localhost:8000/api/v1';
  }

  private async makeRequest(endpoint: string, options: RequestInit = {}): Promise<Response> {
    const url = `${this.baseURL}${endpoint}`;
    const config: RequestInit = {
      headers: {
        "Content-Type": "application/json",
        ...this.getAuthHeaders(),
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      return response;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  private getAuthHeaders(): Record<string, string> {
    const token = localStorage.getItem('access_token');
    if (token) {
      return { 'Authorization': `Bearer ${token}` };
    }
    return {};
  }

  // Health check endpoint - no auth required
  async healthCheck(): Promise<HealthCheckResponse> {
    const response = await this.makeRequest('/health/');

    if (!response.ok) {
      throw new Error('Health check failed');
    }

    return response.json();
  }

  // Authentication methods
  async register(data: RegisterData): Promise<{ user: User; tokens: { access: string; refresh: string } }> {
    const response = await this.makeRequest('/users/register/', {
      method: 'POST',
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.error.message);
    }

    return response.json();
  }

  async login(data: LoginCredentials): Promise<{ user: User; tokens: { access: string; refresh: string } }> {
    const response = await this.makeRequest('/users/login/', {
      method: 'POST',
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.error.message);
    }

    return response.json();
  }

  async refreshToken(data: { refresh: string }): Promise<{ access: string }> {
    const response = await this.makeRequest('/users/refresh-token/', {
      method: 'POST',
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.error.message);
    }

    return response.json();
  }

  // Password reset / forgot password
  async forgotPassword(data: { email: string }): Promise<{ detail: string }> {
    const response = await this.makeRequest('/users/password/reset/', {
      method: 'POST',
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error?.error?.message || 'Failed to request password reset');
    }

    return response.json();
  }

  // User methods
  async getUserProfile(): Promise<User> {
    const response = await this.makeRequest('/users/profile/');

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.error.message);
    }

    return response.json();
  }

  async updateUserProfile(data: Partial<User>): Promise<User> {
    const response = await this.makeRequest('/users/profile/', {
      method: 'PATCH',
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.error.message);
    }

    return response.json();
  }

  async getMentors(params?: { skills?: string; experience_level?: string; page?: number }): Promise<PaginatedResponse<User>> {
    const queryString = params ? new URLSearchParams(params as any).toString() : '';
    const response = await this.makeRequest(`/users/mentors/${queryString ? '?' + queryString : ''}`);

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.error.message);
    }

    return response.json();
  }

  // Roadmap methods
  async generateRoadmap(data: RoadmapGenerationData): Promise<Roadmap> {
    const response = await this.makeRequest('/roadmaps/generate/', {
      method: 'POST',
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.error.message);
    }

    return response.json();
  }

  async getUserRoadmaps(): Promise<PaginatedResponse<Roadmap>> {
    const response = await this.makeRequest('/roadmaps/');

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.error.message);
    }

    return response.json();
  }

  async getRoadmap(roadmapId: string): Promise<Roadmap> {
    const response = await this.makeRequest(`/roadmaps/${roadmapId}/`);

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.error.message);
    }

    return response.json();
  }

  async updateRoadmapProgress(roadmapId: string, moduleId: string, data: any): Promise<void> {
    const response = await this.makeRequest(`/roadmaps/${roadmapId}/modules/${moduleId}/progress/`, {
      method: 'POST',
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.error.message);
    }
  }

  // Matches methods
  async requestMentorMatch(data: MentorRequestData): Promise<MentorMatch> {
    const response = await this.makeRequest('/matches/request/', {
      method: 'POST',
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.error.message);
    }

    return response.json();
  }

  async getMatches(params?: { status?: string; role?: string }): Promise<PaginatedResponse<MentorMatch>> {
    const queryString = params ? new URLSearchParams(params).toString() : '';
    const response = await this.makeRequest(`/matches/${queryString ? '?' + queryString : ''}`);

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.error.message);
    }

    return response.json();
  }

  async respondToMatch(matchId: string, data: { action: 'accept' | 'reject'; message?: string }): Promise<void> {
    const response = await this.makeRequest(`/matches/${matchId}/respond/`, {
      method: 'POST',
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.error.message);
    }
  }

  // Progress methods
  async logProgress(data: ProgressLogData): Promise<ProgressEntry> {
    const response = await this.makeRequest('/progress/log/', {
      method: 'POST',
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.error.message);
    }

    return response.json();
  }

  async getProgressAnalytics(params?: { period?: string; roadmap_id?: number }): Promise<ProgressAnalytics> {
    const queryString = params ? new URLSearchParams(params as any).toString() : '';
    const response = await this.makeRequest(`/progress/analytics/${queryString ? '?' + queryString : ''}`);

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.error.message);
    }

    return response.json();
  }

  // Badges methods
  async getEarnedBadges(): Promise<PaginatedResponse<Badge>> {
    const response = await this.makeRequest('/badges/');

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.error.message);
    }

    return response.json();
  }

  async getLeaderboard(params?: { category?: string; limit?: number }): Promise<Leaderboard> {
    const queryString = params ? new URLSearchParams(params as any).toString() : '';
    const response = await this.makeRequest(`/leaderboard/${queryString ? '?' + queryString : ''}`);

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.error.message);
    }

    return response.json();
  }

  // Forum methods
  async getForumPosts(params?: { category?: string; tags?: string; sort?: string }): Promise<PaginatedResponse<ForumPost>> {
    const queryString = params ? new URLSearchParams(params as any).toString() : '';
    const response = await this.makeRequest(`/forum/discussions/${queryString ? '?' + queryString : ''}`);

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.error.message);
    }

    return response.json();
  }

  async createForumPost(data: { title: string; content: string; category: string; tags?: string[] }): Promise<ForumPost> {
    const response = await this.makeRequest('/forum/discussions/', {
      method: 'POST',
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.error.message);
    }

    return response.json();
  }

  // Notifications methods
  async getNotifications(params?: { unread_only?: boolean; type?: string }): Promise<PaginatedResponse<Notification>> {
    const queryString = params ? new URLSearchParams(params as any).toString() : '';
    const response = await this.makeRequest(`/notifications/${queryString ? '?' + queryString : ''}`);

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.error.message);
    }

    return response.json();
  }

  async markNotificationAsRead(notificationId: number): Promise<void> {
    const response = await this.makeRequest(`/notifications/${notificationId}/read/`, {
      method: 'POST',
    });

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.error.message);
    }
  }

  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string; version: string }> {
    const response = await this.makeRequest('/health/');

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.error.message);
    }

    return response.json();
  }
}

// Create and export API client instance
export const apiClient = new DjangoAPIClient();

// Export types for convenience
export type {
  User,
  Roadmap,
  MentorMatch,
  ProgressEntry,
  ProgressAnalytics,
  Badge,
  LeaderboardEntry,
  Leaderboard,
  ForumPost,
  Notification,
  PaginatedResponse,
  ApiError,
  LoginCredentials,
  RegisterData,
  RoadmapGenerationData,
  ProgressLogData,
  MentorRequestData,
};
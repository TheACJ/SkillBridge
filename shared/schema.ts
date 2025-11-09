// Shared types for SkillBridge frontend and backend integration
// These types match the Django REST API models and serializers

import { z } from "zod";

// User types (matching Django User model)
export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  user_type: 'mentee' | 'mentor';
  skills: string[];
  experience_level: 'beginner' | 'intermediate' | 'advanced';
  bio?: string;
  github_username?: string;
  linkedin_url?: string;
  portfolio_url?: string;
  location?: string;
  availability: 'available' | 'busy' | 'unavailable';
  timezone?: string;
  languages: string[];
  profile_completion: number;
  is_active: boolean;
  date_joined: string;
  rating?: number;
  total_mentees?: number;
}

// Roadmap types (matching Django Roadmap model)
export interface Roadmap {
  id: number;
  title: string;
  description: string;
  goal: string;
  modules: RoadmapModule[];
  total_modules: number;
  estimated_total_hours: number;
  progress_percentage: number;
  created_at: string;
  updated_at: string;
}

export interface RoadmapModule {
  id: number;
  title: string;
  description: string;
  order: number;
  estimated_hours: number;
  completed: boolean;
  progress_percentage: number;
  resources: Resource[];
}

// Resource types
export interface Resource {
  id: number;
  title: string;
  type: 'book' | 'video' | 'article' | 'course' | 'tutorial';
  url: string;
  platform?: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  duration?: string;
  thumbnail?: string;
}

// Mentor Match types
export interface MentorMatch {
  id: number;
  mentee: User;
  mentor: User;
  status: 'pending' | 'accepted' | 'active' | 'completed' | 'cancelled';
  message: string;
  topics: string[];
  created_at: string;
  updated_at: string;
  last_activity?: string;
  unread_messages?: number;
}

// Progress types
export interface ProgressEntry {
  id: number;
  user_id: number;
  roadmap_id: number;
  module_id: number;
  activity_type: 'study' | 'practice' | 'project' | 'review';
  description: string;
  time_spent_minutes: number;
  difficulty_rating: 1 | 2 | 3 | 4 | 5;
  notes?: string;
  resources_used: string[];
  created_at: string;
}

export interface ProgressAnalytics {
  total_time_spent: number;
  average_session_length: number;
  current_streak_days: number;
  longest_streak_days: number;
  completion_rate: number;
  skill_progress: Record<string, number>;
  weekly_stats: WeeklyProgressStats[];
}

export interface WeeklyProgressStats {
  week: string;
  time_spent: number;
  modules_completed: number;
  average_difficulty: number;
}

// Badge types
export interface Badge {
  id: number;
  name: string;
  description: string;
  icon: string;
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
  category: 'progress' | 'achievement' | 'social' | 'learning';
  earned_at: string;
}

// Leaderboard types
export interface LeaderboardEntry {
  rank: number;
  user: {
    id: number;
    name: string;
    avatar?: string;
  };
  score: number;
  badges_count: number;
  streak_days: number;
}

export interface Leaderboard {
  leaderboard: LeaderboardEntry[];
  user_rank: {
    rank: number;
    score: number;
    change: number;
  };
}

// Forum types
export interface ForumPost {
  id: number;
  title: string;
  author: {
    id: number;
    name: string;
  };
  category: string;
  tags: string[];
  replies_count: number;
  views_count: number;
  last_activity: string;
  is_solved: boolean;
  created_at: string;
}

// Notification types
export interface Notification {
  id: number;
  type: 'match_request' | 'message' | 'badge_earned' | 'roadmap_complete' | 'system';
  title: string;
  message: string;
  data?: Record<string, any>;
  is_read: boolean;
  created_at: string;
}

// API Response types
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: Record<string, string[]>;
  };
}

// Form validation schemas using Zod
export const loginSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(1, "Password is required"),
});

export const registerSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
  first_name: z.string().min(1, "First name is required"),
  last_name: z.string().min(1, "Last name is required"),
  user_type: z.enum(['mentee', 'mentor'], {
    errorMap: () => ({ message: "Please select a user type" }),
  }),
  skills: z.array(z.string()).optional(),
  experience_level: z.enum(['beginner', 'intermediate', 'advanced']).optional(),
});

export const roadmapGenerationSchema = z.object({
  goal: z.string().min(10, "Goal must be at least 10 characters"),
  current_skills: z.array(z.string()).min(1, "At least one current skill is required"),
  target_skills: z.array(z.string()).min(1, "At least one target skill is required"),
  time_commitment: z.enum(['5_hours_week', '10_hours_week', '20_hours_week', 'full_time']),
  timeline_months: z.number().min(1).max(24),
  learning_style: z.enum(['hands_on', 'theory_first', 'balanced']),
});

export const progressLogSchema = z.object({
  roadmap_id: z.number(),
  module_id: z.number(),
  activity_type: z.enum(['study', 'practice', 'project', 'review']),
  description: z.string().min(10, "Description must be at least 10 characters"),
  time_spent_minutes: z.number().min(1).max(480), // Max 8 hours
  difficulty_rating: z.number().min(1).max(5),
  notes: z.string().optional(),
  resources_used: z.array(z.string()).optional(),
});

export const mentorRequestSchema = z.object({
  mentor_id: z.number(),
  message: z.string().min(20, "Message must be at least 20 characters"),
  topics: z.array(z.string()).min(1, "At least one topic is required"),
  availability: z.string().min(1, "Availability is required"),
  goals: z.string().min(10, "Goals must be at least 10 characters"),
});

// Type exports
export type LoginCredentials = z.infer<typeof loginSchema>;
export type RegisterData = z.infer<typeof registerSchema>;
export type RoadmapGenerationData = z.infer<typeof roadmapGenerationSchema>;
export type ProgressLogData = z.infer<typeof progressLogSchema>;
export type MentorRequestData = z.infer<typeof mentorRequestSchema>;

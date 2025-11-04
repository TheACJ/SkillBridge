import { db } from "./db";
import { eq, desc, and, sql, or } from "drizzle-orm";
import type {
  User,
  InsertUser,
  UpsertUser,
  Roadmap,
  InsertRoadmap,
  Module,
  InsertModule,
  Resource,
  InsertResource,
  Mentor,
  InsertMentor,
  MentorSession,
  InsertMentorSession,
  Badge,
  InsertBadge,
  UserBadge,
  InsertUserBadge,
  ForumPost,
  InsertForumPost,
  ForumReply,
  InsertForumReply,
  Progress,
  InsertProgress,
} from "@shared/schema";
import {
  users,
  roadmaps,
  modules,
  resources,
  mentors,
  mentorSessions,
  badges,
  userBadges,
  forumPosts,
  forumReplies,
  progress,
} from "@shared/schema";

export interface IStorage {
  // User operations (including Replit Auth required methods)
  getUser(id: string): Promise<User | undefined>;
  getUserByEmail(email: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  upsertUser(user: UpsertUser): Promise<User>; // For Replit Auth
  updateUser(id: string, updates: Partial<InsertUser>): Promise<User | undefined>;
  updateUserStreak(id: string, currentStreak: number, longestStreak: number): Promise<void>;

  // Roadmap operations
  getRoadmap(id: string): Promise<Roadmap | undefined>;
  getRoadmapsByUserId(userId: string): Promise<Roadmap[]>;
  createRoadmap(roadmap: InsertRoadmap): Promise<Roadmap>;
  updateRoadmap(id: string, updates: Partial<InsertRoadmap>): Promise<Roadmap | undefined>;
  deleteRoadmap(id: string): Promise<void>;

  // Module operations
  getModule(id: string): Promise<Module | undefined>;
  getModulesByRoadmapId(roadmapId: string): Promise<Module[]>;
  createModule(module: InsertModule): Promise<Module>;
  updateModule(id: string, updates: Partial<InsertModule>): Promise<Module | undefined>;
  deleteModule(id: string): Promise<void>;

  // Resource operations
  getResourcesByModuleId(moduleId: string): Promise<Resource[]>;
  createResource(resource: InsertResource): Promise<Resource>;
  deleteResource(id: string): Promise<void>;

  // Mentor operations
  getMentor(id: string): Promise<Mentor | undefined>;
  getMentorByUserId(userId: string): Promise<Mentor | undefined>;
  getAllMentors(filters?: { available?: boolean; expertise?: string }): Promise<(Mentor & { user: User })[]>;
  createMentor(mentor: InsertMentor): Promise<Mentor>;
  updateMentor(id: string, updates: Partial<InsertMentor>): Promise<Mentor | undefined>;

  // Mentor Session operations
  getMentorSession(id: string): Promise<MentorSession | undefined>;
  getMentorSessionsByLearnerId(learnerId: string): Promise<MentorSession[]>;
  getMentorSessionsByMentorId(mentorId: string): Promise<MentorSession[]>;
  createMentorSession(session: InsertMentorSession): Promise<MentorSession>;
  updateMentorSession(id: string, updates: Partial<InsertMentorSession>): Promise<MentorSession | undefined>;

  // Badge operations
  getAllBadges(): Promise<Badge[]>;
  createBadge(badge: InsertBadge): Promise<Badge>;
  getUserBadges(userId: string): Promise<(UserBadge & { badge: Badge })[]>;
  awardBadge(userBadge: InsertUserBadge): Promise<UserBadge>;

  // Forum operations
  getForumPost(id: string): Promise<(ForumPost & { author: User }) | undefined>;
  getAllForumPosts(filters?: { category?: string; limit?: number }): Promise<(ForumPost & { author: User })[]>;
  createForumPost(post: InsertForumPost): Promise<ForumPost>;
  updateForumPost(id: string, updates: Partial<InsertForumPost>): Promise<ForumPost | undefined>;
  incrementForumPostUpvotes(id: string): Promise<void>;

  // Forum Reply operations
  getForumRepliesByPostId(postId: string): Promise<(ForumReply & { author: User })[]>;
  createForumReply(reply: InsertForumReply): Promise<ForumReply>;
  incrementForumReplyUpvotes(id: string): Promise<void>;

  // Progress operations
  getProgress(userId: string, moduleId: string): Promise<Progress | undefined>;
  getProgressByUserId(userId: string): Promise<Progress[]>;
  createOrUpdateProgress(progress: InsertProgress): Promise<Progress>;
}

export class DbStorage implements IStorage {
  // User operations
  async getUser(id: string): Promise<User | undefined> {
    const result = await db.select().from(users).where(eq(users.id, id)).limit(1);
    return result[0];
  }

  async getUserByEmail(email: string): Promise<User | undefined> {
    const result = await db.select().from(users).where(eq(users.email, email)).limit(1);
    return result[0];
  }

  async createUser(user: InsertUser): Promise<User> {
    const result = await db.insert(users).values(user).returning();
    return result[0];
  }

  async upsertUser(userData: UpsertUser): Promise<User> {
    const result = await db
      .insert(users)
      .values(userData)
      .onConflictDoUpdate({
        target: users.id,
        set: {
          ...userData,
          updatedAt: new Date(),
        },
      })
      .returning();
    return result[0];
  }

  async updateUser(id: string, updates: Partial<InsertUser>): Promise<User | undefined> {
    const result = await db
      .update(users)
      .set(updates)
      .where(eq(users.id, id))
      .returning();
    return result[0];
  }

  async updateUserStreak(id: string, currentStreak: number, longestStreak: number): Promise<void> {
    await db
      .update(users)
      .set({
        currentStreak,
        longestStreak,
        lastActiveDate: new Date(),
      })
      .where(eq(users.id, id));
  }

  // Roadmap operations
  async getRoadmap(id: string): Promise<Roadmap | undefined> {
    const result = await db.select().from(roadmaps).where(eq(roadmaps.id, id)).limit(1);
    return result[0];
  }

  async getRoadmapsByUserId(userId: string): Promise<Roadmap[]> {
    return await db
      .select()
      .from(roadmaps)
      .where(eq(roadmaps.userId, userId))
      .orderBy(desc(roadmaps.createdAt));
  }

  async createRoadmap(roadmap: InsertRoadmap): Promise<Roadmap> {
    const result = await db.insert(roadmaps).values(roadmap).returning();
    return result[0];
  }

  async updateRoadmap(id: string, updates: Partial<InsertRoadmap>): Promise<Roadmap | undefined> {
    const result = await db
      .update(roadmaps)
      .set({ ...updates, updatedAt: new Date() })
      .where(eq(roadmaps.id, id))
      .returning();
    return result[0];
  }

  async deleteRoadmap(id: string): Promise<void> {
    await db.delete(roadmaps).where(eq(roadmaps.id, id));
  }

  // Module operations
  async getModule(id: string): Promise<Module | undefined> {
    const result = await db.select().from(modules).where(eq(modules.id, id)).limit(1);
    return result[0];
  }

  async getModulesByRoadmapId(roadmapId: string): Promise<Module[]> {
    return await db
      .select()
      .from(modules)
      .where(eq(modules.roadmapId, roadmapId))
      .orderBy(modules.order);
  }

  async createModule(module: InsertModule): Promise<Module> {
    const result = await db.insert(modules).values(module).returning();
    return result[0];
  }

  async updateModule(id: string, updates: Partial<InsertModule>): Promise<Module | undefined> {
    const result = await db
      .update(modules)
      .set(updates)
      .where(eq(modules.id, id))
      .returning();
    return result[0];
  }

  async deleteModule(id: string): Promise<void> {
    await db.delete(modules).where(eq(modules.id, id));
  }

  // Resource operations
  async getResourcesByModuleId(moduleId: string): Promise<Resource[]> {
    return await db
      .select()
      .from(resources)
      .where(eq(resources.moduleId, moduleId))
      .orderBy(resources.order);
  }

  async createResource(resource: InsertResource): Promise<Resource> {
    const result = await db.insert(resources).values(resource).returning();
    return result[0];
  }

  async deleteResource(id: string): Promise<void> {
    await db.delete(resources).where(eq(resources.id, id));
  }

  // Mentor operations
  async getMentor(id: string): Promise<Mentor | undefined> {
    const result = await db.select().from(mentors).where(eq(mentors.id, id)).limit(1);
    return result[0];
  }

  async getMentorByUserId(userId: string): Promise<Mentor | undefined> {
    const result = await db.select().from(mentors).where(eq(mentors.userId, userId)).limit(1);
    return result[0];
  }

  async getAllMentors(filters?: { available?: boolean; expertise?: string }): Promise<(Mentor & { user: User })[]> {
    let query = db
      .select({
        id: mentors.id,
        userId: mentors.userId,
        expertise: mentors.expertise,
        rating: mentors.rating,
        totalSessions: mentors.totalSessions,
        availableSlots: mentors.availableSlots,
        isAvailable: mentors.isAvailable,
        bio: mentors.bio,
        hourlyRate: mentors.hourlyRate,
        createdAt: mentors.createdAt,
        user: users,
      })
      .from(mentors)
      .innerJoin(users, eq(mentors.userId, users.id));

    if (filters?.available !== undefined) {
      query = query.where(eq(mentors.isAvailable, filters.available)) as typeof query;
    }

    if (filters?.expertise) {
      query = query.where(sql`${filters.expertise} = ANY(${mentors.expertise})`) as typeof query;
    }

    return await query.orderBy(desc(mentors.rating));
  }

  async createMentor(mentor: InsertMentor): Promise<Mentor> {
    const result = await db.insert(mentors).values(mentor).returning();
    return result[0];
  }

  async updateMentor(id: string, updates: Partial<InsertMentor>): Promise<Mentor | undefined> {
    const result = await db
      .update(mentors)
      .set(updates)
      .where(eq(mentors.id, id))
      .returning();
    return result[0];
  }

  // Mentor Session operations
  async getMentorSession(id: string): Promise<MentorSession | undefined> {
    const result = await db.select().from(mentorSessions).where(eq(mentorSessions.id, id)).limit(1);
    return result[0];
  }

  async getMentorSessionsByLearnerId(learnerId: string): Promise<MentorSession[]> {
    return await db
      .select()
      .from(mentorSessions)
      .where(eq(mentorSessions.learnerId, learnerId))
      .orderBy(desc(mentorSessions.scheduledAt));
  }

  async getMentorSessionsByMentorId(mentorId: string): Promise<MentorSession[]> {
    return await db
      .select()
      .from(mentorSessions)
      .where(eq(mentorSessions.mentorId, mentorId))
      .orderBy(desc(mentorSessions.scheduledAt));
  }

  async createMentorSession(session: InsertMentorSession): Promise<MentorSession> {
    const result = await db.insert(mentorSessions).values(session).returning();
    return result[0];
  }

  async updateMentorSession(id: string, updates: Partial<InsertMentorSession>): Promise<MentorSession | undefined> {
    const result = await db
      .update(mentorSessions)
      .set(updates)
      .where(eq(mentorSessions.id, id))
      .returning();
    return result[0];
  }

  // Badge operations
  async getAllBadges(): Promise<Badge[]> {
    return await db.select().from(badges).orderBy(badges.name);
  }

  async createBadge(badge: InsertBadge): Promise<Badge> {
    const result = await db.insert(badges).values(badge).returning();
    return result[0];
  }

  async getUserBadges(userId: string): Promise<(UserBadge & { badge: Badge })[]> {
    return await db
      .select({
        id: userBadges.id,
        userId: userBadges.userId,
        badgeId: userBadges.badgeId,
        earnedAt: userBadges.earnedAt,
        badge: badges,
      })
      .from(userBadges)
      .innerJoin(badges, eq(userBadges.badgeId, badges.id))
      .where(eq(userBadges.userId, userId))
      .orderBy(desc(userBadges.earnedAt));
  }

  async awardBadge(userBadge: InsertUserBadge): Promise<UserBadge> {
    const result = await db.insert(userBadges).values(userBadge).returning();
    return result[0];
  }

  // Forum operations
  async getForumPost(id: string): Promise<(ForumPost & { author: User }) | undefined> {
    const result = await db
      .select({
        id: forumPosts.id,
        authorId: forumPosts.authorId,
        title: forumPosts.title,
        content: forumPosts.content,
        category: forumPosts.category,
        upvotes: forumPosts.upvotes,
        replyCount: forumPosts.replyCount,
        createdAt: forumPosts.createdAt,
        updatedAt: forumPosts.updatedAt,
        author: users,
      })
      .from(forumPosts)
      .innerJoin(users, eq(forumPosts.authorId, users.id))
      .where(eq(forumPosts.id, id))
      .limit(1);
    return result[0];
  }

  async getAllForumPosts(filters?: { category?: string; limit?: number }): Promise<(ForumPost & { author: User })[]> {
    let query = db
      .select({
        id: forumPosts.id,
        authorId: forumPosts.authorId,
        title: forumPosts.title,
        content: forumPosts.content,
        category: forumPosts.category,
        upvotes: forumPosts.upvotes,
        replyCount: forumPosts.replyCount,
        createdAt: forumPosts.createdAt,
        updatedAt: forumPosts.updatedAt,
        author: users,
      })
      .from(forumPosts)
      .innerJoin(users, eq(forumPosts.authorId, users.id));

    if (filters?.category) {
      query = query.where(eq(forumPosts.category, filters.category)) as typeof query;
    }

    query = query.orderBy(desc(forumPosts.createdAt)) as typeof query;

    if (filters?.limit) {
      query = query.limit(filters.limit) as typeof query;
    }

    return await query;
  }

  async createForumPost(post: InsertForumPost): Promise<ForumPost> {
    const result = await db.insert(forumPosts).values(post).returning();
    return result[0];
  }

  async updateForumPost(id: string, updates: Partial<InsertForumPost>): Promise<ForumPost | undefined> {
    const result = await db
      .update(forumPosts)
      .set({ ...updates, updatedAt: new Date() })
      .where(eq(forumPosts.id, id))
      .returning();
    return result[0];
  }

  async incrementForumPostUpvotes(id: string): Promise<void> {
    await db
      .update(forumPosts)
      .set({ upvotes: sql`${forumPosts.upvotes} + 1` })
      .where(eq(forumPosts.id, id));
  }

  // Forum Reply operations
  async getForumRepliesByPostId(postId: string): Promise<(ForumReply & { author: User })[]> {
    return await db
      .select({
        id: forumReplies.id,
        postId: forumReplies.postId,
        authorId: forumReplies.authorId,
        content: forumReplies.content,
        upvotes: forumReplies.upvotes,
        createdAt: forumReplies.createdAt,
        author: users,
      })
      .from(forumReplies)
      .innerJoin(users, eq(forumReplies.authorId, users.id))
      .where(eq(forumReplies.postId, postId))
      .orderBy(forumReplies.createdAt);
  }

  async createForumReply(reply: InsertForumReply): Promise<ForumReply> {
    const result = await db.insert(forumReplies).values(reply).returning();

    // Increment reply count on the post
    await db
      .update(forumPosts)
      .set({ replyCount: sql`${forumPosts.replyCount} + 1` })
      .where(eq(forumPosts.id, reply.postId));

    return result[0];
  }

  async incrementForumReplyUpvotes(id: string): Promise<void> {
    await db
      .update(forumReplies)
      .set({ upvotes: sql`${forumReplies.upvotes} + 1` })
      .where(eq(forumReplies.id, id));
  }

  // Progress operations
  async getProgress(userId: string, moduleId: string): Promise<Progress | undefined> {
    const result = await db
      .select()
      .from(progress)
      .where(and(eq(progress.userId, userId), eq(progress.moduleId, moduleId)))
      .limit(1);
    return result[0];
  }

  async getProgressByUserId(userId: string): Promise<Progress[]> {
    return await db
      .select()
      .from(progress)
      .where(eq(progress.userId, userId))
      .orderBy(desc(progress.updatedAt));
  }

  async createOrUpdateProgress(progressData: InsertProgress): Promise<Progress> {
    const existing = await this.getProgress(progressData.userId, progressData.moduleId);

    if (existing) {
      const result = await db
        .update(progress)
        .set({ ...progressData, updatedAt: new Date() })
        .where(eq(progress.id, existing.id))
        .returning();
      return result[0];
    } else {
      const result = await db.insert(progress).values(progressData).returning();
      return result[0];
    }
  }
}

export const storage = new DbStorage();

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
from django.db.models import Count, Q, Avg
from .models import Badge
from users.models import User
from roadmaps.models import Roadmap
from progress.models import ProgressLog

logger = logging.getLogger(__name__)

class BadgeService:
    """Service class for badge awarding and management"""
    
    BADGE_DEFINITIONS = {
        'first_roadmap': {
            'name': 'First Steps',
            'description': 'Created your first learning roadmap',
            'icon': '🎯',
            'criteria': {'type': 'roadmap_count', 'value': 1}
        },
        'roadmap_master': {
            'name': 'Roadmap Master',
            'description': 'Completed 5 learning roadmaps',
            'icon': '👑',
            'criteria': {'type': 'completed_roadmaps', 'value': 5}
        },
        'fast_learner': {
            'name': 'Fast Learner',
            'description': 'Completed a roadmap in under 2 weeks',
            'icon': '⚡',
            'criteria': {'type': 'roadmap_completion_time', 'value': 14}
        },
        'consistent_learner': {
            'name': 'Consistent Learner',
            'description': 'Maintained a 7-day learning streak',
            'icon': '🔥',
            'criteria': {'type': 'learning_streak', 'value': 7}
        },
        'mentor_seeker': {
            'name': 'Mentor Seeker',
            'description': 'Connected with your first mentor',
            'icon': '🤝',
            'criteria': {'type': 'mentor_connections', 'value': 1}
        },
        'knowledge_sharer': {
            'name': 'Knowledge Sharer',
            'description': 'Created 10 forum posts',
            'icon': '💡',
            'criteria': {'type': 'forum_posts', 'value': 10}
        },
        'skill_explorer': {
            'name': 'Skill Explorer',
            'description': 'Started learning in 3 different domains',
            'icon': '🗺️',
            'criteria': {'type': 'domains_learned', 'value': 3}
        },
        'early_bird': {
            'name': 'Early Bird',
            'description': 'Completed 5 modules before 9 AM',
            'icon': '🌅',
            'criteria': {'type': 'early_completions', 'value': 5}
        },
        'night_owl': {
            'name': 'Night Owl',
            'description': 'Completed 5 modules after 9 PM',
            'icon': '🦉',
            'criteria': {'type': 'late_completions', 'value': 5}
        },
        'dedicated_learner': {
            'name': 'Dedicated Learner',
            'description': 'Logged 100+ learning hours',
            'icon': '📚',
            'criteria': {'type': 'total_hours', 'value': 100}
        },
        'social_learner': {
            'name': 'Social Learner',
            'description': 'Received 5+ upvotes on forum posts',
            'icon': '👥',
            'criteria': {'type': 'forum_upvotes', 'value': 5}
        },
        'perfectionist': {
            'name': 'Perfectionist',
            'description': 'Completed all modules in a roadmap',
            'icon': '💎',
            'criteria': {'type': 'perfect_completion', 'value': 1}
        }
    }
    
    @staticmethod
    def award_badge(user: User, badge_type: str) -> Optional[Badge]:
        """
        Award a badge to a user
        """
        try:
            # Check if user already has this badge
            existing_badge = Badge.objects.filter(mentor=user, type=badge_type).first()
            if existing_badge:
                logger.info(f"User {user.id} already has badge {badge_type}")
                return existing_badge
            
            # Get badge definition
            badge_def = BadgeService.BADGE_DEFINITIONS.get(badge_type)
            if not badge_def:
                logger.error(f"Unknown badge type: {badge_type}")
                return None
            
            # Create badge
            badge = Badge.objects.create(
                mentor=user,
                type=badge_type,
                criteria=badge_def
            )
            
            # Create notification
            try:
                from notifications.services import NotificationService
                NotificationService.create_notification(
                    user_id=str(user.id),
                    notification_type='badge',
                    content=f"🎉 Congratulations! You earned the '{badge_def['name']}' badge!",
                    action_url=f"{settings.FRONTEND_URL}/dashboard/badges",
                    priority='normal'
                )
            except Exception as e:
                logger.error(f"Error creating badge notification: {str(e)}")
            
            logger.info(f"Badge {badge_type} awarded to user {user.id}")
            return badge
            
        except Exception as e:
            logger.error(f"Error awarding badge {badge_type} to user {user.id}: {str(e)}")
            return None
    
    @staticmethod
    def check_and_award_badges(user: User) -> List[Badge]:
        """
        Check all badge criteria and award applicable badges
        """
        try:
            newly_awarded = []
            
            for badge_type, badge_def in BadgeService.BADGE_DEFINITIONS.items():
                if BadgeService._check_badge_criteria(user, badge_def['criteria']):
                    badge = BadgeService.award_badge(user, badge_type)
                    if badge:
                        newly_awarded.append(badge)
            
            return newly_awarded
            
        except Exception as e:
            logger.error(f"Error checking and awarding badges for user {user.id}: {str(e)}")
            return []
    
    @staticmethod
    def _check_badge_criteria(user: User, criteria: Dict[str, Any]) -> bool:
        """
        Check if user meets badge criteria
        """
        try:
            criteria_type = criteria.get('type')
            required_value = criteria.get('value', 0)
            
            if criteria_type == 'roadmap_count':
                count = Roadmap.objects.filter(user=user).count()
                return count >= required_value
            
            elif criteria_type == 'completed_roadmaps':
                count = Roadmap.objects.filter(
                    user=user,
                    progress=100
                ).count()
                return count >= required_value
            
            elif criteria_type == 'roadmap_completion_time':
                # Check if any roadmap was completed in under X days
                roadmaps = Roadmap.objects.filter(
                    user=user,
                    progress=100
                )
                
                for roadmap in roadmaps:
                    completion_time = (roadmap.updated_at - roadmap.created_at).days
                    if completion_time <= required_value:
                        return True
                return False
            
            elif criteria_type == 'learning_streak':
                # This would need to be calculated from progress logs
                # For now, return False (would be implemented with proper streak tracking)
                return False
            
            elif criteria_type == 'mentor_connections':
                # This would check mentor matches
                from matches.models import MentorMatch
                count = MentorMatch.objects.filter(
                    learner=user,
                    status__in=['active', 'completed']
                ).count()
                return count >= required_value
            
            elif criteria_type == 'forum_posts':
                # This would check forum posts
                from forum.models import ForumPost
                count = ForumPost.objects.filter(user=user).count()
                return count >= required_value
            
            elif criteria_type == 'domains_learned':
                domains = Roadmap.objects.filter(user=user).values('domain').distinct()
                return len(domains) >= required_value
            
            elif criteria_type == 'total_hours':
                # Estimate from progress logs
                logs = ProgressLog.objects.filter(user=user, event_type='session_time')
                total_hours = sum(
                    log.details.get('duration', 0) for log in logs
                ) / 3600  # Convert seconds to hours
                return total_hours >= required_value
            
            elif criteria_type == 'perfect_completion':
                # Check if user has any roadmap with 100% completion
                count = Roadmap.objects.filter(user=user, progress=100).count()
                return count >= required_value
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking badge criteria: {str(e)}")
            return False
    
    @staticmethod
    def get_user_badges(user: User) -> List[Dict[str, Any]]:
        """
        Get all badges for a user
        """
        try:
            cache_key = f"user_badges_{user.id}"
            cached_result = cache.get(cache_key)
            
            if cached_result:
                return cached_result
            
            badges = Badge.objects.filter(mentor=user).order_by('-awarded_at')
            
            result = []
            for badge in badges:
                result.append({
                    'id': badge.id,
                    'type': badge.type,
                    'name': badge.criteria.get('name', badge.type),
                    'description': badge.criteria.get('description', ''),
                    'icon': badge.criteria.get('icon', '🏆'),
                    'awarded_at': badge.awarded_at.isoformat(),
                    'criteria': badge.criteria
                })
            
            # Cache for 10 minutes
            cache.set(cache_key, result, 600)
            return result
            
        except Exception as e:
            logger.error(f"Error getting user badges: {str(e)}")
            return []
    
    @staticmethod
    def get_available_badges() -> List[Dict[str, Any]]:
        """
        Get all available badge definitions
        """
        try:
            cache_key = "available_badges"
            cached_result = cache.get(cache_key)
            
            if cached_result:
                return cached_result
            
            result = []
            for badge_type, badge_def in BadgeService.BADGE_DEFINITIONS.items():
                result.append({
                    'type': badge_type,
                    'name': badge_def['name'],
                    'description': badge_def['description'],
                    'icon': badge_def['icon'],
                    'criteria': badge_def['criteria']
                })
            
            # Cache for 1 hour
            cache.set(cache_key, result, 3600)
            return result
            
        except Exception as e:
            logger.error(f"Error getting available badges: {str(e)}")
            return []
    
    @staticmethod
    def calculate_badge_progress(user: User, badge_type: str) -> Dict[str, Any]:
        """
        Calculate progress toward earning a badge
        """
        try:
            badge_def = BadgeService.BADGE_DEFINITIONS.get(badge_type)
            if not badge_def:
                return {}
            
            criteria = badge_def['criteria']
            criteria_type = criteria.get('type')
            required_value = criteria.get('value', 0)
            
            # Check current progress
            if criteria_type == 'roadmap_count':
                current = Roadmap.objects.filter(user=user).count()
                progress = min((current / required_value) * 100, 100)
                
                return {
                    'badge_type': badge_type,
                    'name': badge_def['name'],
                    'current': current,
                    'required': required_value,
                    'progress_percentage': round(progress, 2),
                    'description': badge_def['description']
                }
            
            elif criteria_type == 'completed_roadmaps':
                current = Roadmap.objects.filter(
                    user=user,
                    progress=100
                ).count()
                progress = min((current / required_value) * 100, 100)
                
                return {
                    'badge_type': badge_type,
                    'name': badge_def['name'],
                    'current': current,
                    'required': required_value,
                    'progress_percentage': round(progress, 2),
                    'description': badge_def['description']
                }
            
            elif criteria_type == 'mentor_connections':
                from matches.models import MentorMatch
                current = MentorMatch.objects.filter(
                    learner=user,
                    status__in=['active', 'completed']
                ).count()
                progress = min((current / required_value) * 100, 100)
                
                return {
                    'badge_type': badge_type,
                    'name': badge_def['name'],
                    'current': current,
                    'required': required_value,
                    'progress_percentage': round(progress, 2),
                    'description': badge_def['description']
                }
            
            elif criteria_type == 'domains_learned':
                domains = Roadmap.objects.filter(user=user).values('domain').distinct()
                current = len(domains)
                progress = min((current / required_value) * 100, 100)
                
                return {
                    'badge_type': badge_type,
                    'name': badge_def['name'],
                    'current': current,
                    'required': required_value,
                    'progress_percentage': round(progress, 2),
                    'description': badge_def['description']
                }
            
            # For other criteria types, return default structure with 0 progress
            return {
                'badge_type': badge_type,
                'name': badge_def['name'],
                'current': 0,
                'required': required_value,
                'progress_percentage': 0,
                'description': badge_def['description']
            }
            
        except Exception as e:
            logger.error(f"Error calculating badge progress: {str(e)}")
            return {}


class GamificationService:
    """Service class for gamification features and scoring"""
    
    POINTS_SYSTEM = {
        'roadmap_created': 10,
        'module_completed': 5,
        'roadmap_completed': 50,
        'forum_post_created': 2,
        'forum_post_upvoted': 1,
        'mentor_match_created': 15,
        'mentor_session_completed': 25,
        'daily_login': 1,
        'weekly_goal_achieved': 20,
        'streak_milestone': 30
    }
    
    LEVEL_THRESHOLDS = [
        (0, 1, 'Novice Learner'),
        (100, 2, 'Apprentice'),
        (250, 3, 'Scholar'),
        (500, 4, 'Expert'),
        (1000, 5, 'Master'),
        (2000, 6, 'Grandmaster'),
        (5000, 7, 'Legend')
    ]
    
    @staticmethod
    def award_points(user: User, action: str, metadata: Optional[Dict] = None) -> int:
        """
        Award points to a user for a specific action
        """
        try:
            points = GamificationService.POINTS_SYSTEM.get(action, 0)
            
            if points > 0:
                # Update user's total points
                user_profile = user.profile or {}
                current_points = user_profile.get('total_points', 0)
                user_profile['total_points'] = current_points + points
                user.profile = user_profile
                user.save()
                
                # Clear points cache
                GamificationService._clear_points_cache(user.id)
                
                logger.info(f"Awarded {points} points to user {user.id} for {action}")
                
                # Check for level up
                new_level = GamificationService._calculate_level(current_points + points)
                current_level = user_profile.get('level', 1)
                
                if new_level > current_level:
                    GamificationService._handle_level_up(user, new_level)
                
                # Check for badge eligibility
                try:
                    BadgeService.check_and_award_badges(user)
                except Exception as e:
                    logger.error(f"Error checking badges after points award: {str(e)}")
            
            return points
            
        except Exception as e:
            logger.error(f"Error awarding points to user {user.id}: {str(e)}")
            return 0
    
    @staticmethod
    def get_user_stats(user: User) -> Dict[str, Any]:
        """
        Get comprehensive gamification stats for a user
        """
        try:
            cache_key = f"user_gamification_stats_{user.id}"
            cached_result = cache.get(cache_key)
            
            if cached_result:
                return cached_result
            
            user_profile = user.profile or {}
            total_points = user_profile.get('total_points', 0)
            current_level = GamificationService._calculate_level(total_points)
            
            # Calculate points to next level
            next_level_info = GamificationService._get_next_level_info(total_points)
            
            # Get recent activity points
            recent_points = GamificationService._get_recent_points(user)
            
            # Get achievements (badges)
            badges = BadgeService.get_user_badges(user)
            
            stats = {
                'user_id': str(user.id),
                'total_points': total_points,
                'current_level': current_level,
                'current_level_name': next_level_info['current_name'],
                'next_level': next_level_info['next_level'],
                'next_level_name': next_level_info['next_name'],
                'points_to_next_level': next_level_info['points_needed'],
                'progress_to_next_level': next_level_info['progress_percentage'],
                'recent_points': recent_points,
                'badges_count': len(badges),
                'badges': badges,
                'rank': GamificationService._calculate_user_rank(user),
                'generated_at': datetime.now().isoformat()
            }
            
            # Cache for 15 minutes
            cache.set(cache_key, stats, 900)
            return stats
            
        except Exception as e:
            logger.error(f"Error getting user stats: {str(e)}")
            return {}
    
    @staticmethod
    def _calculate_level(points: int) -> int:
        """Calculate user level based on total points"""
        current_level = 1  # Default level
        for threshold, level, name in GamificationService.LEVEL_THRESHOLDS:
            if points >= threshold:
                current_level = level
            else:
                break
        return current_level
    
    @staticmethod
    def _get_next_level_info(points: int) -> Dict[str, Any]:
        """Get information about next level"""
        try:
            current_level = GamificationService._calculate_level(points)
            
            # Find current and next level thresholds
            next_level_info = None
            current_name = 'Novice Learner'
            current_threshold = 0
            next_threshold = 5000  # Default max
            
            for threshold, level, name in GamificationService.LEVEL_THRESHOLDS:
                if level == current_level:
                    current_name = name
                    current_threshold = threshold
                elif level == current_level + 1:
                    next_threshold = threshold
                    points_needed = max(0, next_threshold - points)
                    
                    # Calculate progress percentage in the current level range
                    level_range = next_threshold - current_threshold
                    progress_in_level = points - current_threshold
                    
                    if level_range > 0 and progress_in_level >= 0:
                        progress_percentage = min(100, (progress_in_level / level_range) * 100)
                    else:
                        progress_percentage = 0
                    
                    next_level_info = {
                        'next_level': level,
                        'next_name': name,
                        'points_needed': points_needed,
                        'progress_percentage': progress_percentage
                    }
                    break
            
            if not next_level_info:
                # User is at max level
                next_level_info = {
                    'next_level': current_level,
                    'next_name': current_name,
                    'points_needed': 0,
                    'progress_percentage': 100
                }
            
            next_level_info['current_name'] = current_name
            return next_level_info
            
        except Exception as e:
            logger.error(f"Error getting next level info: {str(e)}")
            return {
                'current_name': 'Unknown',
                'next_level': 1,
                'next_name': 'Learner',
                'points_needed': 100,
                'progress_percentage': 0
            }
    
    @staticmethod
    def _get_recent_points(user: User, days: int = 7) -> int:
        """Get points earned in recent timeframe"""
        try:
            # This would require a points transaction log in production
            # For now, return estimated value based on recent activity
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Estimate from progress logs
            recent_modules = ProgressLog.objects.filter(
                user=user,
                event_type='module_completed',
                timestamp__range=[start_date, end_date]
            ).count()
            
            recent_roadmaps = Roadmap.objects.filter(
                user=user,
                updated_at__range=[start_date, end_date],
                progress=100
            ).count()
            
            points = (recent_modules * 5) + (recent_roadmaps * 50)
            return points
            
        except Exception as e:
            logger.error(f"Error getting recent points: {str(e)}")
            return 0
    
    @staticmethod
    def _handle_level_up(user: User, new_level: int):
        """Handle level up event"""
        try:
            # Update user level
            user_profile = user.profile or {}
            user_profile['level'] = new_level
            user.profile = user_profile
            user.save()
            
            # Create level up notification
            try:
                from notifications.services import NotificationService
                level_info = GamificationService.LEVEL_THRESHOLDS[new_level - 1]
                level_name = level_info[2]
                
                NotificationService.create_notification(
                    user_id=str(user.id),
                    notification_type='level_up',
                    content=f"🎉 Congratulations! You've reached Level {new_level}: {level_name}!",
                    priority='high'
                )
            except Exception as e:
                logger.error(f"Error creating level up notification: {str(e)}")
            
            logger.info(f"User {user.id} leveled up to {new_level}")
            
        except Exception as e:
            logger.error(f"Error handling level up: {str(e)}")
    
    @staticmethod
    def _calculate_user_rank(user: User) -> Dict[str, Any]:
        """Calculate user's rank among all users"""
        try:
            from users.models import User
            
            # Get all users with points, including the current user
            all_users = User.objects.all()
            users_with_points = []
            
            for u in all_users:
                profile = u.profile or {}
                total_points = profile.get('total_points', 0)
                users_with_points.append((u, total_points))
            
            # Sort by points descending
            users_with_points.sort(key=lambda x: x[1], reverse=True)
            
            # Find user's rank
            user_rank = 1
            for rank, (other_user, points) in enumerate(users_with_points, 1):
                if other_user.id == user.id:
                    user_rank = rank
                    break
            
            total_users = len(users_with_points)
            
            return {
                'rank': user_rank,
                'total_users': total_users,
                'percentile': round(((total_users - user_rank) / total_users) * 100, 1) if total_users > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error calculating user rank: {str(e)}")
            return {'rank': 0, 'total_users': 0, 'percentile': 0}
    
    @staticmethod
    def _clear_points_cache(user_id: str):
        """Clear gamification cache for a user"""
        try:
            cache.delete(f"user_gamification_stats_{user_id}")
            # Clear leaderboard cache by deleting all known patterns
            if hasattr(cache, 'delete_pattern'):
                cache.delete_pattern(f"user_leaderboard_*")
            else:
                # For simple cache backends, just delete common keys
                cache.delete("user_leaderboard_all_time_50")
                cache.delete("user_leaderboard_weekly_50")
                cache.delete("user_leaderboard_monthly_50")
        except Exception as e:
            logger.error(f"Error clearing points cache: {str(e)}")
    
    @staticmethod
    def get_leaderboard(limit: int = 50, timeframe: str = 'all_time') -> List[Dict[str, Any]]:
        """
        Get user leaderboard
        """
        try:
            cache_key = f"user_leaderboard_{timeframe}_{limit}"
            cached_result = cache.get(cache_key)
            
            if cached_result:
                return cached_result
            
            from users.models import User
            
            queryset = User.objects.filter(
                profile__total_points__isnull=False
            ).order_by('-profile__total_points')[:limit]
            
            leaderboard = []
            for rank, user in enumerate(queryset, 1):
                user_profile = user.profile or {}
                total_points = user_profile.get('total_points', 0)
                level = GamificationService._calculate_level(total_points)
                
                leaderboard.append({
                    'rank': rank,
                    'user_id': str(user.id),
                    'email': user.email,
                    'total_points': total_points,
                    'level': level,
                    'level_name': GamificationService.LEVEL_THRESHOLDS[level - 1][2],
                    'badges_count': Badge.objects.filter(mentor=user).count()
                })
            
            # Cache for 30 minutes
            cache.set(cache_key, leaderboard, 1800)
            return leaderboard
            
        except Exception as e:
            logger.error(f"Error getting leaderboard: {str(e)}")
            return []
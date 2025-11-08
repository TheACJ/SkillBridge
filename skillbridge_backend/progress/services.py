import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from django.conf import settings
from django.db.models import Avg, Count, Q
from django.core.cache import cache
from .models import ProgressLog
from users.models import User
from roadmaps.models import Roadmap
from roadmaps.integrations import OpenAIIntegration

logger = logging.getLogger(__name__)

class ProgressService:
    """Service class for progress tracking and calculations"""
    
    @staticmethod
    def log_progress_event(user: User, event_type: str, details: Dict[str, Any], 
                          roadmap: Optional[Roadmap] = None) -> ProgressLog:
        """
        Log a progress event with comprehensive details
        """
        try:
            progress_log = ProgressLog.objects.create(
                user=user,
                roadmap=roadmap,
                event_type=event_type,
                details=details
            )
            
            # Clear related cache entries
            ProgressService._clear_progress_cache(user.id)
            
            return progress_log
            
        except Exception as e:
            logger.error(f"Error logging progress event: {str(e)}")
            raise
    
    @staticmethod
    def calculate_user_progress(user: User, roadmap: Optional[Roadmap] = None) -> Dict[str, Any]:
        """
        Calculate comprehensive user progress metrics
        """
        try:
            cache_key = f"user_progress_{user.id}_{roadmap.id if roadmap else 'all'}"
            cached_result = cache.get(cache_key)
            
            if cached_result:
                return cached_result
            
            if roadmap:
                # Progress for specific roadmap
                progress_data = ProgressService._calculate_roadmap_progress(user, roadmap)
            else:
                # Overall progress across all roadmaps
                progress_data = ProgressService._calculate_overall_progress(user)
            
            # Cache for 15 minutes
            cache.set(cache_key, progress_data, 900)
            return progress_data
            
        except Exception as e:
            logger.error(f"Error calculating user progress: {str(e)}")
            return {}
    
    @staticmethod
    def _calculate_roadmap_progress(user: User, roadmap: Roadmap) -> Dict[str, Any]:
        """Calculate progress for a specific roadmap"""
        try:
            # Get progress logs for this roadmap
            progress_logs = ProgressLog.objects.filter(
                user=user,
                roadmap=roadmap
            ).order_by('-timestamp')
            
            # Calculate completion percentage
            total_modules = len(roadmap.modules)
            completed_modules = sum(1 for module in roadmap.modules if module.get('completed', False))
            completion_percentage = (completed_modules / total_modules * 100) if total_modules > 0 else 0
            
            # Calculate time spent (estimated from logs)
            time_spent = ProgressService._estimate_time_spent(progress_logs)
            
            # Calculate recent activity
            recent_activity = ProgressService._get_recent_activity(progress_logs)
            
            # Get milestones achieved
            milestones = ProgressService._calculate_milestones(progress_logs, completed_modules, total_modules)
            
            return {
                'roadmap_id': roadmap.id,
                'domain': roadmap.domain,
                'completion_percentage': round(completion_percentage, 2),
                'completed_modules': completed_modules,
                'total_modules': total_modules,
                'time_spent_hours': time_spent,
                'recent_activity': recent_activity,
                'milestones': milestones,
                'next_milestone': ProgressService._get_next_milestone(completed_modules, total_modules),
                'progress_velocity': ProgressService._calculate_velocity(progress_logs),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating roadmap progress: {str(e)}")
            return {}
    
    @staticmethod
    def _calculate_overall_progress(user: User) -> Dict[str, Any]:
        """Calculate overall progress across all roadmaps"""
        try:
            roadmaps = Roadmap.objects.filter(user=user)
            total_roadmaps = roadmaps.count()
            
            if total_roadmaps == 0:
                return {
                    'total_roadmaps': 0,
                    'completed_roadmaps': 0,
                    'total_modules_completed': 0,
                    'average_completion': 0,
                    'total_time_spent': 0
                }
            
            completed_roadmaps = 0
            total_modules_completed = 0
            total_modules = 0
            total_time_spent = 0
            
            for roadmap in roadmaps:
                roadmap_progress = ProgressService._calculate_roadmap_progress(user, roadmap)
                completion_pct = roadmap_progress.get('completion_percentage', 0)
                
                if completion_pct >= 100:
                    completed_roadmaps += 1
                
                total_modules_completed += roadmap_progress.get('completed_modules', 0)
                total_modules += roadmap_progress.get('total_modules', 0)
                total_time_spent += roadmap_progress.get('time_spent_hours', 0)
            
            average_completion = (total_modules_completed / total_modules * 100) if total_modules > 0 else 0
            
            return {
                'total_roadmaps': total_roadmaps,
                'completed_roadmaps': completed_roadmaps,
                'total_modules_completed': total_modules_completed,
                'total_modules': total_modules,
                'average_completion': round(average_completion, 2),
                'total_time_spent_hours': round(total_time_spent, 2),
                'roadmap_breakdown': [
                    ProgressService._calculate_roadmap_progress(user, roadmap)
                    for roadmap in roadmaps
                ]
            }
            
        except Exception as e:
            logger.error(f"Error calculating overall progress: {str(e)}")
            return {}
    
    @staticmethod
    def _estimate_time_spent(progress_logs) -> float:
        """Estimate time spent based on progress logs"""
        try:
            # This is a simplified estimation - in production, you might use more sophisticated algorithms
            time_per_module = 2.0  # hours
            
            completions = progress_logs.filter(event_type='module_completed').count()
            return completions * time_per_module
            
        except Exception as e:
            logger.error(f"Error estimating time spent: {str(e)}")
            return 0.0
    
    @staticmethod
    def _get_recent_activity(progress_logs) -> List[Dict[str, Any]]:
        """Get recent activity from progress logs"""
        try:
            recent_logs = progress_logs[:5]  # Last 5 activities
            activities = []
            
            for log in recent_logs:
                activities.append({
                    'event_type': log.event_type,
                    'details': log.details,
                    'timestamp': log.timestamp.isoformat(),
                    'roadmap_domain': log.roadmap.domain if log.roadmap else None
                })
            
            return activities
            
        except Exception as e:
            logger.error(f"Error getting recent activity: {str(e)}")
            return []
    
    @staticmethod
    def _calculate_milestones(progress_logs, completed_modules: int, total_modules: int) -> List[Dict[str, Any]]:
        """Calculate achieved milestones"""
        try:
            milestones = []
            percentages = [25, 50, 75, 100]
            
            if total_modules == 0:
                return milestones
            
            current_percentage = (completed_modules / total_modules) * 100
            
            for percentage in percentages:
                if current_percentage >= percentage:
                    milestones.append({
                        'percentage': percentage,
                        'achieved': True,
                        'achieved_at': datetime.now().isoformat()
                    })
                else:
                    milestones.append({
                        'percentage': percentage,
                        'achieved': False
                    })
            
            return milestones
            
        except Exception as e:
            logger.error(f"Error calculating milestones: {str(e)}")
            return []
    
    @staticmethod
    def _get_next_milestone(completed_modules: int, total_modules: int) -> Optional[Dict[str, Any]]:
        """Get the next milestone to achieve"""
        try:
            if total_modules == 0:
                return None
            
            percentages = [25, 50, 75, 100]
            current_percentage = (completed_modules / total_modules) * 100
            
            for percentage in percentages:
                if current_percentage < percentage:
                    return {
                        'percentage': percentage,
                        'modules_remaining': int((percentage/100) * total_modules) - completed_modules,
                        'modules_target': int((percentage/100) * total_modules)
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting next milestone: {str(e)}")
            return None
    
    @staticmethod
    def _calculate_velocity(progress_logs) -> float:
        """Calculate learning velocity (modules per week)"""
        try:
            # Get logs from last 30 days
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_logs = progress_logs.filter(
                event_type='module_completed',
                timestamp__gte=thirty_days_ago
            )
            
            modules_completed = recent_logs.count()
            weeks = 30 / 7
            velocity = modules_completed / weeks
            
            return round(velocity, 2)
            
        except Exception as e:
            logger.error(f"Error calculating velocity: {str(e)}")
            return 0.0
    
    @staticmethod
    def _clear_progress_cache(user_id: str):
        """Clear progress-related cache for a user"""
        try:
            cache.delete(f"user_progress_{user_id}_all")
            
            # Clear roadmap-specific cache
            roadmaps = Roadmap.objects.filter(user_id=user_id)
            for roadmap in roadmaps:
                cache.delete(f"user_progress_{user_id}_{roadmap.id}")
                
        except Exception as e:
            logger.error(f"Error clearing progress cache: {str(e)}")


class AnalyticsService:
    """Service class for learning analytics and insights"""
    
    @staticmethod
    def get_learning_analytics(user: User, timeframe_days: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive learning analytics for a user
        """
        try:
            cache_key = f"learning_analytics_{user.id}_{timeframe_days}"
            cached_result = cache.get(cache_key)
            
            if cached_result:
                return cached_result
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=timeframe_days)
            
            # Get progress logs for the timeframe
            progress_logs = ProgressLog.objects.filter(
                user=user,
                timestamp__range=[start_date, end_date]
            )
            
            # Calculate various metrics
            analytics = {
                'timeframe_days': timeframe_days,
                'total_activities': progress_logs.count(),
                'learning_streak': AnalyticsService._calculate_learning_streak(user),
                'daily_activity': AnalyticsService._get_daily_activity(progress_logs, start_date, end_date),
                'skill_progress': AnalyticsService._get_skill_progress(user),
                'time_distribution': AnalyticsService._get_time_distribution(progress_logs),
                'productivity_metrics': AnalyticsService._get_productivity_metrics(progress_logs),
                'recommendations': AnalyticsService._generate_learning_recommendations(user, progress_logs),
                'generated_at': datetime.now().isoformat()
            }
            
            # Cache for 30 minutes
            cache.set(cache_key, analytics, 1800)
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting learning analytics: {str(e)}")
            return {}
    
    @staticmethod
    def _calculate_learning_streak(user: User) -> int:
        """Calculate current learning streak in days"""
        try:
            # Get consecutive days with activity
            today = datetime.now().date()
            streak = 0
            current_date = today
            
            while True:
                has_activity = ProgressLog.objects.filter(
                    user=user,
                    timestamp__date=current_date
                ).exists()
                
                if has_activity:
                    streak += 1
                    current_date -= timedelta(days=1)
                else:
                    break
            
            return streak
            
        except Exception as e:
            logger.error(f"Error calculating learning streak: {str(e)}")
            return 0
    
    @staticmethod
    def _get_daily_activity(progress_logs, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get daily activity breakdown"""
        try:
            daily_stats = []
            current_date = start_date.date()
            
            while current_date <= end_date.date():
                day_logs = progress_logs.filter(timestamp__date=current_date)
                
                daily_stats.append({
                    'date': current_date.isoformat(),
                    'activities': day_logs.count(),
                    'modules_completed': day_logs.filter(event_type='module_completed').count(),
                    'time_spent_hours': day_logs.filter(event_type='session_time').aggregate(
                        total_time=Avg('details__duration')
                    )['total_time'] or 0
                })
                
                current_date += timedelta(days=1)
            
            return daily_stats
            
        except Exception as e:
            logger.error(f"Error getting daily activity: {str(e)}")
            return []
    
    @staticmethod
    def _get_skill_progress(user: User) -> List[Dict[str, Any]]:
        """Get progress by skill/domain"""
        try:
            roadmaps = Roadmap.objects.filter(user=user)
            skill_progress = []
            
            for roadmap in roadmaps:
                progress_data = ProgressService._calculate_roadmap_progress(user, roadmap)
                skill_progress.append({
                    'domain': roadmap.domain,
                    'completion_percentage': progress_data.get('completion_percentage', 0),
                    'time_spent_hours': progress_data.get('time_spent_hours', 0),
                    'modules_completed': progress_data.get('completed_modules', 0)
                })
            
            return skill_progress
            
        except Exception as e:
            logger.error(f"Error getting skill progress: {str(e)}")
            return []
    
    @staticmethod
    def _get_time_distribution(progress_logs) -> Dict[str, Any]:
        """Get time distribution across different activity types"""
        try:
            time_by_event = {}
            
            # Group logs by event type and count
            event_counts = progress_logs.values('event_type').annotate(count=Count('id'))
            
            for event in event_counts:
                time_by_event[event['event_type']] = event['count']
            
            total_activities = sum(time_by_event.values())
            
            # Calculate percentages
            distribution = {}
            for event_type, count in time_by_event.items():
                distribution[event_type] = {
                    'count': count,
                    'percentage': round((count / total_activities * 100), 2) if total_activities > 0 else 0
                }
            
            return distribution
            
        except Exception as e:
            logger.error(f"Error getting time distribution: {str(e)}")
            return {}
    
    @staticmethod
    def _get_productivity_metrics(progress_logs) -> Dict[str, Any]:
        """Calculate productivity metrics"""
        try:
            # Calculate average sessions per week
            total_days = 30  # Default timeframe
            weeks = total_days / 7
            total_sessions = progress_logs.filter(event_type='session_start').count()
            sessions_per_week = total_sessions / weeks if weeks > 0 else 0
            
            # Calculate module completion rate
            total_attempts = progress_logs.filter(event_type='module_started').count()
            total_completions = progress_logs.filter(event_type='module_completed').count()
            completion_rate = (total_completions / total_attempts * 100) if total_attempts > 0 else 0
            
            return {
                'sessions_per_week': round(sessions_per_week, 2),
                'average_session_length_hours': 1.5,  # Estimated
                'module_completion_rate': round(completion_rate, 2),
                'total_modules_started': total_attempts,
                'total_modules_completed': total_completions
            }
            
        except Exception as e:
            logger.error(f"Error getting productivity metrics: {str(e)}")
            return {}
    
    @staticmethod
    def _generate_learning_recommendations(user: User, progress_logs) -> List[str]:
        """Generate personalized learning recommendations"""
        try:
            recommendations = []
            
            # Analyze learning patterns
            recent_activity = progress_logs.filter(
                timestamp__gte=datetime.now() - timedelta(days=7)
            ).count()
            
            if recent_activity < 3:
                recommendations.append("Consider setting a consistent learning schedule with at least 3 sessions per week")
            
            # Check for domain imbalance
            skill_progress = AnalyticsService._get_skill_progress(user)
            if len(skill_progress) > 1:
                active_domains = [s for s in skill_progress if s['completion_percentage'] > 10]
                if len(active_domains) > 2:
                    recommendations.append("Focus on completing existing roadmaps before starting new ones")
            
            # Time-based recommendations
            streak = AnalyticsService._calculate_learning_streak(user)
            if streak < 3:
                recommendations.append("Try to maintain a consistent learning streak for better retention")
            
            # Generic recommendations
            if not recommendations:
                recommendations.append("Great progress! Keep up the consistent learning schedule")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating learning recommendations: {str(e)}")
            return ["Continue your learning journey"]
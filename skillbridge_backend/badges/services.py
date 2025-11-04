import logging
from typing import Dict, List, Any, Optional
from django.db.models import Q, Count
from .models import Badge
from users.models import User
from matches.models import MentorMatch
from notifications.models import Notification

logger = logging.getLogger(__name__)

class BadgeService:
    """Service class for badge-related business logic"""

    # Badge criteria definitions
    BADGE_CRITERIA = {
        'first_session': {
            'name': 'First Steps',
            'description': 'Completed your first mentorship session',
            'tier': 'Bronze',
            'criteria': {'sessions_completed': 1},
            'icon': '🎯'
        },
        'five_sessions': {
            'name': 'Mentor Guide',
            'description': 'Completed 5 mentorship sessions',
            'tier': 'Bronze',
            'criteria': {'sessions_completed': 5},
            'icon': '📚'
        },
        'ten_sessions': {
            'name': 'Knowledge Sharer',
            'description': 'Completed 10 mentorship sessions',
            'tier': 'Silver',
            'criteria': {'sessions_completed': 10},
            'icon': '🎓'
        },
        'twenty_five_sessions': {
            'name': 'Expert Mentor',
            'description': 'Completed 25 mentorship sessions',
            'tier': 'Gold',
            'criteria': {'sessions_completed': 25},
            'icon': '👑'
        },
        'high_rated': {
            'name': 'Five-Star Mentor',
            'description': 'Achieved an average rating of 4.8 or higher',
            'tier': 'Gold',
            'criteria': {'average_rating': 4.8},
            'icon': '⭐'
        },
        'streak_learner': {
            'name': 'Consistent Learner',
            'description': 'Maintained a 7-day learning streak',
            'tier': 'Bronze',
            'criteria': {'learning_streak': 7},
            'icon': '🔥'
        },
        'streak_mentor': {
            'name': 'Dedicated Mentor',
            'description': 'Mentored for 30 consecutive days',
            'tier': 'Silver',
            'criteria': {'mentoring_streak': 30},
            'icon': '💪'
        }
    }

    @staticmethod
    def check_and_award_badges(user: User) -> List[Badge]:
        """
        Check if user qualifies for any badges and award them
        """
        awarded_badges = []

        try:
            if user.role == 'mentor':
                awarded_badges.extend(BadgeService._check_mentor_badges(user))
            elif user.role == 'learner':
                awarded_badges.extend(BadgeService._check_learner_badges(user))

        except Exception as e:
            logger.error(f"Error checking badges for user {user.id}: {str(e)}")

        return awarded_badges

    @staticmethod
    def _check_mentor_badges(mentor: User) -> List[Badge]:
        """Check and award badges for mentors"""
        awarded_badges = []

        try:
            # Get mentor statistics
            stats = BadgeService._get_mentor_stats(mentor)

            for badge_key, badge_config in BadgeService.BADGE_CRITERIA.items():
                if badge_key.startswith(('first_session', 'five_sessions', 'ten_sessions',
                                      'twenty_five_sessions', 'high_rated')):

                    # Check if mentor already has this badge
                    if Badge.objects.filter(mentor=mentor, type=badge_config['name']).exists():
                        continue

                    # Check criteria
                    if BadgeService._meets_criteria(stats, badge_config['criteria']):
                        badge = Badge.objects.create(
                            mentor=mentor,
                            type=badge_config['name'],
                            criteria=badge_config['criteria']
                        )
                        awarded_badges.append(badge)

                        # Create notification
                        Notification.objects.create(
                            user=mentor,
                            type='badge_awarded',
                            content=f"Congratulations! You've earned the '{badge_config['name']}' badge!",
                        )

                        logger.info(f"Awarded badge '{badge_config['name']}' to mentor {mentor.id}")

        except Exception as e:
            logger.error(f"Error checking mentor badges: {str(e)}")

        return awarded_badges

    @staticmethod
    def _check_learner_badges(learner: User) -> List[Badge]:
        """Check and award badges for learners"""
        awarded_badges = []

        try:
            # Get learner statistics
            stats = BadgeService._get_learner_stats(learner)

            for badge_key, badge_config in BadgeService.BADGE_CRITERIA.items():
                if badge_key.startswith(('streak_learner',)):

                    # Check if learner already has this badge
                    if Badge.objects.filter(mentor=learner, type=badge_config['name']).exists():
                        continue

                    # Check criteria
                    if BadgeService._meets_criteria(stats, badge_config['criteria']):
                        badge = Badge.objects.create(
                            mentor=learner,  # Note: using mentor field for learners too
                            type=badge_config['name'],
                            criteria=badge_config['criteria']
                        )
                        awarded_badges.append(badge)

                        # Create notification
                        Notification.objects.create(
                            user=learner,
                            type='badge_awarded',
                            content=f"Congratulations! You've earned the '{badge_config['name']}' badge!",
                        )

                        logger.info(f"Awarded badge '{badge_config['name']}' to learner {learner.id}")

        except Exception as e:
            logger.error(f"Error checking learner badges: {str(e)}")

        return awarded_badges

    @staticmethod
    def _get_mentor_stats(mentor: User) -> Dict[str, Any]:
        """Get statistics for a mentor"""
        try:
            matches = MentorMatch.objects.filter(mentor=mentor)

            completed_matches = matches.filter(status='completed')
            sessions_completed = completed_matches.count()

            # Calculate average rating
            ratings = [match.rating for match in completed_matches if match.rating]
            average_rating = sum(ratings) / len(ratings) if ratings else 0

            return {
                'sessions_completed': sessions_completed,
                'average_rating': round(average_rating, 1) if average_rating else 0,
                'total_matches': matches.count(),
                'active_matches': matches.filter(status='active').count(),
            }

        except Exception as e:
            logger.error(f"Error getting mentor stats: {str(e)}")
            return {}

    @staticmethod
    def _get_learner_stats(learner: User) -> Dict[str, Any]:
        """Get statistics for a learner"""
        try:
            # This would integrate with progress tracking
            # For now, return mock data
            return {
                'learning_streak': 0,  # Would be calculated from progress logs
                'completed_modules': 0,
                'total_study_time': 0,
            }

        except Exception as e:
            logger.error(f"Error getting learner stats: {str(e)}")
            return {}

    @staticmethod
    def _meets_criteria(stats: Dict[str, Any], criteria: Dict[str, Any]) -> bool:
        """Check if user stats meet badge criteria"""
        try:
            for key, value in criteria.items():
                if key not in stats:
                    return False
                if stats[key] < value:
                    return False
            return True

        except Exception as e:
            logger.error(f"Error checking criteria: {str(e)}")
            return False

    @staticmethod
    def get_badge_definitions() -> Dict[str, Dict[str, Any]]:
        """Get all available badge definitions"""
        return BadgeService.BADGE_CRITERIA.copy()

    @staticmethod
    def get_user_badges(user: User) -> List[Dict[str, Any]]:
        """Get all badges for a user with additional metadata"""
        try:
            badges = Badge.objects.filter(mentor=user).order_by('-awarded_at')

            badge_data = []
            for badge in badges:
                badge_info = BadgeService.BADGE_CRITERIA.get(
                    BadgeService._get_badge_key_by_name(badge.type), {}
                )

                badge_data.append({
                    'id': badge.id,
                    'name': badge.type,
                    'description': badge_info.get('description', ''),
                    'tier': badge_info.get('tier', 'Bronze'),
                    'icon': badge_info.get('icon', '🏆'),
                    'awarded_at': badge.awarded_at,
                    'criteria': badge.criteria,
                })

            return badge_data

        except Exception as e:
            logger.error(f"Error getting user badges: {str(e)}")
            return []

    @staticmethod
    def _get_badge_key_by_name(name: str) -> Optional[str]:
        """Get badge key by name"""
        for key, config in BadgeService.BADGE_CRITERIA.items():
            if config['name'] == name:
                return key
        return None

    @staticmethod
    def award_specific_badge(mentor: User, badge_type: str) -> Optional[Badge]:
        """Manually award a specific badge (admin function)"""
        try:
            if badge_type not in BadgeService.BADGE_CRITERIA:
                raise ValueError(f"Unknown badge type: {badge_type}")

            badge_config = BadgeService.BADGE_CRITERIA[badge_type]

            # Check if mentor already has this badge
            if Badge.objects.filter(mentor=mentor, type=badge_config['name']).exists():
                return None

            badge = Badge.objects.create(
                mentor=mentor,
                type=badge_config['name'],
                criteria=badge_config['criteria']
            )

            # Create notification
            Notification.objects.create(
                user=mentor,
                type='badge_awarded',
                content=f"Congratulations! You've been awarded the '{badge_config['name']}' badge!",
            )

            return badge

        except Exception as e:
            logger.error(f"Error awarding specific badge: {str(e)}")
            return None
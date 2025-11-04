import os
import hmac
import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from django.utils import timezone
from .models import ProgressLog
from roadmaps.models import Roadmap
from users.models import User
from notifications.models import Notification

logger = logging.getLogger(__name__)

class ProgressTrackingService:
    """Service class for progress tracking and GitHub integration"""

    GITHUB_WEBHOOK_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET', '')

    @staticmethod
    def process_github_webhook(payload: Dict[str, Any], signature: str = "") -> bool:
        """
        Process GitHub webhook payload for progress tracking
        """
        try:
            # Verify webhook signature if secret is configured
            if ProgressTrackingService.GITHUB_WEBHOOK_SECRET and signature:
                if not ProgressTrackingService._verify_github_signature(payload, signature):
                    logger.warning("Invalid GitHub webhook signature")
                    return False

            event_type = payload.get('action', 'push')

            if 'commits' in payload:
                return ProgressTrackingService._process_push_event(payload)
            elif event_type == 'opened' and 'pull_request' in payload:
                return ProgressTrackingService._process_pull_request_event(payload)
            elif event_type == 'opened' and 'issue' in payload:
                return ProgressTrackingService._process_issue_event(payload)

            return True

        except Exception as e:
            logger.error(f"Error processing GitHub webhook: {str(e)}")
            return False

    @staticmethod
    def _verify_github_signature(payload: Dict[str, Any], signature: str) -> bool:
        """Verify GitHub webhook signature"""
        try:
            if not signature.startswith('sha256='):
                return False

            expected_signature = 'sha256=' + hmac.new(
                ProgressTrackingService.GITHUB_WEBHOOK_SECRET.encode(),
                json.dumps(payload, separators=(',', ':')).encode(),
                hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(expected_signature, signature)

        except Exception as e:
            logger.error(f"Error verifying signature: {str(e)}")
            return False

    @staticmethod
    def _process_push_event(payload: Dict[str, Any]) -> bool:
        """Process GitHub push event"""
        try:
            repo_name = payload['repository']['full_name']
            commits = payload.get('commits', [])

            for commit in commits:
                author_email = commit['author']['email']

                # Find user by GitHub username/email
                user = ProgressTrackingService._find_user_by_github_info(author_email)
                if not user:
                    continue

                # Find relevant roadmap (this is simplified - in production, you'd match by repo)
                roadmap = ProgressTrackingService._find_relevant_roadmap(user, repo_name)
                if not roadmap:
                    continue

                # Log the commit
                ProgressLog.objects.create(
                    user=user,
                    roadmap=roadmap,
                    event_type='commit',
                    details={
                        'repo': repo_name,
                        'commit_hash': commit['id'],
                        'message': commit['message'],
                        'files_changed': len(commit.get('modified', [])) + len(commit.get('added', [])) + len(commit.get('removed', [])),
                        'url': commit['url']
                    }
                )

                # Update roadmap progress
                ProgressTrackingService._update_roadmap_progress_from_commits(roadmap, user)

            return True

        except Exception as e:
            logger.error(f"Error processing push event: {str(e)}")
            return False

    @staticmethod
    def _process_pull_request_event(payload: Dict[str, Any]) -> bool:
        """Process GitHub pull request event"""
        try:
            pr = payload['pull_request']
            author_email = pr['user']['login']  # GitHub username

            user = ProgressTrackingService._find_user_by_github_info(author_email)
            if not user:
                return True

            roadmap = ProgressTrackingService._find_relevant_roadmap(user, pr['base']['repo']['full_name'])
            if not roadmap:
                return True

            ProgressLog.objects.create(
                user=user,
                roadmap=roadmap,
                event_type='pull_request',
                details={
                    'pr_number': pr['number'],
                    'title': pr['title'],
                    'state': pr['state'],
                    'url': pr['html_url'],
                    'repo': pr['base']['repo']['full_name']
                }
            )

            return True

        except Exception as e:
            logger.error(f"Error processing PR event: {str(e)}")
            return False

    @staticmethod
    def _process_issue_event(payload: Dict[str, Any]) -> bool:
        """Process GitHub issue event"""
        try:
            issue = payload['issue']
            author_email = issue['user']['login']

            user = ProgressTrackingService._find_user_by_github_info(author_email)
            if not user:
                return True

            # Issues might not be directly tied to roadmaps, but could be learning-related
            ProgressLog.objects.create(
                user=user,
                roadmap=None,  # Issues might not be roadmap-specific
                event_type='issue',
                details={
                    'issue_number': issue['number'],
                    'title': issue['title'],
                    'state': issue['state'],
                    'url': issue['html_url'],
                    'repo': payload['repository']['full_name']
                }
            )

            return True

        except Exception as e:
            logger.error(f"Error processing issue event: {str(e)}")
            return False

    @staticmethod
    def _find_user_by_github_info(github_identifier: str) -> Optional[User]:
        """Find user by GitHub username or email"""
        try:
            # Try to find by email first
            user = User.objects.filter(email=github_identifier).first()
            if user:
                return user

            # Try to find by GitHub username in profile
            users = User.objects.filter(profile__github_username=github_identifier)
            return users.first()

        except Exception as e:
            logger.error(f"Error finding user by GitHub info: {str(e)}")
            return None

    @staticmethod
    def _find_relevant_roadmap(user: User, repo_name: str) -> Optional[Roadmap]:
        """Find the most relevant roadmap for a repository"""
        try:
            # This is a simplified implementation
            # In production, you'd have a mapping of repos to roadmaps
            roadmaps = Roadmap.objects.filter(user=user)

            # Try to match by domain keywords in repo name
            for roadmap in roadmaps:
                domain_keywords = roadmap.domain.lower().split()
                repo_lower = repo_name.lower()

                if any(keyword in repo_lower for keyword in domain_keywords):
                    return roadmap

            # Return the most recent roadmap if no match
            return roadmaps.order_by('-created_at').first()

        except Exception as e:
            logger.error(f"Error finding relevant roadmap: {str(e)}")
            return None

    @staticmethod
    def _update_roadmap_progress_from_commits(roadmap: Roadmap, user: User):
        """Update roadmap progress based on commit activity"""
        try:
            # Count commits in the last 30 days
            thirty_days_ago = timezone.now() - timedelta(days=30)
            recent_commits = ProgressLog.objects.filter(
                user=user,
                roadmap=roadmap,
                event_type='commit',
                timestamp__gte=thirty_days_ago
            ).count()

            # Simple progress calculation: more commits = more progress
            # This is highly simplified - in production, you'd have more sophisticated logic
            if recent_commits > 10:
                new_progress = min(roadmap.progress + 5, 100)
                if new_progress != roadmap.progress:
                    roadmap.progress = new_progress
                    roadmap.save()

                    # Create progress notification
                    Notification.objects.create(
                        user=user,
                        type='progress_update',
                        content=f"Great progress on your {roadmap.domain} roadmap! You've reached {new_progress}% completion.",
                    )

        except Exception as e:
            logger.error(f"Error updating roadmap progress: {str(e)}")

    @staticmethod
    def calculate_learning_streak(user: User) -> int:
        """
        Calculate the current learning streak for a user
        """
        try:
            # Get progress logs from the last 60 days
            sixty_days_ago = timezone.now() - timedelta(days=60)
            recent_logs = ProgressLog.objects.filter(
                user=user,
                timestamp__gte=sixty_days_ago
            ).order_by('-timestamp')

            if not recent_logs:
                return 0

            # Group by date and check for consecutive days
            streak = 0
            current_date = timezone.now().date()
            checked_dates = set()

            for log in recent_logs:
                log_date = log.timestamp.date()

                if log_date in checked_dates:
                    continue

                if log_date == current_date - timedelta(days=streak):
                    streak += 1
                    checked_dates.add(log_date)
                elif streak == 0 and log_date == current_date:
                    streak = 1
                    checked_dates.add(log_date)
                else:
                    break

            return streak

        except Exception as e:
            logger.error(f"Error calculating learning streak: {str(e)}")
            return 0

    @staticmethod
    def get_progress_summary(user: User) -> Dict[str, Any]:
        """
        Get comprehensive progress summary for a user
        """
        try:
            # Get all progress logs
            logs = ProgressLog.objects.filter(user=user)

            # Calculate various metrics
            total_commits = logs.filter(event_type='commit').count()
            total_prs = logs.filter(event_type='pull_request').count()
            total_issues = logs.filter(event_type='issue').count()

            # Get recent activity (last 7 days)
            week_ago = timezone.now() - timedelta(days=7)
            recent_logs = logs.filter(timestamp__gte=week_ago)

            # Calculate streaks
            learning_streak = ProgressTrackingService.calculate_learning_streak(user)

            return {
                'total_commits': total_commits,
                'total_pull_requests': total_prs,
                'total_issues': total_issues,
                'recent_activity_count': recent_logs.count(),
                'learning_streak_days': learning_streak,
                'most_active_day': ProgressTrackingService._get_most_active_day(logs),
                'progress_by_roadmap': ProgressTrackingService._get_progress_by_roadmap(user),
            }

        except Exception as e:
            logger.error(f"Error getting progress summary: {str(e)}")
            return {}

    @staticmethod
    def _get_most_active_day(logs: List[ProgressLog]) -> Optional[str]:
        """Get the day with most activity"""
        try:
            if not logs:
                return None

            day_counts = {}
            for log in logs:
                day = log.timestamp.strftime('%A')
                day_counts[day] = day_counts.get(day, 0) + 1

            return max(day_counts, key=day_counts.get) if day_counts else None

        except Exception:
            return None

    @staticmethod
    def _get_progress_by_roadmap(user: User) -> List[Dict[str, Any]]:
        """Get progress breakdown by roadmap"""
        try:
            roadmaps = Roadmap.objects.filter(user=user)
            progress_data = []

            for roadmap in roadmaps:
                logs_count = ProgressLog.objects.filter(
                    user=user,
                    roadmap=roadmap
                ).count()

                progress_data.append({
                    'roadmap_id': roadmap.id,
                    'domain': roadmap.domain,
                    'progress_percentage': roadmap.progress,
                    'activity_count': logs_count,
                })

            return progress_data

        except Exception as e:
            logger.error(f"Error getting progress by roadmap: {str(e)}")
            return []
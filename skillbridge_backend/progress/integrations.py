import os
import hmac
import hashlib
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from django.utils import timezone
from github import Github, GithubIntegration
from .models import ProgressLog
from users.models import User
from roadmaps.models import Roadmap

logger = logging.getLogger(__name__)

class GitHubIntegration:
    """Integration with GitHub for progress tracking"""

    def __init__(self):
        self.github_token = os.getenv('GITHUB_ACCESS_TOKEN')
        self.webhook_secret = os.getenv('GITHUB_WEBHOOK_SECRET')
        self.app_id = os.getenv('GITHUB_APP_ID')
        self.private_key = os.getenv('GITHUB_PRIVATE_KEY')

        # Initialize GitHub client
        if self.github_token:
            self.github = Github(self.github_token)
        elif self.app_id and self.private_key:
            # GitHub App authentication
            self.github = self._init_github_app()
        else:
            self.github = None
            logger.warning("GitHub credentials not configured")

    def _init_github_app(self) -> Optional[Github]:
        """Initialize GitHub App authentication"""
        try:
            integration = GithubIntegration(
                app_id=int(self.app_id),
                private_key=self.private_key
            )
            # This would need installation access token
            # For now, return None
            return None
        except Exception as e:
            logger.error(f"Failed to initialize GitHub App: {str(e)}")
            return None

    def process_webhook(self, payload: Dict[str, Any], signature: str = "") -> bool:
        """
        Process GitHub webhook payload
        """
        try:
            # Verify webhook signature
            if self.webhook_secret and signature:
                if not self._verify_signature(payload, signature):
                    logger.warning("Invalid GitHub webhook signature")
                    return False

            event_type = payload.get('action', 'push')

            if 'commits' in payload and payload.get('commits'):
                return self._process_push_event(payload)
            elif event_type == 'opened' and 'pull_request' in payload:
                return self._process_pull_request_event(payload)
            elif event_type == 'opened' and 'issue' in payload:
                return self._process_issue_event(payload)

            return True

        except Exception as e:
            logger.error(f"Error processing GitHub webhook: {str(e)}")
            return False

    def _verify_signature(self, payload: Dict[str, Any], signature: str) -> bool:
        """Verify GitHub webhook signature"""
        if not signature.startswith('sha256='):
            return False

        expected_signature = 'sha256=' + hmac.new(
            self.webhook_secret.encode(),
            json.dumps(payload, separators=(',', ':')).encode(),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected_signature, signature)

    def _process_push_event(self, payload: Dict[str, Any]) -> bool:
        """Process GitHub push event"""
        try:
            repo_full_name = payload['repository']['full_name']
            commits = payload.get('commits', [])

            # Extract pusher information
            pusher = payload.get('pusher', {})
            pusher_email = pusher.get('email')
            pusher_name = pusher.get('name')

            # Find user by email or name
            user = self._find_user_by_github_info(pusher_email, pusher_name)
            if not user:
                logger.info(f"No user found for GitHub pusher: {pusher_email or pusher_name}")
                return True

            # Find relevant roadmap
            roadmap = self._find_relevant_roadmap(user, repo_full_name)
            if not roadmap:
                logger.info(f"No relevant roadmap found for repo: {repo_full_name}")
                return True

            # Process each commit
            for commit in commits:
                self._log_commit(user, roadmap, commit, repo_full_name)

            # Update roadmap progress
            self._update_roadmap_progress_from_commits(roadmap, user)

            return True

        except Exception as e:
            logger.error(f"Error processing push event: {str(e)}")
            return False

    def _process_pull_request_event(self, payload: Dict[str, Any]) -> bool:
        """Process GitHub pull request event"""
        try:
            pr = payload['pull_request']
            repo_full_name = payload['repository']['full_name']

            # Find user
            user = self._find_user_by_github_info(
                pr['user']['login'],  # GitHub username
                pr['user'].get('email')
            )
            if not user:
                return True

            roadmap = self._find_relevant_roadmap(user, repo_full_name)
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
                    'repo': repo_full_name,
                    'additions': pr.get('additions', 0),
                    'deletions': pr.get('deletions', 0),
                    'changed_files': pr.get('changed_files', 0)
                }
            )

            return True

        except Exception as e:
            logger.error(f"Error processing PR event: {str(e)}")
            return False

    def _process_issue_event(self, payload: Dict[str, Any]) -> bool:
        """Process GitHub issue event"""
        try:
            issue = payload['issue']
            repo_full_name = payload['repository']['full_name']

            user = self._find_user_by_github_info(
                issue['user']['login'],
                issue['user'].get('email')
            )
            if not user:
                return True

            # Issues might not be tied to specific roadmaps
            ProgressLog.objects.create(
                user=user,
                roadmap=None,  # Issues are general learning activities
                event_type='issue',
                details={
                    'issue_number': issue['number'],
                    'title': issue['title'],
                    'state': issue['state'],
                    'url': issue['html_url'],
                    'repo': repo_full_name,
                    'labels': [label['name'] for label in issue.get('labels', [])]
                }
            )

            return True

        except Exception as e:
            logger.error(f"Error processing issue event: {str(e)}")
            return False

    def _log_commit(self, user: User, roadmap: Roadmap, commit: Dict[str, Any], repo_name: str):
        """Log a commit to the progress system"""
        try:
            ProgressLog.objects.create(
                user=user,
                roadmap=roadmap,
                event_type='commit',
                details={
                    'repo': repo_name,
                    'commit_hash': commit['id'],
                    'message': commit['message'],
                    'url': commit['url'],
                    'files_modified': len(commit.get('modified', [])),
                    'files_added': len(commit.get('added', [])),
                    'files_removed': len(commit.get('removed', [])),
                    'author': commit.get('author', {}).get('name', 'Unknown')
                }
            )

        except Exception as e:
            logger.error(f"Error logging commit: {str(e)}")

    def _find_user_by_github_info(self, identifier1: str, identifier2: Optional[str] = None) -> Optional[User]:
        """Find user by GitHub username or email"""
        try:
            # Try email first
            if identifier1 and '@' in identifier1:
                user = User.objects.filter(email=identifier1).first()
                if user:
                    return user

            # Try GitHub username in profile
            identifiers = [id for id in [identifier1, identifier2] if id]
            for identifier in identifiers:
                users = User.objects.filter(profile__github_username=identifier)
                if users.exists():
                    return users.first()

            return None

        except Exception as e:
            logger.error(f"Error finding user by GitHub info: {str(e)}")
            return None

    def _find_relevant_roadmap(self, user: User, repo_name: str) -> Optional[Roadmap]:
        """Find the most relevant roadmap for a repository"""
        try:
            roadmaps = Roadmap.objects.filter(user=user)

            # Try to match by domain keywords in repo name
            repo_lower = repo_name.lower()
            for roadmap in roadmaps:
                domain_keywords = roadmap.domain.lower().split()
                if any(keyword in repo_lower for keyword in domain_keywords):
                    return roadmap

            # Return most recent roadmap if no match
            return roadmaps.order_by('-created_at').first()

        except Exception as e:
            logger.error(f"Error finding relevant roadmap: {str(e)}")
            return None

    def _update_roadmap_progress_from_commits(self, roadmap: Roadmap, user: User):
        """Update roadmap progress based on recent commit activity"""
        try:
            # Count commits in last 30 days
            thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
            recent_commits = ProgressLog.objects.filter(
                user=user,
                roadmap=roadmap,
                event_type='commit',
                timestamp__gte=thirty_days_ago
            ).count()

            # Simple progress calculation
            if recent_commits > 10:
                new_progress = min(roadmap.progress + 5, 100)
                if new_progress != roadmap.progress:
                    roadmap.progress = new_progress
                    roadmap.save()

                    # Create progress notification
                    from notifications.models import Notification
                    Notification.objects.create(
                        user=user,
                        type='progress_update',
                        content=f"Great progress on your {roadmap.domain} roadmap! You've reached {new_progress}% completion.",
                    )

        except Exception as e:
            logger.error(f"Error updating roadmap progress: {str(e)}")

    def get_user_repositories(self, user: User) -> List[Dict[str, Any]]:
        """Get user's GitHub repositories"""
        if not self.github:
            return []

        try:
            github_username = user.profile.get('github_username') if user.profile else None
            if not github_username:
                return []

            user_repos = self.github.get_user(github_username).get_repos()
            return [
                {
                    'name': repo.name,
                    'full_name': repo.full_name,
                    'url': repo.html_url,
                    'language': repo.language,
                    'stars': repo.stargazers_count,
                    'forks': repo.forks_count,
                    'updated_at': repo.updated_at.isoformat() if repo.updated_at else None
                }
                for repo in user_repos[:10]  # Limit to 10 repos
            ]

        except Exception as e:
            logger.error(f"Error getting user repositories: {str(e)}")
            return []

    def validate_credentials(self) -> bool:
        """Validate GitHub credentials"""
        if not self.github:
            return False

        try:
            # Test API access
            self.github.get_user().login
            return True
        except Exception as e:
            logger.error(f"GitHub credentials validation failed: {str(e)}")
            return False
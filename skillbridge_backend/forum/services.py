import logging
from typing import Dict, List, Any, Optional
from django.db.models import Q, Count
from django.utils import timezone
from .models import ForumPost
from users.models import User

logger = logging.getLogger(__name__)

class ForumService:
    """Service class for forum-related business logic"""

    @staticmethod
    def create_post(user: User, category: str, content: str, parent_id: Optional[str] = None) -> ForumPost:
        """
        Create a new forum post or reply
        """
        try:
            parent = None
            if parent_id:
                parent = ForumPost.objects.get(id=parent_id)

            post = ForumPost.objects.create(
                user=user,
                category=category,
                content=content,
                parent=parent
            )

            # Update reply count on parent post if this is a reply
            if parent:
                ForumService._update_reply_count(parent)

            return post

        except Exception as e:
            logger.error(f"Error creating forum post: {str(e)}")
            raise

    @staticmethod
    def _update_reply_count(post: ForumPost):
        """Update the reply count for a post (cached for performance)"""
        try:
            reply_count = post.replies.count()
            # In production, you might cache this value in the post model
            # For now, we'll calculate it on demand
            pass

        except Exception as e:
            logger.error(f"Error updating reply count: {str(e)}")

    @staticmethod
    def search_posts(query: str, category: Optional[str] = None, limit: int = 50) -> List[ForumPost]:
        """
        Search forum posts by content, title, or author
        """
        try:
            posts = ForumPost.objects.select_related('user')

            # Apply category filter
            if category:
                posts = posts.filter(category=category)

            # Apply search query
            if query:
                posts = posts.filter(
                    Q(content__icontains=query) |
                    Q(user__email__icontains=query) |
                    Q(user__first_name__icontains=query) |
                    Q(user__last_name__icontains=query)
                )

            return posts.order_by('-created_at')[:limit]

        except Exception as e:
            logger.error(f"Error searching posts: {str(e)}")
            return []

    @staticmethod
    def get_popular_categories(limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most popular forum categories by post count
        """
        try:
            categories = ForumPost.objects.values('category').annotate(
                post_count=Count('id'),
                recent_posts=Count('id', filter=Q(created_at__gte=timezone.now() - timezone.timedelta(days=30)))
            ).order_by('-post_count')[:limit]

            return list(categories)

        except Exception as e:
            logger.error(f"Error getting popular categories: {str(e)}")
            return []

    @staticmethod
    def get_user_post_stats(user: User) -> Dict[str, Any]:
        """
        Get posting statistics for a user
        """
        try:
            posts = ForumPost.objects.filter(user=user)

            return {
                'total_posts': posts.count(),
                'total_replies': posts.filter(parent__isnull=False).count(),
                'original_posts': posts.filter(parent__isnull=True).count(),
                'categories_used': posts.values('category').distinct().count(),
                'most_active_category': ForumService._get_most_active_category(posts),
                'recent_activity': posts.filter(
                    created_at__gte=timezone.now() - timezone.timedelta(days=30)
                ).count()
            }

        except Exception as e:
            logger.error(f"Error getting user post stats: {str(e)}")
            return {}

    @staticmethod
    def _get_most_active_category(posts) -> Optional[str]:
        """Get the category where user is most active"""
        try:
            category_counts = posts.values('category').annotate(
                count=Count('id')
            ).order_by('-count')

            if category_counts:
                return category_counts[0]['category']
            return None

        except Exception:
            return None

    @staticmethod
    def moderate_post(post_id: str, action: str, moderator: User) -> bool:
        """
        Moderate a forum post (admin/moderator function)
        """
        try:
            if moderator.role != 'admin':
                raise PermissionError("Only admins can moderate posts")

            post = ForumPost.objects.get(id=post_id)

            if action == 'delete':
                post.delete()
                logger.info(f"Post {post_id} deleted by moderator {moderator.id}")
            elif action == 'hide':
                # In a real implementation, you'd add an 'is_hidden' field
                logger.info(f"Post {post_id} hidden by moderator {moderator.id}")
            else:
                raise ValueError(f"Unknown moderation action: {action}")

            return True

        except Exception as e:
            logger.error(f"Error moderating post: {str(e)}")
            return False

    @staticmethod
    def get_thread_with_replies(post_id: str, max_depth: int = 3) -> Optional[Dict[str, Any]]:
        """
        Get a complete thread with replies up to specified depth
        """
        try:
            root_post = ForumPost.objects.select_related('user').get(id=post_id)

            def build_thread(post, current_depth=0):
                if current_depth >= max_depth:
                    return None

                thread = {
                    'post': post,
                    'replies': []
                }

                replies = ForumPost.objects.select_related('user').filter(
                    parent=post
                ).order_by('created_at')

                for reply in replies:
                    reply_thread = build_thread(reply, current_depth + 1)
                    if reply_thread:
                        thread['replies'].append(reply_thread)

                return thread

            return build_thread(root_post)

        except ForumPost.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Error getting thread: {str(e)}")
            return None

    @staticmethod
    def get_featured_posts(limit: int = 5) -> List[ForumPost]:
        """
        Get featured/high-quality posts (based on engagement metrics)
        """
        try:
            # This is a simplified implementation
            # In production, you'd have voting/reputation systems
            posts = ForumPost.objects.select_related('user').filter(
                parent__isnull=True,  # Only original posts
                created_at__gte=timezone.now() - timezone.timedelta(days=30)  # Recent posts
            ).annotate(
                reply_count=Count('replies')
            ).filter(
                reply_count__gte=2  # Posts with at least 2 replies
            ).order_by('-reply_count', '-created_at')[:limit]

            return list(posts)

        except Exception as e:
            logger.error(f"Error getting featured posts: {str(e)}")
            return []

    @staticmethod
    def validate_post_content(content: str) -> Dict[str, Any]:
        """
        Validate forum post content
        """
        errors = {}

        if not content or not content.strip():
            errors['content'] = 'Content cannot be empty'

        if len(content) < 10:
            errors['content'] = 'Content must be at least 10 characters long'

        if len(content) > 10000:
            errors['content'] = 'Content cannot exceed 10,000 characters'

        # Check for spam patterns (simplified)
        spam_keywords = ['spam', 'advertisement', 'buy now']
        content_lower = content.lower()
        if any(keyword in content_lower for keyword in spam_keywords):
            errors['content'] = 'Content appears to contain spam'

        return errors

    @staticmethod
    def get_category_stats() -> Dict[str, Any]:
        """
        Get statistics for all forum categories
        """
        try:
            stats = {}

            categories = ForumPost.objects.values('category').distinct()

            for cat in categories:
                category = cat['category']
                posts = ForumPost.objects.filter(category=category)

                stats[category] = {
                    'total_posts': posts.count(),
                    'original_posts': posts.filter(parent__isnull=True).count(),
                    'replies': posts.filter(parent__isnull=False).count(),
                    'recent_posts': posts.filter(
                        created_at__gte=timezone.now() - timezone.timedelta(days=7)
                    ).count(),
                    'active_users': posts.values('user').distinct().count()
                }

            return stats

        except Exception as e:
            logger.error(f"Error getting category stats: {str(e)}")
            return {}
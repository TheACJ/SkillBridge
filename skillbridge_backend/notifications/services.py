import os
import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core.cache import cache
from .models import Notification

logger = logging.getLogger(__name__)

class NotificationService:
    """Service class for notification delivery and management"""
    
    @staticmethod
    def create_notification(user_id: str, notification_type: str, content: str, 
                          action_url: Optional[str] = None, metadata: Optional[Dict] = None,
                          priority: str = 'normal') -> Notification:
        """
        Create a notification with comprehensive metadata
        """
        try:
            notification = Notification.objects.create(
                user_id=user_id,
                type=notification_type,
                content=content,
                action_url=action_url,
                metadata=metadata or {},
                priority=priority
            )
            
            # Trigger immediate delivery if high priority
            if priority == 'high':
                NotificationService._deliver_notification(notification)
            
            return notification
            
        except Exception as e:
            logger.error(f"Error creating notification: {str(e)}")
            raise
    
    @staticmethod
    def deliver_notification(notification: Notification, channels: List[str] = None) -> bool:
        """
        Deliver notification through specified channels
        """
        try:
            if channels is None:
                channels = ['in_app']  # Default to in-app only
            
            delivery_results = {}
            
            for channel in channels:
                if channel == 'in_app':
                    delivery_results['in_app'] = True  # Already created
                elif channel == 'email':
                    delivery_results['email'] = NotificationService._send_email_notification(notification)
                elif channel == 'sms':
                    delivery_results['sms'] = NotificationService._send_sms_notification(notification)
                elif channel == 'push':
                    delivery_results['push'] = NotificationService._send_push_notification(notification)
            
            # Update notification with delivery status
            notification.metadata = {
                **(notification.metadata or {}),
                'delivery_results': delivery_results,
                'delivered_at': datetime.now().isoformat()
            }
            notification.save()
            
            return any(delivery_results.values())
            
        except Exception as e:
            logger.error(f"Error delivering notification: {str(e)}")
            return False
    
    @staticmethod
    def _send_email_notification(notification: Notification) -> bool:
        """Send email notification"""
        try:
            from users.models import User
            user = User.objects.get(id=notification.user_id)
            
            if not user.email:
                logger.warning(f"No email address for user {user.id}")
                return False
            
            subject = f"SkillBridge - {notification.type.title()}"
            
            # Create HTML email content
            html_content = NotificationService._create_email_html(notification, user)
            text_content = notification.content
            
            # Send email
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            email.attach_alternative(html_content, "text/html")
            
            email.send()
            
            logger.info(f"Email notification sent to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email notification: {str(e)}")
            return False
    
    @staticmethod
    def _send_sms_notification(notification: Notification) -> bool:
        """Send SMS notification (placeholder for SMS service integration)"""
        try:
            # Placeholder for SMS integration (Twilio, AWS SNS, etc.)
            # In production, implement actual SMS service here
            
            logger.info(f"SMS notification would be sent for notification {notification.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending SMS notification: {str(e)}")
            return False
    
    @staticmethod
    def _send_push_notification(notification: Notification) -> bool:
        """Send push notification (placeholder for push service integration)"""
        try:
            # Placeholder for push notification service (Firebase, AWS SNS, etc.)
            # In production, implement actual push service here
            
            logger.info(f"Push notification would be sent for notification {notification.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending push notification: {str(e)}")
            return False
    
    @staticmethod
    def _create_email_html(notification: Notification, user) -> str:
        """Create HTML email content"""
        try:
            context = {
                'user': user,
                'notification': notification,
                'action_url': notification.action_url,
                'timestamp': notification.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return render_to_string('emails/notification.html', context)
            
        except Exception as e:
            logger.error(f"Error creating email HTML: {str(e)}")
            return f"<p>{notification.content}</p>"
    
    @staticmethod
    def get_user_notifications(user_id: str, limit: int = 50, unread_only: bool = False) -> List[Dict[str, Any]]:
        """
        Get notifications for a user with filtering and pagination
        """
        try:
            cache_key = f"user_notifications_{user_id}_{limit}_{unread_only}"
            cached_result = cache.get(cache_key)
            
            if cached_result:
                return cached_result
            
            queryset = Notification.objects.filter(user_id=user_id)
            
            if unread_only:
                queryset = queryset.filter(read=False)
            
            notifications = queryset.order_by('-created_at')[:limit]
            
            result = [
                {
                    'id': notification.id,
                    'type': notification.type,
                    'content': notification.content,
                    'read': notification.read,
                    'priority': notification.priority,
                    'action_url': notification.action_url,
                    'metadata': notification.metadata,
                    'created_at': notification.created_at.isoformat(),
                    'read_at': notification.read_at.isoformat() if notification.read_at else None
                }
                for notification in notifications
            ]
            
            # Cache for 5 minutes
            cache.set(cache_key, result, 300)
            return result
            
        except Exception as e:
            logger.error(f"Error getting user notifications: {str(e)}")
            return []
    
    @staticmethod
    def mark_as_read(notification_id: str, user_id: str) -> bool:
        """
        Mark a notification as read
        """
        try:
            notification = Notification.objects.get(id=notification_id, user_id=user_id)
            notification.read = True
            notification.read_at = datetime.now()
            notification.save()
            
            # Clear related cache
            NotificationService._clear_notification_cache(user_id)
            
            return True
            
        except Notification.DoesNotExist:
            logger.warning(f"Notification {notification_id} not found for user {user_id}")
            return False
        except Exception as e:
            logger.error(f"Error marking notification as read: {str(e)}")
            return False
    
    @staticmethod
    def mark_all_as_read(user_id: str) -> int:
        """
        Mark all notifications as read for a user
        """
        try:
            updated_count = Notification.objects.filter(
                user_id=user_id,
                read=False
            ).update(read=True, read_at=datetime.now())
            
            # Clear related cache
            NotificationService._clear_notification_cache(user_id)
            
            return updated_count
            
        except Exception as e:
            logger.error(f"Error marking all notifications as read: {str(e)}")
            return 0
    
    @staticmethod
    def cleanup_old_notifications(days_old: int = 30) -> int:
        """
        Clean up old notifications
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            deleted_count, _ = Notification.objects.filter(
                read=True,
                read_at__lt=cutoff_date
            ).delete()
            
            logger.info(f"Cleaned up {deleted_count} old notifications")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old notifications: {str(e)}")
            return 0
    
    @staticmethod
    def _clear_notification_cache(user_id: str):
        """Clear notification cache for a user"""
        try:
            cache.delete_pattern(f"user_notifications_{user_id}_*")
        except Exception as e:
            logger.error(f"Error clearing notification cache: {str(e)}")
    
    @staticmethod
    def _deliver_notification(notification: Notification):
        """Immediate delivery for high priority notifications"""
        try:
            NotificationService.deliver_notification(notification, ['in_app', 'email'])
        except Exception as e:
            logger.error(f"Error delivering high priority notification: {str(e)}")


class EmailService:
    """Service class for email operations"""
    
    @staticmethod
    def send_welcome_email(user) -> bool:
        """Send welcome email to new users"""
        try:
            subject = "Welcome to SkillBridge - Your Learning Journey Begins!"
            
            context = {
                'user': user,
                'login_url': f"{settings.FRONTEND_URL}/login",
                'dashboard_url': f"{settings.FRONTEND_URL}/dashboard"
            }
            
            html_content = render_to_string('emails/welcome.html', context)
            text_content = f"""
            Welcome to SkillBridge, {user.email}!
            
            Your learning journey starts here. Visit your dashboard to:
            - Create your first learning roadmap
            - Find a mentor in your field
            - Join the learning community
            
            Get started: {context['dashboard_url']}
            """
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            
            logger.info(f"Welcome email sent to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending welcome email: {str(e)}")
            return False
    
    @staticmethod
    def send_mentor_match_email(learner, mentor, match) -> bool:
        """Send email when mentor match is created"""
        try:
            subject = "New Mentorship Request - SkillBridge"
            
            context = {
                'learner': learner,
                'mentor': mentor,
                'match': match,
                'dashboard_url': f"{settings.FRONTEND_URL}/dashboard"
            }
            
            html_content = render_to_string('emails/mentor_match.html', context)
            text_content = f"""
            New mentorship request received!
            
            {learner.email} has requested to be mentored by {mentor.email}.
            
            View details: {context['dashboard_url']}
            """
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[mentor.email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            
            logger.info(f"Mentor match email sent to {mentor.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending mentor match email: {str(e)}")
            return False
    
    @staticmethod
    def send_roadmap_completion_email(user, roadmap) -> bool:
        """Send email when roadmap is completed"""
        try:
            subject = f"Congratulations! You've completed your {roadmap.domain} roadmap"
            
            context = {
                'user': user,
                'roadmap': roadmap,
                'dashboard_url': f"{settings.FRONTEND_URL}/dashboard",
                'next_steps_url': f"{settings.FRONTEND_URL}/roadmaps/new"
            }
            
            html_content = render_to_string('emails/roadmap_completion.html', context)
            text_content = f"""
            Congratulations {user.email}!
            
            You've successfully completed your {roadmap.domain} learning roadmap!
            
            What's next?
            - Create a new roadmap
            - Share your achievement
            - Find a new mentor
            
            Continue your journey: {context['next_steps_url']}
            """
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            
            logger.info(f"Roadmap completion email sent to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending roadmap completion email: {str(e)}")
            return False
    
    @staticmethod
    def send_weekly_progress_email(user, progress_data) -> bool:
        """Send weekly progress summary email"""
        try:
            subject = "Your Weekly Learning Progress - SkillBridge"
            
            context = {
                'user': user,
                'progress_data': progress_data,
                'dashboard_url': f"{settings.FRONTEND_URL}/dashboard"
            }
            
            html_content = render_to_string('emails/weekly_progress.html', context)
            text_content = f"""
            Weekly Progress Summary for {user.email}
            
            Here's your learning progress this week:
            - Modules completed: {progress_data.get('modules_completed', 0)}
            - Time spent: {progress_data.get('time_spent_hours', 0)} hours
            - Learning streak: {progress_data.get('learning_streak', 0)} days
            
            View detailed progress: {context['dashboard_url']}
            """
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            
            logger.info(f"Weekly progress email sent to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending weekly progress email: {str(e)}")
            return False


class CommunicationService:
    """Service class for bulk communication operations"""
    
    @staticmethod
    def send_bulk_notifications(user_ids: List[str], notification_type: str, 
                              content: str, **kwargs) -> Dict[str, int]:
        """
        Send notifications to multiple users
        """
        try:
            results = {
                'total': len(user_ids),
                'successful': 0,
                'failed': 0
            }
            
            for user_id in user_ids:
                try:
                    notification = NotificationService.create_notification(
                        user_id=user_id,
                        notification_type=notification_type,
                        content=content,
                        **kwargs
                    )
                    
                    if NotificationService.deliver_notification(notification):
                        results['successful'] += 1
                    else:
                        results['failed'] += 1
                        
                except Exception as e:
                    logger.error(f"Failed to send notification to user {user_id}: {str(e)}")
                    results['failed'] += 1
            
            logger.info(f"Bulk notifications sent: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error sending bulk notifications: {str(e)}")
            return {'total': 0, 'successful': 0, 'failed': 0}
    
    @staticmethod
    def send_announcement_to_all_users(title: str, content: str, 
                                     priority: str = 'normal') -> Dict[str, int]:
        """
        Send announcement to all active users
        """
        try:
            from users.models import User
            
            active_users = User.objects.filter(is_active=True)
            user_ids = [str(user.id) for user in active_users]
            
            return CommunicationService.send_bulk_notifications(
                user_ids=user_ids,
                notification_type='announcement',
                content=f"{title}: {content}",
                priority=priority
            )
            
        except Exception as e:
            logger.error(f"Error sending announcement: {str(e)}")
            return {'total': 0, 'successful': 0, 'failed': 0}
    
    @staticmethod
    def get_communication_stats(days: int = 30) -> Dict[str, Any]:
        """
        Get communication statistics
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get notification statistics
            total_notifications = Notification.objects.filter(
                created_at__range=[start_date, end_date]
            ).count()
            
            unread_notifications = Notification.objects.filter(
                created_at__range=[start_date, end_date],
                read=False
            ).count()
            
            notifications_by_type = Notification.objects.filter(
                created_at__range=[start_date, end_date]
            ).values('type').annotate(count=Count('id'))
            
            # Email statistics (would require email tracking in production)
            emails_sent = 0  # Placeholder
            
            return {
                'timeframe_days': days,
                'total_notifications': total_notifications,
                'unread_notifications': unread_notifications,
                'notification_rate': round(total_notifications / days, 2),
                'notifications_by_type': dict(notifications_by_type),
                'emails_sent': emails_sent,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting communication stats: {str(e)}")
            return {}
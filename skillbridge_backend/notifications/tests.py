import json
import uuid
from datetime import datetime, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core import mail
from django.conf import settings
from unittest.mock import patch, MagicMock

from .models import Notification
from .services import NotificationService, EmailService, CommunicationService

User = get_user_model()

class NotificationServiceTest(TestCase):
    """Test cases for NotificationService"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            id=str(uuid.uuid4()),
            email='notify@example.com',
            password='testpass123',
            role='learner'
        )
        
        self.mentor = User.objects.create_user(
            id=str(uuid.uuid4()),
            email='mentor@example.com',
            password='testpass123',
            role='mentor'
        )
    
    def test_create_notification(self):
        """Test creating a notification"""
        notification = NotificationService.create_notification(
            user_id=str(self.user.id),
            notification_type='info',
            content='Test notification content',
            action_url='/test/action',
            priority='normal'
        )
        
        self.assertIsNotNone(notification)
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.type, 'info')
        self.assertEqual(notification.content, 'Test notification content')
        self.assertEqual(notification.action_url, '/test/action')
        self.assertEqual(notification.priority, 'normal')
        self.assertFalse(notification.read)
    
    def test_create_notification_with_metadata(self):
        """Test creating notification with metadata"""
        metadata = {'roadmap_id': '123', 'module_name': 'Python Basics'}
        
        notification = NotificationService.create_notification(
            user_id=str(self.user.id),
            notification_type='roadmap',
            content='Module completed!',
            metadata=metadata
        )
        
        self.assertIsNotNone(notification)
        self.assertEqual(notification.metadata, metadata)
    
    def test_create_high_priority_notification(self):
        """Test creating high priority notification"""
        notification = NotificationService.create_notification(
            user_id=str(self.user.id),
            notification_type='urgent',
            content='Important update',
            priority='high'
        )
        
        self.assertIsNotNone(notification)
        self.assertEqual(notification.priority, 'high')
    
    def test_get_user_notifications(self):
        """Test retrieving user notifications"""
        # Create some notifications
        NotificationService.create_notification(
            user_id=str(self.user.id),
            notification_type='info',
            content='Notification 1'
        )
        NotificationService.create_notification(
            user_id=str(self.user.id),
            notification_type='roadmap',
            content='Notification 2'
        )
        
        notifications = NotificationService.get_user_notifications(str(self.user.id))
        
        self.assertIsInstance(notifications, list)
        self.assertEqual(len(notifications), 2)
        
        for notification in notifications:
            self.assertIn('id', notification)
            self.assertIn('type', notification)
            self.assertIn('content', notification)
            self.assertIn('read', notification)
            self.assertIn('priority', notification)
            self.assertIn('created_at', notification)
    
    def test_get_user_notifications_unread_only(self):
        """Test retrieving only unread notifications"""
        # Create notifications
        notif1 = NotificationService.create_notification(
            user_id=str(self.user.id),
            notification_type='info',
            content='Unread notification'
        )
        
        notif2 = NotificationService.create_notification(
            user_id=str(self.user.id),
            notification_type='roadmap',
            content='Another notification'
        )
        
        # Mark one as read
        NotificationService.mark_as_read(notif1.id, str(self.user.id))
        
        unread_notifications = NotificationService.get_user_notifications(
            str(self.user.id), 
            unread_only=True
        )
        
        self.assertEqual(len(unread_notifications), 1)
        self.assertEqual(unread_notifications[0]['id'], str(notif2.id))
    
    def test_mark_as_read(self):
        """Test marking notification as read"""
        notification = NotificationService.create_notification(
            user_id=str(self.user.id),
            notification_type='info',
            content='Test notification'
        )
        
        self.assertFalse(notification.read)
        
        success = NotificationService.mark_as_read(notification.id, str(self.user.id))
        self.assertTrue(success)
        
        # Refresh from database
        notification.refresh_from_db()
        self.assertTrue(notification.read)
        self.assertIsNotNone(notification.read_at)
    
    def test_mark_as_read_invalid_notification(self):
        """Test marking non-existent notification as read"""
        success = NotificationService.mark_as_read('nonexistent-id', str(self.user.id))
        self.assertFalse(success)
    
    def test_mark_all_as_read(self):
        """Test marking all notifications as read"""
        # Create multiple notifications
        for i in range(3):
            NotificationService.create_notification(
                user_id=str(self.user.id),
                notification_type='info',
                content=f'Notification {i+1}'
            )
        
        # Initially all should be unread
        unread_count = Notification.objects.filter(user=self.user, read=False).count()
        self.assertEqual(unread_count, 3)
        
        # Mark all as read
        updated_count = NotificationService.mark_all_as_read(str(self.user.id))
        self.assertEqual(updated_count, 3)
        
        # Now all should be read
        unread_count = Notification.objects.filter(user=self.user, read=False).count()
        self.assertEqual(unread_count, 0)
    
    def test_cleanup_old_notifications(self):
        """Test cleaning up old notifications"""
        # Create old notifications (30+ days old)
        old_date = datetime.now() - timedelta(days=35)
        
        # Create read old notification
        notif1 = Notification.objects.create(
            user=self.user,
            type='old',
            content='Old notification',
            read=True,
            created_at=old_date,
            read_at=old_date
        )
        
        # Create recent notification
        notif2 = NotificationService.create_notification(
            user_id=str(self.user.id),
            notification_type='recent',
            content='Recent notification'
        )
        
        # Cleanup old notifications
        deleted_count = NotificationService.cleanup_old_notifications(30)
        
        self.assertEqual(deleted_count, 1)
        self.assertFalse(Notification.objects.filter(id=notif1.id).exists())
        self.assertTrue(Notification.objects.filter(id=notif2.id).exists())
    
    def test_cache_functionality_notifications(self):
        """Test caching of notifications"""
        # First call
        notifications1 = NotificationService.get_user_notifications(str(self.user.id))
        
        # Create new notification
        NotificationService.create_notification(
            user_id=str(self.user.id),
            notification_type='cache',
            content='Cache test'
        )
        
        # Second call should reflect new notification
        notifications2 = NotificationService.get_user_notifications(str(self.user.id))
        
        self.assertGreater(len(notifications2), len(notifications1))


class EmailServiceTest(TestCase):
    """Test cases for EmailService"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            id=str(uuid.uuid4()),
            email='email@example.com',
            password='testpass123',
            role='learner'
        )
        
        self.mentor = User.objects.create_user(
            id=str(uuid.uuid4()),
            email='mentor@example.com',
            password='testpass123',
            role='mentor'
        )
    
    @patch('notifications.services.render_to_string')
    def test_send_welcome_email(self, mock_render):
        """Test sending welcome email"""
        mock_render.return_value = '<h1>Welcome!</h1>'
        
        result = EmailService.send_welcome_email(self.user)
        
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        self.assertEqual(email.to, [self.user.email])
        self.assertIn('Welcome to SkillBridge', email.subject)
        self.assertIn('Welcome!', email.body)
    
    @patch('notifications.services.render_to_string')
    def test_send_mentor_match_email(self, mock_render):
        """Test sending mentor match email"""
        mock_render.return_value = '<h1>New Match!</h1>'
        
        # Create a match
        from matches.models import MentorMatch
        match = MentorMatch.objects.create(
            id=str(uuid.uuid4()),
            learner=self.user,
            mentor=self.mentor,
            status='pending'
        )
        
        result = EmailService.send_mentor_match_email(self.user, self.mentor, match)
        
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        self.assertEqual(email.to, [self.mentor.email])
        self.assertIn('Mentorship Request', email.subject)
        self.assertIn('New Match!', email.body)
    
    @patch('notifications.services.render_to_string')
    def test_send_roadmap_completion_email(self, mock_render):
        """Test sending roadmap completion email"""
        mock_render.return_value = '<h1>Congratulations!</h1>'
        
        # Create a roadmap
        from roadmaps.models import Roadmap
        roadmap = Roadmap.objects.create(
            id=str(uuid.uuid4()),
            user=self.user,
            domain='Python',
            modules=[],
            progress=100.0
        )
        
        result = EmailService.send_roadmap_completion_email(self.user, roadmap)
        
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        self.assertEqual(email.to, [self.user.email])
        self.assertIn('Congratulations', email.subject)
        self.assertIn('Python', email.subject)
    
    @patch('notifications.services.render_to_string')
    def test_send_weekly_progress_email(self, mock_render):
        """Test sending weekly progress email"""
        mock_render.return_value = '<h1>Weekly Progress</h1>'
        
        progress_data = {
            'modules_completed': 5,
            'time_spent_hours': 15,
            'learning_streak': 7
        }
        
        result = EmailService.send_weekly_progress_email(self.user, progress_data)
        
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        self.assertEqual(email.to, [self.user.email])
        self.assertIn('Weekly Progress', email.subject)


class CommunicationServiceTest(TestCase):
    """Test cases for CommunicationService"""
    
    def setUp(self):
        """Set up test data"""
        self.users = []
        for i in range(5):
            user = User.objects.create_user(
                id=str(uuid.uuid4()),
                email=f'comm{i}@example.com',
                password='testpass123',
                role='learner'
            )
            self.users.append(user)
    
    def test_send_bulk_notifications(self):
        """Test sending bulk notifications"""
        user_ids = [str(user.id) for user in self.users[:3]]
        
        results = CommunicationService.send_bulk_notifications(
            user_ids=user_ids,
            notification_type='announcement',
            content='Bulk announcement message'
        )
        
        self.assertIsInstance(results, dict)
        self.assertEqual(results['total'], 3)
        self.assertEqual(results['successful'], 3)
        self.assertEqual(results['failed'], 0)
        
        # Verify notifications were created
        for user_id in user_ids:
            notifications = Notification.objects.filter(user_id=user_id)
            self.assertEqual(notifications.count(), 1)
            notification = notifications.first()
            self.assertEqual(notification.type, 'announcement')
            self.assertIn('Bulk announcement', notification.content)
    
    def test_send_bulk_notifications_partial_failure(self):
        """Test bulk notifications with some failures"""
        user_ids = [str(self.users[0].id), 'nonexistent-user-id', str(self.users[1].id)]
        
        results = CommunicationService.send_bulk_notifications(
            user_ids=user_ids,
            notification_type='test',
            content='Test message'
        )
        
        self.assertEqual(results['total'], 3)
        self.assertEqual(results['successful'], 2)
        self.assertEqual(results['failed'], 1)
    
    def test_send_announcement_to_all_users(self):
        """Test sending announcement to all users"""
        # Mark some users as inactive
        self.users[0].is_active = False
        self.users[0].save()
        
        results = CommunicationService.send_announcement_to_all_users(
            title='System Update',
            content='Scheduled maintenance tonight',
            priority='normal'
        )
        
        # Should send to 4 active users
        self.assertEqual(results['total'], 4)
        self.assertEqual(results['successful'], 4)
        
        # Verify all active users received notification
        active_users = [user for user in self.users if user.is_active]
        for user in active_users:
            notifications = Notification.objects.filter(user=user)
            self.assertEqual(notifications.count(), 1)
            notification = notifications.first()
            self.assertEqual(notification.type, 'announcement')
            self.assertIn('System Update', notification.content)
            self.assertEqual(notification.priority, 'normal')
    
    def test_get_communication_stats(self):
        """Test getting communication statistics"""
        # Create some notifications
        for user in self.users[:3]:
            NotificationService.create_notification(
                user_id=str(user.id),
                notification_type='info',
                content='Test notification'
            )
        
        stats = CommunicationService.get_communication_stats(30)
        
        self.assertIsInstance(stats, dict)
        self.assertIn('timeframe_days', stats)
        self.assertIn('total_notifications', stats)
        self.assertIn('unread_notifications', stats)
        self.assertIn('notification_rate', stats)
        self.assertIn('notifications_by_type', stats)
        self.assertIn('emails_sent', stats)
        self.assertIn('generated_at', stats)
        
        # Should have 3 notifications
        self.assertEqual(stats['total_notifications'], 3)
        self.assertEqual(stats['unread_notifications'], 3)
    
    def test_get_communication_stats_no_data(self):
        """Test communication stats with no data"""
        stats = CommunicationService.get_communication_stats(30)
        
        self.assertIsInstance(stats, dict)
        self.assertEqual(stats['total_notifications'], 0)
        self.assertEqual(stats['unread_notifications'], 0)
        self.assertEqual(stats['emails_sent'], 0)


class NotificationIntegrationTest(TestCase):
    """Integration tests for notification system"""
    
    def setUp(self):
        """Set up integration test data"""
        self.user = User.objects.create_user(
            id=str(uuid.uuid4()),
            email='int-notify@example.com',
            password='testpass123',
            role='learner'
        )
        
        self.mentor = User.objects.create_user(
            id=str(uuid.uuid4()),
            email='int-mentor@example.com',
            password='testpass123',
            role='mentor'
        )
    
    def test_complete_notification_workflow(self):
        """Test complete notification workflow"""
        # Create notification for user
        notification = NotificationService.create_notification(
            user_id=str(self.user.id),
            notification_type='roadmap',
            content='Your Python roadmap is ready!',
            action_url='/dashboard/roadmaps/123',
            priority='normal'
        )
        
        # User gets notifications
        notifications = NotificationService.get_user_notifications(str(self.user.id))
        self.assertEqual(len(notifications), 1)
        
        # User reads notification
        success = NotificationService.mark_as_read(notification.id, str(self.user.id))
        self.assertTrue(success)
        
        # Verify it's marked as read
        notifications_after_read = NotificationService.get_user_notifications(
            str(self.user.id), 
            unread_only=True
        )
        self.assertEqual(len(notifications_after_read), 0)
    
    def test_notification_cascade_deletion(self):
        """Test that notification cleanup works properly"""
        # Create multiple notifications
        notifications = []
        for i in range(10):
            notif = NotificationService.create_notification(
                user_id=str(self.user.id),
                notification_type='test',
                content=f'Test notification {i+1}'
            )
            notifications.append(notif)
        
        # Mark some as read
        for i in range(5):
            NotificationService.mark_as_read(notifications[i].id, str(self.user.id))
        
        # Create old read notifications for cleanup
        old_date = datetime.now() - timedelta(days=35)
        for i in range(3):
            old_notif = Notification.objects.create(
                user=self.user,
                type='old',
                content='Old notification',
                read=True,
                created_at=old_date,
                read_at=old_date
            )
        
        # Cleanup old notifications
        deleted_count = NotificationService.cleanup_old_notifications(30)
        self.assertEqual(deleted_count, 3)
        
        # Verify only relevant notifications remain
        remaining_notifications = Notification.objects.filter(user=self.user)
        self.assertEqual(remaining_notifications.count(), 7)  # 5 unread + 2 recent read
        
        # Verify recent read notifications are still there
        for i in range(5):
            self.assertTrue(Notification.objects.filter(id=notifications[i].id).exists())
    
    def test_email_notification_integration(self):
        """Test integration with email notifications"""
        # Create a high-priority notification
        notification = NotificationService.create_notification(
            user_id=str(self.user.id),
            notification_type='urgent',
            content='System maintenance scheduled',
            priority='high'
        )
        
        # Mock email sending
        with patch('notifications.services.EmailService.send_mail') as mock_send:
            mock_send.return_value = 1
            
            # Deliver notification (should trigger email)
            result = NotificationService.deliver_notification(
                notification, 
                channels=['in_app', 'email']
            )
            
            self.assertTrue(result)
    
    def test_performance_with_many_notifications(self):
        """Test performance with many notifications"""
        import time
        
        # Create many notifications
        start_time = time.time()
        for i in range(100):
            NotificationService.create_notification(
                user_id=str(self.user.id),
                notification_type='bulk',
                content=f'Bulk notification {i+1}'
            )
        creation_time = time.time() - start_time
        
        # Test retrieval performance
        start_time = time.time()
        notifications = NotificationService.get_user_notifications(str(self.user.id), limit=50)
        retrieval_time = time.time() - start_time
        
        # Should complete within reasonable time
        self.assertLess(creation_time, 5.0)
        self.assertLess(retrieval_time, 2.0)
        self.assertEqual(len(notifications), 50)
        
        # Test bulk read performance
        start_time = time.time()
        updated_count = NotificationService.mark_all_as_read(str(self.user.id))
        mark_all_time = time.time() - start_time
        
        self.assertLess(mark_all_time, 1.0)
        self.assertEqual(updated_count, 100)

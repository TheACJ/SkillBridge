import json
import uuid
from datetime import datetime, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import connection
from unittest.mock import patch, MagicMock
from rest_framework.test import APITestCase

from .models import ProgressLog
from .services import ProgressService, AnalyticsService
from roadmaps.models import Roadmap
from matches.models import MentorMatch
from forum.models import ForumPost

User = get_user_model()

class ProgressServiceTest(TestCase):
    """Test cases for ProgressService"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            id=str(uuid.uuid4()),
            email='test@example.com',
            password='testpass123',
            role='learner'
        )
        
        self.mentor = User.objects.create_user(
            id=str(uuid.uuid4()),
            email='mentor@example.com',
            password='testpass123',
            role='mentor'
        )
        
        self.roadmap = Roadmap.objects.create(
            id=str(uuid.uuid4()),
            user=self.user,
            domain='Python',
            modules=[
                {'name': 'Basics', 'completed': True, 'estimated_time': 20},
                {'name': 'OOP', 'completed': False, 'estimated_time': 30}
            ],
            progress=50.0
        )
    
    def test_log_progress_event(self):
        """Test logging progress events"""
        details = {'module_name': 'Python Basics', 'duration': 30}
        progress_log = ProgressService.log_progress_event(
            self.user, 'module_completed', details, self.roadmap
        )
        
        self.assertIsNotNone(progress_log)
        self.assertEqual(progress_log.user, self.user)
        self.assertEqual(progress_log.event_type, 'module_completed')
        self.assertEqual(progress_log.roadmap, self.roadmap)
        self.assertEqual(progress_log.details['module_name'], 'Python Basics')
    
    def test_calculate_roadmap_progress(self):
        """Test roadmap progress calculation"""
        # Create some progress logs
        ProgressService.log_progress_event(
            self.user, 'module_completed', {'module': 'Basics'}, self.roadmap
        )
        ProgressService.log_progress_event(
            self.user, 'session_time', {'duration': 3600}, self.roadmap
        )
        
        progress_data = ProgressService.calculate_user_progress(self.user, self.roadmap)
        
        self.assertIsNotNone(progress_data)
        self.assertEqual(progress_data['domain'], 'Python')
        self.assertEqual(progress_data['total_modules'], 2)
        self.assertEqual(progress_data['completed_modules'], 1)
        self.assertIn('completion_percentage', progress_data)
        self.assertIn('milestones', progress_data)
    
    def test_calculate_overall_progress(self):
        """Test overall progress calculation"""
        progress_data = ProgressService.calculate_user_progress(self.user)
        
        self.assertIsNotNone(progress_data)
        self.assertEqual(progress_data['total_roadmaps'], 1)
        self.assertEqual(progress_data['completed_roadmaps'], 0)
        self.assertIsNotNone(progress_data['roadmap_breakdown'])
    
    def test_cache_functionality(self):
        """Test caching of progress data"""
        # First call should hit database
        ProgressService.calculate_user_progress(self.user, self.roadmap)
        
        # Second call should use cache
        progress_data_cached = ProgressService.calculate_user_progress(self.user, self.roadmap)
        
        self.assertIsNotNone(progress_data_cached)
    
    def test_estimate_time_spent(self):
        """Test time estimation from progress logs"""
        # Log some module completions
        for i in range(3):
            ProgressService.log_progress_event(
                self.user, 'module_completed', {'module': f'Module {i}'}, self.roadmap
            )
        
        progress_logs = ProgressLog.objects.filter(user=self.user)
        time_spent = ProgressService._estimate_time_spent(progress_logs)
        
        self.assertGreater(time_spent, 0)
    
    def test_milestone_calculation(self):
        """Test milestone achievement calculation"""
        progress_logs = ProgressLog.objects.filter(user=self.user, roadmap=self.roadmap)
        milestones = ProgressService._calculate_milestones(progress_logs, 1, 4)
        
        self.assertIsInstance(milestones, list)
        for milestone in milestones:
            self.assertIn('percentage', milestone)
            self.assertIn('achieved', milestone)
    
    def test_learning_velocity(self):
        """Test learning velocity calculation"""
        # Create recent progress logs
        for i in range(3):
            ProgressService.log_progress_event(
                self.user, 'module_completed', {'module': f'Module {i}'}, self.roadmap
            )
        
        progress_logs = ProgressLog.objects.filter(user=self.user, roadmap=self.roadmap)
        velocity = ProgressService._calculate_velocity(progress_logs)
        
        self.assertIsInstance(velocity, float)
        self.assertGreaterEqual(velocity, 0)
    
    def test_cache_clearing(self):
        """Test cache clearing functionality"""
        # Generate progress data to populate cache
        ProgressService.calculate_user_progress(self.user, self.roadmap)
        
        # Clear cache
        ProgressService._clear_progress_cache(self.user.id)
        
        # Verify cache is cleared (this would need more sophisticated testing)


class AnalyticsServiceTest(TestCase):
    """Test cases for AnalyticsService"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            id=str(uuid.uuid4()),
            email='analytics@example.com',
            password='testpass123',
            role='learner'
        )
        
        self.roadmap = Roadmap.objects.create(
            id=str(uuid.uuid4()),
            user=self.user,
            domain='JavaScript',
            modules=[
                {'name': 'Basics', 'completed': True, 'estimated_time': 20},
                {'name': 'DOM', 'completed': False, 'estimated_time': 25}
            ],
            progress=50.0
        )
        
        # Create progress logs over time
        for i in range(7):  # Last 7 days
            date = datetime.now() - timedelta(days=i)
            ProgressService.log_progress_event(
                self.user, 'module_completed', {'module': 'JavaScript Basics'}, self.roadmap
            )
    
    def test_get_learning_analytics(self):
        """Test comprehensive learning analytics"""
        analytics = AnalyticsService.get_learning_analytics(self.user, 30)
        
        self.assertIsInstance(analytics, dict)
        self.assertIn('timeframe_days', analytics)
        self.assertIn('total_activities', analytics)
        self.assertIn('learning_streak', analytics)
        self.assertIn('daily_activity', analytics)
        self.assertIn('productivity_metrics', analytics)
        self.assertIn('recommendations', analytics)
    
    def test_learning_streak_calculation(self):
        """Test learning streak calculation"""
        streak = AnalyticsService._calculate_learning_streak(self.user)
        
        self.assertIsInstance(streak, int)
        self.assertGreaterEqual(streak, 0)
    
    def test_daily_activity_breakdown(self):
        """Test daily activity analysis"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        progress_logs = ProgressLog.objects.filter(
            user=self.user,
            timestamp__range=[start_date, end_date]
        )
        
        daily_activity = AnalyticsService._get_daily_activity(progress_logs, start_date, end_date)
        
        self.assertIsInstance(daily_activity, list)
        for day in daily_activity:
            self.assertIn('date', day)
            self.assertIn('activities', day)
    
    def test_skill_progress_tracking(self):
        """Test skill progress by domain"""
        skill_progress = AnalyticsService._get_skill_progress(self.user)
        
        self.assertIsInstance(skill_progress, list)
        if skill_progress:
            progress = skill_progress[0]
            self.assertIn('domain', progress)
            self.assertIn('completion_percentage', progress)
            self.assertIn('time_spent_hours', progress)
    
    def test_time_distribution_analysis(self):
        """Test time distribution across activity types"""
        progress_logs = ProgressLog.objects.filter(user=self.user)
        time_dist = AnalyticsService._get_time_distribution(progress_logs)
        
        self.assertIsInstance(time_dist, dict)
        total_activities = sum(dist['count'] for dist in time_dist.values())
        self.assertGreater(total_activities, 0)
    
    def test_productivity_metrics(self):
        """Test productivity metrics calculation"""
        progress_logs = ProgressLog.objects.filter(user=self.user)
        metrics = AnalyticsService._get_productivity_metrics(progress_logs)
        
        self.assertIsInstance(metrics, dict)
        self.assertIn('sessions_per_week', metrics)
        self.assertIn('module_completion_rate', metrics)
    
    def test_learning_recommendations(self):
        """Test personalized learning recommendations"""
        progress_logs = ProgressLog.objects.filter(user=self.user)
        recommendations = AnalyticsService._generate_learning_recommendations(self.user, progress_logs)
        
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        self.assertIsInstance(recommendations[0], str)
    
    def test_cache_functionality_analytics(self):
        """Test caching for analytics data"""
        # First call
        analytics1 = AnalyticsService.get_learning_analytics(self.user)
        
        # Second call should use cache
        analytics2 = AnalyticsService.get_learning_analytics(self.user)
        
        self.assertEqual(analytics1, analytics2)
    
    def test_analytics_with_no_data(self):
        """Test analytics when user has no activity"""
        new_user = User.objects.create_user(
            id=str(uuid.uuid4()),
            email='nodata@example.com',
            password='testpass123'
        )
        
        analytics = AnalyticsService.get_learning_analytics(new_user)
        
        self.assertIsInstance(analytics, dict)
        self.assertEqual(analytics['total_activities'], 0)


class ProgressIntegrationTest(TestCase):
    """Integration tests for progress system"""
    
    def setUp(self):
        """Set up integration test data"""
        self.user = User.objects.create_user(
            id=str(uuid.uuid4()),
            email='integration@example.com',
            password='testpass123'
        )
        
        self.mentor = User.objects.create_user(
            id=str(uuid.uuid4()),
            email='mentor-integration@example.com',
            password='testpass123',
            role='mentor'
        )
    
    def test_complete_learning_journey(self):
        """Test a complete learning journey flow"""
        # Create roadmap
        roadmap = Roadmap.objects.create(
            id=str(uuid.uuid4()),
            user=self.user,
            domain='Python',
            modules=[
                {'name': 'Basics', 'completed': False, 'estimated_time': 20},
                {'name': 'OOP', 'completed': False, 'estimated_time': 25}
            ],
            progress=0.0
        )
        
        # Simulate learning journey
        ProgressService.log_progress_event(
            self.user, 'roadmap_started', {'roadmap': 'Python Basics'}, roadmap
        )
        
        ProgressService.log_progress_event(
            self.user, 'module_started', {'module': 'Basics'}, roadmap
        )
        
        ProgressService.log_progress_event(
            self.user, 'session_time', {'duration': 1800}, roadmap  # 30 minutes
        )
        
        ProgressService.log_progress_event(
            self.user, 'module_completed', {'module': 'Basics'}, roadmap
        )
        
        # Update roadmap progress
        roadmap.progress = 50.0
        roadmap.save()
        
        # Get analytics
        analytics = AnalyticsService.get_learning_analytics(self.user)
        
        # Verify journey tracking
        self.assertGreater(analytics['total_activities'], 0)
        self.assertIsNotNone(analytics['learning_streak'])
        
        # Get progress data
        progress_data = ProgressService.calculate_user_progress(self.user, roadmap)
        
        self.assertEqual(progress_data['completed_modules'], 1)
        self.assertEqual(progress_data['total_modules'], 2)
    
    def test_cross_roadmap_analytics(self):
        """Test analytics across multiple roadmaps"""
        # Create multiple roadmaps
        python_roadmap = Roadmap.objects.create(
            id=str(uuid.uuid4()),
            user=self.user,
            domain='Python',
            modules=[{'name': 'Basics', 'completed': True}],
            progress=100.0
        )
        
        js_roadmap = Roadmap.objects.create(
            id=str(uuid.uuid4()),
            user=self.user,
            domain='JavaScript',
            modules=[{'name': 'Basics', 'completed': False}],
            progress=50.0
        )
        
        # Create progress logs
        ProgressService.log_progress_event(
            self.user, 'roadmap_completed', {'roadmap': 'Python'}, python_roadmap
        )
        
        ProgressService.log_progress_event(
            self.user, 'module_completed', {'module': 'JS Basics'}, js_roadmap
        )
        
        # Get overall analytics
        overall_progress = ProgressService.calculate_user_progress(self.user)
        analytics = AnalyticsService.get_learning_analytics(self.user)
        
        # Verify cross-roadmap tracking
        self.assertEqual(overall_progress['total_roadmaps'], 2)
        self.assertEqual(overall_progress['completed_roadmaps'], 1)
        self.assertEqual(len(analytics['skill_progress']), 2)
    
    def test_performance_with_large_dataset(self):
        """Test performance with larger datasets"""
        # Create larger dataset
        roadmaps = []
        for i in range(10):
            roadmap = Roadmap.objects.create(
                id=str(uuid.uuid4()),
                user=self.user,
                domain=f'Domain {i}',
                modules=[{'name': f'Module {j}', 'completed': j % 2 == 0} for j in range(5)],
                progress=i * 10
            )
            roadmaps.append(roadmap)
            
            # Create progress logs
            for j in range(5):
                ProgressService.log_progress_event(
                    self.user, 'module_completed', {'module': f'Module {j}', 'roadmap': f'Domain {i}'},
                    roadmap
                )
        
        # Test analytics performance
        import time
        start_time = time.time()
        analytics = AnalyticsService.get_learning_analytics(self.user, 30)
        end_time = time.time()
        
        # Should complete within reasonable time (adjust threshold as needed)
        self.assertLess(end_time - start_time, 5.0)
        self.assertIsInstance(analytics, dict)
        self.assertGreater(analytics['total_activities'], 0)

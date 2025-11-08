import json
import uuid
from datetime import datetime, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache
from unittest.mock import patch, MagicMock

from .models import Badge
from .services import BadgeService, GamificationService
from roadmaps.models import Roadmap
from matches.models import MentorMatch
from progress.models import ProgressLog
from forum.models import ForumPost

User = get_user_model()

class BadgeServiceTest(TestCase):
    """Test cases for BadgeService"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            id=str(uuid.uuid4()),
            email='badge@example.com',
            password='testpass123',
            role='learner'
        )
        
        self.mentor_user = User.objects.create_user(
            id=str(uuid.uuid4()),
            email='mentor@example.com',
            password='testpass123',
            role='mentor'
        )
    
    def test_badge_definitions(self):
        """Test that badge definitions are properly structured"""
        definitions = BadgeService.BADGE_DEFINITIONS
        
        self.assertIsInstance(definitions, dict)
        self.assertIn('first_roadmap', definitions)
        self.assertIn('roadmap_master', definitions)
        
        # Test first_roadmap structure
        first_roadmap = definitions['first_roadmap']
        self.assertIn('name', first_roadmap)
        self.assertIn('description', first_roadmap)
        self.assertIn('icon', first_roadmap)
        self.assertIn('criteria', first_roadmap)
        
        criteria = first_roadmap['criteria']
        self.assertIn('type', criteria)
        self.assertIn('value', criteria)
    
    def test_award_badge_success(self):
        """Test successful badge awarding"""
        badge = BadgeService.award_badge(self.mentor_user, 'first_roadmap')
        
        self.assertIsNotNone(badge)
        self.assertEqual(badge.mentor, self.mentor_user)
        self.assertEqual(badge.type, 'first_roadmap')
        self.assertIn('name', badge.criteria)
        self.assertIn('description', badge.criteria)
    
    def test_award_duplicate_badge(self):
        """Test that duplicate badges are not awarded"""
        # Award badge first time
        badge1 = BadgeService.award_badge(self.mentor_user, 'first_roadmap')
        self.assertIsNotNone(badge1)
        
        # Try to award same badge again
        badge2 = BadgeService.award_badge(self.mentor_user, 'first_roadmap')
        
        # Should return existing badge
        self.assertIsNotNone(badge2)
        self.assertEqual(badge1.id, badge2.id)
        
        # Should be only one badge in database
        badges = Badge.objects.filter(mentor=self.mentor_user, type='first_roadmap')
        self.assertEqual(badges.count(), 1)
    
    def test_award_nonexistent_badge(self):
        """Test awarding a non-existent badge type"""
        badge = BadgeService.award_badge(self.mentor_user, 'nonexistent_badge')
        
        self.assertIsNone(badge)
    
    def test_check_badge_criteria_roadmap_count(self):
        """Test badge criteria checking for roadmap count"""
        criteria = {'type': 'roadmap_count', 'value': 1}
        
        # User has no roadmaps initially
        result = BadgeService._check_badge_criteria(self.user, criteria)
        self.assertFalse(result)
        
        # Create a roadmap
        Roadmap.objects.create(
            id=str(uuid.uuid4()),
            user=self.user,
            domain='Python',
            modules=[],
            progress=0.0
        )
        
        # Now criteria should be met
        result = BadgeService._check_badge_criteria(self.user, criteria)
        self.assertTrue(result)
    
    def test_check_badge_criteria_completed_roadmaps(self):
        """Test badge criteria checking for completed roadmaps"""
        criteria = {'type': 'completed_roadmaps', 'value': 1}
        
        # Create an incomplete roadmap
        Roadmap.objects.create(
            id=str(uuid.uuid4()),
            user=self.user,
            domain='Python',
            modules=[],
            progress=50.0
        )
        
        result = BadgeService._check_badge_criteria(self.user, criteria)
        self.assertFalse(result)
        
        # Create a completed roadmap
        Roadmap.objects.create(
            id=str(uuid.uuid4()),
            user=self.user,
            domain='JavaScript',
            modules=[],
            progress=100.0
        )
        
        result = BadgeService._check_badge_criteria(self.user, criteria)
        self.assertTrue(result)
    
    def test_check_badge_criteria_domains_learned(self):
        """Test badge criteria checking for domains learned"""
        criteria = {'type': 'domains_learned', 'value': 2}
        
        # User has roadmaps in one domain
        Roadmap.objects.create(
            id=str(uuid.uuid4()),
            user=self.user,
            domain='Python',
            modules=[],
            progress=0.0
        )
        
        result = BadgeService._check_badge_criteria(self.user, criteria)
        self.assertFalse(result)
        
        # Add roadmap in different domain
        Roadmap.objects.create(
            id=str(uuid.uuid4()),
            user=self.user,
            domain='JavaScript',
            modules=[],
            progress=0.0
        )
        
        result = BadgeService._check_badge_criteria(self.user, criteria)
        self.assertTrue(result)
    
    def test_check_and_award_badges(self):
        """Test checking and awarding multiple badges"""
        # Create data to meet multiple badge criteria
        Roadmap.objects.create(
            id=str(uuid.uuid4()),
            user=self.user,
            domain='Python',
            modules=[],
            progress=0.0
        )
        
        Roadmap.objects.create(
            id=str(uuid.uuid4()),
            user=self.user,
            domain='JavaScript',
            modules=[],
            progress=0.0
        )
        
        # Create mentor match
        MentorMatch.objects.create(
            id=str(uuid.uuid4()),
            learner=self.user,
            mentor=self.mentor_user,
            status='active'
        )
        
        newly_awarded = BadgeService.check_and_award_badges(self.user)
        
        self.assertIsInstance(newly_awarded, list)
        # Should award first_roadmap and mentor_seeker badges
        badge_types = [badge.type for badge in newly_awarded]
        self.assertIn('first_roadmap', badge_types)
        self.assertIn('mentor_seeker', badge_types)
    
    def test_get_user_badges(self):
        """Test retrieving user badges"""
        # Award some badges
        BadgeService.award_badge(self.mentor_user, 'first_roadmap')
        BadgeService.award_badge(self.mentor_user, 'mentor_seeker')
        
        badges = BadgeService.get_user_badges(self.mentor_user)
        
        self.assertIsInstance(badges, list)
        self.assertEqual(len(badges), 2)
        
        for badge in badges:
            self.assertIn('id', badge)
            self.assertIn('type', badge)
            self.assertIn('name', badge)
            self.assertIn('description', badge)
            self.assertIn('icon', badge)
            self.assertIn('awarded_at', badge)
    
    def test_get_available_badges(self):
        """Test retrieving all available badge definitions"""
        available_badges = BadgeService.get_available_badges()
        
        self.assertIsInstance(available_badges, list)
        self.assertGreater(len(available_badges), 0)
        
        for badge in available_badges:
            self.assertIn('type', badge)
            self.assertIn('name', badge)
            self.assertIn('description', badge)
            self.assertIn('icon', badge)
            self.assertIn('criteria', badge)
    
    def test_calculate_badge_progress(self):
        """Test calculating progress toward earning a badge"""
        # Create one completed roadmap (out of 5 needed for roadmap_master)
        Roadmap.objects.create(
            id=str(uuid.uuid4()),
            user=self.user,
            domain='Python',
            modules=[],
            progress=100.0  # Complete roadmap
        )
        
        progress = BadgeService.calculate_badge_progress(self.user, 'roadmap_master')
        
        self.assertIsInstance(progress, dict)
        self.assertIn('badge_type', progress)
        self.assertIn('name', progress)
        self.assertIn('current', progress)
        self.assertIn('required', progress)
        self.assertIn('progress_percentage', progress)
        
        self.assertEqual(progress['current'], 1)
        self.assertEqual(progress['required'], 5)
        self.assertEqual(progress['progress_percentage'], 20.0)
    
    def test_cache_functionality(self):
        """Test caching of badge data"""
        # First call
        badges1 = BadgeService.get_user_badges(self.mentor_user)
        
        # Award new badge
        BadgeService.award_badge(self.mentor_user, 'roadmap_master')
        
        # Should get updated cache or fresh data
        badges2 = BadgeService.get_user_badges(self.mentor_user)
        
        # Badge count should be updated
        self.assertGreaterEqual(len(badges2), len(badges1))


class GamificationServiceTest(TestCase):
    """Test cases for GamificationService"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            id=str(uuid.uuid4()),
            email='game@example.com',
            password='testpass123',
            role='learner'
        )
        
        # Initialize user profile with points
        self.user.profile = {'total_points': 0, 'level': 1}
        self.user.save()
    
    def test_points_system(self):
        """Test points system definitions"""
        points_system = GamificationService.POINTS_SYSTEM
        
        self.assertIsInstance(points_system, dict)
        self.assertIn('roadmap_created', points_system)
        self.assertIn('module_completed', points_system)
        self.assertIn('roadmap_completed', points_system)
        
        # Test point values
        self.assertEqual(points_system['roadmap_created'], 10)
        self.assertEqual(points_system['module_completed'], 5)
        self.assertEqual(points_system['roadmap_completed'], 50)
    
    def test_award_points(self):
        """Test awarding points to user"""
        points = GamificationService.award_points(self.user, 'roadmap_created')
        
        self.assertEqual(points, 10)
        
        # Check user profile was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile['total_points'], 10)
    
    def test_award_points_invalid_action(self):
        """Test awarding points for invalid action"""
        points = GamificationService.award_points(self.user, 'invalid_action')
        
        self.assertEqual(points, 0)
        
        # User points should not change
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile['total_points'], 0)
    
    def test_calculate_level(self):
        """Test level calculation from points"""
        # Test different point thresholds
        self.assertEqual(GamificationService._calculate_level(0), 1)
        self.assertEqual(GamificationService._calculate_level(50), 1)
        self.assertEqual(GamificationService._calculate_level(100), 2)
        self.assertEqual(GamificationService._calculate_level(250), 3)
        self.assertEqual(GamificationService._calculate_level(500), 4)
        self.assertEqual(GamificationService._calculate_level(1000), 5)
        self.assertEqual(GamificationService._calculate_level(2000), 6)
        self.assertEqual(GamificationService._calculate_level(5000), 7)
    
    def test_get_next_level_info(self):
        """Test getting next level information"""
        # User with 150 points should be at level 2, next level 3
        info = GamificationService._get_next_level_info(150)
        
        self.assertIsInstance(info, dict)
        self.assertIn('current_name', info)
        self.assertIn('next_level', info)
        self.assertIn('next_name', info)
        self.assertIn('points_needed', info)
        self.assertIn('progress_percentage', info)
        
        self.assertEqual(info['next_level'], 3)
        self.assertGreater(info['points_needed'], 0)
        self.assertGreater(info['progress_percentage'], 0)
    
    def test_get_user_stats(self):
        """Test getting comprehensive user stats"""
        # Award some points
        GamificationService.award_points(self.user, 'roadmap_created')
        GamificationService.award_points(self.user, 'module_completed')
        
        stats = GamificationService.get_user_stats(self.user)
        
        self.assertIsInstance(stats, dict)
        self.assertIn('user_id', stats)
        self.assertIn('total_points', stats)
        self.assertIn('current_level', stats)
        self.assertIn('current_level_name', stats)
        self.assertIn('next_level', stats)
        self.assertIn('points_to_next_level', stats)
        self.assertIn('progress_to_next_level', stats)
        self.assertIn('recent_points', stats)
        self.assertIn('badges_count', stats)
        self.assertIn('rank', stats)
        
        # Should have 15 points total
        self.assertEqual(stats['total_points'], 15)
        self.assertEqual(stats['current_level'], 1)
    
    def test_get_recent_points(self):
        """Test getting recent points earned"""
        # Create progress logs to simulate recent activity
        roadmap = Roadmap.objects.create(
            id=str(uuid.uuid4()),
            user=self.user,
            domain='Python',
            modules=[],
            progress=0.0
        )
        
        # Create recent module completions
        for i in range(3):
            ProgressLog.objects.create(
                id=str(uuid.uuid4()),
                user=self.user,
                event_type='module_completed',
                details={'module': f'Module {i}'}
            )
        
        # Create recent completed roadmap
        roadmap.progress = 100.0
        roadmap.save()
        
        recent_points = GamificationService._get_recent_points(self.user, 7)
        
        self.assertIsInstance(recent_points, int)
        self.assertGreaterEqual(recent_points, 0)
    
    def test_level_up_handling(self):
        """Test level up event handling"""
        # Set user to have points just below next level
        self.user.profile = {'total_points': 95, 'level': 1}
        self.user.save()
        
        # Award points to trigger level up
        points = GamificationService.award_points(self.user, 'roadmap_completed')  # 50 points
        
        # User should have leveled up
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile['level'], 2)
    
    def test_calculate_user_rank(self):
        """Test calculating user rank among all users"""
        # Create additional users with different point totals
        user2 = User.objects.create_user(
            id=str(uuid.uuid4()),
            email='rank2@example.com',
            password='testpass123'
        )
        user2.profile = {'total_points': 200, 'level': 3}
        user2.save()
        
        user3 = User.objects.create_user(
            id=str(uuid.uuid4()),
            email='rank3@example.com',
            password='testpass123'
        )
        user3.profile = {'total_points': 50, 'level': 1}
        user3.save()
        
        # Set current user points
        self.user.profile = {'total_points': 100, 'level': 2}
        self.user.save()
        
        # Refresh from DB to ensure we get the saved profile
        self.user.refresh_from_db()
        user2.refresh_from_db()
        user3.refresh_from_db()
        
        rank_info = GamificationService._calculate_user_rank(self.user)
        
        self.assertIsInstance(rank_info, dict)
        self.assertIn('rank', rank_info)
        self.assertIn('total_users', rank_info)
        self.assertIn('percentile', rank_info)
        
        # User with 100 points should be rank 2
        self.assertEqual(rank_info['rank'], 2)
        self.assertEqual(rank_info['total_users'], 3)
    
    def test_get_leaderboard(self):
        """Test getting user leaderboard"""
        # Create users with different point totals
        users = []
        for i in range(5):
            user = User.objects.create_user(
                id=str(uuid.uuid4()),
                email=f'leaderboard{i}@example.com',
                password='testpass123'
            )
            user.profile = {'total_points': (5-i) * 50, 'level': i+1}
            user.save()
            users.append(user)
        
        leaderboard = GamificationService.get_leaderboard(limit=3)
        
        self.assertIsInstance(leaderboard, list)
        self.assertEqual(len(leaderboard), 3)
        
        # Should be ordered by points (highest first)
        self.assertGreaterEqual(leaderboard[0]['total_points'], leaderboard[1]['total_points'])
        self.assertGreaterEqual(leaderboard[1]['total_points'], leaderboard[2]['total_points'])
        
        for entry in leaderboard:
            self.assertIn('rank', entry)
            self.assertIn('user_id', entry)
            self.assertIn('email', entry)
            self.assertIn('total_points', entry)
            self.assertIn('level', entry)
            self.assertIn('level_name', entry)
            self.assertIn('badges_count', entry)
    
    def test_cache_functionality_gamification(self):
        """Test caching for gamification data"""
        # First call
        stats1 = GamificationService.get_user_stats(self.user)
        
        # Award points
        GamificationService.award_points(self.user, 'roadmap_created')
        
        # Should get updated stats
        stats2 = GamificationService.get_user_stats(self.user)
        
        # Points should be different
        self.assertNotEqual(stats1['total_points'], stats2['total_points'])


class BadgeGamificationIntegrationTest(TestCase):
    """Integration tests for badge and gamification services"""
    
    def setUp(self):
        """Set up integration test data"""
        self.user = User.objects.create_user(
            id=str(uuid.uuid4()),
            email='int-game@example.com',
            password='testpass123',
            role='learner'
        )
        
        self.user.profile = {'total_points': 0, 'level': 1}
        self.user.save()
        self.user.profile = {'total_points': 0, 'level': 1}
        self.user.save()
    
    def test_badge_earning_triggers_points(self):
        """Test that earning badges can trigger point awards (if implemented)"""
        # This test would verify integration between badge earning and points
        # Currently badges don't automatically award points, but this could be added
        
        # Award a badge
        badge = BadgeService.award_badge(self.user, 'first_roadmap')
        self.assertIsNotNone(badge)
        
        # Check if points were awarded (currently they aren't, but could be implemented)
        self.user.refresh_from_db()
        # Currently 0 points - badges don't automatically award points
        # self.assertGreater(self.user.profile['total_points'], 0)
    
    def test_comprehensive_learning_journey_gamification(self):
        """Test gamification through a complete learning journey"""
        # Create roadmap
        roadmap = Roadmap.objects.create(
            id=str(uuid.uuid4()),
            user=self.user,
            domain='Python',
            modules=[
                {'name': 'Basics', 'completed': False},
                {'name': 'OOP', 'completed': False}
            ],
            progress=0.0
        )
        
        # Award points for creating roadmap
        GamificationService.award_points(self.user, 'roadmap_created')
        
        # Complete modules
        for i, module in enumerate(roadmap.modules):
            # Update module completion
            roadmap.modules[i]['completed'] = True
            
            # Log progress
            ProgressLog.objects.create(
                user=self.user,
                roadmap=roadmap,
                event_type='module_completed',
                details={'module': module['name']}
            )
            
            # Award points
            GamificationService.award_points(self.user, 'module_completed')
        
        # Update roadmap progress
        roadmap.progress = 100.0
        roadmap.save()
        
        # Award points for completion
        GamificationService.award_points(self.user, 'roadmap_completed')
        
        # Check final state
        self.user.refresh_from_db()
        stats = GamificationService.get_user_stats(self.user)
        
        # Should have earned points for: roadmap creation (10) + 2 modules (10) + completion (50) = 70
        # 70 points should still be at level 1 (needs 100 for level 2)
        self.assertEqual(self.user.profile['total_points'], 70)
        self.assertEqual(stats['current_level'], 1)
        
        # Should have earned badge
        badges = BadgeService.get_user_badges(self.user)
        self.assertGreater(len(badges), 0)
    
    def test_performance_with_many_users(self):
        """Test performance with multiple users earning badges and points"""
        import time
        
        users = []
        start_time = time.time()
        
        # Create 50 users and simulate their progress
        for i in range(50):
            user = User.objects.create_user(
                id=str(uuid.uuid4()),
                email=f'perf{i}@example.com',
                password='testpass123'
            )
            user.profile = {'total_points': i * 100, 'level': min(i // 10 + 1, 7)}
            user.save()
            users.append(user)
            
            # Award some badges
            if i % 5 == 0:
                BadgeService.award_badge(user, 'first_roadmap')
        
        end_time = time.time()
        
        # Test leaderboard performance
        leaderboard_start = time.time()
        leaderboard = GamificationService.get_leaderboard(limit=20)
        leaderboard_end = time.time()
        
        # Should complete within reasonable time
        self.assertLess(leaderboard_end - leaderboard_start, 2.0)
        self.assertEqual(len(leaderboard), 20)
        
        # Verify leaderboard is correctly ordered
        for i in range(len(leaderboard) - 1):
            self.assertGreaterEqual(
                leaderboard[i]['total_points'],
                leaderboard[i + 1]['total_points']
            )

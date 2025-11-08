import unittest
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.conf import settings
from .youtube import YouTubeIntegration
from .calendly import CalendlyIntegration
from .learning_platforms import (
    CourseraIntegration, UdemyIntegration, FreeCodeCampIntegration,
    LearningPlatformAggregator
)
from .manager import IntegrationManager

class YouTubeIntegrationTest(TestCase):
    """Test YouTube API integration"""
    
    def setUp(self):
        self.integration = YouTubeIntegration()
    
    def test_initialization_without_api_key(self):
        """Test initialization without API key"""
        self.assertIsNotNone(self.integration)
        self.assertIsNone(self.integration.youtube)
    
    def test_search_learning_videos(self):
        """Test video search functionality"""
        videos = self.integration.search_learning_videos('Python', 3)
        
        self.assertIsInstance(videos, list)
        self.assertEqual(len(videos), 3)
        
        # Check video structure
        for video in videos:
            self.assertIn('id', video)
            self.assertIn('title', video)
            self.assertIn('url', video)
            self.assertIn('difficulty', video)
    
    def test_get_learning_playlists(self):
        """Test playlist retrieval"""
        playlists = self.integration.get_learning_playlists('JavaScript', 2)
        
        self.assertIsInstance(playlists, list)
        self.assertEqual(len(playlists), 2)
        
        for playlist in playlists:
            self.assertIn('id', playlist)
            self.assertIn('title', playlist)
            self.assertIn('video_count', playlist)
    
    def test_get_educational_channels(self):
        """Test educational channel search"""
        channels = self.integration.get_educational_channels('Web Development', 2)
        
        self.assertIsInstance(channels, list)
        self.assertEqual(len(channels), 2)
        
        for channel in channels:
            self.assertIn('id', channel)
            self.assertIn('title', channel)
            self.assertIn('subscriber_count', channel)
    
    def test_difficulty_estimation(self):
        """Test video difficulty estimation"""
        # Test beginner content
        difficulty = self.integration._estimate_difficulty(
            'Python Basics for Beginners',
            'Learn Python fundamentals'
        )
        self.assertEqual(difficulty, 'beginner')
        
        # Test advanced content
        difficulty = self.integration._estimate_difficulty(
            'Advanced Python Masterclass',
            'Expert-level techniques'
        )
        self.assertEqual(difficulty, 'advanced')
    
    def test_health_check(self):
        """Test health check functionality"""
        health = self.integration.health_check()
        
        self.assertIn('status', health)
        self.assertIn('message', health)
        self.assertEqual(health['status'], 'unhealthy')  # No API key configured

class CalendlyIntegrationTest(TestCase):
    """Test Calendly API integration"""
    
    def setUp(self):
        self.integration = CalendlyIntegration()
    
    def test_initialization(self):
        """Test initialization"""
        self.assertIsNotNone(self.integration)
        self.assertIsNone(self.integration.api_token)
    
    def test_get_user_info(self):
        """Test user info retrieval"""
        user_info = self.integration.get_user_info()
        
        self.assertIsNotNone(user_info)
        self.assertIn('resource', user_info)
        self.assertIn('name', user_info['resource'])
    
    def test_get_event_types(self):
        """Test event types retrieval"""
        user_info = self.integration.get_user_info()
        if user_info:
            event_types = self.integration.get_event_types(user_info['resource']['uri'])
            self.assertIsInstance(event_types, list)
    
    def test_get_scheduled_events(self):
        """Test scheduled events retrieval"""
        from datetime import datetime
        
        events = self.integration.get_scheduled_events('mock-user', datetime.now())
        self.assertIsInstance(events, list)
        
        for event in events:
            self.assertIn('uri', event)
            self.assertIn('name', event)
            self.assertIn('formatted_start', event)
    
    def test_find_mentor_availability(self):
        """Test mentor availability search"""
        from datetime import datetime
        
        mentors = ['mentor1@example.com', 'mentor2@example.com']
        availability = self.integration.find_mentor_availability(
            mentors, datetime.now(), 60
        )
        
        self.assertIsInstance(availability, dict)
        self.assertIn('mentors', availability)
        self.assertIn('total_available_slots', availability)
        
        self.assertEqual(len(availability['mentors']), 2)
        for mentor in availability['mentors']:
            self.assertIn('email', mentor)
            self.assertIn('available_slots', mentor)
    
    def test_health_check(self):
        """Test health check"""
        health = self.integration.health_check()
        
        self.assertIn('status', health)
        self.assertIn('message', health)
        self.assertEqual(health['status'], 'unhealthy')  # No API key configured

class LearningPlatformIntegrationTest(TestCase):
    """Test learning platform integrations"""
    
    def setUp(self):
        self.coursera = CourseraIntegration()
        self.udemy = UdemyIntegration()
        self.freecodecamp = FreeCodeCampIntegration()
        self.aggregator = LearningPlatformAggregator()
    
    def test_coursera_integration(self):
        """Test Coursera integration"""
        courses = self.coursera.search_courses('Python', 3)
        
        self.assertIsInstance(courses, list)
        self.assertEqual(len(courses), 3)
        
        for course in courses:
            self.assertIn('id', course)
            self.assertIn('title', course)
            self.assertEqual(course['provider'], 'Coursera')
    
    def test_udemy_integration(self):
        """Test Udemy integration"""
        courses = self.udemy.search_courses('JavaScript', 3)
        
        self.assertIsInstance(courses, list)
        self.assertEqual(len(courses), 3)
        
        for course in courses:
            self.assertIn('id', course)
            self.assertIn('title', course)
            self.assertEqual(course['provider'], 'Udemy')
    
    def test_freecodecamp_integration(self):
        """Test FreeCodeCamp integration"""
        curriculum = self.freecodecamp.get_curriculum('front-end')
        
        self.assertIn('type', curriculum)
        self.assertIn('modules', curriculum)
        self.assertEqual(curriculum['type'], 'front-end')
    
    def test_platform_aggregator(self):
        """Test platform aggregator"""
        results = self.aggregator.search_all_platforms('Python', 2)
        
        self.assertIsInstance(results, dict)
        self.assertIn('coursera', results)
        self.assertIn('udemy', results)
        self.assertIn('freecodecamp', results)
        
        for platform, courses in results.items():
            self.assertIsInstance(courses, list)
            self.assertLessEqual(len(courses), 2)
    
    def test_course_recommendations(self):
        """Test course recommendation system"""
        recommendations = self.aggregator.recommend_courses(
            'intermediate', 
            ['Python', 'Web Development']
        )
        
        self.assertIsInstance(recommendations, list)
        
        for rec in recommendations:
            self.assertIn('recommendation_reason', rec)
            self.assertIn('platform', rec)
            self.assertIn('rating', rec)
    
    def test_health_status(self):
        """Test health status for all platforms"""
        status = self.aggregator.get_health_status()
        
        self.assertIn('overall_status', status)
        self.assertIn('platforms', status)
        
        for platform_name, platform_status in status['platforms'].items():
            self.assertIn('status', platform_status)
            self.assertEqual(platform_status['status'], 'unconfigured')

class IntegrationManagerTest(TestCase):
    """Test integration manager"""
    
    def setUp(self):
        self.manager = IntegrationManager()
    
    def test_initialization(self):
        """Test manager initialization"""
        self.assertIsNotNone(self.manager.youtube)
        self.assertIsNotNone(self.manager.calendly)
        self.assertIsNotNone(self.manager.learning_platforms)
    
    def test_health_status(self):
        """Test comprehensive health status"""
        status = self.manager.get_all_health_status()
        
        self.assertIn('timestamp', status)
        self.assertIn('overall_status', status)
        self.assertIn('integrations', status)
        
        expected_integrations = ['openai', 'github', 'youtube', 'calendly', 'learning_platforms']
        for integration in expected_integrations:
            self.assertIn(integration, status['integrations'])
    
    def test_get_learning_resources(self):
        """Test learning resource aggregation"""
        resources = self.manager.get_learning_resources('Python', 'beginner')
        
        self.assertIn('topic', resources)
        self.assertIn('skill_level', resources)
        self.assertIn('videos', resources)
        self.assertIn('courses', resources)
        
        self.assertEqual(resources['topic'], 'Python')
        self.assertEqual(resources['skill_level'], 'beginner')
        self.assertIsInstance(resources['videos'], list)
        self.assertIsInstance(resources['courses'], dict)
    
    def test_get_mentor_availability(self):
        """Test mentor availability retrieval"""
        mentor_emails = ['mentor1@example.com', 'mentor2@example.com']
        availability = self.manager.get_mentor_availability(mentor_emails)
        
        self.assertIn('mentors', availability)
        self.assertIn('total_available_slots', availability)
        self.assertEqual(len(availability['mentors']), 2)
    
    def test_get_roadmap_enrichment(self):
        """Test roadmap enrichment with external resources"""
        domain = 'Python'
        modules = [
            {'name': 'Python Basics', 'description': 'Introduction to Python'},
            {'name': 'Data Structures', 'description': 'Learn Python data structures'}
        ]
        
        enrichment = self.manager.get_roadmap_enrichment(domain, modules)
        
        self.assertIn('domain', enrichment)
        self.assertIn('enriched_modules', enrichment)
        self.assertIn('additional_resources', enrichment)
        
        self.assertEqual(len(enrichment['enriched_modules']), 2)
        for module in enrichment['enriched_modules']:
            self.assertIn('external_resources', module)
    
    def test_create_skill_recommendations(self):
        """Test skill learning recommendations"""
        user_skills = ['HTML', 'CSS']
        target_skills = ['JavaScript', 'React']
        
        recommendations = self.manager.create_skill_recommendations(
            user_skills, target_skills
        )
        
        self.assertIn('learning_path', recommendations)
        self.assertIn('resources', recommendations)
        self.assertIn('estimated_timeline', recommendations)
        
        self.assertEqual(len(recommendations['learning_path']), 2)
        for skill_rec in recommendations['learning_path']:
            self.assertIn('skill', skill_rec)
            self.assertIn('learning_modules', skill_rec)
            self.assertIn('resources', skill_rec)

class IntegrationIntegrationTest(TestCase):
    """Integration tests for the complete integration system"""
    
    def setUp(self):
        self.manager = IntegrationManager()
    
    def test_complete_learning_workflow(self):
        """Test complete learning resource workflow"""
        # Simulate a user wanting to learn web development
        topic = 'Web Development'
        skill_level = 'beginner'
        
        # Get comprehensive resources
        resources = self.manager.get_learning_resources(topic, skill_level)
        
        # Verify all resource types are present
        self.assertIsNotNone(resources['videos'])
        self.assertIsNotNone(resources['courses'])
        
        # Get skill recommendations
        recommendations = self.manager.create_skill_recommendations(
            [],  # No existing skills
            [topic]
        )
        
        self.assertIsNotNone(recommendations['learning_path'])
    
    def test_mentor_scheduling_workflow(self):
        """Test mentor scheduling workflow"""
        # Get mentor availability
        availability = self.manager.get_mentor_availability([
            'mentor1@example.com', 
            'mentor2@example.com'
        ])
        
        # Verify availability structure
        self.assertIn('mentors', availability)
        self.assertIn('total_available_slots', availability)
        self.assertGreater(availability['total_available_slots'], 0)
    
    def test_roadmap_enrichment_workflow(self):
        """Test roadmap enrichment workflow"""
        domain = 'JavaScript'
        current_modules = [
            {
                'name': 'JavaScript Fundamentals',
                'description': 'Learn the basics of JavaScript',
                'estimated_hours': 20
            }
        ]
        
        # Enrich the roadmap
        enrichment = self.manager.get_roadmap_enrichment(domain, current_modules)
        
        # Verify enrichment
        self.assertEqual(len(enrichment['enriched_modules']), 1)
        enriched_module = enrichment['enriched_modules'][0]
        self.assertIn('external_resources', enriched_module)
        self.assertIn('videos', enriched_module['external_resources'])
        self.assertIn('courses', enriched_module['external_resources'])

if __name__ == '__main__':
    unittest.main()
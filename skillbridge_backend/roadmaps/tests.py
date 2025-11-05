import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Roadmap
from .serializers import RoadmapSerializer, RoadmapCreateSerializer
from .services import RoadmapService

User = get_user_model()


class RoadmapModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            role='learner'
        )

    def test_create_roadmap(self):
        roadmap = Roadmap.objects.create(
            user=self.user,
            domain='Python',
            modules=[
                {
                    'name': 'Introduction to Python',
                    'resources': ['https://example.com/resource1'],
                    'estimated_time': 10,
                    'completed': False
                }
            ],
            progress=0.0
        )
        self.assertEqual(roadmap.domain, 'Python')
        self.assertEqual(roadmap.user, self.user)
        self.assertEqual(len(roadmap.modules), 1)

    def test_roadmap_str_method(self):
        roadmap = Roadmap.objects.create(
            user=self.user,
            domain='JavaScript',
            modules=[],
            progress=0.0
        )
        expected_str = f"{self.user.email}'s JavaScript Roadmap"
        self.assertEqual(str(roadmap), expected_str)


class RoadmapServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            role='learner',
            profile={
                'skills': ['python'],
                'learning_goals': ['web development'],
                'experience_level': 'beginner'
            }
        )

    def test_generate_roadmap_ai_mock(self):
        """Test roadmap generation with mock data"""
        roadmap_data = RoadmapService.generate_roadmap_ai(
            domain='Python',
            skill_level='beginner',
            time_availability='part-time',
            user_context=None
        )

        self.assertIn('domain', roadmap_data)
        self.assertIn('modules', roadmap_data)
        self.assertIn('progress', roadmap_data)
        self.assertEqual(roadmap_data['domain'], 'Python')
        self.assertIsInstance(roadmap_data['modules'], list)

    def test_calculate_progress(self):
        """Test progress calculation"""
        roadmap = Roadmap.objects.create(
            user=self.user,
            domain='Python',
            modules=[
                {'completed': True, 'estimated_time': 10},
                {'completed': False, 'estimated_time': 10},
                {'completed': True, 'estimated_time': 10}
            ],
            progress=0.0
        )

        progress = RoadmapService.calculate_progress(roadmap)
        self.assertEqual(progress, 66.67)  # 2 out of 3 completed

    def test_update_module_completion(self):
        """Test module completion update"""
        roadmap = Roadmap.objects.create(
            user=self.user,
            domain='Python',
            modules=[
                {'name': 'Module 1', 'completed': False, 'estimated_time': 10},
                {'name': 'Module 2', 'completed': False, 'estimated_time': 10}
            ],
            progress=0.0
        )

        result = RoadmapService.update_module_completion(roadmap, 0, True)
        self.assertTrue(result)
        roadmap.refresh_from_db()
        self.assertTrue(roadmap.modules[0]['completed'])
        self.assertFalse(roadmap.modules[1]['completed'])


class RoadmapAPITest(APITestCase):
    def setUp(self):
        # Clean up any existing roadmaps to ensure test isolation
        Roadmap.objects.all().delete()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            role='learner'
        )
        self.client.force_authenticate(user=self.user)

    def test_create_roadmap(self):
        data = {
            'domain': 'Python',
            'modules': [
                {
                    'name': 'Introduction',
                    'resources': ['https://example.com'],
                    'estimated_time': 10,
                    'completed': False
                }
            ]
        }
        response = self.client.post('/api/v1/roadmaps/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['domain'], 'Python')

    def test_list_user_roadmaps(self):
        # Create a roadmap
        Roadmap.objects.create(
            user=self.user,
            domain='Python',
            modules=[],
            progress=0.0
        )

        response = self.client.get('/api/v1/roadmaps/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_generate_roadmap_ai(self):
        data = {
            'domain': 'JavaScript',
            'skill_level': 'beginner',
            'time_availability': 'part-time'
        }
        response = self.client.post('/api/v1/roadmaps/generate/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('domain', response.data)
        self.assertIn('modules', response.data)

    def test_update_roadmap_progress(self):
        roadmap = Roadmap.objects.create(
            user=self.user,
            domain='Python',
            modules=[],
            progress=0.0
        )

        data = {'progress': 50.0}
        response = self.client.patch(f'/api/v1/roadmaps/{roadmap.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['progress'], 50.0)

    def test_unauthorized_access(self):
        # Create another user
        other_user = User.objects.create_user(
            email='other@example.com',
            password='testpass123'
        )

        roadmap = Roadmap.objects.create(
            user=other_user,
            domain='Python',
            modules=[],
            progress=0.0
        )

        # Try to access other user's roadmap
        response = self.client.get(f'/api/v1/roadmaps/{roadmap.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

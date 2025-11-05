import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User
from .serializers import UserSerializer, UserRegistrationSerializer, UserLoginSerializer


class UserModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'role': 'learner',
            'profile': {
                'skills': ['python', 'django'],
                'location': 'Nigeria',
                'availability': 10
            }
        }

    def test_create_user(self):
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            role='learner'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.role, 'learner')
        self.assertTrue(user.check_password('testpass123'))

    def test_user_str_method(self):
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(str(user), 'test@example.com')

    def test_user_properties(self):
        learner = User.objects.create_user(email='learner@test.com', password='pass', role='learner')
        mentor = User.objects.create_user(email='mentor@test.com', password='pass', role='mentor')
        admin = User.objects.create_user(email='admin@test.com', password='pass', role='admin')

        self.assertTrue(learner.is_learner)
        self.assertFalse(learner.is_mentor)
        self.assertFalse(learner.is_admin)

        self.assertTrue(mentor.is_mentor)
        self.assertFalse(mentor.is_learner)

        self.assertTrue(admin.is_admin)


class UserSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            role='learner',
            profile={'skills': ['python'], 'location': 'Nigeria'}
        )

    def test_user_serializer(self):
        serializer = UserSerializer(self.user)
        data = serializer.data
        self.assertEqual(data['email'], 'test@example.com')
        self.assertEqual(data['role'], 'learner')
        self.assertIn('skills', data['profile'])

    def test_user_registration_serializer_valid(self):
        data = {
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
            'role': 'mentor'
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_user_registration_serializer_password_mismatch(self):
        data = {
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'password_confirm': 'differentpass',
            'role': 'mentor'
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)


class UserAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            role='learner'
        )

    def test_user_registration_api(self):
        data = {
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
            'role': 'mentor'
        }
        response = self.client.post('/api/v1/users/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)

    def test_user_login_api(self):
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post('/api/v1/users/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])

    def test_get_user_profile_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/users/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_get_user_profile_unauthenticated(self):
        response = self.client.get('/api/v1/users/profile/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

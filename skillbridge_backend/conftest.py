import pytest
from django.test import Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
import factory

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f'user{n}@example.com')
    role = 'learner'
    profile = {
        'skills': ['python'],
        'location': 'Nigeria',
        'availability': 10
    }

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override to handle password setting"""
        password = kwargs.pop('password', 'testpass123')
        obj = super()._create(model_class, *args, **kwargs)
        obj.set_password(password)
        obj.save()
        return obj


@pytest.fixture
def api_client():
    """Return an APIClient instance."""
    return APIClient()


@pytest.fixture
def user():
    """Create and return a test user."""
    return UserFactory(password='testpass123')


@pytest.fixture
def authenticated_client(api_client, user):
    """Return an authenticated APIClient."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def mentor():
    """Create and return a mentor user."""
    return UserFactory(
        role='mentor',
        profile={
            'skills': ['python', 'django'],
            'location': 'Nigeria',
            'availability': 15,
            'expertise': ['web development', 'python'],
            'experience_years': 3,
            'hourly_rate': 50
        }
    )


@pytest.fixture
def learner():
    """Create and return a learner user."""
    return UserFactory(
        role='learner',
        profile={
            'skills': ['javascript'],
            'location': 'Kenya',
            'availability': 8,
            'learning_goals': ['web development', 'react']
        }
    )
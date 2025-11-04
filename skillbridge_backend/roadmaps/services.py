import os
import json
import logging
from typing import Dict, List, Any, Optional
from django.conf import settings
from .models import Roadmap
from users.models import User

logger = logging.getLogger(__name__)

class RoadmapService:
    """Service class for roadmap-related business logic"""

    @staticmethod
    def generate_roadmap_ai(domain: str, skill_level: str = 'beginner',
                           time_availability: str = 'part-time') -> Dict[str, Any]:
        """
        Generate a personalized roadmap using AI (OpenAI integration placeholder)
        In production, this would call OpenAI API
        """
        try:
            # Mock AI response - replace with actual OpenAI integration
            base_modules = {
                'beginner': [
                    {
                        'name': f'Introduction to {domain}',
                        'resources': [
                            f'https://freecodecamp.org/learn/{domain.lower().replace(" ", "-")}',
                            f'https://developer.mozilla.org/en-US/docs/Learn/{domain.replace(" ", "_")}'
                        ],
                        'estimated_time': 20,
                        'completed': False
                    },
                    {
                        'name': f'Basic {domain} Concepts',
                        'resources': [
                            f'https://www.youtube.com/results?search_query={domain.lower()}+tutorial',
                            f'https://github.com/topics/{domain.lower().replace(" ", "")}'
                        ],
                        'estimated_time': 30,
                        'completed': False
                    },
                    {
                        'name': f'Building Your First {domain} Project',
                        'resources': [
                            'https://roadmap.sh/guides',
                            'https://github.com/practical-projects'
                        ],
                        'estimated_time': 40,
                        'completed': False
                    }
                ],
                'intermediate': [
                    {
                        'name': f'Advanced {domain} Patterns',
                        'resources': [
                            f'https://dev.to/t/{domain.lower()}',
                            f'https://stackoverflow.com/questions/tagged/{domain.lower().replace(" ", "-")}'
                        ],
                        'estimated_time': 50,
                        'completed': False
                    },
                    {
                        'name': f'{domain} Best Practices',
                        'resources': [
                            'https://refactoring.guru',
                            'https://martinfowler.com'
                        ],
                        'estimated_time': 35,
                        'completed': False
                    }
                ],
                'advanced': [
                    {
                        'name': f'Expert {domain} Techniques',
                        'resources': [
                            f'https://arxiv.org/search/?query={domain.lower()}',
                            'https://research.google/pubs/'
                        ],
                        'estimated_time': 60,
                        'completed': False
                    }
                ]
            }

            modules = []
            if skill_level == 'beginner':
                modules.extend(base_modules['beginner'])
                if time_availability == 'full-time':
                    modules.extend(base_modules['intermediate'][:1])
            elif skill_level == 'intermediate':
                modules.extend(base_modules['intermediate'])
                modules.extend(base_modules['beginner'][-1:])  # Add project building
            else:  # advanced
                modules.extend(base_modules['advanced'])
                modules.extend(base_modules['intermediate'])

            return {
                'domain': domain,
                'modules': modules,
                'progress': 0,
                'skill_level': skill_level,
                'estimated_completion_weeks': len(modules) * 2
            }

        except Exception as e:
            logger.error(f"Error generating roadmap: {str(e)}")
            raise Exception("Failed to generate roadmap")

    @staticmethod
    def calculate_progress(roadmap: Roadmap) -> float:
        """
        Calculate roadmap progress based on completed modules
        """
        try:
            total_modules = len(roadmap.modules)
            if total_modules == 0:
                return 0.0

            completed_modules = sum(1 for module in roadmap.modules if module.get('completed', False))
            progress = (completed_modules / total_modules) * 100

            return round(progress, 2)

        except Exception as e:
            logger.error(f"Error calculating progress: {str(e)}")
            return 0.0

    @staticmethod
    def update_module_completion(roadmap: Roadmap, module_index: int, completed: bool) -> bool:
        """
        Update completion status of a specific module
        """
        try:
            if 0 <= module_index < len(roadmap.modules):
                roadmap.modules[module_index]['completed'] = completed
                roadmap.progress = RoadmapService.calculate_progress(roadmap)
                roadmap.save()
                return True
            return False

        except Exception as e:
            logger.error(f"Error updating module completion: {str(e)}")
            return False

    @staticmethod
    def get_recommended_resources(domain: str, skill_level: str) -> List[Dict[str, Any]]:
        """
        Get recommended resources for a domain and skill level
        """
        try:
            # Mock resource recommendations - in production, this could be from a database
            resources = {
                'python': {
                    'beginner': [
                        {
                            'title': 'Python for Everybody',
                            'platform': 'Coursera',
                            'url': 'https://www.coursera.org/specializations/python',
                            'difficulty': 'Beginner',
                            'duration': '8 weeks'
                        },
                        {
                            'title': 'Automate the Boring Stuff with Python',
                            'platform': 'Free',
                            'url': 'https://automatetheboringstuff.com',
                            'difficulty': 'Beginner',
                            'duration': 'Self-paced'
                        }
                    ],
                    'intermediate': [
                        {
                            'title': 'Python Data Structures and Algorithms',
                            'platform': 'Udemy',
                            'url': 'https://www.udemy.com/course/python-data-structures-and-algorithms',
                            'difficulty': 'Intermediate',
                            'duration': '20 hours'
                        }
                    ]
                },
                'web-development': {
                    'beginner': [
                        {
                            'title': 'HTML & CSS Full Course',
                            'platform': 'freeCodeCamp',
                            'url': 'https://www.freecodecamp.org/learn/responsive-web-design/',
                            'difficulty': 'Beginner',
                            'duration': '300 hours'
                        }
                    ]
                }
            }

            domain_key = domain.lower().replace(' ', '-')
            return resources.get(domain_key, {}).get(skill_level, [])

        except Exception as e:
            logger.error(f"Error getting recommended resources: {str(e)}")
            return []

    @staticmethod
    def validate_roadmap_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate roadmap data structure
        """
        errors = {}

        if 'domain' not in data or not data['domain'].strip():
            errors['domain'] = 'Domain is required'

        if 'modules' not in data or not isinstance(data['modules'], list):
            errors['modules'] = 'Modules must be a list'
        else:
            for i, module in enumerate(data['modules']):
                if not isinstance(module, dict):
                    errors[f'modules[{i}]'] = 'Each module must be a dictionary'
                    continue

                required_fields = ['name', 'resources', 'estimated_time']
                for field in required_fields:
                    if field not in module:
                        errors[f'modules[{i}].{field}'] = f'{field} is required'

                if 'estimated_time' in module and not isinstance(module['estimated_time'], (int, float)):
                    errors[f'modules[{i}].estimated_time'] = 'estimated_time must be a number'

        if errors:
            raise ValueError(f"Validation errors: {errors}")

        return data
import os
import logging
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib
import json

logger = logging.getLogger(__name__)

class LearningPlatformIntegration:
    """Base class for learning platform integrations"""
    
    def __init__(self, platform_name: str):
        self.platform_name = platform_name
        self.api_key = os.getenv(f'{platform_name.upper()}_API_KEY')
        self.base_url = os.getenv(f'{platform_name.upper()}_API_URL')
        self.cache_ttl = 3600  # 1 hour cache
        
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the integration"""
        return {
            'platform': self.platform_name,
            'status': 'healthy' if self.api_key else 'unconfigured',
            'message': 'API key configured' if self.api_key else 'API key not configured'
        }

class CourseraIntegration(LearningPlatformIntegration):
    """Coursera API integration"""
    
    def __init__(self):
        super().__init__('coursera')
        self.api_url = 'https://api.coursera.org/api'
    
    def search_courses(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for courses on Coursera"""
        if not self.api_key:
            return self._get_mock_courses(query, limit)
        
        try:
            # Note: Coursera public API is limited, this is a mock implementation
            # In production, you would use their partner API
            return self._get_mock_courses(query, limit)
        except Exception as e:
            logger.error(f"Error searching Coursera courses: {str(e)}")
            return self._get_mock_courses(query, limit)
    
    def get_course_details(self, course_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed course information"""
        if not self.api_key:
            return self._get_mock_course_details(course_id)
        
        try:
            return self._get_mock_course_details(course_id)
        except Exception as e:
            logger.error(f"Error getting course details: {str(e)}")
            return None
    
    def _get_mock_courses(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Generate mock course data"""
        return [
            {
                'id': f'coursera-{i}',
                'title': f'{query} - Course {i+1}',
                'provider': 'Coursera',
                'instructor': f'Instructor {i+1}',
                'rating': 4.5 + (i * 0.1),
                'duration': f'{4 + i} weeks',
                'level': ['Beginner', 'Intermediate', 'Advanced'][i % 3],
                'url': f'https://coursera.org/learn/{query.lower().replace(" ", "-")}-{i}',
                'thumbnail': f'https://via.placeholder.com/300x200?text={query}+Course+{i+1}',
                'description': f'Comprehensive {query} course covering fundamentals to advanced topics',
                'enrollment_count': 10000 + (i * 500),
                'free_trial': True,
                'certification': True
            }
            for i in range(limit)
        ]
    
    def _get_mock_course_details(self, course_id: str) -> Dict[str, Any]:
        """Generate mock course details"""
        return {
            'id': course_id,
            'title': f'Advanced {course_id} Programming',
            'provider': 'Coursera',
            'instructor': 'Dr. Jane Smith',
            'rating': 4.7,
            'duration': '6 weeks',
            'level': 'Intermediate',
            'url': f'https://coursera.org/learn/{course_id}',
            'thumbnail': f'https://via.placeholder.com/600x400?text={course_id}',
            'description': f'Comprehensive {course_id} course with hands-on projects',
            'enrollment_count': 15000,
            'free_trial': True,
            'certification': True,
            'skills': [f'{course_id} Fundamentals', f'{course_id} Advanced', 'Project Development'],
            'modules': [
                {'name': 'Introduction', 'duration': '1 week'},
                {'name': 'Core Concepts', 'duration': '2 weeks'},
                {'name': 'Advanced Topics', 'duration': '2 weeks'},
                {'name': 'Final Project', 'duration': '1 week'}
            ]
        }

class UdemyIntegration(LearningPlatformIntegration):
    """Udemy API integration"""
    
    def __init__(self):
        super().__init__('udemy')
        self.api_url = 'https://www.udemy.com/api-2.0'
    
    def search_courses(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for courses on Udemy"""
        if not self.api_key:
            return self._get_mock_courses(query, limit)
        
        try:
            headers = {'Authorization': f'Bearer {self.api_key}'}
            params = {
                'search': query,
                'page_size': limit
            }
            
            response = requests.get(
                f"{self.api_url}/courses/",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._process_udemy_courses(data.get('results', []))
            else:
                return self._get_mock_courses(query, limit)
                
        except Exception as e:
            logger.error(f"Error searching Udemy courses: {str(e)}")
            return self._get_mock_courses(query, limit)
    
    def _process_udemy_courses(self, courses: List[Dict]) -> List[Dict[str, Any]]:
        """Process Udemy API response"""
        processed = []
        for course in courses:
            processed.append({
                'id': course.get('id'),
                'title': course.get('title'),
                'provider': 'Udemy',
                'instructor': course.get('visible_instructors', [{}])[0].get('display_name', 'Unknown'),
                'rating': course.get('rating', 0),
                'duration': f"{course.get('content_length_minutes', 0) // 60} hours",
                'level': course.get('instructional_level', 'All Levels'),
                'url': f"https://www.udemy.com{course.get('url', '')}",
                'thumbnail': course.get('image_480x270', ''),
                'description': course.get('headline', ''),
                'enrollment_count': course.get('num_published_lectures', 0),
                'price': course.get('price', 'Free'),
                'discount_price': course.get('discount_price', {}).get('amount', 'Free'),
                'bestseller': course.get('bestseller_badge_content') is not None
            })
        return processed
    
    def _get_mock_courses(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Generate mock course data"""
        return [
            {
                'id': f'udemy-{i}',
                'title': f'{query} Bootcamp {i+1}',
                'provider': 'Udemy',
                'instructor': f'Expert Instructor {i+1}',
                'rating': 4.3 + (i * 0.15),
                'duration': f'{8 + i * 2} hours',
                'level': ['Beginner', 'Intermediate', 'Advanced'][i % 3],
                'url': f'https://udemy.com/course/{query.lower()}-course-{i}/',
                'thumbnail': f'https://via.placeholder.com/480x270?text={query}+Udemy+{i+1}',
                'description': f'Master {query} with this comprehensive bootcamp course',
                'enrollment_count': 2500 + (i * 200),
                'price': '$49.99',
                'discount_price': '$19.99' if i % 2 == 0 else None,
                'bestseller': i == 0
            }
            for i in range(limit)
        ]

class FreeCodeCampIntegration(LearningPlatformIntegration):
    """FreeCodeCamp API integration (mock implementation)"""
    
    def __init__(self):
        super().__init__('freecodecamp')
        self.api_url = 'https://api.freecodecamp.org'
    
    def search_courses(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for FreeCodeCamp curriculum (mock implementation)"""
        if not self.api_key:
            return self._get_mock_courses(query, limit)
        
        try:
            return self._get_mock_courses(query, limit)
        except Exception as e:
            logger.error(f"Error searching FreeCodeCamp: {str(e)}")
            return self._get_mock_courses(query, limit)
    
    def get_curriculum(self, curriculum_type: str = 'full-stack') -> Dict[str, Any]:
        """Get FreeCodeCamp curriculum information"""
        if not self.api_key:
            return self._get_mock_curriculum(curriculum_type)
        
        try:
            # FreeCodeCamp doesn't have a public API, so we return mock data
            return self._get_mock_curriculum(curriculum_type)
        except Exception as e:
            logger.error(f"Error getting FreeCodeCamp curriculum: {str(e)}")
            return self._get_mock_curriculum(curriculum_type)
    
    def _get_mock_curriculum(self, curriculum_type: str) -> Dict[str, Any]:
        """Generate mock curriculum data"""
        return {
            'type': curriculum_type,
            'certification': f'{curriculum_type.title()} Development Certification',
            'estimated_time': '300 hours',
            'difficulty': 'Beginner to Advanced',
            'url': f'https://freecodecamp.org/learn/{curriculum_type}/',
            'modules': [
                {
                    'title': 'HTML and CSS',
                    'description': 'Learn the building blocks of web development',
                    'challenges': 35,
                    'estimated_time': '25 hours'
                },
                {
                    'title': 'JavaScript Algorithms',
                    'description': 'Master JavaScript programming fundamentals',
                    'challenges': 50,
                    'estimated_time': '50 hours'
                },
                {
                    'title': 'Frontend Libraries',
                    'description': 'Build interactive web applications',
                    'challenges': 30,
                    'estimated_time': '75 hours'
                },
                {
                    'title': 'Data Visualization',
                    'description': 'Create data visualizations with D3.js',
                    'challenges': 15,
                    'estimated_time': '50 hours'
                },
                {
                    'title': 'APIs and Microservices',
                    'description': 'Build RESTful APIs and microservices',
                    'challenges': 20,
                    'estimated_time': '50 hours'
                },
                {
                    'title': 'Quality Assurance',
                    'description': 'Test and debug code effectively',
                    'challenges': 20,
                    'estimated_time': '50 hours'
                }
            ]
        }
    
    def _get_mock_courses(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Generate mock FreeCodeCamp course data"""
        return [
            {
                'id': f'freecodecamp-{i}',
                'title': f'{query} - FreeCodeCamp Course {i+1}',
                'provider': 'FreeCodeCamp',
                'instructor': 'FreeCodeCamp Community',
                'rating': 4.6 + (i * 0.05),
                'duration': f'{50 + i * 10} hours',
                'level': 'Beginner to Intermediate',
                'url': f'https://freecodecamp.org/learn/{query.lower().replace(" ", "")}/',
                'thumbnail': f'https://via.placeholder.com/480x270?text={query}+FCC+{i+1}',
                'description': f'Free comprehensive {query} course with hands-on projects',
                'enrollment_count': 5000 + (i * 500),
                'free': True,
                'certification': True,
                'interactive': True
            }
            for i in range(limit)
        ]

class LearningPlatformAggregator:
    """Aggregate multiple learning platform integrations"""
    
    def __init__(self):
        self.integrations = {
            'coursera': CourseraIntegration(),
            'udemy': UdemyIntegration(),
            'freecodecamp': FreeCodeCampIntegration(),
        }
    
    def search_all_platforms(self, query: str, limit_per_platform: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """Search across all learning platforms"""
        results = {}
        
        for platform_name, integration in self.integrations.items():
            try:
                courses = integration.search_courses(query, limit_per_platform)
                results[platform_name] = courses
            except Exception as e:
                logger.error(f"Error searching {platform_name}: {str(e)}")
                results[platform_name] = []
        
        return results
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of all integrations"""
        status = {
            'overall_status': 'healthy',
            'platforms': {}
        }
        
        for platform_name, integration in self.integrations.items():
            platform_status = integration.get_health_status()
            status['platforms'][platform_name] = platform_status
            
            if platform_status['status'] == 'unconfigured':
                status['overall_status'] = 'degraded'
        
        return status
    
    def recommend_courses(self, skill_level: str, interests: List[str]) -> List[Dict[str, Any]]:
        """Get course recommendations based on skill level and interests"""
        recommendations = []
        
        for interest in interests:
            platform_results = self.search_all_platforms(interest, 3)
            
            for platform, courses in platform_results.items():
                for course in courses:
                    # Filter by skill level if possible
                    if skill_level.lower() in course.get('level', '').lower() or course.get('level', '') == 'All Levels':
                        course['recommendation_reason'] = f'Matches your interest in {interest}'
                        course['platform'] = platform
                        recommendations.append(course)
        
        # Sort by rating and return top recommendations
        recommendations.sort(key=lambda x: x.get('rating', 0), reverse=True)
        return recommendations[:10]

# Global instance
learning_platforms = LearningPlatformAggregator()
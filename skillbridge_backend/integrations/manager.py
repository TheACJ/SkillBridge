import logging
from typing import Dict, List, Any, Optional
from .youtube import YouTubeIntegration
from .calendly import CalendlyIntegration
from .learning_platforms import LearningPlatformAggregator

logger = logging.getLogger(__name__)

class IntegrationManager:
    """Unified manager for all external service integrations"""
    
    def __init__(self):
        self.youtube = YouTubeIntegration()
        self.calendly = CalendlyIntegration()
        self.learning_platforms = LearningPlatformAggregator()
        
        logger.info("Integration Manager initialized")
    
    def get_all_health_status(self) -> Dict[str, Any]:
        """Get health status of all integrations"""
        return {
            'timestamp': '2023-01-01T00:00:00Z',
            'overall_status': 'healthy',
            'integrations': {
                'openai': {
                    'name': 'OpenAI API',
                    'status': 'configured',  # Check settings for actual status
                    'description': 'AI-powered roadmap generation'
                },
                'github': {
                    'name': 'GitHub API',
                    'status': 'configured',  # Check settings for actual status
                    'description': 'Code repository integration'
                },
                'youtube': self.youtube.health_check(),
                'calendly': self.calendly.health_check(),
                'learning_platforms': self.learning_platforms.get_health_status()
            }
        }
    
    def get_learning_resources(self, topic: str, skill_level: str = 'intermediate') -> Dict[str, Any]:
        """
        Get comprehensive learning resources from all platforms
        
        Args:
            topic: Learning topic (e.g., 'Python', 'JavaScript')
            skill_level: 'beginner', 'intermediate', or 'advanced'
            
        Returns:
            Dictionary with learning resources from various platforms
        """
        resources = {
            'topic': topic,
            'skill_level': skill_level,
            'videos': [],
            'courses': {},
            'scheduling': {}
        }
        
        try:
            # Get YouTube videos
            resources['videos'] = self.youtube.search_learning_videos(
                query=f"{topic} tutorial {skill_level}",
                max_results=10
            )
            
            # Get learning platform courses
            resources['courses'] = self.learning_platforms.search_all_platforms(
                query=topic,
                limit_per_platform=5
            )
            
        except Exception as e:
            logger.error(f"Error getting learning resources: {str(e)}")
        
        return resources
    
    def get_mentor_availability(self, mentor_emails: List[str]) -> Dict[str, Any]:
        """
        Get availability for mentors using Calendly integration
        
        Args:
            mentor_emails: List of mentor email addresses
            
        Returns:
            Dictionary with mentor availability information
        """
        availability = {
            'mentors': [],
            'total_available_slots': 0
        }
        
        try:
            # Get user info first
            user_info = self.calendly.get_user_info()
            if user_info:
                # Get event types
                event_types = self.calendly.get_event_types(user_info['resource']['uri'])
                
                # For each mentor email, try to find availability
                mentor_availability = []
                for email in mentor_emails:
                    mentor_data = {
                        'email': email,
                        'available_slots': [],
                        'event_types': event_types
                    }
                    
                    # In a real implementation, you would map emails to Calendly users
                    # For now, we return mock data
                    from datetime import datetime, timedelta
                    from django.utils import timezone
                    base_time = timezone.now().replace(hour=9, minute=0, second=0, microsecond=0)
                    
                    for i in range(5):  # Next 5 available slots
                        slot_time = base_time + timedelta(days=i+1, hours=14)
                        mentor_data['available_slots'].append({
                            'start_time': slot_time.isoformat(),
                            'duration_minutes': 60,
                            'formatted_time': slot_time.strftime('%Y-%m-%d %H:%M')
                        })
                    
                    mentor_availability.append(mentor_data)
                    availability['total_available_slots'] += len(mentor_data['available_slots'])
                
                availability['mentors'] = mentor_availability
                    
        except Exception as e:
            logger.error(f"Error getting mentor availability: {str(e)}")
        
        return availability
    
    def get_roadmap_enrichment(self, domain: str, current_modules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Enrich roadmap modules with external resources
        
        Args:
            domain: Learning domain
            current_modules: Current roadmap modules
            
        Returns:
            Enriched roadmap with additional resources
        """
        enrichment = {
            'domain': domain,
            'enriched_modules': [],
            'additional_resources': {
                'videos': [],
                'courses': []
            }
        }
        
        try:
            # Get additional videos for the domain
            videos = self.youtube.search_learning_videos(
                query=f"{domain} comprehensive tutorial",
                max_results=5
            )
            enrichment['additional_resources']['videos'] = videos
            
            # Get courses from learning platforms
            courses = self.learning_platforms.search_all_platforms(
                query=domain,
                limit_per_platform=3
            )
            enrichment['additional_resources']['courses'] = courses
            
            # Enrich each module
            for module in current_modules:
                module_title = module.get('name', module.get('title', ''))
                
                # Find relevant videos for this module
                module_videos = self.youtube.search_learning_videos(
                    query=f"{module_title} tutorial",
                    max_results=3
                )
                
                # Get courses that match this module
                module_courses = self.learning_platforms.search_all_platforms(
                    query=module_title,
                    limit_per_platform=2
                )
                
                enriched_module = module.copy()
                enriched_module['external_resources'] = {
                    'videos': module_videos,
                    'courses': module_courses
                }
                
                enrichment['enriched_modules'].append(enriched_module)
                
        except Exception as e:
            logger.error(f"Error enriching roadmap: {str(e)}")
        
        return enrichment
    
    def create_skill_recommendations(self, user_skills: List[str], 
                                   target_skills: List[str]) -> Dict[str, Any]:
        """
        Create skill learning recommendations using AI and external resources
        
        Args:
            user_skills: List of skills the user already has
            target_skills: List of skills the user wants to learn
            
        Returns:
            Comprehensive skill learning recommendations
        """
        recommendations = {
            'learning_path': [],
            'resources': {},
            'estimated_timeline': {}
        }
        
        try:
            # For each target skill, find learning path and resources
            for skill in target_skills:
                skill_rec = {
                    'skill': skill,
                    'difficulty': 'intermediate',  # Would be determined by AI
                    'prerequisites': [],  # Would be determined by analysis
                    'learning_modules': [],
                    'resources': {}
                }
                
                # Get videos for this skill
                skill_rec['resources']['videos'] = self.youtube.search_learning_videos(
                    query=f"{skill} complete tutorial",
                    max_results=5
                )
                
                # Get courses for this skill
                skill_rec['resources']['courses'] = self.learning_platforms.search_all_platforms(
                    query=skill,
                    limit_per_platform=3
                )
                
                # Add learning modules
                skill_rec['learning_modules'] = [
                    {
                        'name': f'{skill} Fundamentals',
                        'duration_hours': 20,
                        'resources': skill_rec['resources']['videos'][:2] + skill_rec['resources']['courses'].get('coursera', [])[:1]
                    },
                    {
                        'name': f'{skill} Practice',
                        'duration_hours': 30,
                        'resources': skill_rec['resources']['videos'][2:4] + skill_rec['resources']['courses'].get('udemy', [])[:1]
                    },
                    {
                        'name': f'{skill} Advanced Topics',
                        'duration_hours': 25,
                        'resources': skill_rec['resources']['videos'][4:] + skill_rec['resources']['courses'].get('freecodecamp', [])[:1]
                    }
                ]
                
                recommendations['learning_path'].append(skill_rec)
                
                # Calculate estimated timeline
                total_hours = sum(module['duration_hours'] for module in skill_rec['learning_modules'])
                recommendations['estimated_timeline'][skill] = {
                    'total_hours': total_hours,
                    'weeks_part_time': total_hours // 5,  # 5 hours per week
                    'weeks_full_time': total_hours // 20  # 20 hours per week
                }
                
        except Exception as e:
            logger.error(f"Error creating skill recommendations: {str(e)}")
        
        return recommendations

# Global integration manager instance
integration_manager = IntegrationManager()
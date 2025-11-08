import logging
from django.core.cache import cache
from django.conf import settings
from .integrations import OpenAIIntegration

logger = logging.getLogger(__name__)


class RoadmapService:
    """Service class for roadmap-related business logic with caching"""

    @staticmethod
    def generate_roadmap(domain, skill_level='beginner', time_availability='part-time', user_context=None):
        """
        Generate a personalized roadmap using OpenAI with caching
        """
        return RoadmapService.generate_roadmap_ai(domain, skill_level, time_availability, user_context)

    @staticmethod
    def generate_roadmap_ai(domain, skill_level='beginner', time_availability='part-time', user_context=None):
        """
        Generate a personalized roadmap using OpenAI with caching
        """
        # Create cache key based on parameters
        cache_key = f"roadmap_{domain}_{skill_level}_{time_availability}_{hash(str(user_context))}"
        cached_roadmap = cache.get(cache_key)

        if cached_roadmap:
            logger.info(f"Returning cached roadmap for {domain}")
            return cached_roadmap

        try:
            openai_integration = OpenAIIntegration()
            roadmap_data = openai_integration.generate_roadmap(
                domain=domain,
                skill_level=skill_level,
                time_availability=time_availability,
                user_context=user_context
            )

            # Cache the result for 1 hour
            cache.set(cache_key, roadmap_data, 3600)
            logger.info(f"Generated and cached new roadmap for {domain}")

            return roadmap_data

        except Exception as e:
            logger.error(f"Error generating roadmap: {str(e)}")
            raise Exception("Failed to generate roadmap")

    @staticmethod
    def calculate_progress(roadmap):
        """
        Calculate progress for a roadmap with caching
        """
        cache_key = f"roadmap_progress_{roadmap.id}"
        cached_progress = cache.get(cache_key)

        if cached_progress is not None:
            return cached_progress

        try:
            modules = roadmap.modules or []
            if not modules:
                progress = 0.0
            else:
                completed_modules = sum(1 for module in modules if module.get('completed', False))
                progress = round((completed_modules / len(modules)) * 100, 2)

            # Cache for 5 minutes
            cache.set(cache_key, progress, 300)
            return progress

        except Exception as e:
            logger.error(f"Error calculating progress for roadmap {roadmap.id}: {str(e)}")
            return 0.0

    @staticmethod
    def update_module_completion(roadmap, module_id, completed):
        """
        Update module completion status with cache invalidation
        """
        try:
            modules = roadmap.modules or []
            for i, module in enumerate(modules):
                if str(i) == str(module_id) or module.get('name') == str(module_id):
                    module['completed'] = completed
                    break

            roadmap.modules = modules
            roadmap.save()

            # Invalidate progress cache
            cache_key = f"roadmap_progress_{roadmap.id}"
            cache.delete(cache_key)

            logger.info(f"Updated module {module_id} completion for roadmap {roadmap.id}")
            return True

        except Exception as e:
            logger.error(f"Error updating module completion: {str(e)}")
            return False

    @staticmethod
    def get_recommended_resources(domain, skill_level='beginner'):
        """
        Get recommended resources for a domain with caching
        """
        cache_key = f"resources_{domain}_{skill_level}"
        cached_resources = cache.get(cache_key)

        if cached_resources:
            return cached_resources

        # Mock resource recommendations (would integrate with external APIs)
        resources = [
            {
                'title': f'Official {domain} Documentation',
                'type': 'documentation',
                'platform': 'Official',
                'url': f'https://{domain.lower()}.org/docs',
                'free': True,
                'estimated_time': 'Ongoing'
            },
            {
                'title': f'{domain} for {skill_level.title()}s',
                'type': 'course',
                'platform': 'Coursera',
                'url': f'https://coursera.org/{domain.lower()}',
                'free': False,
                'estimated_time': '8 weeks'
            }
        ]

        # Cache for 24 hours
        cache.set(cache_key, resources, 86400)
        return resources

    @staticmethod
    def invalidate_user_cache(user_id):
        """
        Invalidate all caches related to a user
        """
        cache_keys = [
            f"user_roadmaps_{user_id}",
            f"user_stats_{user_id}",
            f"user_matches_{user_id}"
        ]

        for key in cache_keys:
            cache.delete(key)

        logger.info(f"Invalidated cache for user {user_id}")

    @staticmethod
    def invalidate_roadmap_cache(roadmap_id):
        """
        Invalidate all caches related to a roadmap
        """
        cache_keys = [
            f"roadmap_progress_{roadmap_id}",
            f"roadmap_analytics_{roadmap_id}"
        ]

        for key in cache_keys:
            cache.delete(key)

        logger.info(f"Invalidated cache for roadmap {roadmap_id}")
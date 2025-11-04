import os
import requests
import logging
from typing import Dict, List, Any, Optional, Tuple
from django.conf import settings
from .models import MentorMatch
from users.models import User
from notifications.models import Notification

logger = logging.getLogger(__name__)

class MentorMatchingService:
    """Service class for mentor matching business logic"""

    RUST_SERVICE_URL = os.getenv('RUST_SERVICE_URL', 'http://localhost:8001')

    @staticmethod
    def find_best_matches(learner: User, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find best mentor matches for a learner using the Rust microservice
        """
        try:
            # Prepare learner data
            learner_data = MentorMatchingService._prepare_learner_data(learner)

            # Get available mentors
            mentors = User.objects.filter(role='mentor', is_active=True)
            mentors_data = [MentorMatchingService._prepare_mentor_data(mentor) for mentor in mentors]

            # Call Rust microservice for matching algorithm
            matches = MentorMatchingService._call_rust_matching_service(learner_data, mentors_data, limit)

            # Enrich matches with full mentor data
            enriched_matches = []
            for match in matches:
                mentor = mentors.filter(id=match['mentor_id']).first()
                if mentor:
                    enriched_matches.append({
                        'mentor': mentor,
                        'score': match.get('score', 0),
                        'reasoning': match.get('reasoning', ''),
                        'compatibility_factors': match.get('compatibility_factors', {})
                    })

            return enriched_matches

        except Exception as e:
            logger.error(f"Error finding mentor matches: {str(e)}")
            # Fallback to simple matching
            return MentorMatchingService._fallback_matching(learner, limit)

    @staticmethod
    def _prepare_learner_data(learner: User) -> Dict[str, Any]:
        """Prepare learner data for the matching algorithm"""
        profile = learner.profile or {}

        return {
            'id': str(learner.id),
            'skills': profile.get('skills', []),
            'learning_goals': profile.get('learning_goals', []),
            'location': profile.get('location', ''),
            'availability': profile.get('availability', 10),  # hours per week
            'experience_level': profile.get('experience_level', 'beginner'),
            'preferred_languages': profile.get('preferred_languages', []),
        }

    @staticmethod
    def _prepare_mentor_data(mentor: User) -> Dict[str, Any]:
        """Prepare mentor data for the matching algorithm"""
        profile = mentor.profile or {}

        return {
            'id': str(mentor.id),
            'expertise': profile.get('skills', []),
            'location': profile.get('location', ''),
            'availability': profile.get('availability', 10),
            'experience_years': profile.get('experience_years', 0),
            'rating': profile.get('rating', 0),
            'hourly_rate': profile.get('hourly_rate', 0),
            'teaching_style': profile.get('teaching_style', 'structured'),
        }

    @staticmethod
    def _call_rust_matching_service(learner_data: Dict, mentors_data: List[Dict], limit: int) -> List[Dict]:
        """Call the Rust microservice for mentor matching"""
        try:
            payload = {
                'learner': learner_data,
                'mentors': mentors_data,
                'limit': limit
            }

            response = requests.post(
                f"{MentorMatchingService.RUST_SERVICE_URL}/match",
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                return response.json().get('matches', [])
            else:
                logger.warning(f"Rust service returned {response.status_code}: {response.text}")
                raise Exception("Rust service error")

        except requests.RequestException as e:
            logger.error(f"Failed to call Rust service: {str(e)}")
            raise Exception("Matching service unavailable")

    @staticmethod
    def _fallback_matching(learner: User, limit: int) -> List[Dict[str, Any]]:
        """Fallback matching algorithm when Rust service is unavailable"""
        try:
            learner_skills = set((learner.profile or {}).get('skills', []))
            learner_goals = set((learner.profile or {}).get('learning_goals', []))

            mentors = User.objects.filter(role='mentor', is_active=True)[:limit]

            matches = []
            for mentor in mentors:
                mentor_skills = set((mentor.profile or {}).get('skills', []))
                skill_overlap = len(learner_skills & mentor_skills)

                # Simple scoring based on skill overlap
                score = min(skill_overlap * 20, 100)  # Max 100 points

                matches.append({
                    'mentor': mentor,
                    'score': score,
                    'reasoning': f"{skill_overlap} skill(s) in common",
                    'compatibility_factors': {
                        'skill_overlap': skill_overlap,
                        'location_match': learner.profile.get('location') == mentor.profile.get('location')
                    }
                })

            # Sort by score descending
            matches.sort(key=lambda x: x['score'], reverse=True)
            return matches

        except Exception as e:
            logger.error(f"Fallback matching failed: {str(e)}")
            return []

    @staticmethod
    def create_match_request(learner: User, mentor: User, notes: str = "") -> MentorMatch:
        """
        Create a mentor match request
        """
        try:
            # Check if match already exists
            existing_match = MentorMatch.objects.filter(
                learner=learner,
                mentor=mentor,
                status__in=['pending', 'active']
            ).first()

            if existing_match:
                raise ValueError("Match request already exists")

            match = MentorMatch.objects.create(
                learner=learner,
                mentor=mentor,
                status='pending'
            )

            # Create notification for mentor
            Notification.objects.create(
                user=mentor,
                type='match',
                content=f"New mentorship request from {learner.email}",
            )

            return match

        except Exception as e:
            logger.error(f"Error creating match request: {str(e)}")
            raise

    @staticmethod
    def update_match_status(match: MentorMatch, new_status: str, user: User) -> bool:
        """
        Update match status with proper authorization
        """
        try:
            # Authorization check
            if user.role == 'mentor' and match.mentor != user:
                raise PermissionError("Only the assigned mentor can update this match")
            elif user.role not in ['mentor', 'admin'] and match.learner != user:
                raise PermissionError("Unauthorized to update this match")

            # Status transition validation
            valid_transitions = {
                'pending': ['active', 'rejected'],
                'active': ['completed'],
                'rejected': [],
                'completed': []
            }

            if new_status not in valid_transitions.get(match.status, []):
                raise ValueError(f"Invalid status transition from {match.status} to {new_status}")

            match.status = new_status
            match.save()

            # Create notifications
            if new_status == 'active':
                Notification.objects.create(
                    user=match.learner,
                    type='match',
                    content=f"Your mentorship request with {match.mentor.email} has been accepted!",
                )
            elif new_status == 'completed':
                Notification.objects.create(
                    user=match.learner,
                    type='match',
                    content=f"Your mentorship session with {match.mentor.email} has been completed.",
                )

            return True

        except Exception as e:
            logger.error(f"Error updating match status: {str(e)}")
            return False

    @staticmethod
    def calculate_mentor_rating(mentor: User) -> float:
        """
        Calculate mentor's average rating from completed matches
        """
        try:
            completed_matches = MentorMatch.objects.filter(
                mentor=mentor,
                status='completed'
            ).exclude(rating__isnull=True)

            if not completed_matches:
                return 0.0

            total_rating = sum(match.rating for match in completed_matches)
            average_rating = total_rating / completed_matches.count()

            return round(average_rating, 1)

        except Exception as e:
            logger.error(f"Error calculating mentor rating: {str(e)}")
            return 0.0
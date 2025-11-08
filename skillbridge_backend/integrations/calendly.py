import os
import logging
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from datetime import timezone
import json

logger = logging.getLogger(__name__)

class CalendlyIntegration:
    """Calendly API integration for scheduling mentor sessions"""
    
    def __init__(self):
        self.api_token = os.getenv('CALENDLY_API_TOKEN')
        self.base_url = 'https://api.calendly.com'
        self.headers = {}
        
        if self.api_token:
            self.headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json'
            }
            logger.info("Calendly API initialized successfully")
        else:
            logger.warning("Calendly API token not configured")
    
    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """Get current user information from Calendly"""
        if not self.api_token:
            return self._get_mock_user_info()
        
        try:
            response = requests.get(
                f"{self.base_url}/users/me",
                headers=self.headers
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Error getting Calendly user info: {str(e)}")
            return self._get_mock_user_info()
    
    def get_event_types(self, user_uri: str) -> List[Dict[str, Any]]:
        """Get available event types for a user"""
        if not self.api_token:
            return self._get_mock_event_types()
        
        try:
            params = {'user': user_uri}
            response = requests.get(
                f"{self.base_url}/event_types",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get('collection', [])
            
        except requests.RequestException as e:
            logger.error(f"Error getting Calendly event types: {str(e)}")
            return self._get_mock_event_types()
    
    def get_scheduled_events(self, user_uri: str, start_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get scheduled events for a user"""
        if not self.api_token:
            return self._get_mock_scheduled_events()
        
        if not start_time:
            start_time = datetime.now()
        
        try:
            params = {
                'user': user_uri,
                'min_start_time': start_time.isoformat(),
                'max_start_time': (start_time + timedelta(days=30)).isoformat(),
                'sort': 'start_time:asc'
            }
            
            response = requests.get(
                f"{self.base_url}/scheduled_events",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            events = data.get('collection', [])
            
            # Process events to include useful information
            for event in events:
                event['formatted_start'] = datetime.fromisoformat(
                    event['start_time'].replace('Z', '+00:00')
                ).strftime('%Y-%m-%d %H:%M')
                event['formatted_duration'] = self._calculate_duration(event)
            
            return events
            
        except requests.RequestException as e:
            logger.error(f"Error getting scheduled events: {str(e)}")
            return self._get_mock_scheduled_events()
    
    def get_event_details(self, event_uuid: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific event"""
        if not self.api_token:
            return self._get_mock_event_details()
        
        try:
            response = requests.get(
                f"{self.base_url}/scheduled_events/{event_uuid}",
                headers=self.headers
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Error getting event details: {str(e)}")
            return self._get_mock_event_details()
    
    def create_scheduling_link(self, event_type_uri: str, invitee_email: str, 
                              invitee_name: str) -> Optional[Dict[str, Any]]:
        """Create a scheduling link for a specific event type"""
        if not self.api_token:
            return self._get_mock_scheduling_link()
        
        try:
            # Create a one-off scheduling link
            payload = {
                'max_event_count': 1,
                'owner': event_type_uri,
                'owner_type': 'EventType'
            }
            
            response = requests.post(
                f"{self.base_url}/scheduling_links",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Error creating scheduling link: {str(e)}")
            return self._get_mock_scheduling_link()
    
    def get_organization_members(self, organization_uri: str) -> List[Dict[str, Any]]:
        """Get members of an organization"""
        if not self.api_token:
            return self._get_mock_organization_members()
        
        try:
            params = {'organization': organization_uri}
            response = requests.get(
                f"{self.base_url}/organization_memberships",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get('collection', [])
            
        except requests.RequestException as e:
            logger.error(f"Error getting organization members: {str(e)}")
            return self._get_mock_organization_members()
    
    def get_availability_schedules(self, user_uri: str) -> List[Dict[str, Any]]:
        """Get availability schedules for a user"""
        if not self.api_token:
            return self._get_mock_availability_schedules()
        
        try:
            params = {'user': user_uri}
            response = requests.get(
                f"{self.base_url}/availability_schedules",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get('collection', [])
            
        except requests.RequestException as e:
            logger.error(f"Error getting availability schedules: {str(e)}")
            return self._get_mock_availability_schedules()
    
    def find_mentor_availability(self, mentors: List[str], start_time: datetime, 
                                duration_minutes: int = 60) -> Dict[str, Any]:
        """
        Find available time slots for mentors
        
        Args:
            mentors: List of mentor Calendly URIs
            start_time: Start time to search from
            duration_minutes: Desired meeting duration
            
        Returns:
            Dictionary with available slots by mentor
        """
        available_slots = {}
        
        # Ensure start_time is timezone-aware
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)
        
        for mentor_uri in mentors:
            try:
                # Get mentor's event types to determine available durations
                event_types = self.get_event_types(mentor_uri)
                
                # Check scheduled events to find available times
                scheduled_events = self.get_scheduled_events(mentor_uri, start_time)
                
                # Find 30-day window
                end_time = start_time + timedelta(days=30)
                
                # Simple availability calculation (hourly slots)
                available_times = []
                current_time = start_time.replace(hour=9, minute=0, second=0, microsecond=0)
                
                while current_time < end_time:
                    # Skip weekends
                    if current_time.weekday() < 5:  # Monday = 0
                        # Check if this time conflicts with any scheduled events
                        is_available = True
                        
                        for event in scheduled_events:
                            try:
                                event_start = datetime.fromisoformat(
                                    event['start_time'].replace('Z', '+00:00')
                                )
                                event_end = datetime.fromisoformat(
                                    event['end_time'].replace('Z', '+00:00')
                                )
                                
                                # Make event times timezone-aware if they aren't
                                if event_start.tzinfo is None:
                                    event_start = event_start.replace(tzinfo=timezone.utc)
                                if event_end.tzinfo is None:
                                    event_end = event_end.replace(tzinfo=timezone.utc)
                                
                                # Check for conflicts
                                if (current_time < event_end and 
                                    current_time + timedelta(minutes=duration_minutes) > event_start):
                                    is_available = False
                                    break
                            except Exception as inner_e:
                                logger.warning(f"Error parsing event time: {inner_e}")
                                continue
                        
                        if is_available:
                            available_times.append({
                                'start_time': current_time.isoformat(),
                                'end_time': (current_time + timedelta(minutes=duration_minutes)).isoformat(),
                                'formatted_time': current_time.strftime('%Y-%m-%d %H:%M')
                            })
                    
                    current_time += timedelta(hours=1)
                
                available_slots[mentor_uri] = available_times[:10]  # Limit to 10 slots per mentor
                
            except Exception as e:
                logger.error(f"Error checking availability for mentor {mentor_uri}: {str(e)}")
                available_slots[mentor_uri] = []
        
        return available_slots
    
    def _calculate_duration(self, event: Dict[str, Any]) -> int:
        """Calculate event duration in minutes"""
        try:
            start = datetime.fromisoformat(event['start_time'].replace('Z', '+00:00'))
            end = datetime.fromisoformat(event['end_time'].replace('Z', '+00:00'))
            return int((end - start).total_seconds() / 60)
        except:
            return 60  # Default duration
    
    def _get_mock_user_info(self) -> Dict[str, Any]:
        """Get mock user info for testing"""
        return {
            'resource': {
                'uri': 'https://api.calendly.com/users/mock-user',
                'name': 'Mock User',
                'slug': 'mock-user',
                'email': 'mock@example.com',
                'timezone': 'UTC',
                'avatar_url': 'https://via.placeholder.com/100x100'
            }
        }
    
    def _get_mock_event_types(self) -> List[Dict[str, Any]]:
        """Get mock event types for testing"""
        return [
            {
                'uri': 'https://api.calendly.com/event_types/mock-type-1',
                'name': '1:1 Mentoring Session',
                'duration': 60,
                'description': 'One-on-one mentoring session to discuss learning goals and progress',
                'active': True
            },
            {
                'uri': 'https://api.calendly.com/event_types/mock-type-2',
                'name': 'Code Review Session',
                'duration': 90,
                'description': 'Code review and discussion session',
                'active': True
            }
        ]
    
    def _get_mock_scheduled_events(self) -> List[Dict[str, Any]]:
        """Get mock scheduled events for testing"""
        from django.utils import timezone
        now = timezone.now()
        events = [
            {
                'uri': f'https://api.calendly.com/scheduled_events/mock-{i}',
                'name': f'Mentoring Session {i+1}',
                'start_time': (now + timedelta(days=i+1, hours=14)).isoformat() + 'Z',
                'end_time': (now + timedelta(days=i+1, hours=15)).isoformat() + 'Z',
                'event_type': 'https://api.calendly.com/event_types/mock-type-1',
                'status': 'active'
            }
            for i in range(3)
        ]
        
        # Add formatted_start to each event
        for event in events:
            try:
                start_dt = datetime.fromisoformat(event['start_time'].replace('Z', '+00:00'))
                if start_dt.tzinfo is None:
                    start_dt = start_dt.replace(tzinfo=timezone.utc)
                event['formatted_start'] = start_dt.strftime('%Y-%m-%d %H:%M')
            except Exception as e:
                logger.warning(f"Error formatting start time: {e}")
                event['formatted_start'] = 'N/A'
        
        return events
    
    def _get_mock_event_details(self) -> Dict[str, Any]:
        """Get mock event details for testing"""
        return {
            'resource': {
                'uri': 'https://api.calendly.com/scheduled_events/mock-event',
                'name': 'Mock Mentoring Session',
                'start_time': '2023-01-01T14:00:00Z',
                'end_time': '2023-01-01T15:00:00Z',
                'event_type': 'https://api.calendly.com/event_types/mock-type-1',
                'status': 'active',
                'location': {'type': 'zoom', 'location': 'https://zoom.us/j/123456789'}
            }
        }
    
    def _get_mock_scheduling_link(self) -> Dict[str, Any]:
        """Get mock scheduling link for testing"""
        return {
            'resource': {
                'booking_url': 'https://calendly.com/mock-user/mentoring-session',
                'owner': 'https://api.calendly.com/event_types/mock-type-1',
                'max_event_count': 1
            }
        }
    
    def _get_mock_organization_members(self) -> List[Dict[str, Any]]:
        """Get mock organization members for testing"""
        return [
            {
                'uri': 'https://api.calendly.com/organization_memberships/mock-member-1',
                'user': 'https://api.calendly.com/users/mentor-1',
                'organization': 'https://api.calendly.com/organizations/mock-org',
                'role': 'member'
            }
        ]
    
    def _get_mock_availability_schedules(self) -> List[Dict[str, Any]]:
        """Get mock availability schedules for testing"""
        return [
            {
                'uri': 'https://api.calendly.com/availability_schedules/mock-schedule',
                'name': 'Default Schedule',
                'timezone': 'UTC',
                'rules': [
                    {
                        'type': 'wday',
                        'wday': [1, 2, 3, 4, 5],  # Monday-Friday
                        'start_time': '09:00',
                        'end_time': '17:00'
                    }
                ]
            }
        ]
    
    def health_check(self) -> Dict[str, Any]:
        """Check Calendly API health"""
        if not self.api_token:
            return {
                'status': 'unhealthy',
                'message': 'Calendly API token not configured'
            }
        
        try:
            # Test API access
            response = requests.get(
                f"{self.base_url}/users/me",
                headers=self.headers,
                timeout=5
            )
            response.raise_for_status()
            
            return {
                'status': 'healthy',
                'message': 'Calendly API operational'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'API error: {str(e)}'
            }
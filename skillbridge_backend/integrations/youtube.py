import os
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class YouTubeIntegration:
    """YouTube API integration for learning resources"""
    
    def __init__(self):
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        self.youtube = None
        
        if self.api_key:
            try:
                from googleapiclient.discovery import build
                from googleapiclient.errors import HttpError
                self.youtube = build('youtube', 'v3', developerKey=self.api_key)
                logger.info("YouTube API initialized successfully")
            except ImportError:
                logger.warning("googleapiclient not installed, using mock data")
                self.youtube = None
            except Exception as e:
                logger.error(f"Failed to initialize YouTube API: {str(e)}")
                self.youtube = None
        else:
            logger.warning("YouTube API key not configured")
    
    def search_learning_videos(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for educational videos on YouTube
        
        Args:
            query: Search query (e.g., "Python programming tutorial")
            max_results: Maximum number of results to return
            
        Returns:
            List of video metadata dictionaries
        """
        if not self.youtube:
            logger.warning("YouTube API not available, returning mock data")
            return self._generate_mock_videos(query, max_results)
        
        try:
            # Search for videos
            search_response = self.youtube.search().list(
                q=f"{query} tutorial",
                type='video',
                part='snippet',
                maxResults=max_results,
                order='relevance',
                safeSearch='moderate'
            ).execute()
            
            videos = []
            for item in search_response.get('items', []):
                video_id = item['id']['videoId']
                
                # Get additional video statistics
                stats_response = self.youtube.videos().list(
                    part='statistics,contentDetails',
                    id=video_id
                ).execute()
                
                video_data = item['snippet']
                stats = stats_response.get('items', [{}])[0].get('statistics', {})
                content_details = stats_response.get('items', [{}])[0].get('contentDetails', {})
                
                # Parse duration
                duration = self._parse_duration(content_details.get('duration', 'PT0S'))
                
                videos.append({
                    'id': video_id,
                    'title': video_data['title'],
                    'description': video_data['description'],
                    'channel': video_data['channelTitle'],
                    'channel_id': video_data['channelId'],
                    'published_at': video_data['publishedAt'],
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'thumbnail': video_data['thumbnails'].get('high', {}).get('url', ''),
                    'view_count': int(stats.get('viewCount', 0)),
                    'like_count': int(stats.get('likeCount', 0)),
                    'duration_minutes': duration,
                    'difficulty': self._estimate_difficulty(video_data['title'], video_data['description'])
                })
            
            return videos
            
        except HttpError as e:
            logger.error(f"YouTube API error: {str(e)}")
            return self._generate_mock_videos(query, max_results)
        except Exception as e:
            logger.error(f"Error searching YouTube videos: {str(e)}")
            return []
    
    def get_learning_playlists(self, topic: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Get educational playlists for a topic"""
        if not self.youtube:
            return self._generate_mock_playlists(topic, max_results)
        
        try:
            search_response = self.youtube.search().list(
                q=f"{topic} course tutorial playlist",
                type='playlist',
                part='snippet',
                maxResults=max_results,
                order='relevance'
            ).execute()
            
            playlists = []
            for item in search_response.get('items', []):
                playlist_id = item['id']['playlistId']
                playlist_data = item['snippet']
                
                # Get playlist details including video count
                playlist_response = self.youtube.playlists().list(
                    part='contentDetails',
                    id=playlist_id
                ).execute()
                
                content_details = playlist_response.get('items', [{}])[0].get('contentDetails', {})
                video_count = content_details.get('itemCount', 0)
                
                playlists.append({
                    'id': playlist_id,
                    'title': playlist_data['title'],
                    'description': playlist_data['description'],
                    'channel': playlist_data['channelTitle'],
                    'published_at': playlist_data['publishedAt'],
                    'url': f"https://www.youtube.com/playlist?list={playlist_id}",
                    'thumbnail': playlist_data['thumbnails'].get('high', {}).get('url', ''),
                    'video_count': video_count
                })
            
            return playlists
            
        except HttpError as e:
            logger.error(f"YouTube API error: {str(e)}")
            return self._generate_mock_playlists(topic, max_results)
        except Exception as e:
            logger.error(f"Error getting YouTube playlists: {str(e)}")
            return []
    
    def get_educational_channels(self, topic: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Find educational YouTube channels for a topic"""
        if not self.youtube:
            return self._generate_mock_channels(topic, max_results)
        
        try:
            search_response = self.youtube.search().list(
                q=f"{topic} programming coding course",
                type='channel',
                part='snippet',
                maxResults=max_results,
                order='relevance'
            ).execute()
            
            channels = []
            for item in search_response.get('items', []):
                channel_id = item['id']['channelId']
                channel_data = item['snippet']
                
                # Get channel statistics
                channel_response = self.youtube.channels().list(
                    part='statistics',
                    id=channel_id
                ).execute()
                
                stats = channel_response.get('items', [{}])[0].get('statistics', {})
                
                channels.append({
                    'id': channel_id,
                    'title': channel_data['title'],
                    'description': channel_data['description'],
                    'published_at': channel_data['publishedAt'],
                    'url': f"https://www.youtube.com/channel/{channel_id}",
                    'thumbnail': channel_data['thumbnails'].get('high', {}).get('url', ''),
                    'subscriber_count': int(stats.get('subscriberCount', 0)),
                    'video_count': int(stats.get('videoCount', 0)),
                    'view_count': int(stats.get('viewCount', 0))
                })
            
            return channels
            
        except HttpError as e:
            logger.error(f"YouTube API error: {str(e)}")
            return self._generate_mock_channels(topic, max_results)
        except Exception as e:
            logger.error(f"Error getting YouTube channels: {str(e)}")
            return []
    
    def _parse_duration(self, duration: str) -> int:
        """Parse ISO 8601 duration to minutes"""
        try:
            import isodate
            parsed_duration = isodate.parse_duration(duration)
            return int(parsed_duration.total_seconds() / 60)
        except ImportError:
            # Fallback for parsing without isodate
            import re
            match = re.search(r'PT(?:(\d+)H)?(?:(\d+)M)?', duration)
            if match:
                hours = int(match.group(1) or 0)
                minutes = int(match.group(2) or 0)
                return hours * 60 + minutes
            return 0
        except:
            return 0
    
    def _estimate_difficulty(self, title: str, description: str) -> str:
        """Estimate video difficulty based on content"""
        text = f"{title} {description}".lower()
        
        # Beginner indicators
        beginner_keywords = ['beginner', 'introduction', 'basics', 'getting started', 'fundamentals']
        # Intermediate indicators
        intermediate_keywords = ['intermediate', 'advanced basics', 'deep dive']
        # Advanced indicators
        advanced_keywords = ['advanced', 'expert', 'masterclass', 'professional']
        
        if any(keyword in text for keyword in advanced_keywords):
            return 'advanced'
        elif any(keyword in text for keyword in intermediate_keywords):
            return 'intermediate'
        elif any(keyword in text for keyword in beginner_keywords):
            return 'beginner'
        else:
            return 'intermediate'  # default
    
    def _generate_mock_videos(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock video data for testing"""
        return [
            {
                'id': f'mock_{i}',
                'title': f'{query} Tutorial #{i+1}',
                'description': f'Learn {query} with this comprehensive tutorial',
                'channel': 'Educational Channel',
                'channel_id': f'channel_{i}',
                'published_at': '2023-01-01T00:00:00Z',
                'url': f'https://www.youtube.com/watch?v=mock_{i}',
                'thumbnail': 'https://via.placeholder.com/480x360',
                'view_count': 1000 + i * 100,
                'like_count': 50 + i * 10,
                'duration_minutes': 30 + i * 5,
                'difficulty': 'intermediate'
            }
            for i in range(max_results)
        ]
    
    def _generate_mock_playlists(self, topic: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock playlist data for testing"""
        return [
            {
                'id': f'playlist_{i}',
                'title': f'{topic} Complete Course #{i+1}',
                'description': f'Complete {topic} learning course with hands-on projects',
                'channel': 'Learning Platform',
                'published_at': '2023-01-01T00:00:00Z',
                'url': f'https://www.youtube.com/playlist?list=playlist_{i}',
                'thumbnail': 'https://via.placeholder.com/480x360',
                'video_count': 20 + i * 5
            }
            for i in range(max_results)
        ]
    
    def _generate_mock_channels(self, topic: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock channel data for testing"""
        return [
            {
                'id': f'channel_{i}',
                'title': f'{topic} Expert #{i+1}',
                'description': f'Professional {topic} tutorials and courses',
                'published_at': '2020-01-01T00:00:00Z',
                'url': f'https://www.youtube.com/channel/channel_{i}',
                'thumbnail': 'https://via.placeholder.com/88x88',
                'subscriber_count': 10000 + i * 1000,
                'video_count': 50 + i * 10,
                'view_count': 100000 + i * 5000
            }
            for i in range(max_results)
        ]
    
    def health_check(self) -> Dict[str, Any]:
        """Check YouTube API health"""
        if not self.youtube:
            return {
                'status': 'unhealthy',
                'message': 'YouTube API not configured'
            }
        
        try:
            # Simple test request
            self.youtube.search().list(
                q='test',
                part='snippet',
                maxResults=1
            ).execute()
            
            return {
                'status': 'healthy',
                'message': 'YouTube API operational'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'API error: {str(e)}'
            }
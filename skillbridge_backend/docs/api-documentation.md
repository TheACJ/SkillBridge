# SkillBridge API Documentation

## Overview

SkillBridge provides a comprehensive REST API for mentorship platform functionality. The API is built with Django REST Framework and follows RESTful conventions.

**Base URL**: `https://api.skillbridge.com/api/v1/`

**Authentication**: JWT Bearer tokens

**Content Type**: `application/json`

## Authentication

### Register User

```http
POST /api/v1/auth/register/
```

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe",
  "user_type": "mentee",
  "skills": ["python", "django"],
  "experience_level": "beginner"
}
```

**Response** (201 Created):
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "user_type": "mentee",
    "is_active": true,
    "date_joined": "2024-01-01T00:00:00Z"
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

### Login

```http
POST /api/v1/auth/login/
```

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response** (200 OK):
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "user_type": "mentee"
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

### Refresh Token

```http
POST /api/v1/auth/refresh/
```

**Request Body**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## Users

### List Mentors

```http
GET /api/v1/users/mentors/
```

**Query Parameters**:
- `skills` (string): Comma-separated skills
- `experience_level` (string): beginner, intermediate, advanced
- `availability` (string): available, busy, unavailable
- `page` (integer): Page number for pagination

**Response** (200 OK):
```json
{
  "count": 25,
  "next": "http://api.skillbridge.com/api/v1/users/mentors/?page=2",
  "previous": null,
  "results": [
    {
      "id": 2,
      "email": "mentor@example.com",
      "first_name": "Jane",
      "last_name": "Smith",
      "user_type": "mentor",
      "skills": ["python", "django", "react"],
      "experience_level": "advanced",
      "availability": "available",
      "rating": 4.8,
      "total_mentees": 15,
      "bio": "Senior Python developer with 8 years experience",
      "profile_image": "https://api.skillbridge.com/media/profiles/jane.jpg"
    }
  ]
}
```

### Get User Profile

```http
GET /api/v1/users/profile/
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "user_type": "mentee",
  "skills": ["python", "django"],
  "experience_level": "beginner",
  "bio": "Aspiring web developer",
  "github_username": "johndoe",
  "linkedin_url": "https://linkedin.com/in/johndoe",
  "portfolio_url": "https://johndoe.dev",
  "availability": "available",
  "timezone": "America/New_York",
  "languages": ["en", "es"],
  "profile_completion": 85
}
```

### Update Profile

```http
PATCH /api/v1/users/profile/
Authorization: Bearer <access_token>
```

**Request Body**:
```json
{
  "bio": "Updated bio",
  "skills": ["python", "django", "react"],
  "availability": "busy"
}
```

## Roadmaps

### Generate Roadmap

```http
POST /api/v1/roadmaps/generate/
Authorization: Bearer <access_token>
```

**Request Body**:
```json
{
  "goal": "Become a full-stack Python developer",
  "current_skills": ["basic python", "html", "css"],
  "target_skills": ["django", "react", "postgresql", "docker"],
  "time_commitment": "20_hours_week",
  "timeline_months": 6,
  "learning_style": "hands_on"
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "title": "Full-Stack Python Developer Roadmap",
  "description": "6-month journey to becoming a full-stack developer",
  "goal": "Become a full-stack Python developer",
  "modules": [
    {
      "id": 1,
      "title": "Python Fundamentals",
      "description": "Master Python basics and best practices",
      "order": 1,
      "estimated_hours": 40,
      "resources": [
        {
          "title": "Python Crash Course",
          "type": "book",
          "url": "https://example.com/python-crash-course",
          "difficulty": "beginner"
        }
      ],
      "completed": false,
      "progress_percentage": 0
    }
  ],
  "total_modules": 12,
  "estimated_total_hours": 240,
  "progress_percentage": 0,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### List User Roadmaps

```http
GET /api/v1/roadmaps/
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "title": "Full-Stack Python Developer Roadmap",
      "progress_percentage": 35,
      "total_modules": 12,
      "completed_modules": 4,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Update Module Progress

```http
POST /api/v1/roadmaps/{roadmap_id}/modules/{module_id}/progress/
Authorization: Bearer <access_token>
```

**Request Body**:
```json
{
  "completed": true,
  "notes": "Completed all exercises and built a small project",
  "time_spent_hours": 8
}
```

## Matches

### Request Mentor Match

```http
POST /api/v1/matches/request/
Authorization: Bearer <access_token>
```

**Request Body**:
```json
{
  "mentor_id": 2,
  "message": "Hi, I'm interested in learning Python and would love your guidance",
  "topics": ["python", "django", "web development"],
  "availability": "weekends",
  "goals": "Build a portfolio project within 3 months"
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "mentee": {
    "id": 1,
    "name": "John Doe"
  },
  "mentor": {
    "id": 2,
    "name": "Jane Smith"
  },
  "status": "pending",
  "message": "Hi, I'm interested in learning Python...",
  "topics": ["python", "django", "web development"],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### List Matches

```http
GET /api/v1/matches/
Authorization: Bearer <access_token>
```

**Query Parameters**:
- `status` (string): pending, accepted, active, completed, cancelled
- `role` (string): mentee, mentor

**Response** (200 OK):
```json
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "other_user": {
        "id": 2,
        "name": "Jane Smith",
        "role": "mentor"
      },
      "status": "active",
      "topics": ["python", "django"],
      "last_activity": "2024-01-15T10:30:00Z",
      "unread_messages": 2
    }
  ]
}
```

### Accept/Reject Match

```http
POST /api/v1/matches/{match_id}/respond/
Authorization: Bearer <access_token>
```

**Request Body**:
```json
{
  "action": "accept",
  "message": "I'd be happy to mentor you! Let's schedule our first session."
}
```

## Progress Tracking

### Log Progress

```http
POST /api/v1/progress/log/
Authorization: Bearer <access_token>
```

**Request Body**:
```json
{
  "roadmap_id": 1,
  "module_id": 1,
  "activity_type": "study",
  "description": "Completed Python variables and data types chapter",
  "time_spent_minutes": 120,
  "difficulty_rating": 3,
  "notes": "Good progress, need more practice with dictionaries",
  "resources_used": [
    "Python Crash Course - Chapter 2",
    "https://docs.python.org/3/tutorial/"
  ]
}
```

### Get Progress Analytics

```http
GET /api/v1/progress/analytics/
Authorization: Bearer <access_token>
```

**Query Parameters**:
- `period` (string): week, month, year
- `roadmap_id` (integer): Specific roadmap

**Response** (200 OK):
```json
{
  "total_time_spent": 2400,
  "average_session_length": 90,
  "current_streak_days": 7,
  "longest_streak_days": 14,
  "completion_rate": 68.5,
  "skill_progress": {
    "python": 75,
    "django": 45,
    "react": 20
  },
  "weekly_stats": [
    {
      "week": "2024-W01",
      "time_spent": 480,
      "modules_completed": 2,
      "average_difficulty": 2.5
    }
  ]
}
```

## Badges & Gamification

### List Earned Badges

```http
GET /api/v1/badges/
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "name": "First Steps",
      "description": "Complete your first learning module",
      "icon": "🎯",
      "rarity": "common",
      "earned_at": "2024-01-05T00:00:00Z",
      "category": "progress"
    }
  ]
}
```

### Leaderboard

```http
GET /api/v1/leaderboard/
```

**Query Parameters**:
- `category` (string): overall, weekly, monthly
- `limit` (integer): Number of results (default: 50)

**Response** (200 OK):
```json
{
  "leaderboard": [
    {
      "rank": 1,
      "user": {
        "id": 3,
        "name": "Alice Johnson",
        "avatar": "https://api.skillbridge.com/media/avatars/alice.jpg"
      },
      "score": 2450,
      "badges_count": 12,
      "streak_days": 30
    }
  ],
  "user_rank": {
    "rank": 15,
    "score": 1200,
    "change": 2
  }
}
```

## Forum

### List Discussions

```http
GET /api/v1/forum/discussions/
```

**Query Parameters**:
- `category` (string): general, technical, career, projects
- `tags` (string): Comma-separated tags
- `sort` (string): recent, popular, unanswered

**Response** (200 OK):
```json
{
  "count": 25,
  "results": [
    {
      "id": 1,
      "title": "Best practices for Django REST API design",
      "author": {
        "id": 2,
        "name": "Jane Smith"
      },
      "category": "technical",
      "tags": ["django", "api", "best-practices"],
      "replies_count": 8,
      "views_count": 156,
      "last_activity": "2024-01-15T14:30:00Z",
      "is_solved": true,
      "created_at": "2024-01-10T09:00:00Z"
    }
  ]
}
```

### Create Discussion

```http
POST /api/v1/forum/discussions/
Authorization: Bearer <access_token>
```

**Request Body**:
```json
{
  "title": "How to optimize database queries in Django",
  "content": "I'm experiencing slow queries with complex joins...",
  "category": "technical",
  "tags": ["django", "database", "performance"]
}
```

## Notifications

### List Notifications

```http
GET /api/v1/notifications/
Authorization: Bearer <access_token>
```

**Query Parameters**:
- `unread_only` (boolean): Show only unread notifications
- `type` (string): match_request, message, badge_earned, etc.

**Response** (200 OK):
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "type": "match_request",
      "title": "New mentorship request",
      "message": "John Doe wants to connect with you",
      "data": {
        "match_id": 5,
        "requester_name": "John Doe"
      },
      "is_read": false,
      "created_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

### Mark as Read

```http
POST /api/v1/notifications/{notification_id}/read/
Authorization: Bearer <access_token>
```

## Health Check

### System Health

```http
GET /api/v1/health/
```

**Response** (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T12:00:00Z",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "rust_service": "healthy",
    "email": "healthy"
  },
  "metrics": {
    "response_time_ms": 45,
    "active_connections": 12,
    "uptime_seconds": 86400
  }
}
```

## Error Responses

All API errors follow this format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "email": ["This field is required"],
      "password": ["Password must be at least 8 characters"]
    }
  }
}
```

### Common Error Codes

- `VALIDATION_ERROR` (400): Invalid input data
- `AUTHENTICATION_ERROR` (401): Invalid or missing authentication
- `PERMISSION_DENIED` (403): Insufficient permissions
- `NOT_FOUND` (404): Resource not found
- `CONFLICT` (409): Resource conflict
- `RATE_LIMITED` (429): Too many requests
- `INTERNAL_ERROR` (500): Server error

## Rate Limiting

API endpoints are rate limited based on user type:

- **Anonymous users**: 10 requests per minute
- **Authenticated users**: 100 requests per minute
- **Mentors**: 200 requests per minute

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Pagination

List endpoints support pagination with these parameters:

- `page` (integer): Page number (default: 1)
- `page_size` (integer): Items per page (default: 20, max: 100)

Response includes pagination metadata:

```json
{
  "count": 150,
  "next": "https://api.skillbridge.com/api/v1/users/?page=2",
  "previous": null,
  "results": [...]
}
```

## Webhooks

SkillBridge supports webhooks for real-time notifications:

### GitHub Integration Webhook

```http
POST /api/v1/webhooks/github/
X-Hub-Signature-256: sha256=...
```

**Payload**: GitHub webhook payload for push events, used to track progress.

### Supported Events

- `push`: Code commits to track learning progress
- `pull_request`: Opened/merged PRs for project completion
- `issues`: Issue creation/resolution tracking

## SDKs and Libraries

### JavaScript SDK

```javascript
import { SkillBridge } from 'skillbridge-sdk';

const client = new SkillBridge({
  apiKey: 'your-api-key',
  baseURL: 'https://api.skillbridge.com/api/v1'
});

// Authenticate
await client.auth.login('user@example.com', 'password');

// Generate roadmap
const roadmap = await client.roadmaps.generate({
  goal: 'Learn React',
  current_skills: ['javascript', 'html'],
  timeline_months: 3
});
```

### Python SDK

```python
from skillbridge import SkillBridge

client = SkillBridge(api_key='your-api-key')

# Get user profile
profile = client.users.get_profile()

# Log progress
client.progress.log(
    roadmap_id=1,
    module_id=1,
    activity_type='study',
    time_spent_minutes=60
)
```

## Versioning

API versioning follows semantic versioning:

- **v1**: Current stable version
- Breaking changes will introduce new major versions (v2, v3, etc.)
- Backward-compatible changes are added to existing versions

## Support

For API support:

- **Documentation**: https://docs.skillbridge.com
- **Status Page**: https://status.skillbridge.com
- **Support**: support@skillbridge.com
- **Community**: https://community.skillbridge.com

## Changelog

### v1.0.0 (Current)
- Initial release with core mentorship features
- JWT authentication
- Roadmap generation with AI
- Mentor matching
- Progress tracking
- Gamification system
- Forum functionality
- GitHub integration
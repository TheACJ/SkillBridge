# SkillBridge Backend Implementation Guide

## 1. Document Overview
### 1.1 Purpose
This document provides a comprehensive, technical blueprint for implementing the backend of SkillBridge, an AI-powered platform for matching learners with personalized skill roadmaps, free resources, and community mentors. It is designed to be production-ready, covering all aspects from architecture to deployment. The backend team should rely solely on this guide for development, assuming familiarity with Django, Supabase, Rust, and related tools.

This guide aligns with the Product Requirements Document (PRD) and Implementation Plan, focusing exclusively on backend responsibilities. Frontend integrations (e.g., API consumption) are noted but not detailed here.

### 1.2 Scope
- **In Scope**: Database design, models, API endpoints, business logic, integrations (GitHub, OpenAI), Rust microservices, security, performance optimizations, testing, and deployment.
- **Out of Scope**: Frontend code, UI/UX, marketing, or non-technical operations.

### 1.3 Assumptions
- Team uses Python 3.10+ for Django, Rust 1.70+ for microservices.
- Development environment: Docker for local consistency.
- Production environment: Cloud-hosted (e.g., Render/Heroku for Django, AWS for Rust).
- Compliance: Adhere to GDPR/NDPR; assume African user focus with low-bandwidth optimizations.

### 1.4 Version and Updates
- Version: 1.0 (November 04, 2025).
- Updates: Any changes must be versioned and approved by the lead architect.

## 2. Architecture
### 2.1 High-Level Overview
- **Core Framework**: Django 4.2+ as the monolithic backend for API serving, authentication, and orchestration.
- **Database**: Supabase (PostgreSQL-based) for relational data storage, real-time features, and authentication.
- **Microservices**: Rust for performance-intensive tasks (e.g., mentor-matching algorithm) to handle computational efficiency and scalability. Communicate via gRPC for low-latency.
- **Async Processing**: Celery with Redis broker for background tasks (e.g., notifications, AI calls).
- **Caching**: Redis for frequently accessed data (e.g., roadmaps).
- **Integrations**: External APIs (OpenAI, GitHub) via HTTP clients.
- **Real-Time**: Supabase Realtime for notifications and chat updates.
- **Deployment Model**: Containerized (Docker) with orchestration (Kubernetes if scaling beyond initial needs).
- **Scalability**: Horizontal scaling for Django workers; Rust services on serverless (e.g., AWS Lambda) for bursts.

### 2.2 Component Diagram
(Conceptual; implement in draw.io or similar for visuals)
- Client (Frontend) → API Gateway (Django URLs) → Business Logic (Views/Services) → DB (Supabase) / Cache (Redis) / Microservices (Rust via gRPC).
- External: OpenAI API, GitHub Webhooks/API.

### 2.3 Data Flow
- User Request → Authentication Middleware → View → Service (e.g., call Rust for matching) → DB Query → Response.
- Async: Webhook (GitHub) → Celery Task → Update DB → Realtime Broadcast.

## 3. Database Design (Supabase)
### 3.1 Schema Overview
Use Supabase Studio for initial setup, then Row Level Security (RLS) for access control. All tables use UUID primary keys for security.

- **Users Table** (auth.users extended via Supabase Auth):
  - id: UUID (PK)
  - email: String (unique)
  - role: Enum ('learner', 'mentor', 'admin')
  - profile: JSONB (skills: Array<String>, location: String, availability: Integer (hours/week), github_username: String)
  - created_at: Timestamp
  - updated_at: Timestamp

- **Roadmaps Table**:
  - id: UUID (PK)
  - user_id: UUID (FK to Users)
  - domain: String (e.g., 'Python', 'Blockchain')
  - modules: JSONB (array of {name: String, resources: Array<URL>, estimated_time: Integer, completed: Boolean})
  - progress: Float (0-100)
  - created_at: Timestamp
  - updated_at: Timestamp

- **MentorMatches Table**:
  - id: UUID (PK)
  - learner_id: UUID (FK to Users)
  - mentor_id: UUID (FK to Users)
  - status: Enum ('pending', 'active', 'completed', 'rejected')
  - session_schedule: JSONB (array of {time: Timestamp, topic: String})
  - rating: Integer (1-5, post-completion)
  - created_at: Timestamp

- **Badges Table**:
  - id: UUID (PK)
  - mentor_id: UUID (FK to Users)
  - type: String (e.g., 'Bronze Mentor')
  - criteria: JSONB (e.g., {sessions_completed: Integer})
  - awarded_at: Timestamp

- **ProgressLogs Table** (for GitHub tracking):
  - id: UUID (PK)
  - user_id: UUID (FK)
  - roadmap_id: UUID (FK)
  - event_type: String (e.g., 'commit')
  - details: JSONB (e.g., {repo: String, commit_hash: String})
  - timestamp: Timestamp

- **Notifications Table**:
  - id: UUID (PK)
  - user_id: UUID (FK)
  - type: Enum ('match', 'progress_update', 'session_reminder')
  - content: String
  - read: Boolean
  - created_at: Timestamp

- **ForumPosts Table** (for community Q&A):
  - id: UUID (PK)
  - user_id: UUID (FK)
  - category: String (e.g., 'Python')
  - content: Text
  - parent_id: UUID (self-FK for replies)
  - created_at: Timestamp

### 3.2 Indexes and Constraints
- Indexes: On foreign keys, frequently queried fields (e.g., user_id in Roadmaps).
- Constraints: Unique (email), Not Null (critical fields), Check (progress between 0-100).
- RLS Policies: e.g., Users can only read/update their own data; Admins have full access.

### 3.3 Migrations
- Use Django migrations for schema changes, synced with Supabase via custom scripts (e.g., supabase-py client).

## 4. Django Models and Serializers
### 4.1 Models
Define in `models.py` using Django ORM, but map to Supabase via custom backend if needed (default PostgreSQL driver works).

- Example: 
```python
from django.db import models
from uuid import uuid4

class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=[('learner', 'Learner'), ('mentor', 'Mentor'), ('admin', 'Admin')])
    profile = models.JSONField(default=dict)
    # Timestamps via auto_now_add/auto_now
```

Sync all models from Section 3.1.

### 4.2 Serializers (Django REST Framework)
Use DRF Serializers for API responses.

- Example:
```python
from rest_framework import serializers
from .models import Roadmap

class RoadmapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roadmap
        fields = '__all__'
```

Include validation (e.g., ensure modules JSON conforms to schema).

## 5. API Endpoints (Django REST Framework)
### 5.1 Base Configuration
- Use DRF routers for URL patterns.
- Authentication: JWT via Supabase Auth (integrate with django-rest-framework-simplejwt).
- Pagination: LimitOffsetPagination for lists.
- Rate Limiting: DRF built-in (e.g., 100 requests/min per user).
- Base URL: /api/v1/

### 5.2 Endpoints List
- **Authentication**:
  - POST /auth/register: {email, password, role, profile} → Create user in Supabase Auth.
  - POST /auth/login: {email, password} → Return JWT.
  - POST /auth/refresh: Refresh token.

- **Users**:
  - GET /users/me: Retrieve current user profile.
  - PATCH /users/me: Update profile (e.g., skills).
  - GET /users/mentors: List available mentors (filtered by skills, location; paginated).

- **Roadmaps**:
  - POST /roadmaps: {domain, skill_level, time_availability} → Call OpenAI for generation, save to DB.
  - GET /roadmaps/{id}: Retrieve specific roadmap.
  - PATCH /roadmaps/{id}: Update progress (manual or via GitHub).
  - GET /roadmaps/my: List user's roadmaps.

- **Mentor Matching**:
  - POST /matches: {learner_needs} → Call Rust microservice for matching, create match record.
  - GET /matches/my: List user's matches.
  - PATCH /matches/{id}: Update status/rating/schedule.
  - POST /matches/{id}/chat: Send message (store in JSONB or separate table).

- **Badges**:
  - GET /badges/my: List mentor's badges.
  - POST /badges/award: Admin-only; award based on criteria.

- **Progress**:
  - POST /progress/log: {event_type, details} → Log GitHub event.
  - GET /progress/{roadmap_id}: Get progress details.

- **Notifications**:
  - GET /notifications/my: List unread/read.
  - PATCH /notifications/{id}/read: Mark as read.

- **Forum**:
  - POST /forum/posts: {category, content, parent_id}.
  - GET /forum/posts?category=... : List with pagination.
  - GET /forum/posts/{id}: With replies.

### 5.3 Error Handling
- Standard HTTP codes: 200 OK, 400 Bad Request, 401 Unauthorized, 404 Not Found, 500 Internal.
- Custom exceptions: e.g., MatchingFailedError.

## 6. Business Logic and Services
### 6.1 Core Services
- **Roadmap Generation**: In views.py, call OpenAI API:
```python
import openai
openai.api_key = env('OPENAI_KEY')
response = openai.ChatCompletion.create(model="gpt-4", messages=[{"role": "system", "content": "Generate roadmap..."}, {"role": "user", "content": user_input}])
# Parse and save to Roadmap model
```

- **Progress Tracking**: Webhook view for GitHub:
```python
@csrf_exempt
def github_webhook(request):
    # Verify signature
    payload = json.loads(request.body)
    # Update ProgressLogs, recalculate roadmap progress
```

### 6.2 Rust Microservice
- **Purpose**: Handle mentor matching algorithm (graph-based, e.g., bipartite matching for efficiency).
- **Implementation**:
  - Use Rocket or Actix-web for HTTP/gRPC server.
  - Crates: serde, petgraph, rayon (for parallelism).
  - Example Endpoint: POST /match {learners: Vec<UserData>, mentors: Vec<MentorData>} → Return matches as JSON.
  - Algorithm: Use Hungarian algorithm variant for optimal matching based on skills score, location distance (Haversine formula), availability.
  - Deployment: Dockerize, expose on port 8001; Django calls via grpcio or requests.

- **Integration Code (Django)**:
```python
import requests
def match_mentors(learner_data):
    response = requests.post('http://rust-service:8001/match', json=learner_data)
    return response.json()
```

### 6.3 Async Tasks (Celery)
- Setup: celery.py with Redis broker.
- Tasks: e.g., send_email_notification, process_ai_feedback.

## 7. Integrations
### 7.1 OpenAI/GPT
- Use openai-python library.
- Rate Limit: Implement exponential backoff.

### 7.2 GitHub
- OAuth: For login (use social-auth-app-django).
- API: PyGithub for repo/commit queries.
- Webhooks: For real-time progress (verify HMAC signature).

### 7.3 Other
- YouTube/FreeCodeCamp: Search APIs in roadmap generation (use google-api-python-client).
- Calendly-like: Use iCalendar for scheduling exports.

## 8. Security
### 8.1 Authentication/Authorization
- JWT with refresh/expiry.
- RLS in Supabase.
- Middleware: Check roles for endpoints (e.g., admin-only for badges).

### 8.2 Data Protection
- Encryption: Use HTTPS; store sensitive data hashed (e.g., via django.contrib.auth).
- Input Sanitization: DRF validators, bleach for user content.
- Vulnerabilities: Regular scans with Bandit, Dependency-Check.

### 8.3 Logging and Monitoring
- Use logging module; integrate Sentry.
- Audit Logs: For critical actions (e.g., matches).

## 9. Performance and Optimization
- Query Optimization: Use select_related/prefetch_related.
- Caching: @cache_page for GET endpoints.
- Low-Bandwidth: Compress JSON responses (gzip middleware).
- Scaling: Gunicorn workers; Rust for CPU-bound tasks.

## 10. Testing
### 10.1 Unit Tests
- Pytest for models/views (100% coverage target).
- Mock external APIs (responses_mock).

### 10.2 Integration Tests
- Test API endpoints with DRF test client.
- Rust: Cargo test.

### 10.3 Load Tests
- Locust for simulating 1,000 users.

### 10.4 CI/CD
- GitHub Actions: Run tests on PRs, deploy on merge.

## 11. Deployment
### 11.1 Environment Setup
- .env for secrets (OPENAI_KEY, SUPABASE_URL).
- Docker Compose for local: Services for Django, Redis, Celery, Rust, Supabase (local emulation).

### 11.2 Production Deployment
- Platform: Render (Django), AWS ECS/Lambda (Rust).
- Steps:
  1. Build Docker images.
  2. Deploy with env vars.
  3. Set up domain/SSL.
  4. Monitoring: Prometheus/Grafana.
- Blue-Green: For zero-downtime updates.

### 11.3 Maintenance
- Backups: Supabase daily snapshots.
- Updates: Semantic versioning for APIs.

## 12. Appendices
### 12.1 Code Standards
- PEP8 compliant.
- Type Hints: Use mypy.
- Commit Messages: Conventional Commits.

### 12.2 Dependencies
- requirements.txt: django, djangorestframework, celery, redis, openai, pygithub, grpcio, etc.
- Rust: Cargo.toml with dependencies.

This document is exhaustive; implement sequentially per Implementation Plan phases. Contact lead for clarifications.

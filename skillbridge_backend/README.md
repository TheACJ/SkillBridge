# SkillBridge Backend

A comprehensive Django REST API backend for the SkillBridge platform, featuring AI-powered learning roadmaps, intelligent mentor matching, and community-driven education.

## 🚀 Features

- **AI-Powered Roadmaps**: OpenAI GPT-4 integration for personalized learning paths
- **Intelligent Matching**: Rust microservice for high-performance mentor-learner matching
- **GitHub Integration**: Real-time progress tracking via webhooks
- **Community Forum**: Threaded discussions with category-based organization
- **Gamification**: Badge system with automated awarding
- **Real-time Notifications**: WebSocket-ready notification system
- **Security First**: JWT authentication, rate limiting, and comprehensive security measures

## 🏗️ Architecture

### Tech Stack
- **Framework**: Django 4.2 + Django REST Framework
- **Database**: PostgreSQL (production) / SQLite (development)
- **Authentication**: JWT with django-rest-framework-simplejwt
- **Caching**: Redis for session and data caching
- **Background Tasks**: Celery with Redis broker
- **Microservices**: Rust service for matching algorithm
- **External APIs**: OpenAI GPT-4, GitHub API

### Microservices
- **Django API**: Main REST API server
- **Rust Matching Service**: High-performance mentor matching algorithm
- **Redis**: Caching and session storage
- **PostgreSQL**: Primary data storage

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Rust 1.70+ (for microservice)
- Docker & Docker Compose (recommended)

## 🚀 Quick Start

### Development Setup

1. **Clone and setup:**
```bash
git clone <repository-url>
cd skillbridge_backend
```

2. **Environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Docker development:**
```bash
docker-compose up --build
```

4. **Manual setup:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Rust Microservice

```bash
cd ../skillbridge_rust
cargo build --release
cargo run
```

## 📚 API Documentation

### Authentication
```bash
# Register
POST /api/v1/users/register/
{
  "email": "user@example.com",
  "password": "securepass123",
  "role": "learner"
}

# Login
POST /api/v1/auth/token/
{
  "email": "user@example.com",
  "password": "securepass123"
}
```

### Core Endpoints

#### Roadmaps
- `GET /api/v1/roadmaps/` - List user roadmaps
- `POST /api/v1/roadmaps/` - Create roadmap
- `POST /api/v1/roadmaps/generate/` - AI-generated roadmap
- `PATCH /api/v1/roadmaps/{id}/` - Update roadmap

#### Mentor Matching
- `GET /api/v1/matches/` - List user matches
- `POST /api/v1/matches/` - Request mentor match
- `PATCH /api/v1/matches/{id}/` - Update match status

#### Progress Tracking
- `POST /api/v1/progress/github/webhook/` - GitHub webhook
- `GET /api/v1/progress/github/repositories/` - User repositories

#### Community
- `GET /api/v1/forum/posts/` - List forum posts
- `POST /api/v1/forum/posts/` - Create forum post

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific app tests
pytest users/tests.py

# Run Django tests
python manage.py test
```

## 🔒 Security

- JWT authentication with refresh token rotation
- Rate limiting (100/hour anonymous, 1000/hour authenticated)
- CORS configuration for frontend domains
- Input validation and sanitization
- SQL injection prevention via Django ORM
- XSS protection and CSRF tokens
- Security headers (HSTS, CSP, etc.)

## 🚀 Deployment

### Production Checklist
- [ ] Set `DEBUG=False`
- [ ] Configure production database (PostgreSQL)
- [ ] Set secure `SECRET_KEY`
- [ ] Configure Redis for caching
- [ ] Set up SSL/TLS certificates
- [ ] Configure CORS for production domains
- [ ] Set up monitoring and logging
- [ ] Configure backup strategies

### Docker Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables
```bash
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=your-production-secret
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379
OPENAI_API_KEY=your-openai-key
GITHUB_WEBHOOK_SECRET=your-webhook-secret
```

## 📊 Monitoring

- **Health Checks**: `/api/v1/health/`
- **Metrics**: Integrated logging and error tracking
- **Performance**: Database query optimization
- **Security**: Audit logging for sensitive operations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### Code Standards
- PEP 8 compliance
- Type hints for all functions
- Comprehensive docstrings
- 80%+ test coverage

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review existing issues and solutions

## 🗺️ Roadmap

- [ ] Real-time chat system
- [ ] Video call integration
- [ ] Advanced analytics dashboard
- [ ] Mobile app API optimization
- [ ] Multi-language support
- [ ] Advanced AI recommendations
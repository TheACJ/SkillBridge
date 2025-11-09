# SkillBridge Backend

A comprehensive mentorship platform backend built with Django REST Framework, featuring AI-powered roadmap generation, mentor matching, progress tracking, and gamification.

## 🚀 Features

- **AI-Powered Roadmaps**: Generate personalized learning paths using OpenAI GPT
- **Smart Mentor Matching**: Rust-based algorithm for optimal mentor-mentee pairing
- **Progress Tracking**: GitHub integration for automatic progress monitoring
- **Gamification**: Badges, achievements, and leaderboards
- **Real-time Communication**: Forum discussions and chat functionality
- **Comprehensive API**: RESTful API with OpenAPI documentation

## 🏗️ Architecture

### Tech Stack
- **Backend**: Django 4.2 + Django REST Framework 3.14
- **Database**: PostgreSQL with advanced indexing and triggers
- **Cache**: Redis for session and data caching
- **Message Queue**: Celery with Redis broker
- **Matching Engine**: Rust microservice for high-performance algorithms
- **Monitoring**: Prometheus + Grafana + Loki
- **Deployment**: Docker + Nginx + Gunicorn

### Services
- **Django API**: Main application server
- **Rust Service**: Mentor matching algorithms
- **PostgreSQL**: Primary database
- **Redis**: Cache and message broker
- **Celery**: Background task processing
- **Nginx**: Load balancer and reverse proxy

## 📋 Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+
- Rust 1.70+ (for matching service)

## 🚀 Quick Start

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/skillbridge-backend.git
   cd skillbridge-backend
   ```

2. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start Services**
   ```bash
   docker-compose up -d
   ```

4. **Run Migrations**
   ```bash
   docker-compose exec django python manage.py migrate
   ```

5. **Create Superuser**
   ```bash
   docker-compose exec django python manage.py createsuperuser
   ```

### Production Deployment

1. **Build Production Images**
   ```bash
   docker-compose -f docker-compose.prod.yml build
   ```

2. **Deploy**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Setup Monitoring**
   ```bash
   ./scripts/monitoring-setup.sh
   ```

## 📖 API Documentation

### Authentication
The API uses JWT (JSON Web Tokens) for authentication.

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### Core Endpoints

- `GET /api/v1/users/` - List mentors
- `POST /api/v1/roadmaps/` - Generate AI roadmap
- `GET /api/v1/matches/` - View mentor matches
- `POST /api/v1/progress/` - Log progress
- `GET /api/v1/badges/` - View earned badges

### OpenAPI Specification
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI JSON**: http://localhost:8000/api/schema/

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_SETTINGS_MODULE` | Django settings module | `skillbridge_backend.settings.production` |
| `DATABASE_URL` | PostgreSQL connection URL | Required |
| `REDIS_URL` | Redis connection URL | `redis://redis:6379/0` |
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `GITHUB_CLIENT_ID` | GitHub OAuth client ID | Required |
| `SECRET_KEY` | Django secret key | Required |

### Settings Files

- `settings/base.py` - Base configuration
- `settings/development.py` - Development settings
- `settings/production.py` - Production settings

## 🧪 Testing

### Run Tests
```bash
# Unit tests
python manage.py test

# With coverage
coverage run --source='.' manage.py test
coverage report

# Integration tests
python manage.py test --tag=integration
```

### Performance Testing
```bash
# Load testing with locust
locust -f tests/locustfile.py --headless -u 100 -r 10
```

## 📊 Monitoring

### Access URLs
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000
- **Alertmanager**: http://localhost:9093

### Key Metrics
- Application response times
- Error rates
- Database connection counts
- Cache hit rates
- Celery task success rates

## 🔄 Maintenance

### Automated Tasks
```bash
# Database backup
./scripts/backup.sh

# System maintenance
./scripts/maintenance.sh

# Monitoring setup
./scripts/monitoring-setup.sh
```

### Manual Maintenance
```bash
# Clear expired sessions
python manage.py clearsessions

# Update database statistics
python manage.py update_database_stats

# Rebuild search indexes
python manage.py rebuild_index
```

## 🚀 Deployment

### CI/CD Pipeline
The project uses GitHub Actions for automated:
- Testing and linting
- Security scanning
- Docker image building
- Deployment to staging/production

### Manual Deployment
```bash
# Deploy to staging
./.github/workflows/deploy.yml --environment staging

# Deploy to production
./.github/workflows/deploy.yml --environment production

# Rollback
./.github/workflows/rollback.yml --environment production
```

## 🔒 Security

### Features
- JWT authentication with refresh tokens
- Rate limiting and throttling
- Input sanitization with bleach
- CSRF protection
- Security headers middleware
- Audit logging

### Best Practices
- Regular dependency updates
- Security scanning with `safety`
- Log monitoring and alerting
- Database encryption for sensitive data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Development Guidelines
- Follow PEP 8 style guide
- Write comprehensive tests
- Update documentation
- Use type hints
- Keep commits atomic

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-org/skillbridge-backend/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/skillbridge-backend/discussions)
- **Documentation**: [Wiki](https://github.com/your-org/skillbridge-backend/wiki)

## 🙏 Acknowledgments

- Django REST Framework community
- OpenAI for GPT integration
- PostgreSQL and Redis teams
- All contributors and users
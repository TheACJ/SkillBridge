# SkillBridge Deployment Guide

This guide covers the complete deployment process for SkillBridge backend in production environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Infrastructure Setup](#infrastructure-setup)
3. [Application Deployment](#application-deployment)
4. [Monitoring Setup](#monitoring-setup)
5. [Security Configuration](#security-configuration)
6. [Backup and Recovery](#backup-and-recovery)
7. [Scaling](#scaling)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **Server**: Ubuntu 20.04+ or CentOS 7+ with 4GB RAM minimum, 8GB recommended
- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+
- **Domain**: Registered domain with SSL certificate
- **SSL Certificate**: Let's Encrypt or commercial certificate

### Network Requirements

- **Inbound Ports**:
  - 80 (HTTP) - Redirect to HTTPS
  - 443 (HTTPS) - Main application
  - 22 (SSH) - Server access
- **Outbound**: Full internet access for API integrations

### External Services

- **PostgreSQL Database**: Version 15+
- **Redis Cache**: Version 7+
- **Email Service**: SMTP server or service (SendGrid, Mailgun, etc.)
- **GitHub OAuth App**: For repository integration
- **OpenAI API**: For roadmap generation

## Infrastructure Setup

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y curl wget git htop vim ufw

# Configure firewall
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

# Create application user
sudo useradd -m -s /bin/bash skillbridge
sudo usermod -aG docker skillbridge

# Configure SSH
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart sshd
```

### 2. Docker Installation

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo systemctl enable docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 3. SSL Certificate Setup

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate (replace yourdomain.com)
sudo certbot certonly --standalone -d yourdomain.com -d api.yourdomain.com

# Set up auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Application Deployment

### 1. Code Deployment

```bash
# Clone repository
sudo -u skillbridge git clone https://github.com/your-org/skillbridge-backend.git /home/skillbridge/app
cd /home/skillbridge/app

# Create environment file
sudo -u skillbridge cp .env.example .env
# Edit .env with production values
```

### 2. Environment Configuration

Create `/home/skillbridge/app/.env` with:

```bash
# Django Configuration
DJANGO_SETTINGS_MODULE=skillbridge_backend.settings.production
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=your-super-secret-key-here
DJANGO_ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com,localhost

# Database
DATABASE_URL=postgresql://skillbridge:db_password@db:5432/skillbridge

# Redis
REDIS_URL=redis://:redis_password@redis:6379/0
REDIS_PASSWORD=redis_password

# External Services
OPENAI_API_KEY=your-openai-api-key
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
SENTRY_DSN=your-sentry-dsn

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-app-password

# Security
SECRET_KEY=your-super-secret-key-here
```

### 3. Database Setup

```bash
# Start only database service first
docker-compose -f docker-compose.prod.yml up -d db

# Wait for database to be ready
sleep 30

# Create database and user
docker-compose -f docker-compose.prod.yml exec db psql -U postgres -c "
CREATE DATABASE skillbridge;
CREATE USER skillbridge WITH PASSWORD 'db_password';
GRANT ALL PRIVILEGES ON DATABASE skillbridge TO skillbridge;
"

# Run migrations
docker-compose -f docker-compose.prod.yml exec django python manage.py migrate

# Create superuser
docker-compose -f docker-compose.prod.yml exec django python manage.py createsuperuser
```

### 4. Full Deployment

```bash
# Build and start all services
docker-compose -f docker-compose.prod.yml up -d --build

# Check service status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f django
```

### 5. Nginx Configuration

Update `nginx/nginx.conf` with your domain:

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com api.yourdomain.com;

    # SSL certificates
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    # ... rest of configuration
}
```

## Monitoring Setup

### 1. Start Monitoring Stack

```bash
# Start monitoring services
docker-compose -f docker-compose.monitoring.yml up -d

# Run monitoring setup script
./scripts/monitoring-setup.sh
```

### 2. Configure Grafana

1. Access Grafana at `http://your-server:3000`
2. Change default password (admin/admin)
3. Add Prometheus data source: `http://prometheus:9090`
4. Import dashboards from `monitoring/grafana/dashboards/`

### 3. Alert Configuration

Update `monitoring/alertmanager.yml` with your notification channels:

```yaml
route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'slack'
  routes:
  - match:
      severity: critical
    receiver: 'pagerduty'

receivers:
- name: 'slack'
  slack_configs:
  - api_url: 'YOUR_SLACK_WEBHOOK_URL'
    channel: '#alerts'
    send_resolved: true
```

## Security Configuration

### 1. SSL/TLS Configuration

```bash
# Test SSL configuration
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com

# Check SSL rating
curl -s -I https://yourdomain.com | head -n 1
```

### 2. Security Headers

Verify security headers are set in Nginx configuration:

```bash
curl -I https://yourdomain.com
# Should include: X-Frame-Options, X-Content-Type-Options, X-XSS-Protection, etc.
```

### 3. Database Security

```sql
-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Create policies for data access
CREATE POLICY user_own_data ON users
    FOR ALL USING (auth.uid() = id);
```

### 4. Backup Encryption

```bash
# Generate encryption key
openssl rand -base64 32 > /home/skillbridge/backup_key

# Update backup script to use encryption
# Add: --encrypt AES256 --passphrase-file /home/skillbridge/backup_key
```

## Backup and Recovery

### 1. Automated Backups

```bash
# Make backup script executable
chmod +x scripts/backup.sh

# Setup cron job for daily backups
sudo crontab -e
# Add: 0 2 * * * /home/skillbridge/app/scripts/backup.sh
```

### 2. Backup Verification

```bash
# Test backup integrity
./scripts/backup.sh

# Verify latest backup
ls -la /home/skillbridge/backups/
pg_restore --list /home/skillbridge/backups/latest_backup.sql.gz
```

### 3. Disaster Recovery

```bash
# Stop application
docker-compose -f docker-compose.prod.yml down

# Restore database
pg_restore -d skillbridge /path/to/backup.sql.gz

# Restore media files
tar -xzf /path/to/media_backup.tar.gz -C /home/skillbridge/media/

# Restart application
docker-compose -f docker-compose.prod.yml up -d
```

## Scaling

### 1. Horizontal Scaling

```bash
# Scale Django application
docker-compose -f docker-compose.prod.yml up -d --scale django=3

# Scale Celery workers
docker-compose -f docker-compose.prod.yml up -d --scale celery=4
```

### 2. Database Scaling

```bash
# Add read replicas
# Update docker-compose.prod.yml with replica configuration
# Implement read/write splitting in Django settings
```

### 3. Load Balancing

Update Nginx configuration for multiple backend instances:

```nginx
upstream django_backend {
    least_conn;
    server django:8000;
    server django:8000;
    server django:8000;
    keepalive 32;
}
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Issues

```bash
# Check database connectivity
docker-compose -f docker-compose.prod.yml exec django python manage.py dbshell

# Verify connection string
docker-compose -f docker-compose.prod.yml exec django python manage.py shell -c "
import os
from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT version();')
print(cursor.fetchone())
"
```

#### 2. Application Not Starting

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs django

# Check Django settings
docker-compose -f docker-compose.prod.yml exec django python manage.py check --deploy

# Test application
docker-compose -f docker-compose.prod.yml exec django python manage.py shell -c "
import django
django.setup()
print('Django is working')
"
```

#### 3. High Memory Usage

```bash
# Check container resource usage
docker stats

# Monitor Django memory usage
docker-compose -f docker-compose.prod.yml exec django python manage.py shell -c "
import psutil
print(f'Memory usage: {psutil.virtual_memory().percent}%')
"
```

#### 4. Slow Performance

```bash
# Check database query performance
docker-compose -f docker-compose.prod.yml exec django python manage.py shell -c "
from django.db import connection
from django.core.cache import cache

# Check cache hit rate
print('Cache stats:', cache.get_stats() if hasattr(cache, 'get_stats') else 'N/A')

# Check slow queries
with connection.cursor() as cursor:
    cursor.execute('SELECT * FROM pg_stat_activity;')
    print('Active connections:', len(cursor.fetchall()))
"
```

### Log Analysis

```bash
# View application logs
docker-compose -f docker-compose.prod.yml logs -f django

# Search for errors
docker-compose -f docker-compose.prod.yml logs django | grep ERROR

# Monitor log volume
docker-compose -f docker-compose.prod.yml logs django | wc -l
```

### Health Checks

```bash
# Manual health check
curl -f https://yourdomain.com/api/v1/health/

# Check all services
docker-compose -f docker-compose.prod.yml ps

# Database health
docker-compose -f docker-compose.prod.yml exec db pg_isready -U skillbridge
```

## Maintenance Procedures

### Weekly Tasks

1. **Security Updates**
   ```bash
   # Update Docker images
   docker-compose -f docker-compose.prod.yml pull

   # Update system packages
   sudo apt update && sudo apt upgrade -y

   # Restart services
   docker-compose -f docker-compose.prod.yml up -d
   ```

2. **Log Rotation**
   ```bash
   ./scripts/maintenance.sh --only-logs
   ```

3. **Database Maintenance**
   ```bash
   ./scripts/maintenance.sh --only-database
   ```

### Monthly Tasks

1. **Full Backup Verification**
   ```bash
   ./scripts/backup.sh
   # Test restore procedure on separate instance
   ```

2. **Performance Review**
   ```bash
   # Review Grafana dashboards
   # Analyze slow queries
   # Check resource utilization
   ```

3. **Security Audit**
   ```bash
   # Run security scans
   # Review access logs
   # Update dependencies
   ```

## Support and Monitoring

### Monitoring Dashboards

- **Application Health**: Response times, error rates, throughput
- **System Resources**: CPU, memory, disk, network
- **Database Performance**: Connection counts, query times, lock waits
- **External Services**: API response times, failure rates

### Alert Response

1. **Critical Alerts**: Immediate response required
   - Service down
   - Database unavailable
   - High error rates (>10%)

2. **Warning Alerts**: Response within 1 hour
   - High resource usage
   - Slow response times
   - Failed background jobs

3. **Info Alerts**: Monitor and address as needed
   - Low disk space warnings
   - Certificate expiration warnings

### Escalation Procedures

1. Check monitoring dashboards
2. Review application logs
3. Check system resources
4. Restart affected services
5. Contact development team if needed
6. Implement rollback if necessary

---

For additional support, please refer to the [README.md](README.md) or create an issue in the project repository.
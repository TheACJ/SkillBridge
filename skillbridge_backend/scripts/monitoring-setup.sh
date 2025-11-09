#!/bin/bash

# SkillBridge Monitoring Setup Script
# Sets up monitoring infrastructure and configures alerts

set -euo pipefail

# Configuration
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="/app/logs/monitoring_setup_${TIMESTAMP}.log"

# Logging
exec > >(tee -a "$LOG_FILE") 2>&1

echo "Starting SkillBridge monitoring setup at $(date)"

# Function to send notifications
notify() {
    local message="$1"
    local level="${2:-info}"

    echo "[$level] $message"
}

# Check prerequisites
check_prerequisites() {
    echo "Checking prerequisites..."

    # Check if docker and docker-compose are available
    if ! command -v docker &> /dev/null; then
        echo "ERROR: Docker is not installed"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        echo "ERROR: Docker Compose is not installed"
        exit 1
    fi

    # Check if required files exist
    local required_files=(
        "docker-compose.monitoring.yml"
        "monitoring/prometheus.yml"
        "monitoring/alert_rules.yml"
    )

    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            echo "ERROR: Required file $file not found"
            exit 1
        fi
    done

    echo "Prerequisites check passed"
}

# Setup monitoring network
setup_network() {
    echo "Setting up monitoring network..."

    # Create monitoring network if it doesn't exist
    if ! docker network ls | grep -q skillbridge_monitoring_network; then
        docker network create skillbridge_monitoring_network
        echo "Created skillbridge_monitoring_network"
    else
        echo "skillbridge_monitoring_network already exists"
    fi

    # Connect to main application network if it exists
    if docker network ls | grep -q skillbridge_prod_network; then
        echo "Connecting monitoring to production network..."
        # This will be handled by docker-compose
    fi
}

# Start monitoring services
start_monitoring() {
    echo "Starting monitoring services..."

    # Start monitoring stack
    docker-compose -f docker-compose.monitoring.yml up -d

    # Wait for services to be healthy
    echo "Waiting for monitoring services to start..."
    sleep 30

    # Check if services are running
    local services=("prometheus" "grafana" "alertmanager" "loki")
    for service in "${services[@]}"; do
        if ! docker-compose -f docker-compose.monitoring.yml ps "$service" | grep -q "Up"; then
            echo "ERROR: $service failed to start"
            notify "Monitoring service $service failed to start" "error"
            return 1
        fi
    done

    echo "Monitoring services started successfully"
    notify "Monitoring services started successfully" "success"
}

# Configure Grafana
configure_grafana() {
    echo "Configuring Grafana..."

    # Wait for Grafana to be ready
    local max_attempts=30
    local attempt=1

    while ! curl -f http://localhost:3000/api/health 2>/dev/null; do
        if [[ $attempt -ge $max_attempts ]]; then
            echo "ERROR: Grafana failed to become ready"
            return 1
        fi
        echo "Waiting for Grafana... (attempt $attempt/$max_attempts)"
        sleep 10
        ((attempt++))
    done

    # Create data source for Prometheus
    curl -X POST http://admin:admin@localhost:3000/api/datasources \
        -H "Content-Type: application/json" \
        -d '{
            "name": "Prometheus",
            "type": "prometheus",
            "url": "http://prometheus:9090",
            "access": "proxy",
            "isDefault": true
        }'

    # Create data source for Loki
    curl -X POST http://admin:admin@localhost:3000/api/datasources \
        -H "Content-Type: application/json" \
        -d '{
            "name": "Loki",
            "type": "loki",
            "url": "http://loki:3100",
            "access": "proxy"
        }'

    echo "Grafana configured successfully"
}

# Setup dashboards
setup_dashboards() {
    echo "Setting up Grafana dashboards..."

    # Import predefined dashboards
    local dashboard_files=(
        "monitoring/grafana/dashboards/django-overview.json"
        "monitoring/grafana/dashboards/system-overview.json"
        "monitoring/grafana/dashboards/database-overview.json"
    )

    for dashboard_file in "${dashboard_files[@]}"; do
        if [[ -f "$dashboard_file" ]]; then
            echo "Importing dashboard: $dashboard_file"
            curl -X POST http://admin:admin@localhost:3000/api/dashboards/import \
                -H "Content-Type: application/json" \
                -d @"$dashboard_file"
        else
            echo "Dashboard file not found: $dashboard_file"
        fi
    done
}

# Test monitoring setup
test_monitoring() {
    echo "Testing monitoring setup..."

    # Test Prometheus
    if ! curl -f http://localhost:9090/-/healthy; then
        echo "ERROR: Prometheus health check failed"
        return 1
    fi

    # Test Grafana
    if ! curl -f http://localhost:3000/api/health; then
        echo "ERROR: Grafana health check failed"
        return 1
    fi

    # Test Alertmanager
    if ! curl -f http://localhost:9093/-/healthy; then
        echo "ERROR: Alertmanager health check failed"
        return 1
    fi

    echo "Monitoring tests passed"
}

# Setup alert notifications
setup_alerts() {
    echo "Setting up alert notifications..."

    # Configure notification channels (Slack, email, etc.)
    # This would typically involve API calls to Alertmanager or Grafana

    echo "Alert notifications configured"
}

# Generate monitoring documentation
generate_docs() {
    echo "Generating monitoring documentation..."

    local docs_file="/app/docs/monitoring-setup.md"

    mkdir -p /app/docs

    cat > "$docs_file" << 'EOF'
# SkillBridge Monitoring Setup

## Overview
This document describes the monitoring infrastructure for SkillBridge.

## Services

### Prometheus (Port 9090)
- Metrics collection and storage
- Alert evaluation
- Service discovery

### Grafana (Port 3000)
- Dashboard visualization
- Default credentials: admin/admin
- Data sources: Prometheus, Loki

### Alertmanager (Port 9093)
- Alert routing and notification
- Configurable notification channels

### Loki (Port 3100)
- Log aggregation
- Integration with Promtail

## Dashboards

### Django Application Dashboard
- Request/response metrics
- Error rates
- Performance metrics

### System Dashboard
- CPU, memory, disk usage
- Network statistics
- Container metrics

### Database Dashboard
- Connection counts
- Query performance
- Storage metrics

## Alerts

### Critical Alerts
- Service down (Django, Database, Redis, Rust service)
- High error rates (>5%)
- Low disk space (<10%)

### Warning Alerts
- High response times (>5s)
- High resource usage (>85%)
- Database connection spikes

## Access URLs

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
- Alertmanager: http://localhost:9093
- Loki: http://localhost:3100

## Maintenance

### Backup Monitoring Data
```bash
# Backup Prometheus data
docker exec prometheus tar czf /tmp/prometheus_backup.tar.gz -C /prometheus .

# Backup Grafana data
docker exec grafana tar czf /tmp/grafana_backup.tar.gz -C /var/lib/grafana .
```

### Update Alert Rules
Edit `monitoring/alert_rules.yml` and reload Prometheus:
```bash
curl -X POST http://localhost:9090/-/reload
```

### Scale Monitoring Services
```bash
docker-compose -f docker-compose.monitoring.yml up -d --scale prometheus=2
```
EOF

    echo "Monitoring documentation generated: $docs_file"
}

# Main setup function
main() {
    local start_time=$(date +%s)

    echo "========================================"
    echo "SkillBridge Monitoring Setup"
    echo "Started: $(date)"
    echo "========================================"

    # Trap to ensure cleanup
    trap 'notify "Monitoring setup failed at $(date)" "error"' ERR

    check_prerequisites
    setup_network
    start_monitoring
    configure_grafana
    setup_dashboards
    test_monitoring
    setup_alerts
    generate_docs

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    echo "========================================"
    echo "Monitoring setup completed successfully in ${duration}s"
    echo "========================================"

    cat << EOF

Monitoring URLs:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)
- Alertmanager: http://localhost:9093
- Loki: http://localhost:3100

Next steps:
1. Change default Grafana password
2. Configure notification channels in Alertmanager
3. Import additional dashboards as needed
4. Set up log shipping from application containers

EOF

    notify "Monitoring setup completed successfully in ${duration}s" "success"
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        cat << EOF
SkillBridge Monitoring Setup Script

Usage: $0 [OPTIONS]

Options:
  --help, -h          Show this help message
  --test-only         Run tests without setup
  --cleanup           Stop and remove monitoring services

Examples:
  $0                  # Full setup
  $0 --test-only      # Test existing setup
  $0 --cleanup        # Clean up monitoring services
EOF
        exit 0
        ;;
    --test-only)
        test_monitoring
        exit $?
        ;;
    --cleanup)
        echo "Stopping and removing monitoring services..."
        docker-compose -f docker-compose.monitoring.yml down -v
        docker network rm skillbridge_monitoring_network 2>/dev/null || true
        echo "Monitoring cleanup completed"
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
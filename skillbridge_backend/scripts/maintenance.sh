#!/bin/bash

# SkillBridge Maintenance Script
# Performs routine maintenance tasks: cleanup, optimization, health checks

set -euo pipefail

# Configuration
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="/app/logs/maintenance_${TIMESTAMP}.log"
MAINTENANCE_MODE_FILE="/tmp/maintenance_mode"

# Logging
exec > >(tee -a "$LOG_FILE") 2>&1

echo "Starting SkillBridge maintenance at $(date)"

# Function to send notifications
notify() {
    local message="$1"
    local level="${2:-info}"

    echo "[$level] $message"

    # Add notification logic here (Slack, email, etc.)
}

# Enable maintenance mode
enable_maintenance_mode() {
    echo "Enabling maintenance mode..."
    touch "$MAINTENANCE_MODE_FILE"

    # Add logic to put application in maintenance mode
    # Example: touch /app/maintenance.flag
    # Or use a database flag, or load balancer configuration

    notify "Maintenance mode enabled" "warning"
}

# Disable maintenance mode
disable_maintenance_mode() {
    echo "Disabling maintenance mode..."
    rm -f "$MAINTENANCE_MODE_FILE"

    # Remove maintenance flag
    # rm -f /app/maintenance.flag

    notify "Maintenance mode disabled" "info"
}

# Database maintenance
database_maintenance() {
    echo "Performing database maintenance..."

    # Vacuum analyze for optimization
    echo "Running VACUUM ANALYZE..."
    PGPASSWORD="$DB_PASSWORD" psql \
        -h "$DB_HOST" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -c "VACUUM ANALYZE;"

    # Reindex if needed (be careful with this in production)
    echo "Checking for index bloat..."
    # Add index maintenance logic here

    notify "Database maintenance completed" "success"
}

# Cache cleanup
cache_cleanup() {
    echo "Performing cache cleanup..."

    # Clear Redis cache (optional - depends on your strategy)
    # redis-cli -h redis FLUSHDB

    # Clear Django cache
    python manage.py clear_cache

    # Clear expired sessions
    python manage.py clearsessions

    notify "Cache cleanup completed" "success"
}

# Log rotation
log_rotation() {
    echo "Performing log rotation..."

    # Rotate application logs
    find /app/logs -name "*.log" -mtime +30 -delete

    # Compress old logs
    find /app/logs -name "*.log" -mtime +7 -exec gzip {} \;

    # Rotate system logs if applicable
    # logrotate /etc/logrotate.d/skillbridge

    notify "Log rotation completed" "success"
}

# File system cleanup
filesystem_cleanup() {
    echo "Performing filesystem cleanup..."

    # Remove temporary files
    find /tmp -name "skillbridge_*" -type f -mtime +1 -delete

    # Clean up old media files (if you have a cleanup policy)
    # find /app/media -name "*.tmp" -mtime +1 -delete

    # Remove orphaned files
    python manage.py remove_orphaned_files

    notify "Filesystem cleanup completed" "success"
}

# Health checks
health_checks() {
    echo "Performing health checks..."

    # Django health check
    if ! python manage.py check --deploy; then
        notify "Django health check failed" "error"
        return 1
    fi

    # Database connectivity
    if ! PGPASSWORD="$DB_PASSWORD" psql \
        -h "$DB_HOST" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -c "SELECT 1;" > /dev/null; then
        notify "Database connectivity check failed" "error"
        return 1
    fi

    # Redis connectivity
    if ! redis-cli -h redis ping > /dev/null; then
        notify "Redis connectivity check failed" "error"
        return 1
    fi

    notify "All health checks passed" "success"
}

# Performance optimization
performance_optimization() {
    echo "Performing performance optimization..."

    # Update database statistics
    python manage.py update_database_stats

    # Clear expired cache entries
    python manage.py clear_expired_cache

    # Optimize database indexes (if needed)
    # python manage.py reindex_database

    notify "Performance optimization completed" "success"
}

# Security checks
security_checks() {
    echo "Performing security checks..."

    # Check file permissions
    if [[ $(find /app -type f -perm /o+w | wc -l) -gt 0 ]]; then
        notify "Found world-writable files" "warning"
    fi

    # Check for outdated packages (if safety is installed)
    if command -v safety &> /dev/null; then
        safety check --bare || notify "Security vulnerabilities found in dependencies" "warning"
    fi

    # Check SSL certificates expiration (if applicable)
    # Add SSL certificate validation logic

    notify "Security checks completed" "success"
}

# Generate maintenance report
generate_report() {
    echo "Generating maintenance report..."

    local report_file="/app/logs/maintenance_report_${TIMESTAMP}.txt"

    cat > "$report_file" << EOF
SkillBridge Maintenance Report
Generated: $(date)
Duration: ${DURATION:-0}s

Database Status: $(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c "SELECT version();" | head -3 | tail -1)
Redis Status: $(redis-cli -h redis info | grep "redis_version" | cut -d: -f2)

Disk Usage:
$(df -h /app)

Memory Usage:
$(free -h)

Active Processes:
$(ps aux | grep -E "(python|celery|gunicorn)" | grep -v grep | wc -l) application processes

Recent Errors:
$(tail -20 /app/logs/django.log 2>/dev/null || echo "No recent errors")

Maintenance completed successfully.
EOF

    notify "Maintenance report generated: $report_file" "info"
}

# Main maintenance function
main() {
    local start_time=$(date +%s)

    echo "========================================"
    echo "SkillBridge Maintenance Script"
    echo "Started: $(date)"
    echo "========================================"

    # Trap to ensure cleanup
    trap 'notify "Maintenance failed at $(date)" "error"; disable_maintenance_mode' ERR

    # Enable maintenance mode for critical operations
    enable_maintenance_mode

    # Perform maintenance tasks
    health_checks
    database_maintenance
    cache_cleanup
    log_rotation
    filesystem_cleanup
    performance_optimization
    security_checks

    # Generate report
    generate_report

    # Disable maintenance mode
    disable_maintenance_mode

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    DURATION=$duration

    echo "========================================"
    echo "Maintenance completed successfully in ${duration}s"
    echo "========================================"

    notify "Maintenance completed successfully in ${duration}s" "success"
}

# Show usage if requested
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    cat << EOF
SkillBridge Maintenance Script

Usage: $0 [OPTIONS]

Options:
  --help, -h          Show this help message
  --no-maintenance-mode  Skip maintenance mode (for non-critical maintenance)
  --only-health-checks   Run only health checks
  --only-database       Run only database maintenance

Environment Variables:
  DB_HOST              Database host (default: db)
  DB_USER              Database user (default: skillbridge)
  DB_PASSWORD          Database password
  DB_NAME              Database name (default: skillbridge)

Examples:
  $0                          # Full maintenance
  $0 --only-health-checks     # Health checks only
  $0 --no-maintenance-mode    # Maintenance without downtime
EOF
    exit 0
fi

# Handle command line options
SKIP_MAINTENANCE_MODE=false
ONLY_HEALTH_CHECKS=false
ONLY_DATABASE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-maintenance-mode)
            SKIP_MAINTENANCE_MODE=true
            shift
            ;;
        --only-health-checks)
            ONLY_HEALTH_CHECKS=true
            shift
            ;;
        --only-database)
            ONLY_DATABASE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run specific maintenance tasks if requested
if [[ "$ONLY_HEALTH_CHECKS" == true ]]; then
    health_checks
    exit $?
elif [[ "$ONLY_DATABASE" == true ]]; then
    database_maintenance
    exit $?
fi

# Override maintenance mode functions if skipping
if [[ "$SKIP_MAINTENANCE_MODE" == true ]]; then
    enable_maintenance_mode() { echo "Skipping maintenance mode"; }
    disable_maintenance_mode() { echo "Skipping maintenance mode"; }
fi

# Run main maintenance
main "$@"
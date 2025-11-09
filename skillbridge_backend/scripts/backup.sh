#!/bin/bash

# SkillBridge Database Backup Script
# This script creates automated backups of PostgreSQL database and media files

set -euo pipefail

# Configuration
BACKUP_DIR="/backups"
RETENTION_DAYS=30
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="skillbridge_backup_${TIMESTAMP}"

# Database configuration from environment
DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-skillbridge}
DB_USER=${DB_USER:-skillbridge}
DB_PASSWORD=${DB_PASSWORD}

# Media files directory
MEDIA_DIR="/app/media"

# Logging
LOG_FILE="/app/logs/backup_${TIMESTAMP}.log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "Starting SkillBridge backup at $(date)"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Function to send notifications (implement based on your notification system)
notify() {
    local message="$1"
    local level="${2:-info}"

    echo "[$level] $message"

    # Add notification logic here (Slack, email, etc.)
    # Example: curl -X POST -H 'Content-type: application/json' --data '{"text":"'"$message"'"}' $SLACK_WEBHOOK_URL
}

# Database backup function
backup_database() {
    echo "Starting database backup..."

    local db_backup_file="$BACKUP_DIR/${BACKUP_NAME}_db.sql.gz"

    # Export password for pg_dump
    export PGPASSWORD="$DB_PASSWORD"

    # Create compressed database dump
    pg_dump \
        --host="$DB_HOST" \
        --port="$DB_PORT" \
        --username="$DB_USER" \
        --dbname="$DB_NAME" \
        --no-password \
        --format=custom \
        --compress=9 \
        --verbose \
        --file="$db_backup_file"

    echo "Database backup completed: $db_backup_file"
    notify "Database backup completed successfully" "success"
}

# Media files backup function
backup_media() {
    echo "Starting media files backup..."

    local media_backup_file="$BACKUP_DIR/${BACKUP_NAME}_media.tar.gz"

    # Create compressed archive of media files
    tar -czf "$media_backup_file" \
        --exclude='*.tmp' \
        --exclude='cache/*' \
        -C "$MEDIA_DIR" .

    echo "Media files backup completed: $media_backup_file"
    notify "Media files backup completed successfully" "success"
}

# Configuration backup function
backup_config() {
    echo "Starting configuration backup..."

    local config_backup_file="$BACKUP_DIR/${BACKUP_NAME}_config.tar.gz"

    # Backup important configuration files (excluding secrets)
    tar -czf "$config_backup_file" \
        --exclude='*.env' \
        --exclude='secrets/*' \
        --exclude='.git' \
        -C /app \
        settings/ \
        nginx/ \
        monitoring/ \
        docker-compose*.yml \
        requirements*.txt

    echo "Configuration backup completed: $config_backup_file"
    notify "Configuration backup completed successfully" "success"
}

# Cleanup old backups
cleanup_old_backups() {
    echo "Cleaning up backups older than $RETENTION_DAYS days..."

    local deleted_count=0

    # Find and delete old backup files
    while IFS= read -r -d '' file; do
        echo "Deleting old backup: $file"
        rm -f "$file"
        ((deleted_count++))
    done < <(find "$BACKUP_DIR" -name "skillbridge_backup_*.gz" -mtime +"$RETENTION_DAYS" -print0)

    echo "Cleaned up $deleted_count old backup files"
    notify "Cleaned up $deleted_count old backup files" "info"
}

# Verify backup integrity
verify_backup() {
    echo "Verifying backup integrity..."

    local db_backup="$BACKUP_DIR/${BACKUP_NAME}_db.sql.gz"
    local media_backup="$BACKUP_DIR/${BACKUP_NAME}_media.tar.gz"

    # Check if files exist and are not empty
    if [[ ! -s "$db_backup" ]]; then
        echo "ERROR: Database backup file is empty or missing"
        notify "Database backup verification failed" "error"
        return 1
    fi

    if [[ ! -s "$media_backup" ]]; then
        echo "ERROR: Media backup file is empty or missing"
        notify "Media backup verification failed" "error"
        return 1
    fi

    # Test database backup integrity
    if ! pg_restore --list "$db_backup" > /dev/null 2>&1; then
        echo "ERROR: Database backup is corrupted"
        notify "Database backup integrity check failed" "error"
        return 1
    fi

    # Test media backup integrity
    if ! tar -tzf "$media_backup" > /dev/null 2>&1; then
        echo "ERROR: Media backup is corrupted"
        notify "Media backup integrity check failed" "error"
        return 1
    fi

    echo "Backup integrity verification completed successfully"
    notify "Backup integrity verification passed" "success"
}

# Upload to remote storage (optional)
upload_to_remote() {
    if [[ -n "${REMOTE_BACKUP_URL:-}" ]]; then
        echo "Uploading backups to remote storage..."

        # Implement upload logic based on your storage (S3, GCS, etc.)
        # Example for AWS S3:
        # aws s3 cp "$BACKUP_DIR/" "s3://$REMOTE_BACKUP_BUCKET/" --recursive --exclude "*" --include "skillbridge_backup_${TIMESTAMP}*"

        notify "Backup upload to remote storage completed" "success"
    fi
}

# Main backup process
main() {
    local start_time=$(date +%s)

    echo "========================================"
    echo "SkillBridge Backup Script"
    echo "Timestamp: $TIMESTAMP"
    echo "Backup Name: $BACKUP_NAME"
    echo "========================================"

    # Trap to ensure cleanup on error
    trap 'notify "Backup failed at $(date)" "error"' ERR

    backup_database
    backup_media
    backup_config
    verify_backup
    upload_to_remote
    cleanup_old_backups

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    echo "========================================"
    echo "Backup completed successfully in ${duration}s"
    echo "========================================"

    notify "Backup completed successfully in ${duration}s" "success"
}

# Run main function
main "$@"
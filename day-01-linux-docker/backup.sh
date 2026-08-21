#!/usr/bin/env bash
# ==============================================================================
# TestGen AI Platform - Automated Linux Backup Script
# ==============================================================================
# Description : Archives application data, logs, or databases with compression,
#               checksum generation, logging, and automatic retention cleanup.
# ==============================================================================

set -euo pipefail

# Configuration defaults (can be overridden via CLI flags or env vars)
SOURCE_DIR="${SOURCE_DIR:-./data}"
BACKUP_DIR="${BACKUP_DIR:-./backups}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
LOG_FILE="${LOG_FILE:-}"
APP_NAME="testgen-ai"

# Function to display usage help
usage() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Options:
  -s, --source DIR        Source directory to backup (default: ${SOURCE_DIR})
  -b, --backup-dir DIR    Destination directory for backups (default: ${BACKUP_DIR})
  -r, --retention DAYS    Days to retain backup archives (default: ${RETENTION_DAYS})
  -h, --help              Show this help message and exit

Environment Variables:
  SOURCE_DIR, BACKUP_DIR, RETENTION_DAYS, LOG_FILE
EOF
    exit 0
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -s|--source)
            SOURCE_DIR="$2"
            shift 2
            ;;
        -b|--backup-dir)
            BACKUP_DIR="$2"
            shift 2
            ;;
        -r|--retention)
            RETENTION_DAYS="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage
            ;;
    esac
done

# Set default LOG_FILE if not explicitly provided
if [[ -z "${LOG_FILE}" ]]; then
    LOG_FILE="${BACKUP_DIR}/backup.log"
fi

# Ensure backup directory exists before writing logs
mkdir -p "${BACKUP_DIR}"

# Logging helper
log() {
    local level="$1"
    shift
    local msg="$*"
    local timestamp
    timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    echo "[${timestamp}] [${level}] ${msg}" | tee -a "${LOG_FILE}"
}

# Error handler
on_error() {
    local line_no=$1
    log "ERROR" "Backup failed at line ${line_no}. Check log output for details."
    exit 1
}
trap 'on_error ${LINENO}' ERR

log "INFO" "=================================================="
log "INFO" "Starting TestGen AI Platform Backup Process"
log "INFO" "=================================================="

# Validate source directory
if [[ ! -d "${SOURCE_DIR}" ]]; then
    log "ERROR" "Source directory '${SOURCE_DIR}' does not exist!"
    exit 1
fi

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
ARCHIVE_NAME="${APP_NAME}_backup_${TIMESTAMP}.tar.gz"
ARCHIVE_PATH="${BACKUP_DIR}/${ARCHIVE_NAME}"
CHECKSUM_PATH="${ARCHIVE_PATH}.sha256"

log "INFO" "Source Directory : ${SOURCE_DIR}"
log "INFO" "Backup Directory : ${BACKUP_DIR}"
log "INFO" "Target Archive   : ${ARCHIVE_PATH}"

# Create tar.gz archive
log "INFO" "Creating compressed backup archive..."
tar -czf "${ARCHIVE_PATH}" -C "${SOURCE_DIR}" .

# Generate SHA256 checksum for backup verification
log "INFO" "Generating SHA256 checksum..."
sha256sum "${ARCHIVE_PATH}" > "${CHECKSUM_PATH}"

ARCHIVE_SIZE=$(du -sh "${ARCHIVE_PATH}" | cut -f1)
log "INFO" "Backup archive created successfully. Size: ${ARCHIVE_SIZE}"

# Execute Retention Policy (delete archives older than RETENTION_DAYS)
log "INFO" "Applying retention policy (removing archives older than ${RETENTION_DAYS} days)..."
DELETED_COUNT=0
while IFS= read -r file; do
    if [[ -n "${file}" ]]; then
        log "INFO" "Removing old backup: ${file}"
        rm -f "${file}" "${file}.sha256"
        DELETED_COUNT=$((DELETED_COUNT + 1))
    fi
done < <(find "${BACKUP_DIR}" -maxdepth 1 -type f -name "${APP_NAME}_backup_*.tar.gz" -mtime +"${RETENTION_DAYS}")

log "INFO" "Retention cleanup completed. ${DELETED_COUNT} old backup(s) pruned."
log "INFO" "Backup process finished successfully!"
log "INFO" "=================================================="

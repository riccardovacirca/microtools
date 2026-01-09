#!/bin/bash
#
# Production Release Build Script
# Generates production-ready Docker images and distribution packages
#

set -euo pipefail

# =============================================================================
# Configuration
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DIST_DIR="${PROJECT_ROOT}/dist"

# Load project name from .env if exists
if [[ -f "${PROJECT_ROOT}/.env" ]]; then
    PROJECT_NAME=$(grep "^PROJECT_NAME=" "${PROJECT_ROOT}/.env" | cut -d'=' -f2)
else
    PROJECT_NAME="hola"
fi

# Version from argument or default
VERSION="${1:-v1.0.0}"
RELEASE_NAME="${PROJECT_NAME}-${VERSION}"
RELEASE_DIR="${DIST_DIR}/${RELEASE_NAME}"
BUILD_DATE="$(date -u +'%Y-%m-%d %H:%M:%S UTC')"

# Build options
SKIP_FRONTEND="${SKIP_FRONTEND:-false}"
SKIP_SERVICES="${SKIP_SERVICES:-false}"

# =============================================================================
# Utility Functions
# =============================================================================

info() { echo -e "\033[0;34m[INFO]\033[0m $*"; }
warn() { echo -e "\033[0;33m[WARN]\033[0m $*"; }
error() { echo -e "\033[0;31m[ERROR]\033[0m $*" >&2; exit 1; }
step() { echo -e "\n\033[1;36m==>\033[0m \033[1m$*\033[0m\n"; }

# =============================================================================
# Build Functions (Condensed)
# =============================================================================

build_frontend() {
    [[ "$SKIP_FRONTEND" == true ]] && { warn "Skipping frontend build"; return; }
    step "Building frontend..." && docker exec "$PROJECT_NAME" /workspace/bin/wa gui build || error "Frontend build failed"
}

build_services() {
    [[ "$SKIP_SERVICES" == true ]] && { warn "Skipping services build"; return; }
    step "Building C++ services..." && docker exec "$PROJECT_NAME" /workspace/bin/wa service build -n mod_status || warn "Service build failed (non-critical)"
}

validate_container() {
    step "Validating development container..."
    docker ps | grep -q "$PROJECT_NAME" || error "Development container '$PROJECT_NAME' is not running"
    info "Container validation passed"
}

# =============================================================================
# Docker Image Build
# =============================================================================

build_docker_image() {
    step "Building production Docker image: ${PROJECT_NAME}:${VERSION}..."

    docker build \
        -f "${SCRIPT_DIR}/Dockerfile.prod" \
        -t "${PROJECT_NAME}:${VERSION}" \
        -t "${PROJECT_NAME}:latest" \
        --build-arg VERSION="${VERSION}" \
        --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
        "${PROJECT_ROOT}" || error "Docker build failed"

    info "Docker image built successfully: ${PROJECT_NAME}:${VERSION}"
}

export_docker_image() {
    step "Exporting Docker image to TAR archive..."

    mkdir -p "$RELEASE_DIR"
    docker save "${PROJECT_NAME}:${VERSION}" | gzip > "${RELEASE_DIR}/${RELEASE_NAME}.tar.gz" || error "Docker export failed"

    local size=$(du -h "${RELEASE_DIR}/${RELEASE_NAME}.tar.gz" | cut -f1)
    info "Image exported: ${RELEASE_NAME}.tar.gz (${size})"
}

# =============================================================================
# Template Generation Functions
# =============================================================================

generate_install_script() {
    step "Generating install.sh..."

    sed -e "s/__PROJECT_NAME__/${PROJECT_NAME}/g" \
        -e "s/__VERSION__/${VERSION}/g" \
        -e "s/__RELEASE_NAME__/${RELEASE_NAME}/g" \
        "${SCRIPT_DIR}/install.sh.template" > "${RELEASE_DIR}/install.sh"

    chmod +x "${RELEASE_DIR}/install.sh"
    info "Generated: install.sh"
}

generate_readme() {
    step "Generating README.md..."

    sed -e "s/__PROJECT_NAME__/${PROJECT_NAME}/g" \
        -e "s/__VERSION__/${VERSION}/g" \
        -e "s/__RELEASE_NAME__/${RELEASE_NAME}/g" \
        -e "s/__BUILD_DATE__/${BUILD_DATE}/g" \
        "${SCRIPT_DIR}/readme.md.template" > "${RELEASE_DIR}/README.md"

    info "Generated: README.md"
}

generate_checksum() {
    step "Generating checksums..."

    cd "$RELEASE_DIR"
    shasum -a 256 "${RELEASE_NAME}.tar.gz" > SHA256SUMS
    info "Generated: SHA256SUMS"
    cd - >/dev/null
}

compress_release() {
    step "Compressing release directory..."

    cd "$DIST_DIR"
    tar -czf "${RELEASE_NAME}.tar.gz" "${RELEASE_NAME}/" || error "Compression failed"

    local size=$(du -h "${DIST_DIR}/${RELEASE_NAME}.tar.gz" | cut -f1)
    info "Release archive created: ${RELEASE_NAME}.tar.gz (${size})"
    cd - >/dev/null
}

# =============================================================================
# Main Workflow
# =============================================================================

main() {
    step "Starting production build: ${RELEASE_NAME}"

    # Validate environment
    validate_container

    # Build components
    build_frontend
    build_services

    # Build Docker image
    build_docker_image

    # Export and package
    export_docker_image
    generate_install_script
    generate_readme
    generate_checksum
    compress_release

    # Summary
    step "Build complete!"
    info "Release directory: ${RELEASE_DIR}/"
    info "Release archive: ${DIST_DIR}/${RELEASE_NAME}.tar.gz"
    info ""
    info "Directory contents:"
    ls -lh "$RELEASE_DIR" | tail -n +2 | awk '{printf "  - %s (%s)\n", $9, $5}'
    info ""
    info "Distribution files in ${DIST_DIR}/:"
    ls -lh "$DIST_DIR" | grep -E "${RELEASE_NAME}" | awk '{printf "  - %s (%s)\n", $9, $5}'
}

# =============================================================================
# Execute
# =============================================================================

main "$@"

#!/bin/bash
# ==============================================================================
# CI/CD Docker Image Tagging & Push Script
# Project: TestGen AI (Day 2 Docker Advanced)
# Description: Generates multi-tag strategy (SHA, Branch/Version, Date, Latest)
#              and optionally pushes to a Docker Registry / GitHub Container Registry.
# ==============================================================================

set -euo pipefail

# Configuration Defaults
IMAGE_NAME="${IMAGE_NAME:-testgen-ai}"
REGISTRY="${REGISTRY:-docker.io/myorg}"
DOCKERFILE="${DOCKERFILE:-day-02-docker-advanced/Dockerfile}"
BUILD_CONTEXT="${BUILD_CONTEXT:-.}"
DRY_RUN="${DRY_RUN:-false}"
PUSH="${PUSH:-false}"

# Colors for terminal output
RED='\030[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Starting Day 2 CI/CD Docker Tagging Script ===${NC}"

# Extract dynamic tag components
GIT_SHA=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null | tr '/' '-' || echo "main")
BUILD_DATE=$(date -u +'%Y%m%d-%H%M%S')
VERSION=$(cat package.json 2>/dev/null | grep '"version"' | head -n 1 | awk -F '"' '{print $4}' || echo "0.1.0")

FULL_IMAGE_NAME="${REGISTRY}/${IMAGE_NAME}"

# Define tag list
TAGS=(
    "${FULL_IMAGE_NAME}:${GIT_SHA}"
    "${FULL_IMAGE_NAME}:v${VERSION}"
    "${FULL_IMAGE_NAME}:${GIT_BRANCH}"
    "${FULL_IMAGE_NAME}:${BUILD_DATE}"
    "${FULL_IMAGE_NAME}:latest"
)

echo -e "\n${YELLOW}Target Tags to generate:${NC}"
for tag in "${TAGS[@]}"; do
    echo "  - ${tag}"
done

# Prepare docker build tag flags
BUILD_TAG_ARGS=""
for tag in "${TAGS[@]}"; do
    BUILD_TAG_ARGS="${BUILD_TAG_ARGS} -t ${tag}"
done

BUILD_CMD="docker build -f ${DOCKERFILE} ${BUILD_TAG_ARGS} ${BUILD_CONTEXT}"

echo -e "\n${BLUE}Executing Build Command:${NC}"
echo "${BUILD_CMD}"

if [ "${DRY_RUN}" = "true" ]; then
    echo -e "\n${GREEN}[DRY-RUN MODE] Build and Push commands simulated successfully.${NC}"
    exit 0
fi

# Execute Docker Build
eval "${BUILD_CMD}"

# Push Images if requested
if [ "${PUSH}" = "true" ]; then
    echo -e "\n${BLUE}Pushing tagged images to registry (${REGISTRY})...${NC}"
    for tag in "${TAGS[@]}"; do
        echo "Pushing ${tag}..."
        docker push "${tag}"
    done
    echo -e "${GREEN}All images pushed successfully!${NC}"
else
    echo -e "\n${YELLOW}[INFO] Skip push (Set PUSH=true to push images to registry).${NC}"
fi

echo -e "${GREEN}=== CI/CD Tagging completed successfully ===${NC}"

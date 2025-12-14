#!/bin/bash
# =============================================================================
# Manual Deployment Script
# Run this from your local machine to deploy to production
# Usage: bash scripts/deploy.sh
# =============================================================================

set -e

# Configuration - UPDATE THESE VALUES
SERVER_USER="deploy"
SERVER_HOST="YOUR_SERVER_IP"
APP_DIR="/opt/axon"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🚀 Starting deployment to ${SERVER_HOST}...${NC}"

# Check if we can connect to the server
echo -e "${YELLOW}📡 Testing connection...${NC}"
ssh -o ConnectTimeout=10 ${SERVER_USER}@${SERVER_HOST} "echo 'Connection successful'" || {
    echo -e "${RED}❌ Cannot connect to server${NC}"
    exit 1
}

# Deploy
echo -e "${YELLOW}📦 Deploying application...${NC}"
ssh ${SERVER_USER}@${SERVER_HOST} << 'ENDSSH'
    set -e
    cd /opt/axon
    
    echo "📥 Pulling latest changes..."
    git fetch origin main
    git reset --hard origin/main
    
    echo "🐳 Rebuilding containers..."
    docker compose -f docker-compose.prod.yml down
    docker compose -f docker-compose.prod.yml build --no-cache
    docker compose -f docker-compose.prod.yml up -d
    
    echo "🧹 Cleaning up..."
    docker image prune -f
    
    echo "📊 Container status:"
    docker compose -f docker-compose.prod.yml ps
ENDSSH

echo -e "${GREEN}✅ Deployment complete!${NC}"

# Health check
echo -e "${YELLOW}🏥 Running health check...${NC}"
sleep 5

ssh ${SERVER_USER}@${SERVER_HOST} "curl -s http://localhost:8000/health" && \
    echo -e "\n${GREEN}✅ Backend is healthy${NC}" || \
    echo -e "\n${RED}❌ Backend health check failed${NC}"

echo ""
echo -e "${GREEN}🎉 Deployment finished!${NC}"


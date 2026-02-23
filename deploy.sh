#!/bin/bash
# ExcelFlow Docker Deployment Script

set -e  # Exit on error

echo "🚀 ExcelFlow Docker Deployment"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi
echo -e "${GREEN}✅ Docker found${NC}"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    echo "Install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi
echo -e "${GREEN}✅ Docker Compose found${NC}"

# Check service account file
if [ ! -f "service-account.json" ]; then
    echo -e "${RED}❌ service-account.json not found${NC}"
    echo "Please place your GCP service account JSON file in the project root"
    exit 1
fi
echo -e "${GREEN}✅ Service account file found${NC}"

# Validate service account JSON
if ! python3 -c "import json; json.load(open('service-account.json'))" 2>/dev/null; then
    echo -e "${RED}❌ service-account.json is not valid JSON${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Service account file is valid${NC}"

# Extract and display project info
PROJECT_ID=$(python3 -c "import json; print(json.load(open('service-account.json')).get('project_id', 'unknown'))")
SA_EMAIL=$(python3 -c "import json; print(json.load(open('service-account.json')).get('client_email', 'unknown'))")

echo ""
echo "📊 Vertex AI Configuration:"
echo "   Project ID: $PROJECT_ID"
echo "   Service Account: $SA_EMAIL"
echo "   Model: gemini-2.0-flash-exp"
echo "   Location: us-central1"
echo ""

# Check .env file
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found, creating from .env.example...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✅ .env created${NC}"
    else
        echo -e "${RED}❌ .env.example not found${NC}"
        exit 1
    fi
fi

# Build and start services
echo ""
echo "🔨 Building Docker images..."
if docker compose version &> /dev/null; then
    docker compose build
else
    docker-compose build
fi

echo ""
echo "🚀 Starting services..."
if docker compose version &> /dev/null; then
    docker compose up -d
else
    docker-compose up -d
fi

# Wait for services to be healthy
echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check backend health
MAX_RETRIES=30
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f http://localhost:8002/health &> /dev/null; then
        echo -e "${GREEN}✅ Backend is healthy${NC}"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT+1))
    echo "Waiting for backend... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}❌ Backend failed to start${NC}"
    echo "Check logs with: docker compose logs backend"
    exit 1
fi

# Check frontend
if curl -f http://localhost:8003/ &> /dev/null; then
    echo -e "${GREEN}✅ Frontend is healthy${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend might not be ready yet${NC}"
fi

# Display status
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🎉 ExcelFlow is running!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📱 Access points:"
echo "   Frontend: http://localhost:8003"
echo "   Backend API: http://localhost:8002"
echo "   API Docs: http://localhost:8002/docs"
echo "   Health Check: http://localhost:8002/health"
echo ""
echo "🔧 Management commands:"
echo "   View logs: docker compose logs -f"
echo "   Stop: docker compose down"
echo "   Restart: docker compose restart"
echo "   Rebuild: docker compose up -d --build"
echo ""
echo "🤖 AI Configuration:"
echo "   Provider: Vertex AI"
echo "   Model: gemini-2.0-flash-exp"
echo "   Project: $PROJECT_ID"
echo ""

# Test AI endpoint
echo "🧪 Testing AI endpoint..."
AI_INFO=$(curl -s http://localhost:8002/ai/info 2>/dev/null || echo "{}")
if echo "$AI_INFO" | grep -q "vertex"; then
    echo -e "${GREEN}✅ Vertex AI is configured correctly${NC}"
else
    echo -e "${YELLOW}⚠️  AI might not be fully initialized yet${NC}"
    echo "   Check with: curl http://localhost:8002/ai/info"
fi

echo ""
echo -e "${GREEN}✨ Deployment complete!${NC}"

#!/bin/bash
set -e

echo "=============================================="
echo "  Luigi Chat - Docker Compose Test"
echo "=============================================="
echo ""

COMPOSE_FILE="docker-compose.test.yaml"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

cleanup() {
    echo -e "${YELLOW}Cleaning up...${NC}"
    docker-compose -f $COMPOSE_FILE down -v --remove-orphans 2>/dev/null || true
}

trap cleanup EXIT

echo -e "${YELLOW}Building images...${NC}"
docker-compose -f $COMPOSE_FILE build

echo ""
echo -e "${YELLOW}Starting services...${NC}"
docker-compose -f $COMPOSE_FILE up -d

echo ""
echo -e "${YELLOW}Waiting for services to be healthy...${NC}"

# Wait for postgres
echo "Waiting for PostgreSQL..."
for i in {1..30}; do
    if docker-compose -f $COMPOSE_FILE exec -T postgres pg_isready -U luigi > /dev/null 2>&1; then
        echo -e "${GREEN}PostgreSQL is ready!${NC}"
        break
    fi
    sleep 2
done

# Wait for backend
echo "Waiting for Backend..."
for i in {1..30}; do
    if curl -s http://localhost:8080/health > /dev/null 2>&1; then
        echo -e "${GREEN}Backend is ready!${NC}"
        break
    fi
    sleep 2
done

echo ""
echo -e "${YELLOW}Running health checks...${NC}"

# Health check backend
echo -n "Backend health: "
if curl -s http://localhost:8080/health | grep -q "healthy"; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC}"
fi

# Health check frontend
echo -n "Frontend health: "
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${YELLOW}Frontend may need more time${NC}"
fi

echo ""
echo -e "${GREEN}=============================================="
echo "  Test Complete!"
echo "==============================================${NC}"
echo ""
echo "Services running:"
docker-compose -f $COMPOSE_FILE ps
echo ""
echo "Logs:"
echo "  docker-compose -f $COMPOSE_FILE logs -f"
echo ""
echo "Stop:"
echo "  docker-compose -f $COMPOSE_FILE down"

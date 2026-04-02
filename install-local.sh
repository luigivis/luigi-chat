#!/bin/bash

set -e

echo "=============================================="
echo "  Luigi Chat - Local Development Setup"
echo "=============================================="
echo ""
echo "This script sets up Luigi Chat for local development."
echo "It uses local code instead of pre-built Docker images."
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Default values
DEFAULT_POSTGRES_USER="luigi"
DEFAULT_POSTGRES_DB="luigi_chat"
DEFAULT_REDIS_PASSWORD=$(openssl rand -base64 24)

# Questions
echo "=============================================="
echo "  PostgreSQL Configuration"
echo "=============================================="
echo ""
read -p "PostgreSQL username [$DEFAULT_POSTGRES_USER]: " POSTGRES_USER
POSTGRES_USER=${POSTGRES_USER:-$DEFAULT_POSTGRES_USER}

read -p "PostgreSQL database name [$DEFAULT_POSTGRES_DB]: " POSTGRES_DB
POSTGRES_DB=${POSTGRES_DB:-$DEFAULT_POSTGRES_DB}

read -p "PostgreSQL password [$DEFAULT_REDIS_PASSWORD]: " POSTGRES_PASSWORD
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-$DEFAULT_REDIS_PASSWORD}

REDIS_PASSWORD=$POSTGRES_PASSWORD

echo ""
echo "=============================================="
echo "  LiteLLM & MiniMax Configuration"
echo "=============================================="
echo ""
read -p "LiteLLM Master Key (sk-...): " LITELLM_MASTER_KEY
while [ -z "$LITELLM_MASTER_KEY" ]; do
    echo "${RED}LiteLLM Master Key is required${NC}"
    read -p "LiteLLM Master Key (sk-...): " LITELLM_MASTER_KEY
done

echo ""
read -p "MiniMax API Key: " MINIMAX_API_KEY
while [ -z "$MINIMAX_API_KEY" ]; do
    echo "${RED}MiniMax API Key is required${NC}"
    read -p "MiniMax API Key: " MINIMAX_API_KEY
done

echo ""
echo "=============================================="
echo "  Admin User Configuration"
echo "=============================================="
echo ""
read -p "Admin email [admin@example.com]: " ADMIN_EMAIL
ADMIN_EMAIL=${ADMIN_EMAIL:-admin@example.com}

read -p "Admin password: " ADMIN_PASSWORD
while [ -z "$ADMIN_PASSWORD" ]; do
    echo "${RED}Admin password cannot be empty${NC}"
    read -p "Admin password: " ADMIN_PASSWORD
done

echo ""
echo "=============================================="
echo "  Configuration Summary"
echo "=============================================="
echo ""
echo "PostgreSQL:"
echo "  User:     $POSTGRES_USER"
echo "  Database: $POSTGRES_DB"
echo "  Password: ${POSTGRES_PASSWORD:0:4}****"
echo ""
echo "Redis:"
echo "  Password: ${REDIS_PASSWORD:0:4}****"
echo ""
echo "Admin:"
echo "  Email:    $ADMIN_EMAIL"
echo "  Password: ${ADMIN_PASSWORD:0:4}****"
echo ""

read -p "Proceed with installation? [y/N]: " CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    exit 0
fi

# Create scripts directory
echo ""
echo "Creating scripts directory..."
mkdir -p scripts

# Create PostgreSQL init script
echo "Creating PostgreSQL init script..."
cat > scripts/init-postgres.sh << 'EOF'
#!/bin/bash
set -e

# Create LiteLLM database if it doesn't exist
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    SELECT 'CREATE DATABASE luigi' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'luigi');
    CREATE DATABASE luigi;
EOSQL
EOF

chmod +x scripts/init-postgres.sh

# Create .env file
echo ""
echo "Creating .env file..."
cat > .env << EOF
# ================================================
# Luigi Chat - Local Development Environment
# ================================================

# System
WEBUI_NAME="Luigi Chat (Dev)"
SECRET_KEY=dev-secret-change-in-production

# PostgreSQL
DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/${POSTGRES_DB}
POSTGRES_USER=${POSTGRES_USER}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_DB=${POSTGRES_DB}

# Redis
REDIS_URL=redis://:${REDIS_PASSWORD}@localhost:6379/0
REDIS_PASSWORD=${REDIS_PASSWORD}

# LiteLLM
LITELLM_MASTER_KEY=${LITELLM_MASTER_KEY}
LITELLM_DROP_PARAMS=true
LITELLM_MAX_PARALLEL_REQUESTS=100

# MiniMax
MINIMAX_API_KEY=${MINIMAX_API_KEY}
MINIMAX_API_BASE_URL=https://api.minimax.io

# Admin
ADMIN_USERNAME=${POSTGRES_USER}
ADMIN_EMAIL=${ADMIN_EMAIL}
ADMIN_PASSWORD=${ADMIN_PASSWORD}

# Rate Limits
DEFAULT_RPM_LIMIT=3
DEFAULT_TPM_LIMIT=6000

# Frontend
VITE_PUBLIC_API_URL=http://localhost:8080
EOF

# Create docker-compose.local.yaml
echo ""
echo "Creating docker-compose.local.yaml..."
cat > docker-compose.local.yaml << EOF
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-postgres.sh:/docker-entrypoint-initdb.d/init-luigi-db.sh:ro
    ports:
      - "5432:5432"
    networks:
      - luigi-local

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - luigi-local

  litellm:
    build:
      context: ./litellm
      dockerfile: Dockerfile
    ports:
      - "4000:4000"
    environment:
      LITELLM_MASTER_KEY: ${LITELLM_MASTER_KEY}
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/luigi
      REDIS_HOST: redis
      REDIS_PASSWORD: ${REDIS_PASSWORD}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./litellm/config.yaml:/app/config.yaml
    networks:
      - luigi-local

networks:
  luigi-local:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
EOF

# Create Docker network
echo ""
echo "Creating Docker network..."
docker network create luigi-local 2>/dev/null || echo "Network already exists"

# Start database services
echo ""
echo "=============================================="
echo "${GREEN}Starting Database Services${NC}"
echo "=============================================="
echo ""
docker-compose -f docker-compose.local.yaml up -d postgres redis

echo ""
echo "Waiting for PostgreSQL to be ready..."
sleep 5

# Check if PostgreSQL is ready
for i in {1..30}; do
    if docker-compose -f docker-compose.local.yaml exec -T postgres pg_isready -U ${POSTGRES_USER} > /dev/null 2>&1; then
        echo "PostgreSQL is ready!"
        break
    fi
    echo "Waiting for PostgreSQL... ($i/30)"
    sleep 2
done

# Start LiteLLM
echo ""
echo "Starting LiteLLM..."
docker-compose -f docker-compose.local.yaml up -d litellm

echo ""
echo "=============================================="
echo "${GREEN}Database Services Started!${NC}"
echo "=============================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Start Backend (in another terminal):"
echo "   cd backend"
echo "   pip install -r requirements.txt"
echo "   uvicorn app.main:app --reload --port 8080"
echo ""
echo "2. Start Frontend (in another terminal):"
echo "   cd frontend"
echo "   npm install"
echo "   npm run dev"
echo ""
echo "3. Access the application:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8080"
echo "   - LiteLLM Proxy: http://localhost:4000"
echo "   - API Docs: http://localhost:8080/docs"
echo ""
echo "4. Or start everything with Docker:"
echo "   docker-compose -f docker-compose.local.yaml up"
echo ""
echo "Admin login:"
echo "  Email:    $ADMIN_EMAIL"
echo "  Password: $ADMIN_PASSWORD"
echo ""
echo "Configuration saved to:"
echo "  - .env"
echo "  - docker-compose.local.yaml"
echo "  - scripts/init-postgres.sh"
echo ""

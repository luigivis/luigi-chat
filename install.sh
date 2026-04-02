#!/bin/bash

set -e

echo "=============================================="
echo "  Luigi Chat - Installation Script"
echo "=============================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
DEFAULT_SYSTEM_NAME="Luigi Chat"
DEFAULT_POSTGRES_USER="luigi"
DEFAULT_POSTGRES_DB="luigi_chat"
DEFAULT_DOCKER_NETWORK="luigi-network"
DEFAULT_IMAGE_BACKEND="ghcr.io/luigivis/luigi-chat-backend:latest"
DEFAULT_IMAGE_FRONTEND="ghcr.io/luigivis/luigi-chat-frontend:latest"
DEFAULT_IMAGE_LITELLM="ghcr.io/luigivis/luigi-chat-litellm:latest"

# Questions
read -p "System name [$DEFAULT_SYSTEM_NAME]: " SYSTEM_NAME
SYSTEM_NAME=${SYSTEM_NAME:-$DEFAULT_SYSTEM_NAME}

echo ""
echo "=============================================="
echo "  PostgreSQL Configuration"
echo "=============================================="
echo ""
read -p "Do you want to use an existing PostgreSQL database? (y/N): " USE_EXISTING_POSTGRES

if [[ "$USE_EXISTING_POSTGRES" =~ ^[Yy]$ ]]; then
    echo ""
    echo "Enter your existing PostgreSQL connection string:"
    echo "Format: postgresql://user:password@host:port/database"
    read -p "PostgreSQL URL: " POSTGRES_URL
    USE_DOCKER_POSTGRES=false
else
    USE_DOCKER_POSTGRES=true
    echo ""
    read -p "PostgreSQL username [$DEFAULT_POSTGRES_USER]: " POSTGRES_USER
    POSTGRES_USER=${POSTGRES_USER:-$DEFAULT_POSTGRES_USER}

    read -p "PostgreSQL database name [$DEFAULT_POSTGRES_DB]: " POSTGRES_DB
    POSTGRES_DB=${POSTGRES_DB:-$DEFAULT_POSTGRES_DB}

    read -p "PostgreSQL password: " POSTGRES_PASSWORD
    while [ -z "$POSTGRES_PASSWORD" ]; do
        echo "${RED}Password cannot be empty${NC}"
        read -p "PostgreSQL password: " POSTGRES_PASSWORD
    done
fi

echo ""
echo "=============================================="
echo "  Redis Configuration"
echo "=============================================="
echo ""
read -p "Do you want to use an existing Redis server? (y/N): " USE_EXISTING_REDIS

if [[ "$USE_EXISTING_REDIS" =~ ^[Yy]$ ]]; then
    echo ""
    echo "Enter your existing Redis connection string:"
    echo "Format: redis://user:password@host:port/db"
    read -p "Redis URL: " REDIS_URL
    USE_DOCKER_REDIS=false
else
    USE_DOCKER_REDIS=true
    REDIS_PASSWORD=${POSTGRES_PASSWORD:-$(openssl rand -base64 24)}
fi

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
read -p "Admin username [$DEFAULT_POSTGRES_USER]: " ADMIN_USER
ADMIN_USER=${ADMIN_USER:-$DEFAULT_POSTGRES_USER}

read -p "Admin email [admin@example.com]: " ADMIN_EMAIL
ADMIN_EMAIL=${ADMIN_EMAIL:-admin@example.com}

read -p "Admin password: " ADMIN_PASSWORD
while [ -z "$ADMIN_PASSWORD" ]; do
    echo "${RED}Admin password cannot be empty${NC}"
    read -p "Admin password: " ADMIN_PASSWORD
done

echo ""
echo "=============================================="
echo "  Docker Configuration"
echo "=============================================="
echo ""
read -p "Docker network name [$DEFAULT_DOCKER_NETWORK]: " DOCKER_NETWORK
DOCKER_NETWORK=${DOCKER_NETWORK:-$DEFAULT_DOCKER_NETWORK}

echo ""
echo "Do you want to expose ports to host?"
echo "  ${GREEN}Y${NC} - Expose ports (access via localhost:3000, localhost:8080)"
echo "  ${YELLOW}n${NC} - No exposure (access only via internal network)"
read -p "Expose ports? [Y/n]: " EXPOSE_PORTS
EXPOSE_PORTS=${EXPOSE_PORTS:-Y}

echo ""
echo "=============================================="
echo "  Image Configuration"
echo "=============================================="
echo ""
read -p "Backend image URL [$DEFAULT_IMAGE_BACKEND]: " IMAGE_BACKEND
IMAGE_BACKEND=${IMAGE_BACKEND:-$DEFAULT_IMAGE_BACKEND}

read -p "Frontend image URL [$DEFAULT_IMAGE_FRONTEND]: " IMAGE_FRONTEND
IMAGE_FRONTEND=${IMAGE_FRONTEND:-$DEFAULT_IMAGE_FRONTEND}

read -p "LiteLLM image URL [$DEFAULT_IMAGE_LITELLM]: " IMAGE_LITELLM
IMAGE_LITELLM=${IMAGE_LITELLM:-$DEFAULT_IMAGE_LITELLM}

echo ""
echo "=============================================="
echo "  Configuration Summary"
echo "=============================================="
echo ""
echo "System Name:      $SYSTEM_NAME"
echo ""
echo "PostgreSQL:"
if [ "$USE_DOCKER_POSTGRES" = true ]; then
    echo "  Mode:           Docker (new)"
    echo "  User:           $POSTGRES_USER"
    echo "  Database:       $POSTGRES_DB"
    echo "  Password:       ${POSTGRES_PASSWORD:0:4}****"
else
    echo "  Mode:           Existing"
    echo "  URL:            ${POSTGRES_URL:0:20}****"
fi
echo ""
echo "Redis:"
if [ "$USE_DOCKER_REDIS" = true ]; then
    echo "  Mode:           Docker (new)"
else
    echo "  Mode:           Existing"
    echo "  URL:            ${REDIS_URL:0:20}****"
fi
echo ""
echo "Admin:"
echo "  Username:       $ADMIN_USER"
echo "  Email:          $ADMIN_EMAIL"
echo "  Password:       ${ADMIN_PASSWORD:0:4}****"
echo ""
echo "Docker:"
echo "  Network:        $DOCKER_NETWORK"
echo "  Expose Ports:  $EXPOSE_PORTS"
echo ""
echo "Images:"
echo "  Backend:        $IMAGE_BACKEND"
echo "  Frontend:       $IMAGE_FRONTEND"
echo "  LiteLLM:        $IMAGE_LITELLM"
echo ""

read -p "Proceed with installation? [y/N]: " CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    exit 0
fi

# Create .env file
echo ""
echo "Creating .env file..."
cat > .env << EOF
# ================================================
# Luigi Chat - Environment Configuration
# ================================================

# System
WEBUI_NAME="$SYSTEM_NAME"
SECRET_KEY=$(openssl rand -base64 32)

# PostgreSQL
EOF

if [ "$USE_DOCKER_POSTGRES" = true ]; then
    cat >> .env << EOF
DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
POSTGRES_USER=${POSTGRES_USER}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_DB=${POSTGRES_DB}
EOF
else
    echo "DATABASE_URL=${POSTGRES_URL}" >> .env
fi

cat >> .env << EOF

# Redis
EOF

if [ "$USE_DOCKER_REDIS" = true ]; then
    cat >> .env << EOF
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
REDIS_PASSWORD=${REDIS_PASSWORD}
EOF
else
    echo "REDIS_URL=${REDIS_URL}" >> .env
fi

cat >> .env << EOF

# LiteLLM
LITELLM_MASTER_KEY=${LITELLM_MASTER_KEY}
LITELLM_DROP_PARAMS=true
LITELLM_MAX_PARALLEL_REQUESTS=100

# MiniMax
MINIMAX_API_KEY=${MINIMAX_API_KEY}
MINIMAX_API_BASE_URL=https://api.minimax.io

# Admin
ADMIN_USERNAME=${ADMIN_USER}
ADMIN_EMAIL=${ADMIN_EMAIL}
ADMIN_PASSWORD=${ADMIN_PASSWORD}

# Rate Limits
DEFAULT_RPM_LIMIT=3
DEFAULT_TPM_LIMIT=6000

# Frontend
VITE_PUBLIC_API_URL=http://localhost:8080
EOF

# Create docker-compose override
echo ""
echo "Creating docker-compose.override.yaml..."

if [ "$USE_DOCKER_POSTGRES" = true ] && [ "$USE_DOCKER_REDIS" = true ]; then
    # Full local setup
    cat > docker-compose.override.yaml << EOF
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
    networks:
      - ${DOCKER_NETWORK}

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - ${DOCKER_NETWORK}

  litellm:
    image: ${IMAGE_LITELLM}
    volumes:
      - ./litellm:/app/config
    environment:
      LITELLM_MASTER_KEY: ${LITELLM_MASTER_KEY}
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      REDIS_HOST: redis
      REDIS_PASSWORD: ${REDIS_PASSWORD}
    depends_on:
      - postgres
      - redis
    networks:
      - ${DOCKER_NETWORK}
EOF
elif [ "$USE_DOCKER_POSTGRES" = true ]; then
    # Local postgres, external redis
    cat > docker-compose.override.yaml << EOF
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
    networks:
      - ${DOCKER_NETWORK}

  litellm:
    image: ${IMAGE_LITELLM}
    volumes:
      - ./litellm:/app/config
    environment:
      LITELLM_MASTER_KEY: ${LITELLM_MASTER_KEY}
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      REDIS_HOST: ${REDIS_URL#*@}
      REDIS_PASSWORD: ${REDIS_URL%%@*}
    depends_on:
      - postgres
    networks:
      - ${DOCKER_NETWORK}
EOF
elif [ "$USE_DOCKER_REDIS" = true ]; then
    # External postgres, local redis
    cat > docker-compose.override.yaml << EOF
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - ${DOCKER_NETWORK}

  litellm:
    image: ${IMAGE_LITELLM}
    volumes:
      - ./litellm:/app/config
    environment:
      LITELLM_MASTER_KEY: ${LITELLM_MASTER_KEY}
      DATABASE_URL: ${POSTGRES_URL}
      REDIS_HOST: redis
      REDIS_PASSWORD: ${REDIS_PASSWORD}
    depends_on:
      - redis
    networks:
      - ${DOCKER_NETWORK}
EOF
else
    # Both external
    cat > docker-compose.override.yaml << EOF
version: '3.8'

services:
  litellm:
    image: ${IMAGE_LITELLM}
    volumes:
      - ./litellm:/app/config
    environment:
      LITELLM_MASTER_KEY: ${LITELLM_MASTER_KEY}
      DATABASE_URL: ${POSTGRES_URL}
      REDIS_URL: ${REDIS_URL}
    networks:
      - ${DOCKER_NETWORK}
EOF
fi

# Add backend and frontend with or without port exposure
if [[ "$EXPOSE_PORTS" =~ ^[Yy]$ ]]; then
    cat >> docker-compose.override.yaml << EOF

  backend:
    image: ${IMAGE_BACKEND}
    environment:
      DATABASE_URL: ${USE_DOCKER_POSTGRES:+postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}}
      REDIS_URL: ${USE_DOCKER_REDIS:+redis://:${REDIS_PASSWORD}@redis:6379/0}
      MINIMAX_API_KEY: ${MINIMAX_API_KEY}
      SECRET_KEY: $(openssl rand -base64 32 | tr -d '/+=')
      WEBUI_NAME: ${SYSTEM_NAME}
      ADMIN_EMAIL: ${ADMIN_EMAIL}
      ADMIN_PASSWORD: ${ADMIN_PASSWORD}
      LITELLM_MASTER_KEY: ${LITELLM_MASTER_KEY}
    ports:
      - "8080:8080"
    depends_on:
      - postgres
      - redis
      - litellm
    networks:
      - ${DOCKER_NETWORK}

  frontend:
    image: ${IMAGE_FRONTEND}
    ports:
      - "3000:3000"
    depends_on:
      - backend
    networks:
      - ${DOCKER_NETWORK}
EOF
else
    cat >> docker-compose.override.yaml << EOF

  backend:
    image: ${IMAGE_BACKEND}
    environment:
      DATABASE_URL: ${USE_DOCKER_POSTGRES:+postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}}
      REDIS_URL: ${USE_DOCKER_REDIS:+redis://:${REDIS_PASSWORD}@redis:6379/0}
      MINIMAX_API_KEY: ${MINIMAX_API_KEY}
      SECRET_KEY: $(openssl rand -base64 32 | tr -d '/+=')
      WEBUI_NAME: ${SYSTEM_NAME}
      ADMIN_EMAIL: ${ADMIN_EMAIL}
      ADMIN_PASSWORD: ${ADMIN_PASSWORD}
      LITELLM_MASTER_KEY: ${LITELLM_MASTER_KEY}
    depends_on:
      - postgres
      - redis
      - litellm
    networks:
      - ${DOCKER_NETWORK}

  frontend:
    image: ${IMAGE_FRONTEND}
    depends_on:
      - backend
    networks:
      - ${DOCKER_NETWORK}
EOF
fi

# Add network and volumes at the end
cat >> docker-compose.override.yaml << EOF

networks:
  ${DOCKER_NETWORK}:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
EOF

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

# Create Docker network
echo ""
echo "Creating Docker network..."
docker network create ${DOCKER_NETWORK} 2>/dev/null || echo "Network already exists or docker not available"

echo ""
echo "=============================================="
echo "${GREEN}Installation Complete!${NC}"
echo "=============================================="
echo ""
echo "Next steps:"
echo ""
if [[ "$EXPOSE_PORTS" =~ ^[Yy]$ ]]; then
    echo "1. Run: docker-compose up -d"
    echo "2. Access the application at:"
    echo "   - Frontend: http://localhost:3000"
    echo "   - Backend:  http://localhost:8080"
    echo "   - API Docs: http://localhost:8080/docs"
else
    echo "1. Run: docker-compose up -d"
    echo "2. The application is only accessible via the docker network."
    echo "   You can shell into a container to access it:"
    echo "   - docker-compose exec frontend sh"
fi
echo ""
echo "Admin login:"
echo "  Email:    $ADMIN_EMAIL"
echo "  Password: $ADMIN_PASSWORD"
echo ""
echo "Configuration saved to:"
echo "  - .env (environment variables)"
echo "  - docker-compose.override.yaml"
echo ""

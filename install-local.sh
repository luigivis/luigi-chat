#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=============================================="
echo "  Luigi Chat - Local Development Setup"
echo "=============================================="
echo ""
echo "This script sets up Luigi Chat for local development."
echo "It uses local code instead of pre-built Docker images."
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

DEFAULT_POSTGRES_USER="luigi"
DEFAULT_POSTGRES_DB="luigi_chat"
generate_password() {
    openssl rand -base64 24 | tr -dc 'A-Za-z0-9' | head -c 32
}
DEFAULT_REDIS_PASSWORD=$(generate_password)

check_docker() {
    if ! command -v docker &> /dev/null; then
        echo "${RED}Docker is not installed${NC}"
        echo "Please install Docker to continue"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        echo "${RED}Docker daemon is not running${NC}"
        echo "Please start Docker and try again"
        exit 1
    fi
    
    if docker compose version &> /dev/null; then
        DOCKER_COMPOSE="docker compose"
    elif command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE="docker-compose"
    else
        echo "${RED}Docker Compose is not installed${NC}"
        echo "Please install Docker Compose to continue"
        exit 1
    fi
    
    echo "${GREEN}Docker: OK${NC}"
    echo "${GREEN}Docker Compose: OK ($DOCKER_COMPOSE)${NC}"
    echo ""
}

check_existing_services() {
    echo "=============================================="
    echo "  Checking Existing Services"
    echo "=============================================="
    echo ""
    
    local has_conflicts=false
    
    if docker ps -a --filter "name=luigi-chat" --format "{{.Names}}" 2>/dev/null | grep -q .; then
        echo "${YELLOW}⚠️  Docker containers found:${NC}"
        docker ps -a --filter "name=luigi-chat" --format "  - {{.Names}} ({{.Status}})"
        has_conflicts=true
    fi
    
    if systemctl is-active postgresql 2>/dev/null | grep -q "active"; then
        echo "${YELLOW}⚠️  System PostgreSQL is running${NC}"
        echo "  This may conflict with Docker PostgreSQL on port 5432"
        has_conflicts=true
    fi
    
    if lsof -i :5432 2>/dev/null | grep -v "^COMMAND" | grep -q .; then
        echo "${YELLOW}⚠️  Something is listening on port 5432 (PostgreSQL):${NC}"
        lsof -i :5432 2>/dev/null | grep -v "^COMMAND" | head -3
        has_conflicts=true
    fi
    
    if lsof -i :6379 2>/dev/null | grep -v "^COMMAND" | grep -q .; then
        echo "${YELLOW}⚠️  Something is listening on port 6379 (Redis):${NC}"
        lsof -i :6379 2>/dev/null | grep -v "^COMMAND" | head -3
        has_conflicts=true
    fi
    
    if lsof -i :8080 2>/dev/null | grep -v "^COMMAND" | grep -q .; then
        echo "${YELLOW}⚠️  Something is listening on port 8080 (Backend):${NC}"
        lsof -i :8080 2>/dev/null | grep -v "^COMMAND" | head -3
        has_conflicts=true
    fi
    
    if lsof -i :3000 2>/dev/null | grep -v "^COMMAND" | grep -q .; then
        echo "${YELLOW}⚠️  Something is listening on port 3000 (Frontend):${NC}"
        lsof -i :3000 2>/dev/null | grep -v "^COMMAND" | head -3
        has_conflicts=true
    fi
    
    if lsof -i :4000 2>/dev/null | grep -v "^COMMAND" | grep -q .; then
        echo "${YELLOW}⚠️  Something is listening on port 4000 (LiteLLM):${NC}"
        lsof -i :4000 2>/dev/null | grep -v "^COMMAND" | head -3
        has_conflicts=true
    fi
    
    if pgrep -f "uvicorn" > /dev/null 2>&1; then
        echo "${YELLOW}⚠️  Backend processes (uvicorn) found:${NC}"
        pgrep -f "uvicorn" | xargs -I{} ps -p {} -o comm=,args= 2>/dev/null | head -3
        has_conflicts=true
    fi
    
    if pgrep -f "vite" > /dev/null 2>&1; then
        echo "${YELLOW}⚠️  Frontend processes (vite) found:${NC}"
        pgrep -f "vite" | xargs -I{} ps -p {} -o comm=,args= 2>/dev/null | head -3
        has_conflicts=true
    fi
    
    if ! command -v symlink 2>/dev/null && [ -L "$SCRIPT_DIR/backend/.env" ]; then
        echo "${YELLOW}⚠️  Backend .env symlink already exists${NC}"
    fi
    
    echo ""
    
    if $has_conflicts; then
        echo "${RED}⚠️  Conflicts detected!${NC}"
        echo ""
        read -p "Do you want to clean up ALL existing services? [y/N]: " CLEAN_ALL
        if [[ "$CLEAN_ALL" =~ ^[Yy]$ ]]; then
            echo ""
            echo "Cleaning up..."
            echo ""
            
            echo "Stopping Docker containers..."
            docker compose -f docker-compose.local.yaml down --remove-orphans -v 2>/dev/null || true
            
            echo "Removing Docker images..."
            docker images | grep "luigi-chat" | awk '{print $3}' | xargs -r docker rmi -f 2>/dev/null || true
            
            echo "Stopping system PostgreSQL..."
            if command -v sudo &> /dev/null; then
                sudo systemctl mask postgresql 2>/dev/null || true
                sudo systemctl stop postgresql 2>/dev/null || true
                sudo pkill -9 postgres 2>/dev/null || true
            else
                systemctl mask postgresql 2>/dev/null || true
                systemctl stop postgresql 2>/dev/null || true
                pkill -9 postgres 2>/dev/null || true
            fi
            
            echo "Killing backend/frontend processes..."
            pkill -f "uvicorn" 2>/dev/null || true
            pkill -f "vite" 2>/dev/null || true
            pkill -f "npm" 2>/dev/null || true
            
            echo "Waiting for ports to be released..."
            sleep 3
            
            echo ""
            echo "${GREEN}Cleanup complete!${NC}"
            echo ""
        else
            echo ""
            echo "${YELLOW}Proceeding without cleanup...${NC}"
            echo "${YELLOW}Installation may fail if ports are in use!${NC}"
            echo ""
        fi
    else
        echo "${GREEN}No conflicts detected${NC}"
        echo ""
    fi
}

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

url_encode_password() {
    echo -n "$1" | python3 -c "import urllib.parse; print(urllib.parse.quote(input(), safe=''))"
}

POSTGRES_PASSWORD_ENCODED=$(url_encode_password "$POSTGRES_PASSWORD")
REDIS_PASSWORD_ENCODED=$(url_encode_password "$REDIS_PASSWORD")

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

check_docker
check_existing_services

echo "Creating scripts directory..."
mkdir -p scripts

echo "Creating PostgreSQL init script..."
cat > scripts/init-postgres.sh << 'EOF'
#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    SELECT 'CREATE DATABASE luigi' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'luigi');
    CREATE DATABASE luigi;
EOSQL
EOF

chmod +x scripts/init-postgres.sh

echo "Creating .env file..."
cat > .env << EOF
# ================================================
# Luigi Chat - Local Development Environment
# ================================================

# System
WEBUI_NAME="Luigi Chat (Dev)"
SECRET_KEY=dev-secret-change-in-production

# PostgreSQL
DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD_ENCODED}@localhost:5432/${POSTGRES_DB}
POSTGRES_USER=${POSTGRES_USER}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_DB=${POSTGRES_DB}

# Redis
REDIS_URL=redis://:${REDIS_PASSWORD_ENCODED}@localhost:6379/0
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

echo "Creating .env symlink for backend..."
if [ -L "$SCRIPT_DIR/backend/.env" ]; then
    rm "$SCRIPT_DIR/backend/.env"
fi
ln -s "$SCRIPT_DIR/.env" "$SCRIPT_DIR/backend/.env"

echo "Creating docker-compose.local.yaml..."
cat > docker-compose.local.yaml << EOF
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
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - luigi-local
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

  litellm:
    build:
      context: ./litellm
      dockerfile: Dockerfile
    ports:
      - "4000:4000"
    environment:
      LITELLM_MASTER_KEY: ${LITELLM_MASTER_KEY}
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD_ENCODED}@postgres:5432/luigi
      REDIS_HOST: redis
      REDIS_PASSWORD: ${REDIS_PASSWORD}
      MINIMAX_API_KEY: ${MINIMAX_API_KEY}
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

echo "Creating Docker network..."
docker network create luigi-local 2>/dev/null || echo "Network already exists"

echo ""
echo "=============================================="
echo "${GREEN}Starting Services${NC}"
echo "=============================================="
echo ""

${DOCKER_COMPOSE} -f docker-compose.local.yaml up -d

echo ""
echo "Waiting for all services to be healthy..."
echo ""

wait_for_all_services() {
    local max_attempts=60
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        local all_healthy=true
        local not_ready=""
        
        for service in postgres redis litellm; do
            local status=$(${DOCKER_COMPOSE} -f docker-compose.local.yaml ps "$service" --format "{{.Status}}" 2>/dev/null || echo "not found")
            
            if echo "$status" | grep -qE "(Up|healthy|running)"; then
                echo "  ${GREEN}[OK]${NC} $service"
            else
                all_healthy=false
                not_ready="$not_ready $service"
                echo "  ${YELLOW}[WAIT]${NC} $service ($status)"
            fi
        done
        
        if $all_healthy; then
            echo ""
            echo "${GREEN}All services are healthy!${NC}"
            return 0
        fi
        
        echo "  Attempt $attempt/$max_attempts... waiting 3s"
        sleep 3
        attempt=$((attempt + 1))
        
        if [ $((attempt % 10)) -eq 0 ]; then
            echo ""
            echo "${YELLOW}Some services are taking longer than expected...${NC}"
        fi
    done
    
    echo ""
    echo "${RED}Timeout waiting for services to be healthy${NC}"
    return 1
}

if ! wait_for_all_services; then
    echo ""
    echo "${RED}========== Service Logs ==========${NC}"
    echo ""
    for service in postgres redis litellm; do
        echo "${RED}=== $service ===${NC}"
        ${DOCKER_COMPOSE} -f docker-compose.local.yaml logs --tail=30 "$service" 2>&1
        echo ""
    done
    
    echo ""
    echo "${RED}======================================${NC}"
    echo "${RED}   INSTALLATION FAILED${NC}"
    echo "${RED}======================================${NC}"
    echo ""
    echo "To clean up and retry:"
    echo "  docker compose -f docker-compose.local.yaml down -v"
    echo "  ./install-local.sh"
    exit 1
fi

echo ""
echo "=============================================="
echo "${GREEN}All Services Started Successfully!${NC}"
echo "=============================================="
echo ""
echo "Service Status:"
${DOCKER_COMPOSE} -f docker-compose.local.yaml ps
echo ""
echo "Next steps:"
echo ""
echo "Starting Backend and Frontend locally..."
echo ""

start_backend() {
    echo "Setting up backend virtual environment..."
    cd "$SCRIPT_DIR/backend"
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install -r requirements.txt -q
    
    echo "Starting Backend..."
    set -a
    source "$SCRIPT_DIR/.env"
    set +a
    nohup venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload > "$SCRIPT_DIR/logs/backend.log" 2>&1 &
    echo "Backend started in background (PID: $!)"
}

create_admin_user() {
    echo "Creating admin user..."
    cd "$SCRIPT_DIR/backend"
    source venv/bin/activate
    
    local admin_email="$ADMIN_EMAIL"
    local admin_password="$ADMIN_PASSWORD"
    local litellm_key="sk-test-key-for-development"
    
    python3 - "$admin_email" "$admin_password" "$litellm_key" << 'PYEOF'
import asyncio
import bcrypt
import uuid
import sys
import httpx
from app.models import engine
from sqlalchemy import text

async def create_admin_if_not_exists(email, password, placeholder_key):
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT email FROM users WHERE email = :email"), {"email": email})
        if result.fetchone():
            print("Admin user already exists")
            return
        
        admin_id = str(uuid.uuid4())
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        await conn.execute(text("""
            INSERT INTO users (id, email, password_hash, role, theme, primary_color, 
                default_model, voice_enabled, font_size, compact_mode, voice_id,
                speech_speed, speech_emotion, litellm_key, litellm_user_id, status)
            VALUES (:id, :email, :pwd_hash, 'admin', 'dark', '#7000FF', 
                'luigi-thinking', false, 'medium', false, 'male-qn-qingse',
                '1.0', 'neutral', :litellm_key, 'admin-user', 'active')
        """), {"id": admin_id, "email": email, "pwd_hash": password_hash, "litellm_key": placeholder_key})
        print("Admin user created with placeholder key")
        
        return admin_id

async def generate_litellm_key(admin_id, email):
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://localhost:4000/key/generate",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer sk-test"
                },
                json={
                    "user_id": email,
                    "models": ["luigi-thinking"],
                    "key_name": f"admin-key-{admin_id[:8]}",
                    "rpm_limit": 3,
                    "tpm_limit": 6000,
                    "max_budget": 100.0
                }
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("key", None)
            else:
                print(f"LiteLLM key generation failed: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        print(f"Error generating LiteLLM key: {e}")
        return None

async def update_admin_litellm_key(email, new_key):
    async with engine.begin() as conn:
        await conn.execute(
            text("UPDATE users SET litellm_key = :key WHERE email = :email"),
            {"key": new_key, "email": email}
        )
        print("Admin LiteLLM key updated with real key")

async def main():
    email = sys.argv[1]
    password = sys.argv[2]
    placeholder_key = sys.argv[3]
    
    admin_id = await create_admin_if_not_exists(email, password, placeholder_key)
    
    if admin_id:
        real_key = await generate_litellm_key(admin_id, email)
        if real_key:
            await update_admin_litellm_key(email, real_key)
            print(f"Admin fully configured with LiteLLM key")
        else:
            print("Admin created but LiteLLM key generation failed - using placeholder")

asyncio.run(main())
PYEOF
}

start_frontend() {
    echo "Setting up frontend..."
    cd "$SCRIPT_DIR/frontend"
    
    if [ ! -d "node_modules" ]; then
        npm install -q
    fi
    
    echo "Starting Frontend..."
    nohup npm run dev -- --host 0.0.0.0 > "$SCRIPT_DIR/logs/frontend.log" 2>&1 &
    echo "Frontend started in background (PID: $!)"
}

mkdir -p "$SCRIPT_DIR/logs"

start_backend
sleep 5
create_admin_user
sleep 2
start_frontend

sleep 5

echo ""
echo "Checking services..."
if curl -s http://localhost:8080/docs > /dev/null 2>&1; then
    echo "${GREEN}Backend: OK (http://localhost:8080)${NC}"
else
    echo "${RED}Backend: FAILED - Check logs/backend.log${NC}"
fi

if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "${GREEN}Frontend: OK (http://localhost:3000)${NC}"
else
    echo "${RED}Frontend: FAILED - Check logs/frontend.log${NC}"
fi

echo ""
echo "=============================================="
echo "${GREEN}All Services Started!${NC}"
echo "=============================================="
echo ""
echo "Access the application:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend API: http://localhost:8080"
echo "  - LiteLLM Proxy: http://localhost:4000"
echo "  - API Docs: http://localhost:8080/docs"
echo ""
echo "View logs:"
echo "  - Backend: tail -f logs/backend.log"
echo "  - Frontend: tail -f logs/frontend.log"
echo "  - Docker: docker compose -f docker-compose.local.yaml logs -f"
echo ""
echo "Stop services:"
echo "  - pkill -f 'uvicorn app.main'"
echo "  - pkill -f 'npm run dev'"
echo "  - docker compose -f docker-compose.local.yaml down"
echo ""
echo "Admin login:"
echo "  Email:    $ADMIN_EMAIL"
echo "  Password: $ADMIN_PASSWORD"

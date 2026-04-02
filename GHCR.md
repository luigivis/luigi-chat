# GitHub Container Registry (GHCR) Deployment

## Overview

This project uses GitHub Actions to build and push Docker images to GHCR on every push to `main`.

## Docker Images

Images are published to:
- `ghcr.io/luigivis/luigi-chat-frontend:latest`
- `ghcr.io/luigivis/luigi-chat-backend:latest`
- `ghcr.io/luigivis/luigi-chat-litellm:latest`

## GitHub Actions Workflow

The workflow file is at `.github/workflows/build.yml` and performs:

1. **Build & Push** on every push:
   - Builds Docker images for frontend, backend, and litellm
   - Pushes to GHCR with tags: `latest`, `sha-xxxxxxx`, and branch name

2. **Deploy** (on push to main only):
   - SSH into your server
   - Pull new images
   - Run `docker-compose up -d`

## Required Secrets

### For Building (automatic)
No secrets required - uses `GITHUB_TOKEN` automatically.

### For Deployment

Add these secrets in GitHub repo → Settings → Secrets:

| Secret | Description |
|--------|-------------|
| `DEPLOY_HOST` | Server IP or hostname |
| `DEPLOY_USER` | SSH username |
| `DEPLOY_SSH_KEY` | Private SSH key |
| `DEPLOY_PATH` | Path to deployment directory |
| `DEPLOY_ENV` | Full .env file content |

### Example DEPLOY_ENV content:
```
WEBUI_NAME="Luigi Chat"
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
REDIS_URL=redis://:password@redis:6379/0
REDIS_PASSWORD=your-redis-password
POSTGRES_USER=luigi
POSTGRES_PASSWORD=your-postgres-password
POSTGRES_DB=luigi_chat
LITELLM_MASTER_KEY=sk-...
MINIMAX_API_KEY=your-minimax-key
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=your-admin-password
```

## Image Tagging Strategy

| Event | Tag |
|-------|-----|
| Push to `main` | `latest` + `sha-xxxxxxx` |
| Push to branch | `branch-name` |
| PR | `pr-xxx` |
| Tag `v1.2.3` | `1.2.3` |

## Manual Deployment

To deploy manually after images are built:

```bash
# Pull images
docker pull ghcr.io/luigivis/luigi-chat/frontend:latest
docker pull ghcr.io/luigivis/luigi-chat/backend:latest
docker pull ghcr.io/luigivis/luigi-chat/litellm:latest

# Or use docker-compose
docker-compose -f docker-compose.prod.yaml pull
docker-compose -f docker-compose.prod.yaml up -d
```

## First Time Setup

1. Fork/clone this repo
2. Go to GitHub repo → Settings → Secrets → Actions
3. Add deployment secrets
4. Push to main - images will build and deploy automatically

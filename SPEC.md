# Luigi Chat - Especificaciones Técnicas

## Tabla de Contenidos

1. [Visión General](#1-visión-general)
2. [Arquitectura del Sistema](#2-arquitectura-del-sistema)
3. [Stack Tecnológico](#3-stack-tecnológico)
4. [Modelos MiniMax](#4-modelos-minimax)
5. [Estructura de Base de Datos](#5-estructura-de-base-de-datos)
6. [API Endpoints](#6-api-endpoints)
7. [Autenticación y Autorización](#7-autenticación-y-autorización)
8. [LiteLLM Proxy Configuration](#8-litellm-proxy-configuration)
9. [Docker Deployment](#9-docker-deployment)
10. [Frontend](#10-frontend)
11. [Funcionalidades por Usuario](#11-funcionalidades-por-usuario)
12. [Rate Limiting](#12-rate-limiting)
13. [MiniMax File API](#13-minimax-file-api)
14. [MiniMax Speech 2.6 TTS](#14-minimax-speech-26-tts)
15. [Tests](#15-tests)

---

## 1. Visión General

**Luigi Chat** es un rebuild de OpenWebUI con las siguientes características distintivas:

- **Multi-tenant**: Múltiples usuarios con API keys propias
- **Rate limiting configurable**: 3 RPM por defecto por usuario
- **Modelos MiniMax**: luigi-thinking, luigi-vision, luigi-voice
- **UI customizable**: Cada usuario puede personalizar tema y preferencias
- **API keys OpenAI-compatibles**: Generadas automáticamente al registrarse
- **Integración MiniMax File API**: Upload/manage archivos
- **TTS con Speech 2.6**: Voz ultra-low latency

---

## 2. Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                     Luigi Chat UI                           │
│              SvelteKit Frontend (:3000)                    │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐  │
│  │  Chat    │  │  Voice   │  │  Theme   │  │ Admin Panel │  │
│  │Interface │  │  TTS     │  │ Selector │  │  Users/Keys │  │
│  └──────────┘  └──────────┘  └──────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                    HTTP/WebSocket
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Backend FastAPI                          │
│                       Puerto :8080                           │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                    API Routers                          ││
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌───────────┐  ││
│  │  │  Auth   │  │  Users  │  │  Chats  │  │  Files    │  ││
│  │  │Router   │  │ Router  │  │ Router  │  │  Router   │  ││
│  │  └─────────┘  └─────────┘  └─────────┘  └───────────┘  ││
│  └─────────────────────────────────────────────────────────┘│
│                              │                               │
│                              ▼                               │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                   Services Layer                         ││
│  │  ┌───────────────┐  ┌────────────────┐  ┌────────────┐  ││
│  │  │  LiteLLM      │  │  MiniMax API   │  │  File      │  ││
│  │  │  Client       │  │  Client        │  │  Service   │  ││
│  │  └───────────────┘  └────────────────┘  └────────────┘  ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
         │                              │
         ▼                              ▼
┌─────────────────┐          ┌─────────────────────────┐
│  LiteLLM Proxy  │          │      PostgreSQL           │
│    Puerto :4000 │          │   (users, chats, keys)   │
│                 │          └─────────────────────────┘
│  ┌───────────┐  │                      │
│  │ Virtual   │  │                      ▼
│  │ Keys      │  │          ┌─────────────────────────┐
│  │ 3 RPM     │  │          │        Redis             │
│  └───────────┘  │          │  (sessions, cache)      │
└────────┬────────┘          └─────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                       MINIMAX API                            │
│                                                              │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │  M2.7       │  │  Text-01     │  │   Speech 2.6 HD   │  │
│  │  Chat       │  │  Vision      │  │   TTS             │  │
│  │  (texto)    │  │  (imágenes)  │  │   (voz)          │  │
│  └─────────────┘  └──────────────┘  └───────────────────┘  │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                  File Management API                  │  │
│  │   Upload / List / Retrieve / Delete                  │  │
│  │   100GB total, 512MB por archivo                       │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Stack Tecnológico

### Backend

| Componente | Tecnología | Versión |
|------------|------------|---------|
| Framework | FastAPI | 0.115+ |
| Python | Python | 3.11+ |
| ORM | SQLAlchemy | 2.0+ |
| Database | PostgreSQL | 15+ |
| Cache | Redis | 7+ |
| Auth | python-jose (JWT) | 3.3+ |
| Password | bcrypt | 4.0+ |
| HTTP Client | httpx | 0.27+ |
| WebSocket | python-socketio | 5.0+ |
| Uvicorn | uvicorn | 0.30+ |

### Frontend

| Componente | Tecnología | Versión |
|------------|------------|---------|
| Framework | SvelteKit | 2.0+ |
| Language | TypeScript | 5.0+ |
| Styling | TailwindCSS | 3.4+ |
| Build | Vite | 5.0+ |
| Icons | Lucide Svelte | 0.400+ |
| State | Svelte Stores | Built-in |

### AI Gateway

| Componente | Tecnología | Versión |
|------------|------------|---------|
| Proxy | LiteLLM | 1.50+ |
| Database | PostgreSQL | 15+ |

### Deployment

| Componente | Tecnología |
|------------|------------|
| Container | Docker |
| Orchestration | Docker Compose |
| Reverse Proxy | Nginx (prod) |

---

## 4. Modelos MiniMax

### 4.1 Alias de Modelos

| Alias (usuario) | Modelo Real | Descripción | Contexto |
|-----------------|-------------|-------------|----------|
| `luigi-thinking` | `minimax/MiniMax-M2.7` | Chat principal, razonamiento | 204,800 tokens |
| `luigi-vision` | `minimax/MiniMax-Text-01` | Análisis de imágenes | Soporta `image_url` |
| `luigi-voice` | `minimax/speech-2.6-hd` | Text-to-Speech HD | 40+ idiomas, <250ms latency |

### 4.2 Características M2.7

- **Context Window**: 204,800 tokens
- **Output Speed**: ~60 tps (standard), ~100 tps (highspeed)
- **Coding**: SWE-Pro 56.22%, Terminal Bench 2 (57.0%)
- **Tool Calling**: Full function calling support
- **Streaming**: Yes
- **API Compatibility**: Anthropic SDK, OpenAI SDK, Direct HTTP

### 4.3 Características MiniMax-Text-01 (Vision)

- **Vision**: Soporta imágenes via `image_url` en messages
- **Model**: `minimax/MiniMax-Text-01`
- **Use case**: Análisis de diagrams, fotos, documentos

### 4.4 Características Speech 2.6 (TTS)

- **Latency**: <250ms end-to-end
- **Languages**: 40+
- **Voices**: 300+ system voices
- **Features**:
  - Voice cloning (Fluent LoRA)
  - Emotion control (7 emotions)
  - Speed control (0.5-2.0)
  - Pitch control (-12 to 12)
  - Format: MP3, PCM, FLAC, WAV
  - WebSocket streaming

---

## 5. Estructura de Base de Datos

### 5.1 PostgreSQL Schema

```sql
-- Extension UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabla de Usuarios
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',  -- 'admin' | 'user'
    
    -- Preferencias de UI
    theme VARCHAR(50) DEFAULT 'dark',
    primary_color VARCHAR(20) DEFAULT '#7000FF',
    
    -- Preferencias de modelos
    default_model VARCHAR(50) DEFAULT 'luigi-thinking',
    voice_enabled BOOLEAN DEFAULT false,
    voice_id VARCHAR(100) DEFAULT 'male-qn-qingse',
    
    -- API Key (generada automáticamente)
    litellm_key VARCHAR(255),
    litellm_user_id VARCHAR(255),  -- User ID en LiteLLM
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_active_at TIMESTAMP,
    
    -- Status
    status VARCHAR(20) DEFAULT 'active'  -- 'active' | 'disabled'
);

-- Tabla de Chats
CREATE TABLE chats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) DEFAULT 'New Chat',
    model VARCHAR(50) DEFAULT 'luigi-thinking',
    
    -- Metadatos
    tags TEXT[],  -- Array de tags
    folder_id UUID,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de Messages
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chat_id UUID REFERENCES chats(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,  -- 'user' | 'assistant' | 'system'
    content TEXT NOT NULL,
    
    -- Para mensajes con imágenes
    image_urls TEXT[],
    
    -- Model info
    model VARCHAR(50),
    tokens_used INTEGER,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de Files (metadata)
CREATE TABLE files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- MiniMax file info
    minimax_file_id VARCHAR(255) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,  -- 'document' | 'audio' | 'image'
    size_bytes INTEGER NOT NULL,
    
    -- Status
    status VARCHAR(20) DEFAULT 'active',  -- 'active' | 'deleted'
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de Folders
CREATE TABLE folders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    parent_id UUID REFERENCES folders(id) ON DELETE CASCADE,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_chats_user_id ON chats(user_id);
CREATE INDEX idx_messages_chat_id ON messages(chat_id);
CREATE INDEX idx_files_user_id ON files(user_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
```

### 5.2 LiteLLM Database Tables (PostgreSQL separado)

LiteLLM usa su propia base de datos para:

- `LiteLLM_VerificationToken` - API keys virtuales
- `LiteLLM_UserTable` - Usuarios con budgets/spend
- `LiteLLM_TeamTable` - Equipos
- `LiteLLM_SpendLogs` - Logs de gasto

---

## 6. API Endpoints

### 6.1 Auth Router (`/auth`)

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/auth/signup` | Registro de usuario | No |
| POST | `/auth/login` | Login | No |
| POST | `/auth/logout` | Logout | Yes |
| GET | `/auth/me` | Usuario actual | Yes |
| POST | `/auth/refresh` | Refrescar JWT | Yes |

**Signup Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Signup Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "api_key": "sk-...",
  "role": "user"
}
```

**Login Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Login Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "role": "user",
    "theme": "dark",
    "primary_color": "#7000FF"
  }
}
```

### 6.2 Users Router (`/users`) - Admin Only

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/users/` | Listar usuarios | Admin |
| POST | `/users/` | Crear usuario | Admin |
| GET | `/users/{id}` | Ver usuario | Admin |
| PATCH | `/users/{id}` | Actualizar usuario | Admin/User |
| DELETE | `/users/{id}` | Eliminar usuario | Admin |

**Create User Request:**
```json
{
  "email": "newuser@example.com",
  "password": "password123",
  "role": "user",
  "rpm_limit": 3,
  "tpm_limit": 6000
}
```

**Update User Preferences Request:**
```json
{
  "theme": "light",
  "primary_color": "#00FF00",
  "default_model": "luigi-vision",
  "voice_enabled": true,
  "voice_id": "female-qn-qingse"
}
```

### 6.3 Chats Router (`/chats`)

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/chats/` | Listar chats | Yes |
| POST | `/chats/` | Crear chat | Yes |
| GET | `/chats/{id}` | Obtener chat | Yes |
| PATCH | `/chats/{id}` | Actualizar chat | Yes |
| DELETE | `/chats/{id}` | Eliminar chat | Yes |
| POST | `/chats/{id}/messages` | Enviar mensaje | Yes |
| GET | `/chats/{id}/messages` | Obtener mensajes | Yes |

**Create Chat Request:**
```json
{
  "title": "Mi nuevo chat",
  "model": "luigi-thinking"
}
```

**Send Message Request:**
```json
{
  "content": "¿Qué hay en esta imagen?",
  "image_urls": ["https://example.com/image.png"],
  "model": "luigi-vision",
  "stream": true
}
```

**Send Message Response (Streaming):**
```
data: {"content": "", "role": "assistant", "done": false}
data: {"content": "En", "role": "assistant", "done": false}
data: {"content": "esta", "role": "assistant", "done": false}
data: {"content": "imagen", "role": "assistant", "done": false}
data: {"content": "puedo", "role": "assistant", "done": false}
...
data: {"content": "ver un gato.", "role": "assistant", "done": true}
```

### 6.4 Files Router (`/files`)

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/files/upload` | Subir archivo | Yes |
| GET | `/files/` | Listar archivos | Yes |
| GET | `/files/{id}` | Info archivo | Yes |
| GET | `/files/{id}/content` | Descargar contenido | Yes |
| DELETE | `/files/{id}` | Eliminar archivo | Yes |

**Upload File Request:**
```
POST /files/upload
Content-Type: multipart/form-data

file: <binary>
```

**Upload File Response:**
```json
{
  "id": "uuid",
  "minimax_file_id": "file-xxx",
  "filename": "document.pdf",
  "file_type": "document",
  "size_bytes": 1024000
}
```

**Supported File Types:**
- Documents: `pdf`, `docx`, `txt`, `jsonl` (max 512MB)
- Audio: `mp3`, `m4a`, `wav` (max 512MB)
- Images: `png`, `jpg`, `jpeg`, `gif`, `webp` (via chat, not upload)

### 6.5 Audio Router (`/audio`)

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/audio/speech` | Text-to-Speech | Yes |
| GET | `/audio/voices` | Lista de voces | Yes |

**Speech Request:**
```json
{
  "input": "Hola, ¿cómo estás?",
  "model": "luigi-voice",
  "voice_id": "male-qn-qingse",
  "response_format": "mp3",
  "speed": 1.0,
  "emotion": "happy"
}
```

**Speech Response:**
```
Content-Type: audio/mpeg
Binary audio data
```

### 6.6 Models Router (`/models`)

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/models/` | Lista de modelos | Yes |

**Models Response:**
```json
{
  "models": [
    {
      "id": "luigi-thinking",
      "name": "MiniMax M2.7",
      "description": "Chat principal con razonamiento avanzado",
      "context_window": 204800,
      "supports_vision": false,
      "supports_streaming": true
    },
    {
      "id": "luigi-vision",
      "name": "MiniMax Text-01",
      "description": "Análisis de imágenes",
      "context_window": 100000,
      "supports_vision": true,
      "supports_streaming": true
    },
    {
      "id": "luigi-voice",
      "name": "MiniMax Speech 2.6 HD",
      "description": "Text-to-Speech",
      "modality": "audio",
      "supports_streaming": true
    }
  ]
}
```

---

## 7. Autenticación y Autorización

### 7.1 JWT Tokens

**Access Token:**
- Algorithm: HS256
- Expiry: 1 hour
- Payload: `user_id`, `email`, `role`

**Refresh Token:**
- Algorithm: HS256
- Expiry: 7 days
- Payload: `user_id`

### 7.2 Password Hashing

- Algorithm: bcrypt with salt rounds = 12
- Library: `passlib[bcrypt]`

### 7.3 Roles

| Rol | Permisos |
|-----|----------|
| `admin` | CRUD all users, view all chats, manage keys |
| `user` | CRUD own data, use chat, view own stats |

### 7.4 Auto-Key Generation Flow

```
1. Usuario llama POST /auth/signup
2. Backend valida email/password
3. Backend hashea password y guarda user en PostgreSQL
4. Backend llama LiteLLM /user/new con rpm_limit=3
5. Backend llama LiteLLM /key/generate con user_id
6. Backend guarda litellm_key en user table
7. Backend retorna user info + api_key al cliente
```

---

## 8. LiteLLM Proxy Configuration

### 8.1 config.yaml

```yaml
model_list:
  # Alias: luigi-thinking -> MiniMax M2.7
  - model_name: luigi-thinking
    litellm_params:
      model: minimax/MiniMax-M2.7
      api_base: https://api.minimax.io/v1
      api_key: os.environ/MINIMAX_API_KEY
      rpm: 60  # Model-level RPM limit

  # Alias: luigi-vision -> MiniMax Text-01
  - model_name: luigi-vision
    litellm_params:
      model: minimax/MiniMax-Text-01
      api_base: https://api.minimax.io/v1
      api_key: os.environ/MINIMAX_API_KEY
      rpm: 60

  # Alias: luigi-voice -> MiniMax Speech 2.6 HD
  - model_name: luigi-voice
    litellm_params:
      model: minimax/speech-2.6-hd
      api_base: https://api.minimax.io/v1
      api_key: os.environ/MINIMAX_API_KEY
      rpm: 60

litellm_settings:
  drop_params: true
  set_verbose: false
  max_parallel_requests: 100

general_settings:
  master_key: os.environ/LITELLM_MASTER_KEY
  database_url: os.environ/DATABASE_URL
  redis_url: os.environ/REDIS_URL
  port: 4000
  host: 0.0.0.0
```

### 8.2 Model Aliases para Keys

Cuando se genera una key, se configuran aliases:

```json
{
  "aliases": {
    "luigi-thinking": "minimax/MiniMax-M2.7",
    "luigi-vision": "minimax/MiniMax-Text-01",
    "luigi-voice": "minimax/speech-2.6-hd"
  }
}
```

### 8.3 Rate Limit Config

```yaml
# Por defecto en default_key_generate_params
litellm_settings:
  default_key_generate_params:
    rpm_limit: 3
    tpm_limit: 6000
    max_budget: 100
    duration: null  # Sin expiración
```

---

## 9. Docker Deployment

### 9.1 docker-compose.yaml (Desarrollo)

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: luigi_chat
      POSTGRES_USER: luigi
      POSTGRES_PASSWORD: luigi_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U luigi"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
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
      DATABASE_URL: postgresql://luigi:luigi_password@postgres:5432/litellm
      REDIS_URL: redis://redis:6379
      MINIMAX_API_KEY: ${MINIMAX_API_KEY}
      LITELLM_MASTER_KEY: ${LITELLM_MASTER_KEY:-sk-dev-key}
    volumes:
      - ./litellm/config.yaml:/app/config.yaml
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: --config /app/config.yaml

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      DATABASE_URL: postgresql://luigi:luigi_password@postgres:5432/luigi_chat
      REDIS_URL: redis://redis:6379
      LITELLM_MASTER_KEY: ${LITELLM_MASTER_KEY:-sk-dev-key}
      MINIMAX_API_KEY: ${MINIMAX_API_KEY}
      SECRET_KEY: ${SECRET_KEY:-dev-secret-change-in-prod}
      WEBUI_NAME: Luigi Chat
      LITELLM_PROXY_URL: http://litellm:4000
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      litellm:
        condition: service_started
    volumes:
      - ./backend:/app

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      PUBLIC_API_URL: http://localhost:8080
    depends_on:
      - backend

volumes:
  postgres_data:
  redis_data:

networks:
  default:
    name: luigi-network
```

### 9.2 Dockerfile Backend

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
```

### 9.3 Dockerfile LiteLLM

```dockerfile
FROM ghcr.io/berriai/litellm:main-latest

WORKDIR /app

COPY config.yaml /app/config.yaml

CMD ["--config", "/app/config.yaml"]
```

### 9.4 Variables de Entorno

```bash
# .env
# LiteLLM
LITELLM_MASTER_KEY=sk-your-master-key-here
DATABASE_URL=postgresql://luigi:luigi_password@localhost:5432/litellm
REDIS_URL=redis://localhost:6379

# MiniMax
MINIMAX_API_KEY=your-minimax-api-key

# Backend
SECRET_KEY=your-jwt-secret-key-change-in-production
WEBUI_NAME=Luigi Chat

# URLs
LITELLM_PROXY_URL=http://localhost:4000
```

---

## 10. Frontend

### 10.1 Estructura de Carpetas

```
frontend/
├── src/
│   ├── routes/
│   │   ├── (app)/                 # Layout principal con sidebar
│   │   │   ├── +layout.svelte    # Layout con auth check
│   │   │   ├── +page.svelte      # Chat principal
│   │   │   ├── /chat/[id]/       # Chat individual
│   │   │   │   └── +page.svelte
│   │   │   ├── /workspace/       # Settings, etc.
│   │   │   │   ├── +page.svelte
│   │   │   │   ├── models/
│   │   │   │   ├── knowledge/
│   │   │   │   └── settings/
│   │   │   └── /admin/
│   │   │       └── users/
│   │   │           └── +page.svelte
│   │   │
│   │   ├── auth/                  # Rutas públicas
│   │   │   ├── login/
│   │   │   │   └── +page.svelte
│   │   │   └── signup/
│   │   │       └── +page.svelte
│   │   │
│   │   └── +layout.svelte         # Root layout
│   │
│   ├── lib/
│   │   ├── components/
│   │   │   ├── chat/
│   │   │   │   ├── ChatInterface.svelte
│   │   │   │   ├── ChatInput.svelte
│   │   │   │   ├── Messages.svelte
│   │   │   │   ├── Message.svelte
│   │   │   │   ├── ModelSelector.svelte
│   │   │   │   ├── TokenCount.svelte
│   │   │   │   └──SuggestedPrompts.svelte
│   │   │   │
│   │   │   ├── audio/
│   │   │   │   ├── AudioRecorder.svelte
│   │   │   │   ├── AudioPlayer.svelte
│   │   │   │   └── VoiceSelector.svelte
│   │   │   │
│   │   │   ├── layout/
│   │   │   │   ├── Sidebar.svelte
│   │   │   │   ├── Header.svelte
│   │   │   │   ├── MobileNav.svelte
│   │   │   │   └── CommandMenu.svelte
│   │   │   │
│   │   │   ├── theme/
│   │   │   │   ├── ThemeSelector.svelte
│   │   │   │   └── ColorPicker.svelte
│   │   │   │
│   │   │   └── common/
│   │   │       ├── Button.svelte
│   │   │       ├── Input.svelte
│   │   │       ├── Modal.svelte
│   │   │       └── Spinner.svelte
│   │   │
│   │   ├── stores/
│   │   │   ├── auth.ts           # Token, user info
│   │   │   ├── chat.ts           # Chat state
│   │   │   ├── config.ts         # App config
│   │   │   └── theme.ts          # Theme preferences
│   │   │
│   │   ├── apis/
│   │   │   ├── index.ts          # Base API client
│   │   │   ├── auth.ts
│   │   │   ├── chats.ts
│   │   │   ├── users.ts
│   │   │   ├── files.ts
│   │   │   └── audio.ts
│   │   │
│   │   └── utils/
│   │       ├── constants.ts
│   │       └── helpers.ts
│   │
│   ├── app.css                    # Global styles
│   ├── app.html                   # HTML template
│   └── hooks.server.ts            # Server hooks (auth)
│
├── static/
│   └── favicon.ico
│
├── package.json
├── svelte.config.js
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

### 10.2 Chat Interface

**Features:**
- Streaming de respuestas (Server-Sent Events)
- Upload de imágenes (drag & drop)
- Selector de modelo
- Historial de chats en sidebar
- Búsqueda de chats
- Compartir chats
- Exportar chat (JSON, Markdown)

### 10.3 Voice Integration

**Features:**
- Grabar audio con WebRTC
- Reproducir respuesta TTS
- Selector de voz
- Control de velocidad
- Control de emoción
- WebSocket streaming para baja latencia

### 10.4 Theme System

**Opciones por usuario:**
- Theme: `light` | `dark` | `system`
- Primary Color: Color picker
- Font size: `small` | `medium` | `large`
- Compact mode: boolean

---

## 11. Funcionalidades por Usuario

### 11.1 Preferencias de UI

```typescript
interface UserPreferences {
  theme: 'light' | 'dark' | 'system';
  primaryColor: string;  // Hex color
  fontSize: 'small' | 'medium' | 'large';
  compactMode: boolean;
  sidebarCollapsed: boolean;
}
```

### 11.2 Preferencias de Modelo

```typescript
interface ModelPreferences {
  defaultModel: 'luigi-thinking' | 'luigi-vision';
  voiceEnabled: boolean;
  voiceId: string;
  speechSpeed: number;  // 0.5 - 2.0
  speechEmotion: 'happy' | 'sad' | 'angry' | 'neutral';
}
```

### 11.3 Guardado de Preferencias

Las preferencias se guardan en:
1. **Backend**: PostgreSQL tabla `users`
2. **Frontend**: Svelte store + localStorage para sync

---

## 12. Rate Limiting

### 12.1 Límites por Defecto

| Límite | Valor | Descripción |
|--------|-------|-------------|
| RPM | 3 | Requests por minuto |
| TPM | 6000 | Tokens por minuto |
| Max Budget | $100 | Budget máximo por key |

### 12.2 Implementación

LiteLLM maneja el rate limiting automáticamente:

```yaml
# Por key generada
{
  "rpm_limit": 3,
  "tpm_limit": 6000
}
```

### 12.3 Headers de Respuesta

```
x-ratelimit-limit-requests: 3
x-ratelimit-remaining-requests: 2
x-ratelimit-reset-requests: 45s
```

---

## 13. MiniMax File API

### 13.1 Endpoints

| Método | Endpoint MiniMax | Descripción |
|--------|------------------|-------------|
| POST | `/v1/files/upload` | Subir archivo |
| GET | `/v1/files` | Listar archivos |
| GET | `/v1/files/{file_id}` | Info archivo |
| GET | `/v1/files/{file_id}/content` | Descargar |
| DELETE | `/v1/files/{file_id}` | Eliminar |

### 13.2 Límites

| Tipo | Límite |
|------|--------|
| Capacidad total | 100GB |
| Archivo individual | 512MB |
| Documentos | pdf, docx, txt, jsonl |
| Audio | mp3, m4a, wav |

### 13.3 Backend Proxy

El backend proxya las requests a MiniMax:

```python
# POST /api/files/upload
async def upload_file(file: UploadFile, user_id: str):
    # 1. Upload to MiniMax
    minimax_response = await minimax_client.files.upload(
        file=file,
        purpose="fine-tune"  # or "batch", " assistants"
    )
    
    # 2. Save metadata to local DB
    local_file = await db.files.create(
        user_id=user_id,
        minimax_file_id=minimax_response.id,
        filename=file.filename,
        file_type=file.content_type,
        size_bytes=file.size
    )
    
    return local_file
```

---

## 14. MiniMax Speech 2.6 TTS

### 14.1 Características

| Característica | Valor |
|----------------|-------|
| Latencia | <250ms |
| Idiomas | 40+ |
| Voces | 300+ |
| Emociones | 7 (happy, sad, angry, fearful, disgusted, surprised, calm) |
| Velocidad | 0.5 - 2.0 |
| Formatos | mp3, pcm, flac, wav |

### 14.2 WebSocket Streaming

```
wss://api.minimax.io/ws/v1/t2a_v2
```

### 14.3 TTS Request (HTTP)

```bash
POST https://api.minimax.io/v1/t2a_v2
Headers:
  Authorization: Bearer $MINIMAX_API_KEY
  Content-Type: application/json

Body:
{
  "model": "speech-2.6-hd",
  "text": "Hola, ¿cómo estás?",
  "stream": true,
  "voice_setting": {
    "voice_id": "male-qn-qingse",
    "speed": 1.0,
    "pitch": 0,
    "volume": 0,
    "emotion": "happy"
  },
  "audio_setting": {
    "sample_rate": 32000,
    "bitrate": 128000,
    "format": "mp3"
  }
}
```

### 14.4 Backend TTS Endpoint

```python
@router.post("/audio/speech")
async def text_to_speech(
    input: str,
    model: str = "luigi-voice",
    voice_id: str = "male-qn-qingse",
    speed: float = 1.0,
    emotion: str = "neutral",
    format: str = "mp3"
):
    # Usa MiniMax TTS API
    # Retorna audio stream
```

---

## 15. Referencias Externas

### 15.1 MiniMax Platform

**Documentación Oficial:** https://platform.minimax.io/docs

**Modelos MiniMax:**
| Modelo | Endpoint | Descripción |
|--------|----------|-------------|
| M2.7 | `/v1/text/chatcompletion_v2` | Chat principal con razonamiento |
| Text-01 | `/v1/text/chatcompletion_v2` | Vision + texto |
| Speech 2.6 | `/v1/t2a_v2` | Text-to-Speech |
| Image-01 | `/v1/image_gen` | Generación de imágenes |

**Base URL:** `https://api.minimax.io`

**Auth:** Bearer token en header `Authorization: Bearer $MINIMAX_API_KEY`

**Rate Limits:**
| Plan | RPM | TPM |
|------|-----|-----|
| Pay-as-you-go | varies | varies |
| Token Plan | 1000 | 10000 |

**File API:**
- Total capacity: 100GB
- Max file size: 512MB
- Supported: pdf, docx, txt, jsonl, mp3, m4a, wav

**TTS WebSocket:** `wss://api.minimax.io/ws/v1/t2a_v2`

---

### 15.2 OpenWebUI (Inspiración/Fork Base)

**GitHub:** https://github.com/open-webui/open-webui

**Stack:**
- Backend: FastAPI + Python
- Frontend: SvelteKit + TailwindCSS
- Database: SQLAlchemy (SQLite/PostgreSQL)
- Auth: JWT + OAuth
- Real-time: Socket.IO

**Arquitectura Clave:**
```
backend/
├── main.py           # FastAPI app
├── routers/          # API endpoints
├── models/           # DB models
├── services/         # Business logic
└── utils/            # Helpers
```

**Features que adoptamos:**
- Chat interface con streaming
- Historial de chats
- Model selector
- File upload
- Auth system

**Licencia:** Custom (requiere mantener branding de OpenWebUI si se modifica)

---

### 15.3 LiteLLM Proxy

**Documentación:** https://docs.litellm.ai/docs

**GitHub:** https://github.com/BerriAI/litellm

**Virtual Keys:**
```bash
# Generar key
POST /key/generate
{
  "user_id": "user@email.com",
  "models": ["luigi-thinking"],
  "rpm_limit": 3,
  "tpm_limit": 6000,
  "aliases": {
    "luigi-thinking": "minimax/MiniMax-M2.7"
  }
}
```

**Rate Limiting:**
- Per-key RPM/TPM limits
- Automatic tracking en DB
- Headers: `x-ratelimit-limit-requests`

**Model Aliases:**
```yaml
model_list:
  - model_name: luigi-thinking
    litellm_params:
      model: minimax/MiniMax-M2.7
      api_base: https://api.minimax.io/v1
```

**Database Schema (PostgreSQL):**
- `LiteLLM_VerificationToken` - API keys
- `LiteLLM_UserTable` - Users with budgets
- `LiteLLM_SpendLogs` - Cost tracking

---

## 16. Tests

### 16.1 Unit Tests

**Backend:**
```python
# tests/test_auth.py
def test_signup():
    response = client.post("/auth/signup", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 201
    assert "api_key" in response.json()

def test_login():
    # ... test login flow
```

**Frontend:**
```typescript
// tests/lib/auth.test.ts
test('login flow', async () => {
  const response = await fetch('/auth/login', {...});
  expect(response.ok).toBe(true);
});
```

### 16.2 Integration Tests

```python
# tests/test_integration.py
def test_signup_to_chat_flow():
    # 1. Signup
    signup_response = client.post("/auth/signup", json={...})
    assert signup_response.status_code == 201
    api_key = signup_response.json()["api_key"]
    
    # 2. Create chat
    chat_response = client.post("/chats/", headers={
        "Authorization": f"Bearer {api_key}"
    })
    assert chat_response.status_code == 201
    
    # 3. Send message
    message_response = client.post(f"/chats/{chat_id}/messages", json={
        "content": "Hello!"
    })
    assert message_response.status_code == 200
```

### 16.3 E2E Tests (Playwright)

```typescript
// tests/e2e/chat.spec.ts
test('complete chat flow', async ({ page }) => {
  await page.goto('/auth/signup');
  await page.fill('[name="email"]', 'test@example.com');
  await page.fill('[name="password"]', 'password123');
  await page.click('button[type="submit"]');
  
  await page.waitForURL('/');
  await page.fill('textarea[name="message"]', 'Hello!');
  await page.click('button:has-text("Send")');
  
  await expect(page.locator('.message-assistant')).toBeVisible();
});
```

---

## Anexo: Glosario

| Término | Descripción |
|---------|-------------|
| TTS | Text-to-Speech |
| STT | Speech-to-Speech |
| RPM | Requests Per Minute |
| TPM | Tokens Per Minute |
| JWT | JSON Web Token |
| ORM | Object-Relational Mapping |
| TTS | Text-to-Speech |

---

## Anexo: Puertos

| Servicio | Puerto | URL |
|----------|--------|-----|
| Frontend | 3000 | http://localhost:3000 |
| Backend | 8080 | http://localhost:8080 |
| LiteLLM | 4000 | http://localhost:4000 |
| PostgreSQL | 5432 | postgresql://localhost:5432 |
| Redis | 6379 | redis://localhost:6379 |

---

---

## 17. Guía de Uso

### 17.1 Login como Admin

**Endpoint:** `POST /api/auth/login`

```bash
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "tu-password"}'
```

**Respuesta exitosa:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "email": "admin@example.com",
    "role": "admin",
    "theme": "dark",
    "primary_color": "#7000FF"
  }
}
```

**Usando el frontend:**
1. Navega a `http://localhost:3000/auth/login`
2. Ingresa el email y password configurados durante `install.sh`
3. Serás redirigido al chat principal

**Credenciales por defecto (si se usaron los valores default):**
- Email: `admin@example.com`
- Password: La que configuraste durante la instalación

### 17.2 Roles y Permisos

| Rol | Permisos |
|-----|----------|
| `admin` | CRUD all users, view all chats, manage API keys, view spend logs |
| `user` | CRUD own chats, use chat, view own stats |

### 17.3 Endpoints de Frontend

| Ruta | Descripción |
|------|-------------|
| `/auth/login` | Página de login |
| `/auth/signup` | Página de registro |
| `/` | Chat principal |
| `/workspace/settings` | Configuración de usuario |
| `/admin/users` | Panel de administración (solo admin) |

### 17.4 Solución de Problemas

**Error 404 en login:**
- Verifica que el backend esté corriendo en el puerto 8080
- Verifica que `VITE_PUBLIC_API_URL` en `.env` apunte a `http://localhost:8080`

**Error "undefined" en la URL:**
- Asegúrate de que el archivo `.env` usa el prefijo `VITE_` (ej: `VITE_PUBLIC_API_URL=http://localhost:8080`)
- Reinicia el servidor de desarrollo después de cambios en `.env`

**Token expirado:**
- El access token expira en 1 hora
- Usa `POST /api/auth/refresh` para obtener un nuevo token

---

## 18. SEO

### 18.1 Meta Tags por Página

**Login (`/auth/login`):**
```html
<title>Sign In - Luigi Chat</title>
<meta name="description" content="Sign in to your Luigi Chat account..." />
<meta name="robots" content="noindex, nofollow" />
```

**Signup (`/auth/signup`):**
```html
<title>Sign Up - Luigi Chat</title>
<meta name="description" content="Create your Luigi Chat account..." />
<meta name="robots" content="noindex, nofollow" />
```

### 18.2 Open Graph y Twitter Cards

Todas las páginas públicas incluyen:
- `og:title`, `og:description`, `og:type`
- `twitter:card`, `twitter:title`, `twitter:description`

### 18.3 Robots

Las páginas de auth (`/auth/login`, `/auth/signup`) tienen `noindex, nofollow` para evitarindexación de motores de búsqueda.

---

## 19. Variables de Entorno Frontend

| Variable | Default | Descripción |
|----------|---------|-------------|
| `VITE_PUBLIC_API_URL` | `http://localhost:8080` | URL del backend API |
| `VITE_PUBLIC_APP_FONT` | Sistema default | Font principal de la app |

---

**Versión**: 1.0.0
**Última actualización**: 2026-04-02

# Luigi Chat - TODO Checklist
# Usa el skill 'luigi-dev-workflow' para tracking de progreso

## Fase 1: Setup y Configuración

- [x] Crear estructura de carpetas
- [x] Crear SPEC.md con todas las especificaciones
- [x] Crear TODO.md con checklist
- [x] Crear skill 'luigi-dev-workflow'
- [x] Crear `.env.example` con todas las variables
- [x] Crear `docker-compose.yaml` (desarrollo)
- [x] Crear `docker-compose.prod.yaml` (producción)
- [x] Crear `Makefile` con comandos útiles

## Fase 2: Backend - Core

- [x] `backend/requirements.txt` - dependencias Python
- [x] `backend/app/main.py` - FastAPI entry point
- [x] `backend/app/config.py` - Configuración de app
- [x] `backend/app/models/database.py` - SQLAlchemy models
- [x] `backend/app/utils/auth.py` - JWT utilities
- [x] `backend/app/utils/rate_limit.py` - Rate limiting utils

## Fase 3: Backend - Auth System

- [x] `backend/app/routers/auth.py` - signup, login, logout
- [x] Auto-generación de LiteLLM API key al registrar
- [x] JWT token management
- [x] Password hashing con bcrypt
- [x] Session management

## Fase 4: Backend - API Routers

- [x] `backend/app/routers/users.py` - CRUD usuarios (admin)
- [x] `backend/app/routers/chats.py` - Historial de chats
- [x] `backend/app/routers/files.py` - MiniMax File API proxy
- [x] `backend/app/routers/audio.py` - TTS endpoint
- [x] `backend/app/routers/models.py` - Lista de modelos disponibles

## Fase 5: Backend - Services

- [x] `backend/app/services/litellm.py` - Wrapper LiteLLM client
- [x] `backend/app/services/minimax.py` - MiniMax API client
- [x] `backend/app/services/file_service.py` - File upload/download (integrado en routers/files.py)
- [x] `backend/app/services/audio_service.py` - TTS service (integrado en routers/audio.py)

## Fase 6: LiteLLM Configuration

- [x] `litellm/config.yaml` - Model aliases
- [x] `litellm/model_aliases` - luigi-thinking, luigi-vision, luigi-voice
- [x] Rate limiting config (3 RPM por defecto)
- [x] Database connection (PostgreSQL)
- [x] Redis connection para cache/sessions

## Fase 7: Frontend - Base (OpenWebUI Fork)

- [x] Clonar/fork de OpenWebUI base
- [x] Branding: cambiar "Open WebUI" → "Luigi Chat"
- [x] Configurar tema base
- [x] SvelteKit setup

## Fase 8: Frontend - Auth Pages

- [x] `frontend/src/routes/auth/login/+page.svelte`
- [x] `frontend/src/routes/auth/signup/+page.svelte`
- [x] Integración con backend auth API
- [x] JWT token storage

## Fase 9: Frontend - Chat Interface

- [x] `frontend/src/routes/(app)/+page.svelte` - Chat principal
- [x] `frontend/src/lib/components/chat/ChatInterface.svelte`
- [x] `frontend/src/lib/components/chat/ChatInput.svelte`
- [x] `frontend/src/lib/components/chat/Messages.svelte`
- [x] Streaming de respuestas
- [x] Upload de imágenes (luigi-vision)

## Fase 10: Frontend - Voice (TTS)

- [x] Voice recorder component
- [x] Audio player component
- [x] Integración con `luigi-voice` endpoint
- [x] WebSocket para TTS streaming (MiniMax Speech 2.6)

## Fase 11: Frontend - Personalización

- [x] Theme selector (light/dark/auto)
- [x] Color picker para tema
- [x] Guardar preferencias en backend
- [x] Selector de modelo por defecto

## Fase 12: Frontend - Admin Panel

- [x] `frontend/src/routes/admin/+page.svelte`
- [x] Lista de usuarios
- [x] Crear/editar/eliminar usuarios
- [x] Ver API keys y uso
- [ ] Estadísticas de spend

## Fase 13: Testing

- [ ] Tests unitarios: auth
- [x] Tests unitarios: API endpoints
- [ ] Tests de integración: flujo registro → chat
- [ ] Tests de integración: upload de imagen
- [ ] Tests de integración: TTS
- [ ] Docker Compose test (levantando todos los servicios)

## Fase 14: Documentación

- [ ] README.md completo
- [ ] API documentation (OpenAPI/Swagger)
- [ ] Guía de desarrollo
- [ ] Guía de deployment

## Fase 15: Deployment

- [x] Push a GitHub
- [ ] Setup CI/CD (GitHub Actions)
- [ ] Docker image builds
- [ ] Deployment a producción

---

## Modelos MiniMax Configurados

| Alias | Modelo Real | Uso |
|-------|-------------|-----|
| `luigi-thinking` | `minimax/MiniMax-M2.7` | Chat/razonamiento |
| `luigi-vision` | `minimax/MiniMax-Text-01` | Análisis de imágenes |
| `luigi-voice` | `minimax/speech-2.6-hd` | TTS |

## Rate Limits

| Tipo | Límite |
|------|--------|
| Requests por minuto (RPM) | 3 |
| Tokens por minuto (TPM) | 6000 |

## Variables de Entorno Requeridas

```bash
# LiteLLM
LITELLM_MASTER_KEY=sk-...
DATABASE_URL=postgresql://...
REDIS_URL=redis://...

# MiniMax
MINIMAX_API_KEY=...

# Backend
SECRET_KEY=...
WEBUI_NAME="Luigi Chat"

# Frontend
PUBLIC_API_URL=http://localhost:8080
```

## Flujo de Pruebas

### Test 1: Registro → Chat
```
1. POST /auth/signup → Verificar API key generada
2. POST /chats/ → Crear chat
3. POST /chats/{id}/messages → Enviar mensaje
4. Verificar streaming response
5. GET /chats/{id} → Verificar mensaje guardado
```

### Test 2: Rate Limiting
```
1. Usar API key
2. Hacer 3 requests en 1 minuto → Todos OK
3. Request 4 → 429 Too Many Requests
4. Esperar 60 segundos
5. Request 5 → OK nuevamente
```

### Test 3: Visión
```
1. POST /files/upload → Subir imagen
2. POST /chats/{id}/messages con image_urls → Usar luigi-vision
3. Verificar análisis de imagen en respuesta
```

### Test 4: TTS
```
1. POST /audio/speech → Generar audio
2. Verificar audio stream
3. Verificar latencia < 250ms
```

---

**Para más detalles ver:** `SPEC.md` y skill `luigi-dev-workflow`

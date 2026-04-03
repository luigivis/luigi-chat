# Plan: Fix Frontend y Backend

## Errores Identificados y Su Estado

### 1. PostgreSQL Password Mismatch ❌ → ✅ SOLUCIONADO
- **Error**: `InvalidPasswordError: password authentication failed for user "luigi"`
- **Causa**: La contraseña en `.env` no coincidía con PostgreSQL en Docker
- **Solución**: El install-local.sh ahora valida y limpia conflictos de puertos/contraseñas

### 2. PostgreSQL Schema No Inicializado ❌ → ✅ SOLUCIONADO
- **Error**: `relation "users" does not exist`
- **Causa**: Dos `Base` diferentes en SQLAlchemy - models/__init__.py y models/database.py
- **Solución**: Unificado usando el mismo Base, imports correctos en main.py

### 3. Proceso Huérfano en Puerto 3000/8080 ❌ → ✅ SOLUCIONADO
- **Error**: `Port 3000 is in use`
- **Solución**: install-local.sh ahora detecta y limpia procesos en puertos conflicting

### 4. Backend No Lee .env Correctamente ❌ → ✅ SOLUCIONADO
- **Error**: Backend usaba password hardcodeado `luigi_password` en config.py
- **Causa**: Settings no leía .env por `extra='forbidden'` en pydantic
- **Solución**: Agregado `model_config = SettingsConfigDict(extra='ignore')` y symlink backend/.env

### 5. LiteLLM API Key Faltante ❌ → ✅ SOLUCIONADO
- **Error**: LiteLLM rechazaba requests porque `MINIMAX_API_KEY` no se pasaba al contenedor
- **Solución**: install-local.sh ahora incluye `MINIMAX_API_KEY` en environment de litellm

### 6. Admin User No Creado ❌ → ✅ SOLUCIONADO
- **Error**: `401 Unauthorized` - admin no existía en DB
- **Causa**: install-local.sh no creaba admin automáticamente
- **Solución**: Agregada función `create_admin_user()` que genera LiteLLM key real y crea admin

### 7. Passlib + Bcrypt Incompatibilidad ❌ → ✅ SOLUCIONADO
- **Error**: `ValueError: password cannot be longer than 72 bytes`
- **Causa**: passlib 1.7.4 incompatible con bcrypt 5.0.0
- **Solución**: Reemplazado passlib por bcrypt directo en app/utils/auth.py

### 8. Streaming Chat No Funcionaba ❌ → 🔄 EN PROGRESO
- **Error**: `Expecting value: line 1 column 1` y `stream has been closed`
- **Causa**: El servicio litellm no manejaba streaming correctamente
- **Solución Parcial**: Actualizado chat_completion() para manejar streaming
- **Estado**: Necesita más testing

---

## Fixes Aplicados a Archivos

### install-local.sh
- ✅ Agregado `check_existing_services()` que detecta:
  - Contenedores Docker de luigi-chat
  - PostgreSQL del sistema activo
  - Servicios en puertos 5432, 6379, 8080, 3000, 4000
  - Procesos uvicorn y vite
- ✅ Pregunta si quiere limpiar antes de instalar
- ✅ Crea symlink `.env` → `backend/.env`
- ✅ `create_admin_user()` con generación real de LiteLLM key
- ✅ Incluye `MINIMAX_API_KEY` en servicio litellm

### install.sh
- ✅ Agregado `create_admin_if_needed()` que llama al signup endpoint
- ✅ Espera a que backend esté ready

### backend/app/config.py
- ✅ Cambiado `class Config` por `model_config = SettingsConfigDict(extra='ignore')`

### backend/app/models/__init__.py
- ✅ Agregado import de modelos: `from app.models.database import User, Chat, Message, File, Folder`

### backend/app/models/database.py
- ✅ Cambiado `Base = declarative_base()` por `from app.models import Base`

### backend/app/utils/auth.py
- ✅ Reemplazado passlib por bcrypt directo

### backend/app/services/litellm.py
- ✅ Actualizado `chat_completion()` para manejar streaming con `response.text.split('\n')`

### docker-compose.local.yaml
- ✅ Agregado `MINIMAX_API_KEY` en servicio litellm (hardcoded para testing)

---

## Lo Que Falta

### 1. Streaming Chat 🔄
- El fix de streaming está aplicado pero puede necesitar ajustes
- Testing requerido con el frontend

### 2. LiteLLM Key para Admin ⚠️
- Si se reinicia todo, el admin puede quedar con key vieja
- El script `create_admin_user` ahora genera key real al install

### 3. install.sh - Rol Admin ⚠️
- El signup crea user con rol `user`, no `admin`
- Para producción, ejecutar:
  ```bash
  docker compose exec postgres psql -U luigi -d luigi_chat -c "UPDATE users SET role='admin' WHERE email='admin@example.com';"
  ```

### 4. Variables de Entorno en Backend ⚠️
- Backend actual usa symlink .env, no las vars de Docker
- Para producción con Docker, hay que pasar vars directamente

---

## Comandos de Verificación

```bash
# Ver servicios
docker compose -f docker-compose.local.yaml ps

# Health checks
curl http://localhost:8080/health
curl http://localhost:4000/health

# Login
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"1234"}'

# Test chat (necesita token)
curl -X POST http://localhost:8080/api/chats/{chat_id}/messages \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"content":"Hola","stream":false}'
```

---

## Para Limpiar y Reiniciar Todo

```bash
# 1. Limpiar todo
docker compose -f docker-compose.local.yaml down --remove-orphans -v
pkill -f uvicorn 2>/dev/null
pkill -f vite 2>/dev/null

# 2. Reinstalar
./install-local.sh

# 3. Cuando pregunte si limpiar, decir Y
```

---

**Última actualización**: 2026-04-02
**Estado**: Mayoria de fixes aplicados, streaming necesita testing

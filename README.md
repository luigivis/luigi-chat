# Luigi Chat

Rebuild de OpenWebUI con integración MiniMax y LiteLLM.

## Características

- 🤖 **Modelos MiniMax**: luigi-thinking (M2.7), luigi-vision (Text-01), luigi-voice (Speech 2.6)
- 🔐 **Auth con API Keys**: Auto-generación de keys OpenAI-compatibles al registrarse
- ⏱️ **Rate Limiting**: 3 RPM por defecto por usuario
- 🎨 **UI Customizable**: Cada usuario personaliza su tema y preferencias
- 📁 **MiniMax File API**: Upload y gestión de archivos
- 🔊 **TTS con Speech 2.6**: Text-to-Speech con <250ms latencia

## Stack Tecnológico

| Capa | Tecnología |
|------|------------|
| Backend | FastAPI |
| Frontend | SvelteKit (OpenWebUI fork) |
| Database | PostgreSQL |
| Cache | Redis |
| AI Gateway | LiteLLM Proxy |

## Inicio Rápido

### 1. Configurar Variables de Entorno

```bash
cp .env.example .env
# Editar .env con tus credenciales
```

### 2. Levantar Servicios

```bash
docker-compose up -d
```

### 3. Acceder a la Aplicación

- Frontend: http://localhost:3000
- Backend API: http://localhost:8080
- LiteLLM Proxy: http://localhost:4000

## Modelos

| Alias | Modelo Real | Uso |
|-------|-------------|-----|
| `luigi-thinking` | MiniMax-M2.7 | Chat/razonamiento |
| `luigi-vision` | MiniMax-Text-01 | Análisis de imágenes |
| `luigi-voice` | MiniMax-Speech-2.6-HD | Text-to-Speech |

## Desarrollo

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API Keys

Las API keys se generan automáticamente al registrarse. Son compatibles con el SDK de OpenAI:

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-...",
    base_url="http://localhost:4000"
)

response = client.chat.completions.create(
    model="luigi-thinking",
    messages=[{"role": "user", "content": "Hola!"}]
)
```

## Documentación

- [SPEC.md](./SPEC.md) - Especificaciones técnicas completas
- [TODO.md](./TODO.md) - Checklist de implementación

## Licencia

MIT

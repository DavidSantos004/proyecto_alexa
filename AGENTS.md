# JARVIS OS — Personal Intelligence Operating System

## Qué es esto y qué NO es

Este proyecto NO es un chatbot. Es un Sistema Operativo de Inteligencia Personal:
un ecosistema de IA, automatización, domótica, memoria persistente y agentes
inteligentes, diseñado con potencial de convertirse en producto comercial.

El desarrollador (David) es estudiante de Tecnología en Desarrollo de Sistemas
Informáticos. El objetivo del proyecto es doble: (1) construir un asistente
personal real, y (2) que David se forme como arquitecto de software en el
proceso — arquitectura, backend, IA, Docker, DevOps, Linux, redes, diseño de
APIs, domótica, LLMs, orquestación de agentes. No se trata solo de terminar el
proyecto, sino de aprender ingeniería de software mientras se construye.

## Filosofía central (no negociable)

Los LLMs **nunca ejecutan acciones directamente** — únicamente las **proponen**.
El `OrchestratorService` es el único componente que decide si una acción
propuesta se ejecuta. Ningún módulo debe saltarse esta regla, sin importar cuán
simple parezca la acción.

## Arquitectura

**Modular Monolith** — un solo servicio FastAPI, NO microservicios. Esta fue
una decisión deliberada tras evaluar microservicios desde el día 1: con un solo
desarrollador y sin necesidad de escalar por separado, microservicios habrían
agregado complejidad de infraestructura (múltiples contenedores, debugging
distribuido, contratos entre servicios) sin ningún beneficio real en esta
etapa. La regla "monolith first" (Fowler) aplica aquí.

Cada módulo interno bajo `app/` sigue Clean Architecture en miniatura:
- `domain/` — modelos Pydantic puros, sin dependencias de infraestructura
- `ports/` — interfaces (Protocol) que el módulo espera de sus dependencias.
  HOY solo contienen interfaces, sin implementación real — eso llega en un
  sprint posterior cuando se conecte Postgres/Home Assistant de verdad.
- `service.py` — lógica de negocio, usa los ports, nunca importa directamente
  la implementación concreta de otro módulo.

Módulos: `orchestrator/`, `llm_service/`, `memory/`, `devices/`, `automation/`,
`auth/`, `notifications/`, `voice_interface/`.

Extracción a microservicios reales solo se evaluará más adelante, y solo si
un módulo específico tiene una razón concreta para separarse (ej. `llm_service`
necesitando GPU dedicada en otra máquina).

## Hardware objetivo

Todo el desarrollo debe pensarse para correr eventualmente en una **Raspberry
Pi 5 (8GB)**. Esto implica cuidado con el consumo de memoria: Postgres + Redis
(cuando se agregue) + Ollama + modelos LLM cuantizados todos compitiendo por
8GB. Preferir modelos pequeños (3B-7B cuantizados) y no asumir recursos
ilimitados al diseñar.

## Stack

Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic, PostgreSQL 16,
Docker, Docker Compose. IA vía Ollama (Qwen, Gemma, Llama, Mistral como
opciones locales). Frontend futuro: React + Vite + TailwindCSS + TanStack
Query + Zustand (no se toca hasta que el backend tenga contratos de API
estables).

## Restricciones conocidas del Voice Interface (Alexa) — decisiones ya tomadas

Alexa es un **periférico de entrada/salida**, nunca el cerebro del sistema.
Decisiones de diseño ya validadas:

- No hay wake word personalizada — el usuario dice "Alexa, dile a Jarvis que…".
  "Alexa" activa el dispositivo, "Jarvis" es el nombre de invocación de la skill.
- No existe acceso a audio crudo del micrófono ni control genérico de
  Bluetooth vía Alexa Skills Kit — son limitaciones de plataforma, no del
  diseño del proyecto.
- El intent debe usar `AMAZON.SearchQuery` para capturar frase libre en vez de
  patrones rígidos.
- Respuestas deben generarse vía TTS propio (ej. Piper) y devolverse a Alexa
  como audio mediante la interfaz AudioPlayer — no se usa la voz nativa de
  Alexa.
- El backend tiene ~8 segundos para responder en el flujo estándar de skills;
  esto debe considerarse al diseñar la latencia del LLM.
- El endpoint puede ser HTTPS custom (vía Nginx) en vez de Lambda, para evitar
  dependencia de AWS.

## Roadmap de Sprints

- **Sprint 0** (completado): entorno de desarrollo — Linux nativo (dual boot,
  luego migrado a Linux como único SO), Docker, Git, VS Code, Python, OpenCode.
- **Sprint 1** (completado): esqueleto del monolito modular + modelos Pydantic
  del Orchestrator (`ProposedAction`, `OrchestratorDecision`) + función
  `decide()` con auto-aprobación temporal documentada como tal + endpoint
  `POST /orchestrator/propose`.
- **Sprint 2** (completado): Memory Service — modelo de datos sobre Postgres
  (SQL relacional, key-value para hechos + tabla de conversaciones), Repository
  Pattern, adapter SQLAlchemy, migración Alembic.
- **Sprint 3** (completado): LLM Service con Ollama — el LLM propone acciones
  estructuradas (JSON), nunca texto libre ejecutable.
- **Sprint 4** (completado): Device Service + Home Assistant — wrapper que traduce
  acciones aprobadas a llamadas de Home Assistant; Bluetooth crudo vía
  `bluetoothctl` (pendiente de implementar).
- **Sprint 5**: Voice Interface (Alexa Skill) — solo después de que Orchestrator
  + LLM + Memory + Devices funcionen de extremo a extremo por texto/API.
- **Sprint 6**: Automation Service — reglas y triggers proactivos.
- **Sprint 7+**: Auth, Notifications, hardening. Evaluación de si algún módulo
  amerita separarse a microservicio real.

## Modelo de riesgo del Orchestrator (decisión pendiente, documentada)

El campo `risk_level` existe en `ProposedAction` desde Sprint 1, pero
**no se usa aún para tomar decisiones** — todo se auto-aprueba temporalmente
por decisión explícita de David. El campo se diseñó completo desde ahora para
evitar una migración de datos futura. Cuando se defina el sistema de riesgo
real, solo debe cambiar el cuerpo de `decide()` — el resto del sistema
(modelos, endpoints, servicios) no debería tocarse.

## Forma de trabajar (no negociable)

- Explica la decisión técnica y el "por qué" ANTES de escribir código, siempre.
- No generes más de un módulo de código sin pausar para confirmación.
- Si un enfoque solicitado no es buena arquitectura, dilo explícitamente y
  propone una alternativa — no simplemente cumplas la instrucción.
- El usuario quiere entender cada línea, no copiar y pegar sin comprender.
  Prioriza claridad sobre ingenio.
- Nunca clases gigantes, nunca funciones enormes. Repository Pattern, Service
  Layer, Dependency Injection, SOLID en todo momento.
- Trabajo por Sprints: cada uno con objetivos, diseño, implementación,
  pruebas, refactorización — no se empieza a programar sin diseñar primero.

## Convenciones de código

- `StrEnum` para todos los tipos enumerados (`ActionSource`, `DecisionVerdict`, etc.)
- `action_id` generado vía `uuid4().hex` al crear `ProposedAction`
- `ports/__init__.py` lleva docstring explícito: solo interfaces, implementación diferida
- Ruff: line-length 88, reglas `E,F,I,N,W`
- Tests con pytest, basados en clases con `setup_method` (sin fixtures aún)
- Rutas de test reflejan la estructura de `app/`: `tests/test_orchestrator/`, etc.
- Cada test file debe tener un nombre ÚNICO (ej. `test_orchestrator_service.py`, no `test_service.py`) para evitar colisiones de módulo entre paquetes.

## Comandos

```bash
# instalar (desde .venv o docker)
pip install -e ".[dev]"

# correr servidor de desarrollo (modo fakes — default)
JARVIS_USE_FAKES=true uvicorn app.main:app --reload

# correr servidor con servicios reales (Postgres + Ollama)
docker compose up -d db ollama
alembic upgrade head
JARVIS_USE_FAKES=false OLLAMA_BASE_URL=http://localhost:11434 \
  DATABASE_URL=postgresql://jarvis:jarvis@localhost:5432/jarvis_os \
  uvicorn app.main:app --reload

# tests (paquete específico)
python -m pytest tests/test_orchestrator/ -v

# tests con DB real
DATABASE_URL=postgresql://jarvis:jarvis@localhost:5432/jarvis_os \
  python -m pytest tests/test_memory/ -v

# lint
ruff check .

# docker
docker compose up --build
```

## Estado actual (Sprint 4 — completado)

- `orchestrator/` completo: modelos, service con decide(), endpoint `POST /orchestrator/propose`.
- `memory/` completo: modelos Fact/ConversationEntry, SQLAlchemy repository, MemoryService, migración Alembic.
- `llm_service/` completo: modelos LLMContext/LLMResponse, puerto LLMPort, OllamaClient, LLMService con prompt estructurado y parseo JSON.
- `devices/` completo: modelos DeviceCommand/DeviceResult, puerto DevicePort, HomeAssistantClient, DeviceService.
- `api/` completo: ChatService (orquestación LLM→Orchestrator→Memory→Devices), POST /api/chat, dependencias con fakes por default.
- `infrastructure/database.py`: engine + session factory.
- Sin auth, sin decisiones reales de riesgo — todo auto-aprobado temporalmente.
- Postgres y Ollama disponibles en docker-compose.
- Pipeline real verificado: LLM Service con Ollama `qwen2.5:3b` + Memory Service con Postgres 16 + Orchestrator auto-aprueba + Device Service (HA_TOKEN pendiente).
- 29 tests pasando, lint limpio (`ruff check .`).
- 6 commits en main (Sprint 0+1, Sprint 2, Sprint 3, Sprint 4, Pipeline e2e, Pipeline real).
- Postman collection: `jarvis-os.postman_collection.json`.
- Repo: `git@github.com:DavidSantos004/proyecto_alexa.git`
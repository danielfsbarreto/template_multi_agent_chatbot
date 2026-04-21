# Multi-Agent Chatbot

<img width="1478" height="1527" alt="image" src="https://github.com/user-attachments/assets/9fd3d0af-d09f-4965-98f7-a853c98d8371" />


A conversational chatbot built with [CrewAI Flows](https://docs.crewai.com), deployed to [CrewAI AMP](https://docs.crewai.com/en/enterprise), with a Discord-style web UI driven by Flask and vanilla JS.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Browser (vanilla HTML/CSS/JS)                                  │
│  ├── Renders chat channels, messages, images, markdown          │
│  ├── Sends messages via REST → Flask                            │
│  └── Receives real-time updates via SSE ← Flask                 │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP
┌────────────────────────▼────────────────────────────────────────┐
│  Flask UI Server  (ui_template_multi_agent_chatbot/)            │
│  ├── Manages channels & messages in SQLite                      │
│  ├── Proxies /kickoff requests to CrewAI AMP                    │
│  ├── Receives webhook events, broadcasts them as SSE            │
│  └── Exposed publicly via ngrok                                 │
└──────┬──────────────────────────────────────────┬───────────────┘
       │ POST /kickoff                            ▲ POST /api/webhook
       ▼                                          │
┌──────────────────┐                   ┌──────────┴───────────┐
│  CrewAI AMP      │───events─────────▶│  webhook.site        │
│  (deployed flow) │                   │  (XHR redirect)      │
└──────────────────┘                   └──────────────────────┘
```

### Request lifecycle

1. User types a message in the browser.
2. Flask saves it to SQLite, returns `202`, and fires a background `POST /kickoff` to AMP with the channel's `conversation_id` as the flow state `id` + `user_message`.
3. AMP runs the `ConversationalFlow` — `@persist()` restores the state (including prior `messages`) using the flow's `id`, appends the new user message, and hands off to the `HandleUserMessageCrew`.
4. The crew's agent reasons over the conversation and calls tools (`SendMessageToUser`, `NanoBananaImageGeneration`, etc.). Each tool emits events through the `ConversationalEventBus`.
5. The `ConversationalEventListener` catches those events, stamps them with `conversation_id`, and dispatches them to `webhook.site` via the `Dispatcher` client.
6. `webhook.site` XHR-redirects each event to the Flask server's `/api/webhook` endpoint.
7. Flask persists `message_created` / `image_generated` payloads to SQLite and broadcasts all events to connected browsers via SSE.

## Back-End (`src/template_multi_agent_chatbot/`)

### Flow — `main.py`

`ConversationalFlow` is a CrewAI `Flow[ConversationalState]` with two steps:


| Step                   | Decorator                       | What it does                                                                                               |
| ---------------------- | ------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `load_initial_context` | `@start()`                      | Registers the event listener and appends the new user message to state. |
| `handle_new_message`   | `@listen(load_initial_context)` | Instantiates and executes the `HandleUserMessageCrew`.                  |

The flow is decorated with `@persist()`, which automatically saves and restores `ConversationalState` across kickoffs using the flow state's `id` (a UUID passed by the UI as the conversation identifier). State fields: `user_message` and `messages` (the full conversation history, accumulated over time).

### Crew — `crews/handle_user_message_crew.py`

A single-agent, single-task, sequential `Crew`:

- **Agent**: `CrewAI Conversational Assistant` powered by `claude-haiku-4-5`, equipped with skills (image generation, internet searching, user communication) and tools.
- **Task**: Interpret the latest user message using the last 10 messages as context, respond helpfully, and always communicate via the `SendMessageToUser` tool.

### Tools


| Tool                                  | Description                                                                                                                                      |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `SendMessageToUserTool`               | Emits a `MessageCreated` event so the user sees the agent's reply.                                                                               |
| `NanoBananaImageGenerationTool`       | Generates an image via Gemini (`gemini-3.1-flash-image-preview`), emits both a `MessageCreated` (file path) and `ImageGenerated` (base64) event. |
| `NanoBananaImageEditingTool`          | Edits an existing image via Gemini with a text prompt, same event pattern as generation.                                                         |
| `SerperDevTool` / `ScrapeWebsiteTool` | Web search and scraping (from `crewai_tools`).                                                                                                   |


### Event System

The event system is the bridge between the CrewAI agent running in AMP and the external UI.

**Custom event types** (`events/types/`):

- `MessageCreated` — carries `result.message` (role + content).
- `ImageGenerated` — carries `result.image` (base64-encoded PNG).

`**ConversationalEventBus`** (`events/conversational_event_bus.py`):

- Wraps the CrewAI event bus. Tools call `emit_message_created()` / `emit_image_generated()` on it.
- Appends messages to flow state before emitting (persisted automatically by `@persist()`).
- `register_listener()` creates a `ConversationalEventListener` keyed by `state.id` (called at the start of the flow, after state is populated).

`**ConversationalEventListener**` (`events/listeners/conversational_event_listener.py`):

- A `BaseEventListener` that subscribes to `MessageCreated`, `ImageGenerated`, `LLMStreamChunkEvent`, `LLMThinkingChunkEvent`, and `AgentExecutionCompletedEvent`.
- Stamps each event with `source_fingerprint` and `fingerprint_metadata.conversation_id`.
- Dispatches every event to the external webhook via the `Dispatcher` client.

`**Dispatcher**` (`events/clients/dispatcher.py`):

- Simple HTTP POST client that sends JSON event payloads to `DISPATCHER_URL` (webhook.site) with bearer auth.

## UI (`ui_template_multi_agent_chatbot/`)

Flask app with a Discord-inspired dark theme.

- **Channels**: each channel maps to a `conversation_id` (UUID generated on creation). Multiple concurrent conversations.
- **SQLite** (`db/chatbot.db`): stores channels and messages with `event_id`-based deduplication.
- **SSE**: each browser tab subscribes to `/api/channels/<id>/events` for real-time updates.
- **Webhook receiver** (`POST /api/webhook`): receives events forwarded from webhook.site, matches them to channels via `fingerprint_metadata.conversation_id`, persists messages/images, and broadcasts all event types over SSE.
- **Frontend** (`static/js/app.js`): renders messages with markdown support (via `marked.js`), displays base64 images inline, shows a "CrewAI is thinking..." indicator on `kickoff_started` and hides it on `agent_execution_completed`.

## Setup

**Requirements**: Python >= 3.10, < 3.14 · [uv](https://docs.astral.sh/uv/) · [ngrok](https://ngrok.com/) (with `crewai-chatbot.ngrok.io` domain)

1. Copy `.env.example` to `.env` and fill in the keys:

  | Key                 | Purpose                                    |
  | ------------------- | ------------------------------------------ |
  | `ANTHROPIC_API_KEY` | LLM for the conversational agent           |
  | `GEMINI_API_KEY`    | Image generation / editing                 |
  | `SERPER_API_KEY`    | Web search                                 |
  | `DISPATCHER_URL`    | Webhook.site endpoint for event forwarding |
  | `DISPATCHER_KEY`    | Bearer token for the dispatcher            |
  | `DEPLOYMENT_URL`    | CrewAI AMP deployment URL                  |
  | `DEPLOYMENT_KEY`    | CrewAI AMP API key                         |

2. Deploy the flow to CrewAI AMP:
  ```bash
   crewai deploy
  ```
3. Configure `webhook.site` to XHR-redirect incoming events to `https://crewai-chatbot.ngrok.io/api/webhook`.
4. Start the UI:
  ```bash
   bin/start
  ```
   This installs dependencies, wakes up AMP, starts Flask on port 5005, and opens an ngrok tunnel.
5. Open `http://localhost:5005` (or `https://crewai-chatbot.ngrok.io`), create a channel, and start chatting.


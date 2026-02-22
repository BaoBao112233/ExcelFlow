# AI Gateway Architecture

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        ExcelFlow App                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ uses
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Excel Agent                              │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              AI Gateway Instance                          │  │
│  │                                                           │  │
│  │  ┌─────────────┐                                         │  │
│  │  │   Config    │  ◄──── .env / Environment Variables     │  │
│  │  │             │        AI_PROVIDER=openai               │  │
│  │  │  - provider │        OPENAI_API_KEY=...               │  │
│  │  │  - model    │        ANTHROPIC_API_KEY=...            │  │
│  │  │  - api_keys │        GOOGLE_API_KEY=...               │  │
│  │  └──────┬──────┘                                          │  │
│  │         │                                                 │  │
│  │         │ creates & manages                               │  │
│  │         ▼                                                 │  │
│  │  ┌─────────────────────────────────────────┐             │  │
│  │  │      Current Provider Instance          │             │  │
│  │  │                                         │             │  │
│  │  │  One of:                                │             │  │
│  │  │  ┌──────────────┐  ┌──────────────┐    │             │  │
│  │  │  │   OpenAI     │  │  Anthropic   │    │             │  │
│  │  │  │   Provider   │  │   Provider   │    │             │  │
│  │  │  └──────────────┘  └──────────────┘    │             │  │
│  │  │         ┌──────────────┐                │             │  │
│  │  │         │    Google    │                │             │  │
│  │  │         │   Provider   │                │             │  │
│  │  │         └──────────────┘                │             │  │
│  │  └─────────────────┬───────────────────────┘             │  │
│  │                    │                                     │  │
│  │                    │ chat_completion()                   │  │
│  │                    │                                     │  │
│  │                    ▼                                     │  │
│  │         Normalized Response Format                      │  │
│  │         {                                               │  │
│  │           "content": "...",                             │  │
│  │           "tool_calls": [...],                          │  │
│  │           "finish_reason": "stop"                       │  │
│  │         }                                               │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ normalized response
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Excel Operations                            │
│  (read_cell, update_cell, summarize_range, etc.)                │
└─────────────────────────────────────────────────────────────────┘
```

## Component Hierarchy

```
backend/app/
├── agent.py                    # Excel Agent - main application logic
│   └── uses AIGateway
│
└── ai_gateway/                 # AI Gateway Package
    ├── __init__.py
    ├── base_provider.py        # Abstract base class
    │   └── BaseAIProvider
    │       ├── chat_completion()  [abstract]
    │       ├── get_provider_name() [abstract]
    │       ├── normalize_tool_format()
    │       └── normalize_response()
    │
    ├── openai_provider.py      # OpenAI implementation
    │   └── OpenAIProvider(BaseAIProvider)
    │       ├── client: OpenAI
    │       └── implements all abstract methods
    │
    ├── anthropic_provider.py   # Anthropic implementation
    │   └── AnthropicProvider(BaseAIProvider)
    │       ├── client: Anthropic
    │       └── implements all abstract methods
    │
    ├── google_provider.py      # Google implementation
    │   └── GoogleProvider(BaseAIProvider)
    │       ├── client: GenerativeModel
    │       └── implements all abstract methods
    │
    ├── config.py               # Configuration management
    │   └── AIConfig
    │       ├── provider
    │       ├── model
    │       ├── api_keys
    │       ├── validate()
    │       └── switch_provider()
    │
    └── gateway.py              # Main gateway class
        └── AIGateway
            ├── config: AIConfig
            ├── _current_provider: BaseAIProvider
            ├── chat_completion()
            ├── switch_provider()
            └── get_provider_info()
```

## Data Flow

### 1. Initialization
```
User starts app
    → Excel Agent.__init__()
        → AIGateway.create_from_env()
            → AIConfig() loads from .env
            → Creates provider based on AI_PROVIDER
                → OpenAIProvider / AnthropicProvider / GoogleProvider
```

### 2. Chat Completion Request
```
User sends message
    → ExcelAgent.call_agent(messages, excel_utils)
        → AIGateway.chat_completion(messages, tools)
            → Current Provider.chat_completion()
                → OpenAI API / Anthropic API / Google API
            → Provider.normalize_response()
                → Standardized format
        → Parse tool_calls
        → Execute Excel operations
        → Return response
```

### 3. Provider Switching
```
User calls /ai/switch API
    → ExcelAgent.switch_provider(provider, model)
        → AIGateway.switch_provider(provider, model)
            → AIConfig.switch_provider()
                → Update provider & model
            → Destroy old provider instance
            → Create new provider instance
                → New OpenAI/Anthropic/Google Provider
```

## Request/Response Normalization

### Input (OpenAI Format)
All providers accept OpenAI-style format:
```python
{
    "messages": [
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."}
    ],
    "tools": [
        {
            "type": "function",
            "function": {
                "name": "...",
                "description": "...",
                "parameters": {...}
            }
        }
    ]
}
```

### Output (Normalized Format)
All providers return same format:
```python
{
    "content": str,              # Text response
    "tool_calls": [              # Function calls (if any)
        {
            "id": str,
            "type": "function",
            "function": {
                "name": str,
                "arguments": str  # JSON string
            }
        }
    ],
    "finish_reason": str,        # "stop", "tool_calls", etc.
    "raw_message": object        # Original message object
}
```

## Provider-Specific Adaptations

### OpenAI
- Direct pass-through (native format)
- No conversion needed

### Anthropic
- **Messages**: System message extracted separately
- **Tools**: Convert from `{"type": "function", "function": {...}}` to `{"name": ..., "input_schema": ...}`
- **Response**: Parse content blocks (text + tool_use)

### Google
- **Messages**: Convert "assistant" → "model" role
- **Tools**: Convert to `function_declarations` format
- **Response**: Parse candidates and parts

## Configuration Priority

1. **Runtime** (highest priority)
   ```python
   gateway.switch_provider("anthropic", "claude-3-opus")
   ```

2. **Constructor config_dict**
   ```python
   AIGateway(AIConfig({"provider": "google"}))
   ```

3. **Environment Variables**
   ```bash
   AI_PROVIDER=openai
   AI_MODEL=gpt-4o
   ```

4. **Defaults** (lowest priority)
   - OpenAI / gpt-4o
   - Temperature: 0.7
   - Max tokens: 4096

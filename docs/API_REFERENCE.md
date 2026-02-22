# AI Gateway API Reference

## Endpoints

### 1. GET `/ai/info`

Lấy thông tin về AI provider và model hiện tại.

**Request:**
```bash
curl http://localhost:8000/ai/info
```

**Response:**
```json
{
  "provider": "openai",
  "model": "gpt-4o",
  "temperature": 0.7,
  "max_tokens": 4096,
  "available_providers": {
    "openai": true,
    "anthropic": false,
    "google": true,
    "groq": true,
    "vertex": false
  },
  "available_models": [
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4-turbo",
    "gpt-4",
    "gpt-3.5-turbo"
  ]
}
```

---

### 2. POST `/ai/switch`

Switch sang AI provider khác (có thể kèm model).

**Request:**
```bash
curl -X POST http://localhost:8000/ai/switch \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "groq",
    "model": "llama-3.3-70b-versatile"
  }'
```

**Body Parameters:**
- `provider` (required): Provider name
  - `openai`
  - `anthropic`
  - `google`
  - `groq`
  - `vertex`
- `model` (optional): Model name. If not provided, uses default model for provider.

**Response:**
```json
{
  "message": "Switched to groq",
  "info": {
    "provider": "groq",
    "model": "llama-3.3-70b-versatile",
    "temperature": 0.7,
    "max_tokens": 4096,
    "available_providers": {...},
    "available_models": [...]
  }
}
```

**Error Response (400):**
```json
{
  "error": "Unknown provider: xyz. Available providers: ['openai', 'anthropic', 'google', 'groq', 'vertex']"
}
```

---

### 3. POST `/ai/model`

Chỉ thay đổi model mà không đổi provider.

**Request:**
```bash
curl -X POST http://localhost:8000/ai/model \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini"
  }'
```

**Body Parameters:**
- `model` (required): Model name

**Response:**
```json
{
  "message": "Changed model to gpt-4o-mini",
  "info": {
    "provider": "openai",
    "model": "gpt-4o-mini",
    ...
  }
}
```

**Error Response (400):**
```json
{
  "error": "Model 'invalid-model' not available for provider 'openai'. Available models: ['gpt-4o', 'gpt-4o-mini', ...]"
}
```

---

### 4. GET `/ai/models`

Lấy danh sách models available cho provider.

**Request:**
```bash
# Models của provider hiện tại
curl http://localhost:8000/ai/models

# Models của provider khác
curl "http://localhost:8000/ai/models?provider=groq"
```

**Query Parameters:**
- `provider` (optional): Provider name to get models for

**Response:**
```json
{
  "provider": "groq",
  "models": [
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
    "gemma2-9b-it"
  ],
  "current_model": "llama-3.3-70b-versatile"
}
```

---

## Usage Examples

### Example 1: Check current setup
```bash
curl http://localhost:8000/ai/info
```

### Example 2: Switch to Groq for fast inference
```bash
# Switch to Groq with default model
curl -X POST http://localhost:8000/ai/switch \
  -H "Content-Type: application/json" \
  -d '{"provider": "groq"}'

# Or specify model
curl -X POST http://localhost:8000/ai/switch \
  -H "Content-Type: application/json" \
  -d '{"provider": "groq", "model": "llama-3.1-8b-instant"}'
```

### Example 3: Switch to Claude for complex reasoning
```bash
curl -X POST http://localhost:8000/ai/switch \
  -H "Content-Type: application/json" \
  -d '{"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"}'
```

### Example 4: Just change model (stay with same provider)
```bash
# If currently on OpenAI, just switch to cheaper model
curl -X POST http://localhost:8000/ai/model \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-4o-mini"}'
```

### Example 5: Check available models
```bash
# See what models are available for Groq
curl "http://localhost:8000/ai/models?provider=groq"

# See what models are available for current provider
curl http://localhost:8000/ai/models
```

### Example 6: Smart routing based on task
```bash
# For speed-critical task
curl -X POST http://localhost:8000/ai/switch \
  -H "Content-Type: application/json" \
  -d '{"provider": "groq", "model": "llama-3.1-8b-instant"}'

# Then send your query via WebSocket...

# For complex analysis
curl -X POST http://localhost:8000/ai/switch \
  -H "Content-Type: application/json" \
  -d '{"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"}'
```

---

## Python Client Examples

### Using requests library

```python
import requests

BASE_URL = "http://localhost:8000"

# Get current info
response = requests.get(f"{BASE_URL}/ai/info")
print(response.json())

# Switch provider
response = requests.post(
    f"{BASE_URL}/ai/switch",
    json={"provider": "groq", "model": "llama-3.3-70b-versatile"}
)
print(response.json())

# Change model only
response = requests.post(
    f"{BASE_URL}/ai/model",
    json={"model": "llama-3.1-8b-instant"}
)
print(response.json())

# Get available models
response = requests.get(f"{BASE_URL}/ai/models?provider=anthropic")
print(response.json())
```

### Using httpx (async)

```python
import httpx
import asyncio

async def manage_ai_provider():
    async with httpx.AsyncClient() as client:
        # Get info
        response = await client.get("http://localhost:8000/ai/info")
        info = response.json()
        print(f"Current: {info['provider']} - {info['model']}")
        
        # Switch to Groq
        response = await client.post(
            "http://localhost:8000/ai/switch",
            json={"provider": "groq"}
        )
        print(response.json()['message'])

asyncio.run(manage_ai_provider())
```

---

## Integration with WebSocket

After switching provider/model, subsequent WebSocket messages will use the new AI:

```javascript
// Frontend JavaScript
async function switchToGroq() {
  // Switch provider via REST API
  const response = await fetch('http://localhost:8000/ai/switch', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      provider: 'groq',
      model: 'llama-3.3-70b-versatile'
    })
  });
  
  const result = await response.json();
  console.log(result.message);
  
  // Now WebSocket messages will use Groq
  ws.send(JSON.stringify({
    type: 'message',
    content: 'Sum column A'
  }));
}
```

---

## Error Handling

### Common Errors

**1. Provider not available (no API key)**
```json
{
  "error": "API key not found for provider 'anthropic'. Set ANTHROPIC_API_KEY environment variable."
}
```

**Fix:** Add API key to `.env` file

**2. Invalid provider name**
```json
{
  "error": "Unknown provider: xyz. Available providers: ['openai', 'anthropic', 'google', 'groq', 'vertex']"
}
```

**Fix:** Use valid provider name

**3. Invalid model name**
```json
{
  "error": "Model 'gpt-5' not available for provider 'openai'. Available models: ['gpt-4o', 'gpt-4o-mini', ...]"
}
```

**Fix:** Check available models first with `/ai/models`

**4. Package not installed**
```json
{
  "error": "Anthropic package not installed. Install it with: pip install anthropic"
}
```

**Fix:** Install required package

---

## Best Practices

### 1. Check availability before switching
```python
# Get available providers
info = requests.get(f"{BASE_URL}/ai/info").json()
available = info['available_providers']

if available['groq']:
    # Switch to Groq
    requests.post(f"{BASE_URL}/ai/switch", json={"provider": "groq"})
else:
    print("Groq not configured")
```

### 2. List models before selecting
```python
# Get available models for provider
models_response = requests.get(
    f"{BASE_URL}/ai/models?provider=groq"
).json()

print(f"Available models: {models_response['models']}")

# Pick one
requests.post(
    f"{BASE_URL}/ai/model",
    json={"model": models_response['models'][0]}
)
```

### 3. Handle errors gracefully
```python
try:
    response = requests.post(
        f"{BASE_URL}/ai/switch",
        json={"provider": "anthropic"}
    )
    response.raise_for_status()
    print(response.json()['message'])
except requests.exceptions.HTTPError as e:
    error = e.response.json()
    print(f"Error: {error['error']}")
    # Fallback to default provider
    requests.post(
        f"{BASE_URL}/ai/switch",
        json={"provider": "openai"}
    )
```

---

## Complete Workflow Example

```python
import requests

BASE_URL = "http://localhost:8000"

def optimize_provider_for_task(task_type: str):
    """Automatically select best provider for task"""
    
    # Get current info and available providers
    info = requests.get(f"{BASE_URL}/ai/info").json()
    available = info['available_providers']
    
    # Define optimal provider for each task type
    routing_rules = {
        "speed": ("groq", "llama-3.1-8b-instant"),
        "quality": ("anthropic", "claude-3-5-sonnet-20241022"),
        "cost": ("groq", "llama-3.3-70b-versatile"),
        "long_context": ("google", "gemini-1.5-pro"),
        "enterprise": ("vertex", "gemini-1.5-pro"),
    }
    
    provider, model = routing_rules.get(task_type, ("openai", "gpt-4o"))
    
    # Check if provider is available
    if not available.get(provider):
        print(f"{provider} not available, using OpenAI")
        provider, model = "openai", "gpt-4o"
    
    # Switch provider
    response = requests.post(
        f"{BASE_URL}/ai/switch",
        json={"provider": provider, "model": model}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Switched to {result['info']['provider']} - {result['info']['model']}")
        return True
    else:
        print(f"❌ Error: {response.json()['error']}")
        return False

# Usage
optimize_provider_for_task("speed")  # → Groq
# Send your query...

optimize_provider_for_task("quality")  # → Claude
# Send complex query...
```

---

## Monitoring Provider Performance

```python
import requests
import time

def benchmark_providers(query: str):
    """Compare response times across providers"""
    
    BASE_URL = "http://localhost:8000"
    
    # Get available providers
    info = requests.get(f"{BASE_URL}/ai/info").json()
    providers = [p for p, avail in info['available_providers'].items() if avail]
    
    results = {}
    
    for provider in providers:
        # Switch provider
        requests.post(
            f"{BASE_URL}/ai/switch",
            json={"provider": provider}
        )
        
        # Time the request (via your WebSocket or API)
        start = time.time()
        # ... send query and get response ...
        elapsed = time.time() - start
        
        results[provider] = elapsed
    
    # Sort by speed
    sorted_results = sorted(results.items(), key=lambda x: x[1])
    
    print("Provider Performance:")
    for provider, time_taken in sorted_results:
        print(f"{provider}: {time_taken:.2f}s")
    
    return sorted_results

# Usage
benchmark_providers("What is 2+2?")
```

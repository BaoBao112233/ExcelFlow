# AI Gateway - Quick Reference

## 🚀 Cài đặt nhanh

```bash
# 1. Cài base dependencies
cd backend
pip install -r requirements.txt

# 2. Cài provider bạn muốn (optional)
pip install anthropic  # Cho Claude
pip install google-generativeai  # Cho Gemini
pip install google-cloud-aiplatform  # Cho Vertex AI
# Groq dùng openai package, không cần install riêng

# 3. Tạo file .env
cp ../.env.example .env
# Sửa .env và thêm API keys
```

## ⚙️ Configuration

### Environment Variables

```bash
AI_PROVIDER=openai              # openai | anthropic | google | groq | vertex
AI_MODEL=gpt-4o                 # Tên model (optional)
AI_TEMPERATURE=0.7              # 0.0-2.0 (optional)
AI_MAX_TOKENS=4096              # Max tokens (optional)

OPENAI_API_KEY=sk-...           # OpenAI API key
ANTHROPIC_API_KEY=sk-ant-...    # Anthropic API key
GOOGLE_API_KEY=...              # Google API key
GROQ_API_KEY=gsk_...            # Groq API key
VERTEX_PROJECT_ID=...           # GCP Project ID (cho Vertex)
VERTEX_LOCATION=us-central1     # GCP region (optional)
```

## 📋 Supported Models

### OpenAI
```python
"gpt-4o"           # Recommended - mới nhất, mạnh nhất
"gpt-4-turbo"      # Nhanh, mạnh
"gpt-3.5-turbo"    # Rẻ nhất
```

### Anthropic
```python
"claude-3-5-sonnet-20241022"  # Recommended - cân bằng tốt
"claude-3-opus-20240229"      # Mạnh nhất, chậm hơn
"claude-3-haiku-20240307"     # Nhanh, rẻ
```

### Google
```python
"gemini-1.5-pro"    # Recommended - mạnh nhất
"gemini-1.5-flash"  # Nhanh, rẻ hơn
```

### Groq (Cực nhanh!)
```python
"llama-3.3-70b-versatile"  # Recommended - Llama mới nhất
"llama-3.1-70b-versatile"  # Llama 3.1 70B
"llama-3.1-8b-instant"     # Siêu nhanh, model nhỏ
"mixtral-8x7b-32768"       # Mixtral MoE
"gemma2-9b-it"             # Google Gemma
```

### Vertex AI (Enterprise)
```python
"gemini-1.5-pro"    # Enterprise Gemini Pro
"gemini-1.5-flash"  # Enterprise Gemini Flash
```

## 🔄 Switch Provider

### Via API
```bash
# Xem thông tin hiện tại
curl http://localhost:8000/ai/info

# Switch sang OpenAI
curl -X POST http://localhost:8000/ai/switch \
  -H "Content-Type: application/json" \
  -d '{"provider": "openai"}'

# Switch sang Claude với model cụ thể
curl -X POST http://localhost:8000/ai/switch \
  -H "Content-Type: application/json" \
  -d '{"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"}'

# Switch sang Gemini
curl -X POST http://localhost:8000/ai/switch \
  -H "Content-Type: application/json" \
  -d '{"provider": "google"}'

# Switch sang Groq (cực nhanh)
curl -X POST http://localhost:8000/ai/switch \
  -H "Content-Type: application/json" \
  -d '{"provider": "groq"}'
```

### Chỉ đổi model
```bash
curl -X POST http://localhost:8000/ai/model \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-4o-mini"}'
```

### Xem danh sách models
```bash
# Models hiện tại
curl http://localhost:8000/ai/models

# Models của provider khác
curl "http://localhost:8000/ai/models?provider=groq"
```

### Via Python Code
```python
from backend.app.ai_gateway import AIGateway

# Tạo gateway
gateway = AIGateway.create_from_env()

# Switch provider
gateway.switch_provider("anthropic")
gateway.switch_provider("google", "gemini-1.5-flash")

# Get info
print(gateway.get_provider_info())
```

## 💻 Usage Examples

### Basic Chat
```python
from backend.app.ai_gateway import AIGateway

gateway = AIGateway.create_from_env()

messages = [
    {"role": "user", "content": "Hello!"}
]

response = gateway.chat_completion(messages)
print(response['content'])
```

### With Function Calling
```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_data",
            "description": "Get data from database",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"]
            }
        }
    }
]

response = gateway.chat_completion(
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

if response['tool_calls']:
    for tc in response['tool_calls']:
        print(f"Function: {tc['function']['name']}")
        print(f"Args: {tc['function']['arguments']}")
```

### Custom Configuration
```python
from backend.app.ai_gateway import AIConfig, AIGateway

config = AIConfig({
    "provider": "anthropic",
    "model": "claude-3-5-sonnet-20241022",
    "temperature": 0.3,
    "api_keys": {
        "anthropic": "your-key"
    }
})

gateway = AIGateway(config)
```

## 🐛 Troubleshooting

### Import Error
```
ImportError: anthropic package not installed
```
**Fix:** `pip install anthropic`

### API Key Error
```
ValueError: API key not found for provider 'anthropic'
```
**Fix:** Check `.env` file có `ANTHROPIC_API_KEY=...`

### Check Available Providers
```python
gateway = AIGateway.create_from_env()
print(gateway.get_available_providers())
# {'openai': True, 'anthropic': False, 'google': True}
```

## 📦 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ai/info` | GET | Xem thông tin provider hiện tại |
| `/ai/switch` | POST | Switch sang provider khác |

### Response Format

#### GET /ai/info
```json
{
  "provider": "openai",
  "model": "gpt-4o",
  "temperature": 0.7,
  "max_tokens": 4096,
  "available_providers": {
    "openai": true,
    "anthropic": false,
    "google": true
  }
}
```

#### POST /ai/switch
```json
{
  "message": "Switched to anthropic",
  "info": {
    "provider": "anthropic",
    "model": "claude-3-5-sonnet-20241022",
    ...
  }
}
```

## 🧪 Testing

```bash
# Run unit tests
cd backend
python -m pytest tests/test_ai_gateway.py -v

# Run example script
python examples/ai_gateway_demo.py
```

## 📚 More Info

- [Full Documentation](./AI_GATEWAY.md)
- [Architecture](./AI_GATEWAY_ARCHITECTURE.md)
- [Groq Setup Guide](./docs/GROQ_SETUP.md)
- [Vertex AI Setup Guide](./docs/VERTEX_SETUP.md)
- [Examples](./backend/examples/ai_gateway_demo.py)
- [Unit Tests](./backend/tests/test_ai_gateway.py)

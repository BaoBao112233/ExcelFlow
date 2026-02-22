# AI Gateway - Hướng dẫn sử dụng

## Tổng quan

AI Gateway cho phép bạn dễ dàng thay đổi giữa các AI providers khác nhau (OpenAI, Anthropic Claude, Google Gemini) mà không cần thay đổi code.

## Cấu hình

### 1. Cài đặt dependencies

Cài đặt dependencies cơ bản (đã bao gồm OpenAI):
```bash
cd backend
pip install -r requirements.txt
```

Nếu muốn dùng **Anthropic Claude**:
```bash
pip install anthropic>=0.39.0
```

Nếu muốn dùng **Google Gemini**:
```bash
pip install google-generativeai>=0.8.0
```

### 2. Cấu hình environment variables

Copy file `.env.example` thành `.env`:
```bash
cp .env.example .env
```

Sửa file `.env` và thêm API keys:
```bash
# Chọn provider
AI_PROVIDER=openai

# Thêm API key tương ứng
OPENAI_API_KEY=sk-your-key-here
# hoặc
ANTHROPIC_API_KEY=sk-ant-your-key-here
# hoặc
GOOGLE_API_KEY=your-google-key-here
```

### 3. Các provider được hỗ trợ

| Provider | Model mặc định | Cách lấy API Key |
|----------|----------------|------------------|
| `openai` | `gpt-4o` | [platform.openai.com](https://platform.openai.com/api-keys) |
| `anthropic` | `claude-3-5-sonnet-20241022` | [console.anthropic.com](https://console.anthropic.com/) |
| `google` | `gemini-1.5-pro` | [ai.google.dev](https://ai.google.dev/) |
| `groq` | `llama-3.3-70b-versatile` | [console.groq.com](https://console.groq.com/) |
| `vertex` | `gemini-1.5-pro` | [GCP Console](https://console.cloud.google.com/) |

## Sử dụng

### Thay đổi provider qua API

**Xem thông tin provider hiện tại:**
```bash
curl http://localhost:8000/ai/info
```

Response:
```json
{
  "provider": "openai",
  "model": "gpt-4o",
  "temperature": 0.7,
  "max_tokens": 4096,
  "available_providers": {
    "openai": true,
    "anthropic": false,
    "google": false
  }
}
```

**Switch sang provider khác:**
```bash
# Switch sang Anthropic Claude
curl -X POST http://localhost:8000/ai/switch \
  -H "Content-Type: application/json" \
  -d '{"provider": "anthropic"}'

# Switch sang Google Gemini với model cụ thể
curl -X POST http://localhost:8000/ai/switch \
  -H "Content-Type: application/json" \
  -d '{"provider": "google", "model": "gemini-1.5-flash"}'

# Switch sang Groq (fast inference)
curl -X POST http://localhost:8000/ai/switch \
  -H "Content-Type: application/json" \
  -d '{"provider": "groq", "model": "llama-3.3-70b-versatile"}'
```

**Chỉ đổi model (không đổi provider):**
```bash
curl -X POST http://localhost:8000/ai/model \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-4o-mini"}'
```

**Xem danh sách models available:**
```bash
# Models của provider hiện tại
curl http://localhost:8000/ai/models

# Models của provider khác
curl "http://localhost:8000/ai/models?provider=groq"
```

### Thay đổi provider trong code

```python
from backend.app.ai_gateway import AIGateway, AIConfig

# Tạo gateway với config mặc định (từ .env)
gateway = AIGateway.create_from_env()

# Hoặc tạo với config custom
config = AIConfig({
    "provider": "anthropic",
    "model": "claude-3-5-sonnet-20241022",
    "api_keys": {
        "anthropic": "your-key-here"
    }
})
gateway = AIGateway(config)

# Sử dụng
response = gateway.chat_completion(
    messages=[{"role": "user", "content": "Hello!"}]
)

# Switch provider runtime
gateway.switch_provider("google", "gemini-1.5-pro")
```

## Models được khuyên dùng

### OpenAI
- **gpt-4o** - Model mới nhất, tốt nhất (recommended)
- **gpt-4o-mini** - Rẻ hơn, vẫn rất tốt
- **gpt-4-turbo** - Nhanh và mạnh
- **gpt-3.5-turbo** - Rẻ, nhanh nhưng kém hơn

### Anthropic
- **claude-3-5-sonnet-20241022** - Model mới nhất, cân bằng tốt (recommended)
- **claude-3-5-haiku-20241022** - Nhanh nhất, rẻ nhất
- **claude-3-opus-20240229** - Mạnh nhất nhưng chậm hơn

### Google (Free Tier)
- **gemini-1.5-pro** - Model mạnh nhất (recommended)
- **gemini-1.5-flash** - Nhanh và rẻ hơn

### Groq (Cực nhanh, Open Source Models)
- **llama-3.3-70b-versatile** - Llama mới nhất (recommended)
- **llama-3.1-70b-versatile** - Llama 3.1 70B
- **llama-3.1-8b-instant** - Siêu nhanh, model nhỏ
- **mixtral-8x7b-32768** - Mixtral, context dài

### Vertex AI (Enterprise Google)
- **gemini-1.5-pro** - Giống Google free tier nhưng có SLA tốt hơn
- **gemini-1.5-flash** - Nhanh hơn

## Troubleshooting

### Lỗi "API key not found"
- Kiểm tra file `.env` đã có API key chưa
- Đảm bảo tên biến đúng: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`

### Lỗi "Package not installed"
- Cài package tương ứng:
  ```bash
  pip install anthropic  # cho Anthropic
  pip install google-generativeai  # cho Google
  ```

### Provider không available
- Check API key đã set đúng chưa:
  ```bash
  curl http://localhost:8000/ai/info
  ```
- Xem field `available_providers` để biết provider nào có sẵn

## Ví dụ use cases

### 1. Dùng OpenAI cho tác vụ thông thường
```bash
AI_PROVIDER=openai
AI_MODEL=gpt-4o
```

### 2. Dùng Claude cho tác vụ phức tạp, cần reasoning tốt
```bash
AI_PROVIDER=anthropic
AI_MODEL=claude-3-5-sonnet-20241022
```

### 3. Dùng Gemini khi cần xử lý context dài
```bash
AI_PROVIDER=google
AI_MODEL=gemini-1.5-pro
```

### 4. Dùng Groq khi cần inference CỰC NHANH
```bash
AI_PROVIDER=groq
AI_MODEL=llama-3.3-70b-versatile
```

### 5. Dùng Vertex AI cho enterprise workloads
```bash
AI_PROVIDER=vertex
VERTEX_PROJECT_ID=your-gcp-project
VERTEX_LOCATION=us-central1
```

### 6. Switch động theo nhu cầu
```python
# Trong code
if task.requires_reasoning:
    gateway.switch_provider("anthropic")
elif task.requires_speed:
    gateway.switch_provider("groq", "llama-3.1-8b-instant")  # Siêu nhanh!
elif task.requires_long_context:
    gateway.switch_provider("google", "gemini-1.5-pro")
else:
    gateway.switch_provider("openai")
```

# Groq Setup Guide

## Groq là gì?

Groq cung cấp **inference cực nhanh** cho các open-source AI models như Llama, Mixtral, và Gemma. Groq sử dụng hardware chuyên dụng (LPU - Language Processing Unit) để đạt tốc độ inference nhanh nhất thị trường.

**Ưu điểm:**
- ⚡ **Cực kỳ nhanh** - Nhanh hơn nhiều so với GPU thông thường
- 💰 **Miễn phí tier** - Free quota hào phóng
- 🔓 **100% Open Source Models** - Llama, Mixtral, Gemma
- 🔌 **OpenAI Compatible API** - Dễ dàng integrate

**Nhược điểm:**
- Models open-source, có thể kém hơn GPT-4 trong một số tasks
- Rate limits trên free tier

## Cách lấy API Key

1. Truy cập [console.groq.com](https://console.groq.com/)
2. Tạo account (miễn phí)
3. Vào **API Keys** section
4. Click **Create API Key**
5. Copy API key (format: `gsk_...`)

## Setup trong ExcelFlow

### 1. Cài đặt (dùng OpenAI package)

Groq dùng OpenAI-compatible API nên không cần install thêm gì:
```bash
# OpenAI package đã có sẵn trong requirements.txt
pip install openai
```

### 2. Cấu hình .env

Thêm Groq API key vào `.env`:
```bash
# Groq Configuration
AI_PROVIDER=groq
AI_MODEL=llama-3.3-70b-versatile
GROQ_API_KEY=gsk_your_api_key_here
```

### 3. Test

```bash
# Start server
cd backend
uvicorn app.main:app --reload

# Test trong terminal khác
curl http://localhost:8000/ai/info
```

Response:
```json
{
  "provider": "groq",
  "model": "llama-3.3-70b-versatile",
  ...
}
```

## Models được hỗ trợ

### Llama 3.3 (Mới nhất - Recommended)
```
llama-3.3-70b-versatile
```
- **Context**: 128K tokens
- **Best for**: General tasks, reasoning, coding
- **Speed**: Cực nhanh

### Llama 3.1
```
llama-3.1-70b-versatile    # 70B parameters
llama-3.1-8b-instant       # 8B parameters - siêu nhanh
```
- **Context**: 128K tokens
- **Best for**: Versatile tasks

### Mixtral
```
mixtral-8x7b-32768
```
- **Context**: 32K tokens
- **Best for**: Multilingual, reasoning
- **Architecture**: Mixture of Experts (MoE)

### Gemma 2
```
gemma2-9b-it
```
- **Context**: 8K tokens
- **Best for**: Fast general tasks
- **From**: Google

## Cách sử dụng

### Switch sang Groq

```bash
# Via API
curl -X POST http://localhost:8000/ai/switch \
  -H "Content-Type: application/json" \
  -d '{"provider": "groq", "model": "llama-3.3-70b-versatile"}'
```

```python
# Via Python
from backend.app.ai_gateway import AIGateway

gateway = AIGateway.create_from_env()
gateway.switch_provider("groq", "llama-3.3-70b-versatile")
```

### Đổi model Groq

```bash
# Xem danh sách models
curl "http://localhost:8000/ai/models?provider=groq"

# Đổi sang model khác
curl -X POST http://localhost:8000/ai/model \
  -H "Content-Type: application/json" \
  -d '{"model": "llama-3.1-8b-instant"}'
```

## Use Cases

### 1. Cần inference CỰC NHANH
```bash
AI_PROVIDER=groq
AI_MODEL=llama-3.1-8b-instant
```

### 2. Real-time applications
```python
# Groq rất tốt cho real-time chat
if requires_realtime:
    gateway.switch_provider("groq", "llama-3.1-8b-instant")
```

### 3. Cost-effective cho high volume
```python
# Free tier của Groq rất hào phóng
# Tốt cho testing và development
if is_development:
    gateway.switch_provider("groq")
```

### 4. Open-source preference
```python
# Nếu muốn dùng 100% open-source models
gateway.switch_provider("groq", "llama-3.3-70b-versatile")
```

## Rate Limits (Free Tier)

- **Requests per minute**: 30
- **Tokens per minute**: 6,000
- **Requests per day**: 14,400

Đủ cho most use cases! Nếu cần nhiều hơn, có thể upgrade.

## So sánh với providers khác

| Feature | Groq | OpenAI | Anthropic |
|---------|------|--------|-----------|
| **Speed** | ⚡⚡⚡⚡⚡ | ⚡⚡⚡ | ⚡⚡⚡ |
| **Quality** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Cost** | 💰 Free | 💰💰💰 | 💰💰💰 |
| **Models** | Open Source | Proprietary | Proprietary |
| **Context** | 128K | 128K | 200K |

## Troubleshooting

### Error: "Invalid API key"
**Fix:** Check GROQ_API_KEY trong .env file
```bash
echo $GROQ_API_KEY  # Should start with gsk_
```

### Error: "Rate limit exceeded"
**Fix:** Groq free tier có rate limits. Đợi 1 phút hoặc upgrade plan.

### Model không chạy tốt
**Fix:** Thử model lớn hơn:
```bash
# Từ 8B lên 70B
curl -X POST http://localhost:8000/ai/model \
  -d '{"model": "llama-3.3-70b-versatile"}'
```

### Slow performance
Groq **nhanh nhất** trong các providers. Nếu chậm:
- Check network connection
- Verify bạn đang dùng Groq provider: `curl http://localhost:8000/ai/info`

## Resources

- [Groq Console](https://console.groq.com/)
- [Groq Documentation](https://console.groq.com/docs)
- [API Reference](https://console.groq.com/docs/api-reference)
- [Model Comparison](https://console.groq.com/docs/models)

## Tips

1. **Llama 3.3 70B** cho quality tốt nhất
2. **Llama 3.1 8B** cho speed cực nhanh
3. **Mixtral** cho multilingual tasks
4. Groq **miễn phí** và **cực nhanh** - perfect cho development!

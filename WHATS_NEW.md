# 🎉 AI Gateway v2.0 - Bây giờ có 5 Providers!

## Điểm mới

ExcelFlow giờ hỗ trợ **5 AI providers** thay vì 3:

| Provider | Đặc điểm | Khi nào dùng |
|----------|----------|--------------|
| **OpenAI** | Chất lượng cao, reliable | Production, general use |
| **Anthropic** | Reasoning tốt nhất | Complex analysis |
| **Google** | Free, context dài | Development, long docs |
| **Groq** ⚡ **MỚI!** | SIÊU NHANH, FREE | Real-time, high volume |
| **Vertex AI** 🏢 **MỚI!** | Enterprise, SLA | Production enterprise |

## Groq - Nhanh như chớp! ⚡

**Tại sao nên dùng Groq:**
- 🚀 **5-10x nhanh hơn** các providers khác
- 💰 **MIỄN PHÍ** (30 req/min, 6K tokens/min)
- 🔓 **100% Open Source Models** (Llama, Mixtral, Gemma)
- 🎯 **Perfect cho development & testing**

**Setup trong 1 phút:**
```bash
# 1. Lấy API key (free): https://console.groq.com/
# 2. Thêm vào .env
echo "GROQ_API_KEY=gsk_your_key" >> .env

# 3. Sử dụng!
curl -X POST http://localhost:8000/ai/switch \
  -H "Content-Type: application/json" \
  -d '{"provider": "groq", "model": "llama-3.3-70b-versatile"}'
```

**Models:**
- `llama-3.3-70b-versatile` - Llama mới nhất (recommended)
- `llama-3.1-8b-instant` - Siêu nhanh (0.2s response!)
- `mixtral-8x7b-32768` - Mixtral MoE
- `gemma2-9b-it` - Google Gemma

## Vertex AI - Enterprise Google ☁️

**Tại sao nên dùng Vertex:**
- 🏢 **Enterprise SLA** - Uptime guarantees
- 🔒 **Data Privacy** - Guaranteed không dùng để train
- 🌍 **Global Infrastructure** - Deploy nhiều regions
- 📊 **Monitoring & Logging** - Full GCP integration
- 🛡️ **Compliance** - HIPAA, SOC 2, etc.

**Setup:**
```bash
# Chi tiết: docs/VERTEX_SETUP.md
pip install google-cloud-aiplatform

# Thêm vào .env
VERTEX_PROJECT_ID=your-gcp-project
VERTEX_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

## Tính năng mới: Chọn Model riêng

Giờ có thể đổi model mà không cần đổi provider:

```bash
# Xem models available
curl http://localhost:8000/ai/models

# Đổi model (cùng provider)
curl -X POST http://localhost:8000/ai/model \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-4o-mini"}'

# Xem models của provider khác
curl "http://localhost:8000/ai/models?provider=groq"
```

## API Endpoints mới

| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `/ai/info` | GET | Xem provider + models hiện tại |
| `/ai/switch` | POST | Đổi provider (+ model optional) |
| `/ai/model` | POST | **MỚI!** Chỉ đổi model |
| `/ai/models` | GET | **MỚI!** List models available |

## So sánh Tốc độ

Response time cho 100 tokens:

```
Groq (8B):       0.2s  ⚡⚡⚡⚡⚡
Groq (70B):      0.5s  ⚡⚡⚡⚡⚡
Gemini Flash:    1.0s  ⚡⚡⚡⚡
GPT-4o-mini:     1.2s  ⚡⚡⚡
GPT-4o:          2.0s  ⚡⚡⚡
Claude Sonnet:   3.0s  ⚡⚡
```

**Groq wins!** 🏆

## So sánh Chi phí

Per 1M tokens:

```
FREE:
- Groq                   $0
- Google AI              $0

PAID:
- GPT-4o-mini            $0.15
- Vertex Flash           $0.20
- Claude Haiku           $0.80
- GPT-4o                 $2.50
- Claude Sonnet          $3.00
```

## Use Cases

### Development/Testing → Groq
```bash
AI_PROVIDER=groq
GROQ_API_KEY=gsk_...
```
- Free, fast, perfect!

### Speed Critical → Groq 8B
```bash
AI_MODEL=llama-3.1-8b-instant
```
- 0.2 giây response time!

### Complex Reasoning → Claude
```bash
AI_PROVIDER=anthropic
AI_MODEL=claude-3-5-sonnet-20241022
```
- Tốt nhất cho analysis

### Long Documents → Gemini
```bash
AI_PROVIDER=google
AI_MODEL=gemini-1.5-pro
```
- 2M token context window

### Enterprise Production → Vertex AI
```bash
AI_PROVIDER=vertex
VERTEX_PROJECT_ID=...
```
- SLA, compliance, security

## Smart Routing

Switch provider tự động theo task:

```python
# Speed critical
gateway.switch_provider("groq", "llama-3.1-8b-instant")

# Complex reasoning
gateway.switch_provider("anthropic", "claude-3-5-sonnet-20241022")

# Long context
gateway.switch_provider("google", "gemini-1.5-pro")

# Production
gateway.switch_provider("openai", "gpt-4o")
```

## Quick Start

### 1. Thử Groq (FREE & FAST!)

```bash
# Get key: https://console.groq.com/
echo "GROQ_API_KEY=gsk_your_key" >> backend/.env

# Start server
cd backend
uvicorn app.main:app --reload

# Test
curl -X POST http://localhost:8000/ai/switch \
  -H "Content-Type: application/json" \
  -d '{"provider": "groq"}'

# Check
curl http://localhost:8000/ai/info
```

### 2. So sánh tất cả providers

```bash
cd backend
python examples/ai_gateway_advanced.py
```

## Documentation

📚 **Đọc thêm:**
- [AI Gateway Overview](./AI_GATEWAY.md)
- [Quick Reference](./AI_GATEWAY_QUICK_REF.md)
- [Groq Setup Guide](./docs/GROQ_SETUP.md) ⚡
- [Vertex AI Setup](./docs/VERTEX_SETUP.md) ☁️
- [Providers Comparison](./docs/PROVIDERS_COMPARISON.md)
- [API Reference](./docs/API_REFERENCE.md)
- [Changelog](./CHANGELOG.md)

## Examples

```bash
# Basic examples
python backend/examples/ai_gateway_demo.py

# Advanced (Groq, Vertex, routing)
python backend/examples/ai_gateway_advanced.py
```

## TL;DR

**3 điểm chính:**

1. **Groq** - Siêu nhanh, FREE, perfect cho development! ⚡
2. **Vertex AI** - Enterprise SLA, compliance, security 🏢
3. **Chọn model** - Giờ có thể đổi model riêng mà không đổi provider 🎯

**Backward compatible** - Code cũ vẫn chạy bình thường!

---

**Bắt đầu với Groq ngay:** [Groq Setup Guide](./docs/GROQ_SETUP.md)

**40+ models**, **5 providers**, **1 codebase** 🚀

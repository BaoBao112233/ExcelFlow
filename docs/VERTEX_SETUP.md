# Vertex AI Setup Guide

## Vertex AI là gì?

**Vertex AI** là enterprise AI platform của Google Cloud, cung cấp Gemini models với:

**Ưu điểm:**
- 🏢 **Enterprise-grade** - SLA, security, compliance tốt hơn
- 🔒 **Data privacy** - Data không được dùng để train models
- 🌍 **Global infrastructure** - Deploy ở nhiều regions
- 📊 **Monitoring & logging** - Integration với GCP tools
- 💼 **Enterprise support** - 24/7 support từ Google

**So với Google AI (free tier):**
- Better SLA và uptime guarantees
- VPC support, private endpoints
- Data residency controls
- Advanced security features
- Billing và cost management tools

**Nhược điểm:**
- 💰 **Tốn phí** - Không có free tier như Google AI
- 🔧 **Setup phức tạp hơn** - Cần GCP project, IAM, billing
- 📚 **Learning curve** - Cần hiểu GCP ecosystem

## Prerequisites

1. **Google Cloud account**
2. **GCP Project** với billing enabled
3. **Vertex AI API** enabled
4. **Service Account** với quyền phù hợp

## Cách Setup

### 1. Tạo GCP Project

```bash
# Install gcloud CLI
# Linux/Mac: https://cloud.google.com/sdk/docs/install
# Windows: https://cloud.google.com/sdk/docs/install-sdk

# Login
gcloud auth login

# Tạo project mới
gcloud projects create excelflow-ai --name="ExcelFlow AI"

# Set làm default project
gcloud config set project excelflow-ai

# Enable billing (cần link billing account)
gcloud beta billing projects link excelflow-ai \
  --billing-account=YOUR-BILLING-ACCOUNT-ID
```

### 2. Enable Vertex AI API

```bash
# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com

# Enable other required APIs
gcloud services enable compute.googleapis.com
gcloud services enable storage.googleapis.com
```

### 3. Tạo Service Account

```bash
# Tạo service account
gcloud iam service-accounts create excelflow-sa \
  --display-name="ExcelFlow Service Account"

# Grant quyền Vertex AI User
gcloud projects add-iam-policy-binding excelflow-ai \
  --member="serviceAccount:excelflow-sa@excelflow-ai.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

# Tạo và download key
gcloud iam service-accounts keys create ~/excelflow-key.json \
  --iam-account=excelflow-sa@excelflow-ai.iam.gserviceaccount.com
```

### 4. Setup Authentication

**QUAN TRỌNG:** Vertex AI **BẮT BUỘC** phải có service account JSON file.

```bash
# Set environment variable cho service account key
export GOOGLE_APPLICATION_CREDENTIALS=~/excelflow-key.json

# HOẶC thêm vào .env (recommended)
echo "GOOGLE_APPLICATION_CREDENTIALS=$HOME/excelflow-key.json" >> .env
```

**Lưu ý:**
- File JSON này chứa credentials để authenticate với GCP
- **KHÔNG** commit file này vào git
- **KHÔNG** share file này với người khác
- Add vào `.gitignore`: `*.json` (service account files)

## Setup trong ExcelFlow

### 1. Install Dependencies

```bash
pip install google-cloud-aiplatform
```

### 2. Cấu hình .env

```bash
# Vertex AI Configuration
AI_PROVIDER=vertex
AI_MODEL=gemini-1.5-pro

# GCP Project ID (NOT service account email)
VERTEX_PROJECT_ID=excelflow-ai

# GCP Region
VERTEX_LOCATION=us-central1

# Path to service account JSON key file (BẮT BUỘC!)
# File này được tạo ở bước 3
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/excelflow-key.json
# Ví dụ: /home/user/keys/excelflow-key.json
# Hoặc: ~/excelflow-key.json
```

**⚠️ Lưu ý quan trọng:**
1. `GOOGLE_APPLICATION_CREDENTIALS` phải là **absolute path** đến file JSON
2. File JSON phải tồn tại và có quyền đọc
3. File JSON chứa private key - **KHÔNG** commit vào git!
4. Add `*.json` vào `.gitignore`

**Available Regions:**
- `us-central1` (Iowa)
- `us-east4` (Virginia)
- `europe-west4` (Netherlands)
- `asia-southeast1` (Singapore)

### 3. Test Connection

```python
# Test script
import vertexai
from vertexai.generative_models import GenerativeModel

vertexai.init(project="excelflow-ai", location="us-central1")
model = GenerativeModel("gemini-1.5-pro")

response = model.generate_content("Hello!")
print(response.text)
```

### 4. Verify trong ExcelFlow

```bash
# Start server
cd backend
uvicorn app.main:app --reload

# Test
curl http://localhost:8000/ai/info
```

Response:
```json
{
  "provider": "vertex",
  "model": "gemini-1.5-pro",
  ...
}
```

## Models được hỗ trợ

### Gemini 1.5 Pro
```
gemini-1.5-pro
```
- **Context**: 2M tokens (!)
- **Best for**: Complex reasoning, long documents
- **Multimodal**: Text, images, video, audio

### Gemini 1.5 Flash
```
gemini-1.5-flash
```
- **Context**: 1M tokens
- **Best for**: Fast, cost-effective tasks
- **Speed**: Nhanh hơn Pro

### Gemini 1.0 Pro
```
gemini-1.0-pro
```
- **Context**: 32K tokens
- **Legacy model** - nên dùng 1.5

## Pricing

**Gemini 1.5 Pro:**
- Input: $1.25 / 1M tokens
- Output: $5.00 / 1M tokens
- With context caching: Cheaper

**Gemini 1.5 Flash:**
- Input: $0.075 / 1M tokens
- Output: $0.30 / 1M tokens
- Rẻ hơn 16x so với Pro!

**Free tier:** Không có (khác với Google AI free tier)

## Cách sử dụng

### Switch sang Vertex AI

```bash
# Via API
curl -X POST http://localhost:8000/ai/switch \
  -H "Content-Type: application/json" \
  -d '{"provider": "vertex", "model": "gemini-1.5-pro"}'
```

```python
# Via Python
from backend.app.ai_gateway import AIGateway

gateway = AIGateway.create_from_env()
gateway.switch_provider("vertex", "gemini-1.5-pro")
```

## Use Cases

### 1. Enterprise deployments
```bash
# Production environments với SLA requirements
AI_PROVIDER=vertex
VERTEX_PROJECT_ID=production-project
```

### 2. Data privacy requirements
```python
# Khi cần đảm bảo data không được dùng để train
gateway.switch_provider("vertex")
```

### 3. VPC/Private endpoints
```python
# Cho workloads cần private networking
# Configure VPC trong GCP, Vertex AI sẽ respect
```

### 4. Long context processing
```python
# Gemini 1.5 Pro có 2M token context
# Perfect cho việc xử lý Excel files lớn
if excel_file.size > large_threshold:
    gateway.switch_provider("vertex", "gemini-1.5-pro")
```

## Security Best Practices

### 1. Service Account Permissions
Chỉ grant minimum permissions cần thiết:
```bash
# Thay vì aiplatform.admin, dùng aiplatform.user
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SA_EMAIL" \
  --role="roles/aiplatform.user"
```

### 2. Rotate Keys Regularly
```bash
# Delete old keys
gcloud iam service-accounts keys list \
  --iam-account=SA_EMAIL

gcloud iam service-accounts keys delete KEY_ID \
  --iam-account=SA_EMAIL

# Create new key
gcloud iam service-accounts keys create new-key.json \
  --iam-account=SA_EMAIL
```

### 3. VPC Service Controls (Advanced)
Để isolate Vertex AI trong VPC perimeter.

## Monitoring & Logging

### Cloud Logging
```bash
# View Vertex AI logs
gcloud logging read "resource.type=aiplatform.googleapis.com/Endpoint" \
  --limit 50 \
  --format json
```

### Cloud Monitoring
- Metrics: Request count, latency, errors
- Alerts: Setup alerts cho errors hoặc high usage
- Dashboards: Visualize usage patterns

## Cost Management

### 1. Set Budget Alerts
```bash
# Tạo budget alert trong GCP Console
# Billing > Budgets & alerts
```

### 2. Use Flash for cost savings
```python
# Flash rẻ hơn Pro 16x
if task.is_simple:
    gateway.set_model("gemini-1.5-flash")
```

### 3. Monitor usage
```bash
# Check billing
gcloud billing accounts list
gcloud billing projects describe PROJECT_ID
```

## Troubleshooting

### Error: "Permission denied"
**Fix:** Check service account có đủ quyền:
```bash
gcloud projects get-iam-policy PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:SA_EMAIL"
```

### Error: "API not enabled"
**Fix:** Enable Vertex AI API:
```bash
gcloud services enable aiplatform.googleapis.com
```

### Error: "Quota exceeded"
**Fix:** Request quota increase trong GCP Console hoặc switch sang region khác.

### Authentication issues
**Fix:** Verify GOOGLE_APPLICATION_CREDENTIALS:
```bash
echo $GOOGLE_APPLICATION_CREDENTIALS
cat $GOOGLE_APPLICATION_CREDENTIALS  # Should be valid JSON
```

## Vertex AI vs Google AI (Free Tier)

| Feature | Vertex AI | Google AI |
|---------|-----------|-----------|
| **Cost** | Paid | Free tier available |
| **SLA** | ✅ Yes | ❌ No |
| **Data privacy** | ✅ Guaranteed | ⚠️ Best effort |
| **VPC support** | ✅ Yes | ❌ No |
| **Enterprise support** | ✅ 24/7 | ❌ Community |
| **Setup complexity** | 🔧🔧🔧 | 🔧 |
| **Best for** | Production | Development |

## Resources

- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Generative AI on Vertex AI](https://cloud.google.com/vertex-ai/docs/generative-ai/learn/overview)
- [Pricing Calculator](https://cloud.google.com/products/calculator)
- [Gemini API Reference](https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/gemini)

## Quick Decision Guide

**Use Vertex AI if:**
- ✅ Production environment
- ✅ Need SLA guarantees
- ✅ Data privacy is critical
- ✅ Enterprise compliance required
- ✅ Need VPC/private networking

**Use Google AI (free tier) if:**
- ✅ Development/testing
- ✅ Low volume usage
- ✅ Cost is primary concern
- ✅ Quick prototype

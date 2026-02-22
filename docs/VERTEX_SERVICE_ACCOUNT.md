# Vertex AI Quick Setup - Service Account Guide

## Bước 1: Tạo GCP Project (nếu chưa có)

```bash
# Cài gcloud CLI: https://cloud.google.com/sdk/docs/install

# Login
gcloud auth login

# Tạo project
gcloud projects create excelflow-vertex --name="ExcelFlow Vertex AI"

# Set default
gcloud config set project excelflow-vertex

# Enable billing (cần billing account)
gcloud beta billing projects link excelflow-vertex \
  --billing-account=YOUR-BILLING-ACCOUNT-ID
```

## Bước 2: Enable Vertex AI API

```bash
# Enable Vertex AI
gcloud services enable aiplatform.googleapis.com

# Enable dependencies
gcloud services enable compute.googleapis.com
gcloud services enable storage.googleapis.com
```

## Bước 3: Tạo Service Account

### Option A: Qua gcloud CLI (Recommended)

```bash
# 1. Tạo service account
gcloud iam service-accounts create excelflow-sa \
  --display-name="ExcelFlow Service Account" \
  --description="Service account for ExcelFlow Vertex AI"

# 2. Grant Vertex AI User role
gcloud projects add-iam-policy-binding excelflow-vertex \
  --member="serviceAccount:excelflow-sa@excelflow-vertex.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

# 3. Tạo và download JSON key
gcloud iam service-accounts keys create ~/excelflow-vertex-key.json \
  --iam-account=excelflow-sa@excelflow-vertex.iam.gserviceaccount.com

# 4. Verify file được tạo
ls -lh ~/excelflow-vertex-key.json
```

### Option B: Qua GCP Console (GUI)

1. Truy cập [GCP Console](https://console.cloud.google.com/)
2. Chọn project của bạn
3. Vào **IAM & Admin** → **Service Accounts**
4. Click **CREATE SERVICE ACCOUNT**
5. Điền:
   - **Name:** `excelflow-sa`
   - **Description:** Service account for ExcelFlow
6. Click **CREATE AND CONTINUE**
7. Grant role: **Vertex AI User** (`roles/aiplatform.user`)
8. Click **CONTINUE** → **DONE**
9. Click vào service account vừa tạo
10. Tab **KEYS** → **ADD KEY** → **Create new key**
11. Chọn **JSON** → **CREATE**
12. File JSON sẽ tự động download
13. Di chuyển file đến vị trí an toàn:
    ```bash
    mv ~/Downloads/excelflow-vertex-*.json ~/excelflow-vertex-key.json
    chmod 600 ~/excelflow-vertex-key.json  # Chỉ owner read/write
    ```

## Bước 4: Cấu hình Environment

### Setup .env file

```bash
cd /home/baobao/Projects/ExcelFlow

# Tạo/edit .env
cat >> .env << 'EOF'

# Vertex AI Configuration
AI_PROVIDER=vertex
AI_MODEL=gemini-1.5-pro
VERTEX_PROJECT_ID=excelflow-vertex
VERTEX_LOCATION=us-central1

# QUAN TRỌNG: Path to service account JSON
GOOGLE_APPLICATION_CREDENTIALS=/home/baobao/excelflow-vertex-key.json
EOF
```

**⚠️ LƯU Ý:**
- Thay `excelflow-vertex` bằng project ID của bạn
- Thay path đến JSON file cho đúng
- Dùng **absolute path**, KHÔNG dùng `~` hoặc relative path

### Verify path

```bash
# Check file tồn tại
ls -lh $GOOGLE_APPLICATION_CREDENTIALS

# Verify JSON valid
python3 -c "import json; print('✅ Valid JSON'); json.load(open('$GOOGLE_APPLICATION_CREDENTIALS'))"
```

## Bước 5: Install Dependencies

```bash
cd backend
pip install google-cloud-aiplatform
```

## Bước 6: Verify Setup

```bash
# Load environment variables
source ../.env

# Run verification script
../scripts/verify_vertex_setup.sh
```

Output mong đợi:
```
🔍 Vertex AI Service Account Verification
==========================================

✅ VERTEX_PROJECT_ID: excelflow-vertex
✅ GOOGLE_APPLICATION_CREDENTIALS: /home/baobao/excelflow-vertex-key.json
✅ Service account file exists
✅ Service account file is valid JSON
✅ Service Account: excelflow-sa@excelflow-vertex.iam.gserviceaccount.com
✅ Project from SA: excelflow-vertex
✅ vertexai package installed
✅ vertexai.generative_models available

Testing Vertex AI connection...
✅ Vertex AI connection successful!
   Project: excelflow-vertex
   Location: us-central1
   Model: gemini-1.5-flash

🎉 All checks passed! Vertex AI is ready to use.
```

## Bước 7: Test trong ExcelFlow

```bash
# Start server
cd backend
uvicorn app.main:app --reload

# Trong terminal khác, test
curl http://localhost:8000/ai/info

# Switch to Vertex
curl -X POST http://localhost:8000/ai/switch \
  -H "Content-Type: application/json" \
  -d '{"provider": "vertex"}'

# Verify
curl http://localhost:8000/ai/info
```

Expected response:
```json
{
  "provider": "vertex",
  "model": "gemini-1.5-pro",
  ...
}
```

## Troubleshooting

### Error: "GOOGLE_APPLICATION_CREDENTIALS not set"

```bash
# Make sure environment variable is set
echo $GOOGLE_APPLICATION_CREDENTIALS

# If empty, load from .env
source .env
echo $GOOGLE_APPLICATION_CREDENTIALS
```

### Error: "Service account file not found"

```bash
# Check file exists
ls -lh $GOOGLE_APPLICATION_CREDENTIALS

# If not, check path in .env
cat .env | grep GOOGLE_APPLICATION_CREDENTIALS

# Make sure it's absolute path
# ❌ BAD: ~/excelflow-key.json
# ✅ GOOD: /home/baobao/excelflow-key.json
```

### Error: "Failed to initialize Vertex AI"

**Possible causes:**

1. **API not enabled**
   ```bash
   gcloud services enable aiplatform.googleapis.com --project=excelflow-vertex
   ```

2. **Service account không có quyền**
   ```bash
   # Grant Vertex AI User role
   gcloud projects add-iam-policy-binding excelflow-vertex \
     --member="serviceAccount:excelflow-sa@excelflow-vertex.iam.gserviceaccount.com" \
     --role="roles/aiplatform.user"
   ```

3. **Wrong project ID**
   ```bash
   # Check project ID in JSON file
   cat $GOOGLE_APPLICATION_CREDENTIALS | grep project_id
   
   # Should match VERTEX_PROJECT_ID
   echo $VERTEX_PROJECT_ID
   ```

### Error: "Permission denied"

```bash
# Check file permissions
ls -lh $GOOGLE_APPLICATION_CREDENTIALS

# Should be readable
# If not:
chmod 600 $GOOGLE_APPLICATION_CREDENTIALS
```

## Security Best Practices

### 1. ⚠️ KHÔNG commit service account JSON vào git!

```bash
# Add to .gitignore
echo "*.json" >> .gitignore
echo ".env" >> .gitignore

# If already committed, remove from git
git rm --cached excelflow-vertex-key.json
git commit -m "Remove service account key"
```

### 2. Restrict file permissions

```bash
# Only owner can read/write
chmod 600 ~/excelflow-vertex-key.json

# Verify
ls -lh ~/excelflow-vertex-key.json
# Should show: -rw------- (600)
```

### 3. Rotate keys regularly

```bash
# List existing keys
gcloud iam service-accounts keys list \
  --iam-account=excelflow-sa@excelflow-vertex.iam.gserviceaccount.com

# Delete old key (sau khi tạo key mới)
gcloud iam service-accounts keys delete KEY_ID \
  --iam-account=excelflow-sa@excelflow-vertex.iam.gserviceaccount.com

# Create new key
gcloud iam service-accounts keys create ~/excelflow-vertex-key-new.json \
  --iam-account=excelflow-sa@excelflow-vertex.iam.gserviceaccount.com

# Update .env with new path
```

### 4. Use separate service accounts per environment

```bash
# Production
gcloud iam service-accounts create excelflow-prod-sa

# Staging
gcloud iam service-accounts create excelflow-staging-sa

# Development
gcloud iam service-accounts create excelflow-dev-sa
```

### 5. Minimal permissions

Chỉ grant quyền cần thiết:
- ✅ `roles/aiplatform.user` - Enough for Vertex AI
- ❌ `roles/aiplatform.admin` - Too much!
- ❌ `roles/owner` - Never!

## Cost Management

### 1. Set budget alerts

```bash
# Set budget trong GCP Console
# Billing → Budgets & alerts
```

### 2. Monitor usage

```bash
# Check current costs
gcloud billing accounts describe YOUR-BILLING-ACCOUNT-ID

# View project billing
gcloud billing projects describe excelflow-vertex
```

### 3. Use cheaper models for testing

```python
# Development: Use Flash
gateway.switch_provider("vertex", "gemini-1.5-flash")

# Production: Use Pro only when needed
gateway.switch_provider("vertex", "gemini-1.5-pro")
```

## Complete Example

```bash
# 1. Setup
gcloud projects create my-excelflow
gcloud config set project my-excelflow
gcloud services enable aiplatform.googleapis.com

# 2. Create service account
gcloud iam service-accounts create excelflow-sa
gcloud projects add-iam-policy-binding my-excelflow \
  --member="serviceAccount:excelflow-sa@my-excelflow.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

# 3. Create key
gcloud iam service-accounts keys create ~/excelflow-key.json \
  --iam-account=excelflow-sa@my-excelflow.iam.gserviceaccount.com

# 4. Configure
cat >> .env << EOF
VERTEX_PROJECT_ID=my-excelflow
GOOGLE_APPLICATION_CREDENTIALS=$HOME/excelflow-key.json
VERTEX_LOCATION=us-central1
EOF

# 5. Install
pip install google-cloud-aiplatform

# 6. Test
source .env
../scripts/verify_vertex_setup.sh

# 7. Use!
uvicorn app.main:app --reload
```

## Reference

- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Service Accounts](https://cloud.google.com/iam/docs/service-accounts)
- [Authentication](https://cloud.google.com/docs/authentication/getting-started)
- [Pricing](https://cloud.google.com/vertex-ai/pricing)

#!/bin/bash
# Vertex AI Service Account Setup Script
# Script này giúp verify service account setup

set -e

echo "🔍 Vertex AI Service Account Verification"
echo "=========================================="
echo ""

# 1. Check VERTEX_PROJECT_ID
if [ -z "$VERTEX_PROJECT_ID" ]; then
    echo "❌ VERTEX_PROJECT_ID not set"
    echo "   Fix: export VERTEX_PROJECT_ID=your-gcp-project-id"
    exit 1
else
    echo "✅ VERTEX_PROJECT_ID: $VERTEX_PROJECT_ID"
fi

# 2. Check GOOGLE_APPLICATION_CREDENTIALS
if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo "❌ GOOGLE_APPLICATION_CREDENTIALS not set"
    echo "   Fix: export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json"
    exit 1
else
    echo "✅ GOOGLE_APPLICATION_CREDENTIALS: $GOOGLE_APPLICATION_CREDENTIALS"
fi

# 3. Check if file exists
if [ ! -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo "❌ Service account file not found: $GOOGLE_APPLICATION_CREDENTIALS"
    echo "   Make sure the file exists and path is correct"
    exit 1
else
    echo "✅ Service account file exists"
fi

# 4. Check if file is valid JSON
if ! python3 -c "import json; json.load(open('$GOOGLE_APPLICATION_CREDENTIALS'))" 2>/dev/null; then
    echo "❌ Service account file is not valid JSON"
    exit 1
else
    echo "✅ Service account file is valid JSON"
fi

# 5. Extract info from service account
SERVICE_ACCOUNT_EMAIL=$(python3 -c "import json; print(json.load(open('$GOOGLE_APPLICATION_CREDENTIALS'))['client_email'])" 2>/dev/null || echo "")
PROJECT_FROM_SA=$(python3 -c "import json; print(json.load(open('$GOOGLE_APPLICATION_CREDENTIALS'))['project_id'])" 2>/dev/null || echo "")

if [ -n "$SERVICE_ACCOUNT_EMAIL" ]; then
    echo "✅ Service Account: $SERVICE_ACCOUNT_EMAIL"
fi

if [ -n "$PROJECT_FROM_SA" ]; then
    echo "✅ Project from SA: $PROJECT_FROM_SA"
    
    # Check if project IDs match
    if [ "$PROJECT_FROM_SA" != "$VERTEX_PROJECT_ID" ]; then
        echo "⚠️  WARNING: Project ID mismatch!"
        echo "   VERTEX_PROJECT_ID: $VERTEX_PROJECT_ID"
        echo "   Service account project: $PROJECT_FROM_SA"
        echo "   Make sure they match!"
    fi
fi

# 6. Check if gcloud is installed
if command -v gcloud &> /dev/null; then
    echo "✅ gcloud CLI installed"
    
    # Try to verify credentials
    if gcloud auth application-default print-access-token --quiet &> /dev/null; then
        echo "✅ Service account credentials valid"
    else
        echo "⚠️  Could not verify service account (this might be normal)"
    fi
else
    echo "⚠️  gcloud CLI not installed (optional)"
fi

# 7. Check Python packages
echo ""
echo "Checking Python packages..."

if python3 -c "import vertexai" 2>/dev/null; then
    echo "✅ vertexai package installed"
else
    echo "❌ vertexai package not installed"
    echo "   Fix: pip install google-cloud-aiplatform"
    exit 1
fi

if python3 -c "from vertexai.generative_models import GenerativeModel" 2>/dev/null; then
    echo "✅ vertexai.generative_models available"
else
    echo "❌ vertexai.generative_models not available"
    echo "   Fix: pip install --upgrade google-cloud-aiplatform"
    exit 1
fi

# 8. Test Vertex AI connection (optional)
echo ""
echo "Testing Vertex AI connection..."

TEST_SCRIPT=$(cat <<'EOF'
import os
import vertexai
from vertexai.generative_models import GenerativeModel

project_id = os.getenv("VERTEX_PROJECT_ID")
location = os.getenv("VERTEX_LOCATION", "us-central1")

try:
    vertexai.init(project=project_id, location=location)
    model = GenerativeModel("gemini-1.5-flash")  # Use Flash for quick test
    print("✅ Vertex AI connection successful!")
    print(f"   Project: {project_id}")
    print(f"   Location: {location}")
    print(f"   Model: gemini-1.5-flash")
except Exception as e:
    print(f"❌ Vertex AI connection failed: {str(e)}")
    print()
    print("Common issues:")
    print("1. Vertex AI API not enabled")
    print("   Fix: gcloud services enable aiplatform.googleapis.com")
    print("2. Service account doesn't have 'Vertex AI User' role")
    print("   Fix: Grant role in GCP Console IAM")
    print("3. Wrong project ID")
    print("   Fix: Check VERTEX_PROJECT_ID matches your GCP project")
    exit(1)
EOF
)

if python3 -c "$TEST_SCRIPT"; then
    echo ""
    echo "🎉 All checks passed! Vertex AI is ready to use."
    echo ""
    echo "To use in ExcelFlow:"
    echo "  1. Add to .env:"
    echo "     VERTEX_PROJECT_ID=$VERTEX_PROJECT_ID"
    echo "     GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS"
    echo "     VERTEX_LOCATION=${VERTEX_LOCATION:-us-central1}"
    echo ""
    echo "  2. Switch provider:"
    echo "     curl -X POST http://localhost:8000/ai/switch -d '{\"provider\":\"vertex\"}'"
else
    exit 1
fi

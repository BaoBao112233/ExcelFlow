# ExcelFlow Docker Deployment Guide

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose installed
- Service account JSON file from Google Cloud Platform
- Vertex AI API enabled in your GCP project

### 1. Setup Service Account

Place your `service-account.json` file in the project root:
```bash
cp /path/to/your/service-account.json ./service-account.json
```

### 2. Deploy

Run the deployment script:
```bash
chmod +x deploy.sh
./deploy.sh
```

That's it! The script will:
- ✅ Validate prerequisites
- ✅ Build Docker images
- ✅ Start all services
- ✅ Run health checks
- ✅ Display access URLs

## 📱 Access Points

After deployment:
- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔧 Management

### View Logs
```bash
# All services
./logs.sh

# Specific service
./logs.sh backend
./logs.sh frontend
```

### Stop Services
```bash
./stop.sh
```

### Restart Services
```bash
docker-compose restart
```

### Rebuild After Code Changes
```bash
docker-compose up -d --build
```

## 🏗️ Architecture

```
┌─────────────────┐
│   Frontend      │  Port 80
│   (Nginx)       │  React + Vite
└────────┬────────┘
         │
         │ Proxy /api & /ws
         │
┌────────▼────────┐
│   Backend       │  Port 8000
│   (FastAPI)     │  Python 3.11
└────────┬────────┘
         │
         │ Vertex AI Client
         │
┌────────▼────────────────────┐
│   Google Cloud Vertex AI    │
│   gemini-2.0-flash-exp      │
│   Project: kfactory-prod    │
└─────────────────────────────┘
```

## 🔐 Security

### Service Account File
- ⚠️ **NEVER** commit `service-account.json` to git
- File is mounted read-only in the container
- Configured in `.gitignore`

### Environment Variables
- `.env` file contains sensitive configuration
- Not committed to git (in `.gitignore`)
- Use `.env.example` as template

### Production Checklist
- [ ] Update CORS origins in backend
- [ ] Use production-grade secrets management
- [ ] Enable HTTPS/TLS
- [ ] Set up firewall rules
- [ ] Configure proper IAM roles
- [ ] Enable logging and monitoring
- [ ] Set resource limits in docker-compose.yml

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. Service account file not found
# 2. Invalid JSON in service-account.json
# 3. Vertex AI API not enabled
# 4. Wrong project ID
```

### Frontend 502 Bad Gateway
```bash
# Check if backend is running
curl http://localhost:8000/health

# Restart services
docker-compose restart
```

### Vertex AI authentication error
```bash
# Verify service account
docker-compose exec backend python -c "
import json
sa = json.load(open('/app/credentials/service-account.json'))
print('Project:', sa['project_id'])
print('Email:', sa['client_email'])
"

# Check environment
docker-compose exec backend env | grep VERTEX
```

### Port already in use
```bash
# Change ports in docker-compose.yml
# Or stop conflicting services
sudo lsof -i :8000
sudo lsof -i :80
```

## 📊 Configuration

### Change AI Model

Edit `.env`:
```bash
AI_MODEL=gemini-1.5-pro  # or gemini-1.5-flash
```

Restart:
```bash
docker-compose restart backend
```

### Change Location

Edit `.env`:
```bash
VERTEX_LOCATION=asia-southeast1  # or other regions
```

### Resource Limits

Edit `docker-compose.yml`:
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

## 🔄 Updates

### Update Code
```bash
git pull
docker-compose up -d --build
```

### Update Dependencies

Backend:
```bash
# Edit backend/requirements.txt
docker-compose build backend
docker-compose up -d backend
```

Frontend:
```bash
# Edit frontend/package.json
docker-compose build frontend
docker-compose up -d frontend
```

## 📈 Monitoring

### Check Service Status
```bash
docker-compose ps
```

### Resource Usage
```bash
docker stats
```

### Health Checks
```bash
# Backend
curl http://localhost:8000/health

# Frontend
curl http://localhost/

# AI Info
curl http://localhost:8000/ai/info
```

## 🧹 Cleanup

### Stop and remove containers
```bash
docker-compose down
```

### Remove volumes
```bash
docker-compose down -v
```

### Remove images
```bash
docker-compose down --rmi all
```

### Complete cleanup
```bash
docker-compose down -v --rmi all
docker system prune -a
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)

## 🆘 Support

For issues:
1. Check logs: `./logs.sh`
2. Verify health: `curl http://localhost:8000/health`
3. Review configuration: `cat .env`
4. Check service account: `cat service-account.json | jq`

## 📝 License

See LICENSE file in project root.

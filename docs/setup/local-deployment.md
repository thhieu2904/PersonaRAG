# Local Deployment Guide

## 🐳 Docker Local Setup

### 1. Build và chạy với Docker Compose

```bash
# Clone repository
git clone https://github.com/thhieu2904/PersonaRAG.git
cd PersonaRAG

# Build và start services
docker-compose up -d --build

# Check logs
docker-compose logs -f
```

### 2. Dockerfile cho backend

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ .

# Create directories
RUN mkdir -p data/voices data/audio_samples temp_audio logs

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3. Docker Compose Local

```yaml
version: "3.8"

services:
  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./backend/data:/app/data
      - ./backend/temp_audio:/app/temp_audio
      - ./backend/logs:/app/logs
    environment:
      - PYTHONPATH=/app
      - TTS_CACHE_SIZE=50
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    depends_on:
      - backend
    environment:
      - REACT_APP_API_URL=http://localhost:8000
```

## 🔧 Development Setup

### 1. Manual setup (không Docker)

```bash
# Backend setup
cd backend
conda create -n PersonaRAG python=3.11
conda activate PersonaRAG
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install

# Start services
# Terminal 1: Backend
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend && npm start
```

### 2. Environment Variables

```env
# .env file
PYTHONPATH=./backend
TTS_CACHE_SIZE=50
TTS_MODEL_CACHE_SIZE=3
LOG_LEVEL=INFO
```

### 3. Volume Mapping

```bash
# Important directories to map
./backend/data          -> /app/data          # Voice data
./backend/temp_audio    -> /app/temp_audio    # Generated audio
./backend/logs          -> /app/logs          # Application logs
```

## 📦 GitHub Actions CI/CD

### Simple workflow cho container build

```yaml
# .github/workflows/build.yml
name: Build and Test

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Build Docker image
        run: docker-compose build

      - name: Run tests
        run: |
          docker-compose up -d
          sleep 30
          curl -f http://localhost:8000/health
          docker-compose down
```

## 🎯 Production-like Local

### 1. Nginx reverse proxy

```nginx
# nginx.conf
server {
    listen 80;
    server_name localhost;

    location /api/ {
        proxy_pass http://backend:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location / {
        proxy_pass http://frontend:3000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. Docker Compose with Nginx

```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - backend
      - frontend

  backend:
    # ... existing config
    expose:
      - "8000"
    # Remove ports mapping

  frontend:
    # ... existing config
    expose:
      - "3000"
    # Remove ports mapping
```

## 🔧 Maintenance

### Cleanup commands

```bash
# Remove old containers
docker-compose down
docker system prune -f

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Backup voice data

```bash
# Backup before updates
docker run --rm -v personarag_voice_data:/data -v $(pwd):/backup alpine tar czf /backup/voice_backup.tar.gz /data
```

### Update deployment

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

## 📊 Monitoring

### Health checks

```bash
# Check service health
curl http://localhost:8000/health

# Check container status
docker-compose ps

# Check logs
docker-compose logs backend
```

### Resource usage

```bash
# Monitor resource usage
docker stats

# Check disk usage
docker system df
```

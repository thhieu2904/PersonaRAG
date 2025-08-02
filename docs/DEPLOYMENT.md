# PersonaRAG TTS Service - Production Deployment Guide

## 🚀 Tổng quan

PersonaRAG TTS Service đã được tối ưu hóa cho production deployment với:

- **Singleton Pattern**: Khởi tạo nhanh, chia sẻ memory
- **Docker Containerization**: Deployment nhất quán
- **Caching System**: Audio và model caching
- **Few-shot Training**: Fine-tuning cho từng character
- **Load Balancing**: Nginx reverse proxy
- **Monitoring**: Prometheus + Grafana

## 📁 Cấu trúc Project

```
PersonaRAG/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── tts_service_singleton.py    # Singleton service
│   │   │   └── tts_config.py
│   │   ├── api/v1/
│   │   │   └── tts_optimized.py            # Production API
│   │   └── main_optimized.py               # FastAPI app
│   ├── data/
│   │   └── voices/                         # Character training data
│   ├── models/
│   │   ├── base_models/                    # Base F5-TTS models
│   │   └── tuned_models/                   # Fine-tuned models
│   ├── scripts/
│   │   ├── fine_tune.py                    # Training script
│   │   ├── Dockerfile.training             # Training container
│   │   └── run_training.sh                 # Training workflow
│   ├── Dockerfile.production               # Production container
│   └── requirements.txt
├── nginx/
│   └── nginx.conf                          # Load balancer config
├── docker-compose.production.yml           # Production stack
└── scripts/
    └── migrate_to_production.sh            # Migration script
```

## 🔄 Migration từ Development

### 1. Chạy Migration Script

```bash
# Di chuyển đến thư mục project
cd PersonaRAG

# Chạy migration script
chmod +x scripts/migrate_to_production.sh
./scripts/migrate_to_production.sh
```

Script sẽ:

- ✅ Backup current setup
- ✅ Migrate data structure
- ✅ Create production environment
- ✅ Build Docker images
- ✅ Test production setup

### 2. Manual Migration (nếu cần)

```bash
# 1. Migrate data structure
mkdir -p backend/data/voices backend/models/{base_models,tuned_models}

# 2. Migrate existing audio files
for file in backend/data/audio_samples/*.wav; do
    char_name=$(basename "$file" .wav)
    mkdir -p "backend/data/voices/$char_name"
    cp "$file" "backend/data/voices/$char_name/reference.wav"
    # Create metadata.json (see template below)
done

# 3. Build production image
docker-compose -f docker-compose.production.yml build
```

## 🐋 Docker Deployment

### Production Stack

```bash
# Start full production stack
docker-compose -f docker-compose.production.yml up -d

# Start only TTS service
docker-compose -f docker-compose.production.yml up -d tts-service

# Check status
docker-compose -f docker-compose.production.yml ps

# View logs
docker-compose -f docker-compose.production.yml logs -f tts-service
```

### Services trong Stack

1. **tts-service**: Main TTS API service
2. **nginx**: Reverse proxy và load balancer
3. **redis-cache**: Caching layer (optional)
4. **prometheus**: Metrics collection
5. **grafana**: Monitoring dashboard

### Environment Variables

```env
# Service Configuration
TTS_LOG_LEVEL=INFO
TTS_CACHE_SIZE=50
TTS_MODEL_CACHE_SIZE=3

# Device Configuration
CUDA_VISIBLE_DEVICES=0

# API Configuration
API_WORKERS=1
API_HOST=0.0.0.0
API_PORT=8000
```

## 🏋️ Fine-tuning Workflow

### 1. Chuẩn bị Training Data

```bash
# Tạo character directory
mkdir -p backend/data/voices/new_character

# Thêm audio samples
cp audio1.wav backend/data/voices/new_character/
cp audio2.wav backend/data/voices/new_character/

# Tạo metadata.json
cat > backend/data/voices/new_character/metadata.json << EOF
{
    "character_name": "new_character",
    "description": "New character voice",
    "language": "vi-VN",
    "reference_text": "",
    "samples": [
        {"file": "audio1.wav", "text": "Text content 1", "duration": 3.5},
        {"file": "audio2.wav", "text": "Text content 2", "duration": 2.8}
    ],
    "tuning_config": {
        "learning_rate": 1e-5,
        "epochs": 50,
        "batch_size": 2
    }
}
EOF
```

### 2. Chạy Fine-tuning

```bash
# Using Docker (recommended)
cd backend/scripts
./run_training.sh new_character train

# Or manually with Python
python backend/scripts/fine_tune.py --character_name new_character
```

### 3. Deploy Tuned Model

Sau khi training, model sẽ được lưu trong `backend/models/tuned_models/new_character.pt`. Service sẽ tự động detect và sử dụng.

## 🌐 API Endpoints

### Core TTS Endpoints

```bash
# Synthesize speech (return audio file)
curl -X POST "http://localhost:8000/api/v1/tts/synthesize" \
     -H "Content-Type: application/json" \
     -d '{"text": "Xin chào", "character": "gia_cat_luong"}' \
     --output audio.wav

# Synthesize speech (return JSON with base64)
curl -X POST "http://localhost:8000/api/v1/tts/synthesize-json" \
     -H "Content-Type: application/json" \
     -d '{"text": "Xin chào", "character": "gia_cat_luong"}'

# Batch synthesis
curl -X POST "http://localhost:8000/api/v1/tts/synthesize-batch" \
     -H "Content-Type: application/json" \
     -d '{
       "requests": [
         {"text": "Text 1", "character": "char1"},
         {"text": "Text 2", "character": "char2"}
       ],
       "parallel": true
     }'
```

### Management Endpoints

```bash
# Get available characters
curl "http://localhost:8000/api/v1/tts/characters"

# Get service statistics
curl "http://localhost:8000/api/v1/tts/stats"

# Health check
curl "http://localhost:8000/api/v1/tts/health"

# Clear cache
curl -X DELETE "http://localhost:8000/api/v1/tts/cache?cache_type=audio"
```

## 📊 Monitoring & Logging

### Service Stats

```bash
# Get performance metrics
curl "http://localhost:8000/api/v1/tts/stats" | jq
```

Response:

```json
{
  "uptime_seconds": 3600,
  "total_requests": 150,
  "cache_hits": 45,
  "cache_hit_rate_percent": 30.0,
  "average_inference_time": 3.2,
  "cached_models": 2,
  "cached_audio_files": 25,
  "device": "cuda:0",
  "base_model_loaded": true
}
```

### Docker Logs

```bash
# TTS service logs
docker-compose -f docker-compose.production.yml logs tts-service

# All services logs
docker-compose -f docker-compose.production.yml logs

# Follow logs
docker-compose -f docker-compose.production.yml logs -f
```

### Prometheus Metrics

Truy cập: `http://localhost:9090`

Key metrics:

- Request rate
- Response time
- Error rate
- Memory usage
- GPU utilization

### Grafana Dashboard

Truy cập: `http://localhost:3000` (admin/admin123)

Dashboards:

- TTS Service Performance
- System Resources
- Error Tracking

## ⚙️ Configuration

### Nginx Configuration

File: `nginx/nginx.conf`

- Rate limiting cho TTS endpoints
- Extended timeouts cho audio generation
- CORS headers
- Gzip compression

### Production Environment

File: `.env.production`

```env
# Performance tuning
TTS_CACHE_SIZE=50                    # Audio cache size
TTS_MODEL_CACHE_SIZE=3               # Model cache size
TTS_MAX_TEXT_LENGTH=1000             # Max input text length
TTS_MAX_BATCH_SIZE=10                # Max batch requests

# Security
API_RATE_LIMIT_TTS=10                # TTS requests per second
API_RATE_LIMIT_API=30                # API requests per second
API_CORS_ORIGINS=*                   # CORS origins (set properly for production)

# Hardware optimization
TORCH_NUM_THREADS=4                  # PyTorch CPU threads
CUDA_VISIBLE_DEVICES=0               # GPU device
```

## 🔧 Troubleshooting

### Common Issues

1. **Memory Issues**

   ```bash
   # Check memory usage
   docker stats personarag-tts-service

   # Reduce cache sizes in .env.production
   TTS_CACHE_SIZE=20
   TTS_MODEL_CACHE_SIZE=1
   ```

2. **CUDA Issues**

   ```bash
   # Check GPU availability
   docker exec personarag-tts-service python -c "import torch; print(torch.cuda.is_available())"

   # Run on CPU only
   docker-compose -f docker-compose.production.yml up -d --scale tts-service=1
   ```

3. **Model Loading Issues**

   ```bash
   # Check model files
   docker exec personarag-tts-service ls -la models/

   # Reinitialize service
   curl -X DELETE "http://localhost:8000/api/v1/tts/cache?cache_type=models"
   ```

### Health Diagnostics

```bash
# Comprehensive health check
curl "http://localhost:8000/api/v1/tts/health" | jq

# Service statistics
curl "http://localhost:8000/api/v1/tts/stats" | jq

# Available characters
curl "http://localhost:8000/api/v1/tts/characters" | jq
```

## 🚀 Performance Optimization

### Caching Strategy

1. **Audio Cache**: Lưu generated audio với hash của input
2. **Model Cache**: Giữ character models trong memory
3. **Redis Cache**: External caching layer (optional)

### Scaling

```bash
# Scale TTS service (multiple containers)
docker-compose -f docker-compose.production.yml up -d --scale tts-service=3

# Load balancing with Nginx
# (Nginx sẽ tự động distribute requests)
```

### Hardware Recommendations

- **CPU**: Minimum 4 cores, 8 cores recommended
- **RAM**: Minimum 8GB, 16GB recommended
- **GPU**: NVIDIA GPU với 8GB+ VRAM (optional nhưng highly recommended)
- **Storage**: SSD với 50GB+ free space

## 📋 Maintenance

### Backup

```bash
# Backup models và data
docker run --rm -v personarag_models:/data -v $(pwd):/backup alpine tar czf /backup/models_backup.tar.gz /data

# Backup configuration
cp .env.production docker-compose.production.yml nginx/nginx.conf backup/
```

### Updates

```bash
# Pull latest images
docker-compose -f docker-compose.production.yml pull

# Rebuild custom images
docker-compose -f docker-compose.production.yml build --no-cache

# Rolling update
docker-compose -f docker-compose.production.yml up -d
```

### Cleanup

```bash
# Stop services
docker-compose -f docker-compose.production.yml down

# Remove unused images
docker image prune -f

# Remove unused volumes
docker volume prune -f
```

## 🔐 Security Considerations

1. **Network Security**: Configure proper CORS origins
2. **Rate Limiting**: Implemented in Nginx
3. **User Isolation**: Run containers as non-root user
4. **Input Validation**: API validates text length và character names
5. **SSL/TLS**: Configure HTTPS in production (see nginx.conf template)

## 📞 Support

Nếu gặp vấn đề:

1. Check logs: `docker-compose logs tts-service`
2. Check health: `curl localhost:8000/health`
3. Check resources: `docker stats`
4. Clear cache: `curl -X DELETE localhost:8000/api/v1/tts/cache`
5. Restart service: `docker-compose restart tts-service`

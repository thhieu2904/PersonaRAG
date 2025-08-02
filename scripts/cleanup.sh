#!/bin/bash
# PersonaRAG Cleanup Script - Local Development

echo "🧹 PersonaRAG Project Cleanup"
echo "============================="

# Remove Python cache
echo "🐍 Cleaning Python cache..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -exec rm -f {} + 2>/dev/null || true
find . -name "*.pyo" -exec rm -f {} + 2>/dev/null || true

# Remove temporary audio files (keep voice data!)
echo "🎵 Cleaning temporary audio..."
rm -rf backend/temp_audio/*.wav 2>/dev/null || true
rm -rf backend/temp_audio/*.mp3 2>/dev/null || true
rm -rf backend/test_output/ 2>/dev/null || true

# Remove logs
echo "📝 Cleaning logs..."
rm -rf backend/logs/*.log 2>/dev/null || true
rm -rf logs/ 2>/dev/null || true

# Remove Node modules build cache
echo "⚛️ Cleaning frontend cache..."
rm -rf frontend/node_modules/.cache/ 2>/dev/null || true
rm -rf frontend/build/ 2>/dev/null || true
rm -rf frontend/dist/ 2>/dev/null || true

# Remove development temporary files
echo "🛠️ Cleaning development files..."
rm -f backend/test_*.py 2>/dev/null || true
rm -f backend/debug_*.py 2>/dev/null || true
rm -f backend/temp_*.py 2>/dev/null || true
rm -f *_backup.* 2>/dev/null || true

# Docker cleanup (optional)
echo "🐳 Cleaning Docker (if running)..."
docker system prune -f 2>/dev/null || true

# Summary
echo ""
echo "✅ Cleanup completed!"
echo ""
echo "📊 Project size after cleanup:"
du -sh . 2>/dev/null || echo "Size calculation unavailable"
echo ""
echo "🔒 Preserved files:"
echo "   - backend/data/voices/**/*.wav (voice data)"
echo "   - backend/data/audio_samples/*.wav (reference audio)"
echo "   - All source code and configuration"
echo ""
echo "💡 Next steps:"
echo "   - Test: python backend/test_tts_simple.py"
echo "   - Start: docker-compose up -d"

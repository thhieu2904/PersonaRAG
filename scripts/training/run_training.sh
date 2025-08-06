# backend/scripts/run_training.sh
#!/bin/bash

# Script để chạy fine-tuning trong Docker
# Usage: ./run_training.sh [character_name]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if Docker and Docker Compose are installed
check_dependencies() {
    log "Checking dependencies..."
    
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    success "Dependencies check passed"
}

# Check NVIDIA Docker support
check_nvidia_docker() {
    log "Checking NVIDIA Docker support..."
    
    if ! docker run --rm --gpus all nvidia/cuda:11.8-base-ubuntu20.04 nvidia-smi &> /dev/null; then
        warning "NVIDIA Docker support not detected. Training will run on CPU."
        export TRAINING_DEVICE="cpu"
    else
        success "NVIDIA Docker support detected"
        export TRAINING_DEVICE="gpu"
    fi
}

# Validate character data
validate_character() {
    local character_name=$1
    local voices_dir="../data/voices/$character_name"
    
    log "Validating character data for: $character_name"
    
    if [ ! -d "$voices_dir" ]; then
        error "Character directory not found: $voices_dir"
        exit 1
    fi
    
    if [ ! -f "$voices_dir/metadata.json" ]; then
        error "Metadata file not found: $voices_dir/metadata.json"
        exit 1
    fi
    
    # Check if there are any audio files
    audio_count=$(find "$voices_dir" -name "*.wav" | wc -l)
    if [ "$audio_count" -eq 0 ]; then
        error "No audio files found in: $voices_dir"
        exit 1
    fi
    
    success "Character data validation passed ($audio_count audio files found)"
}

# Build Docker image
build_image() {
    log "Building Docker image for training..."
    
    cd "$(dirname "$0")"
    docker-compose -f docker-compose.training.yml build tts-training
    
    if [ $? -eq 0 ]; then
        success "Docker image built successfully"
    else
        error "Failed to build Docker image"
        exit 1
    fi
}

# Run training
run_training() {
    local character_name=$1
    
    log "Starting fine-tuning for character: $character_name"
    log "Device: $TRAINING_DEVICE"
    
    # Start services
    docker-compose -f docker-compose.training.yml up -d
    
    # Wait for container to be ready
    sleep 5
    
    # Execute training
    docker-compose -f docker-compose.training.yml exec tts-training \
        python scripts/fine_tune.py \
        --character_name "$character_name" \
        --device "$TRAINING_DEVICE"
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        success "Fine-tuning completed successfully!"
        log "Tuned model should be available in models/tuned_models/"
    else
        error "Fine-tuning failed with exit code: $exit_code"
    fi
    
    return $exit_code
}

# Cleanup function
cleanup() {
    log "Cleaning up Docker resources..."
    docker-compose -f docker-compose.training.yml down
}

# Show logs
show_logs() {
    log "Showing training logs..."
    docker-compose -f docker-compose.training.yml logs -f tts-training
}

# Main function
main() {
    local character_name=${1:-"gia_cat_luong"}
    local command=${2:-"train"}
    
    echo "=================================================="
    echo "  PersonaRAG TTS Fine-tuning Script"
    echo "=================================================="
    echo "Character: $character_name"
    echo "Command: $command"
    echo "=================================================="
    
    case $command in
        "train")
            check_dependencies
            check_nvidia_docker
            validate_character "$character_name"
            build_image
            
            # Setup trap for cleanup
            trap cleanup EXIT
            
            run_training "$character_name"
            ;;
        "build")
            check_dependencies
            build_image
            ;;
        "logs")
            show_logs
            ;;
        "cleanup")
            cleanup
            ;;
        *)
            echo "Usage: $0 [character_name] [train|build|logs|cleanup]"
            echo ""
            echo "Commands:"
            echo "  train   - Run full training pipeline (default)"
            echo "  build   - Build Docker image only"
            echo "  logs    - Show training logs"
            echo "  cleanup - Stop and remove containers"
            echo ""
            echo "Examples:"
            echo "  $0 gia_cat_luong train"
            echo "  $0 gia_cat_luong build"
            echo "  $0 gia_cat_luong logs"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"

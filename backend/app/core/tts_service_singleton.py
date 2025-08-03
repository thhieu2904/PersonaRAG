# backend/app/core/tts_service_singleton.py
"""
Singleton TTS Service cho production deployment
Tối ưu hóa khởi tạo và quản lý memory cho frontend
"""
import asyncio
import logging
import threading
import time
from pathlib import Path
from typing import Dict, Optional, Union, Any
import torch

from .tts_config import TTSConfig

logger = logging.getLogger(__name__)

class TTSServiceSingleton:
    """
    Singleton TTS Service với lazy loading và caching
    Tối ưu hóa cho deployment với multiple workers
    """
    
    _instance = None
    _lock = threading.Lock()
    _initialized = False
    
    def __new__(cls) -> 'TTSServiceSingleton':
        """Thread-safe singleton implementation"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(TTSServiceSingleton, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize singleton (chỉ chạy một lần)"""
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    self._setup_singleton()
                    self._initialized = True
    
    def _setup_singleton(self):
        """Setup singleton state"""
        logger.info("🚀 Initializing TTS Service Singleton...")
        
        # Core attributes
        self.config = TTSConfig()
        self.device = self.config.get_device()
        
        # Model storage
        self._base_model = None
        self._character_models: Dict[str, Any] = {}
        self._model_cache_size = 3  # Maximum cached models
        
        # Audio cache
        self._audio_cache: Dict[str, bytes] = {}
        self._cache_max_size = 50  # Maximum cached audio files
        
        # Performance tracking
        self._stats = {
            'total_requests': 0,
            'cache_hits': 0,
            'model_loads': 0,
            'inference_times': [],
            'startup_time': time.time()
        }
        
        # State flags
        self._base_model_loaded = False
        self._loading_lock = threading.Lock()
        
        logger.info(f"✅ TTS Service Singleton initialized on device: {self.device}")
    
    def _get_cache_key(self, text: str, character: str, **kwargs) -> str:
        """Generate cache key for audio requests"""
        import hashlib
        
        # Include all relevant parameters in cache key
        cache_data = f"{text}|{character}|{kwargs.get('speed', 1.0)}|{kwargs.get('temperature', 0.7)}"
        return hashlib.md5(cache_data.encode()).hexdigest()
    
    def _load_base_model(self):
        """Lazy load base model"""
        if self._base_model_loaded:
            return
            
        with self._loading_lock:
            if self._base_model_loaded:
                return
                
            try:
                logger.info("📦 Loading base F5-TTS model...")
                start_time = time.time()
                
                # Import F5-TTS components
                import sys
                from pathlib import Path
                
                # Add F5-TTS path
                f5_tts_path = Path(__file__).parent.parent.parent / "F5-TTS-Vietnamese-100h"
                if str(f5_tts_path) not in sys.path:
                    sys.path.insert(0, str(f5_tts_path))
                
                from f5_tts.model import DiT
                from f5_tts.infer.utils_infer import (
                    load_model,
                    load_vocoder,
                    preprocess_ref_audio_text,
                    infer_process,
                    remove_silence_for_generated_wav
                )
                
                # Store imports for later use
                self._f5_imports = {
                    'DiT': DiT,
                    'load_model': load_model,
                    'load_vocoder': load_vocoder,
                    'preprocess_ref_audio_text': preprocess_ref_audio_text,
                    'infer_process': infer_process,
                    'remove_silence_for_generated_wav': remove_silence_for_generated_wav
                }
                
                # Load model
                model_name = "F5-TTS"
                model_path = "hf://SWivid/F5-TTS-Vietnamese-ViVoice/model_1200000.safetensors"
                
                self._base_model, self._vocab_char_map, self._vocab_size = self._f5_imports['load_model'](
                    model_name, model_path, self.device
                )
                
                # Load vocoder
                self._vocoder = self._f5_imports['load_vocoder']()
                
                load_time = time.time() - start_time
                self._stats['model_loads'] += 1
                self._base_model_loaded = True
                
                logger.info(f"✅ Base model loaded in {load_time:.2f}s")
                
            except Exception as e:
                logger.error(f"❌ Failed to load base model: {e}")
                raise
    
    def _load_character_model(self, character: str) -> Any:
        """Load character-specific tuned model"""
        if character in self._character_models:
            return self._character_models[character]
            
        try:
            # Check for tuned model
            tuned_model_path = Path(f"models/tuned_models/{character}.pt")
            
            if tuned_model_path.exists():
                logger.info(f"📦 Loading tuned model for {character}")
                
                # Load tuned model
                model_data = torch.load(tuned_model_path, map_location=self.device)
                
                # TODO: Implement actual model loading logic
                # For now, use base model
                character_model = self._base_model
                
                # Cache management
                if len(self._character_models) >= self._model_cache_size:
                    # Remove oldest model
                    oldest_char = next(iter(self._character_models))
                    del self._character_models[oldest_char]
                    logger.info(f"🗑️ Removed cached model for {oldest_char}")
                
                self._character_models[character] = character_model
                logger.info(f"✅ Character model for {character} loaded and cached")
                
                return character_model
            else:
                logger.info(f"⚠️ No tuned model found for {character}, using base model")
                return self._base_model
                
        except Exception as e:
            logger.error(f"❌ Failed to load character model for {character}: {e}")
            return self._base_model
    
    def _get_reference_audio(self, character: str) -> tuple:
        """Get reference audio for character"""
        try:
            # Default reference
            ref_audio_path = f"data/audio_samples/{character}.wav"
            ref_text = ""  # Empty for voice cloning
            
            # Check for character-specific reference
            character_ref_path = f"data/voices/{character}/reference.wav"
            if Path(character_ref_path).exists():
                ref_audio_path = character_ref_path
                
                # Try to load metadata for reference text
                metadata_path = f"data/voices/{character}/metadata.json"
                if Path(metadata_path).exists():
                    import json
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        ref_text = metadata.get('reference_text', "")
            
            # Preprocess audio
            ref_audio, ref_text_processed = self._f5_imports['preprocess_ref_audio_text'](
                ref_audio_path, ref_text, device=self.device
            )
            
            return ref_audio, ref_text_processed
            
        except Exception as e:
            logger.error(f"❌ Failed to get reference audio for {character}: {e}")
            raise
    
    async def synthesize_speech_async(
        self,
        text: str,
        character: str = "gia_cat_luong",
        **kwargs
    ) -> bytes:
        """Async synthesis method"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.synthesize_speech, text, character, **kwargs)
    
    def synthesize_speech(
        self,
        text: str,
        character: str = "gia_cat_luong",
        **kwargs
    ) -> bytes:
        """
        Main synthesis method với caching và optimization
        """
        start_time = time.time()
        self._stats['total_requests'] += 1
        
        try:
            # Check cache first
            cache_key = self._get_cache_key(text, character, **kwargs)
            if cache_key in self._audio_cache:
                self._stats['cache_hits'] += 1
                logger.info(f"🎯 Cache hit for {character}: {text[:50]}...")
                return self._audio_cache[cache_key]
            
            # Ensure base model is loaded
            self._load_base_model()
            
            # Load character model
            model = self._load_character_model(character)
            
            # Get reference audio
            ref_audio, ref_text = self._get_reference_audio(character)
            
            logger.info(f"🎤 Synthesizing for {character}: {text[:50]}...")
            
            # Inference parameters
            gen_params = {
                'cross_fade_duration': kwargs.get('cross_fade_duration', 0.15),
                'speed': kwargs.get('speed', 1.0),
                'show_info': kwargs.get('show_info', print),
                'progress': kwargs.get('progress', lambda x: None),
                'temperature': kwargs.get('temperature', 0.7),
                'top_p': kwargs.get('top_p', 0.9),
                'top_k': kwargs.get('top_k', 0),
                'repetition_penalty': kwargs.get('repetition_penalty', 1.0),
                'length_penalty': kwargs.get('length_penalty', 1.0)
            }
            
            # Generate audio
            final_wave, final_sample_rate, combined_spectrogram = self._f5_imports['infer_process'](
                ref_audio=ref_audio,
                ref_text=ref_text,
                gen_text=text,
                model_obj=model,
                vocoder=self._vocoder,
                mel_spec_type=self.config.mel_spec_type,
                **gen_params
            )
            
            # Remove silence
            final_wave, _ = self._f5_imports['remove_silence_for_generated_wav'](final_wave)
            
            # Convert to bytes
            import io
            import soundfile as sf
            
            buffer = io.BytesIO()
            sf.write(buffer, final_wave, final_sample_rate, format='WAV')
            audio_bytes = buffer.getvalue()
            
            # Cache result
            if len(self._audio_cache) >= self._cache_max_size:
                # Remove oldest cache entry
                oldest_key = next(iter(self._audio_cache))
                del self._audio_cache[oldest_key]
            
            self._audio_cache[cache_key] = audio_bytes
            
            # Update stats
            inference_time = time.time() - start_time
            self._stats['inference_times'].append(inference_time)
            
            logger.info(f"✅ Synthesis completed in {inference_time:.2f}s")
            
            return audio_bytes
            
        except Exception as e:
            logger.error(f"❌ Synthesis failed: {e}")
            raise
    
    def get_stats(self) -> Dict:
        """Get performance statistics"""
        current_time = time.time()
        uptime = current_time - self._stats['startup_time']
        
        avg_inference_time = 0
        if self._stats['inference_times']:
            avg_inference_time = sum(self._stats['inference_times']) / len(self._stats['inference_times'])
        
        cache_hit_rate = 0
        if self._stats['total_requests'] > 0:
            cache_hit_rate = self._stats['cache_hits'] / self._stats['total_requests'] * 100
        
        return {
            'uptime_seconds': uptime,
            'total_requests': self._stats['total_requests'],
            'cache_hits': self._stats['cache_hits'],
            'cache_hit_rate_percent': cache_hit_rate,
            'model_loads': self._stats['model_loads'],
            'average_inference_time': avg_inference_time,
            'cached_models': len(self._character_models),
            'cached_audio_files': len(self._audio_cache),
            'device': str(self.device),
            'base_model_loaded': self._base_model_loaded
        }
    
    def clear_cache(self, cache_type: str = "all"):
        """Clear various caches"""
        if cache_type in ["all", "audio"]:
            self._audio_cache.clear()
            logger.info("🗑️ Audio cache cleared")
        
        if cache_type in ["all", "models"]:
            self._character_models.clear()
            logger.info("🗑️ Model cache cleared")
        
        if cache_type == "stats":
            self._stats['inference_times'].clear()
            logger.info("🗑️ Stats cleared")
    
    def get_available_characters(self) -> list:
        """Get list of available characters"""
        characters = []
        
        # Check audio samples directory
        audio_samples_dir = Path("data/audio_samples")
        if audio_samples_dir.exists():
            for audio_file in audio_samples_dir.glob("*.wav"):
                characters.append(audio_file.stem)
        
        # Check voices directory
        voices_dir = Path("data/voices")
        if voices_dir.exists():
            for char_dir in voices_dir.iterdir():
                if char_dir.is_dir() and char_dir.name not in characters:
                    characters.append(char_dir.name)
        
        return sorted(characters)
    
    def health_check(self) -> Dict:
        """Health check for monitoring"""
        try:
            # Quick model check
            if not self._base_model_loaded:
                return {
                    'status': 'initializing',
                    'device': str(self.device),
                    'message': 'Base model not loaded yet'
                }
            
            # Memory check
            if torch.cuda.is_available():
                memory_allocated = torch.cuda.memory_allocated(self.device)
                memory_reserved = torch.cuda.memory_reserved(self.device)
                memory_info = {
                    'allocated_mb': memory_allocated / 1024 / 1024,
                    'reserved_mb': memory_reserved / 1024 / 1024
                }
            else:
                memory_info = {'note': 'CPU mode, no GPU memory tracking'}
            
            return {
                'status': 'healthy',
                'device': str(self.device),
                'uptime': time.time() - self._stats['startup_time'],
                'memory': memory_info,
                'stats': self.get_stats()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

# Global instance getter
def get_tts_service() -> TTSServiceSingleton:
    """Get singleton TTS service instance"""
    return TTSServiceSingleton()

# backend/app/core/voice_processor.py
import os
import numpy as np
import librosa
import json
import logging
import pandas as pd # Đã thêm thư viện còn thiếu
from pathlib import Path
from typing import Dict, Any
from scipy.signal import find_peaks

logger = logging.getLogger(__name__)

class VoiceProcessor:
    """
    Class để xử lý việc nhận dạng và tách đặc trưng giọng nói từ file âm thanh.
    """
    
    def __init__(self, sample_rate: int = 22050):
        """
        Khởi tạo VoiceProcessor.
        
        Args:
            sample_rate: Tần số lấy mẫu để xử lý audio. XTTSv2 của Coqui-AI
                         hoạt động tốt nhất ở 22050Hz hoặc 24000Hz.
        """
        self.sample_rate = sample_rate
        
    def extract_voice_features(self, audio_path: str) -> Dict[str, Any]:
        """
        Tách các đặc trưng giọng nói chính từ một file audio.
        
        Args:
            audio_path: Đường dẫn đến file audio.
            
        Returns:
            Một dictionary chứa các đặc trưng đã được trích xuất.
        """
        try:
            logger.info(f"Loading audio from: {audio_path}")
            audio, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            features = {
                'mfcc': self._extract_mfcc(audio, sr),
                'pitch': self._extract_pitch(audio, sr),
                'spectral_features': self._extract_spectral_features(audio, sr),
                'prosody': self._extract_prosody_features(audio, sr),
                'formants': self._extract_formants(audio, sr)
            }
            
            logger.info(f"Successfully extracted features from {audio_path}")
            return features
            
        except Exception as e:
            logger.error(f"Error extracting features from {audio_path}: {e}")
            raise

    def _extract_mfcc(self, audio: np.ndarray, sr: int, n_mfcc: int = 20) -> list:
        """Trích xuất MFCC features (đặc trưng âm sắc)."""
        mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=n_mfcc)
        return np.mean(mfcc, axis=1).tolist()

    def _extract_pitch(self, audio: np.ndarray, sr: int) -> Dict[str, float]:
        """Trích xuất thông tin về pitch (cao độ)."""
        pitches, magnitudes = librosa.piptrack(y=audio, sr=sr)
        pitch_values = pitches[magnitudes > np.median(magnitudes)]
        
        if pitch_values.any():
            return {
                'mean': float(np.mean(pitch_values)),
                'std_dev': float(np.std(pitch_values)),
                'min': float(np.min(pitch_values)),
                'max': float(np.max(pitch_values))
            }
        return {'mean': 0, 'std_dev': 0, 'min': 0, 'max': 0}

    def _extract_spectral_features(self, audio: np.ndarray, sr: int) -> Dict[str, float]:
        """Trích xuất các đặc trưng về phổ tần."""
        spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sr)
        spectral_contrast = librosa.feature.spectral_contrast(y=audio, sr=sr)
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)
        
        return {
            'centroid_mean': float(np.mean(spectral_centroid)),
            'bandwidth_mean': float(np.mean(spectral_bandwidth)),
            'contrast_mean': float(np.mean(spectral_contrast)),
            'rolloff_mean': float(np.mean(spectral_rolloff))
        }

    def _extract_prosody_features(self, audio: np.ndarray, sr: int) -> Dict[str, float]:
        """Trích xuất đặc trưng về ngữ điệu (năng lượng và nhịp điệu)."""
        rms_energy = librosa.feature.rms(y=audio)
        tempo, _ = librosa.beat.beat_track(y=audio, sr=sr)
        
        return {
            'energy_mean': float(np.mean(rms_energy)),
            'energy_std_dev': float(np.std(rms_energy)),
            'tempo': float(tempo)
        }

    def _extract_formants(self, audio: np.ndarray, sr: int, n_formants: int = 4) -> Dict[str, float]:
        """Trích xuất các tần số formant chính."""
        # Đây là một phương pháp ước tính đơn giản
        D = librosa.stft(audio)
        S, phase = librosa.magphase(D)
        freqs = librosa.fft_frequencies(sr=sr)
        
        # Tìm các đỉnh trong phổ trung bình
        mean_spectrum = np.mean(S, axis=1)
        peaks, _ = find_peaks(mean_spectrum, height=np.mean(mean_spectrum), distance=sr//500)
        
        formant_freqs = sorted(freqs[peaks])[:n_formants]
        
        result = {}
        for i, freq in enumerate(formant_freqs, 1):
            result[f'f{i}'] = float(freq)
        
        # Điền các formant còn thiếu bằng 0
        for i in range(len(formant_freqs) + 1, n_formants + 1):
            result[f'f{i}'] = 0.0
            
        return result

    def save_voice_profile(self, features: Dict[str, Any], output_path: str, character_name: str):
        """
        Lưu profile giọng nói thành file JSON.
        
        Args:
            features: Dictionary các đặc trưng đã trích xuất.
            output_path: Đường dẫn để lưu file profile.
            character_name: Tên của nhân vật.
        """
        profile = {
            'character_name': character_name,
            'voice_features': features,
            'created_at': str(pd.Timestamp.now()),
            'sample_rate': self.sample_rate
        }
        
        # Đảm bảo thư mục tồn tại
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=4, ensure_ascii=False)
            
        logger.info(f"Voice profile for '{character_name}' saved to {output_path}")


# backend/scripts/generate_metadata.py
"""
Script tự động tạo metadata cho tất cả characters trong data/voices/
"""
import json
import os
from pathlib import Path
import argparse
from typing import Dict, List

def get_audio_duration(audio_path: str) -> float:
    """Get duration của audio file"""
    try:
        # Try with librosa first
        try:
            import librosa
            duration = librosa.get_duration(path=audio_path)
            return round(duration, 2)
        except ImportError:
            # Fallback to mutagen if librosa not available
            try:
                from mutagen import File
                audio_file = File(audio_path)
                if audio_file is not None and hasattr(audio_file, 'info'):
                    return round(audio_file.info.length, 2)
            except ImportError:
                pass
            
            # Last fallback - estimate from file size (very rough)
            file_size = os.path.getsize(audio_path)
            # Rough estimate: 16-bit, 24kHz stereo = ~96KB/sec
            estimated_duration = file_size / 96000
            return round(estimated_duration, 2)
            
    except Exception as e:
        print(f"Warning: Cannot get duration for {audio_path}: {e}")
        return 0.0

def scan_character_directory(character_dir: Path) -> Dict:
    """Scan một character directory và tạo metadata"""
    character_name = character_dir.name
    
    # Find all audio files
    audio_files = []
    audio_extensions = ['.wav', '.mp3', '.m4a', '.flac']
    
    for ext in audio_extensions:
        audio_files.extend(character_dir.glob(f"*{ext}"))
    
    audio_files = sorted(audio_files)
    
    if not audio_files:
        print(f"Warning: No audio files found in {character_dir}")
        return None
    
    print(f"Found {len(audio_files)} audio files for {character_name}")
    
    # Create samples list
    samples = []
    total_duration = 0
    
    for i, audio_file in enumerate(audio_files):
        try:
            duration = get_audio_duration(str(audio_file))
            total_duration += duration
            
            samples.append({
                "file": audio_file.name,
                "text": f"Sample {i+1} for {character_name}",  # Placeholder text
                "duration": duration
            })
        except Exception as e:
            print(f"Error processing {audio_file}: {e}")
            continue
    
    if not samples:
        return None
    
    # Create metadata
    metadata = {
        "character_name": character_name,
        "description": f"Voice profile for {character_name}",
        "language": "vi-VN",
        "sample_rate": 24000,
        "total_samples": len(samples),
        "total_duration": round(total_duration, 2),
        "samples": samples,
        "tuning_config": {
            "learning_rate": 1e-5,
            "epochs": 50,
            "batch_size": 2,
            "warmup_steps": 100,
            "gradient_accumulation_steps": 1,
            "save_steps": 500
        },
        "created_at": "2025-08-02",
        "version": "2.0",
        "auto_generated": True
    }
    
    return metadata

def main():
    parser = argparse.ArgumentParser(description='Generate metadata for voice characters')
    parser.add_argument('--voices_dir', default='data/voices', help='Path to voices directory')
    parser.add_argument('--force', action='store_true', help='Overwrite existing metadata files')
    parser.add_argument('--character', help='Generate metadata for specific character only')
    
    args = parser.parse_args()
    
    voices_dir = Path(args.voices_dir)
    if not voices_dir.exists():
        print(f"Error: Voices directory not found: {voices_dir}")
        return
    
    print(f"Scanning voices directory: {voices_dir}")
    
    # Get character directories
    character_dirs = []
    if args.character:
        char_dir = voices_dir / args.character
        if char_dir.exists() and char_dir.is_dir():
            character_dirs.append(char_dir)
        else:
            print(f"Error: Character directory not found: {char_dir}")
            return
    else:
        character_dirs = [d for d in voices_dir.iterdir() if d.is_dir()]
    
    print(f"Found {len(character_dirs)} character directories")
    
    for char_dir in character_dirs:
        print(f"\n=== Processing {char_dir.name} ===")
        
        metadata_file = char_dir / "metadata.json"
        
        # Check if metadata already exists
        if metadata_file.exists() and not args.force:
            print(f"Metadata already exists for {char_dir.name}, skipping (use --force to overwrite)")
            continue
        
        # Generate metadata
        metadata = scan_character_directory(char_dir)
        
        if metadata is None:
            print(f"Failed to generate metadata for {char_dir.name}")
            continue
        
        # Save metadata
        try:
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Generated metadata for {char_dir.name}")
            print(f"   - {metadata['total_samples']} samples")
            print(f"   - {metadata['total_duration']}s total duration")
            print(f"   - Saved to: {metadata_file}")
            
        except Exception as e:
            print(f"❌ Failed to save metadata for {char_dir.name}: {e}")

if __name__ == "__main__":
    main()

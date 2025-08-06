# backend/scripts/configure_voice_settings.py
"""
Script để cấu hình voice settings cho từng nhân vật
"""
import json
import argparse
from pathlib import Path
from typing import Dict, Any

def load_character_metadata(character_name: str) -> Dict[str, Any]:
    """Load metadata của character"""
    voices_dir = Path("data/voices")
    metadata_file = voices_dir / character_name / "metadata.json"
    
    if not metadata_file.exists():
        raise FileNotFoundError(f"Metadata not found for {character_name}")
    
    with open(metadata_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_character_metadata(character_name: str, metadata: Dict[str, Any]):
    """Save metadata của character"""
    voices_dir = Path("data/voices")
    metadata_file = voices_dir / character_name / "metadata.json"
    
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

def configure_voice_settings(character_name: str, settings: Dict[str, Any]):
    """Cấu hình voice settings cho character"""
    try:
        # Load existing metadata
        metadata = load_character_metadata(character_name)
        
        # Add or update voice_settings
        if "voice_settings" not in metadata:
            metadata["voice_settings"] = {}
        
        # Update settings
        metadata["voice_settings"].update(settings)
        
        # Update version and timestamp
        import datetime
        metadata["version"] = "2.1"
        metadata["updated_at"] = datetime.datetime.now().isoformat()
        
        # Save metadata
        save_character_metadata(character_name, metadata)
        
        print(f"✅ Updated voice settings for {character_name}")
        print(f"Settings: {json.dumps(settings, indent=2, ensure_ascii=False)}")
        
    except Exception as e:
        print(f"❌ Error configuring voice settings: {e}")

def get_default_settings_for_character(character_name: str) -> Dict[str, Any]:
    """Get default settings based on character personality"""
    
    presets = {
        "gia_cat_luong": {
            "speed": 0.6,  # Chậm rãi hơn, thông thái sâu sắc
            "temperature": 0.55,  # Ổn định hơn
            "pause_scale": 1.8,  # Nghỉ lâu hơn để thể hiện tính cách thâm thúy
            "stress_scale": 0.75,  # Nhẹ nhàng, uy quyền
            "pitch_scale": 0.92,  # Trầm hơn cho uy tín
            "emotion_scale": 1.2,  # Thêm cảm xúc
            "breath_scale": 1.5,  # Lấy hơi tự nhiên hơn
            "description": "Giọng nói chậm rãi, thâm thúy của quân sư thông thái"
        },
        "tu_ma_y": {
            "speed": 0.85,  # Nhanh hơn, năng động
            "temperature": 0.8,  # Nhiều biến đổi hơn
            "pause_scale": 1.2,  # Nghỉ bình thường
            "stress_scale": 1.0,  # Bình thường
            "pitch_scale": 1.05,  # Hơi cao
            "description": "Giọng nói năng động, quyết đoán của tướng quân"
        }
    }
    
    if character_name in presets:
        return presets[character_name]
    else:
        # Default settings cho character mới
        return {
            "speed": 0.8,
            "temperature": 0.7,
            "pause_scale": 1.3,
            "stress_scale": 0.9,
            "pitch_scale": 1.0,
            "description": f"Default voice settings for {character_name}"
        }

def list_characters():
    """List all available characters"""
    voices_dir = Path("data/voices")
    if not voices_dir.exists():
        print("❌ Voices directory not found")
        return []
    
    characters = []
    for char_dir in voices_dir.iterdir():
        if char_dir.is_dir() and (char_dir / "metadata.json").exists():
            characters.append(char_dir.name)
    
    return characters

def show_current_settings(character_name: str):
    """Show current voice settings for character"""
    try:
        metadata = load_character_metadata(character_name)
        
        print(f"\n=== Voice Settings for {character_name} ===")
        print(f"Description: {metadata.get('description', 'N/A')}")
        
        voice_settings = metadata.get('voice_settings', {})
        if voice_settings:
            print("\nCurrent Settings:")
            for key, value in voice_settings.items():
                print(f"  {key}: {value}")
        else:
            print("No custom voice settings found. Using defaults.")
            
        print(f"\nTotal samples: {metadata.get('total_samples', 0)}")
        print(f"Total duration: {metadata.get('total_duration', 0)}s")
        
    except Exception as e:
        print(f"❌ Error loading settings: {e}")

def main():
    parser = argparse.ArgumentParser(description='Configure voice settings for characters')
    parser.add_argument('action', choices=['list', 'show', 'set', 'preset'], 
                       help='Action to perform')
    parser.add_argument('--character', help='Character name')
    parser.add_argument('--speed', type=float, help='Speech speed (0.5-2.0)')
    parser.add_argument('--temperature', type=float, help='Voice variation (0.1-1.0)')
    parser.add_argument('--pause_scale', type=float, help='Pause duration scale (0.5-2.0)')
    parser.add_argument('--stress_scale', type=float, help='Stress intensity (0.5-1.5)')
    parser.add_argument('--pitch_scale', type=float, help='Pitch scale (0.8-1.2)')
    
    args = parser.parse_args()
    
    if args.action == 'list':
        characters = list_characters()
        print(f"📋 Available characters ({len(characters)}):")
        for char in characters:
            print(f"  - {char}")
    
    elif args.action == 'show':
        if not args.character:
            print("❌ --character required for show action")
            return
        show_current_settings(args.character)
    
    elif args.action == 'preset':
        if not args.character:
            print("❌ --character required for preset action")
            return
        
        settings = get_default_settings_for_character(args.character)
        configure_voice_settings(args.character, settings)
    
    elif args.action == 'set':
        if not args.character:
            print("❌ --character required for set action")
            return
        
        settings = {}
        if args.speed is not None:
            settings['speed'] = args.speed
        if args.temperature is not None:
            settings['temperature'] = args.temperature
        if args.pause_scale is not None:
            settings['pause_scale'] = args.pause_scale
        if args.stress_scale is not None:
            settings['stress_scale'] = args.stress_scale
        if args.pitch_scale is not None:
            settings['pitch_scale'] = args.pitch_scale
        
        if not settings:
            print("❌ No settings provided")
            return
        
        configure_voice_settings(args.character, settings)

if __name__ == "__main__":
    main()

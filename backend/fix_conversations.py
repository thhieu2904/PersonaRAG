import json
import os

def fix_conversations_file(file_path, character_id):
    """Fix conversations file by adding character_id field"""
    print(f"Fixing {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        conversations = json.load(f)
    
    # Add character_id to each conversation
    for conv in conversations:
        conv['character_id'] = character_id
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(conversations, f, ensure_ascii=False, indent=2)
    
    print(f"  ✅ Added character_id to {len(conversations)} conversations")

def main():
    """Fix all conversation files"""
    print("🔧 Fixing conversation files...")
    
    # Map of character folders to character IDs
    character_mapping = {
        'gia_cat_luong': 'zhuge_liang',
        'tu_ma_y': 'sima_yi'
    }
    
    base_path = r'D:\Personal\PersonaRAG_v3\backend\data\training'
    
    for folder, char_id in character_mapping.items():
        conv_file = os.path.join(base_path, folder, 'conversations.json')
        if os.path.exists(conv_file):
            fix_conversations_file(conv_file, char_id)
        else:
            print(f"❌ File not found: {conv_file}")
    
    print("✅ All conversation files fixed!")

if __name__ == "__main__":
    main()

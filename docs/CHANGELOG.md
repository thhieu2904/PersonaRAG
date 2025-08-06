# Changelog

All notable changes to PersonaRAG project will be documented in this file.

## [v3.1.0] - 2025-01-05

### 🏗️ **Restructured Architecture**

- **MOVED**: F5-TTS from standalone `backend/F5-TTS-Vietnamese-100h/` to integrated `backend/app/services/cloneVoice/`
- **IMPROVED**: Project structure for better modularity and maintainability
- **UPDATED**: Import paths and configurations to match new structure

### 🔧 **Technical Improvements**

- **OPTIMIZED**: TTS service configuration with proper path management
- **ENHANCED**: Device handling with automatic fallback (CUDA → MPS → CPU)
- **FIXED**: Path references in `tts_config.py` and `tts_service.py`
- **ADDED**: Proper `__init__.py` files for Python package structure

### 🧹 **Cleanup & Maintenance**

- **REMOVED**: Duplicate F5-TTS folder structure
- **CLEANED**: Temporary audio files
- **UPDATED**: `.gitignore` to reflect new structure
- **OPTIMIZED**: File organization for better development workflow

### 📁 **New Structure**

```
backend/app/services/cloneVoice/
├── api.py                 # F5TTS API wrapper
├── wrapper.py            # Service wrapper
├── model/                # Model architecture
├── infer/                # Inference utilities
├── configs/              # Model configurations
├── train/                # Training scripts
└── __init__.py          # Package initialization
```

### 🔄 **Migration Notes**

- All F5-TTS functionalities preserved
- Import statements updated automatically
- Configuration paths adjusted
- No breaking changes for existing features

### 🎯 **Next Steps**

- Integration testing with new structure
- Performance optimization
- Documentation updates
- Enhanced error handling

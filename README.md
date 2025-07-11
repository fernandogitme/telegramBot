# 🎤 Voice Translation Bot for Telegram

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Telegram Bot API](https://img.shields.io/badge/Telegram%20Bot%20API-Latest-blue.svg)](https://core.telegram.org/bots/api)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![OpenAI Whisper](https://img.shields.io/badge/OpenAI-Whisper-orange.svg)](https://github.com/openai/whisper)
[![Ollama](https://img.shields.io/badge/Ollama-Latest-purple.svg)](https://ollama.ai)

A powerful Telegram bot that automatically transcribes voice messages and translates them for multilingual group conversations. Break language barriers in your group chats with AI-powered voice-to-text and translation capabilities.

## ✨ Features

- **🎯 Voice Recognition**: Transcribes voice messages using OpenAI Whisper (large-v3 model)
- **🌐 Multi-language Translation**: Supports 80+ languages with intelligent translation via Ollama
- **🔊 Text-to-Speech**: Generates audio responses using Coqui TTS for supported languages
- **👥 Group Management**: Automatic user language preferences and group cleanup
- **🚀 Zero Configuration**: Works out of the box - users just set their language once
- **🧠 Smart Detection**: Automatically detects the language of incoming voice messages
- **📱 Easy Setup**: Simple commands for users to configure their preferred language

## 🔧 How It Works

1. **👤 User Setup**: Each user sets their language preference once using `/idioma <code>`
2. **🎤 Voice Message**: Someone sends a voice message to the group
3. **📝 Transcription**: Bot transcribes the audio using Whisper AI
4. **🌍 Translation**: Bot translates the text for users who speak different languages
5. **🔊 Audio Response**: Bot generates and sends audio translations (when supported)

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Telegram Bot Token (get it from [@BotFather](https://t.me/BotFather))
- Ollama installed and running locally
- CUDA-compatible GPU (recommended for optimal performance)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/voice-translation-bot.git
   cd voice-translation-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your TELEGRAM_BOT_TOKEN
   ```

4. **Install and configure Ollama**
   ```bash
   # Install Ollama (visit https://ollama.ai for your OS)
   ollama pull phi3:3.8b-mini-128k-instruct-q4_K_M
   ```

5. **Run the bot**
   ```bash
   python bot.py
   ```


## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### Model Configuration

The bot uses these AI models by default:
- **Whisper**: `large-v3` (best accuracy)
- **Ollama**: `phi3:3.8b-mini-128k-instruct-q4_K_M`
- **TTS**: `xtts_v2` (multilingual)

You can modify these in the code if needed.

## 🎯 Usage

### Bot Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/start` or `/ayuda` | Show help message | `/start` |
| `/idioma <code>` | Set your language preference | `/idioma en` |
| `/idiomas_disponibles` | List all available languages | `/idiomas_disponibles` |
| `/mostrar_idiomas` | Show configured languages in the group | `/mostrar_idiomas` |
| `/limpiar_json` | Clean inactive users (admin only) | `/limpiar_json` |

### Supported Languages

The bot supports 80+ languages including:
- **Spanish** (`es`), **English** (`en`), **French** (`fr`)
- **German** (`de`), **Italian** (`it`), **Portuguese** (`pt`)
- **Russian** (`ru`), **Japanese** (`ja`), **Chinese** (`zh`)
- **Arabic** (`ar`), **Hindi** (`hi`), **Korean** (`ko`)
- And many more...

Use `/idiomas_disponibles` to see the complete list.

### Example Workflow

1. **Add bot to group**
   ```
   Bot: ¡Hola! I'm your voice translation assistant...
   ```

2. **Users set their languages**
   ```
   User1: /idioma es
   User2: /idioma en
   User3: /idioma fr
   ```

3. **Send voice message**
   ```
   User1: [sends voice in Spanish]
   Bot: 📝 User1: "Hola, ¿cómo están todos?"
   Bot: 🌐 For @user2 (english): "Hello, how is everyone?"
   Bot: 🌐 For @user3 (french): "Salut, comment allez-vous tous?"
   Bot: [sends audio files for each translation]
   ```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Telegram API  │────│  Voice Message  │────│  Whisper AI     │
│                 │    │   Processing    │    │  (Transcription)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                      │
                                                      ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Coqui TTS     │────│    Ollama AI    │────│   Translation   │
│  (Audio Gen)    │    │   Translation   │    │    Management   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔒 Privacy & Security
Ollama AI 
 (Translation) 
- **No Data Storage**: Voice messages are processed temporarily and deleted immediately
- **Local Processing**: All AI processing happens locally (no external API calls)
- **User Control**: Users can remove their language preferences at any time
- **Automatic Cleanup**: Inactive users are automatically removed from the system

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/voice-translation-bot.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/
```


## 📈 Performance Metrics (30-second audio)

### Processing Times

| Feature | Model | Processing Time | Hardware Requirements |
|---------|-------|----------------|----------------------|
| **Audio Transcription** | Whisper Large v3 | 20-30 seconds | GPU recommended |
| **Audio Transcription** | Whisper Base | 3-5 seconds | CPU/GPU |
| **Language Translation** | Phi3:3.8b-mini-128k-instruct-q4_K_M | 2-5 seconds | CPU/GPU |
| **Audio Generation** | TTS Engine | 20 seconds (GPU) / 40 seconds (CPU) | GPU acceleration optional |

### Performance Summary

- ⚡ **Total Processing Time**: 
  - With Whisper Large v3: ~42-75 seconds
  - With Whisper Base: ~25-45 seconds
- 🔄 **Concurrent Processing**: Multiple audio files supported
- 💾 **Memory Efficient**: Optimized for consumer hardware
- 🚀 **GPU Acceleration**: 2x faster audio generation with GPU

---

*Performance may vary based on hardware specifications and audio complexity*

## 🐛 Troubleshooting

### Common Issues

**Bot doesn't respond to voice messages**
- Check if Whisper model is properly installed
- Verify Ollama is running and the model is pulled
- Check bot permissions in the group

**TTS not working**
- Ensure you have a CUDA-compatible GPU
- Check if the target language is supported by XTTS_v2
- Verify TTS model installation

**High memory usage**
- Consider using smaller Whisper models (`base`, `small`)
- Reduce Ollama model size
- Enable CPU-only mode if GPU memory is limited

### Debug Mode

Enable debug logging by setting:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) for speech recognition
- [Ollama](https://ollama.ai) for local LLM inference
- [Coqui TTS](https://github.com/coqui-ai/TTS) for text-to-speech
- [python-telegram-bot](https://python-telegram-bot.org/) for Telegram integration

## 📊 Stats

![GitHub stars](https://img.shields.io/github/stars/yourusername/voice-translation-bot?style=social)
![GitHub forks](https://img.shields.io/github/forks/yourusername/voice-translation-bot?style=social)
![GitHub issues](https://img.shields.io/github/issues/yourusername/voice-translation-bot)
![GitHub pull requests](https://img.shields.io/github/issues-pr/yourusername/voice-translation-bot)

## 🌟 Show Your Support

If this project helped you, please consider giving it a ⭐ star on GitHub!

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/yourusername">Your Name</a>
</p>

<p align="center">
  <a href="#-voice-translation-bot-for-telegram">Back to Top</a>
</p>
